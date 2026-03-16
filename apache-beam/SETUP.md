# Apache Beam Setup Guide

## Quick Start

### 1. Install Python
Ensure you have Python 3.7 or higher installed:
```bash
python --version
# or
python3 --version
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv beam-env

# Activate virtual environment
# On macOS/Linux:
source beam-env/bin/activate

# On Windows:
beam-env\Scripts\activate
```

### 3. Install Apache Beam
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install manually
pip install apache-beam==2.53.0
```

### 4. Verify Installation
```bash
python -c "import apache_beam; print(apache_beam.__version__)"
```

## Running Examples

### Run Individual Examples
```bash
# Example 1: Word Count
python 01_word_count.py

# Example 2: Filter and Transform
python 02_filter_transform.py

# Example 3: Aggregation
python 03_aggregation.py

# Example 4: Streaming and Windowing
python 04_streaming_windowing.py

# Example 5: ParDo
python 05_pardo_custom.py

# Example 6: Side Inputs
python 06_side_inputs.py

# Example 7: Composite Transforms
python 07_composite_transforms.py
```

### View Results
```bash
# Results are written to the output/ directory
ls -la output/

# View a specific output file
cat output/word_count-00000-of-00001
```

## Running on Different Runners

### DirectRunner (Local - Default)
```python
# No special configuration needed
with beam.Pipeline() as pipeline:
    # Your pipeline code
    pass
```

### DataflowRunner (Google Cloud)
```bash
# Install GCP dependencies
pip install apache-beam[gcp]

# Run on Dataflow
python your_pipeline.py \
    --runner DataflowRunner \
    --project YOUR_PROJECT_ID \
    --region us-central1 \
    --temp_location gs://YOUR_BUCKET/temp/
```

### FlinkRunner (Apache Flink)
```bash
# Install Flink dependencies
pip install apache-beam[flink]

# Run on Flink
python your_pipeline.py \
    --runner FlinkRunner \
    --flink_master localhost:8081
```

### SparkRunner (Apache Spark)
```bash
# Install Spark dependencies
pip install apache-beam[spark]

# Run on Spark
python your_pipeline.py \
    --runner SparkRunner \
    --spark_master_url spark://localhost:7077
```

## Project Structure

```
apache-beam/
├── README.md                      # Main documentation
├── SETUP.md                       # This file
├── requirements.txt               # Python dependencies
├── 01_word_count.py              # Example 1: Basic word count
├── 02_filter_transform.py        # Example 2: Filtering and transforming
├── 03_aggregation.py             # Example 3: Aggregations
├── 04_streaming_windowing.py     # Example 4: Streaming and windows
├── 05_pardo_custom.py            # Example 5: Custom ParDo
├── 06_side_inputs.py             # Example 6: Side inputs
├── 07_composite_transforms.py    # Example 7: Composite transforms
└── output/                        # Output directory (created automatically)
```

## Troubleshooting

### Issue: "No module named 'apache_beam'"
**Solution:**
```bash
pip install apache-beam
```

### Issue: "Permission denied" when writing output
**Solution:**
```bash
# Create output directory with proper permissions
mkdir -p output
chmod 755 output
```

### Issue: Pipeline runs but no output
**Solution:**
- Ensure you're using context manager (`with beam.Pipeline()`) or calling `result.wait_until_finish()`
- Check the output directory exists
- Verify file paths are correct

### Issue: Memory errors with large datasets
**Solution:**
- Use streaming mode
- Increase worker resources
- Process data in smaller batches
- Use more efficient transforms (CombinePerKey instead of GroupByKey)

### Issue: Slow performance
**Solution:**
- Check for hot keys (uneven data distribution)
- Reduce shuffles (GroupByKey operations)
- Use Combiners for aggregations
- Parallelize I/O operations

## Development Workflow

### 1. Start with DirectRunner
Always test locally first:
```python
with beam.Pipeline() as pipeline:
    # Your pipeline
    pass
```

### 2. Add Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 3. Test with Small Data
Create small test datasets before running on production data.

### 4. Monitor Pipeline
```python
result = pipeline.run()
result.wait_until_finish()
print(result.metrics())
```

### 5. Deploy to Production
Once tested locally, deploy to distributed runner (Dataflow, Flink, Spark).

## Best Practices

### 1. Use Virtual Environments
Always use a virtual environment to avoid dependency conflicts.

### 2. Version Control
- Commit your pipeline code
- Track requirements.txt
- Document pipeline configurations

### 3. Testing
```python
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

def test_my_transform():
    with TestPipeline() as p:
        output = (
            p
            | beam.Create([1, 2, 3])
            | beam.Map(lambda x: x * 2)
        )
        assert_that(output, equal_to([2, 4, 6]))
```

### 4. Error Handling
```python
class SafeDoFn(beam.DoFn):
    def process(self, element):
        try:
            yield process_element(element)
        except Exception as e:
            logging.error(f"Error: {e}")
```

### 5. Monitoring
- Use Beam metrics
- Add custom counters
- Log important events

## Additional Resources

- **Official Docs**: https://beam.apache.org/documentation/
- **Python SDK**: https://beam.apache.org/documentation/sdks/python/
- **Beam Playground**: https://play.beam.apache.org/
- **GitHub**: https://github.com/apache/beam
- **Stack Overflow**: Tag `apache-beam`

## Next Steps

1. ✅ Complete setup
2. ✅ Run all examples (01-07)
3. ✅ Modify examples to understand behavior
4. ✅ Build your own pipeline
5. ✅ Deploy to production runner

---

**Happy Beaming! 🚀**
