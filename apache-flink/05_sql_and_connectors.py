"""
Example 5: Flink SQL, Connectors & Changelog/CDC-style Pipelines

This example demonstrates:
- Defining source/sink tables via SQL DDL and the 'datagen'/'print'/
  'filesystem' connectors (no external systems required)
- Windowed SQL aggregation using Table-Valued Functions (TVF windows)
- Changelog streams (INSERT/UPDATE_BEFORE/UPDATE_AFTER/DELETE) -- the
  foundation of CDC-style pipelines
- Writing query results to a sink table

WHAT IT DOES:
Builds small, runnable Flink SQL pipelines that don't require Kafka or any
other external system, so you can learn connector & SQL mechanics locally.
See 07_kafka_streaming_pipeline.py for a real Kafka-backed pipeline.

HOW TO RUN:
python 05_sql_and_connectors.py

EXPECTED OUTPUT:
Console output showing SQL query results and changelog rows.
"""

from pyflink.table import EnvironmentSettings, TableEnvironment


def create_table_environment():
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    return t_env


def datagen_source_demo():
    """
    The 'datagen' connector generates synthetic rows -- extremely useful
    for testing SQL pipelines without any external dependency.
    """
    print("\n" + "=" * 60)
    print("1. SOURCE CONNECTOR: DATAGEN")
    print("=" * 60)

    t_env = create_table_environment()

    t_env.execute_sql(
        """
        CREATE TABLE orders (
            order_id BIGINT,
            customer_id INT,
            amount DOUBLE,
            order_time AS PROCTIME()
        ) WITH (
            'connector' = 'datagen',
            'rows-per-second' = '5',
            'number-of-rows' = '20',
            'fields.customer_id.min' = '1',
            'fields.customer_id.max' = '5',
            'fields.amount.min' = '10.0',
            'fields.amount.max' = '500.0'
        )
        """
    )

    t_env.sql_query("SELECT * FROM orders").execute().print()


def print_sink_demo():
    """
    The 'print' connector is a convenient sink for debugging SQL pipelines
    (equivalent in spirit to calling .print() on a DataStream).
    """
    print("\n" + "=" * 60)
    print("2. SINK CONNECTOR: PRINT")
    print("=" * 60)

    t_env = create_table_environment()

    t_env.execute_sql(
        """
        CREATE TABLE orders (
            order_id BIGINT,
            customer_id INT,
            amount DOUBLE
        ) WITH (
            'connector' = 'datagen',
            'number-of-rows' = '10',
            'fields.customer_id.min' = '1',
            'fields.customer_id.max' = '3',
            'fields.amount.min' = '10.0',
            'fields.amount.max' = '500.0'
        )
        """
    )

    t_env.execute_sql(
        """
        CREATE TABLE orders_sink (
            customer_id INT,
            total_amount DOUBLE
        ) WITH (
            'connector' = 'print'
        )
        """
    )

    # INSERT INTO ... triggers an actual streaming job that writes to the sink.
    t_env.execute_sql(
        """
        INSERT INTO orders_sink
        SELECT customer_id, SUM(amount) AS total_amount
        FROM orders
        GROUP BY customer_id
        """
    ).wait()


def windowed_sql_aggregation_demo():
    """
    Table-Valued Function (TVF) windows in SQL -- the modern, recommended
    way to express tumbling/hopping/cumulative windows in Flink SQL.
    """
    print("\n" + "=" * 60)
    print("3. WINDOWED SQL AGGREGATION (TVF WINDOWS)")
    print("=" * 60)

    t_env = create_table_environment()

    t_env.execute_sql(
        """
        CREATE TABLE orders (
            order_id BIGINT,
            amount DOUBLE,
            order_time AS PROCTIME()
        ) WITH (
            'connector' = 'datagen',
            'rows-per-second' = '10',
            'number-of-rows' = '50',
            'fields.amount.min' = '10.0',
            'fields.amount.max' = '500.0'
        )
        """
    )

    result = t_env.sql_query(
        """
        SELECT
            window_start,
            window_end,
            COUNT(*) AS order_count,
            SUM(amount) AS total_amount
        FROM TABLE(
            TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '5' SECOND)
        )
        GROUP BY window_start, window_end
        """
    )

    result.execute().print()


def changelog_stream_demo():
    """
    Demonstrates that a GROUP BY query on an unbounded stream produces a
    changelog (updates), not just append-only inserts -- the foundation
    of CDC-style / materialized-view pipelines in Flink SQL.
    """
    print("\n" + "=" * 60)
    print("4. CHANGELOG STREAMS (CDC-STYLE SEMANTICS)")
    print("=" * 60)
    print(
        """
    A simple 'SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id'
    on an unbounded stream doesn't produce a single final answer -- it
    produces a continuously updating result. Internally this is a
    changelog stream:

        +I  (customer_id=1, total=50.0)     <- first order for customer 1
        -U  (customer_id=1, total=50.0)     <- retract old value
        +U  (customer_id=1, total=120.0)    <- new updated total

    This changelog model is exactly what Flink CDC connectors (Debezium-based)
    produce when capturing INSERT/UPDATE/DELETE events from a source
    database, which is why Flink SQL is a natural fit for CDC pipelines.
    """
    )

    t_env = create_table_environment()

    t_env.execute_sql(
        """
        CREATE TABLE orders (
            order_id BIGINT,
            customer_id INT,
            amount DOUBLE
        ) WITH (
            'connector' = 'datagen',
            'rows-per-second' = '5',
            'number-of-rows' = '15',
            'fields.customer_id.min' = '1',
            'fields.customer_id.max' = '3',
            'fields.amount.min' = '10.0',
            'fields.amount.max' = '500.0'
        )
        """
    )

    result = t_env.sql_query(
        """
        SELECT customer_id, SUM(amount) AS total_amount
        FROM orders
        GROUP BY customer_id
        """
    )

    # execute().print() on an updating result shows +I / -U / +U rows,
    # making the changelog nature explicit.
    result.execute().print()


# DETAILED EXPLANATION:-
"""
FLINK SQL, CONNECTORS & CDC CONCEPTS:

1. Connectors (via 'WITH' clause in CREATE TABLE):
   - 'datagen': generates synthetic test data -- no external system needed
   - 'print': prints rows to stdout -- convenient debugging sink
   - 'filesystem': read/write CSV/Parquet/JSON on local disk, S3, HDFS
   - 'kafka': read/write Kafka topics, supports exactly-once (see example 7)
   - 'jdbc': read/write relational databases
   - 'elasticsearch': sink for search/analytics dashboards
   - CDC connectors (flink-cdc-connectors, community project): capture
     row-level changes directly from MySQL/Postgres/MongoDB/etc.

2. TVF (Table-Valued Function) Windows:
   - Modern syntax: `TABLE(TUMBLE(TABLE t, DESCRIPTOR(time_col), INTERVAL ...))`
   - Supports TUMBLE, HOP (sliding), and CUMULATE window types
   - Preferred over the legacy GROUP BY window syntax
     (`GROUP BY TUMBLE(rowtime, INTERVAL '1' MINUTE)`) in modern Flink

3. Changelog Streams & Dynamic Tables:
   - Every SQL query on a streaming table produces a *dynamic table* --
     conceptually a table that changes over time
   - The changelog encodes each change as one of: INSERT (+I),
     UPDATE_BEFORE (-U), UPDATE_AFTER (+U), DELETE (-D)
   - Append-only queries (e.g., simple filters/projections) only ever
     produce +I; aggregations/GROUP BY typically produce +I/-U/+U as
     results are retracted and updated

4. Why This Matters for CDC:
   - Change Data Capture connectors emit exactly this kind of changelog
     (a row was inserted/updated/deleted in a source database)
   - Flink SQL can consume a CDC changelog stream and continue processing
     it as a dynamic table -- joins, aggregations, and filters all
     naturally propagate the changelog semantics downstream
   - This lets you build near-real-time materialized views / ETL from a
     production database into a warehouse or search index

5. INSERT INTO vs sql_query():
   - `sql_query()`: returns a Table object you can further transform or
     print for exploration
   - `execute_sql("INSERT INTO sink SELECT ...")`: submits an actual
     streaming job that continuously writes results to the sink table
   - `.wait()` on the result of execute_sql blocks until the (bounded) job
     finishes -- useful for these local, bounded demos

6. EXPLAIN:
   - `t_env.explain_sql("SELECT ...")` shows the optimized logical/physical
     plan Calcite produced -- invaluable for understanding performance

BEST PRACTICES:

1. Prototype pipelines locally with 'datagen'/'print' before wiring up
   real connectors (Kafka, JDBC, etc.) -- much faster iteration loop
2. Prefer TVF window syntax over legacy GROUP BY windowing syntax
3. Understand whether your query is append-only or produces a changelog --
   it determines which sinks are compatible (some sinks only accept
   append-only streams)
4. When building CDC pipelines, validate primary key / changelog mode
   configuration on both source and sink tables
5. Use `EXPLAIN` to inspect query plans when debugging unexpected
   performance or behavior
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - SQL, CONNECTORS & CDC-STYLE PIPELINES")
    print("#" * 60)

    datagen_source_demo()
    print_sink_demo()
    windowed_sql_aggregation_demo()
    changelog_stream_demo()

    print("\n" + "#" * 60)
    print("# ALL SQL & CONNECTOR EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 06_checkpointing_and_fault_tolerance.py")
