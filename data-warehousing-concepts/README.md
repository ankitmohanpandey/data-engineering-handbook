# Data Warehousing Concepts Complete Guide

## Table of Contents
1. [What is Data Warehousing?](#what-is-data-warehousing)
2. [Core Concepts](#core-concepts)
3. [Fact & Dimension Tables](#fact--dimension-tables)
4. [Star & Snowflake Schema](#star--snowflake-schema)
5. [Slowly Changing Dimensions (SCD)](#slowly-changing-dimensions-scd)
6. [Partitioning Strategies](#partitioning-strategies)
7. [Best Practices](#best-practices)
8. [Real-World Examples](#real-world-examples)
9. [Performance Optimization](#performance-optimization)

---

## What is Data Warehousing?

**Data Warehousing** is a system used for reporting and data analysis, serving as a central repository of integrated data from multiple sources.

### Key Points
- **Subject-Oriented**: Organized around key subjects (customers, products, sales)
- **Integrated**: Data from multiple sources consolidated
- **Time-Variant**: Historical data stored with timestamps
- **Non-Volatile**: Data is stable and doesn't change frequently

### Why Use Data Warehousing?
✅ **Centralized Data**: Single source of truth for analytics  
✅ **Historical Analysis**: Track changes over time  
✅ **Optimized for Queries**: Fast analytical queries  
✅ **Business Intelligence**: Support decision-making  
✅ **Data Quality**: Cleaned and standardized data  

### Data Warehouse vs Database

| Feature | Data Warehouse | Transactional Database |
|---------|----------------|------------------------|
| Purpose | Analytics | Operations |
| Schema | Denormalized | Normalized |
| Queries | Complex, read-heavy | Simple, write-heavy |
| Data | Historical | Current |
| Updates | Batch loads | Real-time |
| Users | Analysts, BI tools | Applications |

---

## Core Concepts

### 1. OLAP vs OLTP

**OLTP (Online Transaction Processing)**
- Handles day-to-day transactions
- Normalized schema
- Fast inserts/updates
- Example: E-commerce order system

**OLAP (Online Analytical Processing)**
- Handles complex queries for analysis
- Denormalized schema
- Fast aggregations
- Example: Sales analysis dashboard

### 2. ETL Process

**Extract → Transform → Load**

```
Source Systems → Extract → Transform → Load → Data Warehouse
```

- **Extract**: Pull data from various sources
- **Transform**: Clean, standardize, aggregate
- **Load**: Insert into warehouse

### 3. Data Modeling Approaches

- **Kimball (Bottom-Up)**: Start with data marts, integrate later
- **Inmon (Top-Down)**: Build enterprise warehouse first
- **Data Vault**: Hybrid approach for flexibility

---

## Fact & Dimension Tables

### Fact Tables

**Definition**: Store quantitative data (metrics/measures) for analysis.

**Characteristics:**
- Contains numerical measures (sales amount, quantity, revenue)
- Foreign keys to dimension tables
- Large number of rows
- Narrow (fewer columns)
- Additive, semi-additive, or non-additive measures

**Example: Sales Fact Table**

| sale_id | date_key | product_key | customer_key | store_key | quantity | amount | discount |
|---------|----------|-------------|--------------|-----------|----------|--------|----------|
| 1001 | 20240101 | 501 | 2001 | 301 | 2 | 49.98 | 5.00 |
| 1002 | 20240101 | 502 | 2002 | 302 | 1 | 99.99 | 0.00 |
| 1003 | 20240102 | 501 | 2003 | 301 | 3 | 74.97 | 7.50 |

**Types of Facts:**
- **Additive**: Can be summed across all dimensions (quantity, amount)
- **Semi-Additive**: Can be summed across some dimensions (account balance)
- **Non-Additive**: Cannot be summed (ratios, percentages)

### Dimension Tables

**Definition**: Store descriptive attributes (context) for analysis.

**Characteristics:**
- Contains descriptive text attributes
- Primary key referenced by fact tables
- Fewer rows than fact tables
- Wide (many columns)
- Denormalized for query performance

**Example: Product Dimension Table**

| product_key | product_id | product_name | category | subcategory | brand | price | supplier |
|-------------|------------|--------------|----------|-------------|-------|-------|----------|
| 501 | P-001 | Laptop Pro | Electronics | Computers | TechBrand | 999.99 | Supplier A |
| 502 | P-002 | Wireless Mouse | Electronics | Accessories | TechBrand | 29.99 | Supplier B |
| 503 | P-003 | Office Chair | Furniture | Seating | ComfortCo | 199.99 | Supplier C |

**Example: Date Dimension Table**

| date_key | full_date | day | month | year | quarter | day_of_week | is_weekend | is_holiday |
|----------|-----------|-----|-------|------|---------|-------------|------------|------------|
| 20240101 | 2024-01-01 | 1 | January | 2024 | Q1 | Monday | No | Yes |
| 20240102 | 2024-01-02 | 2 | January | 2024 | Q1 | Tuesday | No | No |

**Common Dimension Types:**
- **Conformed Dimensions**: Shared across multiple fact tables
- **Degenerate Dimensions**: Dimension key in fact table without separate dimension table
- **Junk Dimensions**: Combine low-cardinality flags/indicators
- **Role-Playing Dimensions**: Same dimension used multiple times (order_date, ship_date)

---

## Star & Snowflake Schema

### Star Schema

**Definition**: Fact table at center, surrounded by denormalized dimension tables.

**Structure:**
```
        Dimension 1
              |
Dimension 2 - FACT - Dimension 3
              |
        Dimension 4
```

**Example: Retail Star Schema**

```
    Date Dimension
          |
Product - Sales Fact - Customer
          |
    Store Dimension
```

**Advantages:**
✅ Simple to understand and navigate  
✅ Faster query performance (fewer joins)  
✅ Optimized for BI tools  
✅ Easier to maintain  

**Disadvantages:**
❌ Data redundancy in dimensions  
❌ Larger storage for dimensions  
❌ Update anomalies possible  

**SQL Example:**
```sql
SELECT 
    d.year,
    d.quarter,
    p.category,
    SUM(f.amount) as total_sales,
    SUM(f.quantity) as total_quantity
FROM sales_fact f
JOIN date_dim d ON f.date_key = d.date_key
JOIN product_dim p ON f.product_key = p.product_key
WHERE d.year = 2024
GROUP BY d.year, d.quarter, p.category;
```

### Snowflake Schema

**Definition**: Normalized version of star schema where dimensions are broken into sub-dimensions.

**Structure:**
```
    Sub-Dim 1.1
         |
    Dimension 1
         |
    FACT TABLE
         |
    Dimension 2 - Sub-Dim 2.1
                      |
                 Sub-Dim 2.2
```

**Example: Retail Snowflake Schema**

```
Product Dimension → Category Dimension → Department Dimension
        |
    Sales Fact
        |
Customer Dimension → City Dimension → State Dimension → Country Dimension
```

**Advantages:**
✅ Reduced data redundancy  
✅ Smaller storage footprint  
✅ Easier to maintain dimension hierarchies  
✅ Better data integrity  

**Disadvantages:**
❌ More complex queries (more joins)  
❌ Slower query performance  
❌ More complex for end users  

**SQL Example:**
```sql
SELECT 
    d.year,
    cat.category_name,
    dept.department_name,
    SUM(f.amount) as total_sales
FROM sales_fact f
JOIN product_dim p ON f.product_key = p.product_key
JOIN category_dim cat ON p.category_key = cat.category_key
JOIN department_dim dept ON cat.department_key = dept.department_key
JOIN date_dim d ON f.date_key = d.date_key
GROUP BY d.year, cat.category_name, dept.department_name;
```

### Star vs Snowflake Comparison

| Aspect | Star Schema | Snowflake Schema |
|--------|-------------|------------------|
| Normalization | Denormalized | Normalized |
| Query Performance | Faster | Slower |
| Storage | More | Less |
| Complexity | Simple | Complex |
| Joins | Fewer | More |
| Maintenance | Easier | More complex |
| Best For | Query performance | Storage optimization |

---

## Slowly Changing Dimensions (SCD)

**Definition**: Techniques to handle changes in dimension attributes over time.

### Type 0: Retain Original

**Description**: Never change the data, keep original values.

**Use Case**: Attributes that should never change (birth date, SSN)

**Example:**
```
Customer ID | Name | Birth Date
101 | John Doe | 1990-01-15
```
Birth date never changes even if corrected.

### Type 1: Overwrite

**Description**: Update the attribute, no history kept.

**Use Case**: Corrections or attributes where history doesn't matter

**Before:**
```
Customer ID | Name | Email
101 | John Doe | john.old@email.com
```

**After:**
```
Customer ID | Name | Email
101 | John Doe | john.new@email.com
```

**Advantages:**
✅ Simple to implement  
✅ No additional storage  

**Disadvantages:**
❌ No historical tracking  
❌ Cannot analyze past states  

**SQL Implementation:**
```sql
UPDATE customer_dim
SET email = 'john.new@email.com',
    last_updated = CURRENT_TIMESTAMP
WHERE customer_id = 101;
```

### Type 2: Add New Row

**Description**: Create new row for each change, maintain full history.

**Use Case**: Track historical changes (address, salary, status)

**Initial:**
```
SK | Customer ID | Name | Address | Effective_Date | End_Date | Is_Current
1  | 101 | John Doe | 123 Main St | 2020-01-01 | 2023-12-31 | No
```

**After Change:**
```
SK | Customer ID | Name | Address | Effective_Date | End_Date | Is_Current
1  | 101 | John Doe | 123 Main St | 2020-01-01 | 2023-12-31 | No
2  | 101 | John Doe | 456 Oak Ave | 2024-01-01 | 9999-12-31 | Yes
```

**Advantages:**
✅ Complete history preserved  
✅ Can analyze point-in-time  
✅ Audit trail maintained  

**Disadvantages:**
❌ Increased storage  
❌ More complex queries  
❌ Surrogate keys required  

**SQL Implementation:**
```sql
-- Close current record
UPDATE customer_dim
SET end_date = CURRENT_DATE - 1,
    is_current = FALSE
WHERE customer_id = 101 AND is_current = TRUE;

-- Insert new record
INSERT INTO customer_dim (customer_id, name, address, effective_date, end_date, is_current)
VALUES (101, 'John Doe', '456 Oak Ave', CURRENT_DATE, '9999-12-31', TRUE);
```

**Query for Current State:**
```sql
SELECT * FROM customer_dim
WHERE customer_id = 101 AND is_current = TRUE;
```

**Query for Historical State:**
```sql
SELECT * FROM customer_dim
WHERE customer_id = 101 
  AND '2022-06-15' BETWEEN effective_date AND end_date;
```

### Type 3: Add New Column

**Description**: Add columns to track limited history (previous value).

**Use Case**: Track one or two previous values

**Example:**
```
Customer ID | Name | Current_Address | Previous_Address | Address_Change_Date
101 | John Doe | 456 Oak Ave | 123 Main St | 2024-01-01
```

**Advantages:**
✅ Simple to implement  
✅ Limited history without new rows  
✅ Easy to query  

**Disadvantages:**
❌ Limited history (only previous value)  
❌ Schema changes for new attributes  
❌ Not scalable for multiple changes  

**SQL Implementation:**
```sql
UPDATE customer_dim
SET previous_address = current_address,
    current_address = '456 Oak Ave',
    address_change_date = CURRENT_DATE
WHERE customer_id = 101;
```

### Type 4: Add History Table

**Description**: Current data in main table, history in separate table.

**Current Table:**
```
Customer ID | Name | Address
101 | John Doe | 456 Oak Ave
```

**History Table:**
```
Customer ID | Name | Address | Effective_Date | End_Date
101 | John Doe | 123 Main St | 2020-01-01 | 2023-12-31
101 | John Doe | 456 Oak Ave | 2024-01-01 | 9999-12-31
```

**Advantages:**
✅ Separates current and historical data  
✅ Optimized queries for current state  
✅ Complete history maintained  

**Disadvantages:**
❌ More complex to maintain  
❌ Requires joins for historical analysis  

### Type 6: Hybrid (1+2+3)

**Description**: Combines Type 1, 2, and 3 approaches.

**Example:**
```
SK | Customer ID | Current_Address | Historical_Address | Effective_Date | End_Date | Is_Current
1  | 101 | 456 Oak Ave | 123 Main St | 2020-01-01 | 2023-12-31 | No
2  | 101 | 456 Oak Ave | 456 Oak Ave | 2024-01-01 | 9999-12-31 | Yes
```

**Features:**
- Type 1: Current_Address updated in all rows
- Type 2: New row for each change
- Type 3: Historical_Address column

---

## Partitioning Strategies

**Definition**: Dividing large tables into smaller, manageable pieces for better performance.

### Why Partition?

✅ **Improved Query Performance**: Scan only relevant partitions  
✅ **Easier Maintenance**: Manage data in chunks  
✅ **Faster Loads**: Load data into specific partitions  
✅ **Efficient Archival**: Drop old partitions easily  
✅ **Parallel Processing**: Process partitions concurrently  

### 1. Range Partitioning

**Description**: Partition by value ranges (most common for dates).

**Use Case**: Time-series data, historical data

**Example: Partition by Date**
```sql
-- BigQuery
CREATE TABLE sales_fact
PARTITION BY DATE(order_date)
AS SELECT * FROM source_table;

-- PostgreSQL
CREATE TABLE sales_fact (
    sale_id BIGINT,
    order_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE sales_2023 PARTITION OF sales_fact
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE sales_2024 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Benefits:**
- Easy to add/remove partitions
- Efficient for time-based queries
- Simple partition pruning

**Example Query:**
```sql
-- Only scans 2024 partition
SELECT SUM(amount) 
FROM sales_fact
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';
```

### 2. List Partitioning

**Description**: Partition by discrete values.

**Use Case**: Geographic regions, product categories, status codes

**Example: Partition by Region**
```sql
-- PostgreSQL
CREATE TABLE customer_data (
    customer_id BIGINT,
    region VARCHAR(50),
    data TEXT
) PARTITION BY LIST (region);

CREATE TABLE customer_north PARTITION OF customer_data
    FOR VALUES IN ('North', 'Northeast', 'Northwest');

CREATE TABLE customer_south PARTITION OF customer_data
    FOR VALUES IN ('South', 'Southeast', 'Southwest');

CREATE TABLE customer_other PARTITION OF customer_data
    DEFAULT;
```

**Benefits:**
- Logical data separation
- Efficient for categorical queries
- Easy to manage by category

### 3. Hash Partitioning

**Description**: Partition using hash function on column value.

**Use Case**: Distribute data evenly when no natural partitioning key

**Example: Partition by Customer ID**
```sql
-- PostgreSQL
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2)
) PARTITION BY HASH (customer_id);

CREATE TABLE orders_p0 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE orders_p1 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE orders_p2 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE orders_p3 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**Benefits:**
- Even data distribution
- Good for parallel processing
- No hot partitions

### 4. Composite Partitioning

**Description**: Combine multiple partitioning strategies.

**Use Case**: Large tables needing multiple levels of partitioning

**Example: Range + Hash**
```sql
-- First partition by date (range), then by customer (hash)
CREATE TABLE sales_fact (
    sale_id BIGINT,
    sale_date DATE,
    customer_id BIGINT,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2024 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY HASH (customer_id);

CREATE TABLE sales_2024_p0 PARTITION OF sales_2024
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
-- ... more hash partitions
```

### 5. Time-Based Partitioning Strategies

**Daily Partitioning:**
```sql
-- BigQuery
CREATE TABLE events
PARTITION BY DATE(event_timestamp);
```

**Monthly Partitioning:**
```sql
-- PostgreSQL
CREATE TABLE sales_jan_2024 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Yearly Partitioning:**
```sql
CREATE TABLE sales_2024 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Partition Maintenance

**Add New Partition:**
```sql
CREATE TABLE sales_2025 PARTITION OF sales_fact
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

**Drop Old Partition:**
```sql
DROP TABLE sales_2020;
```

**Archive Partition:**
```sql
-- Detach partition
ALTER TABLE sales_fact DETACH PARTITION sales_2020;

-- Move to archive schema
ALTER TABLE sales_2020 SET SCHEMA archive;
```

### Partitioning Best Practices

✅ **Choose Right Key**: Use columns in WHERE clauses  
✅ **Partition Size**: 10GB - 100GB per partition  
✅ **Not Too Many**: Avoid thousands of partitions  
✅ **Align with Queries**: Match query patterns  
✅ **Document Strategy**: Clear naming conventions  
✅ **Monitor Performance**: Track partition pruning  
✅ **Automate Maintenance**: Scripts for adding/removing partitions  

❌ **Don't Over-Partition**: Too many partitions hurt performance  
❌ **Don't Partition Small Tables**: Overhead not worth it  
❌ **Don't Use High-Cardinality**: Avoid unique values  

---

## Best Practices

### Schema Design

✅ **Use Surrogate Keys**: Auto-generated keys for dimensions  
✅ **Denormalize Dimensions**: Optimize for query performance  
✅ **Date Dimension**: Always create comprehensive date dimension  
✅ **Conformed Dimensions**: Share dimensions across fact tables  
✅ **Grain Definition**: Clearly define fact table grain  

### Performance Optimization

✅ **Indexing**: Create indexes on foreign keys and frequently queried columns  
✅ **Partitioning**: Partition large fact tables by date  
✅ **Materialized Views**: Pre-aggregate common queries  
✅ **Compression**: Use columnar storage and compression  
✅ **Statistics**: Keep table statistics updated  

### Data Quality

✅ **Validation**: Validate data during ETL  
✅ **Referential Integrity**: Ensure fact-dimension relationships  
✅ **Null Handling**: Define strategy for NULL values  
✅ **Data Profiling**: Regular data quality checks  

### Maintenance

✅ **Incremental Loads**: Load only changed data  
✅ **Archival Strategy**: Move old data to archive  
✅ **Backup & Recovery**: Regular backups  
✅ **Documentation**: Document schema and ETL processes  

---

## Real-World Examples

See example files:
- `01_fact_dimension_basics.sql` - Basic fact and dimension tables
- `02_star_schema_example.sql` - Complete star schema implementation
- `03_snowflake_schema_example.sql` - Snowflake schema with normalized dimensions
- `04_scd_type2_implementation.sql` - SCD Type 2 with triggers
- `05_partitioning_examples.sql` - Various partitioning strategies
- `06_retail_warehouse.sql` - Complete retail data warehouse
- `07_financial_warehouse.sql` - Financial services example

---

## Performance Optimization

### Query Optimization

**Use Partition Pruning:**
```sql
-- Good: Scans only relevant partition
SELECT * FROM sales_fact
WHERE order_date = '2024-01-15';

-- Bad: Scans all partitions
SELECT * FROM sales_fact
WHERE EXTRACT(YEAR FROM order_date) = 2024;
```

**Aggregate Tables:**
```sql
-- Create summary table for common queries
CREATE TABLE sales_monthly_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_key,
    SUM(amount) as total_sales,
    SUM(quantity) as total_quantity
FROM sales_fact
GROUP BY DATE_TRUNC('month', order_date), product_key;
```

**Materialized Views:**
```sql
CREATE MATERIALIZED VIEW sales_by_category AS
SELECT 
    d.year,
    d.quarter,
    p.category,
    SUM(f.amount) as total_sales
FROM sales_fact f
JOIN date_dim d ON f.date_key = d.date_key
JOIN product_dim p ON f.product_key = p.product_key
GROUP BY d.year, d.quarter, p.category;
```

### Storage Optimization

**Columnar Storage:**
- Use columnar formats (Parquet, ORC)
- Better compression
- Faster analytical queries

**Compression:**
```sql
-- BigQuery
CREATE TABLE sales_fact
PARTITION BY DATE(order_date)
CLUSTER BY product_key, customer_key
AS SELECT * FROM source;
```

---

## Resources

- **Kimball Group**: https://www.kimballgroup.com/
- **Data Warehouse Toolkit**: Classic book by Ralph Kimball
- **Inmon's Data Warehouse**: Bill Inmon's methodology
- **Modern Data Stack**: dbt, Snowflake, BigQuery documentation

---

## Next Steps

1. Review fact and dimension concepts
2. Practice creating star schemas
3. Implement SCD Type 2
4. Experiment with partitioning
5. Build a sample data warehouse

---

**Remember**: Good data warehouse design balances query performance, storage efficiency, and maintainability!
