"""
Example 1: Word Count - The "Hello World" of Apache Beam

This example demonstrates:
- Reading from a text file
- Basic transformations (Map, FlatMap)
- Aggregation (CombinePerKey)
- Writing results to a file

WHAT IT DOES:
Counts the frequency of each word in a text file.

HOW TO RUN:
python 01_word_count.py

EXPECTED OUTPUT:
A file 'output/word_count-00000-of-00001' with word counts like:
hello: 3
world: 2
apache: 1
"""

import apache_beam as beam
import re


def run():
    # Sample input data (you can also read from a file)
    input_text = [
        "Hello world",
        "Hello Apache Beam",
        "Apache Beam is awesome",
        "Hello world again"
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            # Step 1: Create initial PCollection from list
            | 'Create' >> beam.Create(input_text)
            
            # Step 2: Split each line into words
            # FlatMap: One line -> Multiple words
            | 'Split' >> beam.FlatMap(lambda line: re.findall(r'\w+', line.lower()))
            
            # Step 3: Create (word, 1) pairs
            # Map: One word -> One (word, 1) tuple
            | 'PairWithOne' >> beam.Map(lambda word: (word, 1))
            
            # Step 4: Group by word and sum the counts
            # CombinePerKey: Aggregate all values for each key
            | 'CountPerWord' >> beam.CombinePerKey(sum)
            
            # Step 5: Format output as "word: count"
            | 'Format' >> beam.Map(lambda word_count: f'{word_count[0]}: {word_count[1]}')
            
            # Step 6: Write to file
            | 'Write' >> beam.io.WriteToText('output/word_count')
        )
    
    print("✅ Pipeline completed! Check 'output/word_count-00000-of-00001' for results.")


def run_from_file():
    """
    Alternative: Read from an actual text file
    
    First create a sample file:
    echo "Hello world\nHello Apache Beam\nApache Beam is awesome" > input.txt
    
    Then run this function.
    """
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'Read' >> beam.io.ReadFromText('input.txt')
            | 'Split' >> beam.FlatMap(lambda line: re.findall(r'\w+', line.lower()))
            | 'PairWithOne' >> beam.Map(lambda word: (word, 1))
            | 'CountPerWord' >> beam.CombinePerKey(sum)
            | 'Format' >> beam.Map(lambda wc: f'{wc[0]}: {wc[1]}')
            | 'Write' >> beam.io.WriteToText('output/word_count_from_file')
        )
    
    print("✅ Pipeline completed!")


# DETAILED EXPLANATION OF EACH STEP:
"""
1. Create: 
   Input: Nothing
   Output: PCollection(['Hello world', 'Hello Apache Beam', ...])

2. FlatMap (Split):
   Input: 'Hello world'
   Output: ['hello', 'world']
   (FlatMap flattens the results, so multiple words from one line become separate elements)

3. Map (PairWithOne):
   Input: 'hello'
   Output: ('hello', 1)
   (Creates key-value pairs for counting)

4. CombinePerKey (CountPerWord):
   Input: [('hello', 1), ('hello', 1), ('hello', 1)]
   Output: ('hello', 3)
   (Sums all values for each unique key)

5. Map (Format):
   Input: ('hello', 3)
   Output: 'hello: 3'
   (Formats for readable output)

6. WriteToText:
   Writes each element to a text file
"""


if __name__ == '__main__':
    print("Running Word Count Example...")
    print("-" * 50)
    run()
    
    # Uncomment to run from file:
    # run_from_file()
