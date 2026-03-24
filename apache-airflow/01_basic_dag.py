"""
Basic DAG Example - Apache Airflow

This example demonstrates:
1. Creating a simple DAG
2. Using BashOperator
3. Using PythonOperator
4. Setting task dependencies
5. Basic DAG configuration

Run this example:
    airflow dags test basic_dag 2024-01-01
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Default arguments for all tasks in this DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    dag_id='basic_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'basic'],
)

# Task 1: Print date using BashOperator
print_date = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

# Task 2: Sleep for 5 seconds
sleep = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    dag=dag,
)

# Task 3: Python function
def print_hello(**context):
    """
    Simple Python function that prints hello
    **context allows access to Airflow context variables
    """
    execution_date = context['execution_date']
    print(f"Hello from Airflow!")
    print(f"Execution date: {execution_date}")
    return "Hello task completed"

hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# Task 4: Process data (example)
def process_data(**context):
    """
    Example data processing function
    """
    data = [1, 2, 3, 4, 5]
    result = sum(data)
    print(f"Processing data: {data}")
    print(f"Sum: {result}")
    return result

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

# Task 5: Final task
final_task = BashOperator(
    task_id='final_task',
    bash_command='echo "Pipeline completed successfully!"',
    dag=dag,
)

# Define task dependencies
# Method 1: Using >> operator (recommended)
print_date >> sleep >> hello_task >> process_task >> final_task

# Method 2: Using set_downstream (alternative)
# print_date.set_downstream(sleep)
# sleep.set_downstream(hello_task)

# Method 3: Using set_upstream (alternative)
# sleep.set_upstream(print_date)


"""
DETAILED EXPLANATION
====================

1. DAG DEFINITION
   - dag_id: Unique identifier for the DAG
   - schedule_interval: How often to run (@daily, @hourly, cron expression)
   - start_date: When to start scheduling
   - catchup: If False, only run latest; if True, backfill from start_date
   - tags: Organize DAGs in UI

2. DEFAULT ARGS
   - owner: DAG owner
   - retries: Number of retry attempts on failure
   - retry_delay: Wait time between retries
   - email_on_failure: Send email if task fails
   - depends_on_past: Wait for previous run to succeed

3. OPERATORS
   - BashOperator: Execute bash commands
   - PythonOperator: Execute Python functions
   
4. TASK DEPENDENCIES
   - >> : Downstream dependency (A >> B means B runs after A)
   - << : Upstream dependency (A << B means A runs before B)
   
5. EXECUTION FLOW
   print_date → sleep → print_hello → process_data → final_task

6. CONTEXT VARIABLES
   Available in **context:
   - execution_date: Logical date of DAG run
   - ds: execution_date as string (YYYY-MM-DD)
   - task_instance: Current task instance
   - dag_run: Current DAG run object
   - ti: Short for task_instance

7. TESTING
   # Test entire DAG
   airflow dags test basic_dag 2024-01-01
   
   # Test single task
   airflow tasks test basic_dag print_date 2024-01-01
   
   # List tasks
   airflow tasks list basic_dag
   
   # Show DAG structure
   airflow dags show basic_dag

8. MONITORING
   - View in UI: http://localhost:8080
   - Check logs for each task
   - Monitor task duration and success rate
"""
