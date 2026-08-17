"""
Example 6: Checkpointing & Fault Tolerance

This example demonstrates:
- Enabling checkpointing and configuring checkpoint behavior
- Choosing a state backend (HashMap vs RocksDB)
- The difference between checkpoints and savepoints
- Restart strategies for automatic recovery

WHAT IT DOES:
Configures a job with production-style fault tolerance settings and
explains, via comments and console output, exactly what each setting
controls and why it matters. Checkpointing behavior is best observed on
a real cluster with the Web UI, so this example focuses on correct
configuration plus explanation.

HOW TO RUN:
python 06_checkpointing_and_fault_tolerance.py

EXPECTED OUTPUT:
Console output showing the job running with checkpointing enabled, plus
explanatory notes on fault tolerance concepts.
"""

from pyflink.datastream import (
    StreamExecutionEnvironment,
    CheckpointingMode,
    ExternalizedCheckpointCleanup,
)
from pyflink.common import Duration, RestartStrategies
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor


def configure_checkpointing(env):
    """
    Configure checkpointing with production-oriented defaults.
    """
    # Enable checkpointing every 30 seconds with EXACTLY_ONCE semantics.
    env.enable_checkpointing(30_000, CheckpointingMode.EXACTLY_ONCE)

    checkpoint_config = env.get_checkpoint_config()

    # Don't start a new checkpoint until at least 15s after the previous
    # one *completed* -- prevents checkpoints from piling up if they're slow.
    checkpoint_config.set_min_pause_between_checkpoints(15_000)

    # Fail (and let the restart strategy kick in) if a checkpoint takes
    # longer than 2 minutes -- likely indicates backpressure or a stuck task.
    checkpoint_config.set_checkpoint_timeout(120_000)

    # Only one checkpoint in flight at a time (simplest, safest default).
    checkpoint_config.set_max_concurrent_checkpoints(1)

    # Keep checkpoints on external storage even after the job is cancelled,
    # so you can manually resume from the last checkpoint if needed.
    checkpoint_config.set_externalized_checkpoint_cleanup(
        ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
    )

    return env


def configure_restart_strategy(env):
    """
    Configure how Flink automatically recovers from task failures.
    """
    # Retry up to 3 times, with a 10-second delay between attempts, before
    # giving up and failing the whole job.
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 10_000))
    return env


def checkpointing_configuration_demo():
    print("\n" + "=" * 60)
    print("1. CONFIGURING CHECKPOINTING")
    print("=" * 60)

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    configure_checkpointing(env)
    configure_restart_strategy(env)

    print("Checkpointing enabled: interval=30s, mode=EXACTLY_ONCE")
    print("Min pause between checkpoints: 15s")
    print("Checkpoint timeout: 120s")
    print("Restart strategy: fixed-delay, 3 attempts, 10s delay")

    ds = env.from_collection([1, 2, 3, 4, 5], type_info=Types.INT())
    ds.map(lambda x: x * 2, output_type=Types.INT()).print()

    env.execute("checkpointing-configuration-demo")


def state_backend_explainer():
    print("\n" + "=" * 60)
    print("2. STATE BACKENDS")
    print("=" * 60)
    print(
        """
    HashMapStateBackend (default, on-heap):
        - State objects live on the JVM heap
        - Fastest read/write, but limited by available heap memory
        - Best for small-to-medium state that comfortably fits in memory

    EmbeddedRocksDBStateBackend (off-heap, on local disk):
        - State is serialized and stored in an embedded RocksDB instance
          on local disk (with an in-memory cache/write-buffer)
        - Supports state far larger than available memory
        - Enables INCREMENTAL checkpoints (only deltas are uploaded, not
          the full state each time) -- crucial for large state at scale
        - Slightly higher per-access latency due to (de)serialization

    Configure via flink-conf.yaml (cluster-wide default):
        state.backend: rocksdb
        state.backend.incremental: true

    Or programmatically (job-specific):
        from pyflink.datastream import EmbeddedRocksDBStateBackend
        env.set_state_backend(EmbeddedRocksDBStateBackend())
    """
    )


def checkpoints_vs_savepoints_explainer():
    print("\n" + "=" * 60)
    print("3. CHECKPOINTS VS SAVEPOINTS")
    print("=" * 60)
    print(
        """
    Checkpoints:
        - Automatic, periodic, lightweight snapshots for FAILURE RECOVERY
        - Lifecycle fully managed by Flink (created & cleaned up automatically,
          unless externalized cleanup is configured)
        - Triggered by the JobManager's CheckpointCoordinator sending
          "checkpoint barriers" through the stream (Chandy-Lamport-style
          distributed snapshot algorithm)
        - When a task fails, the whole job (or just the affected region,
          with fine-grained recovery) restarts from the last completed
          checkpoint

    Savepoints:
        - Manually triggered, POINT-IN-TIME snapshots for planned operations:
          job upgrades, Flink version upgrades, rescaling parallelism,
          A/B testing a new job version against the same state
        - Owned by the user -- persists until explicitly deleted
        - Same underlying mechanism as checkpoints, but explicitly requested
          and typically stored in a stable, well-known location

    CLI usage:
        # Trigger a savepoint for a running job
        ./bin/flink savepoint <jobId> /path/to/savepoints

        # Stop a job gracefully, taking a final savepoint
        ./bin/flink stop --savepointPath /path/to/savepoints <jobId>

        # Restart a job from a savepoint (e.g., after a code change)
        ./bin/flink run -s /path/to/savepoints/savepoint-xxxx app.jar
    """
    )


def exactly_once_semantics_explainer():
    print("\n" + "=" * 60)
    print("4. EXACTLY-ONCE SEMANTICS")
    print("=" * 60)
    print(
        """
    Flink's exactly-once guarantee has two layers:

    1) Internal state consistency (always achievable):
       Checkpoint barriers flow through the DAG; each operator snapshots
       its state exactly when the barrier passes. On recovery, all
       operators roll back to a mutually consistent state as of the same
       logical point in the stream. Achieved via CheckpointingMode.EXACTLY_ONCE
       (vs the cheaper, weaker AT_LEAST_ONCE mode).

    2) End-to-end exactly-once (requires cooperating sinks):
       Internal consistency alone isn't enough if a sink might duplicate
       writes on recovery. True end-to-end exactly-once additionally
       requires either:
         a) An idempotent sink (writing the same record twice has the same
            effect as writing it once), or
         b) A transactional / two-phase-commit sink (e.g., Kafka's
            transactional producer via `TwoPhaseCommitSinkFunction`) that
            only commits output once the corresponding checkpoint completes

    Without a cooperating sink, you effectively get at-least-once
    end-to-end delivery even if internal processing is exactly-once.
    """
    )


# DETAILED EXPLANATION:-
"""
CHECKPOINTING & FAULT TOLERANCE CONCEPTS:

1. Checkpoint Barriers & the Snapshot Algorithm:
   - The CheckpointCoordinator (running in the JobManager) periodically
     injects "checkpoint barrier" markers into all source operators
   - Barriers flow downstream through the DAG alongside regular data
   - When an operator has received the barrier from ALL its input
     streams, it snapshots its state and forwards the barrier downstream
   - Once every operator has snapshotted (barrier reaches all sinks),
     the checkpoint is marked complete
   - This is a streaming variant of the Chandy-Lamport distributed
     snapshot algorithm

2. Checkpointing Modes:
   - EXACTLY_ONCE: aligns barriers, may add small latency but guarantees
     internal state consistency exactly once per checkpoint
   - AT_LEAST_ONCE: cheaper, doesn't align barriers as strictly, can
     result in some state being processed more than once on recovery

3. Recovery Flow:
   a) A task fails (exception, TaskManager crash, etc.)
   b) The JobManager detects the failure and, per the restart strategy,
      decides whether/how to restart
   c) All (or an affected subset of, with fine-grained recovery) tasks
      are restarted and their state is restored from the last completed
      checkpoint
   d) Sources rewind to the recorded offsets (e.g., Kafka consumer
      offsets stored in the checkpoint) and reprocessing resumes

4. Restart Strategies:
   - fixed-delay: retry N times with a fixed delay between attempts
   - failure-rate: retry as long as failures don't exceed a rate threshold
   - exponential-delay: increasing delay between retries
   - none: never automatically restart (job fails permanently)

5. Incremental Checkpoints (RocksDB only):
   - Instead of re-uploading the full state every checkpoint, only the
     changed data (delta) since the last checkpoint is uploaded
   - Dramatically reduces checkpoint duration/size for large state,
     at the cost of slightly more complex recovery (must replay deltas)

6. Unaligned Checkpoints:
   - Under heavy backpressure, barrier alignment can be slow (barriers
     queue up behind data in busy channels)
   - Unaligned checkpoints let barriers overtake buffered data, snapshotting
     in-flight data too -- speeds up checkpointing under backpressure at
     the cost of larger checkpoint size

BEST PRACTICES:

1. Always enable checkpointing for production streaming jobs -- it's off
   by default
2. Set `min_pause_between_checkpoints` to avoid checkpoint storms if
   checkpoints are occasionally slow
3. Use RocksDB + incremental checkpoints once state exceeds what
   comfortably fits in heap memory
4. Use savepoints (not checkpoints) for planned upgrades/migrations --
   they're explicitly user-owned and safe from automatic cleanup
5. Pair EXACTLY_ONCE checkpointing with transactional/idempotent sinks if
   you need true end-to-end exactly-once delivery
6. Monitor checkpoint duration and size via the Web UI -- growing
   durations often indicate a state-size or backpressure problem forming
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - CHECKPOINTING & FAULT TOLERANCE")
    print("#" * 60)

    checkpointing_configuration_demo()
    state_backend_explainer()
    checkpoints_vs_savepoints_explainer()
    exactly_once_semantics_explainer()

    print("\n" + "#" * 60)
    print("# ALL CHECKPOINTING EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 07_kafka_streaming_pipeline.py for an end-to-end example")
