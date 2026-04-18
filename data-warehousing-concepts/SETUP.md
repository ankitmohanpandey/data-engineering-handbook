# Data Warehousing Concepts - Setup Guide

## Overview

This guide will help you set up a local environment to practice data warehousing concepts using PostgreSQL.

---

## Prerequisites

- Basic SQL knowledge
- Command line familiarity
- Text editor or SQL client

---

## Option 1: PostgreSQL (Recommended for Learning)

### Installation

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Run installer and follow prompts
- Default port: 5432

### Initial Setup

```bash
# Create a database for practice
createdb warehouse_practice

# Connect to database
psql warehouse_practice

# Or specify user
psql -U postgres -d warehouse_practice
```

### Verify Installation

```sql
-- Check PostgreSQL version
SELECT version();

-- Should show PostgreSQL 15.x or higher
```

---

## Option 2: Docker (Isolated Environment)

### Install Docker

- Download from https://www.docker.com/products/docker-desktop

### Run PostgreSQL Container

```bash
# Pull PostgreSQL image
docker pull postgres:15

# Run container
docker run --name warehouse-postgres \
  -e POSTGRES_PASSWORD=warehouse123 \
  -e POSTGRES_DB=warehouse_practice \
  -p 5432:5432 \
  -d postgres:15

# Connect to database
docker exec -it warehouse-postgres psql -U postgres -d warehouse_practice
```

### Stop/Start Container

```bash
# Stop
docker stop warehouse-postgres

# Start
docker start warehouse-postgres

# Remove
docker rm -f warehouse-postgres
```

---

## Option 3: Cloud Database (BigQuery, Snowflake)

### Google BigQuery

1. Create Google Cloud account (free tier available)
2. Create a project
3. Enable BigQuery API
4. Use BigQuery console or CLI

**Example:**
```sql
-- BigQuery syntax
CREATE TABLE `project.dataset.sales_fact`
PARTITION BY DATE(order_date)
AS SELECT * FROM source_table;
```

### Snowflake

1. Sign up for free trial at https://signup.snowflake.com/
2. Create warehouse and database
3. Use Snowflake web interface or SnowSQL

---

## SQL Client Tools

### Command Line
- **psql**: Built-in PostgreSQL client
- **SnowSQL**: Snowflake CLI

### GUI Tools
- **DBeaver**: Free, multi-database (Recommended)
  - Download: https://dbeaver.io/
  - Supports PostgreSQL, MySQL, BigQuery, Snowflake
  
- **pgAdmin**: PostgreSQL-specific
  - Download: https://www.pgadmin.org/
  
- **DataGrip**: JetBrains (Paid)
  - Download: https://www.jetbrains.com/datagrip/

### VS Code Extensions
- **PostgreSQL** by Chris Kolkman
- **SQLTools** by Matheus Teixeira

---

## Running the Examples

### Step 1: Create Database

```bash
# PostgreSQL
createdb warehouse_practice
psql warehouse_practice
```

### Step 2: Run Example Files

```bash
# Method 1: From command line
psql warehouse_practice < 01_fact_dimension_basics.sql

# Method 2: Inside psql
\i 01_fact_dimension_basics.sql

# Method 3: Copy and paste into SQL client
```

### Step 3: Execute in Order

1. `01_fact_dimension_basics.sql` - Basic concepts
2. `02_star_schema_example.sql` - Star schema
3. `03_snowflake_schema_example.sql` - Snowflake schema
4. `04_scd_type2_implementation.sql` - SCD Type 2
5. `05_partitioning_examples.sql` - Partitioning

---

## Recommended Learning Path

### Week 1: Fundamentals
- [ ] Read README.md sections 1-3
- [ ] Run `01_fact_dimension_basics.sql`
- [ ] Understand fact vs dimension tables
- [ ] Practice writing basic analytical queries

### Week 2: Schema Design
- [ ] Read README.md sections 4-5
- [ ] Run `02_star_schema_example.sql`
- [ ] Run `03_snowflake_schema_example.sql`
- [ ] Compare query performance
- [ ] Design your own schema

### Week 3: Historical Tracking
- [ ] Read README.md section 6
- [ ] Run `04_scd_type2_implementation.sql`
- [ ] Practice SCD updates
- [ ] Write point-in-time queries

### Week 4: Performance
- [ ] Read README.md section 7
- [ ] Run `05_partitioning_examples.sql`
- [ ] Experiment with different strategies
- [ ] Analyze query plans

---

## Practice Exercises

### Exercise 1: Build a Simple Data Warehouse

Create a data warehouse for a library system:

**Dimensions:**
- Book (title, author, genre, publisher)
- Member (name, membership type, join date)
- Date (standard date dimension)
- Library Branch (location, size)

**Fact:**
- Checkouts (date, book, member, branch, duration)

### Exercise 2: Implement SCD Type 2

Track member address changes:
- Initial address
- Address change after 6 months
- Query historical checkouts with correct address

### Exercise 3: Partition Large Table

Create a partitioned fact table:
- Monthly partitions for 2 years
- Insert sample data
- Verify partition pruning

---

## Common Issues & Solutions

### Issue 1: Permission Denied

```bash
# PostgreSQL
sudo -u postgres psql

# Or create superuser
CREATE USER myuser WITH SUPERUSER PASSWORD 'mypassword';
```

### Issue 2: Port Already in Use

```bash
# Check what's using port 5432
lsof -i :5432

# Change PostgreSQL port
# Edit postgresql.conf: port = 5433
```

### Issue 3: Connection Refused

```bash
# Check if PostgreSQL is running
# macOS
brew services list

# Linux
sudo systemctl status postgresql

# Start if not running
brew services start postgresql@15
# or
sudo systemctl start postgresql
```

### Issue 4: Partition Already Exists

```sql
-- Drop existing partition first
DROP TABLE IF EXISTS sales_2024_01 CASCADE;

-- Then recreate
CREATE TABLE sales_2024_01 PARTITION OF sales_fact
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

---

## Performance Testing

### Generate Sample Data

```sql
-- Create function to generate random sales data
CREATE OR REPLACE FUNCTION generate_sales_data(num_rows INTEGER)
RETURNS VOID AS $$
BEGIN
    INSERT INTO fact_sales
    SELECT 
        generate_series(1, num_rows),
        20240101 + (random() * 365)::INTEGER,
        (random() * 100)::INTEGER + 1,
        (random() * 1000)::INTEGER + 1,
        (random() * 10)::INTEGER + 1,
        (random() * 10)::INTEGER + 1,
        (random() * 100)::DECIMAL(10,2),
        (random() * 1000)::DECIMAL(10,2);
END;
$$ LANGUAGE plpgsql;

-- Generate 1 million rows
SELECT generate_sales_data(1000000);
```

### Analyze Query Performance

```sql
-- Enable timing
\timing on

-- Analyze query plan
EXPLAIN ANALYZE
SELECT 
    p.category,
    SUM(f.total_amount)
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category;
```

---

## Additional Resources

### Documentation
- **PostgreSQL**: https://www.postgresql.org/docs/
- **BigQuery**: https://cloud.google.com/bigquery/docs
- **Snowflake**: https://docs.snowflake.com/

### Books
- "The Data Warehouse Toolkit" by Ralph Kimball
- "Building the Data Warehouse" by Bill Inmon
- "Star Schema: The Complete Reference" by Christopher Adamson

### Online Courses
- Coursera: Data Warehousing for Business Intelligence
- Udemy: Complete Data Warehousing Course
- LinkedIn Learning: Data Warehouse Fundamentals

### Communities
- Stack Overflow: Tag `data-warehouse`
- Reddit: r/dataengineering
- DBT Community: https://www.getdbt.com/community/

---

## Next Steps

1. Complete setup using your preferred option
2. Run all example files in order
3. Review QUICK_REFERENCE.md for syntax
4. Practice with exercises
5. Build your own data warehouse project

---

## Troubleshooting

If you encounter issues:

1. Check PostgreSQL is running: `pg_isready`
2. Verify connection: `psql -l`
3. Check logs: `/usr/local/var/log/postgresql@15.log` (macOS)
4. Consult documentation for your specific database

---

**Happy Learning!** 🎓
