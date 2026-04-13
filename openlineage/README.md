# OpenLineage Learning Repository

> **Comprehensive guide to understanding and implementing OpenLineage for data lineage tracking**

OpenLineage is an open framework for data lineage collection and analysis. It provides a standard way to collect lineage metadata from data pipelines, making it easier to understand data flows, track dependencies, and ensure data quality across your data ecosystem.

---

## 📚 Table of Contents

1. [What is OpenLineage?](#what-is-openlineage)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Integration Examples](#integration-examples)
6. [Learning Path](#learning-path)
7. [Official Documentation](#official-documentation)
8. [Best Practices](#best-practices)

---

## What is OpenLineage?

**OpenLineage** is an open standard for metadata and lineage collection designed to instrument jobs as they are running. It defines a standard API for capturing lineage metadata from data pipelines and provides integrations with popular data processing frameworks.

### Key Features

- 🔄 **Standardized Metadata** - Common format for lineage data across tools
- 🔌 **Framework Integrations** - Built-in support for Airflow, Spark, dbt, Flink, and more
- 📊 **Real-time Tracking** - Capture lineage as jobs execute
- 🌐 **Open Source** - Community-driven, vendor-neutral standard
- 🔍 **Observability** - Track data quality, dependencies, and pipeline health

### Use Cases

1. **Data Discovery** - Understand what data exists and where it comes from
2. **Impact Analysis** - Identify downstream dependencies before making changes
3. **Root Cause Analysis** - Trace data quality issues to their source
4. **Compliance** - Track data lineage for regulatory requirements
5. **Data Governance** - Maintain visibility into data flows across the organization

---

## Core Concepts

### 1. Run Event

A **Run Event** represents a point-in-time state of a data processing job.

```json
{
  "eventType": "START",
  "eventTime": "2024-04-07T10:00:00.000Z",
  "run": {
    "runId": "d46e465b-d358-4d32-83d4-df660ff614dd"
  },
  "job": {
    "namespace": "my-scheduler",
    "name": "my-job"
  },
  "inputs": [],
  "outputs": [],
  "producer": "https://github.com/OpenLineage/OpenLineage/tree/0.0.1/client/python"
}
```

**Event Types**:
- `START` - Job execution begins
- `RUNNING` - Job is in progress (optional)
- `COMPLETE` - Job finished successfully
- `FAIL` - Job failed
- `ABORT` - Job was aborted

### 2. Job

A **Job** is a process that consumes and/or produces datasets.

```python
{
  "namespace": "my-scheduler",
  "name": "my-job",
  "facets": {
    "documentation": {
      "description": "Processes customer data"
    },
    "sourceCodeLocation": {
      "type": "git",
      "url": "https://github.com/org/repo",
      "path": "jobs/customer_etl.py"
    }
  }
}
```

### 3. Dataset

A **Dataset** is a collection of data (table, file, topic, etc.).

```python
{
  "namespace": "postgres://mydb:5432",
  "name": "public.customers",
  "facets": {
    "schema": {
      "fields": [
        {"name": "id", "type": "INTEGER"},
        {"name": "name", "type": "VARCHAR"},
        {"name": "email", "type": "VARCHAR"}
      ]
    },
    "dataSource": {
      "name": "postgres",
      "uri": "postgres://mydb:5432"
    }
  }
}
```

### 4. Facets

**Facets** are extensible metadata properties attached to runs, jobs, and datasets.

**Common Facets**:
- `schema` - Dataset schema information
- `dataQuality` - Data quality metrics
- `columnLineage` - Column-level lineage
- `sql` - SQL query text
- `ownership` - Data ownership information
- `documentation` - Human-readable documentation

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Processing Jobs                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Airflow │  │  Spark   │  │   dbt    │  │  Flink   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                   │
│                   OpenLineage Client                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP/Kafka
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  OpenLineage Backend                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Marquez (Reference Implementation)       │  │
│  │                                                        │  │
│  │  ┌──────────────┐         ┌──────────────┐          │  │
│  │  │   API Server │◄────────┤  PostgreSQL  │          │  │
│  │  └──────┬───────┘         └──────────────┘          │  │
│  │         │                                             │  │
│  │         ▼                                             │  │
│  │  ┌──────────────┐                                    │  │
│  │  │   Web UI     │                                    │  │
│  │  └──────────────┘                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Lineage Consumers & Analytics                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Dashboards│ │  Alerts  │  │  Reports │  │  APIs    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **OpenLineage Client** - Collects and emits lineage events
2. **Transport Layer** - HTTP, Kafka, or custom transport
3. **Backend** - Stores and serves lineage data (Marquez, custom, etc.)
4. **Consumers** - Applications that use lineage data

---

## Quick Start

### Installation

```bash
# Install OpenLineage Python client
pip install openlineage-python

# Install Airflow integration
pip install openlineage-airflow

# Install Spark integration
pip install openlineage-spark
```

### Basic Example - Python Client

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from openlineage.client.facet import SqlJobFacet
from datetime import datetime
import uuid

# Initialize client
client = OpenLineageClient(url="http://localhost:5000")

# Create run ID
run_id = str(uuid.uuid4())

# Define job
job = Job(
    namespace="my-scheduler",
    name="customer-etl"
)

# Create START event
start_event = RunEvent(
    eventType=RunState.START,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=run_id),
    job=job,
    producer="my-producer",
    inputs=[],
    outputs=[]
)

# Emit START event
client.emit(start_event)

# ... do work ...

# Create COMPLETE event
complete_event = RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=run_id),
    job=job,
    producer="my-producer",
    inputs=[
        {
            "namespace": "postgres://mydb:5432",
            "name": "public.customers"
        }
    ],
    outputs=[
        {
            "namespace": "s3://my-bucket",
            "name": "processed/customers.parquet"
        }
    ]
)

# Emit COMPLETE event
client.emit(complete_event)
```

---

## Integration Examples

### 1. Apache Airflow Integration

#### Setup

```python
# airflow.cfg or environment variables
[openlineage]
namespace = my-airflow-instance
transport = {"type": "http", "url": "http://marquez:5000"}
```

#### Example DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

def process_data(**context):
    """Process customer data"""
    # Your processing logic
    print("Processing data...")

with DAG(
    'customer_etl',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    extract = PostgresOperator(
        task_id='extract_customers',
        postgres_conn_id='postgres_default',
        sql="""
            SELECT * FROM customers 
            WHERE updated_at >= '{{ ds }}'
        """
    )
    
    transform = PythonOperator(
        task_id='transform_data',
        python_callable=process_data
    )
    
    extract >> transform
```

**OpenLineage automatically captures**:
- Task dependencies
- SQL queries
- Input/output datasets
- Execution times
- Task states

### 2. Apache Spark Integration

#### Setup

```bash
# Add OpenLineage Spark listener
spark-submit \
  --packages io.openlineage:openlineage-spark:1.0.0 \
  --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener \
  --conf spark.openlineage.transport.type=http \
  --conf spark.openlineage.transport.url=http://marquez:5000 \
  --conf spark.openlineage.namespace=spark-jobs \
  my_spark_job.py
```

#### Example Spark Job

```python
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("CustomerETL") \
    .getOrCreate()

# Read data
customers_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/mydb") \
    .option("dbtable", "customers") \
    .load()

# Transform
processed_df = customers_df \
    .filter(customers_df.status == "active") \
    .select("id", "name", "email")

# Write data
processed_df.write \
    .mode("overwrite") \
    .parquet("s3://my-bucket/processed/customers")

spark.stop()
```

**OpenLineage automatically captures**:
- Input datasets (JDBC table)
- Output datasets (S3 parquet)
- Spark job details
- Data transformations
- Column-level lineage

### 3. dbt Integration

#### Setup

```yaml
# profiles.yml
my_project:
  target: prod
  outputs:
    prod:
      type: postgres
      host: localhost
      user: dbt_user
      pass: password
      port: 5432
      dbname: analytics
      schema: public
      threads: 4
```

#### Run dbt with OpenLineage

```bash
# Install dbt-openlineage
pip install dbt-openlineage

# Run dbt with OpenLineage
OPENLINEAGE_URL=http://marquez:5000 \
OPENLINEAGE_NAMESPACE=dbt-project \
dbt run
```

#### Example dbt Model

```sql
-- models/customers_summary.sql
{{ config(
    materialized='table',
    tags=['daily']
) }}

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.order_amount) as total_spent
FROM {{ source('raw', 'customers') }} c
LEFT JOIN {{ source('raw', 'orders') }} o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
```

**OpenLineage automatically captures**:
- Source tables
- Target tables
- SQL transformations
- dbt model metadata
- Column lineage

### 4. Custom Python Application

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import (
    RunEvent, RunState, Run, Job, Dataset
)
from openlineage.client.facet import (
    SqlJobFacet, SchemaDatasetFacet, SchemaField
)
from datetime import datetime
import uuid

class LineageTracker:
    def __init__(self, url="http://localhost:5000"):
        self.client = OpenLineageClient(url=url)
        self.namespace = "my-app"
    
    def track_job(self, job_name, inputs, outputs, sql_query=None):
        """Track a data processing job"""
        run_id = str(uuid.uuid4())
        
        # Create job with SQL facet
        job_facets = {}
        if sql_query:
            job_facets["sql"] = SqlJobFacet(query=sql_query)
        
        job = Job(
            namespace=self.namespace,
            name=job_name,
            facets=job_facets
        )
        
        # START event
        self.client.emit(RunEvent(
            eventType=RunState.START,
            eventTime=datetime.now().isoformat(),
            run=Run(runId=run_id),
            job=job,
            producer="my-app/1.0.0",
            inputs=[],
            outputs=[]
        ))
        
        try:
            # Execute job logic here
            yield run_id
            
            # COMPLETE event with datasets
            self.client.emit(RunEvent(
                eventType=RunState.COMPLETE,
                eventTime=datetime.now().isoformat(),
                run=Run(runId=run_id),
                job=job,
                producer="my-app/1.0.0",
                inputs=[
                    Dataset(
                        namespace=inp["namespace"],
                        name=inp["name"],
                        facets={
                            "schema": SchemaDatasetFacet(
                                fields=[
                                    SchemaField(name=f["name"], type=f["type"])
                                    for f in inp.get("schema", [])
                                ]
                            )
                        }
                    )
                    for inp in inputs
                ],
                outputs=[
                    Dataset(
                        namespace=out["namespace"],
                        name=out["name"]
                    )
                    for out in outputs
                ]
            ))
        except Exception as e:
            # FAIL event
            self.client.emit(RunEvent(
                eventType=RunState.FAIL,
                eventTime=datetime.now().isoformat(),
                run=Run(runId=run_id),
                job=job,
                producer="my-app/1.0.0",
                inputs=[],
                outputs=[]
            ))
            raise

# Usage
tracker = LineageTracker()

with tracker.track_job(
    job_name="customer-aggregation",
    inputs=[{
        "namespace": "postgres://mydb:5432",
        "name": "public.customers",
        "schema": [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR"}
        ]
    }],
    outputs=[{
        "namespace": "s3://my-bucket",
        "name": "analytics/customer_summary.parquet"
    }],
    sql_query="SELECT id, COUNT(*) FROM customers GROUP BY id"
) as run_id:
    print(f"Processing with run_id: {run_id}")
    # Your processing logic
```

---

## Learning Path

### Week 1-2: Foundations
**Goal**: Understand OpenLineage concepts and architecture

**Topics**:
- What is data lineage and why it matters
- OpenLineage specification overview
- Core concepts: Jobs, Runs, Datasets, Facets
- Event model and lifecycle

**Resources**:
- **[OpenLineage Specification](https://openlineage.io/docs/spec/overview)** - Official spec
- **[Getting Started Guide](https://openlineage.io/docs/getting-started)** - Quick start
- **[OpenLineage Blog](https://openlineage.io/blog)** - Use cases and updates

**Hands-on**:
- Install OpenLineage Python client
- Send basic START/COMPLETE events
- Explore event structure with JSON

### Week 3-4: Integration Basics
**Goal**: Integrate OpenLineage with one framework

**Topics**:
- Airflow integration setup
- Automatic vs manual instrumentation
- Transport options (HTTP, Kafka, Console)
- Marquez backend setup

**Resources**:
- **[Airflow Integration](https://openlineage.io/docs/integrations/airflow)** - Airflow guide
- **[Marquez Quickstart](https://marquezproject.github.io/marquez/quickstart.html)** - Backend setup
- **[Transport Configuration](https://openlineage.io/docs/client/python#transports)** - Transport options

**Hands-on**:
- Set up Marquez with Docker
- Configure Airflow with OpenLineage
- Run sample DAG and view lineage in Marquez UI

### Week 5-6: Advanced Integration
**Goal**: Implement multiple integrations and custom facets

**Topics**:
- Spark integration
- dbt integration
- Custom facets creation
- Column-level lineage

**Resources**:
- **[Spark Integration](https://openlineage.io/docs/integrations/spark)** - Spark guide
- **[dbt Integration](https://openlineage.io/docs/integrations/dbt)** - dbt guide
- **[Custom Facets](https://openlineage.io/docs/spec/facets)** - Facet specification

**Hands-on**:
- Integrate Spark job with OpenLineage
- Track dbt models
- Create custom facets for business metadata

### Week 7-8: Production & Best Practices
**Goal**: Deploy OpenLineage in production

**Topics**:
- Scaling considerations
- Security and authentication
- Monitoring and troubleshooting
- Data governance workflows

**Resources**:
- **[Production Guide](https://openlineage.io/docs/guides/production)** - Production tips
- **[Best Practices](https://openlineage.io/docs/guides/best-practices)** - Guidelines
- **[Community Forum](https://github.com/OpenLineage/OpenLineage/discussions)** - Q&A

**Hands-on**:
- Set up production Marquez deployment
- Implement authentication
- Create lineage dashboards
- Build impact analysis workflows

---

## Official Documentation

### Core Documentation
- **[OpenLineage Official Site](https://openlineage.io/)** - Main website
- **[OpenLineage Specification](https://openlineage.io/docs/spec/overview)** - Complete spec
- **[GitHub Repository](https://github.com/OpenLineage/OpenLineage)** - Source code
- **[API Documentation](https://openlineage.io/apidocs/openapi/)** - API reference

### Integration Guides
- **[Apache Airflow](https://openlineage.io/docs/integrations/airflow)** - Airflow integration
- **[Apache Spark](https://openlineage.io/docs/integrations/spark)** - Spark integration
- **[dbt](https://openlineage.io/docs/integrations/dbt)** - dbt integration
- **[Apache Flink](https://openlineage.io/docs/integrations/flink)** - Flink integration
- **[Dagster](https://openlineage.io/docs/integrations/dagster)** - Dagster integration
- **[Great Expectations](https://openlineage.io/docs/integrations/great-expectations)** - Data quality integration

### Client Libraries
- **[Python Client](https://openlineage.io/docs/client/python)** - Python SDK
- **[Java Client](https://openlineage.io/docs/client/java)** - Java SDK
- **[Go Client](https://github.com/OpenLineage/OpenLineage/tree/main/client/go)** - Go SDK

### Marquez (Reference Backend)
- **[Marquez Documentation](https://marquezproject.github.io/marquez/)** - Complete docs
- **[Marquez GitHub](https://github.com/MarquezProject/marquez)** - Source code
- **[Marquez API](https://marquezproject.github.io/marquez/openapi.html)** - API reference
- **[Marquez Quickstart](https://marquezproject.github.io/marquez/quickstart.html)** - Getting started

### Community & Support
- **[Slack Community](http://bit.ly/OpenLineageSlack)** - Join discussions
- **[GitHub Discussions](https://github.com/OpenLineage/OpenLineage/discussions)** - Q&A forum
- **[Monthly Meetings](https://openlineage.io/community)** - Community calls
- **[Blog](https://openlineage.io/blog)** - Updates and use cases

### Research & Papers
- **[OpenLineage: An Open Standard for Lineage Collection](https://openlineage.io/blog/openlineage-an-open-standard/)** - Introduction paper
- **[Data Lineage at Scale](https://openlineage.io/blog/data-lineage-at-scale/)** - Scaling considerations
- **[Column-Level Lineage](https://openlineage.io/blog/column-level-lineage/)** - Fine-grained tracking

### Videos & Tutorials
- **[OpenLineage YouTube Channel](https://www.youtube.com/@openlineage)** - Video tutorials
- **[Getting Started with OpenLineage](https://www.youtube.com/watch?v=anlV5Er_BpM)** - Intro video
- **[Airflow + OpenLineage Demo](https://www.youtube.com/watch?v=3FfZcqRU_oY)** - Integration demo

### Tools & Ecosystem
- **[OpenLineage Proxy](https://github.com/OpenLineage/OpenLineage/tree/main/proxy)** - HTTP proxy
- **[OpenLineage SQL Parser](https://github.com/OpenLineage/OpenLineage/tree/main/integration/sql)** - SQL parsing
- **[Marquez Airflow Plugin](https://github.com/MarquezProject/marquez/tree/main/integrations/airflow)** - Legacy plugin

---

## Best Practices

### 1. Namespace Design

```python
# Good: Hierarchical namespaces
namespace = "production.us-east-1.airflow"
namespace = "staging.eu-west-1.spark"

# Bad: Flat namespaces
namespace = "airflow"
namespace = "spark"
```

### 2. Dataset Naming

```python
# Good: Fully qualified names
dataset = {
    "namespace": "postgres://prod-db:5432",
    "name": "analytics.customers"
}

# Good: Include partition info
dataset = {
    "namespace": "s3://my-bucket",
    "name": "data/events/date=2024-04-07"
}

# Bad: Ambiguous names
dataset = {
    "namespace": "database",
    "name": "customers"
}
```

### 3. Facet Usage

```python
# Add meaningful facets
job_facets = {
    "sql": SqlJobFacet(query="SELECT * FROM customers"),
    "documentation": DocumentationJobFacet(
        description="Daily customer aggregation"
    ),
    "sourceCodeLocation": SourceCodeLocationJobFacet(
        type="git",
        url="https://github.com/org/repo",
        path="jobs/customer_etl.py"
    )
}

dataset_facets = {
    "schema": SchemaDatasetFacet(fields=[...]),
    "dataQuality": DataQualityMetricsDatasetFacet(
        rowCount=1000,
        bytes=50000,
        columnMetrics={...}
    ),
    "ownership": OwnershipDatasetFacet(
        owners=[{"name": "data-team", "type": "team"}]
    )
}
```

### 4. Error Handling

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState

def process_with_lineage():
    client = OpenLineageClient(url="http://marquez:5000")
    run_id = str(uuid.uuid4())
    
    try:
        # Emit START
        client.emit(create_event(RunState.START, run_id))
        
        # Do work
        result = do_work()
        
        # Emit COMPLETE
        client.emit(create_event(RunState.COMPLETE, run_id))
        return result
        
    except Exception as e:
        # Emit FAIL with error info
        client.emit(create_event(
            RunState.FAIL,
            run_id,
            error_message=str(e)
        ))
        raise
```

### 5. Performance Optimization

```python
# Use async transport for high-throughput jobs
from openlineage.client.transport import HttpTransport

transport = HttpTransport(
    url="http://marquez:5000",
    timeout=5.0,
    verify=True,
    session=None  # Reuse session for better performance
)

client = OpenLineageClient(transport=transport)

# Batch events when possible
events = []
for job in jobs:
    events.append(create_event(job))

# Send in batch
for event in events:
    client.emit(event)
```

### 6. Security

```python
# Use authentication
from openlineage.client.transport import HttpTransport

transport = HttpTransport(
    url="https://marquez.company.com",
    auth=("username", "password"),  # Basic auth
    # OR
    headers={"Authorization": "Bearer <token>"}  # Token auth
)

# Use HTTPS in production
client = OpenLineageClient(
    url="https://marquez.company.com",  # Not http://
    transport=transport
)

# Don't log sensitive data
dataset_facets = {
    "schema": SchemaDatasetFacet(
        fields=[
            SchemaField(name="id", type="INTEGER"),
            SchemaField(name="email", type="VARCHAR"),
            # Don't include PII in descriptions
        ]
    )
}
```

---

## Troubleshooting

### Common Issues

#### 1. Events Not Appearing in Marquez

**Check**:
```bash
# Verify Marquez is running
curl http://localhost:5000/api/v1/namespaces

# Check client configuration
echo $OPENLINEAGE_URL
echo $OPENLINEAGE_NAMESPACE

# Enable debug logging
export OPENLINEAGE_CLIENT_LOGGING=DEBUG
```

#### 2. Airflow Integration Not Working

**Check**:
```python
# Verify plugin is installed
pip list | grep openlineage-airflow

# Check Airflow configuration
airflow config get-value openlineage namespace

# Test connection
from openlineage.client import OpenLineageClient
client = OpenLineageClient(url="http://marquez:5000")
# Try sending a test event
```

#### 3. Missing Lineage Data

**Verify**:
- Job namespace matches expected value
- Dataset namespaces are correct
- Events are being emitted (check logs)
- Transport is configured correctly

---

## Next Steps

1. **[Setup Guide](SETUP.md)** - Install and configure OpenLineage
2. **[Quick Reference](QUICK_REFERENCE.md)** - Commands and patterns
3. **[Examples Directory](examples/)** - Working code samples
4. **[Integration Guides](integrations/)** - Framework-specific guides

---

## Repository Structure

```
openlineage/
├── README.md                    # This file
├── SETUP.md                     # Installation guide
├── QUICK_REFERENCE.md          # Quick reference
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── examples/                   # Code examples
│   ├── 01_basic/              # Basic examples
│   ├── 02_airflow/            # Airflow integration
│   ├── 03_spark/              # Spark integration
│   ├── 04_dbt/                # dbt integration
│   └── 05_custom/             # Custom implementations
├── integrations/              # Integration guides
│   ├── airflow/
│   ├── spark/
│   ├── dbt/
│   └── flink/
└── docker/                    # Docker compose files
    ├── marquez/
    └── full-stack/
```

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add examples or documentation
4. Submit a pull request

---

## License

This learning repository is provided as-is for educational purposes.

OpenLineage is licensed under Apache License 2.0.

---

**Happy Learning! 🚀**

*Master data lineage tracking with OpenLineage*
