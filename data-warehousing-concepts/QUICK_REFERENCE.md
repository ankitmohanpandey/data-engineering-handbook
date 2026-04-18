# Data Warehousing Quick Reference

## Fact vs Dimension Tables

### Fact Table
- **Contains**: Measures/metrics (numbers)
- **Structure**: Narrow (few columns), many rows
- **Keys**: Foreign keys to dimensions
- **Examples**: Sales amount, quantity, profit
- **Types**: Additive, semi-additive, non-additive

### Dimension Table
- **Contains**: Descriptive attributes (context)
- **Structure**: Wide (many columns), fewer rows
- **Keys**: Primary key (surrogate)
- **Examples**: Customer name, product category, date
- **Purpose**: Provide context for analysis

---

## Star vs Snowflake Schema

| Aspect | Star Schema | Snowflake Schema |
|--------|-------------|------------------|
| **Structure** | Denormalized dimensions | Normalized dimensions |
| **Joins** | Fewer (1 per dimension) | More (multi-level) |
| **Performance** | Faster queries | Slower queries |
| **Storage** | More space | Less space |
| **Complexity** | Simple | Complex |
| **Best For** | Query performance | Storage optimization |

### When to Use
- **Star**: Most BI/analytics scenarios, query performance priority
- **Snowflake**: Storage constraints, clear hierarchies needed

---

## Slowly Changing Dimensions (SCD)

### Type 0: Retain Original
- Never change
- Use for: Birth date, SSN

### Type 1: Overwrite
```sql
UPDATE customer SET email = 'new@email.com' WHERE id = 123;
```
- No history
- Use for: Corrections, non-critical changes

### Type 2: Add New Row (Most Common)
```sql
-- Close current
UPDATE customer SET end_date = '2024-01-31', is_current = FALSE WHERE id = 123 AND is_current = TRUE;
-- Insert new
INSERT INTO customer VALUES (456, 123, 'new_address', '2024-02-01', '9999-12-31', TRUE);
```
- Full history preserved
- Use for: Address, salary, status changes

### Type 3: Add Column
```sql
ALTER TABLE customer ADD COLUMN previous_address VARCHAR(100);
UPDATE customer SET previous_address = current_address, current_address = 'new';
```
- Limited history (1-2 previous values)
- Use for: Simple before/after tracking

### Type 6: Hybrid (1+2+3)
- Combines all approaches
- Current value in all rows + new row + previous column

---

## Partitioning Strategies

### Range Partitioning (Date)
```sql
-- PostgreSQL
CREATE TABLE sales PARTITION BY RANGE (order_date);
CREATE TABLE sales_2024_01 PARTITION OF sales 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- BigQuery
CREATE TABLE sales PARTITION BY DATE(order_date);
```
**Use for**: Time-series data, historical data

### List Partitioning (Category)
```sql
CREATE TABLE customers PARTITION BY LIST (region);
CREATE TABLE customers_north PARTITION OF customers 
    FOR VALUES IN ('North', 'Northeast');
```
**Use for**: Geographic regions, categories, status

### Hash Partitioning (Even Distribution)
```sql
CREATE TABLE orders PARTITION BY HASH (customer_id);
CREATE TABLE orders_p0 PARTITION OF orders 
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
**Use for**: Even data distribution, no natural key

### Composite Partitioning
```sql
-- Range + Hash
CREATE TABLE sales PARTITION BY RANGE (sale_date);
CREATE TABLE sales_2024 PARTITION OF sales 
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY HASH (customer_id);
```
**Use for**: Large tables needing multiple levels

---

## Common Queries

### Current SCD Type 2 Records
```sql
SELECT * FROM dim_customer WHERE is_current = TRUE;
```

### Point-in-Time Query
```sql
SELECT * FROM dim_customer 
WHERE customer_id = 'CUST-001'
  AND '2023-06-15' BETWEEN effective_date AND end_date;
```

### Sales by Category (Star Schema)
```sql
SELECT 
    p.category,
    SUM(f.amount) as total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category;
```

### Partition Pruning Check
```sql
EXPLAIN ANALYZE
SELECT * FROM sales_partitioned
WHERE order_date = '2024-03-15';
```

---

## Design Patterns

### Surrogate Keys
```sql
-- Use auto-generated keys, not business keys
product_key SERIAL PRIMARY KEY,  -- Surrogate
product_id VARCHAR(20) UNIQUE    -- Business key
```

### Date Dimension
```sql
-- Always create comprehensive date dimension
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_value DATE,
    day_of_week VARCHAR(10),
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

### Degenerate Dimensions
```sql
-- Dimension attributes in fact table
CREATE TABLE fact_sales (
    sale_id BIGINT,
    order_number VARCHAR(20),  -- Degenerate dimension
    invoice_number VARCHAR(20), -- Degenerate dimension
    -- ... measures
);
```

---

## Performance Tips

### Indexing
```sql
-- Index foreign keys
CREATE INDEX idx_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_sales_date ON fact_sales(date_key);

-- Index frequently queried columns
CREATE INDEX idx_customer_segment ON dim_customer(customer_segment);
```

### Partition Pruning
```sql
-- Good: Enables pruning
WHERE order_date = '2024-03-15'
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'

-- Bad: Prevents pruning
WHERE EXTRACT(YEAR FROM order_date) = 2024
WHERE DATE_TRUNC('month', order_date) = '2024-03-01'
```

### Materialized Views
```sql
CREATE MATERIALIZED VIEW sales_monthly AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_key,
    SUM(amount) as total_sales
FROM fact_sales
GROUP BY DATE_TRUNC('month', order_date), product_key;

-- Refresh periodically
REFRESH MATERIALIZED VIEW sales_monthly;
```

---

## Common Mistakes to Avoid

❌ **Using business keys in fact tables**
```sql
-- Bad
CREATE TABLE fact_sales (
    customer_id VARCHAR(20),  -- Business key
    ...
);

-- Good
CREATE TABLE fact_sales (
    customer_key INTEGER,  -- Surrogate key
    ...
);
```

❌ **No date dimension**
```sql
-- Bad: Just store date
order_date DATE

-- Good: Reference date dimension
date_key INTEGER REFERENCES dim_date(date_key)
```

❌ **Over-partitioning**
```sql
-- Bad: Daily partitions for 10 years = 3650 partitions
-- Good: Monthly partitions = 120 partitions
```

❌ **Functions on partition keys**
```sql
-- Bad
WHERE YEAR(order_date) = 2024

-- Good
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
```

---

## Grain Definition

Always clearly define fact table grain:

- ✅ "One row per product per transaction"
- ✅ "One row per customer per day"
- ✅ "One row per store per month"
- ❌ "Sales data" (too vague)

---

## Measure Types

### Additive
Can sum across all dimensions
- Sales amount, quantity, cost

### Semi-Additive
Can sum across some dimensions
- Account balance (not across time)
- Inventory levels (not across time)

### Non-Additive
Cannot sum
- Ratios, percentages, averages
- Calculate from additive measures

---

## Quick Commands

### Check Partition Info
```sql
-- PostgreSQL
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE tablename LIKE 'sales_%'
ORDER BY tablename;
```

### View SCD History
```sql
SELECT 
    customer_id,
    customer_segment,
    effective_date,
    end_date,
    is_current
FROM dim_customer
WHERE customer_id = 'CUST-001'
ORDER BY effective_date;
```

### Add Partition
```sql
CREATE TABLE sales_2024_12 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
```

### Drop Old Partition
```sql
-- Detach first (keeps data)
ALTER TABLE sales_fact DETACH PARTITION sales_2020;

-- Then drop or archive
DROP TABLE sales_2020;
-- OR
ALTER TABLE sales_2020 SET SCHEMA archive;
```

---

## Resources

- **Kimball Method**: Star schema, dimensional modeling
- **Inmon Method**: Normalized, enterprise warehouse
- **Data Vault**: Hybrid approach for agility
- **Tools**: dbt, Snowflake, BigQuery, Redshift, PostgreSQL
