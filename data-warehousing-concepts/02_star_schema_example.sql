-- ============================================================================
-- Star Schema - Complete Implementation
-- ============================================================================
-- This file demonstrates a complete star schema design for a retail
-- data warehouse with one central fact table surrounded by dimension tables.
-- ============================================================================

-- ============================================================================
-- STAR SCHEMA STRUCTURE
-- ============================================================================
--
--           Date Dimension
--                 |
--                 |
--  Product ---- Sales Fact ---- Customer
--  Dimension        |         Dimension
--                   |
--              Store Dimension
--
-- ============================================================================

-- ============================================================================
-- DIMENSION TABLES (Denormalized)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Date Dimension
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
    
    -- Week attributes
    week_of_year INTEGER,
    week_of_month INTEGER,
    
    -- Month attributes
    month_number INTEGER,
    month_name VARCHAR(10),
    month_abbr VARCHAR(3),
    
    -- Quarter attributes
    quarter INTEGER,
    quarter_name VARCHAR(10),
    
    -- Year attributes
    year INTEGER,
    
    -- Fiscal period (assuming fiscal year starts in April)
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    fiscal_month INTEGER,
    
    -- Special day indicators
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    is_business_day BOOLEAN,
    holiday_name VARCHAR(50),
    
    -- Relative date calculations
    days_from_today INTEGER,
    weeks_from_today INTEGER
);

-- Sample data population
INSERT INTO dim_date 
SELECT 
    TO_CHAR(date_value, 'YYYYMMDD')::INTEGER as date_key,
    date_value,
    EXTRACT(DAY FROM date_value)::INTEGER,
    EXTRACT(DOW FROM date_value)::INTEGER,
    TO_CHAR(date_value, 'Day'),
    EXTRACT(DOY FROM date_value)::INTEGER,
    EXTRACT(WEEK FROM date_value)::INTEGER,
    CEIL(EXTRACT(DAY FROM date_value) / 7.0)::INTEGER,
    EXTRACT(MONTH FROM date_value)::INTEGER,
    TO_CHAR(date_value, 'Month'),
    TO_CHAR(date_value, 'Mon'),
    EXTRACT(QUARTER FROM date_value)::INTEGER,
    'Q' || EXTRACT(QUARTER FROM date_value)::TEXT,
    EXTRACT(YEAR FROM date_value)::INTEGER,
    CASE 
        WHEN EXTRACT(MONTH FROM date_value) >= 4 
        THEN EXTRACT(YEAR FROM date_value)::INTEGER
        ELSE EXTRACT(YEAR FROM date_value)::INTEGER - 1
    END,
    CASE 
        WHEN EXTRACT(MONTH FROM date_value) >= 4 
        THEN CEIL((EXTRACT(MONTH FROM date_value) - 3) / 3.0)::INTEGER
        ELSE CEIL((EXTRACT(MONTH FROM date_value) + 9) / 3.0)::INTEGER
    END,
    CASE 
        WHEN EXTRACT(MONTH FROM date_value) >= 4 
        THEN EXTRACT(MONTH FROM date_value)::INTEGER - 3
        ELSE EXTRACT(MONTH FROM date_value)::INTEGER + 9
    END,
    EXTRACT(DOW FROM date_value) IN (0, 6),
    FALSE,
    EXTRACT(DOW FROM date_value) NOT IN (0, 6),
    NULL,
    (CURRENT_DATE - date_value)::INTEGER,
    ((CURRENT_DATE - date_value) / 7)::INTEGER
FROM generate_series('2023-01-01'::DATE, '2025-12-31'::DATE, '1 day'::INTERVAL) as date_value;

-- ----------------------------------------------------------------------------
-- 2. Product Dimension (Denormalized - includes category hierarchy)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_product CASCADE;

CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY,
    
    -- Product identifiers
    product_id VARCHAR(20) NOT NULL UNIQUE,
    sku VARCHAR(30),
    
    -- Product details
    product_name VARCHAR(100) NOT NULL,
    product_description TEXT,
    
    -- Category hierarchy (denormalized for star schema)
    department_id VARCHAR(10),
    department_name VARCHAR(50),
    category_id VARCHAR(10),
    category_name VARCHAR(50),
    subcategory_id VARCHAR(10),
    subcategory_name VARCHAR(50),
    
    -- Brand information
    brand_id VARCHAR(10),
    brand_name VARCHAR(50),
    
    -- Supplier information
    supplier_id VARCHAR(10),
    supplier_name VARCHAR(100),
    supplier_country VARCHAR(50),
    
    -- Product attributes
    color VARCHAR(30),
    size VARCHAR(20),
    weight_kg DECIMAL(8,2),
    unit_of_measure VARCHAR(20),
    
    -- Pricing
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    
    -- Status
    product_status VARCHAR(20),
    is_active BOOLEAN,
    
    -- Dates
    launch_date DATE,
    discontinue_date DATE,
    
    -- Metadata
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    row_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO dim_product VALUES
(1, 'PROD-001', 'SKU-001', 'Laptop Pro 15"', 'High-performance laptop with 16GB RAM', 'DEPT-01', 'Electronics', 'CAT-01', 'Computers', 'SUBCAT-01', 'Laptops', 'BRD-01', 'TechBrand', 'SUP-01', 'TechCorp Inc', 'USA', 'Silver', '15"', 2.5, 'Each', 800.00, 1299.99, 'Active', TRUE, '2023-01-01', NULL, '2023-01-01', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'PROD-002', 'SKU-002', 'Wireless Mouse', 'Ergonomic wireless mouse', 'DEPT-01', 'Electronics', 'CAT-02', 'Accessories', 'SUBCAT-02', 'Mice', 'BRD-01', 'TechBrand', 'SUP-01', 'TechCorp Inc', 'USA', 'Black', 'Standard', 0.15, 'Each', 12.00, 29.99, 'Active', TRUE, '2023-01-01', NULL, '2023-01-01', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'PROD-003', 'SKU-003', 'Office Chair', 'Ergonomic office chair', 'DEPT-02', 'Furniture', 'CAT-03', 'Seating', 'SUBCAT-03', 'Office Chairs', 'BRD-02', 'ComfortCo', 'SUP-02', 'Furniture Mfg Ltd', 'China', 'Black', 'Standard', 15.0, 'Each', 150.00, 299.99, 'Active', TRUE, '2023-02-01', NULL, '2023-02-01', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'PROD-004', 'SKU-004', 'LED Desk Lamp', 'Adjustable LED desk lamp', 'DEPT-01', 'Electronics', 'CAT-04', 'Lighting', 'SUBCAT-04', 'Desk Lamps', 'BRD-03', 'BrightLight', 'SUP-03', 'Light Mfg Co', 'Taiwan', 'White', 'Standard', 1.2, 'Each', 20.00, 49.99, 'Active', TRUE, '2023-03-01', NULL, '2023-03-01', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'PROD-005', 'SKU-005', 'Notebook Set', 'Pack of 5 ruled notebooks', 'DEPT-03', 'Stationery', 'CAT-05', 'Paper Products', 'SUBCAT-05', 'Notebooks', 'BRD-04', 'WriteCo', 'SUP-04', 'Paper Mfg Inc', 'India', 'Assorted', 'A4', 0.8, 'Pack', 5.00, 12.99, 'Active', TRUE, '2023-01-01', NULL, '2023-01-01', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ----------------------------------------------------------------------------
-- 3. Customer Dimension (Denormalized - includes geographic hierarchy)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_customer CASCADE;

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    
    -- Customer identifiers
    customer_id VARCHAR(20) NOT NULL UNIQUE,
    
    -- Personal information
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    age_group VARCHAR(20),
    
    -- Demographics
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    education_level VARCHAR(50),
    occupation VARCHAR(50),
    income_bracket VARCHAR(30),
    
    -- Geographic information (denormalized)
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state_province VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    region VARCHAR(30),
    
    -- Customer classification
    customer_type VARCHAR(30),
    customer_segment VARCHAR(30),
    loyalty_tier VARCHAR(20),
    credit_rating VARCHAR(20),
    
    -- Customer metrics
    lifetime_value DECIMAL(12,2),
    total_purchases INTEGER,
    average_purchase_value DECIMAL(10,2),
    
    -- Status
    account_status VARCHAR(20),
    is_active BOOLEAN,
    
    -- Dates
    registration_date DATE,
    first_purchase_date DATE,
    last_purchase_date DATE,
    
    -- Metadata
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    row_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO dim_customer VALUES
(1, 'CUST-001', 'John', 'Smith', 'John Smith', 'john.smith@email.com', '555-0101', '1985-03-15', '35-44', 'Male', 'Married', 'Bachelor', 'Engineer', '$75K-$100K', '123 Main St', NULL, 'New York', 'NY', 'USA', '10001', 'Northeast', 'Individual', 'VIP', 'Gold', 'Excellent', 15000.00, 45, 333.33, 'Active', TRUE, '2020-01-10', '2020-01-15', '2024-01-07', '2020-01-10', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'CUST-002', 'Sarah', 'Johnson', 'Sarah Johnson', 'sarah.j@email.com', '555-0102', '1990-07-22', '25-34', 'Female', 'Single', 'Master', 'Manager', '$100K-$150K', '456 Oak Ave', 'Apt 5B', 'Los Angeles', 'CA', 'USA', '90001', 'West', 'Individual', 'VIP', 'Platinum', 'Excellent', 25000.00, 60, 416.67, 'Active', TRUE, '2020-03-15', '2020-03-20', '2024-01-06', '2020-03-15', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ----------------------------------------------------------------------------
-- 4. Store Dimension (Denormalized - includes location hierarchy)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_store CASCADE;

CREATE TABLE dim_store (
    store_key INTEGER PRIMARY KEY,
    
    -- Store identifiers
    store_id VARCHAR(20) NOT NULL UNIQUE,
    store_number VARCHAR(10),
    
    -- Store details
    store_name VARCHAR(100),
    store_type VARCHAR(30),
    store_format VARCHAR(30),
    
    -- Location (denormalized)
    address VARCHAR(200),
    city VARCHAR(50),
    state_province VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    region VARCHAR(30),
    district VARCHAR(30),
    market VARCHAR(30),
    
    -- Store attributes
    store_size_sqft INTEGER,
    number_of_employees INTEGER,
    has_parking BOOLEAN,
    has_cafe BOOLEAN,
    
    -- Management
    store_manager VARCHAR(100),
    district_manager VARCHAR(100),
    regional_manager VARCHAR(100),
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- Operating hours
    opening_time TIME,
    closing_time TIME,
    operates_24_7 BOOLEAN,
    
    -- Status
    store_status VARCHAR(20),
    is_active BOOLEAN,
    
    -- Dates
    opening_date DATE,
    closing_date DATE,
    last_renovation_date DATE,
    
    -- Metadata
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    row_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO dim_store VALUES
(1, 'STORE-001', 'S001', 'Downtown Flagship', 'Retail', 'Full-Service', '123 Main St', 'New York', 'NY', 'USA', '10001', 'Northeast', 'Manhattan', 'Metro NYC', 5000, 25, TRUE, TRUE, 'Alice Manager', 'Bob District', 'Carol Regional', '555-1001', 'downtown@store.com', '08:00', '22:00', FALSE, 'Active', TRUE, '2018-01-15', NULL, '2023-06-01', '2018-01-15', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'STORE-002', 'S002', 'Suburban Mall', 'Retail', 'Standard', '456 Oak Ave', 'Los Angeles', 'CA', 'USA', '90001', 'West', 'LA County', 'Southern CA', 7500, 30, TRUE, FALSE, 'Dan Manager', 'Eve District', 'Frank Regional', '555-1002', 'suburban@store.com', '09:00', '21:00', FALSE, 'Active', TRUE, '2019-03-20', NULL, '2022-11-15', '2019-03-20', '9999-12-31', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================================
-- FACT TABLE (Center of Star Schema)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Sales Fact Table
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_sales CASCADE;

CREATE TABLE fact_sales (
    -- Composite key (could also use surrogate key)
    sale_id BIGINT PRIMARY KEY,
    
    -- Foreign keys to dimensions (star points)
    date_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    
    -- Degenerate dimensions (dimensions in fact table)
    order_number VARCHAR(20),
    line_number INTEGER,
    invoice_number VARCHAR(20),
    transaction_id VARCHAR(30),
    
    -- Additive measures
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    
    -- Semi-additive measures
    inventory_on_hand INTEGER,
    
    -- Non-additive measures (ratios, percentages)
    discount_percentage DECIMAL(5,2),
    profit_margin_percentage DECIMAL(5,2),
    
    -- Transaction attributes
    transaction_type VARCHAR(20),
    payment_method VARCHAR(20),
    sales_channel VARCHAR(20),
    promotion_code VARCHAR(20),
    
    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_product FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_store FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);

-- Create indexes for better query performance
CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_store ON fact_sales(store_key);
CREATE INDEX idx_fact_sales_order ON fact_sales(order_number);

-- Sample data
INSERT INTO fact_sales VALUES
(1001, 20240101, 1, 1, 1, 'ORD-001', 1, 'INV-001', 'TXN-001', 1, 1299.99, 100.00, 104.00, 0.00, 1303.99, 800.00, 503.99, 5, 7.69, 38.67, 'Sale', 'Credit Card', 'In-Store', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(1002, 20240101, 2, 2, 1, 'ORD-002', 1, 'INV-002', 'TXN-002', 2, 29.99, 0.00, 4.80, 0.00, 64.78, 24.00, 40.78, 15, 0.00, 62.96, 'Sale', 'Cash', 'In-Store', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(1003, 20240102, 3, 1, 2, 'ORD-003', 1, 'INV-003', 'TXN-003', 1, 299.99, 30.00, 21.60, 15.00, 291.59, 150.00, 141.59, 8, 10.00, 48.56, 'Sale', 'Debit Card', 'In-Store', 'PROMO10', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================================
-- ANALYTICAL QUERIES FOR STAR SCHEMA
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Sales by Department and Category
-- ----------------------------------------------------------------------------
SELECT 
    p.department_name,
    p.category_name,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.quantity) as total_units,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value,
    ROUND(100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.total_amount), 0), 2) as profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.department_name, p.category_name
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 2: Monthly Sales Trend with Year-over-Year Comparison
-- ----------------------------------------------------------------------------
SELECT 
    d.year,
    d.month_name,
    SUM(f.total_amount) as monthly_revenue,
    SUM(f.profit_amount) as monthly_profit,
    COUNT(DISTINCT f.customer_key) as unique_customers,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_name, d.month_number
ORDER BY d.year, d.month_number;

-- ----------------------------------------------------------------------------
-- Query 3: Customer Segment Performance
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    c.loyalty_tier,
    c.region,
    COUNT(DISTINCT c.customer_key) as num_customers,
    SUM(f.total_amount) as total_revenue,
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT c.customer_key), 2) as revenue_per_customer,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value,
    SUM(f.quantity) as total_units_purchased
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment, c.loyalty_tier, c.region
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
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT s.store_key), 2) as revenue_per_store,
    ROUND(100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.total_amount), 0), 2) as profit_margin_pct
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
GROUP BY s.region, s.store_type
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 5: Product Performance with Brand Analysis
-- ----------------------------------------------------------------------------
SELECT 
    p.brand_name,
    p.category_name,
    COUNT(DISTINCT p.product_key) as num_products,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(AVG(f.total_amount), 2) as avg_sale_amount
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.brand_name, p.category_name
ORDER BY total_revenue DESC;

-- ============================================================================
-- STAR SCHEMA BENEFITS DEMONSTRATED
-- ============================================================================
-- 1. Simple Joins: Only one join per dimension (no multi-level joins)
-- 2. Query Performance: Fewer joins = faster queries
-- 3. Easy to Understand: Clear relationship between fact and dimensions
-- 4. BI Tool Friendly: Most BI tools optimized for star schemas
-- 5. Denormalized Dimensions: All attributes in one table (e.g., category hierarchy in product)
-- ============================================================================
