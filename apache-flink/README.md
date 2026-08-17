# Apache Flink Complete Guide

## Table of Contents
1. [What is Apache Flink?](#what-is-apache-flink)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Setup & Installation](#setup--installation)
5. [Basic Examples](#basic-examples)
6. [Time, Watermarks & Windows](#time-watermarks--windows)
7. [State & Fault Tolerance](#state--fault-tolerance)
8. [Table API & SQL](#table-api--sql)
9. [Connectors](#connectors)
10. [Real-World Use Cases](#real-world-use-cases)
11. [Best Practices](#best-practices)
12. [Deployment Modes](#deployment-modes)
13. [Troubleshooting](#troubleshooting)
14. [Flink vs Other Frameworks](#flink-vs-other-frameworks)
15. [Resources](#resources)

---

## What is Apache Flink?

**Apache Flink** is a distributed processing engine and framework for stateful computations over
**unbounded** (streaming) and **bounded** (batch) data streams. Unlike Spark, which is fundamentally
a batch engine that simulates streaming via micro-batches, Flink is a **true streaming-first** engine —
batch is treated as a special case of streaming (a bounded stream).

### Key Points
- **True streaming**: Record-at-a-time processing, not micro-batches
- **Low latency**: Sub-second/millisecond latencies for event-driven applications
- **Exactly-once semantics**: Via distributed snapshots (Chandy-Lamport-based checkpointing)
- **Stateful**: First-class, fault-tolerant state management (keyed & operator state)
- **Event-time processing**: Correct results even with out-of-order/late data using watermarks
- **Unified batch & streaming**: Same APIs (DataStream API in `BATCH` or `STREAMING` mode)
- **Language Support**: Java, Scala, Python (PyFlink), SQL

### Why Use Apache Flink?
✅ True streaming with millisecond latency
✅ Strong consistency guarantees (exactly-once end-to-end with 2-phase-commit sinks)
✅ Sophisticated event-time & watermark handling for out-of-order data
✅ Rich, fine-grained state APIs (ValueState, ListState, MapState, etc.)
✅ Backpressure-aware, natively handles slow consumers
✅ Mature SQL/Table API for declarative stream processing
✅ Used at scale by Alibaba, Netflix, Uber, LinkedIn, Stripe, etc.

---

## Core Concepts

### 1. DataStream vs Table API
- **DataStream API**: Low/mid-level API for fine-grained control over streams (Java/Scala/Python)
- **Table API / SQL**: High-level, declarative API — write SQL or a fluent Table API and let
  Flink's Planner (built on Apache Calcite) optimize the execution plan
- Both can be freely mixed via `StreamTableEnvironment`

```python
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
ds = env.from_collection([1, 2, 3, 4, 5])
```

### 2. Bounded vs Unbounded Streams
- **Unbounded stream**: Has a start but no defined end (e.g., Kafka topic) — processed continuously
- **Bounded stream**: Has a defined start and end (e.g., a file) — processed like a batch job
- Flink's `RuntimeExecutionMode` can be `STREAMING`, `BATCH`, or `AUTOMATIC`

### 3. Transformations
Common DataStream transformations:
- `map()`, `flatMap()`, `filter()` — 1:1 or 1:many element transforms
- `keyBy()` — logically partitions the stream by key (required before windowing/state)
- `window()` — groups keyed elements into finite chunks for computation
- `reduce()`, `aggregate()`, `process()` — computation over a window or keyed stream
- `connect()`, `union()`, `join()`, `coGroup()` — combining multiple streams

```python
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
ds = env.from_collection([("a", 1), ("b", 2), ("a", 3)])

result = (
    ds.key_by(lambda x: x[0])
      .reduce(lambda a, b: (a[0], a[1] + b[1]))
)
result.print()
env.execute("keyed-reduce-example")
```

### 4. Operator Chaining & Parallelism
- Flink chains compatible operators into a single task (reduces serialization/network overhead)
- Each operator can have its own `parallelism`; the job graph is turned into an
  **Execution Graph** distributed across TaskManager slots

### 5. Jobs, JobGraph, ExecutionGraph
- A Flink program is translated into a **JobGraph** (logical plan)
- The JobManager turns this into an **ExecutionGraph** (physical plan with parallel task instances)
- Tasks are scheduled onto **TaskManager** slots for execution

---

## Architecture

```
                 ┌───────────────────────────┐
                 │        Client            │
                 │ (submits JobGraph)         │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │        JobManager          │
                 │  - Dispatcher               │
                 │  - ResourceManager          │
                 │  - JobMaster (per job)      │
                 └─────────────┬─────────────┘
                               │ schedules tasks
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
 ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
 │ TaskManager │        │ TaskManager │        │ TaskManager │
 │  (slots)    │        │  (slots)    │        │  (slots)    │
 │  Tasks/Sub- │        │  Tasks/Sub- │        │  Tasks/Sub- │
 │  tasks      │        │  tasks      │        │  tasks      │
 └─────────────┘        └─────────────┘        └─────────────┘
```

**Components:**
- **JobManager**: Coordinates job execution — schedules tasks, coordinates checkpoints,
  handles recovery. Contains the `Dispatcher`, `ResourceManager`, and one `JobMaster` per job.
- **TaskManager**: Worker process; executes tasks (subtasks of operators) in **task slots**.
  Manages memory, network buffers, and reports status back to the JobManager.
- **Task Slots**: Fixed subdivision of a TaskManager's resources. Number of slots ≈ number of
  parallel tasks that can run concurrently.
- **Dispatcher**: Entry point for job submission, starts a JobMaster per submitted job.
- **ResourceManager**: Manages TaskManager registration and resource allocation (integrates with
  YARN/Kubernetes/Standalone resource providers).

### Checkpointing Coordinator
The JobManager also runs the **CheckpointCoordinator**, which triggers distributed snapshots
(checkpoints) across all TaskManagers using a variant of the **Chandy-Lamport algorithm**
(via checkpoint barriers flowing through the stream).

---

## Setup & Installation

### Prerequisites
- Java 11 or 17 (Flink JVM-based runtime)
- Python 3.9–3.11 (for PyFlink; check compatibility with your Flink version)

### Check Java Installation
```bash
java -version
```

### Installation Options

#### Option 1: pip install PyFlink (Easiest, for learning/local dev)
```bash
pip install apache-flink
```

#### Option 2: Download Flink Distribution (for cluster/Flink CLI usage)
1. Download from https://flink.apache.org/downloads/
2. Extract: `tar -xzf flink-1.20.0-bin-scala_2.12.tgz`
3. Start a local cluster:
```bash
cd flink-1.20.0
./bin/start-cluster.sh
```
4. Open the Flink Web UI: http://localhost:8081

### Verify Installation
```bash
python -c "import pyflink; print(pyflink.__version__)"
```

---

## Basic Examples

### Example 1: DataStream Basics
See: `01_datastream_basics.py`

### Example 2: Table API & SQL Basics
See: `02_table_api_basics.py`

### Example 3: Event Time, Watermarks & Windowing
See: `03_windowing_and_watermarks.py`

### Example 4: Keyed & Operator State (Stateful Processing)
See: `04_stateful_processing.py`

### Example 5: SQL, Connectors & CDC-style pipelines
See: `05_sql_and_connectors.py`

### Example 6: Checkpointing & Fault Tolerance
See: `06_checkpointing_and_fault_tolerance.py`

### Example 7: End-to-end Kafka Streaming Pipeline
See: `07_kafka_streaming_pipeline.py`

---

## Time, Watermarks & Windows

### Notions of Time
- **Event time**: Timestamp embedded in the event itself (when it *actually happened*). Preferred
  for correctness with out-of-order/late data.
- **Processing time**: Wall-clock time of the machine processing the event. Fastest, but
  non-deterministic and not reproducible.
- **Ingestion time**: Timestamp assigned when the event enters Flink (a compromise between the two).

### Watermarks
A **watermark** is a marker in the stream asserting "no more events with timestamp ≤ W should
arrive from here on" — it's how Flink knows when it's safe to close a window and produce results
for event-time processing despite out-of-order arrivals.

```python
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Duration

watermark_strategy = (
    WatermarkStrategy
    .for_bounded_out_of_orderness(Duration.of_seconds(5))
    .with_timestamp_assigner(lambda event, ts: event.event_time_millis)
)

ds_with_watermarks = ds.assign_timestamps_and_watermarks(watermark_strategy)
```

### Window Types
- **Tumbling windows**: Fixed-size, non-overlapping (e.g., every 1 minute)
- **Sliding windows**: Fixed-size, overlapping (e.g., 5-minute window, sliding every 1 minute)
- **Session windows**: Dynamic size based on a gap of inactivity
- **Global windows**: All elements of a key in one window (requires a custom trigger)

```python
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common import Time

windowed = (
    ds_with_watermarks
    .key_by(lambda x: x.user_id)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .sum("amount")
)
```

### Late Data Handling
- **Allowed lateness**: `.allowed_lateness(Time.seconds(30))` keeps windows open a bit longer
- **Side outputs**: Route data that arrives too late to a separate stream instead of dropping it

---

## State & Fault Tolerance

### Why State Matters
Streaming applications are inherently stateful — counting, deduplication, joins, and aggregations
all require remembering information across events. Flink treats state as a first-class citizen
with automatic fault-tolerant checkpointing.

### Keyed State (per-key, inside a `KeyedStream`)
- `ValueState<T>` — a single value per key
- `ListState<T>` — a list of values per key
- `MapState<K, V>` — a map per key
- `ReducingState<T>` / `AggregatingState<T>` — incrementally aggregated state

```python
from pyflink.datastream import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor

class CountFunction(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("count", type_info=Types.LONG())
        self.count_state = runtime_context.get_state(descriptor)

    def process_element(self, value, ctx):
        current = self.count_state.value() or 0
        current += 1
        self.count_state.update(current)
        yield (value[0], current)
```

### Operator State
Non-keyed state scoped to a parallel operator instance (e.g., Kafka source offsets). Types:
`ListState` (evenly redistributed on rescale) and `BroadcastState` (same state on every instance).

### Checkpoints vs Savepoints
| | Checkpoints | Savepoints |
|---|---|---|
| Purpose | Automatic fault recovery | Manual, planned state snapshot |
| Trigger | Periodic, automatic | Manual (CLI/REST API) |
| Lifecycle | Managed/cleaned by Flink | Owned by the user, kept until deleted |
| Use case | Failure recovery | Upgrades, migrations, A/B testing, rescaling |

```bash
# Trigger a savepoint
./bin/flink savepoint <jobId> /path/to/savepoints

# Restart a job from a savepoint
./bin/flink run -s /path/to/savepoints/savepoint-xxxx app.jar
```

### State Backends
- **HashMapStateBackend**: State kept as objects on the JVM heap — fast, but limited by heap size
- **EmbeddedRocksDBStateBackend**: State kept in RocksDB on local disk — supports state larger
  than memory, enables incremental checkpoints

### Exactly-Once Semantics
Achieved via:
1. Distributed checkpoint barriers flowing through the DAG (Chandy-Lamport snapshot)
2. Idempotent or transactional sinks (`TwoPhaseCommitSinkFunction`, Kafka's exactly-once producer)

---

## Table API & SQL

Flink's Table API/SQL provides a unified, declarative layer over both batch and streaming data,
optimized by Apache Calcite.

```python
from pyflink.table import EnvironmentSettings, TableEnvironment

env_settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(env_settings)

t_env.execute_sql("""
    CREATE TABLE orders (
        order_id BIGINT,
        amount DOUBLE,
        order_time TIMESTAMP(3),
        WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'orders',
        'properties.bootstrap.servers' = 'localhost:9092',
        'format' = 'json'
    )
""")

result = t_env.sql_query("""
    SELECT
        window_start,
        window_end,
        SUM(amount) AS total_amount
    FROM TABLE(
        TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '1' MINUTE)
    )
    GROUP BY window_start, window_end
""")
```

Key SQL concepts:
- **Dynamic Tables**: A table that changes over time — the SQL/streaming duality
- **Changelog streams**: `INSERT`, `UPDATE_BEFORE`, `UPDATE_AFTER`, `DELETE` — enables CDC use cases
- **Temporal joins**: Join a stream against a versioned/point-in-time table (e.g., FX rates)
- **User Defined Functions (UDF/UDTF/UDAF)**: Extend SQL with custom Python/Java logic

---

## Connectors

Flink ships connectors (as separate JARs/Python packages) for popular systems:

| Connector | Use Case |
|---|---|
| Kafka | Streaming source/sink, exactly-once via transactional producer |
| Filesystem (S3, HDFS, local) | Batch/streaming file source & sink, supports Parquet/ORC/CSV |
| JDBC | Reading/writing to relational databases |
| Elasticsearch | Sink for search/analytics dashboards |
| CDC connectors (Debezium-based) | Change Data Capture from MySQL/Postgres/etc. |
| Pulsar, RabbitMQ, Cassandra | Additional community/ecosystem connectors |

```python
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema

kafka_source = (
    KafkaSource.builder()
    .set_bootstrap_servers("localhost:9092")
    .set_topics("input-topic")
    .set_group_id("flink-learning-group")
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)
```

---

## Real-World Use Cases

### 1. Real-Time Fraud Detection
Pattern matching over event streams (Flink CEP) to flag suspicious transaction sequences
within milliseconds.

### 2. Real-Time Analytics Dashboards
Continuous aggregation of clickstream/IoT data with sub-second latency, feeding dashboards
via Kafka + Elasticsearch/Kibana.

### 3. Change Data Capture (CDC) Pipelines
Streaming database changes (via Debezium/Flink CDC connectors) into a data lake or warehouse
in near real-time.

### 4. ETL / Continuous Data Enrichment
Enriching event streams with reference/dimension data via temporal joins or broadcast state.

### 5. Anomaly Detection & Monitoring
Stateful windowed aggregations to detect anomalies in metrics/logs streams.

### 6. Event-Driven Applications
Using Flink's `ProcessFunction` and state to implement business logic that reacts to events
(e.g., session tracking, SLA monitoring).

---

## Best Practices

### 1. Prefer Event Time over Processing Time
Ensures deterministic, reproducible results regardless of processing delays.

### 2. Choose the Right State Backend
- Small state that fits in memory → `HashMapStateBackend` (faster)
- Large state (GBs+) → `EmbeddedRocksDBStateBackend` with incremental checkpoints

### 3. Set Sensible Checkpoint Intervals
```python
env.enable_checkpointing(60000)  # every 60 seconds
env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
env.get_checkpoint_config().set_checkpoint_timeout(120000)
```
Too frequent → overhead; too infrequent → longer recovery & reprocessing time.

### 4. Avoid Unbounded State Growth
Use **State TTL** (`StateTtlConfig`) to expire state that's no longer needed.

```python
from pyflink.datastream.state import StateTtlConfig
from pyflink.common import Time

ttl_config = (
    StateTtlConfig.new_builder(Time.hours(24))
    .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .set_state_visibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .build()
)
```

### 5. Set Parallelism Thoughtfully
Match parallelism to partition counts of your source (e.g., Kafka partitions) to avoid idle
subtasks.

### 6. Use `keyBy` Carefully
Ensure keys are well-distributed to avoid data skew and hot subtasks.

### 7. Monitor Backpressure
Use the Flink Web UI's backpressure/busy metrics to identify slow operators.

### 8. Use Idempotent or Transactional Sinks
For true end-to-end exactly-once, sinks must support two-phase commit or be idempotent.

---

## Deployment Modes

### 1. Local / MiniCluster (Development)
```python
env = StreamExecutionEnvironment.get_execution_environment()
```

### 2. Standalone Cluster
```bash
./bin/start-cluster.sh
./bin/flink run -m localhost:8081 app.jar
```

### 3. YARN
```bash
./bin/flink run -m yarn-cluster -yn 4 app.jar
```

### 4. Kubernetes (Native or via Flink Kubernetes Operator)
```bash
./bin/flink run-application \
    --target kubernetes-application \
    -Dkubernetes.cluster-id=my-flink-cluster \
    local:///opt/flink/usrlib/app.jar
```

### 5. Session Mode vs Application Mode vs Per-Job Mode
- **Session Mode**: Long-running cluster, submit many jobs (good for short-lived, interactive jobs)
- **Application Mode**: Cluster lifecycle tied to a single application (recommended for production)
- **Per-Job Mode** (deprecated in newer versions): One cluster per job, submitted from a client

---

## Troubleshooting

### Common Issues

#### 1. "Java not found" / Version mismatch
**Solution**: Install Java 11 or 17, matching your Flink version's supported JDKs.
```bash
brew install openjdk@11   # macOS
sudo apt-get install openjdk-11-jdk   # Ubuntu
```

#### 2. Job stuck / checkpoints timing out
**Solutions**:
- Check for backpressure in the Web UI
- Increase `checkpoint.timeout`
- Reduce state size or switch to RocksDB with incremental checkpoints

#### 3. OutOfMemoryError / High GC pauses
**Solutions**:
- Tune `taskmanager.memory.process.size`
- Move large state to `EmbeddedRocksDBStateBackend` (off-heap)

#### 4. Watermarks not advancing / Windows never fire
**Solutions**:
- Ensure all sources/partitions are producing data (idle partitions stall watermarks)
- Use `withIdleness()` on the watermark strategy for sources that can go idle

#### 5. "py4j"-style serialization errors in PyFlink
**Solutions**:
- Ensure Python UDFs return well-defined types (`Types.STRING()`, etc.)
- Check Python/PyFlink version compatibility

---

## Flink vs Other Frameworks

| Feature | Flink | Spark | Kafka Streams | Beam |
|---------|-------|-------|----------------|------|
| Processing model | True streaming (record-at-a-time) | Micro-batch (+ Structured Streaming) | True streaming | Depends on runner |
| Latency | Milliseconds | Seconds (micro-batch) | Milliseconds | Depends on runner |
| State management | Rich, built-in, RocksDB-backed | Limited (mostly stateless/micro-batch state) | Built-in (RocksDB) | Depends on runner |
| Event-time/watermarks | Native, sophisticated | Structured Streaming supports basic watermarks | Basic | Native (windowing model) |
| Batch support | Yes (unified API) | Yes (native strength) | No | Yes |
| SQL support | Yes (Table API/SQL) | Yes (Spark SQL) | KSQL (via ksqlDB) | Limited |
| Exactly-once | Yes (checkpoints + 2PC sinks) | Yes (Structured Streaming) | Yes | Depends on runner |
| Maturity | High | Very High | High (Kafka ecosystem only) | Medium |
| Language Support | Java, Scala, Python, SQL | Python, Scala, Java, R, SQL | Java, Scala | Python, Java, Go |

---

## Resources

- **Official Documentation**: https://nightlies.apache.org/flink/flink-docs-stable/
- **PyFlink API Docs**: https://nightlies.apache.org/flink/flink-docs-stable/api/python/
- **Flink Web UI**: http://localhost:8081 (when running)
- **GitHub (core)**: https://github.com/apache/flink
- **Official training exercises**: https://github.com/apache/flink-training
- **Official playgrounds (incl. PyFlink)**: https://github.com/apache/flink-playgrounds
- **PyFlink-specific playgrounds**: https://github.com/pyflink/playgrounds
- **Stack Overflow**: Tag `apache-flink` or `pyflink`
- **Flink Improvement Proposals (FLIPs)**: https://cwiki.apache.org/confluence/display/FLINK/Flink+Improvement+Proposals

---

## Next Steps

1. Run the examples in order (01 through 07)
2. Modify examples to understand watermarks, windows, and state behavior
3. Stand up a local Flink cluster and use the Web UI to observe job graphs & backpressure
4. Build an end-to-end pipeline: Kafka → Flink (stateful processing) → Kafka/Elasticsearch
5. Explore Flink SQL for declarative streaming pipelines
6. Deploy to a cluster (Kubernetes Application Mode is the modern recommended path)

---

**Remember**: Flink is about correctness first (event time + exactly-once), and speed second.
Think streams, think state, think watermarks! 🌊
