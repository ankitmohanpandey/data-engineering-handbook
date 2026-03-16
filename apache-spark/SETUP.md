# Apache Spark Setup Guide

## Prerequisites

### 1. Java Installation (Required)
Spark requires Java 8 or 11.

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
Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [AdoptOpenJDK](https://adoptopenjdk.net/)

### 2. Python Installation
Python 3.7 or higher required.

```bash
python --version
# or
python3 --version
```

## Installation Options

### Option 1: pip install PySpark (Easiest)

```bash
# Create virtual environment (recommended)
python -m venv spark-env

# Activate virtual environment
# macOS/Linux:
source spark-env/bin/activate
# Windows:
spark-env\Scripts\activate

# Install from requirements.txt
pip install -r requirements.txt

# Or install manually
pip install pyspark==3.5.0
```

### Option 2: Download Full Spark Distribution

1. **Download Spark**
   - Visit https://spark.apache.org/downloads.html
   - Choose: Spark 3.5.0, Pre-built for Apache Hadoop 3.3
   - Download: `spark-3.5.0-bin-hadoop3.tgz`

2. **Extract**
   ```bash
   tar -xzf spark-3.5.0-bin-hadoop3.tgz
   sudo mv spark-3.5.0-bin-hadoop3 /opt/spark
   ```

3. **Set Environment Variables**
   
   Add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   export SPARK_HOME=/opt/spark
   export PATH=$SPARK_HOME/bin:$PATH
   export PYSPARK_PYTHON=python3
   ```
   
   Apply changes:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

## Verify Installation

```bash
# Check PySpark version
pyspark --version

# Start PySpark shell (interactive)
pyspark

# In PySpark shell, try:
>>> spark.version
>>> spark.range(10).count()
>>> exit()
```

## Running Examples

### Run Individual Examples

```bash
# Navigate to spark directory
cd "/Users/5149844/windsurf/personal learning/learning/apache-spark"

# Run examples in order
python 01_rdd_basics.py
python 02_dataframe_basics.py
python 03_spark_sql.py
python 04_joins_io.py
python 05_streaming_basics.py
python 06_mllib_basics.py
```

### View Output Files

```bash
# Check output directory
ls -la output/

# View Parquet files
python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.getOrCreate(); spark.read.parquet('output/employees.parquet').show()"
```

## Spark UI

When running Spark applications, access the web UI:
- **URL**: http://localhost:4040
- **Features**: Jobs, Stages, Storage, Environment, Executors

## Configuration

### Spark Configuration File

Create `spark-defaults.conf`:
```bash
# Memory settings
spark.driver.memory              2g
spark.executor.memory            4g

# Shuffle settings
spark.sql.shuffle.partitions     200

# Logging
spark.eventLog.enabled           true
spark.eventLog.dir               /tmp/spark-events
```

### Programmatic Configuration

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()
```

## Running Modes

### 1. Local Mode (Development)
```python
# Use all available cores
.master("local[*]")

# Use 4 cores
.master("local[4]")
```

### 2. Standalone Cluster
```bash
# Start master
$SPARK_HOME/sbin/start-master.sh

# Start worker
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077

# Submit job
spark-submit --master spark://localhost:7077 app.py
```

### 3. YARN
```bash
spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 10 \
    --executor-memory 4g \
    --executor-cores 2 \
    app.py
```

### 4. Kubernetes
```bash
spark-submit \
    --master k8s://https://kubernetes-api:6443 \
    --deploy-mode cluster \
    --name spark-app \
    app.py
```

## Troubleshooting

### Issue: "Java not found"
**Solution:**
```bash
# Install Java
brew install openjdk@11  # macOS
sudo apt-get install openjdk-11-jdk  # Ubuntu

# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 11)  # macOS
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Ubuntu
```

### Issue: "py4j.protocol.Py4JJavaError"
**Solution:**
- Check Java version compatibility
- Ensure PySpark and Java versions match
- Restart SparkSession

### Issue: OutOfMemoryError
**Solution:**
```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "8g") \
    .getOrCreate()
```

### Issue: Slow Performance
**Solutions:**
- Increase partitions: `df.repartition(200)`
- Cache frequently used DataFrames: `df.cache()`
- Use Parquet instead of CSV
- Check Spark UI for bottlenecks
- Increase executor memory

### Issue: "Address already in use" (Port 4040)
**Solution:**
```python
# Use different port
spark = SparkSession.builder \
    .config("spark.ui.port", "4041") \
    .getOrCreate()
```

### Issue: Permission Denied (Output Directory)
**Solution:**
```bash
# Create output directory
mkdir -p output
chmod 755 output

# Or write to different location
df.write.parquet("/tmp/output")
```

## Best Practices

### 1. Use Virtual Environments
Always use virtual environments to avoid conflicts:
```bash
python -m venv spark-env
source spark-env/bin/activate
```

### 2. Set Log Level
Reduce verbosity:
```python
spark.sparkContext.setLogLevel("ERROR")
```

### 3. Stop SparkSession
Always stop when done:
```python
spark.stop()
```

### 4. Monitor Resources
- Check Spark UI (http://localhost:4040)
- Monitor memory usage
- Check partition count

### 5. Use Appropriate File Formats
- **Parquet**: Best for analytics (columnar, compressed)
- **CSV**: Human-readable but slow
- **JSON**: Semi-structured data
- **Avro**: Schema evolution

## Development Workflow

1. **Start Small**: Test with sample data locally
2. **Use Spark UI**: Monitor performance
3. **Optimize**: Cache, partition, broadcast
4. **Test Locally**: Use `local[*]` mode
5. **Deploy**: Move to cluster when ready

## Project Structure

```
apache-spark/
├── README.md                    # Main documentation
├── SETUP.md                     # This file
├── QUICK_REFERENCE.md          # Cheat sheet
├── requirements.txt            # Dependencies
├── 01_rdd_basics.py           # RDD examples
├── 02_dataframe_basics.py     # DataFrame examples
├── 03_spark_sql.py            # SQL examples
├── 04_joins_io.py             # Joins and I/O
├── 05_streaming_basics.py     # Streaming examples
├── 06_mllib_basics.py         # ML examples
├── output/                     # Output directory
└── .gitignore                 # Git ignore patterns
```

## Additional Resources

- **Official Docs**: https://spark.apache.org/docs/latest/
- **PySpark API**: https://spark.apache.org/docs/latest/api/python/
- **Spark UI**: http://localhost:4040
- **GitHub**: https://github.com/apache/spark
- **Stack Overflow**: Tag `apache-spark` or `pyspark`

## Quick Start Commands

```bash
# Install
pip install pyspark

# Verify
pyspark --version

# Run example
python 01_rdd_basics.py

# Interactive shell
pyspark

# Submit job
spark-submit app.py
```

## Next Steps

1. ✅ Complete setup
2. ✅ Run all examples (01-06)
3. ✅ Experiment with Spark UI
4. ✅ Build your own application
5. ✅ Deploy to cluster

---

**Happy Sparking! ⚡**
