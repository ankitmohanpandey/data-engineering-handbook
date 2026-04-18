-- ============================================================================
-- Partitioning Strategies - Complete Examples
-- ============================================================================
-- This file demonstrates various partitioning strategies for data warehouses
-- including range, list, hash, and composite partitioning.
-- ============================================================================

-- ============================================================================
-- 1. RANGE PARTITIONING (Most Common - Date-based)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 1A: Daily Partitioning (BigQuery Style)
-- ----------------------------------------------------------------------------
-- BigQuery automatically manages partitions

-- BigQuery syntax:
/*
CREATE TABLE sales_fact_daily
PARTITION BY DATE(order_date)
AS SELECT * FROM source_table;
*/

-- ----------------------------------------------------------------------------
-- Example 1B: Monthly Partitioning (PostgreSQL Style)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS sales_fact_monthly CASCADE;

CREATE TABLE sales_fact_monthly (
    sale_id BIGINT,
    order_date DATE NOT NULL,
    customer_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    total_amount DECIMAL(10,2),
    PRIMARY KEY (sale_id, order_date)
) PARTITION BY RANGE (order_date);

-- Create partitions for each month
CREATE TABLE sales_2024_01 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE sales_2024_02 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE sales_2024_03 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

CREATE TABLE sales_2024_04 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');

CREATE TABLE sales_2024_05 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');

CREATE TABLE sales_2024_06 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');

-- Sample data insertion
INSERT INTO sales_fact_monthly VALUES
(1001, '2024-01-15', 'CUST-001', 'PROD-001', 2, 1299.99),
(1002, '2024-01-20', 'CUST-002', 'PROD-002', 1, 299.99),
(1003, '2024-02-10', 'CUST-003', 'PROD-003', 3, 899.97),
(1004, '2024-03-05', 'CUST-001', 'PROD-004', 1, 499.99),
(1005, '2024-04-12', 'CUST-004', 'PROD-001', 2, 2599.98);

-- Query with partition pruning
EXPLAIN ANALYZE
SELECT * FROM sales_fact_monthly
WHERE order_date BETWEEN '2024-02-01' AND '2024-02-29';
-- Only scans sales_2024_02 partition

-- ----------------------------------------------------------------------------
-- Example 1C: Quarterly Partitioning
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS sales_fact_quarterly CASCADE;

CREATE TABLE sales_fact_quarterly (
    sale_id BIGINT,
    order_date DATE NOT NULL,
    customer_id VARCHAR(20),
    total_amount DECIMAL(10,2),
    PRIMARY KEY (sale_id, order_date)
) PARTITION BY RANGE (order_date);

CREATE TABLE sales_2024_q1 PARTITION OF sales_fact_quarterly
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE sales_2024_q2 PARTITION OF sales_fact_quarterly
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE sales_2024_q3 PARTITION OF sales_fact_quarterly
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE sales_2024_q4 PARTITION OF sales_fact_quarterly
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

-- ----------------------------------------------------------------------------
-- Example 1D: Yearly Partitioning
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS sales_fact_yearly CASCADE;

CREATE TABLE sales_fact_yearly (
    sale_id BIGINT,
    order_date DATE NOT NULL,
    customer_id VARCHAR(20),
    total_amount DECIMAL(10,2),
    PRIMARY KEY (sale_id, order_date)
) PARTITION BY RANGE (order_date);

CREATE TABLE sales_2022 PARTITION OF sales_fact_yearly
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

CREATE TABLE sales_2023 PARTITION OF sales_fact_yearly
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE sales_2024 PARTITION OF sales_fact_yearly
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE sales_2025 PARTITION OF sales_fact_yearly
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- ============================================================================
-- 2. LIST PARTITIONING (Categorical Data)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 2A: Partition by Region
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS customer_data_by_region CASCADE;

CREATE TABLE customer_data_by_region (
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    region VARCHAR(50) NOT NULL,
    country VARCHAR(50),
    total_purchases DECIMAL(12,2),
    PRIMARY KEY (customer_id, region)
) PARTITION BY LIST (region);

-- Create partition for each region
CREATE TABLE customers_north_america PARTITION OF customer_data_by_region
    FOR VALUES IN ('North America', 'USA', 'Canada', 'Mexico');

CREATE TABLE customers_europe PARTITION OF customer_data_by_region
    FOR VALUES IN ('Europe', 'UK', 'Germany', 'France', 'Spain');

CREATE TABLE customers_asia PARTITION OF customer_data_by_region
    FOR VALUES IN ('Asia', 'China', 'Japan', 'India', 'Singapore');

CREATE TABLE customers_other PARTITION OF customer_data_by_region
    DEFAULT;  -- Catch-all for any other regions

-- Sample data
INSERT INTO customer_data_by_region VALUES
('CUST-001', 'John Smith', 'USA', 'United States', 15000.00),
('CUST-002', 'Sarah Johnson', 'Canada', 'Canada', 12000.00),
('CUST-003', 'Hans Mueller', 'Germany', 'Germany', 18000.00),
('CUST-004', 'Yuki Tanaka', 'Japan', 'Japan', 20000.00),
('CUST-005', 'Maria Garcia', 'Brazil', 'Brazil', 9000.00);  -- Goes to default partition

-- Query specific region (only scans one partition)
SELECT * FROM customer_data_by_region
WHERE region = 'USA';

-- ----------------------------------------------------------------------------
-- Example 2B: Partition by Product Category
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS inventory_by_category CASCADE;

CREATE TABLE inventory_by_category (
    product_id VARCHAR(20),
    product_name VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    quantity_on_hand INTEGER,
    warehouse_location VARCHAR(50),
    PRIMARY KEY (product_id, category)
) PARTITION BY LIST (category);

CREATE TABLE inventory_electronics PARTITION OF inventory_by_category
    FOR VALUES IN ('Electronics', 'Computers', 'Mobile Devices');

CREATE TABLE inventory_furniture PARTITION OF inventory_by_category
    FOR VALUES IN ('Furniture', 'Office Furniture', 'Home Furniture');

CREATE TABLE inventory_clothing PARTITION OF inventory_by_category
    FOR VALUES IN ('Clothing', 'Apparel', 'Fashion');

CREATE TABLE inventory_other PARTITION OF inventory_by_category
    DEFAULT;

-- ----------------------------------------------------------------------------
-- Example 2C: Partition by Status
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS orders_by_status CASCADE;

CREATE TABLE orders_by_status (
    order_id VARCHAR(20),
    order_date DATE,
    customer_id VARCHAR(20),
    order_status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2),
    PRIMARY KEY (order_id, order_status)
) PARTITION BY LIST (order_status);

CREATE TABLE orders_pending PARTITION OF orders_by_status
    FOR VALUES IN ('Pending', 'Processing', 'Awaiting Payment');

CREATE TABLE orders_active PARTITION OF orders_by_status
    FOR VALUES IN ('Confirmed', 'Shipped', 'In Transit');

CREATE TABLE orders_completed PARTITION OF orders_by_status
    FOR VALUES IN ('Delivered', 'Completed');

CREATE TABLE orders_cancelled PARTITION OF orders_by_status
    FOR VALUES IN ('Cancelled', 'Refunded', 'Returned');

-- ============================================================================
-- 3. HASH PARTITIONING (Even Distribution)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 3A: Partition by Customer ID Hash
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS transactions_by_customer CASCADE;

CREATE TABLE transactions_by_customer (
    transaction_id BIGINT,
    customer_id VARCHAR(20) NOT NULL,
    transaction_date DATE,
    amount DECIMAL(10,2),
    PRIMARY KEY (transaction_id, customer_id)
) PARTITION BY HASH (customer_id);

-- Create 4 hash partitions (distributes data evenly)
CREATE TABLE transactions_p0 PARTITION OF transactions_by_customer
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE transactions_p1 PARTITION OF transactions_by_customer
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE transactions_p2 PARTITION OF transactions_by_customer
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE transactions_p3 PARTITION OF transactions_by_customer
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Sample data (automatically distributed across partitions)
INSERT INTO transactions_by_customer VALUES
(1, 'CUST-001', '2024-01-15', 100.00),
(2, 'CUST-002', '2024-01-16', 200.00),
(3, 'CUST-003', '2024-01-17', 150.00),
(4, 'CUST-004', '2024-01-18', 300.00),
(5, 'CUST-005', '2024-01-19', 250.00);

-- Check distribution
SELECT 
    tableoid::regclass as partition_name,
    COUNT(*) as row_count
FROM transactions_by_customer
GROUP BY tableoid::regclass;

-- ----------------------------------------------------------------------------
-- Example 3B: Partition by Order ID Hash (for very large tables)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS order_details_hash CASCADE;

CREATE TABLE order_details_hash (
    order_detail_id BIGINT NOT NULL,
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    PRIMARY KEY (order_detail_id)
) PARTITION BY HASH (order_detail_id);

-- Create 8 partitions for better parallelism
CREATE TABLE order_details_h0 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 0);

CREATE TABLE order_details_h1 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 1);

CREATE TABLE order_details_h2 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 2);

CREATE TABLE order_details_h3 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 3);

CREATE TABLE order_details_h4 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 4);

CREATE TABLE order_details_h5 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 5);

CREATE TABLE order_details_h6 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 6);

CREATE TABLE order_details_h7 PARTITION OF order_details_hash
    FOR VALUES WITH (MODULUS 8, REMAINDER 7);

-- ============================================================================
-- 4. COMPOSITE PARTITIONING (Multi-Level)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 4A: Range + Hash (Date + Customer)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS sales_composite CASCADE;

CREATE TABLE sales_composite (
    sale_id BIGINT,
    sale_date DATE NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20),
    total_amount DECIMAL(10,2),
    PRIMARY KEY (sale_id, sale_date, customer_id)
) PARTITION BY RANGE (sale_date);

-- First level: partition by year
CREATE TABLE sales_2024_composite PARTITION OF sales_composite
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY HASH (customer_id);

-- Second level: hash partitions within 2024
CREATE TABLE sales_2024_p0 PARTITION OF sales_2024_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE sales_2024_p1 PARTITION OF sales_2024_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE sales_2024_p2 PARTITION OF sales_2024_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE sales_2024_p3 PARTITION OF sales_2024_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Another year
CREATE TABLE sales_2025_composite PARTITION OF sales_composite
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
    PARTITION BY HASH (customer_id);

CREATE TABLE sales_2025_p0 PARTITION OF sales_2025_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE sales_2025_p1 PARTITION OF sales_2025_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE sales_2025_p2 PARTITION OF sales_2025_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE sales_2025_p3 PARTITION OF sales_2025_composite
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Sample data
INSERT INTO sales_composite VALUES
(1, '2024-03-15', 'CUST-001', 'PROD-001', 1299.99),
(2, '2024-06-20', 'CUST-002', 'PROD-002', 299.99),
(3, '2025-01-10', 'CUST-003', 'PROD-003', 899.97);

-- Query benefits from both partitioning levels
SELECT * FROM sales_composite
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND customer_id = 'CUST-001';
-- Only scans one partition: sales_2024_p{X} where X is hash of CUST-001

-- ----------------------------------------------------------------------------
-- Example 4B: Range + List (Date + Region)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS regional_sales CASCADE;

CREATE TABLE regional_sales (
    sale_id BIGINT,
    sale_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_id VARCHAR(20),
    total_amount DECIMAL(10,2),
    PRIMARY KEY (sale_id, sale_date, region)
) PARTITION BY RANGE (sale_date);

-- First level: partition by quarter
CREATE TABLE regional_sales_2024_q1 PARTITION OF regional_sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01')
    PARTITION BY LIST (region);

-- Second level: partition by region within Q1
CREATE TABLE regional_sales_2024_q1_north PARTITION OF regional_sales_2024_q1
    FOR VALUES IN ('North', 'Northeast', 'Northwest');

CREATE TABLE regional_sales_2024_q1_south PARTITION OF regional_sales_2024_q1
    FOR VALUES IN ('South', 'Southeast', 'Southwest');

CREATE TABLE regional_sales_2024_q1_other PARTITION OF regional_sales_2024_q1
    DEFAULT;

-- ============================================================================
-- 5. PARTITION MAINTENANCE OPERATIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Adding New Partitions
-- ----------------------------------------------------------------------------

-- Add new month partition
CREATE TABLE sales_2024_07 PARTITION OF sales_fact_monthly
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');

-- Add new year partition
CREATE TABLE sales_2026 PARTITION OF sales_fact_yearly
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- ----------------------------------------------------------------------------
-- Dropping Old Partitions (for archival)
-- ----------------------------------------------------------------------------

-- Drop old partition (deletes data)
-- DROP TABLE sales_2022;

-- Detach partition (keeps data, removes from parent)
-- ALTER TABLE sales_fact_yearly DETACH PARTITION sales_2022;

-- ----------------------------------------------------------------------------
-- Archiving Partitions
-- ----------------------------------------------------------------------------

-- Create archive schema
CREATE SCHEMA IF NOT EXISTS archive;

-- Detach partition
-- ALTER TABLE sales_fact_yearly DETACH PARTITION sales_2022;

-- Move to archive
-- ALTER TABLE sales_2022 SET SCHEMA archive;

-- Optionally compress or move to cheaper storage
-- pg_dump archive.sales_2022 > /archive/sales_2022.sql
-- DROP TABLE archive.sales_2022;

-- ----------------------------------------------------------------------------
-- Partition Statistics
-- ----------------------------------------------------------------------------

-- View partition information
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'sales_2024%'
ORDER BY tablename;

-- Count rows per partition
SELECT 
    tableoid::regclass as partition_name,
    COUNT(*) as row_count,
    MIN(order_date) as min_date,
    MAX(order_date) as max_date
FROM sales_fact_monthly
GROUP BY tableoid::regclass
ORDER BY partition_name;

-- ============================================================================
-- 6. BIGQUERY PARTITIONING EXAMPLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 6A: Date Partitioned Table
-- ----------------------------------------------------------------------------
/*
-- BigQuery SQL
CREATE TABLE `project.dataset.sales_partitioned`
PARTITION BY DATE(order_date)
AS
SELECT 
    sale_id,
    order_date,
    customer_id,
    total_amount
FROM `project.dataset.source_sales`;
*/

-- ----------------------------------------------------------------------------
-- Example 6B: Date Partitioned with Clustering
-- ----------------------------------------------------------------------------
/*
-- BigQuery SQL
CREATE TABLE `project.dataset.sales_partitioned_clustered`
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, product_id
AS
SELECT * FROM `project.dataset.source_sales`;

-- Benefits:
-- 1. Partition pruning by date
-- 2. Clustering improves queries filtering by customer_id or product_id
*/

-- ----------------------------------------------------------------------------
-- Example 6C: Integer Range Partitioning
-- ----------------------------------------------------------------------------
/*
-- BigQuery SQL
CREATE TABLE `project.dataset.sales_by_amount`
PARTITION BY RANGE_BUCKET(total_amount, GENERATE_ARRAY(0, 10000, 1000))
AS
SELECT * FROM `project.dataset.source_sales`;

-- Creates partitions:
-- < 0, 0-1000, 1000-2000, ..., 9000-10000, > 10000
*/

-- ============================================================================
-- 7. PARTITION PRUNING EXAMPLES
-- ============================================================================

-- Good: Uses partition pruning
EXPLAIN ANALYZE
SELECT * FROM sales_fact_monthly
WHERE order_date = '2024-03-15';
-- Scans only sales_2024_03

-- Good: Range scan with pruning
EXPLAIN ANALYZE
SELECT * FROM sales_fact_monthly
WHERE order_date BETWEEN '2024-02-01' AND '2024-04-30';
-- Scans only sales_2024_02, sales_2024_03, sales_2024_04

-- Bad: No partition pruning (scans all partitions)
EXPLAIN ANALYZE
SELECT * FROM sales_fact_monthly
WHERE EXTRACT(YEAR FROM order_date) = 2024;
-- Scans all partitions because function on partition key

-- Better: Rewrite to enable pruning
EXPLAIN ANALYZE
SELECT * FROM sales_fact_monthly
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
-- Scans only 2024 partitions

-- ============================================================================
-- 8. PARTITIONING BEST PRACTICES
-- ============================================================================

/*
BEST PRACTICES:

1. PARTITION SIZE
   - Target: 10GB - 100GB per partition
   - Too small: Management overhead
   - Too large: Defeats purpose

2. PARTITION KEY SELECTION
   - Choose columns used in WHERE clauses
   - Date columns are most common
   - Consider query patterns

3. NUMBER OF PARTITIONS
   - Avoid thousands of partitions
   - PostgreSQL: < 1000 partitions recommended
   - BigQuery: < 4000 partitions per table

4. PARTITION MAINTENANCE
   - Automate partition creation
   - Regular archival of old partitions
   - Monitor partition sizes

5. QUERY OPTIMIZATION
   - Always include partition key in WHERE clause
   - Avoid functions on partition key
   - Use partition pruning

6. INDEXING
   - Create indexes on partitions, not parent
   - Consider local vs global indexes
   - Index commonly queried columns

7. MONITORING
   - Track partition sizes
   - Monitor query performance
   - Check partition pruning in execution plans

8. DOCUMENTATION
   - Document partitioning strategy
   - Clear naming conventions
   - Maintenance procedures
*/

-- ============================================================================
-- 9. AUTOMATED PARTITION CREATION (PostgreSQL Function)
-- ============================================================================

CREATE OR REPLACE FUNCTION create_monthly_partitions(
    p_table_name TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS VOID AS $$
DECLARE
    v_partition_date DATE;
    v_partition_name TEXT;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    v_partition_date := DATE_TRUNC('month', p_start_date);
    
    WHILE v_partition_date < p_end_date LOOP
        v_partition_name := p_table_name || '_' || TO_CHAR(v_partition_date, 'YYYY_MM');
        v_start_date := v_partition_date;
        v_end_date := v_partition_date + INTERVAL '1 month';
        
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            v_partition_name,
            p_table_name,
            v_start_date,
            v_end_date
        );
        
        RAISE NOTICE 'Created partition: %', v_partition_name;
        
        v_partition_date := v_partition_date + INTERVAL '1 month';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Usage:
-- SELECT create_monthly_partitions('sales_fact_monthly', '2024-01-01', '2024-12-31');

-- ============================================================================
-- END OF PARTITIONING EXAMPLES
-- ============================================================================
