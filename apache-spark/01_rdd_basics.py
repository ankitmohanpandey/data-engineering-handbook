"""
Example 1: RDD Basics - Resilient Distributed Datasets

This example demonstrates:
- Creating RDDs from collections and files
- Basic transformations (map, filter, flatMap)
- Actions (collect, count, reduce)
- Understanding lazy evaluation
- Working with key-value pairs

WHAT IT DOES:
Introduces fundamental RDD operations and concepts.

HOW TO RUN:
python 01_rdd_basics.py

EXPECTED OUTPUT:
Console output showing RDD operations and results.
"""

from pyspark.sql import SparkSession


def create_spark_session():
    """
    Create and configure SparkSession.
    SparkSession is the entry point for Spark functionality.
    """
    spark = SparkSession.builder \
        .appName("RDD Basics") \
        .master("local[*]") \
        .getOrCreate()
    
    # Set log level to reduce verbosity
    spark.sparkContext.setLogLevel("ERROR")
    
    return spark


def basic_rdd_operations():
    """
    Basic RDD creation and operations.
    """
    print("\n" + "="*60)
    print("1. BASIC RDD OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    # Create RDD from a list
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rdd = sc.parallelize(numbers)
    
    print(f"Original data: {numbers}")
    print(f"Number of partitions: {rdd.getNumPartitions()}")
    
    # Transformation: map (multiply each number by 2)
    # NOTE: This is LAZY - not computed yet
    doubled = rdd.map(lambda x: x * 2)
    
    # Action: collect (triggers computation)
    # NOTE: This brings all data to driver - use carefully!
    result = doubled.collect()
    print(f"Doubled: {result}")
    
    # Action: count
    count = rdd.count()
    print(f"Count: {count}")
    
    # Action: first
    first_element = rdd.first()
    print(f"First element: {first_element}")
    
    # Action: take (get first N elements)
    first_three = rdd.take(3)
    print(f"First 3 elements: {first_three}")
    
    spark.stop()


def transformations_demo():
    """
    Demonstrate common RDD transformations.
    """
    print("\n" + "="*60)
    print("2. RDD TRANSFORMATIONS")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rdd = sc.parallelize(numbers)
    
    # map: 1-to-1 transformation
    squared = rdd.map(lambda x: x ** 2)
    print(f"Squared: {squared.collect()}")
    
    # filter: keep elements matching condition
    evens = rdd.filter(lambda x: x % 2 == 0)
    print(f"Even numbers: {evens.collect()}")
    
    # flatMap: 1-to-many transformation
    words = ["hello world", "apache spark"]
    words_rdd = sc.parallelize(words)
    all_words = words_rdd.flatMap(lambda line: line.split())
    print(f"FlatMap result: {all_words.collect()}")
    
    # distinct: remove duplicates
    duplicates = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
    dup_rdd = sc.parallelize(duplicates)
    unique = dup_rdd.distinct()
    print(f"Distinct: {unique.collect()}")
    
    # union: combine two RDDs
    rdd1 = sc.parallelize([1, 2, 3])
    rdd2 = sc.parallelize([4, 5, 6])
    combined = rdd1.union(rdd2)
    print(f"Union: {combined.collect()}")
    
    # intersection: common elements
    rdd3 = sc.parallelize([1, 2, 3, 4, 5])
    rdd4 = sc.parallelize([4, 5, 6, 7, 8])
    common = rdd3.intersection(rdd4)
    print(f"Intersection: {common.collect()}")
    
    spark.stop()


def key_value_operations():
    """
    Working with key-value pair RDDs.
    """
    print("\n" + "="*60)
    print("3. KEY-VALUE PAIR OPERATIONS")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    # Create key-value pairs: (key, value)
    pairs = [
        ("apple", 5),
        ("banana", 3),
        ("apple", 2),
        ("orange", 4),
        ("banana", 7),
        ("apple", 1)
    ]
    pair_rdd = sc.parallelize(pairs)
    
    print(f"Original pairs: {pairs}")
    
    # reduceByKey: aggregate values for each key
    totals = pair_rdd.reduceByKey(lambda a, b: a + b)
    print(f"Totals by key: {totals.collect()}")
    
    # groupByKey: group all values for each key
    # NOTE: Less efficient than reduceByKey for aggregations
    grouped = pair_rdd.groupByKey()
    grouped_result = grouped.mapValues(list).collect()
    print(f"Grouped by key: {grouped_result}")
    
    # mapValues: transform only values (keys unchanged)
    doubled_values = pair_rdd.mapValues(lambda x: x * 2)
    print(f"Doubled values: {doubled_values.collect()}")
    
    # keys() and values()
    keys = pair_rdd.keys().distinct().collect()
    print(f"Unique keys: {keys}")
    
    # countByKey: count values per key
    counts = pair_rdd.countByKey()
    print(f"Count by key: {dict(counts)}")
    
    # sortByKey: sort by keys
    sorted_pairs = totals.sortByKey()
    print(f"Sorted by key: {sorted_pairs.collect()}")
    
    spark.stop()


def actions_demo():
    """
    Demonstrate common RDD actions.
    """
    print("\n" + "="*60)
    print("4. RDD ACTIONS")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rdd = sc.parallelize(numbers)
    
    # collect: return all elements to driver
    all_data = rdd.collect()
    print(f"collect(): {all_data}")
    
    # count: number of elements
    count = rdd.count()
    print(f"count(): {count}")
    
    # first: first element
    first = rdd.first()
    print(f"first(): {first}")
    
    # take: first N elements
    first_five = rdd.take(5)
    print(f"take(5): {first_five}")
    
    # top: top N elements
    top_three = rdd.top(3)
    print(f"top(3): {top_three}")
    
    # reduce: aggregate all elements
    sum_all = rdd.reduce(lambda a, b: a + b)
    print(f"reduce (sum): {sum_all}")
    
    # fold: like reduce but with initial value
    fold_result = rdd.fold(0, lambda a, b: a + b)
    print(f"fold (sum with 0): {fold_result}")
    
    # foreach: apply function to each element (no return)
    print("foreach (print each):")
    rdd.foreach(lambda x: print(f"  Element: {x}"))
    
    # countByValue: count occurrences of each value
    values = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
    value_rdd = sc.parallelize(values)
    value_counts = value_rdd.countByValue()
    print(f"countByValue(): {dict(value_counts)}")
    
    spark.stop()


def word_count_example():
    """
    Classic word count example using RDDs.
    """
    print("\n" + "="*60)
    print("5. WORD COUNT EXAMPLE")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    # Sample text data
    text_data = [
        "Apache Spark is fast",
        "Spark is a unified analytics engine",
        "Spark supports batch and streaming",
        "Apache Spark is powerful"
    ]
    
    # Create RDD
    text_rdd = sc.parallelize(text_data)
    
    # Word count pipeline
    word_counts = (
        text_rdd
        .flatMap(lambda line: line.lower().split())  # Split into words
        .map(lambda word: (word, 1))                  # Create (word, 1) pairs
        .reduceByKey(lambda a, b: a + b)              # Sum counts per word
        .sortBy(lambda x: x[1], ascending=False)      # Sort by count
    )
    
    print("Word counts (sorted by frequency):")
    for word, count in word_counts.collect():
        print(f"  {word}: {count}")
    
    spark.stop()


def lazy_evaluation_demo():
    """
    Demonstrate lazy evaluation concept.
    """
    print("\n" + "="*60)
    print("6. LAZY EVALUATION")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("Creating RDD...")
    rdd = sc.parallelize([1, 2, 3, 4, 5])
    
    print("Applying transformations (NOT executed yet)...")
    rdd2 = rdd.map(lambda x: x * 2)
    rdd3 = rdd2.filter(lambda x: x > 5)
    
    print("Transformations defined but not computed!")
    print("Now calling action (collect)...")
    
    result = rdd3.collect()
    print(f"Result: {result}")
    print("Computation triggered by action!")
    
    spark.stop()


def persistence_demo():
    """
    Demonstrate caching/persistence.
    """
    print("\n" + "="*60)
    print("7. CACHING/PERSISTENCE")
    print("="*60)
    
    spark = create_spark_session()
    sc = spark.sparkContext
    
    # Create RDD with expensive computation
    rdd = sc.parallelize(range(1, 1000000))
    expensive_rdd = rdd.map(lambda x: x * x).filter(lambda x: x % 2 == 0)
    
    print("Without caching:")
    print("First action (count)...")
    count1 = expensive_rdd.count()
    print(f"Count: {count1}")
    
    print("Second action (sum)...")
    sum1 = expensive_rdd.reduce(lambda a, b: a + b)
    print(f"Sum: {sum1}")
    print("RDD recomputed for each action!")
    
    # Now with caching
    print("\nWith caching:")
    expensive_rdd.cache()  # or .persist()
    
    print("First action (count) - computes and caches...")
    count2 = expensive_rdd.count()
    print(f"Count: {count2}")
    
    print("Second action (sum) - uses cached data...")
    sum2 = expensive_rdd.reduce(lambda a, b: a + b)
    print(f"Sum: {sum2}")
    print("RDD computed once, cached, then reused!")
    
    # Unpersist when done
    expensive_rdd.unpersist()
    
    spark.stop()


# DETAILED EXPLANATION:
"""
RDD (RESILIENT DISTRIBUTED DATASET) CONCEPTS:

1. What is an RDD?
   - Fundamental data structure in Spark
   - Distributed collection of objects
   - Immutable (cannot be changed)
   - Fault-tolerant (can recover from failures)
   - Partitioned across cluster nodes

2. Creating RDDs:
   a) From collections:
      sc.parallelize([1, 2, 3, 4, 5])
   
   b) From files:
      sc.textFile("file.txt")
   
   c) From other RDDs:
      rdd.map(lambda x: x * 2)

3. Transformations (Lazy):
   - Return new RDD
   - Not computed immediately
   - Build execution plan (DAG)
   
   Common transformations:
   - map(func): Apply function to each element
   - filter(func): Keep elements matching condition
   - flatMap(func): Map then flatten (1-to-many)
   - distinct(): Remove duplicates
   - union(other): Combine two RDDs
   - intersection(other): Common elements
   - reduceByKey(func): Aggregate by key
   - groupByKey(): Group values by key
   - sortByKey(): Sort by key

4. Actions (Eager):
   - Trigger computation
   - Return results to driver or write to storage
   
   Common actions:
   - collect(): Return all elements to driver
   - count(): Count elements
   - first(): First element
   - take(n): First n elements
   - reduce(func): Aggregate all elements
   - foreach(func): Apply function to each element
   - saveAsTextFile(path): Write to file

5. Lazy Evaluation:
   - Transformations build execution plan
   - Nothing computed until action is called
   - Allows optimization (pipeline fusion, etc.)
   
   Example:
   rdd.map(...).filter(...).map(...)  # Not executed
   result = rdd.collect()              # Now executed

6. Key-Value Pairs:
   - RDD of (key, value) tuples
   - Special operations available
   - reduceByKey, groupByKey, join, etc.

7. Partitions:
   - RDD divided into partitions
   - Each partition processed in parallel
   - Number of partitions = degree of parallelism
   
   Control partitions:
   - repartition(n): Change number of partitions
   - coalesce(n): Reduce partitions (no shuffle)

8. Persistence:
   - Cache intermediate results
   - Avoid recomputation
   - Storage levels: MEMORY_ONLY, MEMORY_AND_DISK, etc.
   
   Usage:
   rdd.cache()        # Cache in memory
   rdd.persist()      # Persist with default level
   rdd.unpersist()    # Remove from cache

9. When to Use RDDs:
   ✅ Low-level control needed
   ✅ Unstructured data
   ✅ Custom partitioning
   
   ❌ Structured data (use DataFrames)
   ❌ SQL-like operations (use DataFrames)
   ❌ Need optimization (use DataFrames)

10. RDD vs DataFrame:
    RDD:
    - Low-level API
    - No schema
    - No optimization
    - Full control
    
    DataFrame:
    - High-level API
    - Schema with columns
    - Catalyst optimizer
    - Easier to use
    
    Recommendation: Use DataFrames unless you need RDD features

EXECUTION FLOW:

1. Create RDD
2. Apply transformations (lazy)
3. Call action (triggers computation)
4. Spark builds DAG (Directed Acyclic Graph)
5. Optimizer optimizes plan
6. Execute tasks on workers
7. Return results

BEST PRACTICES:

1. Avoid collect() on large datasets (OOM risk)
2. Use reduceByKey instead of groupByKey (more efficient)
3. Cache RDDs that are reused multiple times
4. Partition data appropriately
5. Use DataFrames for structured data
6. Monitor Spark UI for performance
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - RDD BASICS")
    print("#"*60)
    
    basic_rdd_operations()
    transformations_demo()
    key_value_operations()
    actions_demo()
    word_count_example()
    lazy_evaluation_demo()
    persistence_demo()
    
    print("\n" + "#"*60)
    print("# ✅ ALL RDD EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nNext: Run 02_dataframe_basics.py to learn about DataFrames")
