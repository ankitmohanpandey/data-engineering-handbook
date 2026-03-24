# Apache Airflow Complete Guide

## Table of Contents
1. [What is Apache Airflow?](#what-is-apache-airflow)
2. [Core Concepts](#core-concepts)
3. [Architecture Overview](#architecture-overview)
4. [Setup & Installation](#setup--installation)
5. [Operators Guide](#operators-guide)
6. [DAG Examples](#dag-examples)
7. [Advanced Features](#advanced-features)
8. [Real-World Use Cases](#real-world-use-cases)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## What is Apache Airflow?

**Apache Airflow** is an open-source platform to programmatically author, schedule, and monitor workflows.

### Key Points
- **Workflow Orchestration**: Manage complex data pipelines
- **Python-Based**: Define workflows as code (DAGs)
- **Scheduling**: Built-in scheduler for automated execution
- **Monitoring**: Rich UI for tracking pipeline execution
- **Extensible**: 200+ built-in operators and custom operators

### Why Use Apache Airflow?
✅ **Dynamic Pipeline Generation**: Create pipelines programmatically  
✅ **Dependency Management**: Define task dependencies easily  
✅ **Scalability**: Run thousands of tasks in parallel  
✅ **Rich UI**: Monitor and troubleshoot visually  
✅ **Extensible**: Custom operators, sensors, hooks  
✅ **Active Community**: Large ecosystem of integrations  

### Airflow vs Other Tools

| Feature | Airflow | Cron | Luigi | Prefect |
|---------|---------|------|-------|---------|
| Dynamic DAGs | ✅ | ❌ | ❌ | ✅ |
| Web UI | ✅ | ❌ | ✅ | ✅ |
| Backfilling | ✅ | ❌ | ❌ | ✅ |
| Task Dependencies | ✅ | ❌ | ✅ | ✅ |
| Retry Logic | ✅ | ❌ | ✅ | ✅ |
| Distributed | ✅ | ❌ | ❌ | ✅ |

---

## Core Concepts

### 1. DAG (Directed Acyclic Graph)
A collection of tasks with dependencies, representing your workflow.

**Key Properties:**
- **Directed**: Tasks flow in one direction
- **Acyclic**: No circular dependencies
- **Graph**: Tasks connected by dependencies

```python
from airflow import DAG
from datetime import datetime

dag = DAG(
    dag_id='my_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
)
```

### 2. Operator
A task template that defines what work to do.

**Common Operators:**
- **BashOperator**: Execute bash commands
- **PythonOperator**: Execute Python functions
- **EmailOperator**: Send emails
- **SQLOperator**: Execute SQL queries
- **SensorOperator**: Wait for conditions

```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag
)
```

### 3. Task
An instance of an operator in a DAG.

```python
# Task is created when operator is instantiated
task1 = BashOperator(task_id='task1', bash_command='echo "Hello"', dag=dag)
task2 = BashOperator(task_id='task2', bash_command='echo "World"', dag=dag)

# Define dependency
task1 >> task2  # task1 runs before task2
```

### 4. Task Instance
A specific run of a task for a particular execution date.

### 5. DAG Run
An execution of a DAG for a specific date/time.

### 6. Executor
Determines how tasks are executed.

**Executor Types:**
- **SequentialExecutor**: One task at a time (default, development)
- **LocalExecutor**: Multiple tasks in parallel (single machine)
- **CeleryExecutor**: Distributed execution (production)
- **KubernetesExecutor**: Tasks as Kubernetes pods
- **DaskExecutor**: Dask cluster execution

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Airflow Architecture                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Web UI     │         │  Scheduler   │         │   Workers    │
│              │         │              │         │              │
│ - Monitor    │         │ - Trigger    │         │ - Execute    │
│ - Trigger    │◄────────┤   DAG Runs   │────────►│   Tasks      │
│ - Logs       │         │ - Monitor    │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │                        │                         │
       └────────────────────────┼─────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Metadata Database  │
                    │   (PostgreSQL/MySQL) │
                    │                      │
                    │ - DAG definitions    │
                    │ - Task states        │
                    │ - Execution history  │
                    └──────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   DAG Directory      │
                    │   (Python files)     │
                    └──────────────────────┘
```

### Components Explained

**1. Web Server**
- User interface for monitoring and management
- Trigger DAG runs manually
- View logs and task status
- Manage connections and variables

**2. Scheduler**
- Monitors DAG directory for new/updated DAGs
- Triggers task instances based on schedule
- Manages task dependencies
- Submits tasks to executor

**3. Executor**
- Determines how tasks run
- Manages task queues
- Distributes work to workers

**4. Workers**
- Execute tasks assigned by executor
- Report task status back
- Can be scaled horizontally

**5. Metadata Database**
- Stores all Airflow state
- DAG definitions and runs
- Task instances and logs
- Connections and variables

**6. DAG Directory**
- Contains Python files defining DAGs
- Scanned by scheduler periodically
- Changes detected automatically

---

## Setup & Installation

See detailed guide in SETUP.md

### Quick Start

```bash
# Install Airflow
pip install apache-airflow==2.8.0

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start web server
airflow webserver --port 8080

# Start scheduler (in another terminal)
airflow scheduler
```

---

## Operators Guide

### 1. BashOperator
Execute bash commands.

```python
from airflow.operators.bash import BashOperator

bash_task = BashOperator(
    task_id='run_script',
    bash_command='bash /path/to/script.sh',
    dag=dag
)
```

### 2. PythonOperator
Execute Python functions.

```python
from airflow.operators.python import PythonOperator

def my_function(**context):
    print("Hello from Python!")
    return "Success"

python_task = PythonOperator(
    task_id='run_python',
    python_callable=my_function,
    dag=dag
)
```

### 3. EmailOperator
Send emails.

```python
from airflow.operators.email import EmailOperator

email_task = EmailOperator(
    task_id='send_email',
    to='user@example.com',
    subject='Pipeline Complete',
    html_content='<p>Your pipeline finished successfully!</p>',
    dag=dag
)
```

### 4. SQLOperators

**PostgresOperator:**
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

sql_task = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='postgres_default',
    sql='SELECT * FROM users WHERE created_date = {{ ds }}',
    dag=dag
)
```

**MySQLOperator, BigQueryOperator, etc.** - Similar pattern

### 5. Sensors
Wait for conditions to be met.

**FileSensor:**
```python
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Timeout after 1 hour
    dag=dag
)
```

**S3KeySensor:**
```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

s3_sensor = S3KeySensor(
    task_id='wait_for_s3_file',
    bucket_name='my-bucket',
    bucket_key='data/file.csv',
    aws_conn_id='aws_default',
    dag=dag
)
```

### 6. Transfer Operators

**S3ToGCSOperator:**
```python
from airflow.providers.google.cloud.transfers.s3_to_gcs import S3ToGCSOperator

transfer = S3ToGCSOperator(
    task_id='s3_to_gcs',
    bucket='s3-bucket',
    prefix='data/',
    dest_gcs='gs://gcs-bucket/data/',
    dag=dag
)
```

### 7. Cloud Operators

**DataprocSubmitJobOperator:**
```python
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator

spark_job = DataprocSubmitJobOperator(
    task_id='submit_spark_job',
    job={
        'reference': {'project_id': 'my-project'},
        'placement': {'cluster_name': 'my-cluster'},
        'pyspark_job': {'main_python_file_uri': 'gs://bucket/job.py'}
    },
    region='us-central1',
    dag=dag
)
```

---

## DAG Examples

See example files:
- `01_basic_dag.py` - Simple DAG structure
- `02_task_dependencies.py` - Complex dependencies
- `03_dynamic_dags.py` - Generate DAGs programmatically
- `04_taskflow_api.py` - Modern TaskFlow API
- `05_sensors_example.py` - Using sensors
- `06_branching.py` - Conditional execution
- `07_subdags.py` - Reusable DAG components
- `08_xcoms.py` - Task communication

---

## Advanced Features

### 1. XComs (Cross-Communication)
Share data between tasks.

```python
# Push data
def push_function(**context):
    context['ti'].xcom_push(key='my_key', value='my_value')

# Pull data
def pull_function(**context):
    value = context['ti'].xcom_pull(key='my_key', task_ids='push_task')
    print(f"Received: {value}")
```

### 2. TaskFlow API (Airflow 2.0+)
Modern, Pythonic way to define DAGs.

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule_interval='@daily')
def my_pipeline():
    
    @task
    def extract():
        return {'data': [1, 2, 3]}
    
    @task
    def transform(data):
        return {'processed': [x * 2 for x in data['data']]}
    
    @task
    def load(data):
        print(f"Loading: {data}")
    
    load(transform(extract()))

dag = my_pipeline()
```

### 3. Branching
Conditional task execution.

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    if context['execution_date'].day % 2 == 0:
        return 'even_day_task'
    return 'odd_day_task'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
    dag=dag
)
```

### 4. Trigger Rules
Control when tasks execute.

```python
task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    trigger_rule='all_success',  # Default
    # Options: all_success, all_failed, all_done, one_success, one_failed, none_failed
    dag=dag
)
```

### 5. Pools
Limit concurrent task execution.

```python
# Create pool via UI or CLI
# airflow pools set my_pool 5 "My pool description"

task = PythonOperator(
    task_id='pooled_task',
    python_callable=my_function,
    pool='my_pool',
    dag=dag
)
```

### 6. Variables
Store configuration values.

```python
from airflow.models import Variable

# Set variable via UI or CLI
# airflow variables set my_var my_value

value = Variable.get('my_var')
```

### 7. Connections
Store external system credentials.

```python
# Create connection via UI or CLI
# Use in operators
sql_task = PostgresOperator(
    task_id='query',
    postgres_conn_id='my_postgres_conn',
    sql='SELECT * FROM table',
    dag=dag
)
```

---

## Real-World Use Cases

### 1. ETL Pipeline
Extract data from source, transform, load to warehouse.

```python
extract >> transform >> load >> send_notification
```

### 2. Data Quality Checks
Validate data before processing.

```python
check_data_quality >> [process_data, send_alert]
```

### 3. ML Pipeline
Train and deploy models.

```python
fetch_data >> prepare_data >> train_model >> evaluate_model >> deploy_model
```

### 4. Report Generation
Generate and distribute reports.

```python
query_data >> generate_report >> send_email
```

### 5. Multi-Cloud Orchestration
Coordinate tasks across cloud providers.

```python
s3_sensor >> process_on_gcp >> write_to_azure
```

---

## Best Practices

### DAG Design

✅ **Idempotent Tasks**: Tasks should produce same result when re-run  
✅ **Atomic Tasks**: Each task should do one thing well  
✅ **Avoid Top-Level Code**: Don't execute code at DAG parse time  
✅ **Use Templates**: Leverage Jinja templating for dynamic values  
✅ **Set Timeouts**: Prevent tasks from running indefinitely  

❌ **Don't**: Put heavy computation in DAG file  
❌ **Don't**: Use dynamic start_date  
❌ **Don't**: Create too many small tasks (overhead)  

### Performance

✅ **Use Pools**: Limit concurrent resource usage  
✅ **Optimize Parsing**: Keep DAG files lightweight  
✅ **Use Sensors Wisely**: Set appropriate poke_interval  
✅ **Parallelism**: Configure appropriate parallelism settings  
✅ **Database**: Use PostgreSQL or MySQL (not SQLite) in production  

### Monitoring

✅ **Set SLAs**: Define expected completion times  
✅ **Email Alerts**: Configure failure notifications  
✅ **Logging**: Use proper logging in tasks  
✅ **Metrics**: Monitor DAG and task duration  

### Security

✅ **Use Connections**: Store credentials securely  
✅ **RBAC**: Enable role-based access control  
✅ **Secrets Backend**: Use external secrets manager  
✅ **Audit Logs**: Enable and monitor audit logs  

---

## Troubleshooting

### Common Issues

#### 1. DAG Not Appearing in UI

**Causes:**
- Syntax error in DAG file
- DAG file not in dags_folder
- Scheduler not running

**Solutions:**
```bash
# Check for errors
python /path/to/dag_file.py

# Verify DAG folder
airflow config get-value core dags_folder

# Restart scheduler
airflow scheduler
```

#### 2. Tasks Stuck in Queued

**Causes:**
- No workers available
- Executor misconfigured
- Pool slots exhausted

**Solutions:**
- Check executor configuration
- Increase pool slots
- Scale workers

#### 3. Task Failures

**Causes:**
- Code errors
- Resource unavailable
- Timeout

**Solutions:**
- Check task logs in UI
- Increase timeout
- Add retry logic

#### 4. Slow DAG Parsing

**Causes:**
- Heavy computation in DAG file
- Too many DAG files
- Complex imports

**Solutions:**
- Move computation to tasks
- Optimize imports
- Increase parsing interval

---

## Scheduling

### Schedule Intervals

```python
# Cron expressions
schedule_interval='0 0 * * *'  # Daily at midnight
schedule_interval='0 */6 * * *'  # Every 6 hours
schedule_interval='0 0 * * 1'  # Every Monday

# Presets
schedule_interval='@daily'     # 0 0 * * *
schedule_interval='@hourly'    # 0 * * * *
schedule_interval='@weekly'    # 0 0 * * 0
schedule_interval='@monthly'   # 0 0 1 * *
schedule_interval='@yearly'    # 0 0 1 1 *

# Timedelta
from datetime import timedelta
schedule_interval=timedelta(hours=2)

# Manual only
schedule_interval=None
```

### Execution Date vs Run Date

- **execution_date**: Logical date (start of period)
- **run_date**: Actual execution time

Example: DAG scheduled daily at midnight
- execution_date: 2024-01-01 00:00:00
- run_date: 2024-01-02 00:00:00 (runs after period ends)

---

## Resources

- **Official Docs**: https://airflow.apache.org/docs/
- **GitHub**: https://github.com/apache/airflow
- **Slack**: https://apache-airflow.slack.com/
- **Stack Overflow**: Tag `airflow`
- **Awesome Airflow**: https://github.com/jghoman/awesome-apache-airflow

---

## Next Steps

1. Complete setup (see SETUP.md)
2. Run basic DAG examples (01-08)
3. Explore operators
4. Build your first pipeline
5. Deploy to production

---

**Remember**: Airflow orchestrates workflows - it's not a data processing engine itself!
