"""
Example 2: Filter and Transform Data

This example demonstrates:
- Filtering data based on conditions
- Chaining multiple transformations
- Working with structured data (dictionaries)
- Multiple output paths

WHAT IT DOES:
Processes a list of users, filters by age, and transforms the data.

HOW TO RUN:
python 02_filter_transform.py

EXPECTED OUTPUT:
Files showing filtered and transformed user data.
"""

import apache_beam as beam


def run():
    # Sample user data
    users = [
        {'name': 'Alice', 'age': 25, 'city': 'New York'},
        {'name': 'Bob', 'age': 17, 'city': 'Los Angeles'},
        {'name': 'Charlie', 'age': 30, 'city': 'Chicago'},
        {'name': 'Diana', 'age': 16, 'city': 'Houston'},
        {'name': 'Eve', 'age': 28, 'city': 'Phoenix'},
        {'name': 'Frank', 'age': 35, 'city': 'Philadelphia'},
    ]
    
    with beam.Pipeline() as pipeline:
        # Create initial PCollection
        all_users = pipeline | 'CreateUsers' >> beam.Create(users)
        
        # Filter: Keep only adults (age >= 18)
        adults = (
            all_users
            | 'FilterAdults' >> beam.Filter(lambda user: user['age'] >= 18)
        )
        
        # Transform: Extract just names of adults
        adult_names = (
            adults
            | 'ExtractNames' >> beam.Map(lambda user: user['name'])
            | 'WriteAdultNames' >> beam.io.WriteToText('output/adult_names')
        )
        
        # Transform: Format adult info as string
        adult_info = (
            adults
            | 'FormatInfo' >> beam.Map(
                lambda u: f"{u['name']} is {u['age']} years old from {u['city']}"
            )
            | 'WriteAdultInfo' >> beam.io.WriteToText('output/adult_info')
        )
        
        # Filter: Keep only users from specific cities
        major_cities = (
            all_users
            | 'FilterMajorCities' >> beam.Filter(
                lambda user: user['city'] in ['New York', 'Los Angeles', 'Chicago']
            )
            | 'FormatCityInfo' >> beam.Map(lambda u: f"{u['name']} - {u['city']}")
            | 'WriteCityInfo' >> beam.io.WriteToText('output/major_cities')
        )
    
    print("✅ Pipeline completed!")
    print("Check output/ directory for results:")
    print("  - adult_names-*")
    print("  - adult_info-*")
    print("  - major_cities-*")


def advanced_filtering():
    """
    More advanced filtering examples
    """
    data = [
        {'product': 'Laptop', 'price': 1200, 'category': 'Electronics'},
        {'product': 'Phone', 'price': 800, 'category': 'Electronics'},
        {'product': 'Desk', 'price': 300, 'category': 'Furniture'},
        {'product': 'Chair', 'price': 150, 'category': 'Furniture'},
        {'product': 'Monitor', 'price': 400, 'category': 'Electronics'},
    ]
    
    with beam.Pipeline() as pipeline:
        products = pipeline | 'CreateProducts' >> beam.Create(data)
        
        # Multiple filter conditions
        expensive_electronics = (
            products
            | 'FilterExpensiveElectronics' >> beam.Filter(
                lambda p: p['category'] == 'Electronics' and p['price'] > 500
            )
            | 'FormatProducts' >> beam.Map(
                lambda p: f"{p['product']}: ${p['price']}"
            )
            | 'WriteExpensive' >> beam.io.WriteToText('output/expensive_electronics')
        )
        
        # Calculate discount prices (20% off)
        discounted = (
            products
            | 'ApplyDiscount' >> beam.Map(
                lambda p: {**p, 'discounted_price': p['price'] * 0.8}
            )
            | 'FormatDiscounted' >> beam.Map(
                lambda p: f"{p['product']}: ${p['price']} -> ${p['discounted_price']:.2f}"
            )
            | 'WriteDiscounted' >> beam.io.WriteToText('output/discounted_products')
        )
    
    print("✅ Advanced filtering completed!")


# DETAILED EXPLANATION:
"""
Filter Transform:
- Takes a PCollection
- Applies a predicate function (returns True/False)
- Keeps only elements where predicate returns True
- Returns a new PCollection with filtered elements

Example:
Input: [1, 2, 3, 4, 5]
Filter: lambda x: x > 3
Output: [4, 5]

Map Transform:
- Takes a PCollection
- Applies a function to each element
- Returns a new PCollection with transformed elements

Example:
Input: [1, 2, 3]
Map: lambda x: x * 2
Output: [2, 4, 6]

Chaining:
You can chain multiple transforms using the | operator:
data | Transform1 | Transform2 | Transform3
"""


if __name__ == '__main__':
    print("Running Filter and Transform Example...")
    print("-" * 50)
    run()
    
    print("\n" + "=" * 50)
    print("Running Advanced Filtering Example...")
    print("-" * 50)
    advanced_filtering()
