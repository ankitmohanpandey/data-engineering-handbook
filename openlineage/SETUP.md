# OpenLineage Setup Guide

> **Complete installation and configuration guide for OpenLineage**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Marquez Backend Setup](#marquez-backend-setup)
4. [Integration Setup](#integration-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Required**:
- Python 3.7+ (for Python client)
- Docker & Docker Compose (for Marquez backend)
- Java 11+ (for Spark integration)

**Recommended**:
- 4GB+ RAM
- 10GB+ disk space

### Software Requirements

#### 1. Python (Required)

```bash
# Check Python version
python --version  # Should be 3.7+

# Create virtual environment
python -m venv openlineage-env
source openlineage-env/bin/activate  # Linux/Mac
# openlineage-env\Scripts\activate  # Windows
```

#### 2. Docker (Required for Marquez)

```bash
# Install Docker
# macOS
brew install docker docker-compose

# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

## Installation

### Step 1: Install OpenLineage Python Client

```bash
# Activate virtual environment
source openlineage-env/bin/activate

# Install OpenLineage Python client
pip install openlineage-python

# Verify installation
python -c "from openlineage.client import OpenLineageClient; print('OpenLineage installed successfully!')"
```

### Step 2: Install Integration Packages

#### Airflow Integration

```bash
# Install OpenLineage Airflow integration
pip install openlineage-airflow

# Verify
pip list | grep openlineage-airflow
```

#### Spark Integration

```bash
# Download OpenLineage Spark JAR
wget https://repo1.maven.org/maven2/io/openlineage/openlineage-spark/1.0.0/openlineage-spark-1.0.0.jar

# Or add to pom.xml for Maven projects
```

```xml
<dependency>
    <groupId>io.openlineage</groupId>
    <artifactId>openlineage-spark</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### dbt Integration

```bash
# Install dbt-openlineage
pip install dbt-openlineage

# Verify
dbt --version
```

### Step 3: Install Additional Dependencies

```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

---

## Marquez Backend Setup

### Option 1: Docker Compose (Recommended)

#### Quick Start

```bash
# Create directory
mkdir marquez-setup
cd marquez-setup

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/MarquezProject/marquez/main/docker-compose.yml

# Start Marquez
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Services Started**:
- Marquez API: http://localhost:5000
- Marquez Web UI: http://localhost:3000
- PostgreSQL: localhost:5432

#### Custom Docker Compose

```yaml
# docker-compose.yml
version: '3.7'

services:
  postgres:
    image: postgres:14
    container_name: marquez-postgres
    environment:
      POSTGRES_USER: marquez
      POSTGRES_PASSWORD: marquez
      POSTGRES_DB: marquez
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - marquez-network

  marquez:
    image: marquezproject/marquez:latest
    container_name: marquez-api
    environment:
      MARQUEZ_PORT: 5000
      MARQUEZ_ADMIN_PORT: 5001
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: marquez
      POSTGRES_USER: marquez
      POSTGRES_PASSWORD: marquez
    ports:
      - "5000:5000"
      - "5001:5001"
    depends_on:
      - postgres
    networks:
      - marquez-network

  marquez-web:
    image: marquezproject/marquez-web:latest
    container_name: marquez-web
    environment:
      MARQUEZ_HOST: marquez
      MARQUEZ_PORT: 5000
    ports:
      - "3000:3000"
    depends_on:
      - marquez
    networks:
      - marquez-network

volumes:
  postgres-data:

networks:
  marquez-network:
    driver: bridge
```

```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f marquez

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Option 2: Kubernetes Deployment

```yaml
# marquez-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: marquez

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: marquez
spec:
  ports:
    - port: 5432
  selector:
    app: postgres

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: marquez
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_USER
          value: "marquez"
        - name: POSTGRES_PASSWORD
          value: "marquez"
        - name: POSTGRES_DB
          value: "marquez"
        ports:
        - containerPort: 5432

---
apiVersion: v1
kind: Service
metadata:
  name: marquez
  namespace: marquez
spec:
  type: LoadBalancer
  ports:
    - port: 5000
      targetPort: 5000
      name: api
    - port: 3000
      targetPort: 3000
      name: web
  selector:
    app: marquez

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marquez
  namespace: marquez
spec:
  replicas: 2
  selector:
    matchLabels:
      app: marquez
  template:
    metadata:
      labels:
        app: marquez
    spec:
      containers:
      - name: marquez-api
        image: marquezproject/marquez:latest
        env:
        - name: POSTGRES_HOST
          value: "postgres"
        - name: POSTGRES_DB
          value: "marquez"
        - name: POSTGRES_USER
          value: "marquez"
        - name: POSTGRES_PASSWORD
          value: "marquez"
        ports:
        - containerPort: 5000
      - name: marquez-web
        image: marquezproject/marquez-web:latest
        env:
        - name: MARQUEZ_HOST
          value: "localhost"
        - name: MARQUEZ_PORT
          value: "5000"
        ports:
        - containerPort: 3000
```

```bash
# Deploy to Kubernetes
kubectl apply -f marquez-deployment.yaml

# Check status
kubectl get pods -n marquez
kubectl get services -n marquez

# Access Marquez
kubectl port-forward -n marquez service/marquez 5000:5000 3000:3000
```

---

## Integration Setup

### Apache Airflow Integration

#### Method 1: Environment Variables

```bash
# Set environment variables
export OPENLINEAGE_URL=http://localhost:5000
export OPENLINEAGE_NAMESPACE=airflow-production
export OPENLINEAGE_API_KEY=your-api-key  # Optional

# Or add to .env file
cat > .env << EOF
OPENLINEAGE_URL=http://localhost:5000
OPENLINEAGE_NAMESPACE=airflow-production
EOF
```

#### Method 2: airflow.cfg Configuration

```ini
# airflow.cfg
[openlineage]
namespace = airflow-production
transport = {"type": "http", "url": "http://localhost:5000"}
disabled = False
disabled_for_operators = []
```

#### Method 3: Programmatic Configuration

```python
# In your DAG file or airflow_local_settings.py
from openlineage.airflow import conf

conf.namespace = "airflow-production"
conf.transport = {
    "type": "http",
    "url": "http://localhost:5000",
    "timeout": 5.0,
    "verify": True
}
```

#### Verify Airflow Integration

```python
# test_airflow_lineage.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'test_openlineage',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    test_task = BashOperator(
        task_id='test_task',
        bash_command='echo "Testing OpenLineage"'
    )
```

```bash
# Run the DAG
airflow dags test test_openlineage 2024-01-01

# Check Marquez UI
open http://localhost:3000
```

### Apache Spark Integration

#### Spark Submit Configuration

```bash
# spark-submit with OpenLineage
spark-submit \
  --packages io.openlineage:openlineage-spark:1.0.0 \
  --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener \
  --conf spark.openlineage.transport.type=http \
  --conf spark.openlineage.transport.url=http://localhost:5000 \
  --conf spark.openlineage.namespace=spark-production \
  --conf spark.openlineage.appName=my-spark-job \
  my_spark_job.py
```

#### spark-defaults.conf Configuration

```properties
# $SPARK_HOME/conf/spark-defaults.conf
spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener
spark.openlineage.transport.type=http
spark.openlineage.transport.url=http://localhost:5000
spark.openlineage.namespace=spark-production
```

#### PySpark Configuration

```python
# pyspark_config.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("OpenLineageTest") \
    .config("spark.jars.packages", "io.openlineage:openlineage-spark:1.0.0") \
    .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener") \
    .config("spark.openlineage.transport.type", "http") \
    .config("spark.openlineage.transport.url", "http://localhost:5000") \
    .config("spark.openlineage.namespace", "spark-production") \
    .getOrCreate()

# Test job
df = spark.read.csv("data/input.csv")
df.write.parquet("data/output.parquet")
spark.stop()
```

### dbt Integration

#### Setup

```bash
# Install dbt-openlineage
pip install dbt-openlineage

# Configure environment variables
export OPENLINEAGE_URL=http://localhost:5000
export OPENLINEAGE_NAMESPACE=dbt-production
```

#### Run dbt with OpenLineage

```bash
# Run dbt models
dbt run

# Run specific model
dbt run --models customers

# Run with profile
dbt run --profile production
```

#### dbt profiles.yml

```yaml
# ~/.dbt/profiles.yml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: dbt_user
      password: password
      port: 5432
      dbname: analytics
      schema: public
      threads: 4
```

---

## Verification

### Step 1: Test OpenLineage Client

```python
# test_client.py
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from datetime import datetime
import uuid

# Initialize client
client = OpenLineageClient(url="http://localhost:5000")

# Create test event
event = RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now().isoformat(),
    run=Run(runId=str(uuid.uuid4())),
    job=Job(namespace="test", name="verification-job"),
    producer="test-script",
    inputs=[],
    outputs=[]
)

# Emit event
try:
    client.emit(event)
    print("✅ Successfully sent event to Marquez")
except Exception as e:
    print(f"❌ Failed to send event: {e}")
```

```bash
# Run test
python test_client.py
```

### Step 2: Verify Marquez API

```bash
# Check Marquez health
curl http://localhost:5000/api/v1/health

# List namespaces
curl http://localhost:5000/api/v1/namespaces

# Get specific namespace
curl http://localhost:5000/api/v1/namespaces/test

# List jobs in namespace
curl http://localhost:5000/api/v1/namespaces/test/jobs
```

### Step 3: Verify Marquez Web UI

```bash
# Open Marquez Web UI
open http://localhost:3000

# Or
xdg-open http://localhost:3000  # Linux
```

**Check**:
- Namespaces appear
- Jobs are listed
- Lineage graph is visible
- Datasets are tracked

### Step 4: Integration Verification

#### Airflow

```bash
# Check Airflow logs
airflow tasks test test_openlineage test_task 2024-01-01

# Look for OpenLineage messages
grep -i "openlineage" $AIRFLOW_HOME/logs/dag_id=test_openlineage/*
```

#### Spark

```bash
# Check Spark logs
cat spark-application-*.log | grep -i "openlineage"

# Verify in Marquez
curl http://localhost:5000/api/v1/namespaces/spark-production/jobs
```

#### dbt

```bash
# Check dbt logs
cat logs/dbt.log | grep -i "openlineage"

# Verify in Marquez
curl http://localhost:5000/api/v1/namespaces/dbt-production/jobs
```

---

## Troubleshooting

### Issue 1: Marquez Not Starting

**Symptoms**: Docker containers fail to start

**Solution**:
```bash
# Check Docker logs
docker-compose logs marquez
docker-compose logs postgres

# Verify ports are not in use
lsof -i :5000
lsof -i :5432
lsof -i :3000

# Remove old containers and volumes
docker-compose down -v
docker-compose up -d
```

### Issue 2: Cannot Connect to Marquez

**Symptoms**: Connection refused or timeout errors

**Solution**:
```bash
# Verify Marquez is running
curl http://localhost:5000/api/v1/health

# Check network connectivity
docker network ls
docker network inspect marquez_default

# Test from within Docker network
docker run --rm --network marquez_default curlimages/curl:latest \
  curl http://marquez:5000/api/v1/health
```

### Issue 3: Events Not Appearing

**Symptoms**: Events sent but not visible in Marquez

**Solution**:
```bash
# Enable debug logging
export OPENLINEAGE_CLIENT_LOGGING=DEBUG

# Check Marquez API directly
curl -X POST http://localhost:5000/api/v1/lineage \
  -H "Content-Type: application/json" \
  -d @test_event.json

# Verify database
docker exec -it marquez-postgres psql -U marquez -d marquez
SELECT * FROM runs LIMIT 10;
```

### Issue 4: Airflow Integration Not Working

**Symptoms**: No lineage data from Airflow DAGs

**Solution**:
```bash
# Verify plugin is installed
pip list | grep openlineage-airflow

# Check Airflow configuration
airflow config get-value openlineage namespace

# Test with simple DAG
airflow dags test test_openlineage 2024-01-01

# Check Airflow logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log | grep -i openlineage
```

### Issue 5: Spark Integration Not Working

**Symptoms**: No lineage data from Spark jobs

**Solution**:
```bash
# Verify JAR is in classpath
ls -la $SPARK_HOME/jars/ | grep openlineage

# Check Spark configuration
spark-submit --conf spark.openlineage.transport.url=http://localhost:5000 \
  --conf spark.openlineage.debugFacet=true \
  my_job.py

# Enable Spark event logging
--conf spark.eventLog.enabled=true \
--conf spark.eventLog.dir=/tmp/spark-events
```

### Issue 6: Permission Errors

**Symptoms**: Permission denied errors

**Solution**:
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
chmod -R 755 openlineage-env/
chmod 600 .env
```

### Issue 7: Database Connection Issues

**Symptoms**: Cannot connect to PostgreSQL

**Solution**:
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec -it marquez-postgres psql -U marquez -d marquez

# Reset database
docker-compose down -v
docker-compose up -d
```

---

## Configuration Files

### .env Template

```bash
# .env
OPENLINEAGE_URL=http://localhost:5000
OPENLINEAGE_NAMESPACE=production
OPENLINEAGE_API_KEY=

# Marquez Database
POSTGRES_USER=marquez
POSTGRES_PASSWORD=marquez
POSTGRES_DB=marquez
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Marquez API
MARQUEZ_PORT=5000
MARQUEZ_ADMIN_PORT=5001

# Marquez Web
MARQUEZ_WEB_PORT=3000
```

### Python Configuration

```python
# openlineage_config.py
import os
from openlineage.client import OpenLineageClient
from openlineage.client.transport import HttpTransport

def get_client():
    """Get configured OpenLineage client"""
    transport = HttpTransport(
        url=os.getenv('OPENLINEAGE_URL', 'http://localhost:5000'),
        timeout=5.0,
        verify=True,
        auth=None  # Add auth if needed
    )
    
    return OpenLineageClient(
        transport=transport,
        namespace=os.getenv('OPENLINEAGE_NAMESPACE', 'default')
    )
```

---

## Next Steps

1. **Run Examples**: Check `examples/` directory
2. **Integrate with Your Pipeline**: Follow integration guides
3. **Explore Marquez UI**: Visualize lineage graphs
4. **Read Best Practices**: See main README.md

---

## Additional Resources

- [OpenLineage Documentation](https://openlineage.io/docs)
- [Marquez Documentation](https://marquezproject.github.io/marquez/)
- [Slack Community](http://bit.ly/OpenLineageSlack)
- [GitHub Issues](https://github.com/OpenLineage/OpenLineage/issues)

---

**Setup Complete! Ready to track data lineage! 🚀**
