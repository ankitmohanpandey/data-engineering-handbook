-- ============================================================================
-- Snowflake Schema - Complete Implementation
-- ============================================================================
-- This file demonstrates a snowflake schema design where dimension tables
-- are normalized into multiple related tables, creating a snowflake-like structure.
-- ============================================================================

-- ============================================================================
-- SNOWFLAKE SCHEMA STRUCTURE
-- ============================================================================
--
--  Department ← Category ← Product ← FACT → Customer → City → State → Country
--                                      ↓
--                                    Store → District → Region
--
-- ============================================================================

-- ============================================================================
-- NORMALIZED DIMENSION TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Product Dimension Hierarchy (Normalized)
-- ----------------------------------------------------------------------------

-- Department (Top level)
DROP TABLE IF EXISTS dim_department CASCADE;
CREATE TABLE dim_department (
    department_key INTEGER PRIMARY KEY,
    department_id VARCHAR(10) NOT NULL UNIQUE,
    department_name VARCHAR(50) NOT NULL,
    department_description TEXT
);

INSERT INTO dim_department VALUES
(1, 'DEPT-01', 'Electronics', 'Electronic devices and accessories'),
(2, 'DEPT-02', 'Furniture', 'Office and home furniture'),
(3, 'DEPT-03', 'Stationery', 'Office supplies and stationery');

-- Category (Mid level)
DROP TABLE IF EXISTS dim_category CASCADE;
CREATE TABLE dim_category (
    category_key INTEGER PRIMARY KEY,
    category_id VARCHAR(10) NOT NULL UNIQUE,
    category_name VARCHAR(50) NOT NULL,
    category_description TEXT,
    department_key INTEGER NOT NULL,
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key)
);

INSERT INTO dim_category VALUES
(1, 'CAT-01', 'Computers', 'Desktop and laptop computers', 1),
(2, 'CAT-02', 'Accessories', 'Computer accessories', 1),
(3, 'CAT-03', 'Seating', 'Chairs and seating solutions', 2),
(4, 'CAT-04', 'Lighting', 'Lamps and lighting fixtures', 1),
(5, 'CAT-05', 'Paper Products', 'Notebooks, paper, etc.', 3);

-- Subcategory (Bottom level)
DROP TABLE IF EXISTS dim_subcategory CASCADE;
CREATE TABLE dim_subcategory (
    subcategory_key INTEGER PRIMARY KEY,
    subcategory_id VARCHAR(10) NOT NULL UNIQUE,
    subcategory_name VARCHAR(50) NOT NULL,
    subcategory_description TEXT,
    category_key INTEGER NOT NULL,
    FOREIGN KEY (category_key) REFERENCES dim_category(category_key)
);

INSERT INTO dim_subcategory VALUES
(1, 'SUBCAT-01', 'Laptops', 'Portable computers', 1),
(2, 'SUBCAT-02', 'Mice', 'Computer mice', 2),
(3, 'SUBCAT-03', 'Office Chairs', 'Ergonomic office chairs', 3),
(4, 'SUBCAT-04', 'Desk Lamps', 'Desktop lighting', 4),
(5, 'SUBCAT-05', 'Notebooks', 'Writing notebooks', 5);

-- Brand
DROP TABLE IF EXISTS dim_brand CASCADE;
CREATE TABLE dim_brand (
    brand_key INTEGER PRIMARY KEY,
    brand_id VARCHAR(10) NOT NULL UNIQUE,
    brand_name VARCHAR(50) NOT NULL,
    brand_country VARCHAR(50),
    brand_website VARCHAR(100)
);

INSERT INTO dim_brand VALUES
(1, 'BRD-01', 'TechBrand', 'USA', 'www.techbrand.com'),
(2, 'BRD-02', 'ComfortCo', 'USA', 'www.comfortco.com'),
(3, 'BRD-03', 'BrightLight', 'Germany', 'www.brightlight.de'),
(4, 'BRD-04', 'WriteCo', 'UK', 'www.writeco.co.uk');

-- Supplier
DROP TABLE IF EXISTS dim_supplier CASCADE;
CREATE TABLE dim_supplier (
    supplier_key INTEGER PRIMARY KEY,
    supplier_id VARCHAR(10) NOT NULL UNIQUE,
    supplier_name VARCHAR(100) NOT NULL,
    supplier_country VARCHAR(50),
    supplier_contact VARCHAR(100),
    supplier_rating DECIMAL(3,2)
);

INSERT INTO dim_supplier VALUES
(1, 'SUP-01', 'TechCorp Inc', 'USA', 'contact@techcorp.com', 4.5),
(2, 'SUP-02', 'Furniture Mfg Ltd', 'China', 'sales@furnituremfg.cn', 4.2),
(3, 'SUP-03', 'Light Mfg Co', 'Taiwan', 'info@lightmfg.tw', 4.7),
(4, 'SUP-04', 'Paper Mfg Inc', 'India', 'orders@papermfg.in', 4.3);

-- Product (Core dimension - normalized)
DROP TABLE IF EXISTS dim_product_snow CASCADE;
CREATE TABLE dim_product_snow (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL UNIQUE,
    sku VARCHAR(30),
    product_name VARCHAR(100) NOT NULL,
    product_description TEXT,
    
    -- Foreign keys to normalized tables
    subcategory_key INTEGER NOT NULL,
    brand_key INTEGER NOT NULL,
    supplier_key INTEGER NOT NULL,
    
    -- Product-specific attributes
    color VARCHAR(30),
    size VARCHAR(20),
    weight_kg DECIMAL(8,2),
    unit_of_measure VARCHAR(20),
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    product_status VARCHAR(20),
    is_active BOOLEAN,
    launch_date DATE,
    
    FOREIGN KEY (subcategory_key) REFERENCES dim_subcategory(subcategory_key),
    FOREIGN KEY (brand_key) REFERENCES dim_brand(brand_key),
    FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key)
);

INSERT INTO dim_product_snow VALUES
(1, 'PROD-001', 'SKU-001', 'Laptop Pro 15"', 'High-performance laptop', 1, 1, 1, 'Silver', '15"', 2.5, 'Each', 800.00, 1299.99, 'Active', TRUE, '2023-01-01'),
(2, 'PROD-002', 'SKU-002', 'Wireless Mouse', 'Ergonomic wireless mouse', 2, 1, 1, 'Black', 'Standard', 0.15, 'Each', 12.00, 29.99, 'Active', TRUE, '2023-01-01'),
(3, 'PROD-003', 'SKU-003', 'Office Chair', 'Ergonomic office chair', 3, 2, 2, 'Black', 'Standard', 15.0, 'Each', 150.00, 299.99, 'Active', TRUE, '2023-02-01'),
(4, 'PROD-004', 'SKU-004', 'LED Desk Lamp', 'Adjustable LED desk lamp', 4, 3, 3, 'White', 'Standard', 1.2, 'Each', 20.00, 49.99, 'Active', TRUE, '2023-03-01'),
(5, 'PROD-005', 'SKU-005', 'Notebook Set', 'Pack of 5 ruled notebooks', 5, 4, 4, 'Assorted', 'A4', 0.8, 'Pack', 5.00, 12.99, 'Active', TRUE, '2023-01-01');

-- ----------------------------------------------------------------------------
-- Customer Geographic Hierarchy (Normalized)
-- ----------------------------------------------------------------------------

-- Country (Top level)
DROP TABLE IF EXISTS dim_country CASCADE;
CREATE TABLE dim_country (
    country_key INTEGER PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL UNIQUE,
    country_name VARCHAR(50) NOT NULL,
    continent VARCHAR(30),
    currency_code VARCHAR(3)
);

INSERT INTO dim_country VALUES
(1, 'USA', 'United States', 'North America', 'USD'),
(2, 'CAN', 'Canada', 'North America', 'CAD'),
(3, 'GBR', 'United Kingdom', 'Europe', 'GBP');

-- State/Province (Mid level)
DROP TABLE IF EXISTS dim_state CASCADE;
CREATE TABLE dim_state (
    state_key INTEGER PRIMARY KEY,
    state_code VARCHAR(10) NOT NULL,
    state_name VARCHAR(50) NOT NULL,
    country_key INTEGER NOT NULL,
    FOREIGN KEY (country_key) REFERENCES dim_country(country_key)
);

INSERT INTO dim_state VALUES
(1, 'NY', 'New York', 1),
(2, 'CA', 'California', 1),
(3, 'IL', 'Illinois', 1),
(4, 'ON', 'Ontario', 2);

-- City (Bottom level)
DROP TABLE IF EXISTS dim_city CASCADE;
CREATE TABLE dim_city (
    city_key INTEGER PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL,
    state_key INTEGER NOT NULL,
    population INTEGER,
    timezone VARCHAR(50),
    FOREIGN KEY (state_key) REFERENCES dim_state(state_key)
);

INSERT INTO dim_city VALUES
(1, 'New York', 1, 8336817, 'America/New_York'),
(2, 'Los Angeles', 2, 3979576, 'America/Los_Angeles'),
(3, 'Chicago', 3, 2693976, 'America/Chicago'),
(4, 'Toronto', 4, 2930000, 'America/Toronto');

-- Customer (Core dimension - normalized)
DROP TABLE IF EXISTS dim_customer_snow CASCADE;
CREATE TABLE dim_customer_snow (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL UNIQUE,
    
    -- Personal information
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    age_group VARCHAR(20),
    gender VARCHAR(10),
    
    -- Demographics
    marital_status VARCHAR(20),
    education_level VARCHAR(50),
    occupation VARCHAR(50),
    income_bracket VARCHAR(30),
    
    -- Geographic reference
    city_key INTEGER NOT NULL,
    postal_code VARCHAR(20),
    
    -- Customer classification
    customer_type VARCHAR(30),
    customer_segment VARCHAR(30),
    loyalty_tier VARCHAR(20),
    
    -- Status and dates
    account_status VARCHAR(20),
    is_active BOOLEAN,
    registration_date DATE,
    
    FOREIGN KEY (city_key) REFERENCES dim_city(city_key)
);

INSERT INTO dim_customer_snow VALUES
(1, 'CUST-001', 'John', 'Smith', 'John Smith', 'john.smith@email.com', '555-0101', '1985-03-15', '35-44', 'Male', 'Married', 'Bachelor', 'Engineer', '$75K-$100K', 1, '10001', 'Individual', 'VIP', 'Gold', 'Active', TRUE, '2020-01-10'),
(2, 'CUST-002', 'Sarah', 'Johnson', 'Sarah Johnson', 'sarah.j@email.com', '555-0102', '1990-07-22', '25-34', 'Female', 'Single', 'Master', 'Manager', '$100K-$150K', 2, '90001', 'Individual', 'VIP', 'Platinum', 'Active', TRUE, '2020-03-15');

-- ----------------------------------------------------------------------------
-- Store Geographic Hierarchy (Normalized)
-- ----------------------------------------------------------------------------

-- Region (Top level)
DROP TABLE IF EXISTS dim_region CASCADE;
CREATE TABLE dim_region (
    region_key INTEGER PRIMARY KEY,
    region_id VARCHAR(10) NOT NULL UNIQUE,
    region_name VARCHAR(30) NOT NULL,
    regional_manager VARCHAR(100)
);

INSERT INTO dim_region VALUES
(1, 'REG-01', 'Northeast', 'Carol Regional'),
(2, 'REG-02', 'West', 'Frank Regional'),
(3, 'REG-03', 'Midwest', 'Grace Regional');

-- District (Mid level)
DROP TABLE IF EXISTS dim_district CASCADE;
CREATE TABLE dim_district (
    district_key INTEGER PRIMARY KEY,
    district_id VARCHAR(10) NOT NULL UNIQUE,
    district_name VARCHAR(30) NOT NULL,
    region_key INTEGER NOT NULL,
    district_manager VARCHAR(100),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);

INSERT INTO dim_district VALUES
(1, 'DIST-01', 'Manhattan', 1, 'Bob District'),
(2, 'DIST-02', 'LA County', 2, 'Eve District'),
(3, 'DIST-03', 'Cook County', 3, 'Henry District');

-- Store (Core dimension - normalized)
DROP TABLE IF EXISTS dim_store_snow CASCADE;
CREATE TABLE dim_store_snow (
    store_key INTEGER PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL UNIQUE,
    store_number VARCHAR(10),
    store_name VARCHAR(100),
    store_type VARCHAR(30),
    
    -- Geographic reference
    district_key INTEGER NOT NULL,
    city_key INTEGER NOT NULL,
    address VARCHAR(200),
    postal_code VARCHAR(20),
    
    -- Store attributes
    store_size_sqft INTEGER,
    store_manager VARCHAR(100),
    phone VARCHAR(20),
    opening_date DATE,
    is_active BOOLEAN,
    
    FOREIGN KEY (district_key) REFERENCES dim_district(district_key),
    FOREIGN KEY (city_key) REFERENCES dim_city(city_key)
);

INSERT INTO dim_store_snow VALUES
(1, 'STORE-001', 'S001', 'Downtown Flagship', 'Retail', 1, 1, '123 Main St', '10001', 5000, 'Alice Manager', '555-1001', '2018-01-15', TRUE),
(2, 'STORE-002', 'S002', 'Suburban Mall', 'Retail', 2, 2, '456 Oak Ave', '90001', 7500, 'Dan Manager', '555-1002', '2019-03-20', TRUE);

-- ----------------------------------------------------------------------------
-- Date Dimension (Same as star schema - typically not normalized)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_date_snow CASCADE;
CREATE TABLE dim_date_snow (
    date_key INTEGER PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_of_week_name VARCHAR(10),
    week_of_year INTEGER,
    month_number INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

INSERT INTO dim_date_snow VALUES
(20240101, '2024-01-01', 1, 1, 'Monday', 1, 1, 'January', 1, 2024, FALSE, TRUE),
(20240102, '2024-01-02', 2, 2, 'Tuesday', 1, 1, 'January', 1, 2024, FALSE, FALSE),
(20240103, '2024-01-03', 3, 3, 'Wednesday', 1, 1, 'January', 1, 2024, FALSE, FALSE);

-- ============================================================================
-- FACT TABLE (Same structure as star schema)
-- ============================================================================

DROP TABLE IF EXISTS fact_sales_snow CASCADE;
CREATE TABLE fact_sales_snow (
    sale_id BIGINT PRIMARY KEY,
    
    -- Foreign keys to dimensions
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
    total_amount DECIMAL(10,2) NOT NULL,
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    
    -- Transaction attributes
    transaction_type VARCHAR(20),
    payment_method VARCHAR(20),
    
    -- Foreign key constraints
    FOREIGN KEY (date_key) REFERENCES dim_date_snow(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product_snow(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer_snow(customer_key),
    FOREIGN KEY (store_key) REFERENCES dim_store_snow(store_key)
);

-- Sample data
INSERT INTO fact_sales_snow VALUES
(1001, 20240101, 1, 1, 1, 'ORD-001', 'INV-001', 1, 1299.99, 100.00, 104.00, 1303.99, 800.00, 503.99, 'Sale', 'Credit Card'),
(1002, 20240101, 2, 2, 1, 'ORD-002', 'INV-002', 2, 29.99, 0.00, 4.80, 64.78, 24.00, 40.78, 'Sale', 'Cash'),
(1003, 20240102, 3, 1, 2, 'ORD-003', 'INV-003', 1, 299.99, 30.00, 21.60, 291.59, 150.00, 141.59, 'Sale', 'Debit Card');

-- ============================================================================
-- ANALYTICAL QUERIES FOR SNOWFLAKE SCHEMA
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Sales by Complete Product Hierarchy
-- ----------------------------------------------------------------------------
-- Notice: Multiple joins required to traverse the hierarchy
SELECT 
    dept.department_name,
    cat.category_name,
    subcat.subcategory_name,
    brand.brand_name,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit
FROM fact_sales_snow f
JOIN dim_product_snow p ON f.product_key = p.product_key
JOIN dim_subcategory subcat ON p.subcategory_key = subcat.subcategory_key
JOIN dim_category cat ON subcat.category_key = cat.category_key
JOIN dim_department dept ON cat.department_key = dept.department_key
JOIN dim_brand brand ON p.brand_key = brand.brand_key
GROUP BY dept.department_name, cat.category_name, subcat.subcategory_name, brand.brand_name
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 2: Sales by Complete Geographic Hierarchy (Customer)
-- ----------------------------------------------------------------------------
SELECT 
    country.country_name,
    state.state_name,
    city.city_name,
    c.customer_segment,
    COUNT(DISTINCT c.customer_key) as num_customers,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM fact_sales_snow f
JOIN dim_customer_snow c ON f.customer_key = c.customer_key
JOIN dim_city city ON c.city_key = city.city_key
JOIN dim_state state ON city.state_key = state.state_key
JOIN dim_country country ON state.country_key = country.country_key
GROUP BY country.country_name, state.state_name, city.city_name, c.customer_segment
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 3: Sales by Store Geographic Hierarchy
-- ----------------------------------------------------------------------------
SELECT 
    region.region_name,
    district.district_name,
    s.store_name,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    COUNT(DISTINCT f.sale_id) as num_transactions
FROM fact_sales_snow f
JOIN dim_store_snow s ON f.store_key = s.store_key
JOIN dim_district district ON s.district_key = district.district_key
JOIN dim_region region ON district.region_key = region.region_key
GROUP BY region.region_name, district.district_name, s.store_name
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 4: Supplier Performance Analysis
-- ----------------------------------------------------------------------------
SELECT 
    supplier.supplier_name,
    supplier.supplier_country,
    brand.brand_name,
    dept.department_name,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit
FROM fact_sales_snow f
JOIN dim_product_snow p ON f.product_key = p.product_key
JOIN dim_supplier supplier ON p.supplier_key = supplier.supplier_key
JOIN dim_brand brand ON p.brand_key = brand.brand_key
JOIN dim_subcategory subcat ON p.subcategory_key = subcat.subcategory_key
JOIN dim_category cat ON subcat.category_key = cat.category_key
JOIN dim_department dept ON cat.department_key = dept.department_key
GROUP BY supplier.supplier_name, supplier.supplier_country, brand.brand_name, dept.department_name
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 5: Cross-Geography Analysis (Customer City vs Store City)
-- ----------------------------------------------------------------------------
SELECT 
    cust_city.city_name as customer_city,
    store_city.city_name as store_city,
    CASE 
        WHEN cust_city.city_key = store_city.city_key THEN 'Local'
        ELSE 'Cross-City'
    END as transaction_type,
    COUNT(DISTINCT f.sale_id) as num_transactions,
    SUM(f.total_amount) as total_revenue
FROM fact_sales_snow f
JOIN dim_customer_snow c ON f.customer_key = c.customer_key
JOIN dim_city cust_city ON c.city_key = cust_city.city_key
JOIN dim_store_snow s ON f.store_key = s.store_key
JOIN dim_city store_city ON s.city_key = store_city.city_key
GROUP BY cust_city.city_name, store_city.city_name, 
         CASE WHEN cust_city.city_key = store_city.city_key THEN 'Local' ELSE 'Cross-City' END
ORDER BY total_revenue DESC;

-- ============================================================================
-- COMPARISON: STAR VS SNOWFLAKE SCHEMA
-- ============================================================================

-- Star Schema Query (Simple - fewer joins)
/*
SELECT 
    p.department_name,
    p.category_name,
    SUM(f.total_amount) as revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.department_name, p.category_name;
*/

-- Snowflake Schema Query (Complex - more joins)
/*
SELECT 
    dept.department_name,
    cat.category_name,
    SUM(f.total_amount) as revenue
FROM fact_sales_snow f
JOIN dim_product_snow p ON f.product_key = p.product_key
JOIN dim_subcategory subcat ON p.subcategory_key = subcat.subcategory_key
JOIN dim_category cat ON subcat.category_key = cat.category_key
JOIN dim_department dept ON cat.department_key = dept.department_key
GROUP BY dept.department_name, cat.category_name;
*/

-- ============================================================================
-- SNOWFLAKE SCHEMA CHARACTERISTICS
-- ============================================================================
-- ADVANTAGES:
-- 1. Reduced Data Redundancy: Category names stored once
-- 2. Easier Maintenance: Update category in one place
-- 3. Better Data Integrity: Referential integrity enforced
-- 4. Smaller Storage: Less duplication
-- 5. Clearer Hierarchies: Explicit parent-child relationships
--
-- DISADVANTAGES:
-- 1. More Complex Queries: Multiple joins required
-- 2. Slower Query Performance: More joins = more processing
-- 3. Less Intuitive: Harder for business users to understand
-- 4. BI Tool Complexity: Some tools prefer star schemas
-- ============================================================================
