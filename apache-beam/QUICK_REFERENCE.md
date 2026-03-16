# Apache Beam Quick Reference Card

## 🚀 Quick Start
```bash
pip install apache-beam
python 01_word_count.py
```

## 📋 Core Concepts Cheat Sheet

### Pipeline
```python
import apache_beam as beam

# Method 1: Context manager (recommended)
with beam.Pipeline() as pipeline:
    # Your transforms

# Method 2: Explicit run
pipeline = beam.Pipeline()
# ... transforms ...
result = pipeline.run()
result.wait_until_finish()
```

### Basic Transforms

#### Map (1-to-1)
```python
| beam.Map(lambda x: x * 2)
| beam.Map(lambda x: x.upper())
| beam.Map(lambda x: (x, 1))  # Create key-value pairs
```

#### FlatMap (1-to-many)
```python
| beam.FlatMap(lambda x: x.split(','))
| beam.FlatMap(lambda line: line.split())
```

#### Filter
```python
| beam.Filter(lambda x: x > 10)
| beam.Filter(lambda x: x.startswith('A'))
```

#### GroupByKey
```python
# Input: [('a', 1), ('b', 2), ('a', 3)]
| beam.GroupByKey()
# Output: [('a', [1, 3]), ('b', [2])]
```

#### CombinePerKey
```python
# Sum
| beam.CombinePerKey(sum)

# Average
| beam.CombinePerKey(beam.combiners.MeanCombineFn())

# Count
| beam.CombinePerKey(beam.combiners.CountCombineFn())

# Max/Min
| beam.CombinePerKey(max)
| beam.CombinePerKey(min)
```

#### Count
```python
# Count all elements
| beam.combiners.Count.Globally()

# Count per element
| beam.combiners.Count.PerElement()

# Count per key
| beam.combiners.Count.PerKey()
```

### I/O Operations

#### Read
```python
# Text file
| beam.io.ReadFromText('input.txt')

# Multiple files
| beam.io.ReadFromText('data/*.txt')

# Create from list
| beam.Create([1, 2, 3, 4, 5])
```

#### Write
```python
# Text file
| beam.io.WriteToText('output/result')

# Note: Beam adds suffix like -00000-of-00001
```

### ParDo (Custom Processing)

#### Basic DoFn
```python
class MyDoFn(beam.DoFn):
    def process(self, element):
        # Process element
        yield processed_element

# Usage
| beam.ParDo(MyDoFn())
```

#### DoFn with Setup/Teardown
```python
class MyDoFn(beam.DoFn):
    def setup(self):
        # Initialize (once per worker)
        self.connection = create_connection()
    
    def process(self, element):
        # Process each element
        yield self.connection.query(element)
    
    def teardown(self):
        # Cleanup (once per worker)
        self.connection.close()
```

### Side Inputs

#### Singleton
```python
config = pipeline | 'CreateConfig' >> beam.Create([0.08])

data | beam.Map(
    lambda x, rate: x * rate,
    rate=beam.pvalue.AsSingleton(config)
)
```

#### List
```python
valid_items = pipeline | beam.Create(['A', 'B', 'C'])

data | beam.Filter(
    lambda x, valid: x in valid,
    valid=beam.pvalue.AsList(valid_items)
)
```

#### Dict (Lookup)
```python
lookup = pipeline | beam.Create([('A', 1), ('B', 2)])

data | beam.Map(
    lambda x, lookup_dict: (x, lookup_dict.get(x)),
    lookup_dict=beam.pvalue.AsDict(lookup)
)
```

### Windowing (Streaming)

#### Fixed Windows
```python
| beam.WindowInto(beam.window.FixedWindows(60))  # 60 seconds
```

#### Sliding Windows
```python
| beam.WindowInto(
    beam.window.SlidingWindows(
        size=60,    # Window size
        period=30   # Slide interval
    )
)
```

#### Session Windows
```python
| beam.WindowInto(
    beam.window.Sessions(30)  # 30-second gap
)
```

### Composite Transforms

```python
class MyTransform(beam.PTransform):
    def expand(self, pcoll):
        return (
            pcoll
            | 'Step1' >> beam.Map(...)
            | 'Step2' >> beam.Filter(...)
        )

# Usage
data | 'MyTransform' >> MyTransform()
```

## 🔥 Common Patterns

### Word Count
```python
(pipeline
 | beam.io.ReadFromText('input.txt')
 | beam.FlatMap(lambda line: line.split())
 | beam.Map(lambda word: (word, 1))
 | beam.CombinePerKey(sum)
 | beam.io.WriteToText('output/counts'))
```

### Filter and Transform
```python
(pipeline
 | beam.Create(data)
 | beam.Filter(lambda x: x['age'] >= 18)
 | beam.Map(lambda x: x['name'])
 | beam.io.WriteToText('output/adults'))
```

### Group and Aggregate
```python
(pipeline
 | beam.Create(sales_data)
 | beam.Map(lambda x: (x['category'], x['amount']))
 | beam.CombinePerKey(sum)
 | beam.io.WriteToText('output/totals'))
```

### Enrich with Lookup
```python
lookup = pipeline | beam.Create(lookup_data)

(main_data
 | beam.Map(
     lambda x, lookup_dict: enrich(x, lookup_dict),
     lookup_dict=beam.pvalue.AsDict(lookup)
 )
 | beam.io.WriteToText('output/enriched'))
```

### Top N
```python
(pipeline
 | beam.Create(data)
 | beam.combiners.Top.Of(10, key=lambda x: x[1])
 | beam.io.WriteToText('output/top10'))
```

## 🎯 When to Use What

| Need | Use |
|------|-----|
| 1-to-1 transform | `Map` |
| 1-to-many transform | `FlatMap` |
| Filter elements | `Filter` |
| Group by key | `GroupByKey` |
| Aggregate per key | `CombinePerKey` |
| Count elements | `Count.Globally()` or `Count.PerElement()` |
| Custom logic | `ParDo` with `DoFn` |
| Small reference data | Side Inputs |
| Reusable logic | Composite Transform |
| Time-based windows | `WindowInto` |

## ⚠️ Common Mistakes

### ❌ Don't
```python
# Don't use GroupByKey for aggregation
| beam.GroupByKey()
| beam.Map(lambda kv: (kv[0], sum(kv[1])))
```

### ✅ Do
```python
# Use CombinePerKey (more efficient)
| beam.CombinePerKey(sum)
```

---

### ❌ Don't
```python
# Don't forget to run pipeline
pipeline = beam.Pipeline()
# ... transforms ...
# Missing: result = pipeline.run()
```

### ✅ Do
```python
# Use context manager
with beam.Pipeline() as pipeline:
    # ... transforms ...
# Automatically runs and waits
```

---

### ❌ Don't
```python
# Don't use large datasets as side inputs
huge_lookup | beam.pvalue.AsDict()  # Memory issues!
```

### ✅ Do
```python
# Use CoGroupByKey for large datasets
| beam.CoGroupByKey()
```

## 🐛 Debugging Tips

### Add Logging
```python
| beam.Map(lambda x: logging.info(f"Processing: {x}") or x)
```

### Print Elements (Development Only)
```python
class PrintFn(beam.DoFn):
    def process(self, element):
        print(f"Element: {element}")
        yield element

| beam.ParDo(PrintFn())
```

### Count Elements
```python
| beam.combiners.Count.Globally()
| beam.Map(print)
```

## 📊 Performance Tips

1. **Use CombinePerKey instead of GroupByKey** - More efficient
2. **Avoid hot keys** - Distribute data evenly
3. **Use side inputs for small data** - Faster than joins
4. **Name your transforms** - Better monitoring
5. **Test locally first** - Use DirectRunner

## 🔗 Quick Links

- Examples: `01_word_count.py` through `07_composite_transforms.py`
- Setup: `SETUP.md`
- Full docs: `README.md`

## 💡 Remember

- **Pipeline**: Container for your data processing
- **PCollection**: Distributed dataset (immutable)
- **PTransform**: Operation on PCollections
- **Runner**: Execution engine (Direct, Dataflow, Flink, Spark)

---

**Pro Tip**: Start simple, test locally, then scale up! 🚀
