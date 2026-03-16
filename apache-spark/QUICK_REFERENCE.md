# Apache Spark Quick Reference Card

## 🚀 Quick Start
```bash
pip install pyspark
python 01_rdd_basics.py
```

## 📋 SparkSession

```python
from pyspark.sql import SparkSession

# Create SparkSession
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

# Stop SparkSession
spark.stop()
```

## 🔥 RDD Operations

### Create RDD
```python
# From list
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# From file
rdd = spark.sparkContext.textFile("file.txt")
```

### Transformations (Lazy)
```python
# Map (1-to-1)
rdd.map(lambda x: x * 2)

# Filter
rdd.filter(lambda x: x > 10)

# FlatMap (1-to-many)
rdd.flatMap(lambda x: x.split())

# Distinct
rdd.distinct()

# Union
rdd1.union(rdd2)

# ReduceByKey (for key-value pairs)
rdd.reduceByKey(lambda a, b: a + b)

# GroupByKey
rdd.groupByKey()
```

### Actions (Eager)
```python
# Collect (return all to driver)
rdd.collect()

# Count
rdd.count()

# First
rdd.first()

# Take (first N)
rdd.take(5)

# Reduce
rdd.reduce(lambda a, b: a + b)

# SaveAsTextFile
rdd.saveAsTextFile("output")
```

## 📊 DataFrame Operations

### Create DataFrame
```python
# From list
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])

# From CSV
df = spark.read.csv("file.csv", header=True, inferSchema=True)

# From JSON
df = spark.read.json("file.json")

# From Parquet
df = spark.read.parquet("file.parquet")
```

### Basic Operations
```python
# Show data
df.show()
df.show(5)  # First 5 rows

# Schema
df.printSchema()

# Count
df.count()

# Columns
df.columns

# Describe (statistics)
df.describe().show()

# Collect
df.collect()
```

### Select & Filter
```python
# Select columns
df.select("col1", "col2")
df.select(col("col1"), col("col2"))

# Filter/Where
df.filter(col("age") > 25)
df.where(col("age") > 25)

# Multiple conditions
df.filter((col("age") > 25) & (col("salary") > 50000))
df.filter((col("dept") == "IT") | (col("dept") == "HR"))
```

### Add/Modify Columns
```python
# Add column
df.withColumn("new_col", col("old_col") * 2)

# Rename column
df.withColumnRenamed("old_name", "new_name")

# Drop column
df.drop("col1")

# Cast type
df.withColumn("age", col("age").cast("integer"))
```

### Aggregations
```python
from pyspark.sql.functions import sum, avg, max, min, count

# GroupBy
df.groupBy("department").count()
df.groupBy("department").avg("salary")

# Multiple aggregations
df.groupBy("department").agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary"),
    max("salary").alias("max_salary")
)

# Global aggregation
df.agg(count("*"), avg("salary"))
```

### Sorting
```python
# Sort ascending
df.orderBy("age")

# Sort descending
df.orderBy(col("salary").desc())

# Multiple columns
df.orderBy(col("age").asc(), col("salary").desc())
```

### Joins
```python
# Inner join
df1.join(df2, "key", "inner")

# Left join
df1.join(df2, "key", "left")

# Right join
df1.join(df2, "key", "right")

# Full outer join
df1.join(df2, "key", "outer")

# Cross join
df1.crossJoin(df2)

# Join on different column names
df1.join(df2, df1.col1 == df2.col2)
```

### Write Data
```python
# Parquet (recommended)
df.write.mode("overwrite").parquet("output.parquet")

# CSV
df.write.mode("overwrite").csv("output.csv", header=True)

# JSON
df.write.mode("overwrite").json("output.json")

# With partitioning
df.write.partitionBy("year", "month").parquet("output")

# Save modes: overwrite, append, ignore, error
```

## 🔍 Spark SQL

```python
# Create temp view
df.createOrReplaceTempView("table_name")

# Run SQL query
result = spark.sql("SELECT * FROM table_name WHERE age > 25")

# SQL aggregation
spark.sql("""
    SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
""").show()

# SQL join
spark.sql("""
    SELECT e.name, d.dept_name
    FROM employees e
    JOIN departments d ON e.dept_id = d.dept_id
""").show()
```

## 🌊 Streaming

```python
# Read stream
stream_df = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 10) \
    .load()

# Transform
result = stream_df.select("timestamp", "value")

# Write stream
query = result.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for termination
query.awaitTermination()

# Stop query
query.stop()
```

## 🤖 MLlib

### Feature Engineering
```python
from pyspark.ml.feature import VectorAssembler, StringIndexer

# StringIndexer (categorical to numeric)
indexer = StringIndexer(inputCol="category", outputCol="category_index")
indexed_df = indexer.fit(df).transform(df)

# VectorAssembler (combine features)
assembler = VectorAssembler(
    inputCols=["col1", "col2"],
    outputCol="features"
)
feature_df = assembler.transform(df)
```

### Classification
```python
from pyspark.ml.classification import LogisticRegression

# Train model
lr = LogisticRegression(featuresCol="features", labelCol="label")
model = lr.fit(train_df)

# Predict
predictions = model.transform(test_df)

# Evaluate
from pyspark.ml.evaluation import BinaryClassificationEvaluator
evaluator = BinaryClassificationEvaluator(labelCol="label")
auc = evaluator.evaluate(predictions)
```

### Regression
```python
from pyspark.ml.regression import LinearRegression

# Train model
lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(train_df)

# Predict
predictions = model.transform(test_df)

# Evaluate
from pyspark.ml.evaluation import RegressionEvaluator
evaluator = RegressionEvaluator(labelCol="label", metricName="rmse")
rmse = evaluator.evaluate(predictions)
```

### Pipeline
```python
from pyspark.ml import Pipeline

# Define stages
pipeline = Pipeline(stages=[
    indexer,    # StringIndexer
    assembler,  # VectorAssembler
    lr          # LogisticRegression
])

# Fit pipeline
model = pipeline.fit(train_df)

# Transform
predictions = model.transform(test_df)
```

## 🔧 Common Functions

```python
from pyspark.sql.functions import *

# String functions
upper(col("name"))
lower(col("name"))
concat(col("first"), lit(" "), col("last"))
substring(col("name"), 1, 3)

# Numeric functions
round(col("value"), 2)
abs(col("value"))
sqrt(col("value"))

# Date functions
current_date()
current_timestamp()
year(col("date"))
month(col("date"))
datediff(col("end_date"), col("start_date"))

# Conditional
when(col("age") < 18, "Minor").otherwise("Adult")

# Aggregation
count("*")
sum(col("amount"))
avg(col("salary"))
max(col("value"))
min(col("value"))

# Window functions
from pyspark.sql.window import Window
windowSpec = Window.partitionBy("category").orderBy("value")
row_number().over(windowSpec)
rank().over(windowSpec)
```

## ⚡ Performance Tips

```python
# Cache frequently used DataFrames
df.cache()
df.persist()
df.unpersist()

# Repartition
df.repartition(100)
df.coalesce(10)  # Reduce partitions (no shuffle)

# Broadcast small tables
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")

# Check partitions
df.rdd.getNumPartitions()

# Explain query plan
df.explain()
```

## 🎯 When to Use What

| Task | Use |
|------|-----|
| Simple transformations | DataFrame API |
| Complex queries | Spark SQL |
| Low-level control | RDD |
| Machine Learning | MLlib |
| Real-time processing | Structured Streaming |
| Large joins | Broadcast join (small table) |
| Aggregations | groupBy + agg |
| File format | Parquet (best) |

## ⚠️ Common Mistakes

### ❌ Don't
```python
# Don't collect large data
all_data = df.collect()  # OOM risk!

# Don't use UDFs when built-in functions exist
udf_func = udf(lambda x: x.upper())  # Slow!

# Don't forget to stop SparkSession
# Missing: spark.stop()
```

### ✅ Do
```python
# Use write instead of collect
df.write.parquet("output")

# Use built-in functions
from pyspark.sql.functions import upper
df.withColumn("name", upper(col("name")))

# Always stop SparkSession
spark.stop()
```

## 📊 Spark UI

Access at: **http://localhost:4040**

- **Jobs**: High-level view of jobs
- **Stages**: Detailed stage information
- **Storage**: Cached RDDs/DataFrames
- **Environment**: Configuration
- **Executors**: Worker information
- **SQL**: SQL query plans

## 🔗 Quick Links

- Examples: `01_rdd_basics.py` through `06_mllib_basics.py`
- Setup: `SETUP.md`
- Full docs: `README.md`
- Official: https://spark.apache.org/docs/latest/

## 💡 Remember

- **RDD**: Low-level, use for unstructured data
- **DataFrame**: High-level, use for structured data (preferred)
- **SQL**: Use for complex queries
- **Cache**: Only reused DataFrames
- **Parquet**: Best file format
- **Broadcast**: For small lookup tables
- **Spark UI**: Monitor performance

---

**Pro Tip**: Start with DataFrames, use SQL for complex queries, and monitor Spark UI! ⚡
