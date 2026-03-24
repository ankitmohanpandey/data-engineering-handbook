# Apache Airflow Quick Reference Card

## 🚀 Quick Start

```bash
# Install
pip install apache-airflow==2.8.0

# Initialize
airflow db init

# Create user
airflow users create --username admin --password admin --role Admin --email admin@example.com --firstname Admin --lastname User

# Start
airflow webserver --port 8080  # Terminal 1
airflow scheduler               # Terminal 2
```

Access: http://localhost:8080

---

## 📋 Core Concepts

| Concept | Description |
|---------|-------------|
| **DAG** | Directed Acyclic Graph - your workflow |
| **Operator** | Task template (what to do) |
| **Task** | Instance of operator |
| **Task Instance** | Specific run of a task |
| **DAG Run** | Execution of a DAG |
| **Executor** | How tasks are executed |

---

## 🔧 Basic DAG Structure

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    dag_id='my_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
)

task = BashOperator(
    task_id='my_task',
    bash_command='echo "Hello"',
    dag=dag
)
```

---

## 📅 Schedule Intervals

```python
# Cron expressions
schedule_interval='0 0 * * *'    # Daily at midnight
schedule_interval='0 */6 * * *'  # Every 6 hours
schedule_interval='0 0 * * 1'    # Every Monday

# Presets
schedule_interval='@once'        # Run once
schedule_interval='@hourly'      # Every hour
schedule_interval='@daily'       # Every day
schedule_interval='@weekly'      # Every week
schedule_interval='@monthly'     # Every month
schedule_interval='@yearly'      # Every year

# Timedelta
from datetime import timedelta
schedule_interval=timedelta(hours=2)

# Manual only
schedule_interval=None
```

---

## 🎯 Common Operators

### BashOperator
```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='run_script',
    bash_command='bash script.sh',
    dag=dag
)
```

### PythonOperator
```python
from airflow.operators.python import PythonOperator

def my_function(**context):
    print("Hello from Python!")
    return "Success"

task = PythonOperator(
    task_id='python_task',
    python_callable=my_function,
    dag=dag
)
```

### EmailOperator
```python
from airflow.operators.email import EmailOperator

task = EmailOperator(
    task_id='send_email',
    to='user@example.com',
    subject='Pipeline Complete',
    html_content='<p>Success!</p>',
    dag=dag
)
```

---

## 🔗 Task Dependencies

```python
# Method 1: >> operator
task1 >> task2 >> task3

# Method 2: << operator
task3 << task2 << task1

# Fan-out
task1 >> [task2, task3, task4]

# Fan-in
[task1, task2, task3] >> task4

# Chain
from airflow.models.baseoperator import chain
chain(task1, task2, task3, task4)
```

---

## 🎨 TaskFlow API (Airflow 2.0+)

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

---

## 📡 Sensors

### FileSensor
```python
from airflow.sensors.filesystem import FileSensor

sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file.csv',
    poke_interval=60,
    timeout=3600,
    dag=dag
)
```

### TimeSensor
```python
from airflow.sensors.time_sensor import TimeSensor

sensor = TimeSensor(
    task_id='wait_until_9am',
    target_time=datetime.strptime('09:00:00', '%H:%M:%S').time(),
    dag=dag
)
```

### ExternalTaskSensor
```python
from airflow.sensors.external_task import ExternalTaskSensor

sensor = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
    dag=dag
)
```

---

## 💾 XComs (Cross-Communication)

```python
# Push data
def push_function(**context):
    context['ti'].xcom_push(key='my_key', value='my_value')

# Pull data
def pull_function(**context):
    value = context['ti'].xcom_pull(task_ids='push_task', key='my_key')
    print(value)

# Return value (auto-pushed)
def return_function():
    return {'data': 'value'}
```

---

## 🔀 Branching

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    if context['execution_date'].weekday() >= 5:
        return 'weekend_task'
    return 'weekday_task'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
    dag=dag
)

branch >> [weekend_task, weekday_task]
```

---

## 🎛️ Trigger Rules

```python
task = BashOperator(
    task_id='my_task',
    bash_command='echo "test"',
    trigger_rule='all_success',  # Options below
    dag=dag
)
```

| Trigger Rule | Description |
|--------------|-------------|
| `all_success` | All parents succeeded (default) |
| `all_failed` | All parents failed |
| `all_done` | All parents completed |
| `one_success` | At least one parent succeeded |
| `one_failed` | At least one parent failed |
| `none_failed` | No parent failed |
| `none_skipped` | No parent skipped |
| `dummy` | Always run |

---

## 🔄 Retries & Timeouts

```python
from datetime import timedelta

task = BashOperator(
    task_id='my_task',
    bash_command='echo "test"',
    retries=3,
    retry_delay=timedelta(minutes=5),
    execution_timeout=timedelta(hours=1),
    dag=dag
)
```

---

## 📝 Context Variables

Available in `**context`:

```python
def my_function(**context):
    execution_date = context['execution_date']
    ds = context['ds']  # YYYY-MM-DD
    ds_nodash = context['ds_nodash']  # YYYYMMDD
    prev_ds = context['prev_ds']
    next_ds = context['next_ds']
    ti = context['ti']  # Task instance
    dag = context['dag']
    task = context['task']
    dag_run = context['dag_run']
```

---

## 🗄️ Variables & Connections

### Variables
```bash
# Set variable
airflow variables set my_var my_value

# Get variable
airflow variables get my_var

# In code
from airflow.models import Variable
value = Variable.get('my_var')
```

### Connections
```bash
# Add connection
airflow connections add my_postgres \
    --conn-type postgres \
    --conn-host localhost \
    --conn-login user \
    --conn-password pass \
    --conn-port 5432

# In code
from airflow.hooks.base import BaseHook
conn = BaseHook.get_connection('my_postgres')
```

---

## 🏊 Pools

```bash
# Create pool
airflow pools set my_pool 5 "Pool description"

# Use in task
task = BashOperator(
    task_id='pooled_task',
    bash_command='echo "test"',
    pool='my_pool',
    dag=dag
)
```

---

## 🛠️ CLI Commands

### DAG Commands
```bash
# List DAGs
airflow dags list

# Trigger DAG
airflow dags trigger my_dag

# Pause/Unpause
airflow dags pause my_dag
airflow dags unpause my_dag

# Test DAG
airflow dags test my_dag 2024-01-01

# Backfill
airflow dags backfill my_dag -s 2024-01-01 -e 2024-01-31
```

### Task Commands
```bash
# List tasks
airflow tasks list my_dag

# Test task
airflow tasks test my_dag task_id 2024-01-01

# Clear task
airflow tasks clear my_dag --task-regex task_id

# Get state
airflow tasks state my_dag task_id 2024-01-01
```

### Database Commands
```bash
# Initialize
airflow db init

# Upgrade
airflow db upgrade

# Check
airflow db check

# Reset (WARNING: deletes all data)
airflow db reset
```

---

## 🎨 DAG Default Args

```python
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

dag = DAG(
    dag_id='my_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
)
```

---

## 🔍 Templating (Jinja)

```python
# Use {{ }} for templating
task = BashOperator(
    task_id='templated_task',
    bash_command='echo "Date: {{ ds }}"',
    dag=dag
)

# Common templates
{{ ds }}                  # YYYY-MM-DD
{{ ds_nodash }}          # YYYYMMDD
{{ execution_date }}     # Full datetime
{{ prev_ds }}            # Previous date
{{ next_ds }}            # Next date
{{ dag.dag_id }}         # DAG ID
{{ task.task_id }}       # Task ID
{{ var.value.my_var }}   # Variable
{{ conn.my_conn.host }}  # Connection
```

---

## 📊 Executors

| Executor | Use Case | Parallelism |
|----------|----------|-------------|
| SequentialExecutor | Development | 1 task at a time |
| LocalExecutor | Single machine | Multiple tasks |
| CeleryExecutor | Distributed | Multiple workers |
| KubernetesExecutor | Kubernetes | Pods |

---

## 🐛 Debugging

```bash
# Check DAG for errors
python /path/to/dag.py

# View logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log

# Test task
airflow tasks test my_dag task_id 2024-01-01

# Check XComs
airflow tasks test my_dag task1 2024-01-01
airflow tasks test my_dag task2 2024-01-01
```

---

## ⚡ Best Practices

✅ Use meaningful task_ids  
✅ Keep tasks idempotent  
✅ Set appropriate timeouts  
✅ Use pools for resource limits  
✅ Use variables for config  
✅ Test DAGs before deploying  
✅ Monitor DAG performance  
✅ Use TaskFlow API for new DAGs  

❌ Don't use top-level code in DAG files  
❌ Don't pass large data via XComs  
❌ Don't create circular dependencies  
❌ Don't use dynamic start_date  

---

## 📚 Resources

- **Docs**: https://airflow.apache.org/docs/
- **GitHub**: https://github.com/apache/airflow
- **Slack**: https://apache-airflow.slack.com/
- **Examples**: `/path/to/airflow/example_dags/`

---

## 🎯 Quick Checklist

- [ ] Install Airflow
- [ ] Initialize database
- [ ] Create admin user
- [ ] Start webserver & scheduler
- [ ] Create first DAG
- [ ] Test DAG
- [ ] Trigger DAG
- [ ] Monitor in UI

---

**Happy Orchestrating! 🚀**
