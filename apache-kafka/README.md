# Apache Kafka Complete Guide

## Table of Contents
1. [What is Apache Kafka?](#what-is-apache-kafka)
2. [Core Concepts](#core-concepts)
3. [Architecture Overview](#architecture-overview)
4. [Setup & Installation](#setup--installation)
5. [Producer Guide](#producer-guide)
6. [Consumer Guide](#consumer-guide)
7. [Kafka Streams](#kafka-streams)
8. [Advanced Features](#advanced-features)
9. [Real-World Use Cases](#real-world-use-cases)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## What is Apache Kafka?

**Apache Kafka** is a distributed event streaming platform capable of handling trillions of events a day.

### Key Points
- **Distributed**: Scalable across multiple servers
- **Fault-Tolerant**: Data replication and recovery
- **High-Throughput**: Millions of messages per second
- **Low-Latency**: Sub-millisecond message delivery
- **Durable**: Persistent storage on disk

### Why Use Apache Kafka?
✅ **Real-Time Processing**: Stream data in real-time  
✅ **Scalability**: Horizontally scalable  
✅ **Durability**: Messages persisted to disk  
✅ **High Availability**: Replication across brokers  
✅ **Decoupling**: Producers and consumers independent  
✅ **Replay**: Re-read historical data  

### Kafka vs Other Systems

| Feature | Kafka | RabbitMQ | AWS Kinesis | Apache Pulsar |
|---------|-------|----------|-------------|---------------|
| Throughput | Very High | Medium | High | Very High |
| Latency | Low | Very Low | Low | Low |
| Persistence | Yes | Optional | Yes | Yes |
| Replay | Yes | No | Limited | Yes |
| Ordering | Per Partition | Per Queue | Per Shard | Per Partition |
| Multi-tenancy | Limited | Good | N/A | Excellent |

---

## Core Concepts

### 1. Topic
A category or feed name to which records are published.

**Key Properties:**
- **Partitioned**: Divided into partitions for parallelism
- **Replicated**: Copies across brokers for fault tolerance
- **Ordered**: Messages ordered within partition
- **Immutable**: Messages cannot be changed once written

```bash
# Create topic
kafka-topics.sh --create \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 2
```

### 2. Partition
Ordered, immutable sequence of records within a topic.

**Key Concepts:**
- Each partition is an ordered log
- Messages get sequential ID (offset)
- Partitions enable parallelism
- Each partition has one leader and multiple replicas

```
Topic: orders (3 partitions)
┌─────────────────────────────────────┐
│ Partition 0: [msg0, msg3, msg6...] │
│ Partition 1: [msg1, msg4, msg7...] │
│ Partition 2: [msg2, msg5, msg8...] │
└─────────────────────────────────────┘
```

### 3. Producer
Application that publishes messages to topics.

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('my-topic', {'key': 'value'})
```

### 4. Consumer
Application that subscribes to topics and processes messages.

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```

### 5. Consumer Group
Group of consumers working together to consume a topic.

**Key Properties:**
- Each partition consumed by only one consumer in group
- Enables parallel processing
- Automatic rebalancing on consumer failure
- Each group maintains its own offset

```
Consumer Group: payment-processors
┌──────────────────────────────────────┐
│ Consumer 1 → Partition 0, 1          │
│ Consumer 2 → Partition 2             │
└──────────────────────────────────────┘
```

### 6. Broker
Kafka server that stores data and serves clients.

**Responsibilities:**
- Store messages
- Serve producer requests
- Serve consumer requests
- Manage partitions
- Replicate data

### 7. Offset
Unique identifier for each message within a partition.

**Types:**
- **Current Offset**: Last read position
- **Committed Offset**: Last successfully processed position
- **Log-End Offset**: Latest message in partition

### 8. Replication
Copies of partition data across multiple brokers.

**Key Concepts:**
- **Leader**: Handles all reads and writes
- **Follower**: Replicates leader data
- **ISR (In-Sync Replicas)**: Replicas caught up with leader
- **Replication Factor**: Number of copies

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kafka Cluster Architecture                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────────────┐
│  Producers   │         │      Kafka Cluster       │
│              │         │                          │
│ Producer 1   │────────►│  ┌────────────────────┐  │
│ Producer 2   │         │  │   Broker 1         │  │
│ Producer 3   │         │  │  - Partition 0 (L) │  │
└──────────────┘         │  │  - Partition 1 (F) │  │
                         │  │  - Partition 2 (F) │  │
                         │  └────────────────────┘  │
                         │                          │
                         │  ┌────────────────────┐  │
                         │  │   Broker 2         │  │
                         │  │  - Partition 0 (F) │  │
                         │  │  - Partition 1 (L) │  │
                         │  │  - Partition 2 (F) │  │
                         │  └────────────────────┘  │
                         │                          │
                         │  ┌────────────────────┐  │
                         │  │   Broker 3         │  │
                         │  │  - Partition 0 (F) │  │
                         │  │  - Partition 1 (F) │  │
                         │  │  - Partition 2 (L) │  │
                         │  └────────────────────┘  │
                         └──────────────────────────┘
                                     │
                                     ▼
                         ┌──────────────────────────┐
                         │    ZooKeeper Ensemble    │
                         │  (Cluster Coordination)  │
                         └──────────────────────────┘
                                     │
                                     ▼
┌──────────────┐         ┌──────────────────────────┐
│  Consumers   │         │    Consumer Groups       │
│              │◄────────│                          │
│ Consumer 1   │         │  Group 1: C1, C2         │
│ Consumer 2   │         │  Group 2: C3, C4, C5     │
│ Consumer 3   │         │                          │
└──────────────┘         └──────────────────────────┘

L = Leader, F = Follower
```

### Components Explained

**1. Producer**
- Publishes messages to topics
- Chooses partition (round-robin, key-based, custom)
- Batches messages for efficiency
- Handles retries and acknowledgments

**2. Broker**
- Stores messages on disk
- Manages partitions
- Handles replication
- Serves read/write requests

**3. Consumer**
- Subscribes to topics
- Reads messages from partitions
- Commits offsets
- Part of consumer group

**4. ZooKeeper** (being replaced by KRaft)
- Cluster coordination
- Leader election
- Configuration management
- Broker discovery

**5. Topic**
- Logical channel for messages
- Divided into partitions
- Replicated across brokers
- Configurable retention

---

## Setup & Installation

See detailed guide in SETUP.md

### Quick Start

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0

# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka (in another terminal)
bin/kafka-server-start.sh config/server.properties

# Create topic
bin/kafka-topics.sh --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# List topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## Producer Guide

### Basic Producer

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('my-topic', {'message': 'Hello Kafka'})
producer.flush()
```

### Producer with Key

```python
# Messages with same key go to same partition
producer.send(
    'my-topic',
    key=b'user-123',
    value={'user_id': 123, 'action': 'login'}
)
```

### Producer with Callback

```python
def on_success(metadata):
    print(f"Message sent to {metadata.topic} partition {metadata.partition} offset {metadata.offset}")

def on_error(e):
    print(f"Error: {e}")

future = producer.send('my-topic', {'data': 'value'})
future.add_callback(on_success)
future.add_errback(on_error)
```

### Producer Configuration

```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    
    # Serialization
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    
    # Acknowledgments
    acks='all',  # 0, 1, or 'all'
    
    # Retries
    retries=3,
    retry_backoff_ms=100,
    
    # Batching
    batch_size=16384,
    linger_ms=10,
    
    # Compression
    compression_type='gzip',  # None, gzip, snappy, lz4, zstd
    
    # Buffer
    buffer_memory=33554432,
    max_block_ms=60000,
)
```

---

## Consumer Guide

### Basic Consumer

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

for message in consumer:
    print(f"Topic: {message.topic}")
    print(f"Partition: {message.partition}")
    print(f"Offset: {message.offset}")
    print(f"Key: {message.key}")
    print(f"Value: {message.value}")
```

### Consumer with Manual Commit

```python
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    enable_auto_commit=False,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    # Process message
    process_message(message.value)
    
    # Manually commit offset
    consumer.commit()
```

### Consumer Configuration

```python
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    
    # Consumer group
    group_id='my-group',
    
    # Offset management
    auto_offset_reset='earliest',  # earliest, latest, none
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
    
    # Deserialization
    key_deserializer=lambda k: k.decode('utf-8'),
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    
    # Fetch settings
    fetch_min_bytes=1,
    fetch_max_wait_ms=500,
    max_partition_fetch_bytes=1048576,
    
    # Session
    session_timeout_ms=10000,
    heartbeat_interval_ms=3000,
)
```

---

## Kafka Streams

### What is Kafka Streams?

Client library for building stream processing applications.

**Features:**
- Stateful and stateless processing
- Windowing operations
- Joins between streams
- Aggregations
- Exactly-once semantics

### Stream Processing Example

```python
# Using kafka-python (basic streaming)
from kafka import KafkaConsumer, KafkaProducer
import json

# Input consumer
input_consumer = KafkaConsumer(
    'input-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Output producer
output_producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Stream processing
for message in input_consumer:
    # Transform
    transformed = transform_data(message.value)
    
    # Filter
    if should_process(transformed):
        # Enrich
        enriched = enrich_data(transformed)
        
        # Send to output topic
        output_producer.send('output-topic', enriched)
```

---

## Advanced Features

### 1. Partitioning Strategies

```python
# Round-robin (default)
producer.send('topic', value={'data': 'value'})

# Key-based partitioning
producer.send('topic', key=b'user-123', value={'data': 'value'})

# Custom partitioner
from kafka.partitioner import Partitioner

class CustomPartitioner(Partitioner):
    def partition(self, key, all_partitions, available_partitions):
        # Custom logic
        return hash(key) % len(all_partitions)

producer = KafkaProducer(partitioner=CustomPartitioner())
```

### 2. Message Compression

```python
producer = KafkaProducer(
    compression_type='gzip'  # gzip, snappy, lz4, zstd
)
```

### 3. Transactions

```python
producer = KafkaProducer(
    transactional_id='my-transactional-id',
    enable_idempotence=True
)

producer.init_transactions()

try:
    producer.begin_transaction()
    producer.send('topic1', {'data': 'value1'})
    producer.send('topic2', {'data': 'value2'})
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
```

### 4. Exactly-Once Semantics

```python
# Producer
producer = KafkaProducer(
    enable_idempotence=True,
    transactional_id='my-transaction-id'
)

# Consumer
consumer = KafkaConsumer(
    isolation_level='read_committed'
)
```

### 5. Schema Registry (with Avro)

```python
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

value_schema = avro.loads('''
{
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"}
    ]
}
''')

producer = AvroProducer({
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
}, default_value_schema=value_schema)

producer.produce(topic='users', value={'name': 'John', 'age': 30})
```

---

## Real-World Use Cases

### 1. Event Sourcing
Store all changes as sequence of events.

```
User Actions → Kafka → Event Store → Rebuild State
```

### 2. Log Aggregation
Collect logs from multiple services.

```
Service Logs → Kafka → Log Processing → Elasticsearch
```

### 3. Stream Processing
Real-time data transformation.

```
Clickstream → Kafka → Stream Processing → Analytics
```

### 4. Messaging
Decouple microservices.

```
Service A → Kafka → Service B, C, D
```

### 5. Metrics & Monitoring
Collect system metrics.

```
Metrics → Kafka → Monitoring System → Alerts
```

### 6. CDC (Change Data Capture)
Track database changes.

```
Database → Debezium → Kafka → Data Warehouse
```

---

## Best Practices

### Producer Best Practices

✅ **Use Batching**: Improve throughput with batching  
✅ **Enable Compression**: Reduce network usage  
✅ **Set Appropriate Acks**: Balance durability and performance  
✅ **Handle Failures**: Implement retry logic  
✅ **Use Keys Wisely**: For ordering and partitioning  
✅ **Monitor Metrics**: Track producer performance  

❌ **Don't**: Send very large messages (> 1MB)  
❌ **Don't**: Ignore producer exceptions  
❌ **Don't**: Use synchronous sends for high throughput  

### Consumer Best Practices

✅ **Use Consumer Groups**: Enable parallel processing  
✅ **Commit Offsets Carefully**: Avoid data loss or duplication  
✅ **Handle Rebalancing**: Implement rebalance listeners  
✅ **Set Appropriate Timeouts**: Avoid unnecessary rebalances  
✅ **Process Idempotently**: Handle duplicate messages  
✅ **Monitor Lag**: Track consumer lag  

❌ **Don't**: Process messages too slowly  
❌ **Don't**: Commit before processing  
❌ **Don't**: Ignore consumer errors  

### Topic Design

✅ **Choose Partition Count Wisely**: Based on throughput needs  
✅ **Set Replication Factor**: At least 2 for production  
✅ **Configure Retention**: Based on use case  
✅ **Use Meaningful Names**: Clear topic naming  
✅ **Plan for Growth**: Partitions can't be reduced  

### Performance

✅ **Tune Batch Size**: Balance latency and throughput  
✅ **Use Compression**: Reduce network and storage  
✅ **Optimize Partition Count**: Match consumer parallelism  
✅ **Monitor Broker Metrics**: CPU, disk, network  
✅ **Use Fast Disks**: SSDs for better performance  

---

## Troubleshooting

### Issue 1: Consumer Lag

**Symptoms:**
- Messages piling up
- Slow processing
- Increasing lag

**Solutions:**
```bash
# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group --describe

# Solutions:
# 1. Add more consumers
# 2. Increase partitions
# 3. Optimize processing logic
# 4. Increase fetch size
```

### Issue 2: Rebalancing Issues

**Symptoms:**
- Frequent rebalances
- Processing interruptions
- Duplicate processing

**Solutions:**
```python
# Increase session timeout
consumer = KafkaConsumer(
    session_timeout_ms=30000,
    heartbeat_interval_ms=10000,
    max_poll_interval_ms=300000
)
```

### Issue 3: Message Loss

**Causes:**
- Producer not waiting for acks
- Consumer committing before processing
- Insufficient replication

**Solutions:**
```python
# Producer: Wait for all replicas
producer = KafkaProducer(acks='all')

# Consumer: Manual commit after processing
consumer.commit()
```

### Issue 4: Duplicate Messages

**Causes:**
- Consumer rebalancing
- Processing failure before commit
- Network issues

**Solutions:**
- Implement idempotent processing
- Use exactly-once semantics
- Deduplicate based on message ID

### Issue 5: Broker Disk Full

**Solutions:**
```bash
# Check disk usage
df -h

# Reduce retention
kafka-configs.sh --alter --entity-type topics \
  --entity-name my-topic \
  --add-config retention.ms=86400000

# Add more brokers
# Increase partition count
```

---

## Monitoring

### Key Metrics

**Producer Metrics:**
- Record send rate
- Record error rate
- Request latency
- Batch size

**Consumer Metrics:**
- Records consumed rate
- Consumer lag
- Commit latency
- Rebalance rate

**Broker Metrics:**
- Messages in per second
- Bytes in per second
- Request queue size
- Under-replicated partitions

### Monitoring Tools

- **Kafka Manager**: Web-based management
- **Confluent Control Center**: Enterprise monitoring
- **Prometheus + Grafana**: Metrics visualization
- **Burrow**: Consumer lag monitoring

---

## Resources

- **Official Docs**: https://kafka.apache.org/documentation/
- **GitHub**: https://github.com/apache/kafka
- **Confluent**: https://docs.confluent.io/
- **Stack Overflow**: Tag `apache-kafka`

---

## Next Steps

1. Complete setup (see SETUP.md)
2. Run producer examples (01-03)
3. Run consumer examples (04-06)
4. Explore Kafka Streams (07-08)
5. Build your first pipeline
6. Deploy to production

---

**Remember**: Kafka is a distributed commit log - messages are durable, ordered, and replayable!
