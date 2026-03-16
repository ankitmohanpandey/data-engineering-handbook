"""
Example 5: Spark Structured Streaming Basics

This example demonstrates:
- Creating streaming DataFrames
- Reading from streaming sources
- Basic streaming transformations
- Writing streaming output
- Windowing and watermarks

WHAT IT DOES:
Introduces Spark Structured Streaming for real-time data processing.

HOW TO RUN:
python 05_streaming_basics.py

NOTE: This example uses simulated streaming with rate source.
For production, use Kafka, Kinesis, or file sources.

EXPECTED OUTPUT:
Console output showing streaming data processing.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, avg, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import time


def create_spark_session():
    """Create SparkSession for streaming."""
    spark = SparkSession.builder \
        .appName("Spark Streaming") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def basic_streaming():
    """
    Basic streaming example using rate source.
    """
    print("\n" + "="*60)
    print("1. BASIC STREAMING")
    print("="*60)
    
    spark = create_spark_session()
    
    # Create streaming DataFrame from rate source
    # Generates rows with timestamp and value columns
    stream_df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 5) \
        .load()
    
    print("\nStreaming DataFrame schema:")
    stream_df.printSchema()
    
    # Simple transformation
    result = stream_df.select(
        col("timestamp"),
        col("value"),
        (col("value") * 2).alias("doubled")
    )
    
    # Write to console
    query = result.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .start()
    
    print("\n⚡ Streaming started... (will run for 10 seconds)")
    time.sleep(10)
    
    query.stop()
    print("✅ Streaming stopped")
    
    spark.stop()


def streaming_aggregation():
    """
    Streaming aggregations with windowing.
    """
    print("\n" + "="*60)
    print("2. STREAMING AGGREGATION")
    print("="*60)
    
    spark = create_spark_session()
    
    # Create streaming DataFrame
    stream_df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 10) \
        .load()
    
    # Add category column
    stream_with_category = stream_df.withColumn(
        "category",
        (col("value") % 3).cast("string")
    )
    
    # Aggregate by category
    aggregated = stream_with_category \
        .groupBy("category") \
        .agg(
            count("*").alias("count"),
            avg("value").alias("avg_value")
        )
    
    # Write to console with complete mode
    query = aggregated.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", False) \
        .start()
    
    print("\n⚡ Streaming aggregation started... (will run for 10 seconds)")
    time.sleep(10)
    
    query.stop()
    print("✅ Streaming stopped")
    
    spark.stop()


def windowed_aggregation():
    """
    Time-based windowing in streaming.
    """
    print("\n" + "="*60)
    print("3. WINDOWED AGGREGATION")
    print("="*60)
    
    spark = create_spark_session()
    
    # Create streaming DataFrame
    stream_df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 5) \
        .load()
    
    # Window aggregation (10-second windows)
    windowed = stream_df \
        .groupBy(window(col("timestamp"), "10 seconds")) \
        .agg(
            count("*").alias("count"),
            avg("value").alias("avg_value")
        )
    
    # Write to console
    query = windowed.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", False) \
        .start()
    
    print("\n⚡ Windowed streaming started... (will run for 15 seconds)")
    time.sleep(15)
    
    query.stop()
    print("✅ Streaming stopped")
    
    spark.stop()


def output_modes_demo():
    """
    Different output modes in streaming.
    """
    print("\n" + "="*60)
    print("4. OUTPUT MODES")
    print("="*60)
    
    spark = create_spark_session()
    
    stream_df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 3) \
        .load()
    
    print("\nOutput Modes:")
    print("1. APPEND: Only new rows (default)")
    print("2. COMPLETE: All rows in result table")
    print("3. UPDATE: Only updated rows")
    
    # Append mode (for non-aggregation queries)
    print("\n--- APPEND MODE ---")
    query_append = stream_df \
        .select("timestamp", "value") \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()
    
    time.sleep(5)
    query_append.stop()
    
    # Complete mode (for aggregations)
    print("\n--- COMPLETE MODE ---")
    aggregated = stream_df.groupBy().agg(count("*").alias("total"))
    query_complete = aggregated \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()
    
    time.sleep(5)
    query_complete.stop()
    
    print("✅ Output modes demo completed")
    
    spark.stop()


def streaming_to_memory():
    """
    Write streaming data to memory table for querying.
    """
    print("\n" + "="*60)
    print("5. STREAMING TO MEMORY TABLE")
    print("="*60)
    
    spark = create_spark_session()
    
    stream_df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 5) \
        .load()
    
    # Write to memory table
    query = stream_df \
        .groupBy() \
        .agg(count("*").alias("total_count")) \
        .writeStream \
        .outputMode("complete") \
        .format("memory") \
        .queryName("streaming_counts") \
        .start()
    
    print("\n⚡ Streaming to memory table...")
    
    # Query the memory table
    for i in range(3):
        time.sleep(3)
        result = spark.sql("SELECT * FROM streaming_counts")
        print(f"\nQuery {i+1}:")
        result.show()
    
    query.stop()
    print("✅ Streaming stopped")
    
    spark.stop()


# DETAILED EXPLANATION:
"""
SPARK STRUCTURED STREAMING CONCEPTS:

1. What is Structured Streaming?
   - Stream processing built on Spark SQL engine
   - Treats streaming as unbounded table
   - Same API as batch processing
   - Exactly-once semantics
   - Fault-tolerant and scalable

2. Core Concepts:
   
   a) Input Table:
      - Unbounded table (continuously growing)
      - New rows appended over time
   
   b) Query:
      - Operations on input table
      - Same as batch DataFrame operations
   
   c) Result Table:
      - Output of query
      - Updated incrementally
   
   d) Output:
      - What to write to external storage
      - Controlled by output mode

3. Creating Streaming DataFrame:
   
   # From rate source (testing)
   df = spark.readStream.format("rate").load()
   
   # From Kafka
   df = spark.readStream \
       .format("kafka") \
       .option("kafka.bootstrap.servers", "host:port") \
       .option("subscribe", "topic") \
       .load()
   
   # From files
   df = spark.readStream \
       .schema(schema) \
       .csv("path/to/directory")
   
   # From socket (testing only)
   df = spark.readStream \
       .format("socket") \
       .option("host", "localhost") \
       .option("port", 9999) \
       .load()

4. Transformations:
   - Same as batch DataFrames
   - select, filter, groupBy, join, etc.
   - Some operations not supported (sort, distinct on full data)
   
   stream_df.select("col1", "col2")
   stream_df.filter(col("value") > 10)
   stream_df.groupBy("category").count()

5. Output Modes:
   
   a) APPEND (default):
      - Only new rows added to result
      - For non-aggregation queries
      - Cannot use with aggregations without watermark
   
   b) COMPLETE:
      - Entire result table output
      - For aggregation queries
      - All rows re-written each trigger
   
   c) UPDATE:
      - Only updated rows output
      - For aggregation queries
      - More efficient than complete

6. Output Sinks:
   
   a) Console (testing):
      .writeStream.format("console")
   
   b) Memory (testing):
      .writeStream.format("memory").queryName("table")
   
   c) File:
      .writeStream.format("parquet").option("path", "output")
   
   d) Kafka:
      .writeStream.format("kafka")
   
   e) Foreach/ForeachBatch (custom):
      .writeStream.foreach(writer)

7. Windowing:
   - Group events by time windows
   - Tumbling windows: Fixed, non-overlapping
   - Sliding windows: Fixed, overlapping
   
   # 10-minute tumbling window
   df.groupBy(window(col("timestamp"), "10 minutes"))
   
   # 10-minute sliding window, 5-minute slide
   df.groupBy(window(col("timestamp"), "10 minutes", "5 minutes"))

8. Watermarks:
   - Handle late data
   - Define how late data can be
   - Allows state cleanup
   
   df.withWatermark("timestamp", "10 minutes") \
     .groupBy(window(col("timestamp"), "10 minutes")) \
     .count()

9. Triggers:
   - Control when to process data
   
   a) Default (micro-batch as soon as possible)
   b) Fixed interval:
      .trigger(processingTime="10 seconds")
   
   c) Once (single batch):
      .trigger(once=True)
   
   d) Continuous (experimental):
      .trigger(continuous="1 second")

10. Checkpointing:
    - Save progress for fault tolerance
    - Required for production
    
    query = df.writeStream \
        .option("checkpointLocation", "checkpoint/") \
        .start()

11. Query Management:
    
    # Start query
    query = df.writeStream.start()
    
    # Wait for termination
    query.awaitTermination()
    
    # Stop query
    query.stop()
    
    # Check status
    query.status
    query.isActive
    
    # Get active queries
    spark.streams.active

12. Streaming Joins:
    
    a) Stream-Static Join:
       stream_df.join(static_df, "key")
    
    b) Stream-Stream Join:
       stream1.join(stream2, "key")
       Requires watermarks for outer joins

13. Deduplication:
    
    # Drop duplicates in streaming
    df.dropDuplicates(["id"])
    
    # With watermark
    df.withWatermark("timestamp", "10 minutes") \
      .dropDuplicates(["id", "timestamp"])

14. Best Practices:
    
    ✅ Always set checkpointLocation in production
    ✅ Use watermarks for aggregations
    ✅ Monitor query progress
    ✅ Handle late data appropriately
    ✅ Use appropriate output mode
    ✅ Test with rate source first
    ✅ Use Parquet for file sink
    
    ❌ Don't use console/memory in production
    ❌ Don't use complete mode for large state
    ❌ Avoid operations requiring full data (sort, distinct)

15. Monitoring:
    
    # Query progress
    query.lastProgress
    query.recentProgress
    
    # Metrics
    query.status
    
    # Spark UI
    # http://localhost:4040

COMMON PATTERNS:

# Read from Kafka, aggregate, write to Parquet
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "host:port") \
    .option("subscribe", "topic") \
    .load()

parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

aggregated = parsed \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(window("timestamp", "5 minutes"), "category") \
    .agg(count("*").alias("count"))

query = aggregated.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "output") \
    .option("checkpointLocation", "checkpoint") \
    .start()

query.awaitTermination()

STREAMING VS BATCH:

Batch:
df = spark.read.csv("file.csv")
result = df.groupBy("col").count()
result.write.parquet("output")

Streaming:
df = spark.readStream.csv("directory")
result = df.groupBy("col").count()
query = result.writeStream.format("parquet").start()
query.awaitTermination()

Same operations, different execution model!
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - STRUCTURED STREAMING")
    print("#"*60)
    
    print("\nNote: These examples use simulated streaming.")
    print("For production, use Kafka, Kinesis, or file sources.")
    
    basic_streaming()
    streaming_aggregation()
    windowed_aggregation()
    output_modes_demo()
    streaming_to_memory()
    
    print("\n" + "#"*60)
    print("# ✅ ALL STREAMING EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nNext: Run 06_mllib_basics.py for machine learning")
