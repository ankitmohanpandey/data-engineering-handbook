"""
Example 5: ParDo and Custom Processing

This example demonstrates:
- ParDo (Parallel Do) - most flexible transform
- Custom DoFn classes
- Element-wise processing with custom logic
- Yielding multiple outputs
- Setup and teardown methods
- Error handling in DoFn

WHAT IT DOES:
Shows how to create custom processing logic using DoFn classes.

HOW TO RUN:
python 05_pardo_custom.py

EXPECTED OUTPUT:
Files showing results of custom processing logic.
"""

import apache_beam as beam
import re
import json


class ExtractWordsFn(beam.DoFn):
    """
    Custom DoFn to extract words from text.
    DoFn = "Do Function" - custom processing logic
    """
    
    def process(self, element):
        """
        Process method is called for each element.
        Use 'yield' to emit one or more outputs.
        """
        # Extract words from the line
        words = re.findall(r'\w+', element.lower())
        
        # Yield each word separately
        for word in words:
            if len(word) > 3:  # Only words longer than 3 characters
                yield word


class EnrichDataFn(beam.DoFn):
    """
    DoFn with setup and teardown methods.
    Useful for initializing resources (DB connections, etc.)
    """
    
    def setup(self):
        """
        Called once per worker before processing elements.
        Use for expensive initialization (DB connections, loading models, etc.)
        """
        print("Setting up worker...")
        # Simulate loading a lookup table
        self.lookup = {
            'PREMIUM': 1.2,
            'STANDARD': 1.0,
            'BASIC': 0.8
        }
    
    def process(self, element):
        """
        Process each element with access to initialized resources.
        """
        user_id, tier, amount = element
        multiplier = self.lookup.get(tier, 1.0)
        enriched_amount = amount * multiplier
        
        yield {
            'user_id': user_id,
            'tier': tier,
            'original_amount': amount,
            'enriched_amount': enriched_amount
        }
    
    def teardown(self):
        """
        Called once per worker after processing all elements.
        Use for cleanup (closing connections, etc.)
        """
        print("Tearing down worker...")


class ParseJsonFn(beam.DoFn):
    """
    DoFn with error handling.
    """
    
    def process(self, element):
        """
        Parse JSON with error handling.
        """
        try:
            data = json.loads(element)
            yield data
        except json.JSONDecodeError as e:
            # Log error and skip invalid records
            print(f"Error parsing JSON: {element[:50]}... - {e}")
            # Could also yield to a dead letter queue
            pass


class SplitByThresholdFn(beam.DoFn):
    """
    DoFn with multiple outputs (tagged outputs).
    """
    
    def process(self, element, threshold=100):
        """
        Split elements into 'high' and 'low' based on threshold.
        """
        value = element[1]  # Assuming (key, value) tuple
        
        if value >= threshold:
            # Tag output as 'high'
            yield beam.pvalue.TaggedOutput('high', element)
        else:
            # Tag output as 'low'
            yield beam.pvalue.TaggedOutput('low', element)


class FilterAndTransformFn(beam.DoFn):
    """
    DoFn that can filter (not yield anything) or transform.
    """
    
    def process(self, element):
        """
        Process only valid elements.
        """
        # Unpack element
        name, age, city = element
        
        # Filter: Skip if age < 18
        if age < 18:
            return  # Don't yield anything (filters out)
        
        # Transform: Create formatted output
        yield f"{name} ({age}) from {city}"


def run_basic_pardo():
    """
    Basic ParDo example with custom DoFn.
    """
    text_data = [
        "Apache Beam is a unified programming model",
        "It supports both batch and streaming data",
        "ParDo is the most flexible transform"
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateText' >> beam.Create(text_data)
            # Use ParDo with custom DoFn
            | 'ExtractWords' >> beam.ParDo(ExtractWordsFn())
            | 'CountWords' >> beam.combiners.Count.PerElement()
            | 'FormatOutput' >> beam.Map(lambda wc: f'{wc[0]}: {wc[1]}')
            | 'WriteWords' >> beam.io.WriteToText('output/pardo_words')
        )
    
    print("✅ Basic ParDo example completed!")


def run_with_setup_teardown():
    """
    ParDo with setup and teardown methods.
    """
    user_data = [
        ('user1', 'PREMIUM', 100),
        ('user2', 'STANDARD', 150),
        ('user3', 'BASIC', 200),
        ('user4', 'PREMIUM', 75),
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateUsers' >> beam.Create(user_data)
            | 'EnrichData' >> beam.ParDo(EnrichDataFn())
            | 'FormatEnriched' >> beam.Map(
                lambda x: f"{x['user_id']}: ${x['original_amount']} -> "
                         f"${x['enriched_amount']:.2f} ({x['tier']})"
            )
            | 'WriteEnriched' >> beam.io.WriteToText('output/enriched_data')
        )
    
    print("✅ Setup/Teardown example completed!")


def run_with_error_handling():
    """
    ParDo with error handling for invalid data.
    """
    json_strings = [
        '{"name": "Alice", "age": 25}',
        '{"name": "Bob", "age": 30}',
        'invalid json data',  # This will be skipped
        '{"name": "Charlie", "age": 35}',
        '{broken',  # This will be skipped
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateJSON' >> beam.Create(json_strings)
            | 'ParseJSON' >> beam.ParDo(ParseJsonFn())
            | 'FormatParsed' >> beam.Map(
                lambda x: f"{x['name']} is {x['age']} years old"
            )
            | 'WriteParsed' >> beam.io.WriteToText('output/parsed_json')
        )
    
    print("✅ Error handling example completed!")


def run_multiple_outputs():
    """
    ParDo with multiple tagged outputs.
    """
    sales_data = [
        ('product1', 150),
        ('product2', 50),
        ('product3', 200),
        ('product4', 75),
        ('product5', 300),
    ]
    
    with beam.Pipeline() as pipeline:
        # Apply ParDo with multiple outputs
        results = (
            pipeline
            | 'CreateSales' >> beam.Create(sales_data)
            | 'SplitByValue' >> beam.ParDo(
                SplitByThresholdFn(),
                threshold=100
            ).with_outputs('high', 'low')
        )
        
        # Process high-value sales
        (
            results.high
            | 'FormatHigh' >> beam.Map(
                lambda x: f'HIGH: {x[0]} = ${x[1]}'
            )
            | 'WriteHigh' >> beam.io.WriteToText('output/high_value_sales')
        )
        
        # Process low-value sales
        (
            results.low
            | 'FormatLow' >> beam.Map(
                lambda x: f'LOW: {x[0]} = ${x[1]}'
            )
            | 'WriteLow' >> beam.io.WriteToText('output/low_value_sales')
        )
    
    print("✅ Multiple outputs example completed!")


def run_filter_transform():
    """
    ParDo that filters and transforms.
    """
    people = [
        ('Alice', 25, 'New York'),
        ('Bob', 17, 'Los Angeles'),  # Will be filtered out
        ('Charlie', 30, 'Chicago'),
        ('Diana', 16, 'Houston'),    # Will be filtered out
        ('Eve', 28, 'Phoenix'),
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreatePeople' >> beam.Create(people)
            | 'FilterAndTransform' >> beam.ParDo(FilterAndTransformFn())
            | 'WriteFiltered' >> beam.io.WriteToText('output/filtered_people')
        )
    
    print("✅ Filter and transform example completed!")


# DETAILED EXPLANATION:
"""
PARDO (Parallel Do):

1. What is ParDo?
   - Most flexible and powerful transform in Beam
   - Allows custom element-wise processing
   - Can emit 0, 1, or many outputs per input
   - Supports side inputs and side outputs

2. DoFn Class:
   - Defines custom processing logic
   - Main method: process(self, element)
   - Optional methods: setup(), teardown(), start_bundle(), finish_bundle()

3. Process Method:
   - Called for each element in the PCollection
   - Use 'yield' to emit outputs (can yield multiple times)
   - Use 'return' to filter out elements (don't yield)

4. Setup and Teardown:
   - setup(): Called once per worker (initialization)
   - teardown(): Called once per worker (cleanup)
   - Use for expensive operations (DB connections, loading models)

5. Multiple Outputs:
   - Use TaggedOutput to emit to different outputs
   - Access outputs using .with_outputs('tag1', 'tag2')
   - Each output is a separate PCollection

6. When to Use ParDo vs Map/FlatMap:
   
   Use Map when:
   - Simple 1-to-1 transformation
   - No need for setup/teardown
   - No complex logic
   
   Use FlatMap when:
   - Simple 1-to-many transformation
   - No need for setup/teardown
   
   Use ParDo when:
   - Need setup/teardown
   - Complex processing logic
   - Multiple outputs
   - Error handling
   - Access to side inputs
   - Stateful processing

7. Best Practices:
   - Make DoFn classes serializable (avoid non-serializable members)
   - Use setup() for expensive initialization
   - Handle errors gracefully
   - Use type hints for better code clarity
   - Name your DoFn classes descriptively

COMPARISON:

# Map (simple 1-to-1)
| beam.Map(lambda x: x * 2)

# FlatMap (simple 1-to-many)
| beam.FlatMap(lambda x: x.split(','))

# ParDo (complex processing)
| beam.ParDo(MyCustomDoFn())
"""


if __name__ == '__main__':
    print("Running ParDo Examples...")
    print("=" * 60)
    
    print("\n1. Basic ParDo")
    print("-" * 60)
    run_basic_pardo()
    
    print("\n2. Setup and Teardown")
    print("-" * 60)
    run_with_setup_teardown()
    
    print("\n3. Error Handling")
    print("-" * 60)
    run_with_error_handling()
    
    print("\n4. Multiple Outputs")
    print("-" * 60)
    run_multiple_outputs()
    
    print("\n5. Filter and Transform")
    print("-" * 60)
    run_filter_transform()
    
    print("\n" + "=" * 60)
    print("✅ All ParDo examples completed!")
    print("Check output/ directory for results.")
