# Apache Flink Quick Reference Card

## 🚀 Quick Start
```bash
pip install apache-flink
python 01_datastream_basics.py
```

## 📋 StreamExecutionEnvironment

```python
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode

# Create environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)  # or BATCH / AUTOMATIC

# Trigger execution (Flink is lazy until execute() is called)
env.execute("my-job-name")
```

## 🔥 DataStream Sources

```python
# From an in-memory collection (learning/testing only)
ds = env.from_collection([1, 2, 3, 4, 5])

# From a text file
ds = env.read_text_file("path/to/file.txt")

# From Kafka
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema

source = (
    KafkaSource.builder()
    .set_bootstrap_servers("localhost:9092")
    .set_topics("my-topic")
    .set_group_id("my-group")
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)
ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "kafka-source")
```

## 🔧 Transformations

```python
# map (1-to-1)
ds.map(lambda x: x * 2)

# flat_map (1-to-many)
ds.flat_map(lambda line: line.split())

# filter
ds.filter(lambda x: x > 10)

# key_by (required before windowing/keyed state)
keyed = ds.key_by(lambda x: x[0])

# reduce (on a KeyedStream)
keyed.reduce(lambda a, b: (a[0], a[1] + b[1]))

# union (combine streams of the same type)
ds1.union(ds2)

# connect (combine streams of different types)
ds1.connect(ds2).map(CoMapFunction(...))
```

## ⏱️ Time & Watermarks

```python
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Duration

# Bounded out-of-orderness watermark strategy
strategy = (
    WatermarkStrategy
    .for_bounded_out_of_orderness(Duration.of_seconds(5))
    .with_timestamp_assigner(lambda event, ts: event.timestamp_millis)
)

ds_with_time = ds.assign_timestamps_and_watermarks(strategy)

# Handle idle sources (avoid stalled watermarks)
strategy_with_idleness = strategy.with_idleness(Duration.of_seconds(30))
```

## 🪟 Windows

```python
from pyflink.datastream.window import (
    TumblingEventTimeWindows,
    SlidingEventTimeWindows,
    EventTimeSessionWindows,
)
from pyflink.common import Time

# Tumbling window (fixed, non-overlapping)
ds.key_by(...).window(TumblingEventTimeWindows.of(Time.minutes(1))).sum("amount")

# Sliding window (fixed, overlapping)
ds.key_by(...).window(
    SlidingEventTimeWindows.of(Time.minutes(5), Time.minutes(1))
).sum("amount")

# Session window (dynamic gap-based)
ds.key_by(...).window(
    EventTimeSessionWindows.with_gap(Time.minutes(10))
).sum("amount")

# Allowed lateness
ds.key_by(...).window(...).allowed_lateness(Time.seconds(30)).sum("amount")
```

## 🗄️ Keyed State

```python
from pyflink.datastream import KeyedProcessFunction
from pyflink.datastream.state import ValueStateDescriptor, ListStateDescriptor, MapStateDescriptor
from pyflink.common.typeinfo import Types

class MyProcessFunction(KeyedProcessFunction):
    def open(self, ctx):
        self.count_state = ctx.get_state(ValueStateDescriptor("count", Types.LONG()))
        self.history_state = ctx.get_list_state(ListStateDescriptor("history", Types.STRING()))

    def process_element(self, value, ctx):
        count = (self.count_state.value() or 0) + 1
        self.count_state.update(count)
        yield (value, count)

ds.key_by(lambda x: x.key).process(MyProcessFunction())
```

## ✅ Checkpointing

```python
from pyflink.datastream import CheckpointingMode

env.enable_checkpointing(60000, CheckpointingMode.EXACTLY_ONCE)
env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
env.get_checkpoint_config().set_checkpoint_timeout(120000)
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
```

## 📊 Table API / SQL

```python
from pyflink.table import EnvironmentSettings, TableEnvironment

t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

# Register a source table
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

# Query it
t_env.sql_query("SELECT * FROM orders WHERE amount > 100").execute().print()

# Windowed aggregation (TVF windows)
t_env.sql_query("""
    SELECT window_start, window_end, SUM(amount) AS total
    FROM TABLE(TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '1' MINUTE))
    GROUP BY window_start, window_end
""")
```

## 🔌 Sinks

```python
# Print (debugging)
ds.print()

# Text file
ds.sink_to(FileSink.for_row_format(...).build())

# Kafka sink
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema

sink = (
    KafkaSink.builder()
    .set_bootstrap_servers("localhost:9092")
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic("output-topic")
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    )
    .build()
)
ds.sink_to(sink)
```

## 🎯 When to Use What

| Task | Use |
|------|-----|
| Simple stateless transforms | DataStream `map`/`filter`/`flatMap` |
| Declarative queries/joins/aggregations | Table API / SQL |
| Fine-grained control + custom state | `KeyedProcessFunction` / `ProcessFunction` |
| Time-based aggregation | Windows (Tumbling/Sliding/Session) |
| CDC / changelog processing | Table API with changelog-aware connectors |
| Pattern detection across events | Flink CEP |
| Large state (> memory) | `EmbeddedRocksDBStateBackend` |

## ⚠️ Common Mistakes

### ❌ Don't
```python
# Don't use processing time when correctness/reproducibility matters
# (results vary depending on when the job actually runs)

# Don't forget key_by before using keyed state or windows
ds.process(MyKeyedProcessFunction())  # Fails: needs key_by first

# Don't let unbounded state grow forever without TTL
```

### ✅ Do
```python
# Use event time + watermarks for correctness
ds_with_time = ds.assign_timestamps_and_watermarks(strategy)

# key_by before keyed state/windows
ds.key_by(lambda x: x.user_id).process(MyKeyedProcessFunction())

# Configure state TTL to bound state size
from pyflink.datastream.state import StateTtlConfig
ttl_config = StateTtlConfig.new_builder(Time.hours(24)).build()
```

## 📊 Flink Web UI

Access at: **http://localhost:8081** (when running against a cluster)

- **Overview**: Running/completed jobs
- **Job Graph**: Visual DAG of operators
- **Checkpoints**: History, duration, size
- **Backpressure**: Identify slow operators
- **TaskManagers**: Resource usage, logs

## 🔗 Quick Links

- Examples: `01_datastream_basics.py` through `07_kafka_streaming_pipeline.py`
- Setup: `SETUP.md`
- Full docs: `README.md`
- Official: https://nightlies.apache.org/flink/flink-docs-stable/

## 💡 Remember

- **DataStream API**: Low-level, fine-grained control
- **Table API/SQL**: High-level, declarative, optimized (preferred when possible)
- **Event time + watermarks**: Use for correctness with out-of-order data
- **State**: First-class citizen — use `ValueState`/`ListState`/`MapState`
- **Checkpoints**: Automatic fault recovery; **Savepoints**: manual, for upgrades
- **RocksDB backend**: For state larger than memory
- **Flink Web UI**: Monitor job graphs, checkpoints, and backpressure

---

**Pro Tip**: Start with the Table API/SQL for straightforward pipelines, and drop down to the
DataStream API + `ProcessFunction` only when you need custom state/timers/logic! 🌊
