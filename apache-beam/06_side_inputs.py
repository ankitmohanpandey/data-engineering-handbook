"""
Example 6: Side Inputs

This example demonstrates:
- Side inputs (additional data available to all elements)
- Different side input types (singleton, list, dict)
- Enriching data with side inputs
- Broadcasting small datasets

WHAT IT DOES:
Shows how to use side inputs to enrich main data with additional context.

HOW TO RUN:
python 06_side_inputs.py

EXPECTED OUTPUT:
Files showing enriched data using side inputs.
"""

import apache_beam as beam
from apache_beam.pvalue import AsSingleton, AsList, AsDict


def run_singleton_side_input():
    """
    Singleton Side Input: A single value available to all elements.
    
    Use case: Apply a global configuration or multiplier to all elements.
    """
    # Main data: sales amounts
    sales = [100, 200, 150, 300, 250]
    
    # Side input: tax rate (single value)
    tax_rate_data = [0.08]  # 8% tax
    
    with beam.Pipeline() as pipeline:
        # Create main PCollection
        sales_pcoll = pipeline | 'CreateSales' >> beam.Create(sales)
        
        # Create side input PCollection
        tax_rate = pipeline | 'CreateTaxRate' >> beam.Create(tax_rate_data)
        
        # Use side input to calculate total with tax
        totals = (
            sales_pcoll
            | 'CalculateTotal' >> beam.Map(
                lambda amount, rate: {
                    'amount': amount,
                    'tax': amount * rate,
                    'total': amount * (1 + rate)
                },
                rate=AsSingleton(tax_rate)  # Side input as singleton
            )
            | 'FormatTotal' >> beam.Map(
                lambda x: f"Amount: ${x['amount']:.2f}, "
                         f"Tax: ${x['tax']:.2f}, "
                         f"Total: ${x['total']:.2f}"
            )
            | 'WriteTotals' >> beam.io.WriteToText('output/sales_with_tax')
        )
    
    print("✅ Singleton side input example completed!")


def run_list_side_input():
    """
    List Side Input: A list of values available to all elements.
    
    Use case: Filter or validate against a list of valid values.
    """
    # Main data: user transactions
    transactions = [
        ('user1', 'product_A', 100),
        ('user2', 'product_B', 200),
        ('user3', 'product_C', 150),  # Invalid product
        ('user4', 'product_A', 300),
        ('user5', 'product_D', 250),  # Invalid product
    ]
    
    # Side input: valid products
    valid_products_data = ['product_A', 'product_B']
    
    with beam.Pipeline() as pipeline:
        txns = pipeline | 'CreateTransactions' >> beam.Create(transactions)
        valid_products = (
            pipeline 
            | 'CreateValidProducts' >> beam.Create(valid_products_data)
        )
        
        # Filter transactions using side input
        valid_txns = (
            txns
            | 'FilterValid' >> beam.Filter(
                lambda txn, valid_list: txn[1] in valid_list,
                valid_list=AsList(valid_products)  # Side input as list
            )
            | 'FormatValid' >> beam.Map(
                lambda t: f"{t[0]} bought {t[1]} for ${t[2]}"
            )
            | 'WriteValid' >> beam.io.WriteToText('output/valid_transactions')
        )
    
    print("✅ List side input example completed!")


def run_dict_side_input():
    """
    Dict Side Input: A dictionary available to all elements.
    
    Use case: Enrich data with lookup values (most common use case).
    """
    # Main data: product sales
    sales = [
        ('product_A', 10),  # 10 units sold
        ('product_B', 5),
        ('product_C', 15),
        ('product_A', 8),
        ('product_B', 12),
    ]
    
    # Side input: product prices (lookup table)
    prices_data = [
        ('product_A', 50),
        ('product_B', 100),
        ('product_C', 75),
    ]
    
    with beam.Pipeline() as pipeline:
        sales_pcoll = pipeline | 'CreateSales' >> beam.Create(sales)
        prices_pcoll = (
            pipeline 
            | 'CreatePrices' >> beam.Create(prices_data)
        )
        
        # Enrich sales with prices
        enriched = (
            sales_pcoll
            | 'EnrichWithPrice' >> beam.Map(
                lambda sale, prices: {
                    'product': sale[0],
                    'quantity': sale[1],
                    'unit_price': prices.get(sale[0], 0),
                    'total_revenue': sale[1] * prices.get(sale[0], 0)
                },
                prices=AsDict(prices_pcoll)  # Side input as dict
            )
            | 'FormatEnriched' >> beam.Map(
                lambda x: f"{x['product']}: {x['quantity']} units × "
                         f"${x['unit_price']} = ${x['total_revenue']}"
            )
            | 'WriteEnriched' >> beam.io.WriteToText('output/enriched_sales')
        )
    
    print("✅ Dict side input example completed!")


def run_multiple_side_inputs():
    """
    Multiple Side Inputs: Use multiple side inputs together.
    
    Use case: Enrich data with multiple lookup tables.
    """
    # Main data: orders
    orders = [
        ('order1', 'user1', 'product_A', 2),
        ('order2', 'user2', 'product_B', 1),
        ('order3', 'user1', 'product_C', 3),
    ]
    
    # Side input 1: user info
    users_data = [
        ('user1', 'Alice'),
        ('user2', 'Bob'),
    ]
    
    # Side input 2: product info
    products_data = [
        ('product_A', 'Laptop', 1000),
        ('product_B', 'Phone', 500),
        ('product_C', 'Monitor', 300),
    ]
    
    with beam.Pipeline() as pipeline:
        orders_pcoll = pipeline | 'CreateOrders' >> beam.Create(orders)
        users_pcoll = (
            pipeline 
            | 'CreateUsers' >> beam.Create(users_data)
        )
        products_pcoll = (
            pipeline 
            | 'CreateProducts' >> beam.Create(products_data)
        )
        
        # Enrich orders with both user and product info
        enriched_orders = (
            orders_pcoll
            | 'EnrichOrders' >> beam.Map(
                lambda order, users, products: {
                    'order_id': order[0],
                    'user_name': users.get(order[1], 'Unknown'),
                    'product_name': products.get(order[2], ('Unknown', 0))[0],
                    'quantity': order[3],
                    'unit_price': products.get(order[2], ('Unknown', 0))[1],
                    'total': order[3] * products.get(order[2], ('Unknown', 0))[1]
                },
                users=AsDict(users_pcoll),
                products=AsDict(products_pcoll)
            )
            | 'FormatOrders' >> beam.Map(
                lambda x: f"Order {x['order_id']}: {x['user_name']} bought "
                         f"{x['quantity']} × {x['product_name']} = ${x['total']}"
            )
            | 'WriteOrders' >> beam.io.WriteToText('output/enriched_orders')
        )
    
    print("✅ Multiple side inputs example completed!")


class EnrichWithSideInputFn(beam.DoFn):
    """
    Using side inputs in a DoFn.
    """
    
    def process(self, element, lookup_dict):
        """
        Process element with side input.
        
        Args:
            element: Main element to process
            lookup_dict: Side input dictionary
        """
        key, value = element
        enriched_value = lookup_dict.get(key, 'N/A')
        
        yield {
            'key': key,
            'value': value,
            'enriched': enriched_value
        }


def run_side_input_with_pardo():
    """
    Using side inputs with ParDo.
    """
    # Main data
    main_data = [
        ('A', 100),
        ('B', 200),
        ('C', 300),
    ]
    
    # Side input: lookup data
    lookup_data = [
        ('A', 'Category 1'),
        ('B', 'Category 2'),
        ('C', 'Category 3'),
    ]
    
    with beam.Pipeline() as pipeline:
        main_pcoll = pipeline | 'CreateMain' >> beam.Create(main_data)
        lookup_pcoll = (
            pipeline 
            | 'CreateLookup' >> beam.Create(lookup_data)
        )
        
        enriched = (
            main_pcoll
            | 'EnrichWithParDo' >> beam.ParDo(
                EnrichWithSideInputFn(),
                lookup_dict=AsDict(lookup_pcoll)
            )
            | 'FormatParDo' >> beam.Map(
                lambda x: f"{x['key']}: {x['value']} ({x['enriched']})"
            )
            | 'WriteParDo' >> beam.io.WriteToText('output/pardo_side_input')
        )
    
    print("✅ ParDo with side input example completed!")


# DETAILED EXPLANATION:
"""
SIDE INPUTS:

1. What are Side Inputs?
   - Additional data available to ALL elements in a transform
   - Like "broadcasting" small datasets to all workers
   - Immutable during processing
   - Loaded into memory on each worker

2. Types of Side Inputs:
   
   a) AsSingleton:
      - Single value
      - Example: Configuration, global parameter
      - Usage: rate=AsSingleton(rate_pcoll)
   
   b) AsList:
      - List of values
      - Example: Whitelist, blacklist
      - Usage: valid_list=AsList(valid_pcoll)
   
   c) AsDict:
      - Dictionary (key-value pairs)
      - Example: Lookup tables, enrichment data
      - Usage: lookup=AsDict(lookup_pcoll)
      - Note: PCollection must contain (key, value) tuples

3. When to Use Side Inputs:
   ✅ Small reference data (fits in memory)
   ✅ Lookup tables
   ✅ Configuration parameters
   ✅ Enrichment data
   ✅ Validation lists
   
   ❌ Large datasets (use CoGroupByKey instead)
   ❌ Data that changes frequently
   ❌ Data that doesn't fit in memory

4. Side Inputs vs Joins:
   
   Side Inputs:
   - For small reference data
   - Broadcast to all workers
   - No shuffle required
   - More efficient for small data
   
   CoGroupByKey (Join):
   - For large datasets
   - Requires shuffle
   - Can handle any size data
   - Use when both datasets are large

5. Syntax:
   
   With Map:
   | beam.Map(
       lambda x, side: process(x, side),
       side=AsSingleton(side_pcoll)
   )
   
   With Filter:
   | beam.Filter(
       lambda x, side_list: x in side_list,
       side_list=AsList(side_pcoll)
   )
   
   With ParDo:
   | beam.ParDo(
       MyDoFn(),
       lookup=AsDict(lookup_pcoll)
   )

6. Best Practices:
   - Keep side inputs small (they're loaded into memory)
   - Use AsDict for lookups (most efficient)
   - Consider CoGroupByKey for large datasets
   - Side inputs are recomputed for each window in streaming

7. Common Patterns:
   
   a) Enrichment:
      Enrich main data with additional attributes from lookup
   
   b) Filtering:
      Filter main data based on whitelist/blacklist
   
   c) Validation:
      Validate main data against reference data
   
   d) Configuration:
      Apply global configuration to all elements

EXAMPLE FLOW:

Main PCollection: [elem1, elem2, elem3, ...]
                        ↓
Side Input PCollection: {key1: val1, key2: val2, ...}
                        ↓
                  (broadcast to all workers)
                        ↓
Transform: Each element can access the side input
                        ↓
Output: [enriched_elem1, enriched_elem2, ...]
"""


if __name__ == '__main__':
    print("Running Side Inputs Examples...")
    print("=" * 60)
    
    print("\n1. Singleton Side Input")
    print("-" * 60)
    run_singleton_side_input()
    
    print("\n2. List Side Input")
    print("-" * 60)
    run_list_side_input()
    
    print("\n3. Dict Side Input")
    print("-" * 60)
    run_dict_side_input()
    
    print("\n4. Multiple Side Inputs")
    print("-" * 60)
    run_multiple_side_inputs()
    
    print("\n5. Side Input with ParDo")
    print("-" * 60)
    run_side_input_with_pardo()
    
    print("\n" + "=" * 60)
    print("✅ All side input examples completed!")
    print("Check output/ directory for results.")
