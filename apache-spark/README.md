# Apache Spark Complete Guide

## Table of Contents
1. [What is Apache Spark?](#what-is-apache-spark)
2. [Core Concepts](#core-concepts)
3. [Setup & Installation](#setup--installation)
4. [Basic Examples](#basic-examples)
5. [Advanced Concepts](#advanced-concepts)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## What is Apache Spark?

**Apache Spark** is a unified analytics engine for large-scale data processing with built-in modules for streaming, SQL, machine learning, and graph processing.

### Key Points
- **Fast**: In-memory computing (up to 100x faster than Hadoop MapReduce)
- **Unified**: Batch, streaming, SQL, ML, graph processing in one framework
- **Language Support**: Python (PySpark), Scala, Java, R, SQL
- **Scalable**: From laptop to thousands of nodes
- **Open Source**: Apache Software Foundation project

### Why Use Apache Spark?
✅ Lightning-fast in-memory processing  
✅ Easy-to-use APIs (DataFrame, SQL)  
✅ Unified platform for multiple workloads  
✅ Rich ecosystem (MLlib, GraphX, Streaming)  
✅ Fault-tolerant and scalable  
✅ Active community and extensive documentation  

---

## Core Concepts

### 1. SparkContext & SparkSession
- **SparkContext**: Entry point for Spark functionality (older API)
- **SparkSession**: Unified entry point (Spark 2.0+, recommended)

```python
from pyspark.sql import SparkSession

# Create SparkSession (includes SparkContext)
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .getOrCreate()
```

### 2. RDD (Resilient Distributed Dataset)
- **Low-level API**: Fundamental data structure
- **Immutable**: Cannot be changed once created
- **Distributed**: Partitioned across cluster
- **Fault-tolerant**: Automatically recovers from failures
- **Lazy evaluation**: Transformations computed only when action is called

```python
# Create RDD
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# Transformations (lazy)
rdd2 = rdd.map(lambda x: x * 2)

# Actions (trigger computation)
result = rdd2.collect()  # [2, 4, 6, 8, 10]
```

### 3. DataFrame
- **High-level API**: Like a table in SQL or pandas DataFrame
- **Optimized**: Catalyst optimizer for query optimization
- **Structured**: Schema with named columns
- **Preferred**: Use DataFrames over RDDs for better performance

```python
# Create DataFrame
df = spark.createDataFrame([
    (1, "Alice", 25),
    (2, "Bob", 30)
], ["id", "name", "age"])

# SQL-like operations
df.filter(df.age > 25).show()
```

### 4. Dataset
- **Type-safe**: Compile-time type checking (Scala/Java only)
- **Best of both**: Combines RDD type-safety with DataFrame optimization
- **Not in Python**: Python uses DataFrames (dynamically typed)

### 5. Transformations vs Actions

**Transformations** (Lazy - return new RDD/DataFrame):
- `map()`, `filter()`, `flatMap()`
- `groupBy()`, `join()`, `union()`
- `select()`, `where()`, `orderBy()`

**Actions** (Eager - trigger computation):
- `collect()`, `count()`, `first()`
- `take()`, `reduce()`, `foreach()`
- `show()`, `save()`

### 6. Partitions
- Data is divided into partitions
- Each partition processed in parallel
- Number of partitions affects parallelism

```python
# Check partitions
rdd.getNumPartitions()

# Repartition
rdd.repartition(10)
```

### 7. Persistence/Caching
- Store intermediate results in memory/disk
- Avoid recomputation

```python
# Cache in memory
df.cache()

# Persist with storage level
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)

# Unpersist
df.unpersist()
```

---

## Setup & Installation

### Prerequisites
- Python 3.7+ (recommended 3.8 or higher)
- Java 8 or 11 (required for Spark)

### Check Java Installation
```bash
java -version
```

### Installation Options

#### Option 1: pip install (Easiest)
```bash
pip install pyspark
```

#### Option 2: Download Spark
1. Download from https://spark.apache.org/downloads.html
2. Extract: `tar -xzf spark-3.5.0-bin-hadoop3.tgz`
3. Set environment variables:
```bash
export SPARK_HOME=/path/to/spark
export PATH=$SPARK_HOME/bin:$PATH
```

### Verify Installation
```bash
pyspark --version
```

---

## Basic Examples

### Example 1: RDD Basics
See: `01_rdd_basics.py`

### Example 2: DataFrame Operations
See: `02_dataframe_basics.py`

### Example 3: Spark SQL
See: `03_spark_sql.py`

### Example 4: Data Aggregation
See: `04_aggregations.py`

### Example 5: Joins and Unions
See: `05_joins_unions.py`

### Example 6: Streaming
See: `06_streaming.py`

### Example 7: Machine Learning (MLlib)
See: `07_mllib_basics.py`

---

## Advanced Concepts

### Spark Architecture

```
Driver Program (SparkContext)
    ↓
Cluster Manager (YARN/Mesos/Standalone)
    ↓
Worker Nodes (Executors)
    ↓
Tasks (Process Partitions)
```

**Components:**
- **Driver**: Runs main() function, creates SparkContext
- **Executors**: Run tasks, store data for caching
- **Cluster Manager**: Allocates resources
- **Tasks**: Units of work sent to executors

### Catalyst Optimizer
- Query optimization for DataFrames/SQL
- Logical plan → Optimized logical plan → Physical plan
- Automatic optimization (predicate pushdown, column pruning, etc.)

### Tungsten Execution Engine
- Memory management and binary processing
- Code generation for faster execution
- Cache-aware computation

### Broadcast Variables
- Read-only variable cached on each worker
- Efficient for small lookup tables

```python
broadcast_var = spark.sparkContext.broadcast([1, 2, 3])
# Use: broadcast_var.value
```

### Accumulators
- Variables that can only be added to
- Used for counters and sums

```python
accum = spark.sparkContext.accumulator(0)
rdd.foreach(lambda x: accum.add(1))
print(accum.value)
```

### Window Functions
- Perform calculations across rows related to current row

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

windowSpec = Window.partitionBy("category").orderBy("price")
df.withColumn("rank", row_number().over(windowSpec))
```

### User-Defined Functions (UDFs)
- Custom functions for DataFrames

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

def square(x):
    return x * x

square_udf = udf(square, IntegerType())
df.withColumn("squared", square_udf(df.value))
```

---

## Real-World Use Cases

### 1. ETL Pipelines
Extract data from sources, transform, load to data warehouse.

### 2. Real-time Analytics
Process streaming data from Kafka, Kinesis, etc.

### 3. Machine Learning
Train models on large datasets using MLlib.

### 4. Log Analysis
Parse and analyze application/server logs.

### 5. Recommendation Systems
Collaborative filtering for product recommendations.

### 6. Graph Processing
Social network analysis using GraphX.

### 7. Data Lake Processing
Process data stored in S3, HDFS, etc.

---

## Best Practices

### 1. Use DataFrames over RDDs
DataFrames are optimized and easier to use.

### 2. Avoid collect() on Large Data
```python
# Bad: Brings all data to driver
all_data = df.collect()  # OOM risk!

# Good: Process in distributed manner
df.write.parquet("output")
```

### 3. Cache Wisely
Only cache data that's reused multiple times.

```python
# Cache if used multiple times
df.cache()
df.count()
df.filter(...).show()
```

### 4. Partition Appropriately
- Too few: Underutilization
- Too many: Overhead

```python
# Rule of thumb: 2-4 partitions per CPU core
df.repartition(100)
```

### 5. Use Built-in Functions
Faster than UDFs.

```python
# Good: Built-in function
from pyspark.sql.functions import upper
df.withColumn("name_upper", upper(df.name))

# Avoid: UDF (slower)
upper_udf = udf(lambda x: x.upper())
df.withColumn("name_upper", upper_udf(df.name))
```

### 6. Broadcast Small Tables
For joins with small tables.

```python
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")
```

### 7. Use Parquet Format
Columnar format, compressed, efficient.

```python
df.write.parquet("output.parquet")
df = spark.read.parquet("output.parquet")
```

### 8. Monitor and Tune
- Use Spark UI (http://localhost:4040)
- Check DAG visualization
- Monitor stages, tasks, storage

---

## Troubleshooting

### Common Issues

#### 1. "Java not found"
**Solution**: Install Java 8 or 11
```bash
# macOS
brew install openjdk@11

# Ubuntu
sudo apt-get install openjdk-11-jdk
```

#### 2. OutOfMemoryError
**Solution**: Increase executor memory
```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
```

#### 3. Slow Performance
**Solutions**:
- Check partition count
- Cache reused DataFrames
- Use broadcast for small tables
- Avoid UDFs when possible
- Use Parquet instead of CSV

#### 4. "Py4JJavaError"
**Solution**: Check Java/Python compatibility, ensure proper data types

#### 5. Shuffle Operations are Slow
**Solutions**:
- Increase shuffle partitions: `spark.sql.shuffle.partitions`
- Use broadcast joins for small tables
- Repartition before shuffle operations

---

## Spark vs Other Frameworks

| Feature | Spark | Hadoop MapReduce | Flink | Beam |
|---------|-------|------------------|-------|------|
| Speed | Very Fast (in-memory) | Slow (disk-based) | Very Fast | Depends on runner |
| Ease of Use | High | Low | Medium | High |
| Streaming | Micro-batch | No | True streaming | Both |
| SQL Support | Yes (Spark SQL) | Limited (Hive) | Yes | Limited |
| ML Library | MLlib | Mahout | FlinkML | No |
| Maturity | High | High | Medium | Medium |
| Language Support | Python, Scala, Java, R | Java | Java, Scala, Python | Python, Java, Go |

---

## Deployment Modes

### 1. Local Mode
```python
spark = SparkSession.builder.master("local[*]").getOrCreate()
```

### 2. Standalone Cluster
```bash
spark-submit --master spark://host:7077 app.py
```

### 3. YARN
```bash
spark-submit --master yarn --deploy-mode cluster app.py
```

### 4. Kubernetes
```bash
spark-submit --master k8s://https://k8s-api app.py
```

### 5. Mesos
```bash
spark-submit --master mesos://host:5050 app.py
```

---

## Quick Reference

### Create SparkSession
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("App").getOrCreate()
```

### Read Data
```python
df = spark.read.csv("data.csv", header=True, inferSchema=True)
df = spark.read.json("data.json")
df = spark.read.parquet("data.parquet")
```

### Basic Operations
```python
df.show()                    # Display data
df.printSchema()             # Show schema
df.count()                   # Count rows
df.columns                   # List columns
df.describe().show()         # Statistics
```

### Transformations
```python
df.select("col1", "col2")
df.filter(df.age > 25)
df.groupBy("category").count()
df.orderBy("age", ascending=False)
df.withColumn("new_col", df.col1 * 2)
df.drop("col1")
```

### SQL
```python
df.createOrReplaceTempView("table")
spark.sql("SELECT * FROM table WHERE age > 25").show()
```

---

## Resources

- **Official Documentation**: https://spark.apache.org/docs/latest/
- **PySpark API**: https://spark.apache.org/docs/latest/api/python/
- **Spark UI**: http://localhost:4040 (when running)
- **GitHub**: https://github.com/apache/spark
- **Stack Overflow**: Tag `apache-spark` or `pyspark`
- **Learning**: https://spark.apache.org/examples.html

---

## Next Steps

1. Run the examples in order (01 through 07)
2. Modify examples to understand behavior
3. Build your own Spark application
4. Deploy to a cluster (YARN, Kubernetes, etc.)
5. Explore MLlib for machine learning
6. Learn Spark Streaming for real-time processing

---

**Remember**: Spark is all about distributed, in-memory processing. Think parallel, think fast! ⚡
