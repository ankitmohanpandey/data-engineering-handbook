-- ============================================================================
-- Slowly Changing Dimensions (SCD) - Type 2 Implementation
-- ============================================================================
-- This file demonstrates SCD Type 2 implementation which maintains full
-- historical tracking by creating new rows for each change.
-- ============================================================================

-- ============================================================================
-- SCD TYPE 2 DIMENSION TABLE
-- ============================================================================

DROP TABLE IF EXISTS dim_customer_scd2 CASCADE;

CREATE TABLE dim_customer_scd2 (
    -- Surrogate key (auto-generated, unique for each version)
    customer_key SERIAL PRIMARY KEY,
    
    -- Business key (natural key from source system - can have duplicates)
    customer_id VARCHAR(20) NOT NULL,
    
    -- Customer attributes (these can change over time)
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    
    -- Address (commonly changes)
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    
    -- Customer classification (can change)
    customer_segment VARCHAR(30),      -- Regular → VIP
    loyalty_tier VARCHAR(20),          -- Bronze → Silver → Gold → Platinum
    credit_rating VARCHAR(20),         -- Good → Excellent
    
    -- SCD Type 2 tracking columns
    effective_date DATE NOT NULL,      -- When this version became active
    end_date DATE NOT NULL,            -- When this version expired (9999-12-31 for current)
    is_current BOOLEAN DEFAULT TRUE,   -- TRUE for current version, FALSE for historical
    
    -- Metadata
    row_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT CURRENT_USER,
    
    -- Ensure business key + effective_date is unique
    UNIQUE (customer_id, effective_date)
);

-- Create indexes for better performance
CREATE INDEX idx_customer_scd2_id ON dim_customer_scd2(customer_id);
CREATE INDEX idx_customer_scd2_current ON dim_customer_scd2(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_customer_scd2_dates ON dim_customer_scd2(effective_date, end_date);

-- ============================================================================
-- INITIAL DATA LOAD
-- ============================================================================

-- Insert initial customer records
INSERT INTO dim_customer_scd2 (
    customer_id, first_name, last_name, email, phone,
    address_line1, city, state, postal_code, country,
    customer_segment, loyalty_tier, credit_rating,
    effective_date, end_date, is_current
) VALUES
('CUST-001', 'John', 'Smith', 'john.smith@email.com', '555-0101',
 '123 Main St', 'New York', 'NY', '10001', 'USA',
 'Regular', 'Bronze', 'Good',
 '2020-01-01', '9999-12-31', TRUE),

('CUST-002', 'Sarah', 'Johnson', 'sarah.j@email.com', '555-0102',
 '456 Oak Ave', 'Los Angeles', 'CA', '90001', 'USA',
 'Regular', 'Bronze', 'Good',
 '2020-03-01', '9999-12-31', TRUE),

('CUST-003', 'Mike', 'Williams', 'mike.w@email.com', '555-0103',
 '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA',
 'Regular', 'Bronze', 'Good',
 '2020-06-01', '9999-12-31', TRUE);

-- ============================================================================
-- SCD TYPE 2 UPDATE SCENARIOS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Scenario 1: Customer moves to new address
-- ----------------------------------------------------------------------------
-- Customer CUST-001 moves from New York to Boston on 2022-01-15

-- Step 1: Close the current record
UPDATE dim_customer_scd2
SET 
    end_date = '2022-01-14',           -- Day before new record starts
    is_current = FALSE,
    row_updated_date = CURRENT_TIMESTAMP
WHERE customer_id = 'CUST-001' 
  AND is_current = TRUE;

-- Step 2: Insert new record with updated address
INSERT INTO dim_customer_scd2 (
    customer_id, first_name, last_name, email, phone,
    address_line1, city, state, postal_code, country,
    customer_segment, loyalty_tier, credit_rating,
    effective_date, end_date, is_current
) VALUES
('CUST-001', 'John', 'Smith', 'john.smith@email.com', '555-0101',
 '999 Harbor Blvd', 'Boston', 'MA', '02101', 'USA',  -- New address
 'Regular', 'Bronze', 'Good',
 '2022-01-15', '9999-12-31', TRUE);

-- ----------------------------------------------------------------------------
-- Scenario 2: Customer upgraded to VIP with new loyalty tier
-- ----------------------------------------------------------------------------
-- Customer CUST-002 upgraded to VIP segment and Gold tier on 2023-06-01

UPDATE dim_customer_scd2
SET 
    end_date = '2023-05-31',
    is_current = FALSE,
    row_updated_date = CURRENT_TIMESTAMP
WHERE customer_id = 'CUST-002' 
  AND is_current = TRUE;

INSERT INTO dim_customer_scd2 (
    customer_id, first_name, last_name, email, phone,
    address_line1, city, state, postal_code, country,
    customer_segment, loyalty_tier, credit_rating,
    effective_date, end_date, is_current
) VALUES
('CUST-002', 'Sarah', 'Johnson', 'sarah.j@email.com', '555-0102',
 '456 Oak Ave', 'Los Angeles', 'CA', '90001', 'USA',
 'VIP', 'Gold', 'Excellent',  -- Upgraded segment, tier, and rating
 '2023-06-01', '9999-12-31', TRUE);

-- ----------------------------------------------------------------------------
-- Scenario 3: Multiple changes over time for same customer
-- ----------------------------------------------------------------------------
-- Customer CUST-001 gets another upgrade on 2024-01-01

UPDATE dim_customer_scd2
SET 
    end_date = '2023-12-31',
    is_current = FALSE,
    row_updated_date = CURRENT_TIMESTAMP
WHERE customer_id = 'CUST-001' 
  AND is_current = TRUE;

INSERT INTO dim_customer_scd2 (
    customer_id, first_name, last_name, email, phone,
    address_line1, city, state, postal_code, country,
    customer_segment, loyalty_tier, credit_rating,
    effective_date, end_date, is_current
) VALUES
('CUST-001', 'John', 'Smith', 'john.smith@email.com', '555-0101',
 '999 Harbor Blvd', 'Boston', 'MA', '02101', 'USA',
 'VIP', 'Platinum', 'Excellent',  -- Upgraded to VIP and Platinum
 '2024-01-01', '9999-12-31', TRUE);

-- ============================================================================
-- STORED PROCEDURE FOR SCD TYPE 2 UPDATES
-- ============================================================================

CREATE OR REPLACE FUNCTION update_customer_scd2(
    p_customer_id VARCHAR(20),
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_email VARCHAR(100),
    p_phone VARCHAR(20),
    p_address_line1 VARCHAR(100),
    p_city VARCHAR(50),
    p_state VARCHAR(50),
    p_postal_code VARCHAR(20),
    p_country VARCHAR(50),
    p_customer_segment VARCHAR(30),
    p_loyalty_tier VARCHAR(20),
    p_credit_rating VARCHAR(20),
    p_effective_date DATE
) RETURNS VOID AS $$
DECLARE
    v_changed BOOLEAN := FALSE;
    v_current_record RECORD;
BEGIN
    -- Get current record
    SELECT * INTO v_current_record
    FROM dim_customer_scd2
    WHERE customer_id = p_customer_id
      AND is_current = TRUE;
    
    -- Check if record exists
    IF NOT FOUND THEN
        -- Insert new customer
        INSERT INTO dim_customer_scd2 (
            customer_id, first_name, last_name, email, phone,
            address_line1, city, state, postal_code, country,
            customer_segment, loyalty_tier, credit_rating,
            effective_date, end_date, is_current
        ) VALUES (
            p_customer_id, p_first_name, p_last_name, p_email, p_phone,
            p_address_line1, p_city, p_state, p_postal_code, p_country,
            p_customer_segment, p_loyalty_tier, p_credit_rating,
            p_effective_date, '9999-12-31', TRUE
        );
        RETURN;
    END IF;
    
    -- Check if any SCD Type 2 attributes changed
    IF v_current_record.address_line1 != p_address_line1 OR
       v_current_record.city != p_city OR
       v_current_record.state != p_state OR
       v_current_record.postal_code != p_postal_code OR
       v_current_record.customer_segment != p_customer_segment OR
       v_current_record.loyalty_tier != p_loyalty_tier OR
       v_current_record.credit_rating != p_credit_rating THEN
        v_changed := TRUE;
    END IF;
    
    -- If changed, create new version
    IF v_changed THEN
        -- Close current record
        UPDATE dim_customer_scd2
        SET 
            end_date = p_effective_date - INTERVAL '1 day',
            is_current = FALSE,
            row_updated_date = CURRENT_TIMESTAMP
        WHERE customer_id = p_customer_id
          AND is_current = TRUE;
        
        -- Insert new version
        INSERT INTO dim_customer_scd2 (
            customer_id, first_name, last_name, email, phone,
            address_line1, city, state, postal_code, country,
            customer_segment, loyalty_tier, credit_rating,
            effective_date, end_date, is_current
        ) VALUES (
            p_customer_id, p_first_name, p_last_name, p_email, p_phone,
            p_address_line1, p_city, p_state, p_postal_code, p_country,
            p_customer_segment, p_loyalty_tier, p_credit_rating,
            p_effective_date, '9999-12-31', TRUE
        );
    ELSE
        -- No SCD Type 2 change, update Type 1 attributes (email, phone, name)
        UPDATE dim_customer_scd2
        SET 
            first_name = p_first_name,
            last_name = p_last_name,
            email = p_email,
            phone = p_phone,
            row_updated_date = CURRENT_TIMESTAMP
        WHERE customer_id = p_customer_id
          AND is_current = TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Example usage of the stored procedure
-- SELECT update_customer_scd2('CUST-003', 'Mike', 'Williams', 'mike.new@email.com', '555-0103',
--     '321 New St', 'Seattle', 'WA', '98101', 'USA',
--     'VIP', 'Silver', 'Good', '2024-02-01');

-- ============================================================================
-- FACT TABLE WITH SCD TYPE 2 DIMENSION
-- ============================================================================

DROP TABLE IF EXISTS fact_sales_scd2 CASCADE;

CREATE TABLE fact_sales_scd2 (
    sale_id BIGINT PRIMARY KEY,
    sale_date DATE NOT NULL,
    
    -- Foreign key to SCD Type 2 dimension (surrogate key, not business key)
    customer_key INTEGER NOT NULL,
    
    -- Other dimensions
    product_id VARCHAR(20),
    store_id VARCHAR(20),
    
    -- Measures
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer_scd2(customer_key)
);

-- Sample sales data
INSERT INTO fact_sales_scd2 VALUES
(1, '2021-06-15', 1, 'PROD-001', 'STORE-001', 2, 100.00, 200.00),  -- customer_key 1 (CUST-001, NY address)
(2, '2022-03-20', 2, 'PROD-002', 'STORE-001', 1, 50.00, 50.00),    -- customer_key 2 (CUST-001, Boston address)
(3, '2023-08-10', 4, 'PROD-003', 'STORE-002', 3, 75.00, 225.00),   -- customer_key 4 (CUST-002, VIP status)
(4, '2024-01-15', 5, 'PROD-001', 'STORE-001', 1, 100.00, 100.00);  -- customer_key 5 (CUST-001, Platinum tier)

-- ============================================================================
-- ANALYTICAL QUERIES WITH SCD TYPE 2
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Get current state of all customers
-- ----------------------------------------------------------------------------
SELECT 
    customer_id,
    first_name,
    last_name,
    city,
    state,
    customer_segment,
    loyalty_tier,
    effective_date,
    end_date
FROM dim_customer_scd2
WHERE is_current = TRUE
ORDER BY customer_id;

-- ----------------------------------------------------------------------------
-- Query 2: Get complete history for a specific customer
-- ----------------------------------------------------------------------------
SELECT 
    customer_key,
    customer_id,
    city,
    state,
    customer_segment,
    loyalty_tier,
    credit_rating,
    effective_date,
    end_date,
    is_current,
    CASE 
        WHEN is_current THEN 'Current'
        ELSE 'Historical'
    END as status
FROM dim_customer_scd2
WHERE customer_id = 'CUST-001'
ORDER BY effective_date;

-- ----------------------------------------------------------------------------
-- Query 3: Point-in-time query (customer state on specific date)
-- ----------------------------------------------------------------------------
-- What was the customer's address on 2021-12-31?
SELECT 
    customer_id,
    first_name,
    last_name,
    address_line1,
    city,
    state,
    customer_segment,
    loyalty_tier
FROM dim_customer_scd2
WHERE customer_id = 'CUST-001'
  AND '2021-12-31' BETWEEN effective_date AND end_date;

-- ----------------------------------------------------------------------------
-- Query 4: Sales analysis with historical customer attributes
-- ----------------------------------------------------------------------------
-- This joins sales to the correct version of customer dimension
SELECT 
    f.sale_date,
    c.customer_id,
    c.customer_segment,
    c.loyalty_tier,
    c.city,
    c.state,
    f.total_amount,
    c.effective_date as customer_version_start,
    c.end_date as customer_version_end
FROM fact_sales_scd2 f
JOIN dim_customer_scd2 c ON f.customer_key = c.customer_key
ORDER BY f.sale_date;

-- ----------------------------------------------------------------------------
-- Query 5: Track customer segment changes over time
-- ----------------------------------------------------------------------------
SELECT 
    customer_id,
    customer_segment,
    loyalty_tier,
    effective_date,
    end_date,
    (end_date - effective_date) as days_in_segment
FROM dim_customer_scd2
WHERE customer_id = 'CUST-001'
ORDER BY effective_date;

-- ----------------------------------------------------------------------------
-- Query 6: Count customers by segment at different points in time
-- ----------------------------------------------------------------------------
-- Customers by segment as of 2022-01-01
SELECT 
    customer_segment,
    COUNT(*) as customer_count
FROM dim_customer_scd2
WHERE '2022-01-01' BETWEEN effective_date AND end_date
GROUP BY customer_segment;

-- Customers by segment as of 2024-01-01
SELECT 
    customer_segment,
    COUNT(*) as customer_count
FROM dim_customer_scd2
WHERE '2024-01-01' BETWEEN effective_date AND end_date
GROUP BY customer_segment;

-- ----------------------------------------------------------------------------
-- Query 7: Customer upgrade analysis
-- ----------------------------------------------------------------------------
-- Find customers who upgraded from Regular to VIP
WITH customer_changes AS (
    SELECT 
        customer_id,
        customer_segment,
        loyalty_tier,
        effective_date,
        LAG(customer_segment) OVER (PARTITION BY customer_id ORDER BY effective_date) as prev_segment,
        LAG(loyalty_tier) OVER (PARTITION BY customer_id ORDER BY effective_date) as prev_tier
    FROM dim_customer_scd2
)
SELECT 
    customer_id,
    prev_segment,
    customer_segment,
    prev_tier,
    loyalty_tier,
    effective_date as upgrade_date
FROM customer_changes
WHERE prev_segment = 'Regular' 
  AND customer_segment = 'VIP';

-- ----------------------------------------------------------------------------
-- Query 8: Sales by customer segment (using historical data)
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    c.loyalty_tier,
    COUNT(DISTINCT f.sale_id) as num_sales,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_sale_amount
FROM fact_sales_scd2 f
JOIN dim_customer_scd2 c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment, c.loyalty_tier
ORDER BY total_revenue DESC;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Find orphaned records (should not exist)
-- ----------------------------------------------------------------------------
SELECT customer_id, COUNT(*) as version_count
FROM dim_customer_scd2
WHERE is_current = TRUE
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- ----------------------------------------------------------------------------
-- Find gaps in date ranges (data quality check)
-- ----------------------------------------------------------------------------
WITH date_gaps AS (
    SELECT 
        customer_id,
        end_date,
        LEAD(effective_date) OVER (PARTITION BY customer_id ORDER BY effective_date) as next_start_date
    FROM dim_customer_scd2
)
SELECT 
    customer_id,
    end_date,
    next_start_date,
    (next_start_date - end_date - 1) as gap_days
FROM date_gaps
WHERE next_start_date IS NOT NULL
  AND next_start_date != end_date + 1;

-- ============================================================================
-- SCD TYPE 2 BEST PRACTICES
-- ============================================================================
-- 1. Always use surrogate keys (customer_key) in fact tables, not business keys
-- 2. Use effective_date and end_date for temporal queries
-- 3. Use is_current flag for quick access to current records
-- 4. Set end_date to '9999-12-31' for current records
-- 5. Create indexes on customer_id, is_current, and date columns
-- 6. Implement stored procedures for consistent updates
-- 7. Regular data quality checks for gaps and overlaps
-- 8. Document which attributes are Type 1 vs Type 2
-- ============================================================================
