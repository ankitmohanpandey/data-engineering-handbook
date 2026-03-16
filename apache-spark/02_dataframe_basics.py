"""
Example 2: DataFrame Basics

This example demonstrates:
- Creating DataFrames from various sources
- DataFrame operations (select, filter, groupBy)
- Column operations and expressions
- Schema definition and inference
- Working with structured data

WHAT IT DOES:
Introduces DataFrame API - the preferred way to work with Spark.

HOW TO RUN:
python 02_dataframe_basics.py

EXPECTED OUTPUT:
Console output showing DataFrame operations and results.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import col, lit, when, concat, upper, lower


def create_spark_session():
    """Create SparkSession."""
    spark = SparkSession.builder \
        .appName("DataFrame Basics") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def create_dataframes():
    """
    Different ways to create DataFrames.
    """
    print("\n" + "="*60)
    print("1. CREATING DATAFRAMES")
    print("="*60)
    
    spark = create_spark_session()
    
    # Method 1: From list of tuples
    data = [
        (1, "Alice", 25, "Engineer"),
        (2, "Bob", 30, "Manager"),
        (3, "Charlie", 35, "Director")
    ]
    df1 = spark.createDataFrame(data, ["id", "name", "age", "role"])
    print("\nDataFrame from tuples:")
    df1.show()
    
    # Method 2: From list of dictionaries
    data_dict = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
        {"id": 3, "name": "Charlie", "age": 35}
    ]
    df2 = spark.createDataFrame(data_dict)
    print("\nDataFrame from dictionaries:")
    df2.show()
    
    # Method 3: With explicit schema
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False),
        StructField("salary", DoubleType(), True)
    ])
    
    data_with_schema = [
        (1, "Alice", 75000.0),
        (2, "Bob", 85000.0),
        (3, "Charlie", 95000.0)
    ]
    df3 = spark.createDataFrame(data_with_schema, schema)
    print("\nDataFrame with explicit schema:")
    df3.show()
    df3.printSchema()
    
    # Method 4: From RDD
    rdd = spark.sparkContext.parallelize([
        (1, "Product A", 100),
        (2, "Product B", 200)
    ])
    df4 = rdd.toDF(["id", "product", "price"])
    print("\nDataFrame from RDD:")
    df4.show()
    
    spark.stop()


def basic_operations():
    """
    Basic DataFrame operations.
    """
    print("\n" + "="*60)
    print("2. BASIC DATAFRAME OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data
    data = [
        (1, "Alice", 25, "Engineering", 75000),
        (2, "Bob", 30, "Sales", 65000),
        (3, "Charlie", 35, "Engineering", 85000),
        (4, "Diana", 28, "Marketing", 70000),
        (5, "Eve", 32, "Sales", 68000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "department", "salary"])
    
    print("\nOriginal DataFrame:")
    df.show()
    
    # show(): Display data
    print("\nFirst 3 rows:")
    df.show(3)
    
    # printSchema(): Show schema
    print("\nSchema:")
    df.printSchema()
    
    # count(): Number of rows
    print(f"\nRow count: {df.count()}")
    
    # columns: List column names
    print(f"Columns: {df.columns}")
    
    # describe(): Statistics
    print("\nStatistics:")
    df.describe().show()
    
    # head() and take(): Get first N rows
    print(f"\nFirst row: {df.head()}")
    print(f"First 2 rows: {df.take(2)}")
    
    # collect(): Get all rows (use carefully!)
    all_rows = df.collect()
    print(f"\nFirst collected row: {all_rows[0]}")
    
    spark.stop()


def select_operations():
    """
    Select and column operations.
    """
    print("\n" + "="*60)
    print("3. SELECT OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", 30, 65000),
        (3, "Charlie", 35, 85000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    # Select specific columns
    print("\nSelect name and age:")
    df.select("name", "age").show()
    
    # Select using col()
    print("\nSelect using col():")
    df.select(col("name"), col("salary")).show()
    
    # Select all columns
    print("\nSelect all columns:")
    df.select("*").show()
    
    # Select with expressions
    print("\nSelect with expression (salary in thousands):")
    df.select("name", (col("salary") / 1000).alias("salary_k")).show()
    
    # Add new column
    print("\nAdd bonus column (10% of salary):")
    df.withColumn("bonus", col("salary") * 0.1).show()
    
    # Rename column
    print("\nRename 'name' to 'employee_name':")
    df.withColumnRenamed("name", "employee_name").show()
    
    # Drop column
    print("\nDrop 'id' column:")
    df.drop("id").show()
    
    # Multiple operations chained
    print("\nChained operations:")
    (df
     .select("name", "age", "salary")
     .withColumn("age_group", when(col("age") < 30, "Young").otherwise("Senior"))
     .withColumn("salary_k", col("salary") / 1000)
     .drop("salary")
     .show())
    
    spark.stop()


def filter_operations():
    """
    Filtering DataFrames.
    """
    print("\n" + "="*60)
    print("4. FILTER OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, "Engineering", 75000),
        (2, "Bob", 30, "Sales", 65000),
        (3, "Charlie", 35, "Engineering", 85000),
        (4, "Diana", 28, "Marketing", 70000),
        (5, "Eve", 32, "Sales", 68000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "department", "salary"])
    
    print("\nOriginal DataFrame:")
    df.show()
    
    # filter() or where() - same thing
    print("\nFilter: age > 30")
    df.filter(col("age") > 30).show()
    
    print("\nWhere: salary >= 70000")
    df.where(col("salary") >= 70000).show()
    
    # Multiple conditions with &, |, ~
    print("\nFilter: age > 25 AND salary > 70000")
    df.filter((col("age") > 25) & (col("salary") > 70000)).show()
    
    print("\nFilter: department = Engineering OR Sales")
    df.filter((col("department") == "Engineering") | (col("department") == "Sales")).show()
    
    # String operations
    print("\nFilter: name starts with 'A'")
    df.filter(col("name").startswith("A")).show()
    
    print("\nFilter: name contains 'li'")
    df.filter(col("name").contains("li")).show()
    
    # IN operator
    print("\nFilter: department IN (Engineering, Marketing)")
    df.filter(col("department").isin(["Engineering", "Marketing"])).show()
    
    # NOT NULL
    print("\nFilter: name is not null")
    df.filter(col("name").isNotNull()).show()
    
    # SQL-style string filter
    print("\nSQL-style filter:")
    df.filter("age > 30 AND salary > 70000").show()
    
    spark.stop()


def aggregation_operations():
    """
    Aggregation and groupBy operations.
    """
    print("\n" + "="*60)
    print("5. AGGREGATION OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", "Engineering", 75000),
        (2, "Bob", "Sales", 65000),
        (3, "Charlie", "Engineering", 85000),
        (4, "Diana", "Marketing", 70000),
        (5, "Eve", "Sales", 68000),
        (6, "Frank", "Engineering", 80000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "department", "salary"])
    
    print("\nOriginal DataFrame:")
    df.show()
    
    # groupBy and count
    print("\nCount by department:")
    df.groupBy("department").count().show()
    
    # groupBy and sum
    print("\nTotal salary by department:")
    df.groupBy("department").sum("salary").show()
    
    # groupBy and avg
    print("\nAverage salary by department:")
    df.groupBy("department").avg("salary").show()
    
    # groupBy and multiple aggregations
    from pyspark.sql.functions import sum, avg, max, min, count
    
    print("\nMultiple aggregations:")
    (df.groupBy("department")
     .agg(
         count("*").alias("employee_count"),
         sum("salary").alias("total_salary"),
         avg("salary").alias("avg_salary"),
         max("salary").alias("max_salary"),
         min("salary").alias("min_salary")
     )
     .show())
    
    # Global aggregations (no groupBy)
    print("\nGlobal aggregations:")
    df.agg(
        count("*").alias("total_employees"),
        avg("salary").alias("avg_salary")
    ).show()
    
    spark.stop()


def sorting_operations():
    """
    Sorting DataFrames.
    """
    print("\n" + "="*60)
    print("6. SORTING OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", 30, 65000),
        (3, "Charlie", 35, 85000),
        (4, "Diana", 28, 70000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    print("\nOriginal DataFrame:")
    df.show()
    
    # Sort by one column (ascending)
    print("\nSort by age (ascending):")
    df.orderBy("age").show()
    
    # Sort by one column (descending)
    print("\nSort by salary (descending):")
    df.orderBy(col("salary").desc()).show()
    
    # Sort by multiple columns
    print("\nSort by age (asc), then salary (desc):")
    df.orderBy(col("age").asc(), col("salary").desc()).show()
    
    # sort() is alias for orderBy()
    print("\nUsing sort():")
    df.sort("name").show()
    
    spark.stop()


def column_operations():
    """
    Advanced column operations.
    """
    print("\n" + "="*60)
    print("7. COLUMN OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "alice", "smith", 25),
        (2, "bob", "jones", 30),
        (3, "charlie", "brown", 35)
    ]
    df = spark.createDataFrame(data, ["id", "first_name", "last_name", "age"])
    
    print("\nOriginal DataFrame:")
    df.show()
    
    # String functions
    print("\nUppercase first_name:")
    df.withColumn("first_name", upper(col("first_name"))).show()
    
    # Concatenate columns
    print("\nConcatenate first_name and last_name:")
    df.withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name"))).show()
    
    # Conditional column (when/otherwise)
    print("\nAdd age_category column:")
    (df.withColumn("age_category",
                   when(col("age") < 30, "Young")
                   .when(col("age") < 40, "Middle")
                   .otherwise("Senior"))
     .show())
    
    # Mathematical operations
    print("\nAge in months:")
    df.withColumn("age_months", col("age") * 12).show()
    
    # Cast column type
    print("\nCast age to string:")
    df.withColumn("age_str", col("age").cast(StringType())).show()
    df.withColumn("age_str", col("age").cast(StringType())).printSchema()
    
    spark.stop()


def handling_nulls():
    """
    Handling NULL values.
    """
    print("\n" + "="*60)
    print("8. HANDLING NULL VALUES")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", None, 65000),
        (3, "Charlie", 35, None),
        (4, None, 28, 70000),
        (5, "Eve", None, None)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    print("\nDataFrame with NULLs:")
    df.show()
    
    # Drop rows with any NULL
    print("\nDrop rows with any NULL:")
    df.dropna().show()
    
    # Drop rows with NULL in specific columns
    print("\nDrop rows with NULL in 'age':")
    df.dropna(subset=["age"]).show()
    
    # Fill NULLs with default values
    print("\nFill NULLs with defaults:")
    df.fillna({"name": "Unknown", "age": 0, "salary": 0}).show()
    
    # Replace specific values
    print("\nReplace NULL ages with average:")
    avg_age = df.select(avg("age")).collect()[0][0]
    df.fillna({"age": avg_age}).show()
    
    spark.stop()


# DETAILED EXPLANATION:
"""
DATAFRAME CONCEPTS:

1. What is a DataFrame?
   - Distributed collection of data organized into named columns
   - Like a table in SQL or pandas DataFrame
   - Built on top of RDDs but with schema
   - Optimized by Catalyst optimizer
   - Preferred over RDDs for structured data

2. Creating DataFrames:
   a) From collections:
      spark.createDataFrame(data, schema)
   
   b) From files:
      spark.read.csv("file.csv")
      spark.read.json("file.json")
      spark.read.parquet("file.parquet")
   
   c) From RDD:
      rdd.toDF(["col1", "col2"])
   
   d) From SQL query:
      spark.sql("SELECT * FROM table")

3. Schema:
   - Defines structure (column names and types)
   - Can be inferred or explicit
   
   Explicit schema:
   schema = StructType([
       StructField("name", StringType(), False),
       StructField("age", IntegerType(), True)
   ])

4. Basic Operations:
   - show(): Display data
   - printSchema(): Show schema
   - count(): Count rows
   - describe(): Statistics
   - columns: List columns
   - dtypes: Column types

5. Select Operations:
   - select(): Choose columns
   - withColumn(): Add/modify column
   - withColumnRenamed(): Rename column
   - drop(): Remove column
   
   Examples:
   df.select("col1", "col2")
   df.withColumn("new_col", col("old_col") * 2)
   df.drop("col1")

6. Filter Operations:
   - filter() or where(): Filter rows
   - Conditions: ==, !=, >, <, >=, <=
   - Logical: & (and), | (or), ~ (not)
   - String: startswith, endswith, contains
   - NULL: isNull, isNotNull
   
   Examples:
   df.filter(col("age") > 25)
   df.where((col("age") > 25) & (col("salary") > 50000))

7. Aggregations:
   - groupBy(): Group by columns
   - agg(): Aggregate functions
   - Functions: count, sum, avg, max, min
   
   Examples:
   df.groupBy("department").count()
   df.groupBy("dept").agg(avg("salary"), max("age"))

8. Sorting:
   - orderBy() or sort(): Sort rows
   - asc(): Ascending (default)
   - desc(): Descending
   
   Examples:
   df.orderBy("age")
   df.orderBy(col("salary").desc())

9. Column Operations:
   - Arithmetic: +, -, *, /
   - String: upper, lower, concat, substring
   - Conditional: when, otherwise
   - Type casting: cast()
   
   Examples:
   df.withColumn("doubled", col("value") * 2)
   df.withColumn("upper_name", upper(col("name")))

10. NULL Handling:
    - dropna(): Drop rows with NULLs
    - fillna(): Fill NULLs with values
    - isNull(), isNotNull(): Check for NULLs
    
    Examples:
    df.dropna()
    df.fillna({"age": 0, "name": "Unknown"})

11. DataFrame vs RDD:
    DataFrame:
    ✅ High-level API
    ✅ Schema with named columns
    ✅ Catalyst optimizer
    ✅ SQL-like operations
    ✅ Better performance
    
    RDD:
    ✅ Low-level control
    ✅ Unstructured data
    ✅ Custom partitioning
    ❌ No optimization
    
    Recommendation: Use DataFrames!

12. Best Practices:
    - Use DataFrames over RDDs
    - Avoid collect() on large data
    - Use built-in functions (faster than UDFs)
    - Cache DataFrames that are reused
    - Use Parquet format for storage
    - Monitor Spark UI for optimization

COMMON PATTERNS:

# Read, transform, write
df = spark.read.csv("input.csv", header=True)
result = (df
    .filter(col("age") > 25)
    .groupBy("department")
    .agg(avg("salary"))
)
result.write.parquet("output.parquet")

# Chaining operations
result = (df
    .select("name", "age", "salary")
    .filter(col("age") > 25)
    .withColumn("bonus", col("salary") * 0.1)
    .orderBy(col("salary").desc())
)
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - DATAFRAME BASICS")
    print("#"*60)
    
    create_dataframes()
    basic_operations()
    select_operations()
    filter_operations()
    aggregation_operations()
    sorting_operations()
    column_operations()
    handling_nulls()
    
    print("\n" + "#"*60)
    print("# ✅ ALL DATAFRAME EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nNext: Run 03_spark_sql.py to learn about Spark SQL")
