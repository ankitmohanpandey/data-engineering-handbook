"""
Example 3: Spark SQL

This example demonstrates:
- Creating temporary views and tables
- Running SQL queries on DataFrames
- Joining tables with SQL
- Using SQL functions
- Mixing DataFrame and SQL APIs

WHAT IT DOES:
Shows how to use SQL syntax with Spark DataFrames.

HOW TO RUN:
python 03_spark_sql.py

EXPECTED OUTPUT:
Console output showing SQL query results.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def create_spark_session():
    """Create SparkSession."""
    spark = SparkSession.builder \
        .appName("Spark SQL") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def basic_sql_queries():
    """
    Basic SQL queries on DataFrames.
    """
    print("\n" + "="*60)
    print("1. BASIC SQL QUERIES")
    print("="*60)
    
    spark = create_spark_session()
    
    # Create DataFrame
    data = [
        (1, "Alice", 25, "Engineering", 75000),
        (2, "Bob", 30, "Sales", 65000),
        (3, "Charlie", 35, "Engineering", 85000),
        (4, "Diana", 28, "Marketing", 70000),
        (5, "Eve", 32, "Sales", 68000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "department", "salary"])
    
    # Create temporary view
    df.createOrReplaceTempView("employees")
    
    # Simple SELECT
    print("\nSELECT all:")
    spark.sql("SELECT * FROM employees").show()
    
    # SELECT specific columns
    print("\nSELECT name and salary:")
    spark.sql("SELECT name, salary FROM employees").show()
    
    # WHERE clause
    print("\nWHERE age > 30:")
    spark.sql("SELECT * FROM employees WHERE age > 30").show()
    
    # ORDER BY
    print("\nORDER BY salary DESC:")
    spark.sql("SELECT name, salary FROM employees ORDER BY salary DESC").show()
    
    # LIMIT
    print("\nLIMIT 3:")
    spark.sql("SELECT * FROM employees LIMIT 3").show()
    
    spark.stop()


def aggregation_sql():
    """
    SQL aggregation queries.
    """
    print("\n" + "="*60)
    print("2. SQL AGGREGATIONS")
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
    df.createOrReplaceTempView("employees")
    
    # COUNT
    print("\nCOUNT by department:")
    spark.sql("""
        SELECT department, COUNT(*) as count
        FROM employees
        GROUP BY department
    """).show()
    
    # SUM
    print("\nSUM salary by department:")
    spark.sql("""
        SELECT department, SUM(salary) as total_salary
        FROM employees
        GROUP BY department
    """).show()
    
    # AVG
    print("\nAVG salary by department:")
    spark.sql("""
        SELECT department, AVG(salary) as avg_salary
        FROM employees
        GROUP BY department
    """).show()
    
    # Multiple aggregations
    print("\nMultiple aggregations:")
    spark.sql("""
        SELECT 
            department,
            COUNT(*) as employee_count,
            AVG(salary) as avg_salary,
            MAX(salary) as max_salary,
            MIN(salary) as min_salary
        FROM employees
        GROUP BY department
        ORDER BY avg_salary DESC
    """).show()
    
    # HAVING clause
    print("\nHAVING avg_salary > 70000:")
    spark.sql("""
        SELECT department, AVG(salary) as avg_salary
        FROM employees
        GROUP BY department
        HAVING AVG(salary) > 70000
    """).show()
    
    spark.stop()


def join_operations():
    """
    SQL JOIN operations.
    """
    print("\n" + "="*60)
    print("3. SQL JOINS")
    print("="*60)
    
    spark = create_spark_session()
    
    # Employees table
    employees = [
        (1, "Alice", 1),
        (2, "Bob", 2),
        (3, "Charlie", 1),
        (4, "Diana", 3)
    ]
    emp_df = spark.createDataFrame(employees, ["id", "name", "dept_id"])
    emp_df.createOrReplaceTempView("employees")
    
    # Departments table
    departments = [
        (1, "Engineering"),
        (2, "Sales"),
        (3, "Marketing")
    ]
    dept_df = spark.createDataFrame(departments, ["dept_id", "dept_name"])
    dept_df.createOrReplaceTempView("departments")
    
    print("\nEmployees:")
    emp_df.show()
    print("Departments:")
    dept_df.show()
    
    # INNER JOIN
    print("\nINNER JOIN:")
    spark.sql("""
        SELECT e.name, d.dept_name
        FROM employees e
        INNER JOIN departments d ON e.dept_id = d.dept_id
    """).show()
    
    # LEFT JOIN
    print("\nLEFT JOIN:")
    spark.sql("""
        SELECT e.name, d.dept_name
        FROM employees e
        LEFT JOIN departments d ON e.dept_id = d.dept_id
    """).show()
    
    # Multiple table join
    salaries = [
        (1, 75000),
        (2, 65000),
        (3, 85000)
    ]
    sal_df = spark.createDataFrame(salaries, ["emp_id", "salary"])
    sal_df.createOrReplaceTempView("salaries")
    
    print("\nMultiple table JOIN:")
    spark.sql("""
        SELECT e.name, d.dept_name, s.salary
        FROM employees e
        INNER JOIN departments d ON e.dept_id = d.dept_id
        LEFT JOIN salaries s ON e.id = s.emp_id
    """).show()
    
    spark.stop()


def subqueries_cte():
    """
    Subqueries and CTEs (Common Table Expressions).
    """
    print("\n" + "="*60)
    print("4. SUBQUERIES AND CTEs")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", "Engineering", 75000),
        (2, "Bob", "Sales", 65000),
        (3, "Charlie", "Engineering", 85000),
        (4, "Diana", "Marketing", 70000),
        (5, "Eve", "Sales", 68000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "department", "salary"])
    df.createOrReplaceTempView("employees")
    
    # Subquery in WHERE
    print("\nSubquery - employees with above average salary:")
    spark.sql("""
        SELECT name, salary
        FROM employees
        WHERE salary > (SELECT AVG(salary) FROM employees)
    """).show()
    
    # Subquery in FROM
    print("\nSubquery in FROM:")
    spark.sql("""
        SELECT dept, avg_sal
        FROM (
            SELECT department as dept, AVG(salary) as avg_sal
            FROM employees
            GROUP BY department
        )
        WHERE avg_sal > 70000
    """).show()
    
    # CTE (WITH clause)
    print("\nCTE - department statistics:")
    spark.sql("""
        WITH dept_stats AS (
            SELECT 
                department,
                COUNT(*) as emp_count,
                AVG(salary) as avg_salary
            FROM employees
            GROUP BY department
        )
        SELECT * FROM dept_stats
        WHERE avg_salary > 70000
        ORDER BY avg_salary DESC
    """).show()
    
    # Multiple CTEs
    print("\nMultiple CTEs:")
    spark.sql("""
        WITH 
        high_earners AS (
            SELECT * FROM employees WHERE salary > 70000
        ),
        dept_counts AS (
            SELECT department, COUNT(*) as count
            FROM high_earners
            GROUP BY department
        )
        SELECT * FROM dept_counts
    """).show()
    
    spark.stop()


def window_functions():
    """
    SQL window functions.
    """
    print("\n" + "="*60)
    print("5. WINDOW FUNCTIONS")
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
    df.createOrReplaceTempView("employees")
    
    # ROW_NUMBER
    print("\nROW_NUMBER - rank within department:")
    spark.sql("""
        SELECT 
            name, 
            department, 
            salary,
            ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
        FROM employees
    """).show()
    
    # RANK and DENSE_RANK
    print("\nRANK vs DENSE_RANK:")
    spark.sql("""
        SELECT 
            name, 
            salary,
            RANK() OVER (ORDER BY salary DESC) as rank,
            DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
        FROM employees
    """).show()
    
    # Running total
    print("\nRunning total of salary:")
    spark.sql("""
        SELECT 
            name, 
            salary,
            SUM(salary) OVER (ORDER BY id) as running_total
        FROM employees
    """).show()
    
    # LAG and LEAD
    print("\nLAG and LEAD:")
    spark.sql("""
        SELECT 
            name, 
            salary,
            LAG(salary, 1) OVER (ORDER BY id) as prev_salary,
            LEAD(salary, 1) OVER (ORDER BY id) as next_salary
        FROM employees
    """).show()
    
    spark.stop()


def mixing_sql_dataframe():
    """
    Mixing SQL and DataFrame APIs.
    """
    print("\n" + "="*60)
    print("6. MIXING SQL AND DATAFRAME APIs")
    print("="*60)
    
    spark = create_spark_session()
    
    data = [
        (1, "Alice", 25, 75000),
        (2, "Bob", 30, 65000),
        (3, "Charlie", 35, 85000)
    ]
    df = spark.createDataFrame(data, ["id", "name", "age", "salary"])
    
    # DataFrame -> SQL
    df.createOrReplaceTempView("employees")
    sql_result = spark.sql("SELECT * FROM employees WHERE age > 25")
    
    print("\nSQL result:")
    sql_result.show()
    
    # SQL result is a DataFrame - can use DataFrame API
    print("\nUsing DataFrame API on SQL result:")
    (sql_result
     .withColumn("bonus", col("salary") * 0.1)
     .select("name", "salary", "bonus")
     .show())
    
    # DataFrame -> SQL -> DataFrame
    print("\nChaining SQL and DataFrame:")
    result = (spark.sql("SELECT * FROM employees WHERE salary > 70000")
              .filter(col("age") < 40)
              .withColumn("salary_k", col("salary") / 1000))
    result.show()
    
    spark.stop()


# DETAILED EXPLANATION:
"""
SPARK SQL CONCEPTS:

1. What is Spark SQL?
   - Module for structured data processing
   - Provides SQL interface to Spark
   - Works with DataFrames
   - Catalyst optimizer for query optimization

2. Temporary Views:
   - Create SQL table from DataFrame
   - Exists only in current session
   
   df.createOrReplaceTempView("table_name")
   spark.sql("SELECT * FROM table_name")

3. Global Temporary Views:
   - Shared across sessions
   - Tied to system database
   
   df.createGlobalTempView("table_name")
   spark.sql("SELECT * FROM global_temp.table_name")

4. SQL Operations:
   
   a) SELECT:
      SELECT col1, col2 FROM table
   
   b) WHERE:
      WHERE condition
   
   c) GROUP BY:
      GROUP BY col1, col2
   
   d) HAVING:
      HAVING aggregate_condition
   
   e) ORDER BY:
      ORDER BY col1 DESC, col2 ASC
   
   f) LIMIT:
      LIMIT n

5. Aggregation Functions:
   - COUNT(*), COUNT(col)
   - SUM(col)
   - AVG(col)
   - MAX(col), MIN(col)
   - STDDEV(col)
   - COLLECT_LIST(col)

6. JOIN Types:
   - INNER JOIN: Matching rows from both tables
   - LEFT JOIN: All from left + matching from right
   - RIGHT JOIN: All from right + matching from left
   - FULL OUTER JOIN: All rows from both tables
   - CROSS JOIN: Cartesian product

7. Subqueries:
   - In WHERE: WHERE col > (SELECT AVG(col) FROM table)
   - In FROM: FROM (SELECT ... FROM table) AS subquery
   - In SELECT: SELECT col, (SELECT ... FROM table2) AS sub

8. CTEs (Common Table Expressions):
   - WITH clause for named subqueries
   - More readable than nested subqueries
   
   WITH cte_name AS (
       SELECT ... FROM table
   )
   SELECT * FROM cte_name

9. Window Functions:
   - Perform calculations across rows
   - PARTITION BY: Group rows
   - ORDER BY: Order within partition
   
   Functions:
   - ROW_NUMBER(): Sequential number
   - RANK(): Rank with gaps
   - DENSE_RANK(): Rank without gaps
   - LAG(): Previous row value
   - LEAD(): Next row value
   - SUM() OVER: Running total
   - AVG() OVER: Moving average

10. SQL vs DataFrame API:
    
    SQL:
    ✅ Familiar syntax
    ✅ Easy for SQL users
    ✅ Complex queries readable
    
    DataFrame:
    ✅ Type-safe (compile-time checking)
    ✅ Better IDE support
    ✅ Programmatic construction
    
    Both are optimized the same way by Catalyst!

11. Best Practices:
    - Use SQL for complex queries
    - Use DataFrame API for programmatic logic
    - Mix both as needed
    - Create views for reusable queries
    - Use CTEs for readability
    - Avoid SELECT * in production

12. Common Patterns:
    
    # Read data
    df = spark.read.csv("data.csv")
    df.createOrReplaceTempView("data")
    
    # Run SQL
    result = spark.sql(\"\"\"
        SELECT category, SUM(amount) as total
        FROM data
        WHERE date > '2024-01-01'
        GROUP BY category
    \"\"\")
    
    # Continue with DataFrame API
    result.filter(col("total") > 1000).show()

COMPARISON:

DataFrame API:
df.select("name", "age").filter(col("age") > 25)

SQL:
spark.sql("SELECT name, age FROM table WHERE age > 25")

Both produce the same optimized execution plan!
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - SPARK SQL")
    print("#"*60)
    
    basic_sql_queries()
    aggregation_sql()
    join_operations()
    subqueries_cte()
    window_functions()
    mixing_sql_dataframe()
    
    print("\n" + "#"*60)
    print("# ✅ ALL SPARK SQL EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nNext: Run 04_aggregations.py for advanced aggregations")
