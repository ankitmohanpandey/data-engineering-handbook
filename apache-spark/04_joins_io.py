"""
Example 4: Joins and I/O Operations

This example demonstrates:
- Different types of joins (inner, left, right, full, cross)
- Reading from various file formats (CSV, JSON, Parquet)
- Writing to different formats
- Partitioning and bucketing
- Reading from multiple sources

WHAT IT DOES:
Shows how to join DataFrames and work with different file formats.

HOW TO RUN:
python 04_joins_io.py

EXPECTED OUTPUT:
Console output and files written to output/ directory.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os


def create_spark_session():
    """Create SparkSession."""
    spark = SparkSession.builder \
        .appName("Joins and I/O") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def join_types():
    """
    Demonstrate different types of joins.
    """
    print("\n" + "="*60)
    print("1. JOIN TYPES")
    print("="*60)
    
    spark = create_spark_session()
    
    # Left table: Employees
    employees = [
        (1, "Alice", 101),
        (2, "Bob", 102),
        (3, "Charlie", 101),
        (4, "Diana", 103),
        (5, "Eve", 104)  # No matching department
    ]
    emp_df = spark.createDataFrame(employees, ["emp_id", "name", "dept_id"])
    
    # Right table: Departments
    departments = [
        (101, "Engineering"),
        (102, "Sales"),
        (103, "Marketing"),
        (105, "HR")  # No matching employee
    ]
    dept_df = spark.createDataFrame(departments, ["dept_id", "dept_name"])
    
    print("\nEmployees:")
    emp_df.show()
    print("Departments:")
    dept_df.show()
    
    # INNER JOIN (default)
    print("\nINNER JOIN (only matching rows):")
    emp_df.join(dept_df, "dept_id", "inner").show()
    
    # LEFT JOIN (all from left + matching from right)
    print("\nLEFT JOIN (all employees + matching departments):")
    emp_df.join(dept_df, "dept_id", "left").show()
    
    # RIGHT JOIN (all from right + matching from left)
    print("\nRIGHT JOIN (all departments + matching employees):")
    emp_df.join(dept_df, "dept_id", "right").show()
    
    # FULL OUTER JOIN (all from both)
    print("\nFULL OUTER JOIN (all rows from both):")
    emp_df.join(dept_df, "dept_id", "outer").show()
    
    # LEFT ANTI JOIN (rows from left with no match in right)
    print("\nLEFT ANTI JOIN (employees without departments):")
    emp_df.join(dept_df, "dept_id", "left_anti").show()
    
    # LEFT SEMI JOIN (rows from left with match in right)
    print("\nLEFT SEMI JOIN (employees with departments):")
    emp_df.join(dept_df, "dept_id", "left_semi").show()
    
    # CROSS JOIN (Cartesian product)
    print("\nCROSS JOIN (all combinations):")
    small_emp = emp_df.limit(2)
    small_dept = dept_df.limit(2)
    small_emp.crossJoin(small_dept).show()
    
    spark.stop()


def complex_joins():
    """
    Complex join scenarios.
    """
    print("\n" + "="*60)
    print("2. COMPLEX JOINS")
    print("="*60)
    
    spark = create_spark_session()
    
    # Three tables
    employees = [
        (1, "Alice", 101),
        (2, "Bob", 102),
        (3, "Charlie", 101)
    ]
    emp_df = spark.createDataFrame(employees, ["emp_id", "name", "dept_id"])
    
    departments = [
        (101, "Engineering", "NY"),
        (102, "Sales", "LA")
    ]
    dept_df = spark.createDataFrame(departments, ["dept_id", "dept_name", "location"])
    
    salaries = [
        (1, 75000),
        (2, 65000),
        (3, 85000)
    ]
    sal_df = spark.createDataFrame(salaries, ["emp_id", "salary"])
    
    # Multiple joins
    print("\nMultiple joins:")
    result = (emp_df
              .join(dept_df, "dept_id")
              .join(sal_df, "emp_id"))
    result.show()
    
    # Join with different column names
    print("\nJoin with different column names:")
    emp_df2 = emp_df.withColumnRenamed("dept_id", "department_id")
    emp_df2.join(dept_df, emp_df2.department_id == dept_df.dept_id).show()
    
    # Join with multiple conditions
    print("\nJoin with multiple conditions:")
    emp_df.join(
        dept_df,
        (emp_df.dept_id == dept_df.dept_id) & (dept_df.location == "NY")
    ).show()
    
    spark.stop()


def read_write_csv():
    """
    Reading and writing CSV files.
    """
    print("\n" + "="*60)
    print("3. CSV I/O")
    print("="*60)
    
    spark = create_spark_session()
    
    # Create sample data
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", 30, 65000),
        (3, "Charlie", 35, 85000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    # Write CSV
    output_path = "output/employees.csv"
    df.write.mode("overwrite").csv(output_path, header=True)
    print(f"\n✅ Written to {output_path}")
    
    # Read CSV
    df_read = spark.read.csv(output_path, header=True, inferSchema=True)
    print("\nRead from CSV:")
    df_read.show()
    df_read.printSchema()
    
    # Read with options
    df_options = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .option("sep", ",") \
        .csv(output_path)
    
    spark.stop()


def read_write_json():
    """
    Reading and writing JSON files.
    """
    print("\n" + "="*60)
    print("4. JSON I/O")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25),
        (2, "Bob", 30),
        (3, "Charlie", 35)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age"])
    
    # Write JSON
    output_path = "output/employees.json"
    df.write.mode("overwrite").json(output_path)
    print(f"\n✅ Written to {output_path}")
    
    # Read JSON
    df_read = spark.read.json(output_path)
    print("\nRead from JSON:")
    df_read.show()
    
    spark.stop()


def read_write_parquet():
    """
    Reading and writing Parquet files (recommended format).
    """
    print("\n" + "="*60)
    print("5. PARQUET I/O (Recommended)")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", 30, 65000),
        (3, "Charlie", 35, 85000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    # Write Parquet
    output_path = "output/employees.parquet"
    df.write.mode("overwrite").parquet(output_path)
    print(f"\n✅ Written to {output_path}")
    
    # Read Parquet
    df_read = spark.read.parquet(output_path)
    print("\nRead from Parquet:")
    df_read.show()
    
    print("\nWhy Parquet?")
    print("✅ Columnar format (efficient for analytics)")
    print("✅ Compressed (smaller file size)")
    print("✅ Schema embedded (no need to infer)")
    print("✅ Fast reads (only read needed columns)")
    
    spark.stop()


def partitioning():
    """
    Partitioning data for better performance.
    """
    print("\n" + "="*60)
    print("6. PARTITIONING")
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
    
    # Write with partitioning
    output_path = "output/employees_partitioned"
    df.write.mode("overwrite").partitionBy("department").parquet(output_path)
    print(f"\n✅ Written partitioned data to {output_path}")
    print("Creates separate directories for each department")
    
    # Read partitioned data
    df_read = spark.read.parquet(output_path)
    print("\nRead partitioned data:")
    df_read.show()
    
    # Filter on partition column (efficient!)
    print("\nFilter on partition column (fast!):")
    df_read.filter(col("department") == "Engineering").show()
    
    spark.stop()


def save_modes():
    """
    Different save modes.
    """
    print("\n" + "="*60)
    print("7. SAVE MODES")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [(1, "Alice"), (2, "Bob")]
    df = spark.createDataFrame(data, ["id", "name"])
    
    output_path = "output/save_modes_test"
    
    print("\nSave modes:")
    print("1. overwrite: Replace existing data")
    print("2. append: Add to existing data")
    print("3. ignore: Do nothing if exists")
    print("4. error/errorifexists: Fail if exists (default)")
    
    # Overwrite mode
    df.write.mode("overwrite").parquet(output_path)
    print(f"\n✅ Written with mode='overwrite'")
    
    # Append mode
    df.write.mode("append").parquet(output_path)
    print(f"✅ Appended with mode='append'")
    
    # Read to verify
    df_read = spark.read.parquet(output_path)
    print(f"\nRows after append: {df_read.count()}")
    
    spark.stop()


# DETAILED EXPLANATION:
"""
JOINS AND I/O CONCEPTS:

1. JOIN TYPES:
   
   a) INNER JOIN:
      - Only matching rows from both tables
      - Default join type
      df1.join(df2, "key", "inner")
   
   b) LEFT JOIN (LEFT OUTER):
      - All rows from left + matching from right
      - NULLs for non-matching right rows
      df1.join(df2, "key", "left")
   
   c) RIGHT JOIN (RIGHT OUTER):
      - All rows from right + matching from left
      - NULLs for non-matching left rows
      df1.join(df2, "key", "right")
   
   d) FULL OUTER JOIN:
      - All rows from both tables
      - NULLs for non-matching rows
      df1.join(df2, "key", "outer")
   
   e) LEFT ANTI JOIN:
      - Rows from left with NO match in right
      - Like LEFT JOIN WHERE right IS NULL
      df1.join(df2, "key", "left_anti")
   
   f) LEFT SEMI JOIN:
      - Rows from left WITH match in right
      - Only returns left columns
      df1.join(df2, "key", "left_semi")
   
   g) CROSS JOIN:
      - Cartesian product (all combinations)
      - Use with caution (can be huge!)
      df1.crossJoin(df2)

2. JOIN CONDITIONS:
   
   a) Single column (same name):
      df1.join(df2, "key")
   
   b) Multiple columns:
      df1.join(df2, ["key1", "key2"])
   
   c) Different column names:
      df1.join(df2, df1.col1 == df2.col2)
   
   d) Complex conditions:
      df1.join(df2, (df1.col1 == df2.col2) & (df1.col3 > 10))

3. FILE FORMATS:
   
   a) CSV:
      - Human-readable
      - Slower than Parquet
      - Need to infer schema
      spark.read.csv("file.csv", header=True)
   
   b) JSON:
      - Semi-structured
      - Self-describing
      - Larger file size
      spark.read.json("file.json")
   
   c) Parquet (RECOMMENDED):
      - Columnar format
      - Compressed
      - Schema embedded
      - Fast reads
      spark.read.parquet("file.parquet")
   
   d) ORC:
      - Similar to Parquet
      - Optimized for Hive
      spark.read.orc("file.orc")
   
   e) Avro:
      - Row-based
      - Schema evolution
      spark.read.format("avro").load("file.avro")

4. READING DATA:
   
   # Basic read
   df = spark.read.csv("file.csv")
   
   # With options
   df = spark.read \
       .option("header", "true") \
       .option("inferSchema", "true") \
       .csv("file.csv")
   
   # Multiple files
   df = spark.read.csv("data/*.csv")
   
   # With schema
   df = spark.read.schema(schema).csv("file.csv")

5. WRITING DATA:
   
   # Basic write
   df.write.parquet("output.parquet")
   
   # With mode
   df.write.mode("overwrite").parquet("output.parquet")
   
   # With partitioning
   df.write.partitionBy("year", "month").parquet("output")
   
   # With options
   df.write \
       .option("compression", "snappy") \
       .parquet("output.parquet")

6. SAVE MODES:
   - overwrite: Replace existing data
   - append: Add to existing data
   - ignore: Skip if exists
   - error: Fail if exists (default)

7. PARTITIONING:
   - Divide data into directories by column values
   - Improves query performance
   - Partition pruning (skip irrelevant partitions)
   
   df.write.partitionBy("year", "month").parquet("output")
   
   Creates structure:
   output/
     year=2024/
       month=01/
         part-00000.parquet
       month=02/
         part-00000.parquet

8. BUCKETING:
   - Divide data into fixed number of buckets
   - Based on hash of column
   - Improves join performance
   
   df.write.bucketBy(10, "id").saveAsTable("table")

9. BEST PRACTICES:
   
   a) File Format:
      ✅ Use Parquet for analytics
      ✅ Use Avro for streaming
      ❌ Avoid CSV for large data
   
   b) Partitioning:
      ✅ Partition by frequently filtered columns
      ✅ Avoid too many partitions (< 10,000)
      ✅ Partition by date/time for time-series
   
   c) Joins:
      ✅ Use broadcast for small tables
      ✅ Filter before join
      ✅ Select only needed columns
      ❌ Avoid cross joins
   
   d) Reading:
      ✅ Specify schema when possible
      ✅ Use column pruning (select specific columns)
      ✅ Use predicate pushdown (filter early)

10. PERFORMANCE TIPS:
    
    # Broadcast small table
    from pyspark.sql.functions import broadcast
    large_df.join(broadcast(small_df), "key")
    
    # Repartition before join
    df1.repartition("key").join(df2.repartition("key"), "key")
    
    # Cache frequently used DataFrames
    df.cache()
    
    # Use Parquet with compression
    df.write.option("compression", "snappy").parquet("output")

COMMON PATTERNS:

# ETL Pipeline
df = (spark.read.parquet("input.parquet")
      .filter(col("date") > "2024-01-01")
      .join(lookup_df, "id")
      .groupBy("category").agg(sum("amount"))
      .write.partitionBy("category").parquet("output"))

# Incremental Load
new_data.write.mode("append").parquet("data.parquet")

# Slowly Changing Dimension (SCD)
existing = spark.read.parquet("dimension.parquet")
updates = new_data.join(existing, "id", "left_anti")
updates.write.mode("append").parquet("dimension.parquet")
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - JOINS AND I/O")
    print("#"*60)
    
    join_types()
    complex_joins()
    read_write_csv()
    read_write_json()
    read_write_parquet()
    partitioning()
    save_modes()
    
    print("\n" + "#"*60)
    print("# ✅ ALL JOIN AND I/O EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nCheck output/ directory for generated files")
