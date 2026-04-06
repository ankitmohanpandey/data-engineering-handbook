# Apache Cassandra Learning Repository

> **Comprehensive guide to learning Apache Cassandra - from basics to production-ready distributed NoSQL database**

A structured learning repository for mastering Cassandra, CQL, data modeling, cluster management, and building scalable applications.

---

## 📚 Table of Contents

1. [What is Apache Cassandra?](#what-is-apache-cassandra)
2. [Repository Structure](#repository-structure)
3. [Core Concepts](#core-concepts)
4. [Quick Start](#quick-start)
5. [Learning Path](#learning-path)
6. [Examples](#examples)
7. [Resources](#resources)

---

## What is Apache Cassandra?

**Apache Cassandra** is a highly scalable, distributed NoSQL database designed to handle massive amounts of data across multiple data centers with no single point of failure.

### Key Features

- **Distributed**: No single point of failure, peer-to-peer architecture
- **Scalable**: Linear scalability - add nodes without downtime
- **High Availability**: Replication across multiple nodes and data centers
- **Fault Tolerant**: Automatic data replication and failure handling
- **Tunable Consistency**: Choose between consistency and availability
- **High Performance**: Optimized for write-heavy workloads

### When to Use Cassandra

✅ **Good For**:
- Time-series data (IoT, logs, metrics)
- High write throughput applications
- Multi-datacenter deployments
- Always-on applications (99.999% uptime)
- Large-scale data (petabytes)
- Real-time analytics

❌ **Not Ideal For**:
- Complex joins and aggregations
- ACID transactions across rows
- Ad-hoc queries
- Small datasets (< 1TB)
- Frequent schema changes

### Cassandra vs Other Databases

| Feature | Cassandra | MongoDB | PostgreSQL | Redis |
|---------|-----------|---------|------------|-------|
| **Type** | Wide-column | Document | Relational | Key-Value |
| **Scalability** | Horizontal | Horizontal | Vertical | Horizontal |
| **Consistency** | Tunable | Strong | Strong | Eventual |
| **Writes** | Excellent | Good | Good | Excellent |
| **Joins** | No | Limited | Yes | No |
| **Use Case** | Time-series | General | OLTP | Caching |

---

## Repository Structure

```
apache-cassandra/
│
├── README.md                          # This file
├── SETUP.md                           # Installation & setup guide
├── QUICK_REFERENCE.md                # CQL commands cheatsheet
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore patterns
│
├── 01_basics/                        # Cassandra Fundamentals
│   ├── README.md                     # Basic concepts
│   ├── architecture.md               # Architecture deep-dive
│   ├── data_model.md                 # Data modeling principles
│   └── examples/
│       ├── simple_keyspace.cql      # Create keyspace
│       ├── simple_table.cql         # Create tables
│       └── basic_operations.cql     # CRUD operations
│
├── 02_cql/                           # Cassandra Query Language
│   ├── README.md                     # CQL overview
│   ├── ddl_commands.cql             # Data Definition Language
│   ├── dml_commands.cql             # Data Manipulation Language
│   ├── data_types.cql               # All data types
│   └── examples/
│       ├── collections.cql          # Lists, Sets, Maps
│       ├── user_defined_types.cql   # UDTs
│       └── secondary_indexes.cql    # Indexing
│
├── 03_data_modeling/                 # Data Modeling Patterns
│   ├── README.md                     # Modeling principles
│   ├── query_first_design.md        # Query-driven design
│   ├── partition_keys.md            # Partition key design
│   ├── clustering_columns.md        # Clustering design
│   └── examples/
│       ├── time_series_model.cql    # Time-series pattern
│       ├── user_profile_model.cql   # User data pattern
│       ├── messaging_model.cql      # Messaging pattern
│       └── sensor_data_model.cql    # IoT pattern
│
├── 04_python_driver/                 # Python Integration
│   ├── README.md                     # Driver overview
│   ├── connection.py                # Connect to cluster
│   ├── crud_operations.py           # CRUD with Python
│   ├── batch_operations.py          # Batch inserts
│   ├── async_operations.py          # Async queries
│   └── examples/
│       ├── user_management.py       # User CRUD app
│       ├── time_series_writer.py    # Time-series ingestion
│       ├── pagination.py            # Paginate results
│       └── prepared_statements.py   # Prepared statements
│
├── 05_advanced_features/             # Advanced Cassandra
│   ├── README.md                     # Advanced topics
│   ├── materialized_views.cql       # Materialized views
│   ├── counters.cql                 # Counter columns
│   ├── lightweight_transactions.cql # LWT (Paxos)
│   ├── ttl_and_tombstones.md        # TTL & deletion
│   └── examples/
│       ├── counter_example.py       # Counter use case
│       ├── ttl_example.py           # TTL patterns
│       └── lwt_example.py           # Conditional updates
│
├── 06_cluster_management/            # Cluster Operations
│   ├── README.md                     # Cluster management
│   ├── replication_strategy.md      # Replication config
│   ├── consistency_levels.md        # Consistency tuning
│   ├── node_operations.md           # Add/remove nodes
│   └── examples/
│       ├── multi_dc_setup.md        # Multi-datacenter
│       ├── backup_restore.sh        # Backup strategies
│       └── repair_operations.sh     # Nodetool repair
│
├── 07_performance_tuning/            # Performance Optimization
│   ├── README.md                     # Tuning guide
│   ├── read_optimization.md         # Read performance
│   ├── write_optimization.md        # Write performance
│   ├── compaction_strategies.md     # Compaction tuning
│   └── examples/
│       ├── partition_size_check.py  # Monitor partitions
│       ├── query_tracing.py         # Trace queries
│       └── metrics_monitoring.py    # Collect metrics
│
├── 08_monitoring/                    # Monitoring & Observability
│   ├── README.md                     # Monitoring guide
│   ├── nodetool_commands.md         # Nodetool reference
│   ├── metrics.md                   # Key metrics
│   ├── grafana_dashboards/          # Grafana configs
│   └── examples/
│       ├── health_check.py          # Cluster health
│       ├── prometheus_exporter.py   # Prometheus metrics
│       └── alerting_rules.yaml      # Alert rules
│
├── 09_integration/                   # Integration Patterns
│   ├── README.md                     # Integration overview
│   ├── kafka_cassandra/             # Kafka → Cassandra
│   ├── spark_cassandra/             # Spark analytics
│   ├── airflow_cassandra/           # Airflow pipelines
│   └── examples/
│       ├── kafka_consumer.py        # Stream to Cassandra
│       ├── spark_analytics.py       # Spark + Cassandra
│       └── rest_api.py              # REST API with FastAPI
│
├── 10_real_world_projects/           # Complete Projects
│   ├── README.md                     # Projects overview
│   ├── iot_sensor_platform/         # IoT data platform
│   ├── user_activity_tracker/       # User analytics
│   ├── messaging_app/               # Chat application
│   ├── time_series_analytics/       # Metrics platform
│   └── e_commerce_catalog/          # Product catalog
│
└── docs/                             # Additional Documentation
    ├── best_practices.md            # Best practices
    ├── anti_patterns.md             # What to avoid
    ├── migration_guide.md           # Migration strategies
    ├── security.md                  # Security guide
    └── troubleshooting.md           # Common issues
```

---

## Core Concepts

### 1. Cassandra Architecture

#### Distributed & Peer-to-Peer

```
┌─────────────────────────────────────────┐
│         Cassandra Cluster                │
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐│
│  │Node 1│  │Node 2│  │Node 3│  │Node 4││
│  │      │  │      │  │      │  │      ││
│  │ Data │  │ Data │  │ Data │  │ Data ││
│  └──────┘  └──────┘  └──────┘  └──────┘│
│      ↕         ↕         ↕         ↕    │
│  ┌──────────────────────────────────┐  │
│  │   Gossip Protocol (P2P Comm)    │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Points**:
- No master node - all nodes are equal
- Gossip protocol for node communication
- Consistent hashing for data distribution
- Virtual nodes (vnodes) for better distribution

#### Data Distribution

```
Token Ring (Hash Ring)
        0
    ┌───┴───┐
  Node4   Node1
    │       │
  Node3   Node2
    └───┬───┘
       256
```

**Key Points**:
- Data distributed based on partition key hash
- Each node responsible for a token range
- Replication factor determines copies
- Tunable consistency levels

---

### 2. Data Model

#### Keyspace → Table → Row

```
Keyspace (like database)
  └── Table (column family)
      ├── Partition Key (determines node)
      ├── Clustering Columns (sort order)
      └── Regular Columns (data)
```

#### Example Table Structure

```cql
CREATE TABLE user_activity (
    user_id UUID,           -- Partition Key
    activity_date DATE,     -- Clustering Column
    activity_time TIMESTAMP,-- Clustering Column
    activity_type TEXT,
    details MAP<TEXT, TEXT>,
    PRIMARY KEY ((user_id), activity_date, activity_time)
) WITH CLUSTERING ORDER BY (activity_date DESC, activity_time DESC);
```

**Key Points**:
- Partition key determines data location
- Clustering columns define sort order within partition
- Query patterns drive data model design
- Denormalization is common

---

### 3. CQL (Cassandra Query Language)

#### Basic Operations

```cql
-- Create Keyspace
CREATE KEYSPACE my_app 
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

-- Create Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);

-- Insert Data
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'john_doe', 'john@example.com', toTimestamp(now()));

-- Query Data
SELECT * FROM users WHERE user_id = ?;

-- Update Data
UPDATE users SET email = 'newemail@example.com' WHERE user_id = ?;

-- Delete Data
DELETE FROM users WHERE user_id = ?;
```

---

### 4. Replication & Consistency

#### Replication Strategy

```cql
-- Simple Strategy (single datacenter)
CREATE KEYSPACE my_app 
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

-- Network Topology Strategy (multi-datacenter)
CREATE KEYSPACE my_app 
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 2
};
```

#### Consistency Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **ONE** | 1 replica responds | Low latency reads |
| **QUORUM** | Majority responds | Balanced |
| **ALL** | All replicas respond | Strong consistency |
| **LOCAL_QUORUM** | Majority in local DC | Multi-DC apps |

**CAP Theorem Trade-off**:
- Cassandra favors **Availability** and **Partition Tolerance**
- Consistency is **tunable** per query

---

## Quick Start

### Prerequisites

- Java 8 or 11
- Python 3.7+ (for examples)
- 4GB+ RAM
- Linux/Mac (or WSL on Windows)

### Installation

#### Option 1: Docker (Recommended for Learning)

```bash
# Pull Cassandra image
docker pull cassandra:latest

# Run single node
docker run --name cassandra -p 9042:9042 -d cassandra:latest

# Wait for startup (30-60 seconds)
docker logs -f cassandra

# Connect with cqlsh
docker exec -it cassandra cqlsh
```

#### Option 2: Local Installation

```bash
# macOS
brew install cassandra

# Ubuntu/Debian
echo "deb https://debian.cassandra.apache.org 41x main" | sudo tee /etc/apt/sources.list.d/cassandra.list
curl https://downloads.apache.org/cassandra/KEYS | sudo apt-key add -
sudo apt update
sudo apt install cassandra

# Start Cassandra
cassandra -f  # Foreground
# OR
sudo systemctl start cassandra  # Background
```

### First Example

```bash
# 1. Connect to Cassandra
cqlsh

# 2. Create keyspace
CREATE KEYSPACE demo 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

# 3. Use keyspace
USE demo;

# 4. Create table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP
);

# 5. Insert data
INSERT INTO users (user_id, name, email, created_at)
VALUES (uuid(), 'Alice', 'alice@example.com', toTimestamp(now()));

# 6. Query data
SELECT * FROM users;

# 7. Exit
exit;
```

---

## Learning Path

### 🟢 Week 1-2: Fundamentals

**Objectives**:
- Understand Cassandra architecture
- Learn basic CQL commands
- Understand data modeling principles

**Topics**:
- Distributed architecture
- Partition keys and clustering columns
- Replication and consistency
- Basic CRUD operations

**Practice**:
- Install Cassandra
- Create keyspaces and tables
- Insert and query data
- Explore cqlsh

**Resources**: `01_basics/`, `02_cql/`

---

### 🟡 Week 3-4: Data Modeling

**Objectives**:
- Master query-first design
- Learn modeling patterns
- Understand partition design

**Topics**:
- Query-driven data modeling
- Partition key selection
- Clustering column design
- Time-series patterns
- Denormalization strategies

**Practice**:
- Model user activity tracking
- Design time-series schema
- Create messaging app schema
- Optimize for query patterns

**Resources**: `03_data_modeling/`

---

### 🟡 Week 5-6: Python Integration

**Objectives**:
- Use Python driver
- Build applications
- Handle async operations

**Topics**:
- Cassandra Python driver
- Connection pooling
- Prepared statements
- Batch operations
- Async queries

**Practice**:
- Build CRUD application
- Implement time-series writer
- Create REST API
- Handle pagination

**Resources**: `04_python_driver/`, `09_integration/`

---

### 🔴 Week 7-8: Advanced & Production

**Objectives**:
- Master advanced features
- Learn cluster management
- Production best practices

**Topics**:
- Materialized views
- Counters and LWT
- TTL and tombstones
- Cluster operations
- Performance tuning
- Monitoring

**Practice**:
- Setup multi-node cluster
- Implement monitoring
- Tune performance
- Build production app

**Resources**: `05_advanced_features/`, `06_cluster_management/`, `07_performance_tuning/`

---

## Examples

### Example 1: Simple CRUD Operations

```python
# 04_python_driver/crud_operations.py
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid

# Connect to cluster
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# Create keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS demo
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")

# Use keyspace
session.set_keyspace('demo')

# Create table
session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id UUID PRIMARY KEY,
        username TEXT,
        email TEXT,
        created_at TIMESTAMP
    )
""")

# Insert data
user_id = uuid.uuid4()
session.execute("""
    INSERT INTO users (user_id, username, email, created_at)
    VALUES (%s, %s, %s, toTimestamp(now()))
""", (user_id, 'john_doe', 'john@example.com'))

# Query data
rows = session.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
for row in rows:
    print(f"User: {row.username}, Email: {row.email}")

# Update data
session.execute("""
    UPDATE users SET email = %s WHERE user_id = %s
""", ('newemail@example.com', user_id))

# Delete data
session.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

# Close connection
cluster.shutdown()
```

---

### Example 2: Time-Series Data Model

```cql
-- 03_data_modeling/examples/time_series_model.cql

-- Sensor data time-series
CREATE TABLE sensor_data (
    sensor_id UUID,
    year INT,
    month INT,
    day INT,
    timestamp TIMESTAMP,
    temperature DECIMAL,
    humidity DECIMAL,
    pressure DECIMAL,
    PRIMARY KEY ((sensor_id, year, month, day), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_size': 1,
    'compaction_window_unit': 'DAYS'
  };

-- Insert sensor reading
INSERT INTO sensor_data (sensor_id, year, month, day, timestamp, temperature, humidity, pressure)
VALUES (uuid(), 2024, 3, 31, toTimestamp(now()), 22.5, 65.0, 1013.25);

-- Query last 24 hours for a sensor
SELECT * FROM sensor_data
WHERE sensor_id = ? 
  AND year = 2024 
  AND month = 3 
  AND day = 31
  AND timestamp > toTimestamp(now()) - 86400000
ORDER BY timestamp DESC;
```

---

### Example 3: User Activity Tracking

```python
# 04_python_driver/examples/user_management.py
from cassandra.cluster import Cluster
from datetime import datetime, timedelta
import uuid

class UserActivityTracker:
    def __init__(self, contact_points=['127.0.0.1']):
        self.cluster = Cluster(contact_points)
        self.session = self.cluster.connect()
        self.setup_schema()
    
    def setup_schema(self):
        # Create keyspace
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS user_tracking
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        
        self.session.set_keyspace('user_tracking')
        
        # Create table
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id UUID,
                activity_date DATE,
                activity_time TIMESTAMP,
                activity_type TEXT,
                page_url TEXT,
                duration_seconds INT,
                PRIMARY KEY ((user_id, activity_date), activity_time)
            ) WITH CLUSTERING ORDER BY (activity_time DESC)
        """)
    
    def track_activity(self, user_id, activity_type, page_url, duration):
        """Track user activity"""
        now = datetime.now()
        
        self.session.execute("""
            INSERT INTO user_activity 
            (user_id, activity_date, activity_time, activity_type, page_url, duration_seconds)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, now.date(), now, activity_type, page_url, duration))
    
    def get_user_activity_today(self, user_id):
        """Get all activity for user today"""
        today = datetime.now().date()
        
        rows = self.session.execute("""
            SELECT * FROM user_activity
            WHERE user_id = %s AND activity_date = %s
            ORDER BY activity_time DESC
        """, (user_id, today))
        
        return list(rows)
    
    def get_activity_summary(self, user_id, days=7):
        """Get activity summary for last N days"""
        activities = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            rows = self.session.execute("""
                SELECT COUNT(*) as count, SUM(duration_seconds) as total_duration
                FROM user_activity
                WHERE user_id = %s AND activity_date = %s
            """, (user_id, date))
            
            for row in rows:
                activities.append({
                    'date': date,
                    'count': row.count,
                    'total_duration': row.total_duration
                })
        
        return activities
    
    def close(self):
        self.cluster.shutdown()

# Usage
if __name__ == '__main__':
    tracker = UserActivityTracker()
    
    user_id = uuid.uuid4()
    
    # Track activities
    tracker.track_activity(user_id, 'page_view', '/home', 30)
    tracker.track_activity(user_id, 'page_view', '/products', 45)
    tracker.track_activity(user_id, 'click', '/products/item-1', 120)
    
    # Get today's activity
    activities = tracker.get_user_activity_today(user_id)
    print(f"Activities today: {len(activities)}")
    
    # Get weekly summary
    summary = tracker.get_activity_summary(user_id, days=7)
    for day in summary:
        print(f"{day['date']}: {day['count']} activities, {day['total_duration']}s total")
    
    tracker.close()
```

---

### Example 4: Kafka to Cassandra Pipeline

```python
# 09_integration/kafka_cassandra/kafka_consumer.py
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import json
import uuid
from datetime import datetime

class KafkaCassandraPipeline:
    def __init__(self, kafka_servers, cassandra_hosts):
        # Kafka consumer
        self.consumer = KafkaConsumer(
            'sensor_data',
            bootstrap_servers=kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Cassandra connection
        self.cluster = Cluster(cassandra_hosts)
        self.session = self.cluster.connect()
        self.setup_cassandra()
    
    def setup_cassandra(self):
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS iot_platform
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3}
        """)
        
        self.session.set_keyspace('iot_platform')
        
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                sensor_id UUID,
                timestamp TIMESTAMP,
                temperature DECIMAL,
                humidity DECIMAL,
                location TEXT,
                PRIMARY KEY ((sensor_id), timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
        """)
        
        # Prepare statement for performance
        self.insert_stmt = self.session.prepare("""
            INSERT INTO sensor_readings 
            (sensor_id, timestamp, temperature, humidity, location)
            VALUES (?, ?, ?, ?, ?)
        """)
    
    def process_messages(self):
        """Consume from Kafka and write to Cassandra"""
        print("Starting Kafka → Cassandra pipeline...")
        
        for message in self.consumer:
            data = message.value
            
            try:
                # Parse sensor data
                sensor_id = uuid.UUID(data['sensor_id'])
                timestamp = datetime.fromisoformat(data['timestamp'])
                temperature = float(data['temperature'])
                humidity = float(data['humidity'])
                location = data['location']
                
                # Write to Cassandra
                self.session.execute(
                    self.insert_stmt,
                    (sensor_id, timestamp, temperature, humidity, location)
                )
                
                print(f"Processed: {sensor_id} at {timestamp}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def close(self):
        self.consumer.close()
        self.cluster.shutdown()

# Usage
if __name__ == '__main__':
    pipeline = KafkaCassandraPipeline(
        kafka_servers=['localhost:9092'],
        cassandra_hosts=['127.0.0.1']
    )
    
    try:
        pipeline.process_messages()
    except KeyboardInterrupt:
        print("Shutting down...")
        pipeline.close()
```

---

## Best Practices

### Data Modeling

1. **Query-First Design** - Design tables based on queries, not entities
2. **One Query Per Table** - Each table optimized for specific query pattern
3. **Denormalize** - Duplicate data to avoid joins
4. **Partition Size** - Keep partitions under 100MB
5. **Avoid Hot Partitions** - Distribute data evenly

### Performance

1. **Use Prepared Statements** - Better performance and security
2. **Batch Wisely** - Only batch to same partition
3. **Avoid SELECT *** - Query only needed columns
4. **Use Appropriate Consistency** - Balance consistency vs latency
5. **Monitor Partition Sizes** - Prevent large partitions

### Operations

1. **Regular Repairs** - Run `nodetool repair` regularly
2. **Monitor Metrics** - Track latency, throughput, errors
3. **Backup Strategy** - Regular snapshots and backups
4. **Capacity Planning** - Monitor disk, CPU, memory
5. **Rolling Upgrades** - Upgrade nodes one at a time

---

## Common Use Cases

### 1. Time-Series Data (IoT, Metrics)
```cql
CREATE TABLE metrics (
    metric_name TEXT,
    bucket_time TIMESTAMP,
    timestamp TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((metric_name, bucket_time), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### 2. User Activity Tracking
```cql
CREATE TABLE user_events (
    user_id UUID,
    event_date DATE,
    event_time TIMESTAMP,
    event_type TEXT,
    details MAP<TEXT, TEXT>,
    PRIMARY KEY ((user_id, event_date), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

### 3. Product Catalog
```cql
CREATE TABLE products (
    category TEXT,
    product_id UUID,
    name TEXT,
    price DECIMAL,
    inventory INT,
    PRIMARY KEY ((category), product_id)
);
```

### 4. Messaging/Chat
```cql
CREATE TABLE messages (
    conversation_id UUID,
    message_time TIMESTAMP,
    sender_id UUID,
    message_text TEXT,
    PRIMARY KEY ((conversation_id), message_time)
) WITH CLUSTERING ORDER BY (message_time DESC);
```

---

## Resources

### 📚 Official Documentation

#### Apache Cassandra Official
- **[Apache Cassandra Documentation](https://cassandra.apache.org/doc/latest/)** - Complete official documentation
- **[CQL Reference](https://cassandra.apache.org/doc/latest/cassandra/cql/)** - CQL language specification
- **[Architecture Guide](https://cassandra.apache.org/doc/latest/cassandra/architecture/)** - Deep dive into Cassandra architecture
- **[Data Modeling Guide](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/)** - Official modeling best practices
- **[Operations Guide](https://cassandra.apache.org/doc/latest/cassandra/operating/)** - Production operations
- **[Configuration Reference](https://cassandra.apache.org/doc/latest/cassandra/configuration/)** - cassandra.yaml settings
- **[Troubleshooting Guide](https://cassandra.apache.org/doc/latest/cassandra/troubleshooting/)** - Common issues and solutions

#### DataStax Documentation
- **[DataStax Cassandra Docs](https://docs.datastax.com/)** - Enhanced documentation and guides
- **[Python Driver Documentation](https://docs.datastax.com/en/developer/python-driver/latest/)** - Official Python driver
- **[Java Driver Documentation](https://docs.datastax.com/en/developer/java-driver/latest/)** - Official Java driver
- **[Node.js Driver Documentation](https://docs.datastax.com/en/developer/nodejs-driver/latest/)** - Official Node.js driver
- **[DataStax Academy](https://academy.datastax.com/)** - Free comprehensive courses

#### API References
- **[CQL Shell (cqlsh) Reference](https://cassandra.apache.org/doc/latest/cassandra/tools/cqlsh.html)** - cqlsh commands
- **[Nodetool Reference](https://cassandra.apache.org/doc/latest/cassandra/tools/nodetool/)** - All nodetool commands
- **[Python Driver API](https://docs.datastax.com/en/developer/python-driver/latest/api/)** - Python API reference

### 📖 Books

#### Recommended Reading
- **"Cassandra: The Definitive Guide"** - Eben Hewitt & Jeff Carpenter (O'Reilly)
  - Most comprehensive Cassandra book
  - Covers architecture, data modeling, operations
  
- **"Mastering Apache Cassandra 3.x"** - Aaron Ploetz, Tejaswi Malepati, Nishant Neeraj
  - Advanced topics and real-world scenarios
  
- **"Learning Apache Cassandra"** - Mat Brown
  - Beginner-friendly introduction
  
- **"Practical Cassandra: A Developer's Approach"** - Russell Bradberry, Eric Lubow
  - Hands-on development guide

### 🎓 Online Courses

#### Free Courses
- **[DataStax Academy](https://academy.datastax.com/)** - Official free courses
  - DS101: Introduction to Apache Cassandra
  - DS201: Foundations of Apache Cassandra
  - DS220: Data Modeling
  
- **[Cassandra Fundamentals - Coursera](https://www.coursera.org/)** - University courses

#### Paid Courses
- **[Apache Cassandra - Udemy](https://www.udemy.com/topic/apache-cassandra/)** - Various courses
- **[Cassandra for Developers - Pluralsight](https://www.pluralsight.com/)** - Developer-focused
- **[LinkedIn Learning Cassandra Courses](https://www.linkedin.com/learning/)** - Professional training

### 🌐 Community & Support

#### Official Community
- **[Apache Cassandra Website](https://cassandra.apache.org/)** - Official homepage
- **[Cassandra Community](https://cassandra.apache.org/community/)** - Community hub
- **[Apache Cassandra Slack](https://cassandra.apache.org/slack)** - Active Slack workspace
- **[Cassandra Mailing Lists](https://cassandra.apache.org/community/#discussions)** - User and dev lists
- **[Cassandra JIRA](https://issues.apache.org/jira/browse/CASSANDRA)** - Bug tracking

#### Forums & Q&A
- **[Stack Overflow - Cassandra Tag](https://stackoverflow.com/questions/tagged/cassandra)** - Q&A community
- **[Reddit r/cassandra](https://www.reddit.com/r/cassandra/)** - Community discussions
- **[DataStax Community](https://community.datastax.com/)** - Official forum

#### Social Media
- **[Cassandra Twitter](https://twitter.com/cassandra)** - Official Twitter
- **[Planet Cassandra](https://planetcassandra.org/)** - Blog aggregator
- **[Cassandra YouTube Channel](https://www.youtube.com/c/PlanetCassandra)** - Video tutorials

### 📝 Blogs & Articles

#### Official Blogs
- **[Apache Cassandra Blog](https://cassandra.apache.org/blog/)** - Official blog
- **[DataStax Blog](https://www.datastax.com/blog)** - Technical articles
- **[Planet Cassandra Blog](https://planetcassandra.org/blog/)** - Community posts

#### Technical Blogs
- **[The Last Pickle Blog](https://thelastpickle.com/blog/)** - Cassandra experts
- **[Instaclustr Blog](https://www.instaclustr.com/blog/)** - Operations insights
- **[Netflix Tech Blog](https://netflixtechblog.com/)** - Netflix's Cassandra usage

### 🎥 Video Resources

#### Conference Talks
- **[Cassandra Summit](https://www.cassandrasummit.org/)** - Annual conference
- **[ApacheCon](https://www.apachecon.com/)** - Apache conferences
- **[DataStax Accelerate](https://www.datastax.com/accelerate)** - DataStax conference

#### YouTube Channels
- **[DataStax Developers](https://www.youtube.com/c/DataStaxDevs)** - Tutorials and talks
- **[Planet Cassandra](https://www.youtube.com/c/PlanetCassandra)** - Community content

### 🛠️ Tools & Utilities

#### Management Tools
- **[Cassandra Reaper](http://cassandra-reaper.io/)** - Automated repair tool
- **[cqlsh](https://cassandra.apache.org/doc/latest/cassandra/tools/cqlsh.html)** - CQL shell
- **[nodetool](https://cassandra.apache.org/doc/latest/cassandra/tools/nodetool/)** - Cluster management

#### Monitoring Tools
- **[Prometheus + Grafana](https://prometheus.io/)** - Metrics monitoring
- **[DataStax OpsCenter](https://www.datastax.com/products/datastax-opscenter)** - Management platform
- **[Cassandra Exporter](https://github.com/criteo/cassandra_exporter)** - Prometheus exporter

#### Development Tools
- **[DBeaver](https://dbeaver.io/)** - Universal database tool
- **[DataGrip](https://www.jetbrains.com/datagrip/)** - JetBrains database IDE
- **[Cassandra Workbench](https://www.datastax.com/)** - Query and modeling tool

### 📊 Benchmarking & Testing

- **[cassandra-stress](https://cassandra.apache.org/doc/latest/cassandra/tools/cassandra_stress.html)** - Built-in stress tool
- **[NoSQLBench](https://github.com/nosqlbench/nosqlbench)** - Performance testing
- **[YCSB](https://github.com/brianfrankcooper/YCSB)** - Yahoo! Cloud Serving Benchmark

### 🔬 Research Papers

- **[Cassandra - A Decentralized Structured Storage System](https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf)** - Original Facebook paper
- **[Dynamo: Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)** - Inspiration for Cassandra

### 🌟 Case Studies

#### Companies Using Cassandra
- **[Netflix](https://netflixtechblog.com/tagged/cassandra)** - Streaming platform
- **[Apple](https://planetcassandra.org/case-study/apple/)** - Consumer electronics
- **[Instagram](https://instagram-engineering.com/)** - Social media
- **[Uber](https://eng.uber.com/)** - Ride-sharing
- **[Discord](https://discord.com/blog)** - Communication platform

### 📚 Additional Learning Resources

#### Tutorials
- **[Cassandra Tutorial - TutorialsPoint](https://www.tutorialspoint.com/cassandra/)** - Beginner tutorial
- **[Cassandra Basics - Baeldung](https://www.baeldung.com/cassandra-with-java)** - Java integration
- **[Real Python - Cassandra](https://realpython.com/)** - Python tutorials

#### Cheat Sheets
- **[CQL Cheat Sheet](https://gist.github.com/jeffreyscarpenter/c7d2c76e6c0d5f3e8e3f)** - Quick CQL reference
- **[Nodetool Cheat Sheet](https://gist.github.com/jeffreyscarpenter/9215967)** - Nodetool commands

### 🔗 Related Technologies

- **[Apache Kafka](https://kafka.apache.org/)** - Stream processing with Cassandra
- **[Apache Spark](https://spark.apache.org/)** - Analytics on Cassandra data
- **[Presto](https://prestodb.io/)** - SQL queries on Cassandra
- **[Elassandra](https://github.com/strapdata/elassandra)** - Elasticsearch + Cassandra

---

## Troubleshooting

### Common Issues

**Connection refused**:
```bash
# Check if Cassandra is running
nodetool status

# Check logs
tail -f /var/log/cassandra/system.log
```

**Out of memory**:
```bash
# Increase heap size in cassandra-env.sh
MAX_HEAP_SIZE="4G"
HEAP_NEWSIZE="800M"
```

**Slow queries**:
```bash
# Enable query tracing
TRACING ON;
SELECT * FROM table WHERE ...;

# Check with nodetool
nodetool tablestats keyspace.table
```

---

## Next Steps

1. **Setup Cassandra**: Follow [SETUP.md](SETUP.md)
2. **Learn Basics**: Start with `01_basics/`
3. **Master CQL**: Work through `02_cql/`
4. **Data Modeling**: Study `03_data_modeling/`
5. **Build Projects**: Create in `10_real_world_projects/`

---

## Contributing

Add your own:
- Data modeling patterns
- Real-world examples
- Performance tips
- Integration patterns

---

## License

This is a learning repository. Use freely for educational purposes.

---

**Happy Learning! 🚀**

*Cassandra - Powering the world's most demanding applications since 2008*
