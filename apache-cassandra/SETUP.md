# Apache Cassandra Setup Guide

> **Complete installation and configuration guide for Apache Cassandra**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Single Node Setup](#single-node-setup)
4. [Multi-Node Cluster Setup](#multi-node-cluster-setup)
5. [Python Driver Setup](#python-driver-setup)
6. [Verification](#verification)
7. [Common Commands](#common-commands)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- 2GB RAM
- 10GB disk space
- 1 CPU core

**Recommended**:
- 8GB+ RAM
- 50GB+ SSD storage
- 4+ CPU cores

### Software Requirements

1. **Java (Required)**
   ```bash
   # Install Java 8 or 11
   # Ubuntu/Debian
   sudo apt update
   sudo apt install openjdk-11-jdk
   
   # macOS
   brew install openjdk@11
   
   # Verify
   java -version
   ```

2. **Python (For examples)**
   ```bash
   python3 --version  # Should be 3.7+
   pip3 install cassandra-driver
   ```

---

## Installation Methods

### Method 1: Docker (Recommended for Learning)

```bash
# Pull Cassandra image
docker pull cassandra:latest

# Run single node
docker run --name cassandra \
  -p 9042:9042 \
  -p 7000:7000 \
  -p 9160:9160 \
  -d cassandra:latest

# Check logs (wait 30-60 seconds for startup)
docker logs -f cassandra

# Connect with cqlsh
docker exec -it cassandra cqlsh

# Stop Cassandra
docker stop cassandra

# Start Cassandra
docker start cassandra

# Remove container
docker rm -f cassandra
```

#### Docker Compose (Multi-node)

```yaml
# docker-compose.yml
version: '3'

services:
  cassandra-1:
    image: cassandra:latest
    container_name: cassandra-1
    ports:
      - "9042:9042"
    environment:
      - CASSANDRA_CLUSTER_NAME=TestCluster
      - CASSANDRA_SEEDS=cassandra-1
    volumes:
      - cassandra-1-data:/var/lib/cassandra

  cassandra-2:
    image: cassandra:latest
    container_name: cassandra-2
    environment:
      - CASSANDRA_CLUSTER_NAME=TestCluster
      - CASSANDRA_SEEDS=cassandra-1
    depends_on:
      - cassandra-1
    volumes:
      - cassandra-2-data:/var/lib/cassandra

  cassandra-3:
    image: cassandra:latest
    container_name: cassandra-3
    environment:
      - CASSANDRA_CLUSTER_NAME=TestCluster
      - CASSANDRA_SEEDS=cassandra-1
    depends_on:
      - cassandra-1
    volumes:
      - cassandra-3-data:/var/lib/cassandra

volumes:
  cassandra-1-data:
  cassandra-2-data:
  cassandra-3-data:
```

```bash
# Start cluster
docker-compose up -d

# Check cluster status
docker exec -it cassandra-1 nodetool status

# Stop cluster
docker-compose down
```

---

### Method 2: Package Manager

#### macOS (Homebrew)

```bash
# Install Cassandra
brew install cassandra

# Start Cassandra
brew services start cassandra

# Stop Cassandra
brew services stop cassandra

# Restart Cassandra
brew services restart cassandra

# Connect with cqlsh
cqlsh
```

#### Ubuntu/Debian

```bash
# Add repository
echo "deb https://debian.cassandra.apache.org 41x main" | \
  sudo tee /etc/apt/sources.list.d/cassandra.list

# Add repository key
curl https://downloads.apache.org/cassandra/KEYS | sudo apt-key add -

# Update and install
sudo apt update
sudo apt install cassandra

# Start Cassandra
sudo systemctl start cassandra

# Enable on boot
sudo systemctl enable cassandra

# Check status
sudo systemctl status cassandra

# Connect with cqlsh
cqlsh
```

#### CentOS/RHEL

```bash
# Add repository
sudo tee /etc/yum.repos.d/cassandra.repo << EOF
[cassandra]
name=Apache Cassandra
baseurl=https://redhat.cassandra.apache.org/41x/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://downloads.apache.org/cassandra/KEYS
EOF

# Install
sudo yum install cassandra

# Start Cassandra
sudo systemctl start cassandra

# Enable on boot
sudo systemctl enable cassandra
```

---

### Method 3: Binary Installation

```bash
# Download Cassandra
cd ~
wget https://downloads.apache.org/cassandra/4.1.3/apache-cassandra-4.1.3-bin.tar.gz

# Extract
tar -xzf apache-cassandra-4.1.3-bin.tar.gz
mv apache-cassandra-4.1.3 cassandra

# Set environment variables
echo 'export CASSANDRA_HOME=~/cassandra' >> ~/.bashrc
echo 'export PATH=$PATH:$CASSANDRA_HOME/bin' >> ~/.bashrc
source ~/.bashrc

# Start Cassandra
cassandra -f  # Foreground
# OR
cassandra     # Background

# Connect with cqlsh
cqlsh
```

---

## Single Node Setup

### Step 1: Configure Cassandra

#### Edit `cassandra.yaml`

```bash
# Location varies by installation method:
# Docker: /etc/cassandra/cassandra.yaml
# Homebrew (Mac): /opt/homebrew/etc/cassandra/cassandra.yaml
# Ubuntu: /etc/cassandra/cassandra.yaml
# Binary: ~/cassandra/conf/cassandra.yaml

# Edit configuration
sudo nano /etc/cassandra/cassandra.yaml
```

**Key Settings**:

```yaml
# Cluster name
cluster_name: 'MyCluster'

# Data directories
data_file_directories:
  - /var/lib/cassandra/data

# Commit log directory
commitlog_directory: /var/lib/cassandra/commitlog

# Saved caches directory
saved_caches_directory: /var/lib/cassandra/saved_caches

# Seeds (for single node, use localhost)
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

# Enable authentication (optional)
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
```

### Step 2: Start Cassandra

```bash
# Start service
sudo systemctl start cassandra

# Check status
sudo systemctl status cassandra

# View logs
tail -f /var/log/cassandra/system.log
```

### Step 3: Verify Installation

```bash
# Check node status
nodetool status

# Expected output:
# Datacenter: datacenter1
# =======================
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address    Load       Tokens  Owns    Host ID                               Rack
# UN  127.0.0.1  108.45 KiB  256     100.0%  xxx-xxx-xxx-xxx                      rack1

# Connect with cqlsh
cqlsh

# Check version
cqlsh> SELECT release_version FROM system.local;
```

---

## Multi-Node Cluster Setup

### Architecture

```
3-Node Cluster
├── Node 1 (Seed) - 192.168.1.101
├── Node 2 (Seed) - 192.168.1.102
└── Node 3        - 192.168.1.103
```

### Prerequisites

- 3+ machines on same network
- Same Cassandra version on all nodes
- Synchronized clocks (NTP)
- Open ports: 7000, 7001, 9042, 9160

### Step 1: Configure Each Node

#### Node 1 Configuration

```yaml
# /etc/cassandra/cassandra.yaml

cluster_name: 'ProductionCluster'

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "192.168.1.101,192.168.1.102"

listen_address: 192.168.1.101
rpc_address: 192.168.1.101

endpoint_snitch: GossipingPropertyFileSnitch

auto_bootstrap: false  # Only for first node, first time
```

#### Node 2 Configuration

```yaml
cluster_name: 'ProductionCluster'

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "192.168.1.101,192.168.1.102"

listen_address: 192.168.1.102
rpc_address: 192.168.1.102

endpoint_snitch: GossipingPropertyFileSnitch
```

#### Node 3 Configuration

```yaml
cluster_name: 'ProductionCluster'

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "192.168.1.101,192.168.1.102"

listen_address: 192.168.1.103
rpc_address: 192.168.1.103

endpoint_snitch: GossipingPropertyFileSnitch
```

### Step 2: Configure Rack & Datacenter

```bash
# Edit cassandra-rackdc.properties on each node
sudo nano /etc/cassandra/cassandra-rackdc.properties

# Node 1
dc=dc1
rack=rack1

# Node 2
dc=dc1
rack=rack1

# Node 3
dc=dc1
rack=rack2
```

### Step 3: Start Cluster

```bash
# Start Node 1 (seed) first
sudo systemctl start cassandra

# Wait 2 minutes, then check
nodetool status

# Start Node 2 (seed)
sudo systemctl start cassandra

# Wait 2 minutes, check on Node 1
nodetool status

# Start Node 3
sudo systemctl start cassandra

# Final check from any node
nodetool status

# Expected output:
# Datacenter: dc1
# ===============
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address        Load       Tokens  Owns    Host ID     Rack
# UN  192.168.1.101  108.45 KiB  256     33.3%   xxx-xxx     rack1
# UN  192.168.1.102  108.45 KiB  256     33.3%   xxx-xxx     rack1
# UN  192.168.1.103  108.45 KiB  256     33.3%   xxx-xxx     rack2
```

### Step 4: Test Replication

```bash
# Connect to any node
cqlsh 192.168.1.101

# Create keyspace with replication
CREATE KEYSPACE test_cluster
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3
};

# Create table
USE test_cluster;
CREATE TABLE users (id UUID PRIMARY KEY, name TEXT);

# Insert data
INSERT INTO users (id, name) VALUES (uuid(), 'Test User');

# Query from different node
cqlsh 192.168.1.102
USE test_cluster;
SELECT * FROM users;  -- Should see the data
```

---

## Python Driver Setup

### Install Driver

```bash
# Install cassandra-driver
pip install cassandra-driver

# Install additional dependencies
pip install numpy  # For numerical operations
pip install pandas  # For data analysis
```

### Create requirements.txt

```txt
cassandra-driver==3.28.0
numpy==1.24.3
pandas==2.0.3
```

### Test Connection

```python
# test_connection.py
from cassandra.cluster import Cluster

# Connect to cluster
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# Test query
rows = session.execute('SELECT release_version FROM system.local')
for row in rows:
    print(f"Cassandra version: {row.release_version}")

# Close connection
cluster.shutdown()
print("Connection successful!")
```

```bash
# Run test
python test_connection.py
```

---

## Verification

### Check Cluster Health

```bash
# Node status
nodetool status

# Ring information
nodetool ring

# Cluster info
nodetool info

# Describe cluster
nodetool describecluster
```

### Check Connectivity

```bash
# Test CQL connection
cqlsh

# Test from Python
python test_connection.py

# Check listening ports
netstat -an | grep 9042  # CQL port
netstat -an | grep 7000  # Inter-node communication
```

### Create Test Keyspace

```cql
-- Connect with cqlsh
cqlsh

-- Create keyspace
CREATE KEYSPACE test
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Use keyspace
USE test;

-- Create table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT,
  email TEXT
);

-- Insert data
INSERT INTO users (id, name, email) 
VALUES (uuid(), 'Alice', 'alice@example.com');

-- Query data
SELECT * FROM users;

-- Drop keyspace
DROP KEYSPACE test;
```

---

## Common Commands

### Nodetool Commands

```bash
# Cluster status
nodetool status

# Node info
nodetool info

# Ring information
nodetool ring

# Repair data
nodetool repair

# Flush memtables to disk
nodetool flush

# Compact SSTables
nodetool compact

# Clean up data
nodetool cleanup

# Take snapshot
nodetool snapshot

# List snapshots
nodetool listsnapshots

# Clear snapshot
nodetool clearsnapshot

# Decommission node
nodetool decommission

# Remove node
nodetool removenode <host_id>

# Rebuild node
nodetool rebuild

# Get endpoint info
nodetool getendpoints <keyspace> <table> <key>

# View logs
nodetool getlogginglevels
nodetool setlogginglevel <logger> <level>
```

### CQL Commands

```cql
-- Show version
SELECT release_version FROM system.local;

-- List keyspaces
DESCRIBE KEYSPACES;

-- Describe keyspace
DESCRIBE KEYSPACE my_keyspace;

-- List tables
DESCRIBE TABLES;

-- Describe table
DESCRIBE TABLE my_table;

-- Show current keyspace
SELECT * FROM system_schema.keyspaces;

-- Show cluster name
SELECT cluster_name FROM system.local;

-- Exit cqlsh
exit;
```

### Service Management

```bash
# Start Cassandra
sudo systemctl start cassandra

# Stop Cassandra
sudo systemctl stop cassandra

# Restart Cassandra
sudo systemctl restart cassandra

# Check status
sudo systemctl status cassandra

# Enable on boot
sudo systemctl enable cassandra

# Disable on boot
sudo systemctl disable cassandra

# View logs
sudo journalctl -u cassandra -f
tail -f /var/log/cassandra/system.log
```

---

## Troubleshooting

### Issue 1: Cassandra Won't Start

**Symptoms**: Service fails to start

**Solutions**:
```bash
# Check logs
tail -f /var/log/cassandra/system.log

# Common issues:
# 1. Port already in use
sudo lsof -i :9042
sudo kill -9 <PID>

# 2. Insufficient memory
# Edit cassandra-env.sh
MAX_HEAP_SIZE="4G"
HEAP_NEWSIZE="800M"

# 3. Disk space full
df -h
# Clean up old snapshots
nodetool clearsnapshot

# 4. Corrupted commit log
# Remove commit logs (WARNING: data loss)
sudo rm -rf /var/lib/cassandra/commitlog/*
```

### Issue 2: Connection Refused

**Symptoms**: Cannot connect with cqlsh or Python

**Solutions**:
```bash
# Check if Cassandra is running
nodetool status

# Check if port is open
telnet localhost 9042

# Check firewall
sudo ufw allow 9042
sudo ufw allow 7000

# Check cassandra.yaml
# Ensure rpc_address is set correctly
rpc_address: 0.0.0.0  # Listen on all interfaces
# OR
rpc_address: localhost  # Local only
```

### Issue 3: Node Not Joining Cluster

**Symptoms**: New node not appearing in `nodetool status`

**Solutions**:
```bash
# Check logs on new node
tail -f /var/log/cassandra/system.log

# Common issues:
# 1. Cluster name mismatch
# Check cluster_name in cassandra.yaml

# 2. Seed list incorrect
# Verify seeds in cassandra.yaml

# 3. Network connectivity
ping <seed_node_ip>
telnet <seed_node_ip> 7000

# 4. Firewall blocking
sudo ufw allow from <node_ip> to any port 7000
sudo ufw allow from <node_ip> to any port 7001

# 5. Clear old data (if re-joining)
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo systemctl start cassandra
```

### Issue 4: Slow Queries

**Symptoms**: Queries taking too long

**Solutions**:
```cql
-- Enable tracing
TRACING ON;
SELECT * FROM my_table WHERE ...;

-- Check with nodetool
nodetool tablestats keyspace.table

-- Common fixes:
-- 1. Add appropriate indexes
CREATE INDEX ON my_table (column_name);

-- 2. Optimize partition key
-- Redesign table with better partition key

-- 3. Increase read timeout
-- In cassandra.yaml:
read_request_timeout_in_ms: 10000

-- 4. Run repair
nodetool repair keyspace table
```

### Issue 5: Out of Memory

**Symptoms**: Java heap space errors

**Solutions**:
```bash
# Edit cassandra-env.sh
sudo nano /etc/cassandra/cassandra-env.sh

# Increase heap size (50% of RAM, max 32GB)
MAX_HEAP_SIZE="8G"
HEAP_NEWSIZE="1600M"

# Restart Cassandra
sudo systemctl restart cassandra

# Monitor memory
nodetool info | grep Heap
```

### Issue 6: Tombstone Warnings

**Symptoms**: "Read X live rows and Y tombstone cells"

**Solutions**:
```bash
# Reduce gc_grace_seconds (default 10 days)
ALTER TABLE my_table WITH gc_grace_seconds = 86400;  -- 1 day

# Run compaction
nodetool compact keyspace table

# Use TTL for auto-expiring data
INSERT INTO table (...) VALUES (...) USING TTL 86400;

# Avoid deletes, use TTL instead
```

---

## Performance Tuning

### Memory Configuration

```bash
# Edit cassandra-env.sh

# Heap size (50% of RAM, max 32GB)
MAX_HEAP_SIZE="16G"
HEAP_NEWSIZE="3200M"

# Off-heap memory for caching
# In cassandra.yaml:
file_cache_size_in_mb: 2048
```

### Compaction Strategy

```cql
-- Size-Tiered (default, good for writes)
ALTER TABLE my_table 
WITH compaction = {
  'class': 'SizeTieredCompactionStrategy'
};

-- Leveled (good for reads)
ALTER TABLE my_table 
WITH compaction = {
  'class': 'LeveledCompactionStrategy'
};

-- Time-Window (good for time-series)
ALTER TABLE my_table 
WITH compaction = {
  'class': 'TimeWindowCompactionStrategy',
  'compaction_window_size': 1,
  'compaction_window_unit': 'DAYS'
};
```

### Caching

```cql
-- Enable row cache
ALTER TABLE my_table 
WITH caching = {
  'keys': 'ALL',
  'rows_per_partition': '100'
};
```

---

## Security Setup

### Enable Authentication

```yaml
# In cassandra.yaml
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
```

```bash
# Restart Cassandra
sudo systemctl restart cassandra

# Connect with default credentials
cqlsh -u cassandra -p cassandra

# Change default password
ALTER USER cassandra WITH PASSWORD 'new_secure_password';

# Create new user
CREATE USER admin WITH PASSWORD 'admin_password' SUPERUSER;

# Create regular user
CREATE USER app_user WITH PASSWORD 'app_password';

# Grant permissions
GRANT SELECT ON KEYSPACE my_keyspace TO app_user;
GRANT MODIFY ON KEYSPACE my_keyspace TO app_user;
```

### Enable SSL/TLS

```yaml
# In cassandra.yaml
client_encryption_options:
  enabled: true
  optional: false
  keystore: /path/to/keystore.jks
  keystore_password: password
```

---

## Backup & Restore

### Snapshot Backup

```bash
# Take snapshot
nodetool snapshot -t backup_name keyspace_name

# List snapshots
nodetool listsnapshots

# Snapshots location
ls /var/lib/cassandra/data/keyspace_name/table_name-*/snapshots/

# Copy snapshots to backup location
tar -czf backup.tar.gz /var/lib/cassandra/data/*/*/snapshots/backup_name/

# Clear snapshot
nodetool clearsnapshot -t backup_name
```

### Restore from Snapshot

```bash
# Stop Cassandra
sudo systemctl stop cassandra

# Restore snapshot files
cp -r /backup/snapshots/* /var/lib/cassandra/data/keyspace/table/

# Fix permissions
sudo chown -R cassandra:cassandra /var/lib/cassandra/data

# Start Cassandra
sudo systemctl start cassandra

# Run repair
nodetool repair
```

---

## Next Steps

1. **Verify Installation**: Run verification commands
2. **Learn CQL**: Start with `02_cql/`
3. **Data Modeling**: Study `03_data_modeling/`
4. **Build Apps**: Try `04_python_driver/`
5. **Production Setup**: Read `06_cluster_management/`

---

## Additional Resources

- [Official Documentation](https://cassandra.apache.org/doc/latest/)
- [DataStax Academy](https://academy.datastax.com/)
- [Cassandra Summit](https://www.cassandrasummit.org/)

---

**Setup Complete! Ready to learn Cassandra! 🚀**
