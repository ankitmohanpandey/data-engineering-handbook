"""
Example 2: Table API & SQL Basics

This example demonstrates:
- Creating a TableEnvironment (streaming mode)
- Creating tables from in-memory data
- Table API operations (select, filter, group_by)
- Running Flink SQL queries
- Converting between DataStream and Table

WHAT IT DOES:
Introduces the declarative Table API/SQL layer, Flink's high-level,
Calcite-optimized alternative to the DataStream API.

HOW TO RUN:
python 02_table_api_basics.py

EXPECTED OUTPUT:
Console output showing Table API/SQL query results.
"""

from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.expressions import col


def create_table_environment():
    """
    Create and configure a streaming TableEnvironment.
    This is the entry point for the Table API / SQL, analogous to
    Spark's SparkSession for Spark SQL.
    """
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    return t_env


def basic_table_operations():
    """
    Basic Table creation and operations using the fluent Table API.
    """
    print("\n" + "=" * 60)
    print("1. BASIC TABLE API OPERATIONS")
    print("=" * 60)

    t_env = create_table_environment()

    # Create a table from an in-memory list of rows (learning/testing only)
    table = t_env.from_elements(
        [
            (1, "Alice", 25, "Engineering"),
            (2, "Bob", 30, "Sales"),
            (3, "Carol", 28, "Engineering"),
            (4, "Dave", 35, "Marketing"),
        ],
        ["id", "name", "age", "department"],
    )

    print("All rows:")
    table.execute().print()

    print("Filtered (age > 27):")
    table.filter(col("age") > 27).execute().print()

    print("Selected columns:")
    table.select(col("name"), col("department")).execute().print()


def group_by_aggregation_demo():
    """
    Demonstrate GROUP BY-style aggregation using the Table API.
    """
    print("\n" + "=" * 60)
    print("2. GROUP BY AGGREGATION")
    print("=" * 60)

    t_env = create_table_environment()

    table = t_env.from_elements(
        [
            (1, "Alice", 25, "Engineering"),
            (2, "Bob", 30, "Sales"),
            (3, "Carol", 28, "Engineering"),
            (4, "Dave", 35, "Marketing"),
            (5, "Eve", 40, "Sales"),
        ],
        ["id", "name", "age", "department"],
    )

    result = (
        table.group_by(col("department"))
        .select(col("department"), col("age").avg.alias("avg_age"), col("id").count.alias("headcount"))
    )

    result.execute().print()


def sql_queries_demo():
    """
    Demonstrate running plain Flink SQL against a registered table.
    """
    print("\n" + "=" * 60)
    print("3. FLINK SQL QUERIES")
    print("=" * 60)

    t_env = create_table_environment()

    table = t_env.from_elements(
        [
            (1, "Alice", 25, "Engineering"),
            (2, "Bob", 30, "Sales"),
            (3, "Carol", 28, "Engineering"),
            (4, "Dave", 35, "Marketing"),
        ],
        ["id", "name", "age", "department"],
    )

    # Register as a temporary view, just like Spark's createOrReplaceTempView
    t_env.create_temporary_view("employees", table)

    result = t_env.sql_query(
        """
        SELECT department, COUNT(*) AS headcount, AVG(age) AS avg_age
        FROM employees
        GROUP BY department
        """
    )

    result.execute().print()


def ddl_table_demo():
    """
    Demonstrate creating a table via SQL DDL backed by a connector
    (here, the 'datagen' connector, useful for testing pipelines without
    needing a real external system).
    """
    print("\n" + "=" * 60)
    print("4. SQL DDL WITH A CONNECTOR (datagen)")
    print("=" * 60)

    t_env = create_table_environment()

    t_env.execute_sql(
        """
        CREATE TABLE synthetic_orders (
            order_id BIGINT,
            amount DOUBLE,
            customer STRING
        ) WITH (
            'connector' = 'datagen',
            'number-of-rows' = '10'
        )
        """
    )

    result = t_env.sql_query("SELECT * FROM synthetic_orders")
    result.execute().print()


# DETAILED EXPLANATION:-
"""
TABLE API / SQL CONCEPTS:

1. What is the Table API?
   - High-level, declarative API for both batch and streaming data
   - Built on Apache Calcite for query parsing, validation, and optimization
   - Table API and SQL are fully interchangeable -- mix and match freely

2. TableEnvironment:
   - Entry point for the Table API / SQL, analogous to Spark's SparkSession
   - `EnvironmentSettings.in_streaming_mode()` vs `in_batch_mode()`
   - Can convert to/from DataStreams via StreamTableEnvironment

3. Creating Tables:
   a) From in-memory elements (testing):
      t_env.from_elements([...], ["col1", "col2"])

   b) Via SQL DDL with a connector:
      CREATE TABLE t (...) WITH ('connector' = 'kafka', ...)

   c) From an existing DataStream:
      table = t_env.from_data_stream(ds)

4. Table API Operations (fluent, similar to PySpark DataFrame API):
   - select(), filter()/where(), group_by()
   - Aggregations: .avg, .sum, .count, .max, .min (as column expressions)
   - join(), union_all()

5. Dynamic Tables (the Streaming/SQL Duality):
   - In streaming mode, a "table" is really a continuously changing
     "Dynamic Table" -- new rows keep arriving and results keep updating
   - A query against a dynamic table produces a changelog stream of
     INSERT / UPDATE_BEFORE / UPDATE_AFTER / DELETE records
   - This is what makes Flink SQL suitable for CDC-style use cases

6. Table <-> DataStream Conversion:
   - `t_env.to_data_stream(table)` -- append-only stream
   - `t_env.to_changelog_stream(table)` -- full changelog (inserts/updates/deletes)
   - `t_env.from_data_stream(ds)` -- wrap a DataStream as a Table

7. When to Use Table API/SQL vs DataStream API:
   ✅ Standard aggregations, joins, filters -> Table API / SQL
   ✅ Want automatic query optimization (Calcite) -> Table API / SQL
   ✅ SQL-savvy team, want fast iteration -> SQL

   ❌ Need custom low-level state/timers -> DataStream API (ProcessFunction)
   ❌ Need very fine-grained control over operator chaining -> DataStream API

BEST PRACTICES:

1. Prefer Table API/SQL for standard ETL/aggregation pipelines
2. Use `datagen` connector tables for local testing without external systems
3. Register tables as temporary views for reuse across multiple SQL queries
4. Use `EXPLAIN` (t_env.explain_sql(...)) to inspect the optimized plan
5. Fall back to DataStream + ProcessFunction only when Table API can't
   express the required custom logic
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - TABLE API & SQL BASICS")
    print("#" * 60)

    basic_table_operations()
    group_by_aggregation_demo()
    sql_queries_demo()
    ddl_table_demo()

    print("\n" + "#" * 60)
    print("# ALL TABLE API BASICS EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 03_windowing_and_watermarks.py to learn about event time & windows")
