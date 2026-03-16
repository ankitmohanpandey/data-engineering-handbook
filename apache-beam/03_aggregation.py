"""
Example 3: Aggregation and GroupBy Operations

This example demonstrates:
- GroupByKey: Grouping data by key
- CombinePerKey: Efficient aggregation per key
- Multiple aggregation operations
- Working with key-value pairs

WHAT IT DOES:
Analyzes sales data to compute totals, averages, and counts per category.

HOW TO RUN:
python 03_aggregation.py

EXPECTED OUTPUT:
Files showing aggregated sales data by category and region.
"""

import apache_beam as beam
from apache_beam.transforms import combiners


def run():
    # Sample sales data: (product, category, price, region)
    sales_data = [
        ('Laptop', 'Electronics', 1200, 'North'),
        ('Phone', 'Electronics', 800, 'South'),
        ('Desk', 'Furniture', 300, 'North'),
        ('Chair', 'Furniture', 150, 'East'),
        ('Monitor', 'Electronics', 400, 'West'),
        ('Table', 'Furniture', 500, 'South'),
        ('Keyboard', 'Electronics', 100, 'North'),
        ('Mouse', 'Electronics', 50, 'East'),
        ('Lamp', 'Furniture', 80, 'West'),
        ('Headphones', 'Electronics', 200, 'South'),
    ]
    
    with beam.Pipeline() as pipeline:
        sales = pipeline | 'CreateSales' >> beam.Create(sales_data)
        
        # Example 1: Total sales per category
        category_totals = (
            sales
            # Create (category, price) pairs
            | 'ExtractCategoryPrice' >> beam.Map(lambda x: (x[1], x[2]))
            # Sum all prices for each category
            | 'SumPerCategory' >> beam.CombinePerKey(sum)
            # Format output
            | 'FormatCategoryTotals' >> beam.Map(
                lambda kv: f'{kv[0]}: ${kv[1]:,}'
            )
            | 'WriteCategoryTotals' >> beam.io.WriteToText('output/category_totals')
        )
        
        # Example 2: Count items per region
        region_counts = (
            sales
            # Create (region, 1) pairs
            | 'ExtractRegion' >> beam.Map(lambda x: (x[3], 1))
            # Count items per region
            | 'CountPerRegion' >> beam.CombinePerKey(sum)
            # Format output
            | 'FormatRegionCounts' >> beam.Map(
                lambda kv: f'{kv[0]}: {kv[1]} items'
            )
            | 'WriteRegionCounts' >> beam.io.WriteToText('output/region_counts')
        )
        
        # Example 3: Average price per category
        category_averages = (
            sales
            # Create (category, price) pairs
            | 'ExtractCategoryPrice2' >> beam.Map(lambda x: (x[1], x[2]))
            # Calculate mean per category
            | 'MeanPerCategory' >> beam.CombinePerKey(combiners.MeanCombineFn())
            # Format output
            | 'FormatCategoryAverages' >> beam.Map(
                lambda kv: f'{kv[0]}: ${kv[1]:.2f} (average)'
            )
            | 'WriteCategoryAverages' >> beam.io.WriteToText('output/category_averages')
        )
        
        # Example 4: Top products per category (using GroupByKey)
        top_products = (
            sales
            # Create (category, (product, price)) pairs
            | 'ExtractCategoryProductPrice' >> beam.Map(
                lambda x: (x[1], (x[0], x[2]))
            )
            # Group all products by category
            | 'GroupByCategory' >> beam.GroupByKey()
            # Find top product per category
            | 'FindTopProduct' >> beam.Map(
                lambda kv: (kv[0], max(kv[1], key=lambda p: p[1]))
            )
            # Format output
            | 'FormatTopProducts' >> beam.Map(
                lambda kv: f'{kv[0]}: {kv[1][0]} (${kv[1][1]})'
            )
            | 'WriteTopProducts' >> beam.io.WriteToText('output/top_products')
        )
    
    print("✅ Pipeline completed!")
    print("Check output/ directory for results:")
    print("  - category_totals-*")
    print("  - region_counts-*")
    print("  - category_averages-*")
    print("  - top_products-*")


def advanced_aggregations():
    """
    More advanced aggregation examples with custom combiners
    """
    # Transaction data: (user_id, amount, timestamp)
    transactions = [
        ('user1', 100, '2024-01-01'),
        ('user2', 200, '2024-01-01'),
        ('user1', 150, '2024-01-02'),
        ('user3', 300, '2024-01-02'),
        ('user2', 250, '2024-01-03'),
        ('user1', 50, '2024-01-03'),
    ]
    
    with beam.Pipeline() as pipeline:
        txns = pipeline | 'CreateTransactions' >> beam.Create(transactions)
        
        # Multiple aggregations per user
        user_stats = (
            txns
            | 'ExtractUserAmount' >> beam.Map(lambda x: (x[0], x[1]))
            | 'CombineUserStats' >> beam.CombinePerKey(
                beam.combiners.TupleCombineFn(
                    sum,  # Total amount
                    combiners.CountCombineFn(),  # Number of transactions
                    max,  # Maximum transaction
                    min   # Minimum transaction
                )
            )
            | 'FormatUserStats' >> beam.Map(
                lambda kv: f'{kv[0]}: Total=${kv[1][0]}, Count={kv[1][1]}, '
                          f'Max=${kv[1][2]}, Min=${kv[1][3]}'
            )
            | 'WriteUserStats' >> beam.io.WriteToText('output/user_stats')
        )
        
        # Top 3 users by total spending
        top_users = (
            txns
            | 'ExtractUserAmount2' >> beam.Map(lambda x: (x[0], x[1]))
            | 'SumPerUser' >> beam.CombinePerKey(sum)
            | 'GetTop3' >> beam.combiners.Top.Of(3, key=lambda kv: kv[1])
            | 'FormatTop3' >> beam.FlatMap(
                lambda top_list: [f'{i+1}. {kv[0]}: ${kv[1]}' 
                                  for i, kv in enumerate(top_list)]
            )
            | 'WriteTop3' >> beam.io.WriteToText('output/top_users')
        )
    
    print("✅ Advanced aggregations completed!")


# DETAILED EXPLANATION:
"""
GroupByKey vs CombinePerKey:

1. GroupByKey:
   - Groups all values for each key
   - Returns (key, iterable_of_values)
   - Can cause memory issues with large value lists
   - Use when you need all values together
   
   Example:
   Input: [('a', 1), ('b', 2), ('a', 3), ('b', 4)]
   Output: [('a', [1, 3]), ('b', [2, 4])]

2. CombinePerKey:
   - Efficiently aggregates values for each key
   - Uses a combiner function (sum, mean, max, etc.)
   - More memory efficient (partial aggregations)
   - Use for aggregations (sum, count, average, etc.)
   
   Example with sum:
   Input: [('a', 1), ('b', 2), ('a', 3), ('b', 4)]
   Output: [('a', 4), ('b', 6)]

Best Practice:
- Use CombinePerKey when possible (more efficient)
- Use GroupByKey only when you need all values

Built-in Combiners:
- sum: Sum all values
- combiners.MeanCombineFn(): Calculate average
- combiners.CountCombineFn(): Count elements
- max/min: Find maximum/minimum
- combiners.Top.Of(n): Get top N elements
- combiners.TupleCombineFn(): Combine multiple aggregations
"""


if __name__ == '__main__':
    print("Running Aggregation Example...")
    print("-" * 50)
    run()
    
    print("\n" + "=" * 50)
    print("Running Advanced Aggregations Example...")
    print("-" * 50)
    advanced_aggregations()
