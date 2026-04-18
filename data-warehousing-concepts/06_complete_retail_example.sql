-- ============================================================================
-- Complete Retail Data Warehouse Example
-- ============================================================================
-- This file demonstrates a complete, production-ready retail data warehouse
-- with all concepts integrated: star schema, SCD Type 2, and partitioning.
-- ============================================================================

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Date Dimension (Comprehensive)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    
    -- Day attributes
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_of_week_name VARCHAR(10),
    day_of_year INTEGER,
    day_suffix VARCHAR(4),
    
    -- Week attributes
    week_of_year INTEGER,
    week_of_month INTEGER,
    iso_week VARCHAR(10),
    
    -- Month attributes
    month_number INTEGER,
    month_name VARCHAR(10),
    month_abbr VARCHAR(3),
    days_in_month INTEGER,
    
    -- Quarter attributes
    quarter INTEGER,
    quarter_name VARCHAR(10),
    
    -- Year attributes
    year INTEGER,
    year_month VARCHAR(7),
    
    -- Fiscal period
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    fiscal_month INTEGER,
    fiscal_week INTEGER,
    
    -- Special indicators
    is_weekend BOOLEAN,
    is_weekday BOOLEAN,
    is_holiday BOOLEAN,
    is_business_day BOOLEAN,
    holiday_name VARCHAR(50),
    
    -- Season
    season VARCHAR(10),
    
    -- Relative dates
    is_current_day BOOLEAN,
    is_current_week BOOLEAN,
    is_current_month BOOLEAN,
    is_current_quarter BOOLEAN,
    is_current_year BOOLEAN
);

-- Populate date dimension for 5 years
INSERT INTO dim_date
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INTEGER as date_key,
    d as date_value,
    EXTRACT(DAY FROM d)::INTEGER,
    EXTRACT(DOW FROM d)::INTEGER,
    TO_CHAR(d, 'Day'),
    EXTRACT(DOY FROM d)::INTEGER,
    TO_CHAR(d, 'DDth'),
    EXTRACT(WEEK FROM d)::INTEGER,
    CEIL(EXTRACT(DAY FROM d) / 7.0)::INTEGER,
    TO_CHAR(d, 'IYYY-IW'),
    EXTRACT(MONTH FROM d)::INTEGER,
    TO_CHAR(d, 'Month'),
    TO_CHAR(d, 'Mon'),
    EXTRACT(DAY FROM (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day'))::INTEGER,
    EXTRACT(QUARTER FROM d)::INTEGER,
    'Q' || EXTRACT(QUARTER FROM d)::TEXT,
    EXTRACT(YEAR FROM d)::INTEGER,
    TO_CHAR(d, 'YYYY-MM'),
    CASE WHEN EXTRACT(MONTH FROM d) >= 4 THEN EXTRACT(YEAR FROM d)::INTEGER 
         ELSE EXTRACT(YEAR FROM d)::INTEGER - 1 END,
    CASE WHEN EXTRACT(MONTH FROM d) >= 4 THEN CEIL((EXTRACT(MONTH FROM d) - 3) / 3.0)::INTEGER
         ELSE CEIL((EXTRACT(MONTH FROM d) + 9) / 3.0)::INTEGER END,
    CASE WHEN EXTRACT(MONTH FROM d) >= 4 THEN EXTRACT(MONTH FROM d)::INTEGER - 3
         ELSE EXTRACT(MONTH FROM d)::INTEGER + 9 END,
    EXTRACT(WEEK FROM d)::INTEGER,
    EXTRACT(DOW FROM d) IN (0, 6),
    EXTRACT(DOW FROM d) NOT IN (0, 6),
    d IN ('2024-01-01', '2024-07-04', '2024-12-25'),
    EXTRACT(DOW FROM d) NOT IN (0, 6) AND d NOT IN ('2024-01-01', '2024-07-04', '2024-12-25'),
    CASE 
        WHEN d = '2024-01-01' THEN 'New Year'
        WHEN d = '2024-07-04' THEN 'Independence Day'
        WHEN d = '2024-12-25' THEN 'Christmas'
        ELSE NULL
    END,
    CASE 
        WHEN EXTRACT(MONTH FROM d) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM d) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM d) IN (6, 7, 8) THEN 'Summer'
        ELSE 'Fall'
    END,
    d = CURRENT_DATE,
    DATE_TRUNC('week', d) = DATE_TRUNC('week', CURRENT_DATE),
    DATE_TRUNC('month', d) = DATE_TRUNC('month', CURRENT_DATE),
    DATE_TRUNC('quarter', d) = DATE_TRUNC('quarter', CURRENT_DATE),
    DATE_TRUNC('year', d) = DATE_TRUNC('year', CURRENT_DATE)
FROM generate_series('2022-01-01'::DATE, '2026-12-31'::DATE, '1 day'::INTERVAL) d;

CREATE INDEX idx_date_value ON dim_date(date_value);
CREATE INDEX idx_date_year_month ON dim_date(year, month_number);

-- ----------------------------------------------------------------------------
-- Product Dimension (Star Schema - Denormalized)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_product CASCADE;

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL UNIQUE,
    sku VARCHAR(30),
    upc VARCHAR(20),
    
    -- Product details
    product_name VARCHAR(200) NOT NULL,
    product_description TEXT,
    
    -- Category hierarchy (denormalized)
    department_id VARCHAR(10),
    department_name VARCHAR(50),
    category_id VARCHAR(10),
    category_name VARCHAR(50),
    subcategory_id VARCHAR(10),
    subcategory_name VARCHAR(50),
    
    -- Brand
    brand_id VARCHAR(10),
    brand_name VARCHAR(50),
    
    -- Supplier
    supplier_id VARCHAR(10),
    supplier_name VARCHAR(100),
    
    -- Product attributes
    color VARCHAR(30),
    size VARCHAR(20),
    weight_kg DECIMAL(8,2),
    dimensions VARCHAR(50),
    
    -- Pricing
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    wholesale_price DECIMAL(10,2),
    
    -- Status
    product_status VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_discontinued BOOLEAN DEFAULT FALSE,
    
    -- Dates
    launch_date DATE,
    discontinue_date DATE,
    
    -- Metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample products
INSERT INTO dim_product (product_id, sku, product_name, department_name, category_name, subcategory_name, 
                         brand_name, supplier_name, standard_cost, list_price, product_status, is_active) VALUES
('PROD-001', 'SKU-001', 'Laptop Pro 15"', 'Electronics', 'Computers', 'Laptops', 'TechBrand', 'TechCorp', 800.00, 1299.99, 'Active', TRUE),
('PROD-002', 'SKU-002', 'Wireless Mouse', 'Electronics', 'Accessories', 'Mice', 'TechBrand', 'TechCorp', 12.00, 29.99, 'Active', TRUE),
('PROD-003', 'SKU-003', 'Office Chair Deluxe', 'Furniture', 'Seating', 'Office Chairs', 'ComfortCo', 'FurnitureMfg', 150.00, 299.99, 'Active', TRUE),
('PROD-004', 'SKU-004', 'LED Desk Lamp', 'Electronics', 'Lighting', 'Desk Lamps', 'BrightLight', 'LightMfg', 20.00, 49.99, 'Active', TRUE),
('PROD-005', 'SKU-005', 'Notebook Set Premium', 'Stationery', 'Paper Products', 'Notebooks', 'WriteCo', 'PaperMfg', 5.00, 12.99, 'Active', TRUE),
('PROD-006', 'SKU-006', 'Mechanical Keyboard', 'Electronics', 'Accessories', 'Keyboards', 'TechBrand', 'TechCorp', 45.00, 89.99, 'Active', TRUE),
('PROD-007', 'SKU-007', 'Monitor 27"', 'Electronics', 'Displays', 'Monitors', 'ViewTech', 'DisplayCorp', 180.00, 349.99, 'Active', TRUE),
('PROD-008', 'SKU-008', 'Desk Organizer', 'Stationery', 'Organization', 'Desk Accessories', 'OfficePro', 'OfficeMfg', 8.00, 19.99, 'Active', TRUE);

CREATE INDEX idx_product_id ON dim_product(product_id);
CREATE INDEX idx_product_category ON dim_product(category_name);
CREATE INDEX idx_product_brand ON dim_product(brand_name);

-- ----------------------------------------------------------------------------
-- Customer Dimension (SCD Type 2)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_customer CASCADE;

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    
    -- Personal info
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    
    -- Address (SCD Type 2 tracked)
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    
    -- Demographics
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    income_bracket VARCHAR(30),
    
    -- Customer classification (SCD Type 2 tracked)
    customer_segment VARCHAR(30),
    loyalty_tier VARCHAR(20),
    
    -- SCD Type 2 columns
    effective_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (customer_id, effective_date)
);

-- Sample customers
INSERT INTO dim_customer (customer_id, first_name, last_name, full_name, email, phone, city, state, country,
                         customer_segment, loyalty_tier, effective_date, end_date, is_current) VALUES
('CUST-001', 'John', 'Smith', 'John Smith', 'john.smith@email.com', '555-0101', 'New York', 'NY', 'USA', 'VIP', 'Gold', '2020-01-01', '9999-12-31', TRUE),
('CUST-002', 'Sarah', 'Johnson', 'Sarah Johnson', 'sarah.j@email.com', '555-0102', 'Los Angeles', 'CA', 'USA', 'VIP', 'Platinum', '2020-03-01', '9999-12-31', TRUE),
('CUST-003', 'Mike', 'Williams', 'Mike Williams', 'mike.w@email.com', '555-0103', 'Chicago', 'IL', 'USA', 'Regular', 'Silver', '2021-06-01', '9999-12-31', TRUE),
('CUST-004', 'Emily', 'Brown', 'Emily Brown', 'emily.b@email.com', '555-0104', 'Houston', 'TX', 'USA', 'Regular', 'Bronze', '2022-01-01', '9999-12-31', TRUE),
('CUST-005', 'David', 'Lee', 'David Lee', 'david.l@email.com', '555-0105', 'Seattle', 'WA', 'USA', 'VIP', 'Platinum', '2019-11-01', '9999-12-31', TRUE);

CREATE INDEX idx_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_customer_current ON dim_customer(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_customer_dates ON dim_customer(effective_date, end_date);

-- ----------------------------------------------------------------------------
-- Store Dimension
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_store CASCADE;

CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL UNIQUE,
    store_name VARCHAR(100),
    store_type VARCHAR(30),
    
    -- Location
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    region VARCHAR(30),
    
    -- Store details
    store_size_sqft INTEGER,
    store_manager VARCHAR(100),
    phone VARCHAR(20),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    opening_date DATE,
    
    -- Metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample stores
INSERT INTO dim_store (store_id, store_name, store_type, city, state, country, region, store_size_sqft, is_active) VALUES
('STORE-001', 'Downtown Flagship', 'Retail', 'New York', 'NY', 'USA', 'Northeast', 5000, TRUE),
('STORE-002', 'Suburban Mall', 'Retail', 'Los Angeles', 'CA', 'USA', 'West', 7500, TRUE),
('STORE-003', 'Airport Store', 'Retail', 'Chicago', 'IL', 'USA', 'Midwest', 3000, TRUE),
('STORE-004', 'Online Store', 'Online', 'Seattle', 'WA', 'USA', 'Online', 0, TRUE);

CREATE INDEX idx_store_id ON dim_store(store_id);
CREATE INDEX idx_store_region ON dim_store(region);

-- ============================================================================
-- FACT TABLE (Partitioned by Date)
-- ============================================================================

DROP TABLE IF EXISTS fact_sales CASCADE;

CREATE TABLE fact_sales (
    sale_id BIGINT,
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    
    -- Degenerate dimensions
    order_number VARCHAR(20),
    invoice_number VARCHAR(20),
    
    -- Measures
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    
    -- Transaction details
    transaction_type VARCHAR(20),
    payment_method VARCHAR(20),
    sales_channel VARCHAR(20),
    
    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (sale_id, date_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
) PARTITION BY RANGE (date_key);

-- Create monthly partitions for 2024
CREATE TABLE fact_sales_2024_01 PARTITION OF fact_sales FOR VALUES FROM (20240101) TO (20240201);
CREATE TABLE fact_sales_2024_02 PARTITION OF fact_sales FOR VALUES FROM (20240201) TO (20240301);
CREATE TABLE fact_sales_2024_03 PARTITION OF fact_sales FOR VALUES FROM (20240301) TO (20240401);
CREATE TABLE fact_sales_2024_04 PARTITION OF fact_sales FOR VALUES FROM (20240401) TO (20240501);
CREATE TABLE fact_sales_2024_05 PARTITION OF fact_sales FOR VALUES FROM (20240501) TO (20240601);
CREATE TABLE fact_sales_2024_06 PARTITION OF fact_sales FOR VALUES FROM (20240601) TO (20240701);

-- Create indexes on partitions
CREATE INDEX idx_sales_product_2024_01 ON fact_sales_2024_01(product_key);
CREATE INDEX idx_sales_customer_2024_01 ON fact_sales_2024_01(customer_key);

-- Sample sales data
INSERT INTO fact_sales VALUES
(1001, 20240115, 1, 1, 1, 'ORD-001', 'INV-001', 1, 1299.99, 100.00, 104.00, 0, 1303.99, 800.00, 503.99, 'Sale', 'Credit Card', 'In-Store', CURRENT_TIMESTAMP),
(1002, 20240120, 2, 2, 1, 'ORD-002', 'INV-002', 2, 29.99, 0.00, 4.80, 0, 64.78, 24.00, 40.78, 'Sale', 'Cash', 'In-Store', CURRENT_TIMESTAMP),
(1003, 20240210, 3, 3, 2, 'ORD-003', 'INV-003', 1, 299.99, 30.00, 21.60, 15.00, 291.59, 150.00, 141.59, 'Sale', 'Debit Card', 'In-Store', CURRENT_TIMESTAMP),
(1004, 20240305, 4, 1, 3, 'ORD-004', 'INV-004', 1, 49.99, 5.00, 3.60, 0, 48.59, 20.00, 28.59, 'Sale', 'Credit Card', 'In-Store', CURRENT_TIMESTAMP),
(1005, 20240412, 5, 4, 1, 'ORD-005', 'INV-005', 3, 12.99, 0.00, 3.12, 0, 41.09, 15.00, 26.09, 'Sale', 'Cash', 'In-Store', CURRENT_TIMESTAMP),
(1006, 20240518, 6, 5, 4, 'ORD-006', 'INV-006', 1, 89.99, 10.00, 6.40, 5.00, 91.39, 45.00, 46.39, 'Sale', 'Credit Card', 'Online', CURRENT_TIMESTAMP),
(1007, 20240622, 7, 2, 2, 'ORD-007', 'INV-007', 1, 349.99, 0.00, 28.00, 0, 377.99, 180.00, 197.99, 'Sale', 'Debit Card', 'In-Store', CURRENT_TIMESTAMP);

-- ============================================================================
-- BUSINESS INTELLIGENCE QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Monthly Sales Summary
-- ----------------------------------------------------------------------------
SELECT 
    d.year,
    d.month_name,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.total_amount), 0), 2) as profit_margin_pct,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_name, d.month_number
ORDER BY d.year, d.month_number;

-- ----------------------------------------------------------------------------
-- Query 2: Product Performance by Category
-- ----------------------------------------------------------------------------
SELECT 
    p.department_name,
    p.category_name,
    COUNT(DISTINCT f.sale_id) as num_sales,
    SUM(f.quantity) as units_sold,
    SUM(f.total_amount) as revenue,
    SUM(f.profit_amount) as profit,
    ROUND(AVG(f.total_amount), 2) as avg_sale_amount
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.department_name, p.category_name
ORDER BY revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 3: Customer Segment Analysis
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_key) as num_customers,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.total_amount) as total_revenue,
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT c.customer_key), 2) as revenue_per_customer,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.is_current = TRUE
GROUP BY c.customer_segment, c.loyalty_tier
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 4: Store Performance by Region
-- ----------------------------------------------------------------------------
SELECT 
    s.region,
    s.store_type,
    COUNT(DISTINCT s.store_key) as num_stores,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT s.store_key), 2) as revenue_per_store
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
GROUP BY s.region, s.store_type
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 5: Sales Trend Analysis (Week over Week)
-- ----------------------------------------------------------------------------
WITH weekly_sales AS (
    SELECT 
        d.year,
        d.week_of_year,
        SUM(f.total_amount) as weekly_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.week_of_year
)
SELECT 
    year,
    week_of_year,
    weekly_revenue,
    LAG(weekly_revenue) OVER (ORDER BY year, week_of_year) as prev_week_revenue,
    weekly_revenue - LAG(weekly_revenue) OVER (ORDER BY year, week_of_year) as revenue_change,
    ROUND(100.0 * (weekly_revenue - LAG(weekly_revenue) OVER (ORDER BY year, week_of_year)) / 
          NULLIF(LAG(weekly_revenue) OVER (ORDER BY year, week_of_year), 0), 2) as pct_change
FROM weekly_sales
ORDER BY year, week_of_year;

-- ----------------------------------------------------------------------------
-- Query 6: Top Customers by Revenue
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.full_name,
    c.customer_segment,
    c.loyalty_tier,
    c.city,
    c.state,
    COUNT(DISTINCT f.sale_id) as num_purchases,
    SUM(f.total_amount) as total_spent,
    ROUND(AVG(f.total_amount), 2) as avg_purchase_value,
    MAX(d.date_value) as last_purchase_date
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE c.is_current = TRUE
GROUP BY c.customer_id, c.full_name, c.customer_segment, c.loyalty_tier, c.city, c.state
ORDER BY total_spent DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Query 7: Sales by Day of Week
-- ----------------------------------------------------------------------------
SELECT 
    d.day_of_week_name,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value,
    CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_of_week_name, d.is_weekend
ORDER BY d.day_of_week;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- This example demonstrates:
-- 1. Star schema design with denormalized dimensions
-- 2. SCD Type 2 for customer dimension
-- 3. Range partitioning on fact table by date
-- 4. Comprehensive date dimension
-- 5. Production-ready analytical queries
-- 6. Proper indexing strategy
-- 7. Real-world business metrics
-- ============================================================================
