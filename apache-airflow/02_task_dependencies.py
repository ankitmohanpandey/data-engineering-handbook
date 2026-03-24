"""
Task Dependencies Example - Apache Airflow

This example demonstrates:
1. Linear dependencies
2. Fan-out (one task to many)
3. Fan-in (many tasks to one)
4. Complex dependency patterns
5. Task groups

Run this example:
    airflow dags test task_dependencies_dag 2024-01-01
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='task_dependencies_dag',
    default_args=default_args,
    description='Complex task dependencies example',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'dependencies'],
)

# ============================================================================
# EXAMPLE 1: LINEAR DEPENDENCIES
# ============================================================================

start = BashOperator(
    task_id='start',
    bash_command='echo "Starting pipeline"',
    dag=dag,
)

# ============================================================================
# EXAMPLE 2: FAN-OUT (One task to multiple tasks)
# ============================================================================

def extract_data(source, **context):
    print(f"Extracting data from {source}")
    return f"Data from {source}"

extract_db = PythonOperator(
    task_id='extract_from_database',
    python_callable=extract_data,
    op_kwargs={'source': 'database'},
    dag=dag,
)

extract_api = PythonOperator(
    task_id='extract_from_api',
    python_callable=extract_data,
    op_kwargs={'source': 'API'},
    dag=dag,
)

extract_file = PythonOperator(
    task_id='extract_from_file',
    python_callable=extract_data,
    op_kwargs={'source': 'file'},
    dag=dag,
)

# Fan-out: start runs, then all three extract tasks run in parallel
start >> [extract_db, extract_api, extract_file]

# ============================================================================
# EXAMPLE 3: PARALLEL PROCESSING
# ============================================================================

def transform_data(dataset, **context):
    print(f"Transforming {dataset}")
    return f"Transformed {dataset}"

transform_db = PythonOperator(
    task_id='transform_database_data',
    python_callable=transform_data,
    op_kwargs={'dataset': 'database'},
    dag=dag,
)

transform_api = PythonOperator(
    task_id='transform_api_data',
    python_callable=transform_data,
    op_kwargs={'dataset': 'API'},
    dag=dag,
)

transform_file = PythonOperator(
    task_id='transform_file_data',
    python_callable=transform_data,
    op_kwargs={'dataset': 'file'},
    dag=dag,
)

# Each extract task triggers its corresponding transform task
extract_db >> transform_db
extract_api >> transform_api
extract_file >> transform_file

# ============================================================================
# EXAMPLE 4: FAN-IN (Multiple tasks to one task)
# ============================================================================

def merge_data(**context):
    print("Merging all transformed data")
    return "Merged dataset"

merge = PythonOperator(
    task_id='merge_all_data',
    python_callable=merge_data,
    dag=dag,
)

# Fan-in: All transform tasks must complete before merge runs
[transform_db, transform_api, transform_file] >> merge

# ============================================================================
# EXAMPLE 5: TASK GROUPS (Organize related tasks)
# ============================================================================

with TaskGroup(group_id='data_quality_checks', dag=dag) as quality_checks:
    
    check_nulls = BashOperator(
        task_id='check_null_values',
        bash_command='echo "Checking for null values"',
    )
    
    check_duplicates = BashOperator(
        task_id='check_duplicates',
        bash_command='echo "Checking for duplicates"',
    )
    
    check_schema = BashOperator(
        task_id='check_schema',
        bash_command='echo "Validating schema"',
    )
    
    # Tasks within group can have dependencies
    check_nulls >> check_duplicates >> check_schema

# Task group as a whole depends on merge
merge >> quality_checks

# ============================================================================
# EXAMPLE 6: CONDITIONAL DEPENDENCIES
# ============================================================================

def load_to_warehouse(**context):
    print("Loading data to warehouse")
    return "Load complete"

load = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag,
)

# Load only runs after quality checks pass
quality_checks >> load

# ============================================================================
# EXAMPLE 7: MULTIPLE DOWNSTREAM TASKS
# ============================================================================

send_success_email = BashOperator(
    task_id='send_success_notification',
    bash_command='echo "Sending success email"',
    dag=dag,
)

update_metadata = BashOperator(
    task_id='update_metadata_table',
    bash_command='echo "Updating metadata"',
    dag=dag,
)

archive_data = BashOperator(
    task_id='archive_raw_data',
    bash_command='echo "Archiving raw data"',
    dag=dag,
)

# After load completes, run all three tasks in parallel
load >> [send_success_email, update_metadata, archive_data]

# ============================================================================
# EXAMPLE 8: FINAL TASK
# ============================================================================

end = BashOperator(
    task_id='end',
    bash_command='echo "Pipeline completed"',
    dag=dag,
)

# All final tasks must complete before end
[send_success_email, update_metadata, archive_data] >> end


"""
DETAILED EXPLANATION
====================

1. DEPENDENCY PATTERNS

   a) Linear: A >> B >> C
      ┌───┐    ┌───┐    ┌───┐
      │ A │───►│ B │───►│ C │
      └───┘    └───┘    └───┘

   b) Fan-out: A >> [B, C, D]
      ┌───┐    ┌───┐
      │ A │───►│ B │
      └───┘  ┌►└───┘
             │ ┌───┐
             ├►│ C │
             │ └───┘
             │ ┌───┐
             └►│ D │
               └───┘

   c) Fan-in: [A, B, C] >> D
      ┌───┐
      │ A │───┐
      └───┘   │ ┌───┐
      ┌───┐   ├►│ D │
      │ B │───┤ └───┘
      └───┘   │
      ┌───┐   │
      │ C │───┘
      └───┘

   d) Diamond:
      ┌───┐
      │ A │
      └───┘
       ├──────┐
      ┌▼──┐  ┌▼──┐
      │ B │  │ C │
      └───┘  └───┘
       └──────┤
          ┌───▼┐
          │ D  │
          └────┘

2. DEPENDENCY SYNTAX

   # Single dependency
   task1 >> task2
   
   # Multiple downstream
   task1 >> [task2, task3, task4]
   
   # Multiple upstream
   [task1, task2, task3] >> task4
   
   # Chain
   task1 >> task2 >> task3 >> task4
   
   # Bi-directional (equivalent)
   task1 >> task2
   task2 << task1

3. TASK GROUPS

   Benefits:
   - Organize related tasks visually in UI
   - Collapse/expand in graph view
   - Apply common configuration
   - Reusable components
   
   Usage:
   with TaskGroup(group_id='my_group') as group:
       task1 = BashOperator(...)
       task2 = BashOperator(...)
       task1 >> task2

4. EXECUTION ORDER

   This DAG executes in this order:
   
   1. start
   2. extract_db, extract_api, extract_file (parallel)
   3. transform_db, transform_api, transform_file (parallel)
   4. merge
   5. quality_checks (check_nulls >> check_duplicates >> check_schema)
   6. load
   7. send_success_email, update_metadata, archive_data (parallel)
   8. end

5. PARALLELISM

   Tasks run in parallel when:
   - They have the same upstream dependencies
   - No direct dependency between them
   - Executor supports parallelism
   
   Example: extract_db, extract_api, extract_file all depend only on
   'start', so they run in parallel.

6. BEST PRACTICES

   ✅ Use task groups for logical organization
   ✅ Minimize dependencies for better parallelism
   ✅ Use meaningful task IDs
   ✅ Keep tasks atomic and idempotent
   ✅ Use fan-out for parallel processing
   
   ❌ Don't create circular dependencies
   ❌ Don't make tasks too granular (overhead)
   ❌ Don't create unnecessary dependencies

7. TESTING

   # Visualize dependencies
   airflow dags show task_dependencies_dag
   
   # List tasks in execution order
   airflow tasks list task_dependencies_dag --tree
   
   # Test specific task
   airflow tasks test task_dependencies_dag merge 2024-01-01

8. MONITORING

   In Airflow UI:
   - Graph View: See visual representation
   - Tree View: See historical runs
   - Gantt Chart: See task duration and parallelism
"""
