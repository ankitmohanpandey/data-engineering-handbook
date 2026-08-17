"""
Example 4: Stateful Processing - Keyed State & ProcessFunction

This example demonstrates:
- ValueState, ListState, and MapState (keyed state primitives)
- KeyedProcessFunction for custom, low-level stateful logic
- Timers (event-time and processing-time) for detecting inactivity/timeouts
- State TTL to automatically expire old state

WHAT IT DOES:
Shows how to build custom stateful streaming logic beyond what
windows/reduce provide -- e.g., running counts, deduplication, and
session-timeout detection using raw state + timers.

HOW TO RUN:
python 04_stateful_processing.py

EXPECTED OUTPUT:
Console output showing per-key running counts, deduplicated events, and
timeout notifications.
"""

from pyflink.datastream import StreamExecutionEnvironment, KeyedProcessFunction
from pyflink.datastream.state import (
    ValueStateDescriptor,
    ListStateDescriptor,
    MapStateDescriptor,
    StateTtlConfig,
)
from pyflink.common.typeinfo import Types
from pyflink.common import Time


def create_execution_environment():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    return env


class RunningCountFunction(KeyedProcessFunction):
    """
    Maintains a running count per key using ValueState.
    Analogous conceptually to a keyed 'reduce', but with full control.
    """

    def open(self, runtime_context):
        descriptor = ValueStateDescriptor("running_count", Types.LONG())
        self.count_state = runtime_context.get_state(descriptor)

    def process_element(self, value, ctx):
        current = self.count_state.value()
        if current is None:
            current = 0
        current += 1
        self.count_state.update(current)
        yield (value[0], current)


class DeduplicationFunction(KeyedProcessFunction):
    """
    Suppresses duplicate events per key using MapState as a "seen" set.
    Uses State TTL so the dedup window doesn't grow state unboundedly.
    """

    def open(self, runtime_context):
        descriptor = MapStateDescriptor("seen_event_ids", Types.STRING(), Types.BOOLEAN())

        ttl_config = (
            StateTtlConfig.new_builder(Time.minutes(10))
            .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite)
            .set_state_visibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
            .build()
        )
        descriptor.enable_time_to_live(ttl_config)

        self.seen_state = runtime_context.get_map_state(descriptor)

    def process_element(self, value, ctx):
        key, event_id = value[0], value[1]
        if not self.seen_state.contains(event_id):
            self.seen_state.put(event_id, True)
            yield (key, event_id, "NEW")
        else:
            yield (key, event_id, "DUPLICATE")


class SessionTimeoutFunction(KeyedProcessFunction):
    """
    Detects when a key has been "quiet" for a configured timeout by
    registering a processing-time timer that gets reset on each new event.

    This is the classic pattern for session-timeout / inactivity detection
    that windows alone can't easily express.
    """

    TIMEOUT_MS = 5_000  # 5 seconds of inactivity => session considered over

    def open(self, runtime_context):
        self.last_seen_state = runtime_context.get_state(
            ValueStateDescriptor("last_seen_timer", Types.LONG())
        )
        self.event_count_state = runtime_context.get_state(
            ValueStateDescriptor("event_count", Types.LONG())
        )

    def process_element(self, value, ctx):
        key = value[0]

        # Cancel the previous timer (if any) before registering a new one.
        old_timer = self.last_seen_state.value()
        if old_timer is not None:
            ctx.timer_service().delete_processing_time_timer(old_timer)

        count = self.event_count_state.value() or 0
        count += 1
        self.event_count_state.update(count)

        new_timer = ctx.timer_service().current_processing_time() + self.TIMEOUT_MS
        ctx.timer_service().register_processing_time_timer(new_timer)
        self.last_seen_state.update(new_timer)

        yield (key, f"event #{count} received")

    def on_timer(self, timestamp, ctx):
        key = ctx.get_current_key()
        count = self.event_count_state.value() or 0
        yield (key, f"SESSION TIMED OUT after {count} events")

        # Clean up state for this key now that the session is over.
        self.last_seen_state.clear()
        self.event_count_state.clear()


def running_count_demo():
    print("\n" + "=" * 60)
    print("1. RUNNING COUNT WITH VALUESTATE")
    print("=" * 60)

    env = create_execution_environment()

    events = [("alice", "click"), ("bob", "click"), ("alice", "click"), ("alice", "click")]
    ds = env.from_collection(events, type_info=Types.TUPLE([Types.STRING(), Types.STRING()]))

    result = ds.key_by(lambda x: x[0]).process(
        RunningCountFunction(), output_type=Types.TUPLE([Types.STRING(), Types.LONG()])
    )
    result.print()

    env.execute("running-count-demo")


def deduplication_demo():
    print("\n" + "=" * 60)
    print("2. DEDUPLICATION WITH MAPSTATE + TTL")
    print("=" * 60)

    env = create_execution_environment()

    events = [
        ("alice", "evt-1"),
        ("alice", "evt-2"),
        ("alice", "evt-1"),  # duplicate
        ("bob", "evt-1"),
        ("bob", "evt-1"),  # duplicate
    ]
    ds = env.from_collection(events, type_info=Types.TUPLE([Types.STRING(), Types.STRING()]))

    result = ds.key_by(lambda x: x[0]).process(
        DeduplicationFunction(),
        output_type=Types.TUPLE([Types.STRING(), Types.STRING(), Types.STRING()]),
    )
    result.print()

    env.execute("deduplication-demo")


def session_timeout_demo():
    print("\n" + "=" * 60)
    print("3. SESSION TIMEOUT DETECTION WITH TIMERS")
    print("=" * 60)
    print(
        "NOTE: In a bounded/collection-based demo, timers fire once the job "
        "reaches its 'end of time' -- in a real unbounded stream, timers "
        "fire based on wall-clock/event-time as configured.\n"
    )

    env = create_execution_environment()

    events = [("alice", "ping"), ("alice", "ping"), ("bob", "ping")]
    ds = env.from_collection(events, type_info=Types.TUPLE([Types.STRING(), Types.STRING()]))

    result = ds.key_by(lambda x: x[0]).process(
        SessionTimeoutFunction(),
        output_type=Types.TUPLE([Types.STRING(), Types.STRING()]),
    )
    result.print()

    env.execute("session-timeout-demo")


# DETAILED EXPLANATION:-
"""
STATEFUL PROCESSING CONCEPTS:

1. Why Custom State?
   - Windows and reduce()/aggregate() cover common cases, but many
     real-world patterns need bespoke logic: deduplication, session
     timeouts, rate limiting, complex event sequencing, joins with custom
     semantics, etc.
   - `ProcessFunction` / `KeyedProcessFunction` give you direct access to
     state, timers, and the current key/timestamp/watermark.

2. Keyed State Primitives (only usable after key_by):
   - ValueState<T>: a single value per key (e.g., a counter, last-seen ts)
   - ListState<T>: an append-only list of values per key
   - MapState<K, V>: a key-value map per key (e.g., a "seen IDs" set)
   - ReducingState<T> / AggregatingState<T>: incrementally combined state

3. KeyedProcessFunction Lifecycle:
   - open(runtime_context): called once per parallel instance -- register
     state descriptors here
   - process_element(value, ctx): called for every incoming element;
     ctx gives access to the current key, timestamp, and timer service
   - on_timer(timestamp, ctx): called when a previously registered timer
     fires (processing-time or event-time)

4. Timers:
   - `ctx.timer_service().register_processing_time_timer(ts)`: fires at
     wall-clock time `ts`
   - `ctx.timer_service().register_event_time_timer(ts)`: fires once the
     watermark passes `ts` -- useful for deterministic, event-time-based
     timeout logic
   - Timers are per-key and are checkpointed along with other state --
     they survive failures/restarts
   - A common pattern: cancel + re-register a timer on every new event to
     implement "N seconds since last event" style timeouts

5. State TTL (Time-To-Live):
   - Prevents state from growing forever for keys that go stale
     (e.g., a deduplication set for a user who never returns)
   - `StateTtlConfig` controls when the TTL clock resets (on write only,
     or on read+write) and whether expired-but-not-yet-cleaned state is
     ever returned to the application

6. State Backends & Checkpointing (see 06_checkpointing_and_fault_tolerance.py):
   - All of this state is automatically included in Flink's checkpoints,
     so a failed task can resume with its state fully intact
   - Backend choice (heap vs RocksDB) affects how large this state can
     grow before you hit memory limits

7. When to Reach for ProcessFunction:
   ✅ Custom timeout/session logic that windows can't express cleanly
   ✅ Deduplication / exactly-once-processing semantics at the app level
   ✅ Fine-grained access to watermarks/timestamps for custom logic
   ✅ Emitting to side outputs based on custom conditions

   ❌ Standard windowed aggregations -- use window().reduce()/aggregate()
      instead, it's simpler and better optimized

BEST PRACTICES:

1. Always set State TTL for state tied to entities that may "go away"
   (users, sessions, devices) to bound memory usage
2. Cancel old timers before registering new ones when implementing
   "reset on activity" timeout patterns -- otherwise you leak timers
3. Prefer event-time timers over processing-time timers when timeout
   logic needs to be deterministic/reproducible
4. Keep state types serializable and as small as practical -- large
   per-key state multiplies with the number of keys and checkpoint size
5. Clear state explicitly (e.g., in on_timer after a session ends) rather
   than relying solely on TTL, when you know exactly when it's safe to do so
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - STATEFUL PROCESSING")
    print("#" * 60)

    running_count_demo()
    deduplication_demo()
    session_timeout_demo()

    print("\n" + "#" * 60)
    print("# ALL STATEFUL PROCESSING EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 05_sql_and_connectors.py to learn about SQL & connectors")
