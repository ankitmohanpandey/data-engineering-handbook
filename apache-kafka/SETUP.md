# Apache Kafka Setup Guide

## Prerequisites

### System Requirements
- **Java**: JDK 8 or 11 (required for Kafka broker)
- **Python**: 3.7+ (for Python clients)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Disk**: 10GB+ free space
- **OS**: Linux, macOS, or Windows

### Check Java Version
```bash
java -version
# Should show version 8 or 11
```

### Install Java (if needed)
```bash
# macOS
brew install openjdk@11

# Ubuntu
sudo apt-get update
sudo apt-get install openjdk-11-jdk

# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 11)  # macOS
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Ubuntu
```

---

## Installation Methods

### Option 1: Binary Download (Recommended)

```bash
# Download Kafka
cd ~/Downloads
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz

# Extract
tar -xzf kafka_2.13-3.6.0.tgz

# Move to installation directory
sudo mv kafka_2.13-3.6.0 /opt/kafka
cd /opt/kafka

# Add to PATH (optional)
echo 'export PATH=$PATH:/opt/kafka/bin' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: Homebrew (macOS)

```bash
# Install Kafka
brew install kafka

# Kafka installed at: /usr/local/opt/kafka
# Config files at: /usr/local/etc/kafka
```

### Option 3: Docker

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
  
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Option 4: Python Client Only

```bash
# If you only need Python client (not broker)
pip install kafka-python
```

---

## Starting Kafka

### Step 1: Start ZooKeeper

```bash
# Terminal 1: Start ZooKeeper
cd /opt/kafka

# Using default config
bin/zookeeper-server-start.sh config/zookeeper.properties

# Or in background
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
```

**ZooKeeper Configuration** (`config/zookeeper.properties`):
```properties
# Data directory
dataDir=/tmp/zookeeper

# Client port
clientPort=2181

# Max client connections
maxClientCnxns=0

# Admin server
admin.enableServer=false
```

### Step 2: Start Kafka Broker

```bash
# Terminal 2: Start Kafka
cd /opt/kafka

# Using default config
bin/kafka-server-start.sh config/server.properties

# Or in background
bin/kafka-server-start.sh -daemon config/server.properties
```

**Kafka Configuration** (`config/server.properties`):
```properties
# Broker ID
broker.id=0

# Listeners
listeners=PLAINTEXT://localhost:9092

# Log directories
log.dirs=/tmp/kafka-logs

# Zookeeper connection
zookeeper.connect=localhost:2181

# Number of partitions
num.partitions=3

# Replication factor
default.replication.factor=1

# Log retention
log.retention.hours=168
log.retention.bytes=1073741824

# Segment size
log.segment.bytes=1073741824
```

### Step 3: Verify Installation

```bash
# Check if Kafka is running
jps
# Should show: Kafka, QuorumPeerMain (ZooKeeper)

# Or check ports
netstat -an | grep 9092  # Kafka
netstat -an | grep 2181  # ZooKeeper
```

---

## Python Client Setup

### Install Python Dependencies

```bash
# Navigate to project directory
cd "/Users/5149844/windsurf/personal learning/learning/apache-kafka"

# Create virtual environment
python -m venv kafka-env

# Activate virtual environment
# macOS/Linux:
source kafka-env/bin/activate
# Windows:
kafka-env\Scripts\activate

# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install kafka-python==2.0.2
pip install confluent-kafka==2.3.0
```

---

## Basic Operations

### Topic Management

```bash
# Create topic
kafka-topics.sh --create \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# List topics
kafka-topics.sh --list \
  --bootstrap-server localhost:9092

# Describe topic
kafka-topics.sh --describe \
  --topic my-topic \
  --bootstrap-server localhost:9092

# Delete topic
kafka-topics.sh --delete \
  --topic my-topic \
  --bootstrap-server localhost:9092

# Alter topic (add partitions)
kafka-topics.sh --alter \
  --topic my-topic \
  --partitions 5 \
  --bootstrap-server localhost:9092
```

### Producer Console

```bash
# Start console producer
kafka-console-producer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092

# With key
kafka-console-producer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --property "parse.key=true" \
  --property "key.separator=:"
```

### Consumer Console

```bash
# Start console consumer (from latest)
kafka-console-consumer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092

# From beginning
kafka-console-consumer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --from-beginning

# With consumer group
kafka-console-consumer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --group my-group

# Show keys
kafka-console-consumer.sh \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --property print.key=true \
  --property key.separator=":"
```

### Consumer Groups

```bash
# List consumer groups
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list

# Describe consumer group
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --describe

# Reset offsets to earliest
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic \
  --reset-offsets --to-earliest \
  --execute

# Reset offsets to specific offset
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-group \
  --topic my-topic:0 \
  --reset-offsets --to-offset 100 \
  --execute
```

---

## Multi-Broker Setup

### Create Multiple Broker Configs

```bash
# Copy default config
cp config/server.properties config/server-1.properties
cp config/server.properties config/server-2.properties

# Edit server-1.properties
broker.id=1
listeners=PLAINTEXT://localhost:9093
log.dirs=/tmp/kafka-logs-1

# Edit server-2.properties
broker.id=2
listeners=PLAINTEXT://localhost:9094
log.dirs=/tmp/kafka-logs-2
```

### Start Multiple Brokers

```bash
# Start broker 1
bin/kafka-server-start.sh -daemon config/server-1.properties

# Start broker 2
bin/kafka-server-start.sh -daemon config/server-2.properties

# Verify
jps
# Should show multiple Kafka processes
```

### Create Replicated Topic

```bash
kafka-topics.sh --create \
  --topic replicated-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 3
```

---

## Running Examples

### Test Producer

```bash
# Activate virtual environment
source kafka-env/bin/activate

# Run basic producer
python 01_basic_producer.py

# Run advanced producer
python 03_advanced_producer.py
```

### Test Consumer

```bash
# In another terminal
source kafka-env/bin/activate

# Run basic consumer
python 02_basic_consumer.py
```

---

## Troubleshooting

### Issue 1: Kafka Won't Start

**Symptoms:**
- Kafka fails to start
- Connection refused errors

**Solutions:**
```bash
# Check if ZooKeeper is running
jps | grep QuorumPeerMain

# Check logs
tail -f /opt/kafka/logs/server.log

# Verify Java version
java -version

# Check port availability
lsof -i :9092
lsof -i :2181

# Clean up old data (WARNING: deletes all data)
rm -rf /tmp/kafka-logs
rm -rf /tmp/zookeeper
```

### Issue 2: Topic Creation Fails

**Symptoms:**
- Topic not created
- Timeout errors

**Solutions:**
```bash
# Verify broker is running
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check ZooKeeper connection
kafka-topics.sh --list --bootstrap-server localhost:9092

# Increase timeout
kafka-topics.sh --create --topic test \
  --bootstrap-server localhost:9092 \
  --command-config <(echo "request.timeout.ms=30000")
```

### Issue 3: Consumer Lag

**Symptoms:**
- Messages piling up
- Slow consumption

**Solutions:**
```bash
# Check consumer lag
kafka-consumer-groups.sh --describe \
  --group my-group \
  --bootstrap-server localhost:9092

# Solutions:
# 1. Add more consumers to group
# 2. Increase partitions
# 3. Optimize consumer processing
# 4. Increase fetch size
```

### Issue 4: Out of Memory

**Symptoms:**
- Java heap space errors
- Broker crashes

**Solutions:**
```bash
# Increase heap size
export KAFKA_HEAP_OPTS="-Xmx2G -Xms2G"

# Edit kafka-server-start.sh
# Add: export KAFKA_HEAP_OPTS="-Xmx4G -Xms4G"

# Restart Kafka
bin/kafka-server-stop.sh
bin/kafka-server-start.sh config/server.properties
```

### Issue 5: Connection Timeout

**Symptoms:**
- TimeoutError in Python
- Can't connect to broker

**Solutions:**
```python
# Increase timeout in producer/consumer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    request_timeout_ms=30000,
    api_version_auto_timeout_ms=10000
)

# Check firewall
# Check broker advertised.listeners
# Verify broker is accessible
```

---

## Performance Tuning

### Broker Configuration

```properties
# Increase throughput
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Optimize log
log.flush.interval.messages=10000
log.flush.interval.ms=1000

# Compression
compression.type=lz4

# Replication
min.insync.replicas=2
```

### Producer Tuning

```python
producer = KafkaProducer(
    # Batching
    batch_size=32768,  # 32KB
    linger_ms=10,
    
    # Compression
    compression_type='lz4',
    
    # Buffer
    buffer_memory=67108864,  # 64MB
    
    # Throughput
    max_in_flight_requests_per_connection=5
)
```

### Consumer Tuning

```python
consumer = KafkaConsumer(
    # Fetch settings
    fetch_min_bytes=1024,  # 1KB
    fetch_max_wait_ms=500,
    max_partition_fetch_bytes=1048576,  # 1MB
    
    # Polling
    max_poll_records=500,
    max_poll_interval_ms=300000
)
```

---

## Monitoring

### JMX Metrics

```bash
# Enable JMX
export JMX_PORT=9999
bin/kafka-server-start.sh config/server.properties

# Connect with JConsole
jconsole localhost:9999
```

### Key Metrics to Monitor

**Broker Metrics:**
- MessagesInPerSec
- BytesInPerSec
- BytesOutPerSec
- UnderReplicatedPartitions
- OfflinePartitionsCount

**Producer Metrics:**
- record-send-rate
- record-error-rate
- request-latency-avg

**Consumer Metrics:**
- records-consumed-rate
- records-lag-max
- fetch-latency-avg

---

## Production Deployment

### Systemd Service (Linux)

```bash
# Create service file: /etc/systemd/system/kafka.service
[Unit]
Description=Apache Kafka
After=network.target zookeeper.service

[Service]
Type=simple
User=kafka
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable kafka
sudo systemctl start kafka
sudo systemctl status kafka
```

### Best Practices

✅ **Use multiple brokers** (at least 3)  
✅ **Set replication factor ≥ 2**  
✅ **Use dedicated disks** for Kafka logs  
✅ **Monitor broker metrics**  
✅ **Enable authentication** (SASL)  
✅ **Enable encryption** (SSL/TLS)  
✅ **Regular backups**  
✅ **Capacity planning**  

---

## Stopping Kafka

```bash
# Stop Kafka broker
bin/kafka-server-stop.sh

# Stop ZooKeeper
bin/zookeeper-server-stop.sh

# Or kill processes
pkill -f kafka.Kafka
pkill -f zookeeper
```

---

## Cleanup

```bash
# Remove all data (WARNING: deletes everything)
rm -rf /tmp/kafka-logs
rm -rf /tmp/zookeeper

# Remove installation
sudo rm -rf /opt/kafka
```

---

## Quick Start Checklist

- [ ] Install Java 8 or 11
- [ ] Download and extract Kafka
- [ ] Start ZooKeeper
- [ ] Start Kafka broker
- [ ] Create test topic
- [ ] Install Python dependencies
- [ ] Run producer example
- [ ] Run consumer example
- [ ] Verify messages received

---

## Resources

- **Official Docs**: https://kafka.apache.org/documentation/
- **Quickstart**: https://kafka.apache.org/quickstart
- **Configuration**: https://kafka.apache.org/documentation/#configuration
- **Operations**: https://kafka.apache.org/documentation/#operations

---

**You're ready to start streaming with Apache Kafka!** 🚀
