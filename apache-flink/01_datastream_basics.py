"""
Example 1: DataStream API Basics

This example demonstrates:
- Creating a StreamExecutionEnvironment
- Creating DataStreams from collections
- Basic transformations (map, filter, flat_map)
- keyBy and reduce (stateful aggregation)
- Lazy execution model (nothing runs until env.execute())

WHAT IT DOES:
Introduces fundamental DataStream API operations and concepts.

HOW TO RUN:
python 01_datastream_basics.py

EXPECTED OUTPUT:
Console output showing DataStream operations and results.
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types


def create_execution_environment():
    """
    Create and configure the StreamExecutionEnvironment.
    This is the entry point for all Flink DataStream programs, analogous to
    Spark's SparkSession/SparkContext.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)
    return env


def basic_datastream_operations():
    """
    Basic DataStream creation and transformations.
    """
    print("\n" + "=" * 60)
    print("1. BASIC DATASTREAM OPERATIONS")
    print("=" * 60)

    env = create_execution_environment()

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ds = env.from_collection(numbers, type_info=Types.INT())

    # Transformation: map (multiply each number by 2)
    # NOTE: This is LAZY - not computed until env.execute() is called
    doubled = ds.map(lambda x: x * 2, output_type=Types.INT())

    doubled.print()

    env.execute("basic-datastream-operations")


def transformations_demo():
    """
    Demonstrate common DataStream transformations.
    """
    print("\n" + "=" * 60)
    print("2. DATASTREAM TRANSFORMATIONS")
    print("=" * 60)

    env = create_execution_environment()

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ds = env.from_collection(numbers, type_info=Types.INT())

    # map: 1-to-1 transformation
    squared = ds.map(lambda x: x ** 2, output_type=Types.INT())

    # filter: keep elements matching condition
    evens = squared.filter(lambda x: x % 2 == 0)

    # flat_map: 1-to-many transformation
    words = ["hello world", "apache flink is fast"]
    words_ds = env.from_collection(words, type_info=Types.STRING())
    all_words = words_ds.flat_map(
        lambda line: line.split(), output_type=Types.STRING()
    )

    evens.print()
    all_words.print()

    env.execute("transformations-demo")


def key_by_and_reduce_demo():
    """
    Working with keyed streams: key_by + reduce for aggregation.
    This is the streaming equivalent of Spark's reduceByKey.
    """
    print("\n" + "=" * 60)
    print("3. KEY_BY AND REDUCE (STATEFUL AGGREGATION)")
    print("=" * 60)

    env = create_execution_environment()

    pairs = [
        ("apple", 5),
        ("banana", 3),
        ("apple", 2),
        ("orange", 4),
        ("banana", 7),
        ("apple", 1),
    ]

    ds = env.from_collection(
        pairs, type_info=Types.TUPLE([Types.STRING(), Types.INT()])
    )

    # key_by partitions the stream logically by key -- required before
    # any keyed state or windowed operation.
    keyed = ds.key_by(lambda x: x[0])

    # reduce: incrementally aggregate values for each key.
    # Unlike Spark's reduceByKey (a batch operation), this runs continuously
    # and emits an updated running total every time a new element arrives
    # for a given key.
    totals = keyed.reduce(lambda a, b: (a[0], a[1] + b[1]))

    totals.print()

    env.execute("key-by-reduce-demo")


def word_count_example():
    """
    Classic word count example using the DataStream API.
    """
    print("\n" + "=" * 60)
    print("4. WORD COUNT EXAMPLE")
    print("=" * 60)

    env = create_execution_environment()

    text_data = [
        "Apache Flink is a streaming engine",
        "Flink processes unbounded and bounded streams",
        "Flink supports exactly-once state",
        "Apache Flink is powerful",
    ]

    ds = env.from_collection(text_data, type_info=Types.STRING())

    word_counts = (
        ds.flat_map(
            lambda line: line.lower().split(), output_type=Types.STRING()
        )
        .map(lambda word: (word, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()]))
        .key_by(lambda x: x[0])
        .reduce(lambda a, b: (a[0], a[1] + b[1]))
    )

    word_counts.print()

    env.execute("word-count-example")


def lazy_execution_demo():
    """
    Demonstrate Flink's lazy execution model.
    """
    print("\n" + "=" * 60)
    print("5. LAZY EXECUTION MODEL")
    print("=" * 60)

    env = create_execution_environment()

    print("Creating DataStream...")
    ds = env.from_collection([1, 2, 3, 4, 5], type_info=Types.INT())

    print("Applying transformations (NOT executed yet)...")
    ds2 = ds.map(lambda x: x * 2, output_type=Types.INT())
    ds3 = ds2.filter(lambda x: x > 5)

    print("Transformations build a JobGraph, but nothing runs yet!")
    print("Now calling env.execute()...")

    ds3.print()
    env.execute("lazy-execution-demo")

    print("Computation triggered by execute()!")


# DETAILED EXPLANATION:-
"""
DATASTREAM API CONCEPTS:

1. What is a DataStream?
   - Fundamental abstraction for a (possibly unbounded) stream of events
   - Immutable: transformations return new DataStreams
   - Distributed: split into partitions processed in parallel
   - Fault-tolerant: recoverable via checkpoints

2. Creating DataStreams:
   a) From collections (testing/learning only):
      env.from_collection([1, 2, 3])

   b) From files:
      env.read_text_file("file.txt")

   c) From connectors (Kafka, etc.):
      env.from_source(kafka_source, watermark_strategy, "source-name")

3. Transformations (Lazy):
   - Return new DataStreams
   - Not computed immediately - build a JobGraph (logical plan)

   Common transformations:
   - map(func): Apply function to each element (1-to-1)
   - flat_map(func): Map then flatten (1-to-many)
   - filter(func): Keep elements matching condition
   - key_by(func): Logically partition the stream by key
   - reduce(func): Incrementally aggregate a KeyedStream
   - union(other): Combine streams of the same type
   - connect(other): Combine streams of different types

4. Execution:
   - Nothing runs until env.execute("job-name") is called
   - Flink builds a JobGraph -> ExecutionGraph -> schedules tasks
   - Unlike Spark's per-action triggering, an entire Flink program is
     typically a single continuously-running job (or one bounded run)

5. key_by (Critical Concept):
   - Logically partitions a stream so all events with the same key are
     processed by the same parallel subtask
   - REQUIRED before using keyed state, windows, or reduce/aggregate
   - Analogous to a shuffle in Spark, but continuous rather than one-shot

6. reduce() on a KeyedStream vs Spark's reduceByKey:
   - Spark: batch operation, computes a final answer once
   - Flink: continuous operation, emits an updated result every time a
     new element arrives for that key (there is no "final" answer for an
     unbounded stream unless you window it)

7. DataStream vs Table API:
   - DataStream: Low-level, imperative, full control over state/timers
   - Table API/SQL: High-level, declarative, optimized by Calcite
   - Use DataStream when you need custom stateful logic (ProcessFunction),
     use Table API/SQL for standard aggregations/joins/filters

EXECUTION FLOW:

1. Create DataStream (source)
2. Apply transformations (lazy, builds JobGraph)
3. Call env.execute() (triggers submission and execution)
4. Flink translates JobGraph -> ExecutionGraph
5. JobManager schedules tasks onto TaskManager slots
6. Tasks execute continuously (for unbounded streams) or until data ends
   (for bounded streams)

BEST PRACTICES:

1. Prefer the Table API/SQL for standard aggregations when possible
2. Always key_by before using keyed state or windows
3. Keep transformation functions side-effect free where possible
4. Set an explicit, meaningful job name in execute() for observability
5. Monitor the Flink Web UI for job graphs and backpressure
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - DATASTREAM API BASICS")
    print("#" * 60)

    basic_datastream_operations()
    transformations_demo()
    key_by_and_reduce_demo()
    word_count_example()
    lazy_execution_demo()

    print("\n" + "#" * 60)
    print("# ALL DATASTREAM BASICS EXAMPLES COMPLETED!")
    print("#" * 60)
    print("\nNext: Run 02_table_api_basics.py to learn about the Table API & SQL")
