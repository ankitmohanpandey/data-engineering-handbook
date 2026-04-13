# OpenLineage Quick Reference

> **Quick commands and patterns cheatsheet**

---

## Core Concepts

### Event Types
```python
RunState.START      # Job started
RunState.RUNNING    # Job in progress (optional)
RunState.COMPLETE   # Job completed successfully
RunState.FAIL       # Job failed
RunState.ABORT      # Job aborted
```

### Event Structure
```json
{
  "eventType": "COMPLETE",
  "eventTime": "2024-04-07T10:00:00.000Z",
  "run": {"runId": "uuid"},
  "job": {"namespace": "ns", "name": "job-name"},
  "inputs": [],
  "outputs": [],
  "producer": "producer-name"
}
```

---

## Python Client

### Basic Usage

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from datetime import datetime
import uuid

# Initialize client
client = OpenLineageClient(url="http://localhost:5000")

# Create event
event = RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=str(uuid.uuid4())),
    job=Job(namespace="my-namespace", name="my-job"),
    producer="my-app/1.0.0",
    inputs=[],
    outputs=[]
)

# Emit event
client.emit(event)
```

### With Datasets

```python
from openlineage.client.run import Dataset

event = RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=str(uuid.uuid4())),
    job=Job(namespace="etl", name="customer-pipeline"),
    producer="my-app",
    inputs=[
        Dataset(
            namespace="postgres://db:5432",
            name="public.customers"
        )
    ],
    outputs=[
        Dataset(
            namespace="s3://bucket",
            name="processed/customers.parquet"
        )
    ]
)
```

### With Facets

```python
from openlineage.client.facet import (
    SqlJobFacet,
    SchemaDatasetFacet,
    SchemaField
)

job = Job(
    namespace="etl",
    name="transform",
    facets={
        "sql": SqlJobFacet(query="SELECT * FROM customers")
    }
)

dataset = Dataset(
    namespace="postgres://db:5432",
    name="public.customers",
    facets={
        "schema": SchemaDatasetFacet(
            fields=[
                SchemaField(name="id", type="INTEGER"),
                SchemaField(name="name", type="VARCHAR")
            ]
        )
    }
)
```

---

## Airflow Integration

### Configuration

```ini
# airflow.cfg
[openlineage]
namespace = airflow-prod
transport = {"type": "http", "url": "http://localhost:5000"}
```

```bash
# Environment variables
export OPENLINEAGE_URL=http://localhost:5000
export OPENLINEAGE_NAMESPACE=airflow-prod
```

### Example DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    'customer_etl',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily'
) as dag:
    
    extract = PostgresOperator(
        task_id='extract',
        postgres_conn_id='postgres_default',
        sql="SELECT * FROM customers"
    )
    
    transform = PythonOperator(
        task_id='transform',
        python_callable=lambda: print("Transform")
    )
    
    extract >> transform
```

### Disable for Specific Operators

```ini
# airflow.cfg
[openlineage]
disabled_for_operators = DummyOperator;BashOperator
```

---

## Spark Integration

### Spark Submit

```bash
spark-submit \
  --packages io.openlineage:openlineage-spark:1.0.0 \
  --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener \
  --conf spark.openlineage.transport.type=http \
  --conf spark.openlineage.transport.url=http://localhost:5000 \
  --conf spark.openlineage.namespace=spark-prod \
  my_job.py
```

### PySpark Configuration

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyJob") \
    .config("spark.jars.packages", "io.openlineage:openlineage-spark:1.0.0") \
    .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener") \
    .config("spark.openlineage.transport.type", "http") \
    .config("spark.openlineage.transport.url", "http://localhost:5000") \
    .config("spark.openlineage.namespace", "spark-prod") \
    .getOrCreate()
```

### spark-defaults.conf

```properties
spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener
spark.openlineage.transport.type=http
spark.openlineage.transport.url=http://localhost:5000
spark.openlineage.namespace=spark-prod
```

---

## dbt Integration

### Setup

```bash
# Install
pip install dbt-openlineage

# Configure
export OPENLINEAGE_URL=http://localhost:5000
export OPENLINEAGE_NAMESPACE=dbt-prod
```

### Run dbt

```bash
# Run all models
dbt run

# Run specific model
dbt run --models customers

# Run with full refresh
dbt run --full-refresh
```

---

## Marquez API

### Health Check

```bash
curl http://localhost:5000/api/v1/health
```

### List Namespaces

```bash
curl http://localhost:5000/api/v1/namespaces
```

### Get Namespace

```bash
curl http://localhost:5000/api/v1/namespaces/my-namespace
```

### List Jobs

```bash
curl http://localhost:5000/api/v1/namespaces/my-namespace/jobs
```

### Get Job

```bash
curl http://localhost:5000/api/v1/namespaces/my-namespace/jobs/my-job
```

### List Datasets

```bash
curl http://localhost:5000/api/v1/namespaces/my-namespace/datasets
```

### Get Dataset

```bash
curl "http://localhost:5000/api/v1/namespaces/my-namespace/datasets/my-dataset"
```

### Get Lineage

```bash
curl "http://localhost:5000/api/v1/lineage?nodeId=dataset:my-namespace:my-dataset"
```

### Send Event

```bash
curl -X POST http://localhost:5000/api/v1/lineage \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "COMPLETE",
    "eventTime": "2024-04-07T10:00:00.000Z",
    "run": {"runId": "uuid"},
    "job": {"namespace": "ns", "name": "job"},
    "inputs": [],
    "outputs": [],
    "producer": "test"
  }'
```

---

## Docker Commands

### Start Marquez

```bash
# Using docker-compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f marquez

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Marquez Services

```bash
# Marquez API
curl http://localhost:5000/api/v1/health

# Marquez Web UI
open http://localhost:3000

# PostgreSQL
docker exec -it marquez-postgres psql -U marquez -d marquez
```

---

## Common Patterns

### Job with START and COMPLETE

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from datetime import datetime
import uuid

client = OpenLineageClient(url="http://localhost:5000")
run_id = str(uuid.uuid4())
job = Job(namespace="etl", name="process-data")

# START
client.emit(RunEvent(
    eventType=RunState.START,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=run_id),
    job=job,
    producer="my-app",
    inputs=[],
    outputs=[]
))

# Do work...

# COMPLETE
client.emit(RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=run_id),
    job=job,
    producer="my-app",
    inputs=[],
    outputs=[]
))
```

### Error Handling

```python
try:
    # START
    client.emit(start_event)
    
    # Do work
    result = process_data()
    
    # COMPLETE
    client.emit(complete_event)
    
except Exception as e:
    # FAIL
    client.emit(RunEvent(
        eventType=RunState.FAIL,
        eventTime=datetime.now().isoformat(),
        run=Run(runId=run_id),
        job=job,
        producer="my-app",
        inputs=[],
        outputs=[]
    ))
    raise
```

### Context Manager

```python
from contextlib import contextmanager

@contextmanager
def track_lineage(client, job, run_id):
    # START
    client.emit(create_event(RunState.START, job, run_id))
    
    try:
        yield run_id
        # COMPLETE
        client.emit(create_event(RunState.COMPLETE, job, run_id))
    except Exception as e:
        # FAIL
        client.emit(create_event(RunState.FAIL, job, run_id))
        raise

# Usage
with track_lineage(client, job, run_id) as rid:
    process_data()
```

---

## Facets Reference

### Job Facets

```python
from openlineage.client.facet import (
    SqlJobFacet,
    DocumentationJobFacet,
    SourceCodeLocationJobFacet
)

job_facets = {
    "sql": SqlJobFacet(query="SELECT * FROM table"),
    "documentation": DocumentationJobFacet(
        description="Job description"
    ),
    "sourceCodeLocation": SourceCodeLocationJobFacet(
        type="git",
        url="https://github.com/org/repo",
        path="jobs/my_job.py"
    )
}
```

### Dataset Facets

```python
from openlineage.client.facet import (
    SchemaDatasetFacet,
    SchemaField,
    DataQualityMetricsDatasetFacet,
    OwnershipDatasetFacet
)

dataset_facets = {
    "schema": SchemaDatasetFacet(
        fields=[
            SchemaField(name="id", type="INTEGER"),
            SchemaField(name="name", type="VARCHAR")
        ]
    ),
    "dataQuality": DataQualityMetricsDatasetFacet(
        rowCount=1000,
        bytes=50000
    ),
    "ownership": OwnershipDatasetFacet(
        owners=[{"name": "data-team", "type": "team"}]
    )
}
```

---

## Troubleshooting

### Enable Debug Logging

```bash
export OPENLINEAGE_CLIENT_LOGGING=DEBUG
```

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Connection

```python
from openlineage.client import OpenLineageClient

client = OpenLineageClient(url="http://localhost:5000")
# If no error, connection is OK
```

### Check Marquez

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Check logs
docker-compose logs marquez

# Check database
docker exec -it marquez-postgres psql -U marquez -d marquez
SELECT * FROM runs LIMIT 10;
```

### Verify Events

```bash
# List jobs
curl http://localhost:5000/api/v1/namespaces/my-namespace/jobs

# Get job runs
curl http://localhost:5000/api/v1/namespaces/my-namespace/jobs/my-job/runs
```

---

## Environment Variables

```bash
# OpenLineage Client
OPENLINEAGE_URL=http://localhost:5000
OPENLINEAGE_NAMESPACE=production
OPENLINEAGE_API_KEY=
OPENLINEAGE_CLIENT_LOGGING=INFO

# Marquez
MARQUEZ_PORT=5000
MARQUEZ_ADMIN_PORT=5001
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=marquez
POSTGRES_USER=marquez
POSTGRES_PASSWORD=marquez
```

---

## Useful Links

- [OpenLineage Docs](https://openlineage.io/docs)
- [Marquez Docs](https://marquezproject.github.io/marquez/)
- [Slack Community](http://bit.ly/OpenLineageSlack)
- [GitHub](https://github.com/OpenLineage/OpenLineage)

---

**Keep this handy while working with OpenLineage! 🚀**
