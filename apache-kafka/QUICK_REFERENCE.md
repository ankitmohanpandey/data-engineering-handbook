# Apache Kafka Quick Reference Card

## 🚀 Quick Start

```bash
# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties

# Create topic
bin/kafka-topics.sh --create --topic test --bootstrap-server localhost:9092 --partitions 3

# Python producer
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('test', b'Hello Kafka')

# Python consumer
from kafka import KafkaConsumer
consumer = KafkaConsumer('test', bootstrap_servers=['localhost:9092'])
for msg in consumer:
    print(msg.value)
```

---

## 📋 Core Concepts

| Concept | Description |
|---------|-------------|
| **Topic** | Category/feed for messages |
| **Partition** | Ordered log within topic |
| **Producer** | Publishes messages to topics |
| **Consumer** | Subscribes to topics |
| **Consumer Group** | Group of consumers sharing work |
| **Broker** | Kafka server |
| **Offset** | Unique message ID in partition |
| **Replication** | Copies of partitions across brokers |

---

## 🔧 Topic Commands

```bash
# Create topic
kafka-topics.sh --create \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 2

# List topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe topic
kafka-topics.sh --describe --topic my-topic --bootstrap-server localhost:9092

# Delete topic
kafka-topics.sh --delete --topic my-topic --bootstrap-server localhost:9092

# Alter partitions
kafka-topics.sh --alter --topic my-topic --partitions 5 --bootstrap-server localhost:9092
```

---

## 📤 Producer (Python)

### Basic Producer
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('topic', {'key': 'value'})
producer.flush()
```

### Producer with Key
```python
producer.send('topic', key=b'user-123', value={'data': 'value'})
```

### Synchronous Send
```python
future = producer.send('topic', {'data': 'value'})
metadata = future.get(timeout=10)
print(f"Partition: {metadata.partition}, Offset: {metadata.offset}")
```

### With Callback
```python
def on_success(metadata):
    print(f"Sent to {metadata.partition}:{metadata.offset}")

future = producer.send('topic', {'data': 'value'})
future.add_callback(on_success)
```

### Producer Configuration
```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    acks='all',              # 0, 1, 'all'
    retries=3,
    batch_size=16384,
    linger_ms=10,
    compression_type='gzip', # gzip, snappy, lz4, zstd
    max_in_flight_requests_per_connection=5
)
```

---

## 📥 Consumer (Python)

### Basic Consumer
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'  # earliest, latest, none
)

for message in consumer:
    print(f"Partition: {message.partition}")
    print(f"Offset: {message.offset}")
    print(f"Value: {message.value}")
```

### Manual Commit
```python
consumer = KafkaConsumer(
    'topic',
    enable_auto_commit=False,
    bootstrap_servers=['localhost:9092']
)

for message in consumer:
    process(message)
    consumer.commit()  # Commit after processing
```

### Seek to Offset
```python
from kafka import TopicPartition

partition = TopicPartition('topic', 0)
consumer.assign([partition])
consumer.seek(partition, 100)  # Seek to offset 100
```

### Consumer Configuration
```python
consumer = KafkaConsumer(
    'topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
    max_poll_records=500,
    session_timeout_ms=10000,
    heartbeat_interval_ms=3000
)
```

---

## 🎯 Console Tools

### Console Producer
```bash
# Basic
kafka-console-producer.sh --topic test --bootstrap-server localhost:9092

# With key
kafka-console-producer.sh --topic test --bootstrap-server localhost:9092 \
  --property "parse.key=true" --property "key.separator=:"
```

### Console Consumer
```bash
# From latest
kafka-console-consumer.sh --topic test --bootstrap-server localhost:9092

# From beginning
kafka-console-consumer.sh --topic test --bootstrap-server localhost:9092 --from-beginning

# With group
kafka-console-consumer.sh --topic test --bootstrap-server localhost:9092 --group my-group

# Show keys
kafka-console-consumer.sh --topic test --bootstrap-server localhost:9092 \
  --property print.key=true --property key.separator=":"
```

---

## 👥 Consumer Groups

```bash
# List groups
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# Describe group
kafka-consumer-groups.sh --describe --group my-group --bootstrap-server localhost:9092

# Reset offsets to earliest
kafka-consumer-groups.sh --group my-group --topic test \
  --reset-offsets --to-earliest --execute --bootstrap-server localhost:9092

# Reset to specific offset
kafka-consumer-groups.sh --group my-group --topic test:0 \
  --reset-offsets --to-offset 100 --execute --bootstrap-server localhost:9092

# Reset to datetime
kafka-consumer-groups.sh --group my-group --topic test \
  --reset-offsets --to-datetime 2024-01-01T00:00:00.000 --execute --bootstrap-server localhost:9092
```

---

## ⚙️ Configuration

### Producer Settings

| Setting | Values | Description |
|---------|--------|-------------|
| `acks` | 0, 1, 'all' | Acknowledgment level |
| `retries` | int | Retry attempts |
| `batch_size` | bytes | Batch size |
| `linger_ms` | ms | Wait time for batch |
| `compression_type` | none, gzip, snappy, lz4, zstd | Compression |
| `max_in_flight_requests_per_connection` | int | Concurrent requests |

### Consumer Settings

| Setting | Values | Description |
|---------|--------|-------------|
| `group_id` | string | Consumer group ID |
| `auto_offset_reset` | earliest, latest, none | Starting offset |
| `enable_auto_commit` | bool | Auto-commit offsets |
| `auto_commit_interval_ms` | ms | Commit interval |
| `max_poll_records` | int | Records per poll |
| `session_timeout_ms` | ms | Session timeout |

---

## 🔄 Partitioning

### Default (Round-Robin)
```python
producer.send('topic', value)  # No key
```

### Key-Based
```python
producer.send('topic', key=b'user-123', value=data)
# Same key → same partition
```

### Custom Partitioner
```python
from kafka.partitioner import Partitioner

class CustomPartitioner(Partitioner):
    def partition(self, key, all_partitions, available_partitions):
        return hash(key) % len(all_partitions)

producer = KafkaProducer(partitioner=CustomPartitioner())
```

---

## 🔒 Advanced Features

### Idempotent Producer
```python
producer = KafkaProducer(
    enable_idempotence=True,
    acks='all',
    retries=3
)
```

### Transactions
```python
producer = KafkaProducer(
    transactional_id='my-id',
    enable_idempotence=True
)

producer.init_transactions()
producer.begin_transaction()
producer.send('topic', data)
producer.commit_transaction()
```

### Message Headers
```python
headers = [('key', b'value')]
producer.send('topic', value=data, headers=headers)
```

---

## 📊 Monitoring Commands

```bash
# Broker API versions
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Log directories
kafka-log-dirs.sh --describe --bootstrap-server localhost:9092

# Dump log segment
kafka-dump-log.sh --files /tmp/kafka-logs/test-0/00000000000000000000.log

# Get offsets
kafka-get-offsets.sh --topic test --bootstrap-server localhost:9092
```

---

## 🎨 Message Formats

### JSON
```python
# Producer
value_serializer=lambda v: json.dumps(v).encode('utf-8')

# Consumer
value_deserializer=lambda m: json.loads(m.decode('utf-8'))
```

### String
```python
# Producer
value_serializer=lambda v: v.encode('utf-8')

# Consumer
value_deserializer=lambda m: m.decode('utf-8')
```

### Bytes
```python
# No serializer/deserializer needed
producer.send('topic', b'raw bytes')
```

---

## 🔍 Offset Management

```python
# Get current offset
consumer.position(TopicPartition('topic', 0))

# Get committed offset
consumer.committed(TopicPartition('topic', 0))

# Seek to beginning
consumer.seek_to_beginning()

# Seek to end
consumer.seek_to_end()

# Seek to specific offset
consumer.seek(TopicPartition('topic', 0), 100)
```

---

## ⚡ Performance Tips

### Producer
✅ Enable batching (`batch_size`, `linger_ms`)  
✅ Use compression (`compression_type`)  
✅ Async sends (default)  
✅ Tune `buffer_memory`  
✅ Use idempotence for safety  

### Consumer
✅ Use consumer groups for parallelism  
✅ Tune `fetch_min_bytes` and `fetch_max_wait_ms`  
✅ Batch process messages  
✅ Manual commit for control  
✅ Monitor consumer lag  

### Broker
✅ Use multiple brokers  
✅ Set replication factor ≥ 2  
✅ Use fast disks (SSD)  
✅ Tune `num.io.threads`  
✅ Enable compression  

---

## 🐛 Common Issues

### Connection Refused
```bash
# Check if Kafka is running
jps | grep Kafka

# Check port
lsof -i :9092

# Verify bootstrap servers
telnet localhost 9092
```

### Topic Not Found
```bash
# List topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Create topic
kafka-topics.sh --create --topic test --bootstrap-server localhost:9092
```

### Consumer Lag
```bash
# Check lag
kafka-consumer-groups.sh --describe --group my-group --bootstrap-server localhost:9092

# Solutions:
# - Add more consumers
# - Increase partitions
# - Optimize processing
```

---

## 📚 Guarantees

### At-Most-Once
```python
# Auto-commit before processing
consumer = KafkaConsumer(enable_auto_commit=True)
for msg in consumer:
    process(msg)  # May lose if crashes
```

### At-Least-Once
```python
# Manual commit after processing
consumer = KafkaConsumer(enable_auto_commit=False)
for msg in consumer:
    process(msg)
    consumer.commit()  # May duplicate if crashes
```

### Exactly-Once
```python
# Transactions + idempotence
producer = KafkaProducer(
    transactional_id='id',
    enable_idempotence=True
)
consumer = KafkaConsumer(
    isolation_level='read_committed'
)
```

---

## 🎯 Use Cases

- **Messaging**: Decouple microservices
- **Event Sourcing**: Store all events
- **Log Aggregation**: Collect logs
- **Stream Processing**: Real-time analytics
- **Metrics**: Collect system metrics
- **CDC**: Database change capture

---

## 📖 Resources

- **Docs**: https://kafka.apache.org/documentation/
- **Quickstart**: https://kafka.apache.org/quickstart
- **Python Client**: https://kafka-python.readthedocs.io/
- **Confluent**: https://docs.confluent.io/

---

## ✅ Quick Checklist

- [ ] Java installed
- [ ] Kafka downloaded
- [ ] ZooKeeper started
- [ ] Kafka broker started
- [ ] Topic created
- [ ] Python client installed
- [ ] Producer working
- [ ] Consumer working

---

**Happy Streaming! 🚀**
