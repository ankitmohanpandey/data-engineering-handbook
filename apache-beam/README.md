# Apache Beam Complete Guide

## Table of Contents
1. [What is Apache Beam?](#what-is-apache-beam)
2. [Core Concepts](#core-concepts)
3. [Setup & Installation](#setup--installation)
4. [Basic Examples](#basic-examples)
5. [Advanced Concepts](#advanced-concepts)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## What is Apache Beam?

**Apache Beam** = **B**atch + Str**eam** (unified processing)

### Key Points
- **Unified Model**: Write once, run anywhere (Spark, Flink, Dataflow, etc.)
- **Language Support**: Python, Java, Go
- **Processing Types**: Batch (bounded data) and Streaming (unbounded data)
- **Open Source**: Apache Software Foundation project

### Why Use Apache Beam?
✅ Portable across different execution engines  
✅ Same code for batch and streaming  
✅ Rich set of built-in transformations  
✅ Handles late data and out-of-order events  
✅ Scalable from laptop to cluster  

---

## Core Concepts

### 1. Pipeline
The entire data processing workflow. Think of it as a container for all your data operations.

```python
import apache_beam as beam

# Create a pipeline
pipeline = beam.Pipeline()

# Or use context manager (recommended)
with beam.Pipeline() as p:
    # Your transformations here
    pass
```

### 2. PCollection (Parallel Collection)
A distributed, immutable dataset. Can be:
- **Bounded**: Fixed dataset (like a file) - Batch processing
- **Unbounded**: Continuous data stream (like Kafka) - Stream processing

```python
# PCollection is created by reading data or transforming other PCollections
lines = pipeline | 'Read' >> beam.io.ReadFromText('input.txt')
```

### 3. PTransform (Parallel Transform)
Operations that transform data. Takes PCollection(s) as input, produces PCollection(s) as output.

**Common Transforms:**
- `Map`: 1-to-1 transformation
- `FlatMap`: 1-to-many transformation
- `Filter`: Keep elements matching condition
- `GroupByKey`: Group by key (for key-value pairs)
- `CombinePerKey`: Aggregate values per key
- `Flatten`: Merge multiple PCollections
- `Partition`: Split into multiple PCollections

### 4. Runner
Executes your pipeline on a processing engine.

**Available Runners:**
- **DirectRunner**: Local execution (testing/development)
- **DataflowRunner**: Google Cloud Dataflow
- **FlinkRunner**: Apache Flink
- **SparkRunner**: Apache Spark
- **SamzaRunner**: Apache Samza

### 5. Windowing (for Streaming)
Divides unbounded data into finite chunks based on time.

**Window Types:**
- **Fixed Windows**: Non-overlapping time intervals (e.g., every 1 hour)
- **Sliding Windows**: Overlapping time intervals (e.g., 1 hour window, sliding every 30 min)
- **Session Windows**: Dynamic windows based on activity gaps
- **Global Window**: Default, entire dataset as one window

### 6. Triggers
Control when results are emitted from a window.

### 7. Watermarks
Track progress of event time in streaming pipelines.

---

## Setup & Installation

### Prerequisites
- Python 3.7+ (recommended 3.8 or higher)
- pip

### Installation
```bash
# Install Apache Beam
pip install apache-beam

# With Google Cloud Dataflow support
pip install apache-beam[gcp]

# With interactive features
pip install apache-beam[interactive]
```

### Verify Installation
```bash
python -c "import apache_beam; print(apache_beam.__version__)"
```

---

## Basic Examples

### Example 1: Word Count (Hello World of Beam)
See: `01_word_count.py`

### Example 2: Data Filtering and Transformation
See: `02_filter_transform.py`

### Example 3: Aggregation and GroupBy
See: `03_aggregation.py`

### Example 4: Streaming with Windowing
See: `04_streaming_windowing.py`

### Example 5: ParDo (Custom Processing)
See: `05_pardo_custom.py`

### Example 6: Side Inputs
See: `06_side_inputs.py`

### Example 7: Composite Transforms
See: `07_composite_transforms.py`

---

## Advanced Concepts

### ParDo (Parallel Do)
Most flexible transform. Allows custom processing logic.

```python
class MyDoFn(beam.DoFn):
    def process(self, element):
        # Your custom logic
        yield processed_element
```

### Side Inputs
Additional data available to all elements in a transform.

```python
def enrich_with_side_input(element, side_data):
    return element + side_data

enriched = main_data | beam.Map(enrich_with_side_input, 
                                side_data=beam.pvalue.AsSingleton(side_pcollection))
```

### Composite Transforms
Combine multiple transforms into reusable components.

```python
class MyCompositeTransform(beam.PTransform):
    def expand(self, pcoll):
        return (pcoll
                | 'Step1' >> beam.Map(lambda x: x * 2)
                | 'Step2' >> beam.Filter(lambda x: x > 10))
```

### State and Timers
Maintain state across elements (stateful processing).

### Schemas
Structured data with named fields (like dataframes).

---

## Real-World Use Cases

### 1. ETL Pipelines
Extract data from sources, transform, load to destinations.

### 2. Log Processing
Parse, filter, and aggregate application logs.

### 3. Real-time Analytics
Process streaming data for dashboards and alerts.

### 4. Data Validation
Check data quality and consistency.

### 5. Machine Learning Pipelines
Preprocess data for ML models.

### 6. Click Stream Analysis
Analyze user behavior on websites.

---

## Best Practices

### 1. Use Context Managers
```python
with beam.Pipeline() as pipeline:
    # Ensures proper cleanup
```

### 2. Name Your Transforms
```python
# Good
data | 'ParseJSON' >> beam.Map(json.loads)

# Bad
data | beam.Map(json.loads)
```

### 3. Use Type Hints
```python
def process_record(record: dict) -> str:
    return record['name']
```

### 4. Test Locally First
Always test with DirectRunner before deploying to production.

### 5. Handle Errors Gracefully
```python
class SafeDoFn(beam.DoFn):
    def process(self, element):
        try:
            yield process_element(element)
        except Exception as e:
            logging.error(f"Error processing {element}: {e}")
```

### 6. Use Combiners for Aggregations
More efficient than GroupByKey + Map.

### 7. Avoid Shuffles When Possible
GroupByKey and CoGroupByKey trigger shuffles (expensive).

### 8. Monitor Pipeline Metrics
Use Beam metrics for monitoring.

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'apache_beam'"
**Solution**: Install Apache Beam
```bash
pip install apache-beam
```

#### 2. Pipeline runs but produces no output
**Solution**: Check if pipeline is being executed
```python
# Use context manager or call run()
with beam.Pipeline() as p:
    # transforms
# OR
result = pipeline.run()
result.wait_until_finish()
```

#### 3. Memory errors with large datasets
**Solution**: 
- Use streaming mode
- Increase worker resources
- Optimize transforms

#### 4. Slow pipeline performance
**Solution**:
- Reduce shuffles
- Use Combiners instead of GroupByKey
- Parallelize I/O operations
- Check for hot keys

---

## Pipeline Execution Flow

```
Data Source
    ↓
Read Transform (creates PCollection)
    ↓
Transform 1 (Map/Filter/etc.)
    ↓
Transform 2
    ↓
Transform N
    ↓
Write Transform
    ↓
Data Sink
```

---

## Comparison with Other Frameworks

| Feature | Apache Beam | Apache Spark | Apache Flink |
|---------|-------------|--------------|--------------|
| Unified Batch/Stream | ✅ | Partial | ✅ |
| Portability | ✅ (multiple runners) | ❌ | ❌ |
| Language Support | Python, Java, Go | Python, Java, Scala, R | Java, Scala, Python |
| Ease of Use | High | Medium | Medium |
| Maturity | Medium | High | High |

---

## Quick Reference

### Pipeline Pattern
```python
import apache_beam as beam

with beam.Pipeline() as pipeline:
    (pipeline
     | 'Read' >> beam.io.ReadFromText('input.txt')
     | 'Transform' >> beam.Map(lambda x: x.upper())
     | 'Write' >> beam.io.WriteToText('output.txt'))
```

### Common Transforms Cheat Sheet
```python
# Map: 1-to-1
| beam.Map(lambda x: x * 2)

# FlatMap: 1-to-many
| beam.FlatMap(lambda x: x.split(','))

# Filter: Keep matching elements
| beam.Filter(lambda x: x > 10)

# GroupByKey: Group (key, value) pairs
| beam.GroupByKey()

# CombinePerKey: Aggregate per key
| beam.CombinePerKey(sum)

# Flatten: Merge PCollections
| beam.Flatten()

# Partition: Split into N PCollections
| beam.Partition(lambda x, n: x % n, 3)
```

---

## Resources

- **Official Documentation**: https://beam.apache.org/documentation/
- **Python SDK**: https://beam.apache.org/documentation/sdks/python/
- **Beam Playground**: https://play.beam.apache.org/
- **GitHub**: https://github.com/apache/beam
- **Stack Overflow**: Tag `apache-beam`

---

## Next Steps

1. Run the examples in order (01 through 07)
2. Modify examples to understand behavior
3. Build your own pipeline for a real use case
4. Deploy to a distributed runner (Dataflow, Flink, Spark)

---

**Remember**: Apache Beam is about writing portable data processing logic. The same code can run on your laptop or a massive cluster!
