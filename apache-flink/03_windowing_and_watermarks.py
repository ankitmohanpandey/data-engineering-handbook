"""
Example 3: Event Time, Watermarks & Windowing

This example demonstrates:
- The difference between event time and processing time
- Assigning timestamps and watermarks to a DataStream
- Tumbling, sliding, and session windows
- Handling out-of-order and late-arriving data
- Windowed aggregations (sum, reduce, process)

WHAT IT DOES:
Shows how Flink achieves correct results over unbounded, out-of-order
streams by using event time and watermarks, and how to bucket events
into windows for aggregation.

HOW TO RUN:
python 03_windowing_and_watermarks.py

EXPECTED OUTPUT:
Console output showing windowed aggregation results, grouped by window.
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import (
    TumblingEventTimeWindows,
    SlidingEventTimeWindows,
    EventTimeSessionWindows,
)
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.common import Duration, Time
from pyflink.common.typeinfo import Types


# Sample events: (user_id, amount, event_time_millis)
# Note the out-of-order arrival (timestamps aren't strictly increasing).
SAMPLE_EVENTS = [
    ("alice", 10, 1_000),
    ("bob", 5, 2_000),
    ("alice", 20, 1_500),   # arrives "out of order" relative to bob's event
    ("alice", 15, 5_000),
    ("bob", 8, 4_000),
    ("alice", 30, 61_000),  # falls into the next tumbling minute-window
    ("bob", 12, 62_000),
]


class TupleTimestampAssigner(TimestampAssigner):
    """Extracts the event-time timestamp (3rd tuple field) in milliseconds."""

    def extract_timestamp(self, value, record_timestamp):
        return value[2]


def create_execution_environment():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # deterministic ordering for this demo's output
    return env


def event_time_vs_processing_time_explainer():
    """
    Not runnable code -- a conceptual walkthrough printed to the console.
    """
    print("\n" + "=" * 60)
    print("1. EVENT TIME VS PROCESSING TIME")
    print("=" * 60)
    print(
        """
    Event time:      the timestamp embedded in the event (when it happened)
    Processing time: the wall-clock time of the machine processing it (when
                      Flink saw it)

    Event time is preferred for correctness: results are deterministic and
    reproducible even if the pipeline is replayed, delayed, or restarted --
    because the "meaning" of a window is anchored to when things actually
    happened, not when Flink happened to process them.
    """
    )


def watermark_strategy_demo():
    """
    Assign event-time timestamps and a bounded-out-of-orderness watermark
    strategy to a DataStream.
    """
    print("\n" + "=" * 60)
    print("2. ASSIGNING WATERMARKS")
    print("=" * 60)

    env = create_execution_environment()

    ds = env.from_collection(
        SAMPLE_EVENTS,
        type_info=Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG()]),
    )

    # Allow events to be up to 5 seconds out of order before being
    # considered "too late". The watermark trails the max seen timestamp
    # by this amount.
    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(TupleTimestampAssigner())
    )

    ds_with_watermarks = ds.assign_timestamps_and_watermarks(watermark_strategy)
    ds_with_watermarks.print()

    env.execute("watermark-strategy-demo")


def tumbling_window_demo():
    """
    Tumbling windows: fixed-size, non-overlapping, e.g. one window per minute.
    """
    print("\n" + "=" * 60)
    print("3. TUMBLING EVENT-TIME WINDOWS")
    print("=" * 60)

    env = create_execution_environment()

    ds = env.from_collection(
        SAMPLE_EVENTS,
        type_info=Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG()]),
    )

    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(TupleTimestampAssigner())
    )

    ds_with_watermarks = ds.assign_timestamps_and_watermarks(watermark_strategy)

    windowed = (
        ds_with_watermarks.key_by(lambda x: x[0])
        .window(TumblingEventTimeWindows.of(Time.minutes(1)))
        .reduce(lambda a, b: (a[0], a[1] + b[1], max(a[2], b[2])))
    )

    windowed.print()

    env.execute("tumbling-window-demo")


def sliding_window_demo():
    """
    Sliding windows: fixed-size but overlapping, e.g. a 1-minute window that
    slides forward every 30 seconds. An event can belong to multiple windows.
    """
    print("\n" + "=" * 60)
    print("4. SLIDING EVENT-TIME WINDOWS")
    print("=" * 60)

    env = create_execution_environment()

    ds = env.from_collection(
        SAMPLE_EVENTS,
        type_info=Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG()]),
    )

    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(TupleTimestampAssigner())
    )

    ds_with_watermarks = ds.assign_timestamps_and_watermarks(watermark_strategy)

    windowed = (
        ds_with_watermarks.key_by(lambda x: x[0])
        .window(SlidingEventTimeWindows.of(Time.seconds(60), Time.seconds(30)))
        .reduce(lambda a, b: (a[0], a[1] + b[1], max(a[2], b[2])))
    )

    windowed.print()

    env.execute("sliding-window-demo")


def session_window_demo():
    """
    Session windows: dynamic size, closed after a gap of inactivity for a key.
    Useful for user session tracking.
    """
    print("\n" + "=" * 60)
    print("5. SESSION WINDOWS")
    print("=" * 60)

    env = create_execution_environment()

    # A gap of > 10 seconds between "alice" events at t=15000 and t=61000
    # will start a new session window for alice.
    ds = env.from_collection(
        SAMPLE_EVENTS,
        type_info=Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG()]),
    )

    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(TupleTimestampAssigner())
    )

    ds_with_watermarks = ds.assign_timestamps_and_watermarks(watermark_strategy)

    windowed = (
        ds_with_watermarks.key_by(lambda x: x[0])
        .window(EventTimeSessionWindows.with_gap(Time.seconds(10)))
        .reduce(lambda a, b: (a[0], a[1] + b[1], max(a[2], b[2])))
    )

    windowed.print()

    env.execute("session-window-demo")


# DETAILED EXPLANATION:-
"""
EVENT TIME, WATERMARKS & WINDOWING CONCEPTS:

1. Why Event Time?
   - Real-world events arrive out of order (network delays, retries,
     mobile devices being offline, etc.)
   - Processing-time results depend on *when* Flink happens to process
     events -- not reproducible, not "correct" in a business sense
   - Event-time results are deterministic: replaying the exact same input
     always produces the exact same output, regardless of processing speed

2. Watermarks:
   - A watermark W is a special marker: "I believe no more events with
     timestamp <= W will arrive from this point on"
   - Windows can only "fire" (produce a result) once the watermark passes
     the window's end -- this is how Flink knows it's safe to finalize
   - `for_bounded_out_of_orderness(Duration)`: watermark = max seen
     timestamp - the bound. Larger bound = more tolerance for lateness,
     but higher latency (windows fire later)

3. Idle Sources & Watermarks:
   - If a source/partition stops producing data, its watermark contribution
     stalls, which can stall the whole pipeline's watermark
   - Use `.with_idleness(Duration)` on the WatermarkStrategy so idle
     sources are excluded from watermark calculation

4. Window Types:
   - Tumbling: fixed size, no overlap, every event belongs to exactly one
     window (e.g., "per-minute" aggregates)
   - Sliding: fixed size, overlapping, an event can belong to multiple
     windows (e.g., "trailing 5-minute average, updated every minute")
   - Session: dynamic size based on an inactivity gap per key (e.g., user
     session tracking on a website)
   - Global: all elements for a key go into one window -- requires a
     custom Trigger to ever fire (rarely used directly)

5. Window Functions:
   - reduce(): incremental, associative aggregation (like a running fold)
   - aggregate(): more general than reduce -- separate accumulator/output
     types, supports pre-aggregation
   - process(): full access to window metadata (start/end, all elements)
     via a ProcessWindowFunction -- most flexible but least optimized

6. Allowed Lateness & Side Outputs:
   - `.allowed_lateness(Time)`: keeps a window's state around a bit longer
     after the watermark passes, so late events can still update the result
   - Events later than allowed lateness can be routed to a side output
     instead of being silently dropped -- important for auditing/debugging

7. Window Lifecycle:
   a) Window is created when the first element for that key/window arrives
   b) Elements accumulate in window state as they arrive
   c) The window "fires" once the watermark passes window_end (or a custom
      Trigger says so), producing an output element
   d) The window's state is cleaned up after allowed_lateness expires

BEST PRACTICES:

1. Always assign timestamps and watermarks before keyBy + window
2. Choose a bounded-out-of-orderness duration based on your real
   data's latency profile -- measure it, don't guess
3. Use `.with_idleness()` for sources that may have idle periods
   (e.g., low-traffic Kafka partitions)
4. Prefer reduce()/aggregate() over process() when you don't need window
   metadata -- they enable more efficient incremental computation
5. Set allowed lateness deliberately, and monitor/side-output truly late
   data rather than silently dropping it
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - EVENT TIME, WATERMARKS & WINDOWING")
    print("#" * 60)

    event_time_vs_processing_time_explainer()
    watermark_strategy_demo()
    tumbling_window_demo()
    sliding_window_demo()
    session_window_demo()

    print("\n" + "#" * 60)
    print("# ALL WINDOWING EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 04_stateful_processing.py to learn about keyed & operator state")
