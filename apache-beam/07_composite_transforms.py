"""
Example 7: Composite Transforms

This example demonstrates:
- Creating reusable composite transforms
- Combining multiple transforms into one
- Building modular pipeline components
- PTransform class
- Best practices for code reusability

WHAT IT DOES:
Shows how to create custom composite transforms for reusable pipeline logic.

HOW TO RUN:
python 07_composite_transforms.py

EXPECTED OUTPUT:
Files showing results from composite transforms.
"""

import apache_beam as beam
import re


class CountWords(beam.PTransform):
    """
    Composite transform that counts words in text.
    
    Combines multiple transforms into a single reusable component.
    """
    
    def expand(self, pcoll):
        """
        Define the composite transform logic.
        
        Args:
            pcoll: Input PCollection
            
        Returns:
            Output PCollection with word counts
        """
        return (
            pcoll
            | 'SplitWords' >> beam.FlatMap(lambda line: re.findall(r'\w+', line.lower()))
            | 'PairWithOne' >> beam.Map(lambda word: (word, 1))
            | 'GroupAndSum' >> beam.CombinePerKey(sum)
        )


class FilterAndFormat(beam.PTransform):
    """
    Composite transform with parameters.
    
    Filters elements and formats output.
    """
    
    def __init__(self, min_value, format_string="{key}: {value}"):
        """
        Initialize with parameters.
        
        Args:
            min_value: Minimum value to keep
            format_string: Format for output
        """
        super().__init__()
        self.min_value = min_value
        self.format_string = format_string
    
    def expand(self, pcoll):
        """
        Apply filter and format transforms.
        """
        return (
            pcoll
            | 'FilterByValue' >> beam.Filter(lambda kv: kv[1] >= self.min_value)
            | 'FormatOutput' >> beam.Map(
                lambda kv: self.format_string.format(key=kv[0], value=kv[1])
            )
        )


class ExtractAndEnrich(beam.PTransform):
    """
    Composite transform with side inputs.
    
    Extracts data and enriches with lookup table.
    """
    
    def __init__(self, lookup_pcoll):
        """
        Initialize with side input.
        
        Args:
            lookup_pcoll: PCollection to use as lookup table
        """
        super().__init__()
        self.lookup_pcoll = lookup_pcoll
    
    def expand(self, pcoll):
        """
        Extract keys and enrich with lookup data.
        """
        return (
            pcoll
            | 'ExtractKey' >> beam.Map(lambda x: (x[0], x))
            | 'EnrichData' >> beam.Map(
                lambda kv, lookup: {
                    'id': kv[0],
                    'data': kv[1],
                    'enriched': lookup.get(kv[0], 'N/A')
                },
                lookup=beam.pvalue.AsDict(self.lookup_pcoll)
            )
        )


class CalculateStatistics(beam.PTransform):
    """
    Composite transform that calculates multiple statistics.
    
    Returns multiple PCollections (branching).
    """
    
    def expand(self, pcoll):
        """
        Calculate count, sum, and average.
        
        Returns a dictionary of PCollections.
        """
        # Count
        count = (
            pcoll
            | 'Count' >> beam.combiners.Count.Globally()
        )
        
        # Sum
        total = (
            pcoll
            | 'Sum' >> beam.CombineGlobally(sum)
        )
        
        # Average
        average = (
            pcoll
            | 'Average' >> beam.CombineGlobally(beam.combiners.MeanCombineFn())
        )
        
        return {
            'count': count,
            'sum': total,
            'average': average
        }


class TopKPerKey(beam.PTransform):
    """
    Composite transform to get top K elements per key.
    """
    
    def __init__(self, k=3):
        """
        Initialize with K value.
        
        Args:
            k: Number of top elements to keep
        """
        super().__init__()
        self.k = k
    
    def expand(self, pcoll):
        """
        Get top K elements per key.
        
        Input: PCollection of (key, value) tuples
        Output: PCollection of (key, [top_k_values]) tuples
        """
        return (
            pcoll
            | 'GroupByKey' >> beam.GroupByKey()
            | 'GetTopK' >> beam.Map(
                lambda kv: (kv[0], sorted(kv[1], reverse=True)[:self.k])
            )
        )


def run_basic_composite():
    """
    Basic composite transform example.
    """
    text_data = [
        "Apache Beam is powerful",
        "Beam makes data processing easy",
        "Apache Beam supports batch and streaming"
    ]
    
    with beam.Pipeline() as pipeline:
        word_counts = (
            pipeline
            | 'CreateText' >> beam.Create(text_data)
            # Use custom composite transform
            | 'CountWords' >> CountWords()
            | 'FormatCounts' >> beam.Map(lambda wc: f'{wc[0]}: {wc[1]}')
            | 'WriteCounts' >> beam.io.WriteToText('output/composite_word_counts')
        )
    
    print("✅ Basic composite transform completed!")


def run_parameterized_composite():
    """
    Composite transform with parameters.
    """
    data = [
        ('apple', 5),
        ('banana', 12),
        ('cherry', 3),
        ('date', 8),
        ('elderberry', 15),
    ]
    
    with beam.Pipeline() as pipeline:
        # Filter and format with min_value=10
        filtered = (
            pipeline
            | 'CreateData' >> beam.Create(data)
            | 'FilterAndFormat' >> FilterAndFormat(
                min_value=10,
                format_string="{key} has {value} items"
            )
            | 'WriteFiltered' >> beam.io.WriteToText('output/filtered_formatted')
        )
    
    print("✅ Parameterized composite transform completed!")


def run_composite_with_side_input():
    """
    Composite transform with side inputs.
    """
    # Main data
    main_data = [
        ('A', 100, 'data1'),
        ('B', 200, 'data2'),
        ('C', 300, 'data3'),
    ]
    
    # Lookup data
    lookup_data = [
        ('A', 'Category Alpha'),
        ('B', 'Category Beta'),
        ('C', 'Category Gamma'),
    ]
    
    with beam.Pipeline() as pipeline:
        main_pcoll = pipeline | 'CreateMain' >> beam.Create(main_data)
        lookup_pcoll = pipeline | 'CreateLookup' >> beam.Create(lookup_data)
        
        enriched = (
            main_pcoll
            | 'ExtractAndEnrich' >> ExtractAndEnrich(lookup_pcoll)
            | 'FormatEnriched' >> beam.Map(
                lambda x: f"{x['id']}: {x['data']} -> {x['enriched']}"
            )
            | 'WriteEnriched' >> beam.io.WriteToText('output/composite_enriched')
        )
    
    print("✅ Composite with side input completed!")


def run_statistics_composite():
    """
    Composite transform with multiple outputs.
    """
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    with beam.Pipeline() as pipeline:
        data = pipeline | 'CreateNumbers' >> beam.Create(numbers)
        
        # Calculate statistics (returns dict of PCollections)
        stats = data | 'CalculateStats' >> CalculateStatistics()
        
        # Write each statistic to separate file
        (
            stats['count']
            | 'FormatCount' >> beam.Map(lambda x: f'Count: {x}')
            | 'WriteCount' >> beam.io.WriteToText('output/stats_count')
        )
        
        (
            stats['sum']
            | 'FormatSum' >> beam.Map(lambda x: f'Sum: {x}')
            | 'WriteSum' >> beam.io.WriteToText('output/stats_sum')
        )
        
        (
            stats['average']
            | 'FormatAverage' >> beam.Map(lambda x: f'Average: {x:.2f}')
            | 'WriteAverage' >> beam.io.WriteToText('output/stats_average')
        )
    
    print("✅ Statistics composite transform completed!")


def run_topk_composite():
    """
    Top K per key composite transform.
    """
    # Sales data: (category, amount)
    sales = [
        ('Electronics', 1200),
        ('Electronics', 800),
        ('Electronics', 1500),
        ('Electronics', 600),
        ('Furniture', 300),
        ('Furniture', 500),
        ('Furniture', 200),
        ('Furniture', 450),
        ('Clothing', 100),
        ('Clothing', 150),
        ('Clothing', 80),
    ]
    
    with beam.Pipeline() as pipeline:
        top_sales = (
            pipeline
            | 'CreateSales' >> beam.Create(sales)
            # Get top 3 sales per category
            | 'GetTop3' >> TopKPerKey(k=3)
            | 'FormatTop3' >> beam.Map(
                lambda kv: f"{kv[0]}: Top 3 = {kv[1]}"
            )
            | 'WriteTop3' >> beam.io.WriteToText('output/top3_per_category')
        )
    
    print("✅ Top K composite transform completed!")


def run_nested_composites():
    """
    Nesting composite transforms.
    """
    
    class ProcessAndAnalyze(beam.PTransform):
        """
        Nested composite that uses other composites.
        """
        
        def expand(self, pcoll):
            # First, count words
            word_counts = pcoll | 'CountWords' >> CountWords()
            
            # Then, filter and format
            filtered = (
                word_counts
                | 'FilterAndFormat' >> FilterAndFormat(
                    min_value=2,
                    format_string="Word '{key}' appears {value} times"
                )
            )
            
            return filtered
    
    text_data = [
        "beam beam beam",
        "apache apache",
        "data processing with beam",
        "beam is great"
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateText' >> beam.Create(text_data)
            # Use nested composite
            | 'ProcessAndAnalyze' >> ProcessAndAnalyze()
            | 'WriteNested' >> beam.io.WriteToText('output/nested_composite')
        )
    
    print("✅ Nested composite transforms completed!")


# DETAILED EXPLANATION:
"""
COMPOSITE TRANSFORMS:

1. What are Composite Transforms?
   - Combine multiple transforms into a single reusable component
   - Encapsulate complex logic
   - Make pipelines more readable and maintainable
   - Can be parameterized and reused across pipelines

2. Creating a Composite Transform:
   
   class MyTransform(beam.PTransform):
       def expand(self, pcoll):
           return (
               pcoll
               | 'Step1' >> beam.Map(...)
               | 'Step2' >> beam.Filter(...)
           )

3. Key Components:
   
   a) Class Definition:
      - Inherit from beam.PTransform
      - Override expand() method
   
   b) expand() method:
      - Takes input PCollection(s)
      - Returns output PCollection(s)
      - Contains the transform logic
   
   c) __init__() method (optional):
      - For parameterized transforms
      - Store configuration

4. Benefits:
   ✅ Code reusability
   ✅ Better organization
   ✅ Easier testing
   ✅ Cleaner pipeline code
   ✅ Encapsulation of complex logic

5. Types of Composite Transforms:
   
   a) Simple Composite:
      - Chains multiple transforms
      - Single input, single output
   
   b) Parameterized Composite:
      - Accepts parameters in __init__
      - Configurable behavior
   
   c) Multiple Outputs:
      - Returns dict of PCollections
      - Branching logic
   
   d) With Side Inputs:
      - Uses additional PCollections
      - Enrichment patterns

6. Best Practices:
   
   a) Naming:
      - Use descriptive names
      - Name internal transforms clearly
      - Example: 'ExtractWords', 'CountPerKey'
   
   b) Modularity:
      - Keep composites focused on one task
      - Compose smaller transforms into larger ones
   
   c) Parameters:
      - Make transforms configurable
      - Use sensible defaults
   
   d) Documentation:
      - Document input/output types
      - Explain parameters
      - Provide usage examples
   
   e) Testing:
      - Test composite transforms independently
      - Use TestPipeline for unit tests

7. When to Use Composite Transforms:
   
   Use when:
   ✅ Logic is reused across pipelines
   ✅ Complex multi-step processing
   ✅ Want to encapsulate business logic
   ✅ Improve code readability
   
   Don't use when:
   ❌ Simple one-off transforms
   ❌ Over-engineering simple pipelines

8. Comparison:

   Without Composite:
   data | 'Step1' >> beam.Map(...)
        | 'Step2' >> beam.Filter(...)
        | 'Step3' >> beam.CombinePerKey(...)
   
   With Composite:
   data | 'ProcessData' >> MyCompositeTransform()

9. Advanced Patterns:
   
   a) Nested Composites:
      Composites can use other composites
   
   b) Dynamic Composites:
      Generate transforms based on configuration
   
   c) Template Composites:
      Generic composites with type parameters

10. Real-World Examples:
    
    - ReadAndParse: Read file + parse JSON
    - ValidateAndEnrich: Validate + enrich with lookup
    - AggregateAndFormat: Aggregate + format output
    - FilterTransformWrite: Complete ETL in one transform

EXAMPLE STRUCTURE:

class MyETL(beam.PTransform):
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def expand(self, pcoll):
        # Extract
        extracted = pcoll | 'Extract' >> beam.Map(...)
        
        # Transform
        transformed = extracted | 'Transform' >> beam.Filter(...)
        
        # Load
        loaded = transformed | 'Load' >> beam.Map(...)
        
        return loaded

# Usage
data | 'ETL' >> MyETL(config={'threshold': 100})
"""


if __name__ == '__main__':
    print("Running Composite Transforms Examples...")
    print("=" * 60)
    
    print("\n1. Basic Composite Transform")
    print("-" * 60)
    run_basic_composite()
    
    print("\n2. Parameterized Composite Transform")
    print("-" * 60)
    run_parameterized_composite()
    
    print("\n3. Composite with Side Input")
    print("-" * 60)
    run_composite_with_side_input()
    
    print("\n4. Statistics Composite (Multiple Outputs)")
    print("-" * 60)
    run_statistics_composite()
    
    print("\n5. Top K Composite")
    print("-" * 60)
    run_topk_composite()
    
    print("\n6. Nested Composites")
    print("-" * 60)
    run_nested_composites()
    
    print("\n" + "=" * 60)
    print("✅ All composite transform examples completed!")
    print("Check output/ directory for results.")
