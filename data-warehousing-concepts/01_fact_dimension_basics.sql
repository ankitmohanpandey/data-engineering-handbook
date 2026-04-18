-- ============================================================================
-- Fact & Dimension Tables - Basics
-- ============================================================================
-- This file demonstrates the fundamental concepts of fact and dimension tables
-- in a data warehouse environment.
-- ============================================================================

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================
-- Dimension tables contain descriptive attributes that provide context
-- to the measures in fact tables.

-- ----------------------------------------------------------------------------
-- Date Dimension
-- ----------------------------------------------------------------------------
-- One of the most important dimensions in any data warehouse
-- Provides rich date attributes for time-based analysis

CREATE TABLE date_dim (
    date_key INTEGER PRIMARY KEY,           -- Surrogate key (YYYYMMDD format)
    full_date DATE NOT NULL,                -- Actual date
    day_of_week VARCHAR(10),                -- Monday, Tuesday, etc.
    day_of_month INTEGER,                   -- 1-31
    day_of_year INTEGER,                    -- 1-366
    week_of_year INTEGER,                   -- 1-53
    month_name VARCHAR(10),                 -- January, February, etc.
    month_number INTEGER,                   -- 1-12
    quarter INTEGER,                        -- 1-4
    year INTEGER,                           -- 2024, 2025, etc.
    is_weekend BOOLEAN,                     -- TRUE/FALSE
    is_holiday BOOLEAN,                     -- TRUE/FALSE
    holiday_name VARCHAR(50),               -- Christmas, New Year, etc.
    fiscal_year INTEGER,                    -- For companies with non-calendar fiscal year
    fiscal_quarter INTEGER,                 -- Fiscal quarter
    fiscal_month INTEGER                    -- Fiscal month
);

-- Sample data for date dimension
INSERT INTO date_dim VALUES
(20240101, '2024-01-01', 'Monday', 1, 1, 1, 'January', 1, 1, 2024, FALSE, TRUE, 'New Year Day', 2024, 1, 1),
(20240102, '2024-01-02', 'Tuesday', 2, 2, 1, 'January', 1, 1, 2024, FALSE, FALSE, NULL, 2024, 1, 1),
(20240103, '2024-01-03', 'Wednesday', 3, 3, 1, 'January', 1, 1, 2024, FALSE, FALSE, NULL, 2024, 1, 1),
(20240106, '2024-01-06', 'Saturday', 6, 6, 1, 'January', 1, 1, 2024, TRUE, FALSE, NULL, 2024, 1, 1),
(20240107, '2024-01-07', 'Sunday', 7, 7, 1, 'January', 1, 1, 2024, TRUE, FALSE, NULL, 2024, 1, 1);

-- ----------------------------------------------------------------------------
-- Product Dimension
-- ----------------------------------------------------------------------------
-- Contains all product-related attributes

CREATE TABLE product_dim (
    product_key INTEGER PRIMARY KEY,        -- Surrogate key
    product_id VARCHAR(20) NOT NULL,        -- Business key (from source system)
    product_name VARCHAR(100) NOT NULL,
    product_description TEXT,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50),
    manufacturer VARCHAR(100),
    unit_price DECIMAL(10,2),
    unit_cost DECIMAL(10,2),
    package_type VARCHAR(30),
    weight_kg DECIMAL(8,2),
    is_active BOOLEAN,
    created_date DATE,
    last_updated_date TIMESTAMP
);

-- Sample data for product dimension
INSERT INTO product_dim VALUES
(1, 'PROD-001', 'Laptop Pro 15"', 'High-performance laptop', 'Electronics', 'Computers', 'TechBrand', 'TechCorp', 1299.99, 800.00, 'Box', 2.5, TRUE, '2023-01-15', CURRENT_TIMESTAMP),
(2, 'PROD-002', 'Wireless Mouse', 'Ergonomic wireless mouse', 'Electronics', 'Accessories', 'TechBrand', 'TechCorp', 29.99, 12.00, 'Blister Pack', 0.15, TRUE, '2023-02-20', CURRENT_TIMESTAMP),
(3, 'PROD-003', 'Office Chair', 'Ergonomic office chair', 'Furniture', 'Seating', 'ComfortCo', 'FurnitureMfg', 299.99, 150.00, 'Box', 15.0, TRUE, '2023-03-10', CURRENT_TIMESTAMP),
(4, 'PROD-004', 'Desk Lamp', 'LED desk lamp', 'Electronics', 'Lighting', 'BrightLight', 'LightMfg', 49.99, 20.00, 'Box', 1.2, TRUE, '2023-04-05', CURRENT_TIMESTAMP),
(5, 'PROD-005', 'Notebook Set', 'Pack of 5 notebooks', 'Stationery', 'Paper Products', 'WriteCo', 'PaperMfg', 12.99, 5.00, 'Shrink Wrap', 0.8, TRUE, '2023-05-12', CURRENT_TIMESTAMP);

-- ----------------------------------------------------------------------------
-- Customer Dimension
-- ----------------------------------------------------------------------------
-- Contains customer information and demographics

CREATE TABLE customer_dim (
    customer_key INTEGER PRIMARY KEY,       -- Surrogate key
    customer_id VARCHAR(20) NOT NULL,       -- Business key
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    education_level VARCHAR(50),
    occupation VARCHAR(50),
    income_bracket VARCHAR(30),
    customer_segment VARCHAR(30),           -- VIP, Regular, New, etc.
    registration_date DATE,
    is_active BOOLEAN,
    loyalty_tier VARCHAR(20),               -- Bronze, Silver, Gold, Platinum
    lifetime_value DECIMAL(12,2)
);

-- Sample data for customer dimension
INSERT INTO customer_dim VALUES
(1, 'CUST-001', 'John', 'Smith', 'John Smith', 'john.smith@email.com', '555-0101', '1985-03-15', 'Male', 'Married', 'Bachelor', 'Engineer', '$75K-$100K', 'VIP', '2020-01-10', TRUE, 'Gold', 15000.00),
(2, 'CUST-002', 'Sarah', 'Johnson', 'Sarah Johnson', 'sarah.j@email.com', '555-0102', '1990-07-22', 'Female', 'Single', 'Master', 'Manager', '$100K-$150K', 'VIP', '2020-03-15', TRUE, 'Platinum', 25000.00),
(3, 'CUST-003', 'Mike', 'Williams', 'Mike Williams', 'mike.w@email.com', '555-0103', '1988-11-30', 'Male', 'Married', 'Bachelor', 'Teacher', '$50K-$75K', 'Regular', '2021-06-20', TRUE, 'Silver', 8000.00),
(4, 'CUST-004', 'Emily', 'Brown', 'Emily Brown', 'emily.b@email.com', '555-0104', '1995-02-14', 'Female', 'Single', 'Bachelor', 'Designer', '$50K-$75K', 'Regular', '2022-01-05', TRUE, 'Bronze', 3000.00),
(5, 'CUST-005', 'David', 'Lee', 'David Lee', 'david.l@email.com', '555-0105', '1982-09-08', 'Male', 'Married', 'PhD', 'Scientist', '$150K+', 'VIP', '2019-11-12', TRUE, 'Platinum', 35000.00);

-- ----------------------------------------------------------------------------
-- Store Dimension
-- ----------------------------------------------------------------------------
-- Contains store location and attributes

CREATE TABLE store_dim (
    store_key INTEGER PRIMARY KEY,          -- Surrogate key
    store_id VARCHAR(20) NOT NULL,          -- Business key
    store_name VARCHAR(100),
    store_type VARCHAR(30),                 -- Retail, Warehouse, Online
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    region VARCHAR(30),                     -- North, South, East, West
    district VARCHAR(30),
    store_size_sqft INTEGER,
    opening_date DATE,
    manager_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN
);

-- Sample data for store dimension
INSERT INTO store_dim VALUES
(1, 'STORE-001', 'Downtown Store', 'Retail', '123 Main St', 'New York', 'NY', 'USA', '10001', 'Northeast', 'Manhattan', 5000, '2018-01-15', 'Alice Manager', '555-1001', TRUE),
(2, 'STORE-002', 'Suburban Mall', 'Retail', '456 Oak Ave', 'Los Angeles', 'CA', 'USA', '90001', 'West', 'LA County', 7500, '2019-03-20', 'Bob Manager', '555-1002', TRUE),
(3, 'STORE-003', 'Airport Location', 'Retail', '789 Airport Rd', 'Chicago', 'IL', 'USA', '60601', 'Midwest', 'Cook County', 3000, '2020-06-10', 'Carol Manager', '555-1003', TRUE),
(4, 'STORE-004', 'Online Store', 'Online', 'Virtual', 'Seattle', 'WA', 'USA', '98101', 'Northwest', 'Online', 0, '2017-01-01', 'Dan Manager', '555-1004', TRUE),
(5, 'STORE-005', 'Warehouse Store', 'Warehouse', '321 Industrial Blvd', 'Houston', 'TX', 'USA', '77001', 'South', 'Harris County', 15000, '2018-09-01', 'Eve Manager', '555-1005', TRUE);

-- ============================================================================
-- FACT TABLES
-- ============================================================================
-- Fact tables contain quantitative measures and foreign keys to dimensions

-- ----------------------------------------------------------------------------
-- Sales Fact Table
-- ----------------------------------------------------------------------------
-- Stores individual sales transactions
-- Grain: One row per product per transaction

CREATE TABLE sales_fact (
    sale_id BIGINT PRIMARY KEY,             -- Transaction identifier
    date_key INTEGER NOT NULL,              -- FK to date_dim
    product_key INTEGER NOT NULL,           -- FK to product_dim
    customer_key INTEGER NOT NULL,          -- FK to customer_dim
    store_key INTEGER NOT NULL,             -- FK to store_dim
    
    -- Measures (Additive)
    quantity INTEGER NOT NULL,              -- Number of units sold
    unit_price DECIMAL(10,2) NOT NULL,      -- Price per unit
    discount_amount DECIMAL(10,2) DEFAULT 0,-- Discount applied
    tax_amount DECIMAL(10,2) DEFAULT 0,     -- Tax charged
    total_amount DECIMAL(10,2) NOT NULL,    -- Total sale amount
    cost_amount DECIMAL(10,2),              -- Cost of goods sold
    profit_amount DECIMAL(10,2),            -- Profit (total - cost)
    
    -- Degenerate Dimensions (dimension attributes in fact table)
    order_number VARCHAR(20),               -- Order reference
    transaction_type VARCHAR(20),           -- Sale, Return, Exchange
    payment_method VARCHAR(20),             -- Cash, Credit, Debit
    
    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES date_dim(date_key),
    FOREIGN KEY (product_key) REFERENCES product_dim(product_key),
    FOREIGN KEY (customer_key) REFERENCES customer_dim(customer_key),
    FOREIGN KEY (store_key) REFERENCES store_dim(store_key)
);

-- Sample data for sales fact
INSERT INTO sales_fact VALUES
(1001, 20240101, 1, 1, 1, 1, 1299.99, 100.00, 104.00, 1303.99, 800.00, 503.99, 'ORD-001', 'Sale', 'Credit Card', CURRENT_TIMESTAMP),
(1002, 20240101, 2, 2, 1, 2, 29.99, 0.00, 4.80, 64.78, 24.00, 40.78, 'ORD-002', 'Sale', 'Cash', CURRENT_TIMESTAMP),
(1003, 20240102, 3, 3, 2, 1, 299.99, 30.00, 21.60, 291.59, 150.00, 141.59, 'ORD-003', 'Sale', 'Debit Card', CURRENT_TIMESTAMP),
(1004, 20240102, 4, 1, 3, 1, 49.99, 5.00, 3.60, 48.59, 20.00, 28.59, 'ORD-004', 'Sale', 'Credit Card', CURRENT_TIMESTAMP),
(1005, 20240103, 5, 4, 1, 3, 12.99, 0.00, 1.04, 14.03, 5.00, 9.03, 'ORD-005', 'Sale', 'Cash', CURRENT_TIMESTAMP),
(1006, 20240103, 1, 5, 4, 2, 1299.99, 150.00, 92.00, 1241.99, 800.00, 441.99, 'ORD-006', 'Sale', 'Credit Card', CURRENT_TIMESTAMP),
(1007, 20240106, 2, 2, 2, 1, 29.99, 3.00, 2.16, 29.15, 12.00, 17.15, 'ORD-007', 'Sale', 'Debit Card', CURRENT_TIMESTAMP),
(1008, 20240107, 3, 3, 5, 1, 299.99, 0.00, 24.00, 323.99, 150.00, 173.99, 'ORD-008', 'Sale', 'Cash', CURRENT_TIMESTAMP);

-- ============================================================================
-- ANALYTICAL QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Total Sales by Product Category
-- ----------------------------------------------------------------------------
SELECT 
    p.category,
    p.subcategory,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM sales_fact f
JOIN product_dim p ON f.product_key = p.product_key
GROUP BY p.category, p.subcategory
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 2: Sales by Date and Day of Week
-- ----------------------------------------------------------------------------
SELECT 
    d.day_of_week,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value
FROM sales_fact f
JOIN date_dim d ON f.date_key = d.date_key
GROUP BY d.day_of_week
ORDER BY 
    CASE d.day_of_week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;

-- ----------------------------------------------------------------------------
-- Query 3: Customer Segmentation Analysis
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_key) as customer_count,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.total_amount) as total_revenue,
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT c.customer_key), 2) as revenue_per_customer,
    ROUND(SUM(f.total_amount) / COUNT(DISTINCT f.sale_id), 2) as avg_transaction_value
FROM sales_fact f
JOIN customer_dim c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment, c.loyalty_tier
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 4: Store Performance Comparison
-- ----------------------------------------------------------------------------
SELECT 
    s.store_name,
    s.store_type,
    s.region,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.total_amount), 0), 2) as profit_margin_pct
FROM sales_fact f
JOIN store_dim s ON f.store_key = s.store_key
GROUP BY s.store_name, s.store_type, s.region
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 5: Monthly Sales Trend
-- ----------------------------------------------------------------------------
SELECT 
    d.year,
    d.month_name,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.total_amount), 0), 2) as profit_margin_pct
FROM sales_fact f
JOIN date_dim d ON f.date_key = d.date_key
GROUP BY d.year, d.month_name, d.month_number
ORDER BY d.year, d.month_number;

-- ----------------------------------------------------------------------------
-- Query 6: Top Customers by Revenue
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.full_name,
    c.customer_segment,
    c.loyalty_tier,
    COUNT(DISTINCT f.sale_id) as purchase_count,
    SUM(f.total_amount) as total_spent,
    ROUND(AVG(f.total_amount), 2) as avg_purchase_value,
    MAX(d.full_date) as last_purchase_date
FROM sales_fact f
JOIN customer_dim c ON f.customer_key = c.customer_key
JOIN date_dim d ON f.date_key = d.date_key
GROUP BY c.customer_id, c.full_name, c.customer_segment, c.loyalty_tier
ORDER BY total_spent DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Query 7: Product Performance Analysis
-- ----------------------------------------------------------------------------
SELECT 
    p.product_name,
    p.category,
    p.brand,
    COUNT(DISTINCT f.sale_id) as times_sold,
    SUM(f.quantity) as total_units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    ROUND(AVG(f.total_amount), 2) as avg_sale_amount
FROM sales_fact f
JOIN product_dim p ON f.product_key = p.product_key
GROUP BY p.product_name, p.category, p.brand
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 8: Weekend vs Weekday Sales
-- ----------------------------------------------------------------------------
SELECT 
    CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type,
    COUNT(DISTINCT f.sale_id) as transaction_count,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_transaction_value,
    SUM(f.quantity) as total_units_sold
FROM sales_fact f
JOIN date_dim d ON f.date_key = d.date_key
GROUP BY CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END
ORDER BY day_type;

-- ============================================================================
-- KEY CONCEPTS DEMONSTRATED
-- ============================================================================
-- 1. Surrogate Keys: Auto-generated keys (product_key, customer_key, etc.)
-- 2. Business Keys: Natural keys from source systems (product_id, customer_id)
-- 3. Additive Measures: Can be summed (quantity, amount, profit)
-- 4. Degenerate Dimensions: Dimension attributes in fact table (order_number)
-- 5. Foreign Key Relationships: Fact table references dimension tables
-- 6. Denormalized Dimensions: All attributes in single table for performance
-- 7. Date Dimension: Rich date attributes for time-based analysis
-- 8. Grain: One row per product per transaction in sales_fact
-- ============================================================================
