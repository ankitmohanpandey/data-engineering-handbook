# Cassandra Quick Reference

> **Quick commands and concepts cheatsheet**

---

## CQL Commands

### Keyspace Operations

```cql
-- Create keyspace (SimpleStrategy)
CREATE KEYSPACE my_app 
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

-- Create keyspace (NetworkTopologyStrategy)
CREATE KEYSPACE my_app 
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 2
};

-- Use keyspace
USE my_app;

-- Alter keyspace
ALTER KEYSPACE my_app 
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 2
};

-- Drop keyspace
DROP KEYSPACE my_app;

-- Describe keyspace
DESCRIBE KEYSPACE my_app;

-- List all keyspaces
DESCRIBE KEYSPACES;
```

---

### Table Operations

```cql
-- Create table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);

-- Create table with composite key
CREATE TABLE user_activity (
    user_id UUID,
    activity_date DATE,
    activity_time TIMESTAMP,
    activity_type TEXT,
    PRIMARY KEY ((user_id, activity_date), activity_time)
) WITH CLUSTERING ORDER BY (activity_time DESC);

-- Create table with collections
CREATE TABLE user_profile (
    user_id UUID PRIMARY KEY,
    tags SET<TEXT>,
    preferences MAP<TEXT, TEXT>,
    login_history LIST<TIMESTAMP>
);

-- Alter table (add column)
ALTER TABLE users ADD phone TEXT;

-- Alter table (drop column)
ALTER TABLE users DROP phone;

-- Drop table
DROP TABLE users;

-- Truncate table
TRUNCATE TABLE users;

-- Describe table
DESCRIBE TABLE users;

-- List all tables
DESCRIBE TABLES;
```

---

### Data Manipulation

```cql
-- Insert data
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'john_doe', 'john@example.com', toTimestamp(now()));

-- Insert with TTL (expires after 86400 seconds)
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'temp_user', 'temp@example.com')
USING TTL 86400;

-- Update data
UPDATE users 
SET email = 'newemail@example.com'
WHERE user_id = ?;

-- Update with TTL
UPDATE users USING TTL 3600
SET email = 'temp@example.com'
WHERE user_id = ?;

-- Delete specific columns
DELETE email FROM users WHERE user_id = ?;

-- Delete entire row
DELETE FROM users WHERE user_id = ?;

-- Delete with timestamp
DELETE FROM users 
USING TIMESTAMP 1234567890
WHERE user_id = ?;

-- Batch operations
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (uuid(), 'user1');
    INSERT INTO users (user_id, username) VALUES (uuid(), 'user2');
    UPDATE users SET email = 'new@example.com' WHERE user_id = ?;
APPLY BATCH;
```

---

### Querying Data

```cql
-- Select all
SELECT * FROM users;

-- Select specific columns
SELECT user_id, username FROM users;

-- Select with WHERE clause
SELECT * FROM users WHERE user_id = ?;

-- Select with IN clause
SELECT * FROM users WHERE user_id IN (?, ?, ?);

-- Select with range
SELECT * FROM user_activity 
WHERE user_id = ? 
  AND activity_time > '2024-01-01'
  AND activity_time < '2024-12-31';

-- Select with LIMIT
SELECT * FROM users LIMIT 10;

-- Select with ORDER BY (only on clustering columns)
SELECT * FROM user_activity 
WHERE user_id = ?
ORDER BY activity_time DESC;

-- Select with ALLOW FILTERING (avoid in production)
SELECT * FROM users WHERE email = 'john@example.com' ALLOW FILTERING;

-- Count rows
SELECT COUNT(*) FROM users;

-- Select with token function (pagination)
SELECT * FROM users WHERE token(user_id) > token(?);
```

---

### Indexes

```cql
-- Create secondary index
CREATE INDEX ON users (email);

-- Create index with name
CREATE INDEX users_email_idx ON users (email);

-- Create index on collection
CREATE INDEX ON user_profile (tags);

-- Create index on map keys
CREATE INDEX ON user_profile (KEYS(preferences));

-- Create index on map values
CREATE INDEX ON user_profile (VALUES(preferences));

-- Drop index
DROP INDEX users_email_idx;

-- List indexes
DESCRIBE INDEX users_email_idx;
```

---

### Materialized Views

```cql
-- Create materialized view
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT user_id, username, email
    FROM users
    WHERE email IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);

-- Drop materialized view
DROP MATERIALIZED VIEW users_by_email;

-- Describe materialized view
DESCRIBE MATERIALIZED VIEW users_by_email;
```

---

### User-Defined Types

```cql
-- Create UDT
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT
);

-- Use UDT in table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name TEXT,
    home_address FROZEN<address>,
    work_address FROZEN<address>
);

-- Insert with UDT
INSERT INTO users (user_id, name, home_address)
VALUES (uuid(), 'John', {
    street: '123 Main St',
    city: 'New York',
    state: 'NY',
    zip_code: '10001'
});

-- Drop UDT
DROP TYPE address;
```

---

### Counters

```cql
-- Create counter table
CREATE TABLE page_views (
    page_id UUID PRIMARY KEY,
    view_count COUNTER
);

-- Increment counter
UPDATE page_views SET view_count = view_count + 1 WHERE page_id = ?;

-- Decrement counter
UPDATE page_views SET view_count = view_count - 1 WHERE page_id = ?;

-- Read counter
SELECT view_count FROM page_views WHERE page_id = ?;
```

---

### Lightweight Transactions (LWT)

```cql
-- Insert if not exists
INSERT INTO users (user_id, username, email)
VALUES (?, 'john_doe', 'john@example.com')
IF NOT EXISTS;

-- Update if condition met
UPDATE users 
SET email = 'new@example.com'
WHERE user_id = ?
IF email = 'old@example.com';

-- Delete if condition met
DELETE FROM users 
WHERE user_id = ?
IF username = 'john_doe';
```

---

## Data Types

### Basic Types

```cql
TEXT          -- UTF-8 string
VARCHAR       -- Alias for TEXT
ASCII         -- ASCII string
INT           -- 32-bit integer
BIGINT        -- 64-bit integer
SMALLINT      -- 16-bit integer
TINYINT       -- 8-bit integer
VARINT        -- Arbitrary precision integer
FLOAT         -- 32-bit floating point
DOUBLE        -- 64-bit floating point
DECIMAL       -- Variable precision decimal
BOOLEAN       -- true/false
UUID          -- Type 4 UUID
TIMEUUID      -- Type 1 UUID (time-based)
TIMESTAMP     -- Date and time
DATE          -- Date (no time)
TIME          -- Time (no date)
DURATION      -- Duration
BLOB          -- Binary data
INET          -- IP address (IPv4 or IPv6)
```

### Collection Types

```cql
-- Set (unique, unordered)
SET<TEXT>

-- List (ordered, duplicates allowed)
LIST<TEXT>

-- Map (key-value pairs)
MAP<TEXT, INT>

-- Frozen collection (immutable)
FROZEN<SET<TEXT>>
```

---

## Nodetool Commands

### Cluster Information

```bash
# Cluster status
nodetool status

# Ring information
nodetool ring

# Cluster info
nodetool info

# Describe cluster
nodetool describecluster

# Version
nodetool version

# Get endpoints for key
nodetool getendpoints <keyspace> <table> <key>
```

### Maintenance Operations

```bash
# Repair (sync data across replicas)
nodetool repair
nodetool repair <keyspace>
nodetool repair <keyspace> <table>

# Flush memtables to disk
nodetool flush
nodetool flush <keyspace>
nodetool flush <keyspace> <table>

# Compact SSTables
nodetool compact
nodetool compact <keyspace>
nodetool compact <keyspace> <table>

# Cleanup (remove data not owned by node)
nodetool cleanup
nodetool cleanup <keyspace>

# Scrub (rebuild SSTables)
nodetool scrub <keyspace> <table>

# Refresh (reload SSTables)
nodetool refresh <keyspace> <table>
```

### Snapshots

```bash
# Take snapshot
nodetool snapshot -t <snapshot_name>
nodetool snapshot -t <snapshot_name> <keyspace>

# List snapshots
nodetool listsnapshots

# Clear snapshot
nodetool clearsnapshot
nodetool clearsnapshot -t <snapshot_name>
```

### Performance & Monitoring

```bash
# Table statistics
nodetool tablestats
nodetool tablestats <keyspace>
nodetool tablestats <keyspace>.<table>

# Table histograms
nodetool tablehistograms <keyspace> <table>

# Compaction statistics
nodetool compactionstats

# Thread pool statistics
nodetool tpstats

# Garbage collection statistics
nodetool gcstats

# Proxyhistograms
nodetool proxyhistograms

# Get streaming info
nodetool netstats

# Get cache statistics
nodetool info | grep Cache
```

### Node Operations

```bash
# Drain node (stop writes, flush data)
nodetool drain

# Stop gossip
nodetool disablegossip

# Start gossip
nodetool enablegossip

# Stop native transport
nodetool disablebinary

# Start native transport
nodetool enablebinary

# Decommission node
nodetool decommission

# Remove dead node
nodetool removenode <host_id>

# Assassinate node (force remove)
nodetool assassinate <ip_address>

# Move node to new token
nodetool move <new_token>

# Rebuild from another DC
nodetool rebuild <source_dc>
```

### Configuration

```bash
# Get compaction throughput
nodetool getcompactionthroughput

# Set compaction throughput (MB/s)
nodetool setcompactionthroughput <value>

# Get stream throughput
nodetool getstreamthroughput

# Set stream throughput (MB/s)
nodetool setstreamthroughput <value>

# Get timeout
nodetool gettimeout <type>

# Set timeout
nodetool settimeout <type> <value>

# Get logging level
nodetool getlogginglevels

# Set logging level
nodetool setlogginglevel <logger> <level>
```

---

## Consistency Levels

### Read Consistency

```cql
-- Set consistency for session
CONSISTENCY ONE;
CONSISTENCY QUORUM;
CONSISTENCY ALL;
CONSISTENCY LOCAL_QUORUM;
CONSISTENCY EACH_QUORUM;

-- In Python driver
from cassandra import ConsistencyLevel
session.execute(query, consistency_level=ConsistencyLevel.QUORUM)
```

### Consistency Level Options

| Level | Description | Replicas | Use Case |
|-------|-------------|----------|----------|
| **ANY** | Any node (write only) | 1 | Highest availability |
| **ONE** | One replica | 1 | Low latency reads |
| **TWO** | Two replicas | 2 | Better durability |
| **THREE** | Three replicas | 3 | More durability |
| **QUORUM** | Majority of replicas | (RF/2) + 1 | Balanced |
| **ALL** | All replicas | RF | Strong consistency |
| **LOCAL_ONE** | One in local DC | 1 | Multi-DC, low latency |
| **LOCAL_QUORUM** | Majority in local DC | Local (RF/2) + 1 | Multi-DC, balanced |
| **EACH_QUORUM** | Majority in each DC | Each DC (RF/2) + 1 | Multi-DC, strong |

---

## Python Driver Quick Reference

### Connection

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Simple connection
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# With authentication
auth_provider = PlainTextAuthProvider(username='user', password='pass')
cluster = Cluster(['127.0.0.1'], auth_provider=auth_provider)
session = cluster.connect()

# Set keyspace
session.set_keyspace('my_keyspace')

# Close connection
cluster.shutdown()
```

### Queries

```python
# Simple query
rows = session.execute("SELECT * FROM users")
for row in rows:
    print(row.username, row.email)

# Parameterized query
query = "SELECT * FROM users WHERE user_id = %s"
rows = session.execute(query, (user_id,))

# Prepared statement (better performance)
prepared = session.prepare("SELECT * FROM users WHERE user_id = ?")
rows = session.execute(prepared, (user_id,))

# Batch operations
from cassandra.query import BatchStatement
batch = BatchStatement()
batch.add(prepared, (user_id1,))
batch.add(prepared, (user_id2,))
session.execute(batch)

# Async queries
future = session.execute_async("SELECT * FROM users")
rows = future.result()
```

### Consistency Level

```python
from cassandra import ConsistencyLevel

# Set for query
session.execute(query, consistency_level=ConsistencyLevel.QUORUM)

# Set default for session
session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
```

---

## Data Modeling Patterns

### Time-Series Pattern

```cql
CREATE TABLE sensor_data (
    sensor_id UUID,
    year INT,
    month INT,
    day INT,
    timestamp TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id, year, month, day), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### User Activity Pattern

```cql
CREATE TABLE user_activity (
    user_id UUID,
    activity_date DATE,
    activity_time TIMESTAMP,
    activity_type TEXT,
    PRIMARY KEY ((user_id, activity_date), activity_time)
) WITH CLUSTERING ORDER BY (activity_time DESC);
```

### Messaging Pattern

```cql
CREATE TABLE messages (
    conversation_id UUID,
    message_time TIMESTAMP,
    sender_id UUID,
    message_text TEXT,
    PRIMARY KEY ((conversation_id), message_time)
) WITH CLUSTERING ORDER BY (message_time DESC);
```

### Leaderboard Pattern

```cql
CREATE TABLE leaderboard (
    game_id UUID,
    score INT,
    player_id UUID,
    player_name TEXT,
    PRIMARY KEY ((game_id), score, player_id)
) WITH CLUSTERING ORDER BY (score DESC);
```

---

## Common Patterns

### Pagination

```python
# Using paging
from cassandra.query import SimpleStatement

query = SimpleStatement("SELECT * FROM users", fetch_size=100)
for row in session.execute(query):
    print(row)

# Manual pagination with token
last_token = None
while True:
    if last_token:
        query = f"SELECT * FROM users WHERE token(user_id) > {last_token} LIMIT 100"
    else:
        query = "SELECT * FROM users LIMIT 100"
    
    rows = list(session.execute(query))
    if not rows:
        break
    
    for row in rows:
        print(row)
    
    last_token = rows[-1].user_id
```

### Bulk Loading

```python
from cassandra.concurrent import execute_concurrent_with_args

# Prepare statement
prepared = session.prepare("INSERT INTO users (user_id, username) VALUES (?, ?)")

# Bulk data
data = [(uuid.uuid4(), f'user{i}') for i in range(1000)]

# Execute concurrently
execute_concurrent_with_args(session, prepared, data, concurrency=50)
```

---

## Performance Tips

### Query Optimization

1. **Avoid ALLOW FILTERING** - Redesign table instead
2. **Use Prepared Statements** - Better performance
3. **Batch to Same Partition** - Don't batch across partitions
4. **Limit Result Size** - Use LIMIT or paging
5. **Use Appropriate Consistency** - Balance consistency vs latency

### Data Modeling

1. **Query-First Design** - Design for queries, not entities
2. **Denormalize** - Duplicate data to avoid joins
3. **Partition Size** - Keep under 100MB
4. **Even Distribution** - Avoid hot partitions
5. **Use Clustering Columns** - For sorting within partition

### Operations

1. **Regular Repairs** - Keep data consistent
2. **Monitor Metrics** - Track latency, throughput
3. **Appropriate Compaction** - Choose right strategy
4. **Use TTL** - Auto-expire data instead of deletes
5. **Proper Replication** - RF=3 for production

---

## Troubleshooting Quick Fixes

### Connection Issues

```bash
# Check if Cassandra is running
nodetool status

# Check port
telnet localhost 9042

# Check logs
tail -f /var/log/cassandra/system.log
```

### Performance Issues

```cql
-- Enable tracing
TRACING ON;
SELECT * FROM table WHERE ...;

-- Check table stats
nodetool tablestats keyspace.table
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clear snapshots
nodetool clearsnapshot

# Compact tables
nodetool compact
```

### Memory Issues

```bash
# Check heap usage
nodetool info | grep Heap

# Increase heap in cassandra-env.sh
MAX_HEAP_SIZE="8G"
```

---

## Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

alias cass='cqlsh'
alias casstatus='nodetool status'
alias cassinfo='nodetool info'
alias cassrepair='nodetool repair'
alias casscompact='nodetool compact'
alias casslogs='tail -f /var/log/cassandra/system.log'
```

---

## Configuration Files

### Key Files

```bash
# Cassandra configuration
/etc/cassandra/cassandra.yaml

# Environment settings
/etc/cassandra/cassandra-env.sh

# Rack/DC configuration
/etc/cassandra/cassandra-rackdc.properties

# Logging configuration
/etc/cassandra/logback.xml

# Data directory
/var/lib/cassandra/data/

# Logs directory
/var/log/cassandra/
```

---

## Important cassandra.yaml Settings

```yaml
# Cluster name
cluster_name: 'MyCluster'

# Seeds
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "127.0.0.1"

# Listen address
listen_address: localhost

# RPC address
rpc_address: localhost

# Native transport port
native_transport_port: 9042

# Replication factor
# (set per keyspace, not in yaml)

# Compaction throughput
compaction_throughput_mb_per_sec: 64

# Concurrent reads/writes
concurrent_reads: 32
concurrent_writes: 32

# Memtable flush
memtable_flush_writers: 2

# Cache sizes
key_cache_size_in_mb: 100
row_cache_size_in_mb: 0
```

---

**Keep this handy while working with Cassandra! 🚀**
