# Apache Flink Setup Guide

## Prerequisites

### 1. Java Installation (Required)
Flink runs on the JVM. Check the compatibility matrix for your Flink version, but Java 11 or 17
work for recent (1.18+) releases.

#### Check Java Version
```bash
java -version
```

#### Install Java (if needed)

**macOS:**
```bash
brew install openjdk@11
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openjdk-11-jdk
```

**Windows:**
Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [Adoptium](https://adoptium.net/)

### 2. Python Installation (for PyFlink)
Python 3.9–3.11 is required (check the exact range supported by your PyFlink version).

```bash
python --version
# or
python3 --version
```

## Installation Options

### Option 1: pip install PyFlink (Easiest — for learning/local dev)

```bash
# Create virtual environment (recommended)
python -m venv flink-env

# Activate virtual environment
# macOS/Linux:
source flink-env/bin/activate
# Windows:
flink-env\Scripts\activate

# Install from requirements.txt
pip install -r requirements.txt

# Or install manually
pip install apache-flink==1.20.0
```

### Option 2: Download the Full Flink Distribution (for CLI / cluster usage)

1. **Download Flink**
   - Visit https://flink.apache.org/downloads/
   - Choose a stable release, e.g. `flink-1.20.0-bin-scala_2.12.tgz`

2. **Extract**
   ```bash
   tar -xzf flink-1.20.0-bin-scala_2.12.tgz
   sudo mv flink-1.20.0 /opt/flink
   ```

3. **Set Environment Variables**

   Add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   export FLINK_HOME=/opt/flink
   export PATH=$FLINK_HOME/bin:$PATH
   ```

   Apply changes:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

## Verify Installation

```bash
# Check PyFlink version
python -c "import pyflink; print(pyflink.__version__)"

# Start a local standalone cluster (if using the full distribution)
$FLINK_HOME/bin/start-cluster.sh

# Open the Web UI
open http://localhost:8081   # macOS
# or visit http://localhost:8081 in your browser

# Stop the cluster when done
$FLINK_HOME/bin/stop-cluster.sh
```

## Running Examples

### Run Individual Examples (local MiniCluster — no separate cluster required)

```bash
# Navigate to the flink directory
cd apache-flink

# Run examples in order
python 01_datastream_basics.py
python 02_table_api_basics.py
python 03_windowing_and_watermarks.py
python 04_stateful_processing.py
python 05_sql_and_connectors.py
python 06_checkpointing_and_fault_tolerance.py
python 07_kafka_streaming_pipeline.py
```

Most examples run against Flink's embedded `MiniCluster`, so no external cluster is required to
follow along — except `07_kafka_streaming_pipeline.py`, which needs a running Kafka broker
(see the Docker Compose note below).

### Optional: Kafka for the Streaming Pipeline Example

```bash
# Quick local Kafka via Docker (single broker, for learning purposes only)
docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_ENABLE_KRAFT=yes \
  -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
  -e KAFKA_CFG_NODE_ID=1 \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@127.0.0.1:9093 \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e ALLOW_PLAINTEXT_LISTENER=yes \
  bitnami/kafka:latest
```

For a more complete environment, use the official playground instead:
```bash
git clone https://github.com/apache/flink-playgrounds.git
cd flink-playgrounds/pyflink-walkthrough
docker-compose up -d
```

## Flink Web UI

When running against a cluster (standalone/YARN/Kubernetes), access the web UI:
- **URL**: http://localhost:8081
- **Features**: Job graph, task metrics, checkpoints, backpressure, TaskManager logs

## Configuration

### `flink-conf.yaml` (in `$FLINK_HOME/conf`)

```yaml
# JobManager / TaskManager memory
jobmanager.memory.process.size: 1600m
taskmanager.memory.process.size: 1728m

# Parallelism
taskmanager.numberOfTaskSlots: 4
parallelism.default: 2

# Checkpointing
execution.checkpointing.interval: 60000
state.backend: rocksdb
state.checkpoints.dir: file:///tmp/flink-checkpoints
```

### Programmatic Configuration (PyFlink)

```python
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode

env = StreamExecutionEnvironment.get_execution_environment()
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
env.set_parallelism(4)
env.enable_checkpointing(60000)  # ms
```

## Running Modes

### 1. Local Mode / MiniCluster (Development)
Just run your Python script directly — PyFlink spins up an embedded MiniCluster automatically
when no remote cluster is configured.

### 2. Standalone Cluster
```bash
$FLINK_HOME/bin/start-cluster.sh
$FLINK_HOME/bin/flink run -m localhost:8081 -py app.py
```

### 3. YARN
```bash
$FLINK_HOME/bin/flink run -m yarn-cluster -yn 4 -py app.py
```

### 4. Kubernetes (Application Mode)
```bash
$FLINK_HOME/bin/flink run-application \
    --target kubernetes-application \
    -Dkubernetes.cluster-id=my-flink-cluster \
    -Dkubernetes.container.image=my-pyflink-image:latest \
    local:///opt/flink/usrlib/app.py
```

## Troubleshooting

### Issue: "Java not found"
**Solution:**
```bash
brew install openjdk@11  # macOS
sudo apt-get install openjdk-11-jdk  # Ubuntu

# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 11)  # macOS
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Ubuntu
```

### Issue: `py4j`/gateway errors when starting PyFlink jobs
**Solution:**
- Confirm Java is installed and `JAVA_HOME` is set
- Confirm the PyFlink and Python versions are compatible (check release notes)
- Restart the Python process / virtual environment

### Issue: OutOfMemoryError on TaskManager
**Solution:**
```yaml
# flink-conf.yaml
taskmanager.memory.process.size: 4096m
taskmanager.memory.managed.fraction: 0.4
```
Or move large keyed state to `EmbeddedRocksDBStateBackend`.

### Issue: Checkpoints failing/timing out
**Solutions:**
- Increase `execution.checkpointing.timeout`
- Check for backpressure in the Web UI (slow sink/operator)
- Reduce state size or enable incremental RocksDB checkpoints

### Issue: "Address already in use" (Port 8081)
**Solution:**
```yaml
# flink-conf.yaml
rest.port: 8082
```

### Issue: Kafka connector JAR not found (when using the full distribution + SQL client)
**Solution:**
Download the matching `flink-sql-connector-kafka-*.jar` from the Maven Central repository and
place it in `$FLINK_HOME/lib/`.

## Best Practices

### 1. Use Virtual Environments
```bash
python -m venv flink-env
source flink-env/bin/activate
```

### 2. Pin Your Flink/PyFlink Version
Avoid mixing PyFlink pip package versions with a different full-distribution version — they must
match to avoid protocol/serialization mismatches.

### 3. Enable Checkpointing Early
Even in development, enabling checkpointing helps you understand recovery behavior before
production.

### 4. Monitor via the Web UI
- Check the Web UI (http://localhost:8081) for job graphs, backpressure, and checkpoint stats

### 5. Use Appropriate State Backends
- **HashMapStateBackend**: Small state, fastest
- **EmbeddedRocksDBStateBackend**: Large state, supports incremental checkpoints

## Development Workflow

1. **Start Small**: Test transformations with `env.from_collection()` locally
2. **Use the Web UI**: Monitor job graph and backpressure once on a real cluster
3. **Add State & Time Semantics**: Move from stateless maps to keyed/windowed/stateful logic
4. **Test Locally**: Use the embedded MiniCluster (no cluster setup needed)
5. **Deploy**: Move to Application Mode on Kubernetes/YARN when ready

## Project Structure

```
apache-flink/
├── README.md                              # Main documentation
├── SETUP.md                               # This file
├── QUICK_REFERENCE.md                     # Cheat sheet
├── requirements.txt                       # Dependencies
├── 01_datastream_basics.py                # DataStream API fundamentals
├── 02_table_api_basics.py                 # Table API & SQL fundamentals
├── 03_windowing_and_watermarks.py         # Event time, watermarks, windows
├── 04_stateful_processing.py              # Keyed/operator state, ProcessFunction
├── 05_sql_and_connectors.py               # Flink SQL, connectors, CDC-style pipeline
├── 06_checkpointing_and_fault_tolerance.py# Checkpoints, savepoints, state backends
└── 07_kafka_streaming_pipeline.py         # End-to-end Kafka streaming example
```

## Additional Resources

- **Official Docs**: https://nightlies.apache.org/flink/flink-docs-stable/
- **PyFlink API**: https://nightlies.apache.org/flink/flink-docs-stable/api/python/
- **Flink Web UI**: http://localhost:8081
- **GitHub**: https://github.com/apache/flink
- **Training Exercises**: https://github.com/apache/flink-training
- **Playgrounds**: https://github.com/apache/flink-playgrounds
- **Stack Overflow**: Tag `apache-flink` or `pyflink`

## Quick Start Commands

```bash
# Install
pip install apache-flink

# Verify
python -c "import pyflink; print(pyflink.__version__)"

# Run example
python 01_datastream_basics.py

# Start local cluster (full distribution)
$FLINK_HOME/bin/start-cluster.sh

# Submit a job to the cluster
$FLINK_HOME/bin/flink run -py app.py
```

## Next Steps

1. ✅ Complete setup
2. ✅ Run all examples (01-07)
3. ✅ Experiment with the Flink Web UI
4. ✅ Build your own stateful streaming application
5. ✅ Deploy to a cluster (Kubernetes Application Mode recommended)

---

**Happy Streaming! 🌊**
