"""
Operators Guide - Apache Airflow

This example demonstrates all major operators:
1. BashOperator
2. PythonOperator
3. EmailOperator
4. SQL Operators
5. Sensor Operators
6. Transfer Operators
7. Custom Operators

Run this example:
    airflow dags test operators_guide_dag 2024-01-01
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='operators_guide_dag',
    default_args=default_args,
    description='Comprehensive operators guide',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'operators'],
)

# ============================================================================
# 1. BASHOPERATOR - Execute bash commands
# ============================================================================

# Simple bash command
bash_simple = BashOperator(
    task_id='bash_simple',
    bash_command='echo "Hello from Bash"',
    dag=dag,
)

# Bash command with templating
bash_templated = BashOperator(
    task_id='bash_templated',
    bash_command='echo "Execution date: {{ ds }}"',
    dag=dag,
)

# Multi-line bash script
bash_script = BashOperator(
    task_id='bash_script',
    bash_command='''
        echo "Starting script..."
        date
        echo "Current directory: $(pwd)"
        echo "Script completed"
    ''',
    dag=dag,
)

# Execute external script
bash_external = BashOperator(
    task_id='bash_external_script',
    bash_command='bash /path/to/script.sh ',
    dag=dag,
)

# Bash with environment variables
bash_env = BashOperator(
    task_id='bash_with_env',
    bash_command='echo "User: $USER, Home: $HOME"',
    env={'CUSTOM_VAR': 'custom_value'},
    dag=dag,
)

# ============================================================================
# 2. PYTHONOPERATOR - Execute Python functions
# ============================================================================

# Simple Python function
def simple_python_function():
    print("Hello from Python!")
    return "Success"

python_simple = PythonOperator(
    task_id='python_simple',
    python_callable=simple_python_function,
    dag=dag,
)

# Python function with arguments
def python_with_args(name, age):
    print(f"Name: {name}, Age: {age}")
    return f"Processed {name}"

python_args = PythonOperator(
    task_id='python_with_args',
    python_callable=python_with_args,
    op_args=['John', 30],  # Positional arguments
    dag=dag,
)

# Python function with keyword arguments
python_kwargs = PythonOperator(
    task_id='python_with_kwargs',
    python_callable=python_with_args,
    op_kwargs={'name': 'Jane', 'age': 25},  # Keyword arguments
    dag=dag,
)

# Python function with context
def python_with_context(**context):
    """
    Access Airflow context variables
    """
    execution_date = context['execution_date']
    task_instance = context['ti']
    dag_run = context['dag_run']
    
    print(f"Execution Date: {execution_date}")
    print(f"Task Instance: {task_instance.task_id}")
    print(f"DAG Run ID: {dag_run.run_id}")
    
    # Access template variables
    ds = context['ds']  # YYYY-MM-DD
    ds_nodash = context['ds_nodash']  # YYYYMMDD
    
    print(f"Date String: {ds}")
    print(f"Date No Dash: {ds_nodash}")
    
    return "Context processed"

python_context = PythonOperator(
    task_id='python_with_context',
    python_callable=python_with_context,
    provide_context=True,
    dag=dag,
)

# Python function that returns value
def extract_data(**context):
    data = {'users': 100, 'revenue': 50000}
    print(f"Extracted data: {data}")
    # Push to XCom
    context['ti'].xcom_push(key='extracted_data', value=data)
    return data

python_extract = PythonOperator(
    task_id='python_extract_data',
    python_callable=extract_data,
    dag=dag,
)

# Python function that reads XCom
def process_data(**context):
    # Pull from XCom
    data = context['ti'].xcom_pull(
        task_ids='python_extract_data',
        key='extracted_data'
    )
    print(f"Processing data: {data}")
    return f"Processed {data}"

python_process = PythonOperator(
    task_id='python_process_data',
    python_callable=process_data,
    dag=dag,
)

python_extract >> python_process

# ============================================================================
# 3. EMAILOPERATOR - Send emails
# ============================================================================

# Note: Requires SMTP configuration in airflow.cfg
email_task = EmailOperator(
    task_id='send_email',
    to='user@example.com',
    subject='Airflow Pipeline Notification',
    html_content='''
        <h3>Pipeline Status</h3>
        <p>Your data pipeline completed successfully!</p>
        <p>Execution Date: {{ ds }}</p>
    ''',
    dag=dag,
)

# Email with attachments
email_with_attachment = EmailOperator(
    task_id='send_email_with_attachment',
    to=['user1@example.com', 'user2@example.com'],
    subject='Report - {{ ds }}',
    html_content='<p>Please find attached report.</p>',
    files=['/path/to/report.pdf'],
    dag=dag,
)

# ============================================================================
# 4. DUMMYOPERATOR - Placeholder tasks
# ============================================================================

# Useful for organizing DAG structure
start = DummyOperator(
    task_id='start',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

# ============================================================================
# 5. BRANCHING - Conditional execution
# ============================================================================

from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    """
    Decide which branch to execute based on logic
    """
    execution_date = context['execution_date']
    
    # Example: Different processing on weekends
    if execution_date.weekday() >= 5:  # Saturday or Sunday
        return 'weekend_processing'
    else:
        return 'weekday_processing'

branch_task = BranchPythonOperator(
    task_id='branch_decision',
    python_callable=choose_branch,
    dag=dag,
)

weekend_task = BashOperator(
    task_id='weekend_processing',
    bash_command='echo "Weekend processing"',
    dag=dag,
)

weekday_task = BashOperator(
    task_id='weekday_processing',
    bash_command='echo "Weekday processing"',
    dag=dag,
)

branch_task >> [weekend_task, weekday_task]

# ============================================================================
# 6. SHORTCIRCUITOPERATOR - Skip downstream tasks
# ============================================================================

from airflow.operators.python import ShortCircuitOperator

def check_condition(**context):
    """
    Return False to skip all downstream tasks
    """
    # Example: Only run on first day of month
    execution_date = context['execution_date']
    return execution_date.day == 1

short_circuit = ShortCircuitOperator(
    task_id='check_if_first_day',
    python_callable=check_condition,
    dag=dag,
)

monthly_task = BashOperator(
    task_id='monthly_processing',
    bash_command='echo "Running monthly task"',
    dag=dag,
)

short_circuit >> monthly_task

# ============================================================================
# 7. TRIGGER RULES
# ============================================================================

# Task that runs only if all parents succeed (default)
all_success = BashOperator(
    task_id='all_success_task',
    bash_command='echo "All parents succeeded"',
    trigger_rule='all_success',  # Default
    dag=dag,
)

# Task that runs if any parent succeeds
one_success = BashOperator(
    task_id='one_success_task',
    bash_command='echo "At least one parent succeeded"',
    trigger_rule='one_success',
    dag=dag,
)

# Task that always runs
always_run = BashOperator(
    task_id='always_run_task',
    bash_command='echo "Always runs"',
    trigger_rule='all_done',  # Runs regardless of parent status
    dag=dag,
)

# Task that runs if parent fails
on_failure = BashOperator(
    task_id='on_failure_task',
    bash_command='echo "Parent failed"',
    trigger_rule='one_failed',
    dag=dag,
)

# ============================================================================
# 8. TASK TIMEOUTS AND RETRIES
# ============================================================================

timeout_task = BashOperator(
    task_id='task_with_timeout',
    bash_command='sleep 10',
    execution_timeout=timedelta(seconds=5),  # Will fail if takes > 5 seconds
    retries=3,
    retry_delay=timedelta(seconds=10),
    dag=dag,
)

# ============================================================================
# 9. POOLS - Limit concurrent execution
# ============================================================================

# Create pool: airflow pools set my_pool 2 "My pool"
pooled_task = BashOperator(
    task_id='pooled_task',
    bash_command='echo "Running in pool"',
    pool='my_pool',  # Limit concurrent tasks
    dag=dag,
)

# ============================================================================
# 10. PRIORITY - Task execution order
# ============================================================================

high_priority = BashOperator(
    task_id='high_priority_task',
    bash_command='echo "High priority"',
    priority_weight=10,  # Higher number = higher priority
    dag=dag,
)

low_priority = BashOperator(
    task_id='low_priority_task',
    bash_command='echo "Low priority"',
    priority_weight=1,
    dag=dag,
)


"""
DETAILED EXPLANATION
====================

1. BASHOPERATOR

   Use cases:
   - Execute shell scripts
   - Run command-line tools
   - File operations
   - System commands
   
   Parameters:
   - bash_command: Command to execute
   - env: Environment variables
   - cwd: Working directory
   - append_env: Append to existing env vars

2. PYTHONOPERATOR

   Use cases:
   - Data processing
   - API calls
   - Complex logic
   - Database operations
   
   Parameters:
   - python_callable: Function to execute
   - op_args: Positional arguments
   - op_kwargs: Keyword arguments
   - provide_context: Pass Airflow context

3. CONTEXT VARIABLES

   Available in **context:
   - execution_date: Logical date
   - ds: Date string (YYYY-MM-DD)
   - ds_nodash: Date string (YYYYMMDD)
   - prev_ds: Previous execution date
   - next_ds: Next execution date
   - ti: Task instance
   - task: Task object
   - dag: DAG object
   - dag_run: DAG run object
   - conf: DAG run configuration

4. XCOMS (Cross-Communication)

   Share data between tasks:
   
   # Push data
   ti.xcom_push(key='my_key', value='my_value')
   
   # Pull data
   value = ti.xcom_pull(task_ids='task_id', key='my_key')
   
   # Return value (automatically pushed)
   return {'data': 'value'}

5. BRANCHING

   Conditional task execution:
   - BranchPythonOperator: Choose one branch
   - ShortCircuitOperator: Skip all downstream
   
   Return task_id to execute that branch

6. TRIGGER RULES

   Control when task runs:
   - all_success: All parents succeeded (default)
   - all_failed: All parents failed
   - all_done: All parents completed
   - one_success: At least one parent succeeded
   - one_failed: At least one parent failed
   - none_failed: No parent failed
   - none_skipped: No parent skipped
   - dummy: Always run

7. RETRIES AND TIMEOUTS

   - retries: Number of retry attempts
   - retry_delay: Wait time between retries
   - retry_exponential_backoff: Exponential backoff
   - max_retry_delay: Maximum retry delay
   - execution_timeout: Task timeout

8. POOLS

   Limit concurrent task execution:
   
   # Create pool
   airflow pools set pool_name 5 "Description"
   
   # Use in task
   task = BashOperator(
       task_id='task',
       bash_command='echo "test"',
       pool='pool_name'
   )

9. PRIORITY

   Control task execution order:
   - priority_weight: Higher = higher priority
   - weight_rule: How to calculate priority
     - downstream: Sum of downstream tasks
     - upstream: Sum of upstream tasks
     - absolute: Use priority_weight as-is

10. BEST PRACTICES

    ✅ Use BashOperator for simple commands
    ✅ Use PythonOperator for complex logic
    ✅ Keep tasks idempotent
    ✅ Use XComs for small data only
    ✅ Set appropriate timeouts
    ✅ Use pools to limit resource usage
    
    ❌ Don't pass large data via XComs
    ❌ Don't use long-running tasks
    ❌ Don't ignore error handling
    ❌ Don't hardcode values (use Variables)

11. TESTING

    # Test Python function
    airflow tasks test operators_guide_dag python_simple 2024-01-01
    
    # Test Bash command
    airflow tasks test operators_guide_dag bash_simple 2024-01-01
    
    # Check XCom values
    airflow tasks test operators_guide_dag python_extract_data 2024-01-01
    airflow tasks test operators_guide_dag python_process_data 2024-01-01
"""
