"""
Sensors Example - Apache Airflow

This example demonstrates:
1. FileSensor - Wait for file
2. TimeSensor - Wait for specific time
3. ExternalTaskSensor - Wait for another DAG
4. Custom Sensors
5. Sensor modes (poke vs reschedule)

Run this example:
    airflow dags test sensors_example_dag 2024-01-01
"""

from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.time_sensor import TimeSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.python import PythonSensor
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='sensors_example_dag',
    default_args=default_args,
    description='Sensors demonstration',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'sensors'],
)

# ============================================================================
# 1. FILESENSOR - Wait for file to exist
# ============================================================================

wait_for_file = FileSensor(
    task_id='wait_for_input_file',
    filepath='/tmp/input_data.csv',  # File path to check
    poke_interval=30,  # Check every 30 seconds
    timeout=600,  # Timeout after 10 minutes
    mode='poke',  # 'poke' or 'reschedule'
    dag=dag,
)

# Process file once it exists
process_file = BashOperator(
    task_id='process_file',
    bash_command='echo "Processing file: /tmp/input_data.csv"',
    dag=dag,
)

wait_for_file >> process_file

# ============================================================================
# 2. FILESENSOR - Wait for multiple files
# ============================================================================

wait_for_file1 = FileSensor(
    task_id='wait_for_file1',
    filepath='/tmp/file1.csv',
    poke_interval=60,
    timeout=3600,
    dag=dag,
)

wait_for_file2 = FileSensor(
    task_id='wait_for_file2',
    filepath='/tmp/file2.csv',
    poke_interval=60,
    timeout=3600,
    dag=dag,
)

merge_files = BashOperator(
    task_id='merge_files',
    bash_command='cat /tmp/file1.csv /tmp/file2.csv > /tmp/merged.csv',
    dag=dag,
)

[wait_for_file1, wait_for_file2] >> merge_files

# ============================================================================
# 3. TIMESENSOR - Wait until specific time
# ============================================================================

# Wait until 9 AM
wait_until_9am = TimeSensor(
    task_id='wait_until_9am',
    target_time=datetime.strptime('09:00:00', '%H:%M:%S').time(),
    dag=dag,
)

morning_task = BashOperator(
    task_id='morning_processing',
    bash_command='echo "Running morning batch"',
    dag=dag,
)

wait_until_9am >> morning_task

# ============================================================================
# 4. EXTERNALTASKSENSOR - Wait for another DAG
# ============================================================================

# Wait for another DAG to complete
wait_for_upstream_dag = ExternalTaskSensor(
    task_id='wait_for_data_ingestion',
    external_dag_id='data_ingestion_dag',  # DAG to wait for
    external_task_id='final_task',  # Specific task to wait for
    timeout=3600,
    poke_interval=60,
    mode='reschedule',  # Free up worker slot while waiting
    dag=dag,
)

process_ingested_data = BashOperator(
    task_id='process_ingested_data',
    bash_command='echo "Processing data from upstream DAG"',
    dag=dag,
)

wait_for_upstream_dag >> process_ingested_data

# ============================================================================
# 5. PYTHONSENSOR - Custom condition
# ============================================================================

def check_api_available(**context):
    """
    Custom sensor logic
    Return True when condition is met
    """
    import random
    # Simulate API check
    is_available = random.choice([True, False])
    
    if is_available:
        print("API is available!")
        return True
    else:
        print("API not available yet, will retry...")
        return False

wait_for_api = PythonSensor(
    task_id='wait_for_api',
    python_callable=check_api_available,
    poke_interval=30,
    timeout=600,
    mode='poke',
    dag=dag,
)

call_api = BashOperator(
    task_id='call_api',
    bash_command='echo "Calling API"',
    dag=dag,
)

wait_for_api >> call_api

# ============================================================================
# 6. PYTHONSENSOR - Check database record
# ============================================================================

def check_database_record(**context):
    """
    Check if specific record exists in database
    """
    # Simulated database check
    # In real scenario, query database here
    
    execution_date = context['execution_date']
    date_str = execution_date.strftime('%Y-%m-%d')
    
    print(f"Checking for record with date: {date_str}")
    
    # Simulate check
    # SELECT COUNT(*) FROM table WHERE date = date_str
    record_exists = True  # Replace with actual query
    
    if record_exists:
        print("Record found!")
        return True
    else:
        print("Record not found, waiting...")
        return False

wait_for_db_record = PythonSensor(
    task_id='wait_for_database_record',
    python_callable=check_database_record,
    poke_interval=120,  # Check every 2 minutes
    timeout=7200,  # 2 hours timeout
    mode='reschedule',
    dag=dag,
)

process_record = BashOperator(
    task_id='process_database_record',
    bash_command='echo "Processing database record"',
    dag=dag,
)

wait_for_db_record >> process_record

# ============================================================================
# 7. PYTHONSENSOR - Check file size
# ============================================================================

def check_file_size(**context):
    """
    Wait until file reaches minimum size
    """
    filepath = '/tmp/large_file.dat'
    min_size_mb = 100
    
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist yet")
        return False
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Current file size: {size_mb:.2f} MB")
    
    if size_mb >= min_size_mb:
        print(f"File size reached {min_size_mb} MB threshold")
        return True
    else:
        print(f"File size below threshold, waiting...")
        return False

wait_for_file_size = PythonSensor(
    task_id='wait_for_file_size',
    python_callable=check_file_size,
    poke_interval=300,  # Check every 5 minutes
    timeout=3600,
    dag=dag,
)

# ============================================================================
# 8. SENSOR MODES COMPARISON
# ============================================================================

# POKE MODE: Keeps worker slot occupied
poke_sensor = FileSensor(
    task_id='poke_mode_sensor',
    filepath='/tmp/poke_file.txt',
    poke_interval=60,
    timeout=600,
    mode='poke',  # Blocks worker slot
    dag=dag,
)

# RESCHEDULE MODE: Frees worker slot between checks
reschedule_sensor = FileSensor(
    task_id='reschedule_mode_sensor',
    filepath='/tmp/reschedule_file.txt',
    poke_interval=60,
    timeout=600,
    mode='reschedule',  # Frees worker slot
    dag=dag,
)

# ============================================================================
# 9. SOFT FAIL - Don't fail DAG if sensor times out
# ============================================================================

optional_file_sensor = FileSensor(
    task_id='optional_file_sensor',
    filepath='/tmp/optional_file.txt',
    poke_interval=30,
    timeout=300,
    soft_fail=True,  # Mark as skipped instead of failed
    dag=dag,
)

conditional_task = BashOperator(
    task_id='conditional_processing',
    bash_command='echo "Processing optional file"',
    trigger_rule='none_failed',  # Run even if sensor is skipped
    dag=dag,
)

optional_file_sensor >> conditional_task


"""
DETAILED EXPLANATION
====================

1. WHAT ARE SENSORS?

   Sensors are special operators that wait for a condition to be true:
   - Check condition repeatedly
   - Block task execution until condition met
   - Timeout if condition not met within time limit

2. FILESENSOR

   Wait for file to exist:
   
   Parameters:
   - filepath: Path to file
   - poke_interval: Seconds between checks
   - timeout: Maximum wait time
   - mode: 'poke' or 'reschedule'
   
   Use cases:
   - Wait for data file from external system
   - Wait for completion marker file
   - Wait for multiple files before processing

3. TIMESENSOR

   Wait until specific time:
   
   Parameters:
   - target_time: Time to wait for (time object)
   
   Use cases:
   - Start processing at specific time
   - Wait for business hours
   - Coordinate with external schedules

4. EXTERNALTASKSENSOR

   Wait for another DAG/task:
   
   Parameters:
   - external_dag_id: DAG to wait for
   - external_task_id: Specific task (optional)
   - execution_delta: Time difference between DAGs
   
   Use cases:
   - DAG dependencies
   - Wait for upstream pipeline
   - Coordinate multiple workflows

5. PYTHONSENSOR

   Custom sensor logic:
   
   def sensor_function(**context):
       # Check condition
       if condition_met:
           return True
       else:
           return False
   
   Use cases:
   - Check API availability
   - Check database records
   - Check file content
   - Custom business logic

6. SENSOR MODES

   POKE MODE:
   - Keeps worker slot occupied
   - Checks condition at intervals
   - Use for short waits (< 5 minutes)
   
   RESCHEDULE MODE:
   - Frees worker slot between checks
   - Reschedules task for next check
   - Use for long waits (> 5 minutes)
   - Better resource utilization

7. SENSOR PARAMETERS

   Common parameters:
   - poke_interval: Seconds between checks
   - timeout: Maximum wait time (seconds)
   - mode: 'poke' or 'reschedule'
   - soft_fail: Skip instead of fail on timeout
   - exponential_backoff: Increase interval over time

8. BEST PRACTICES

   ✅ Use reschedule mode for long waits
   ✅ Set appropriate timeouts
   ✅ Use soft_fail for optional dependencies
   ✅ Monitor sensor duration
   ✅ Use exponential backoff for external APIs
   
   ❌ Don't use poke mode for long waits
   ❌ Don't set very short poke_intervals
   ❌ Don't create too many sensors
   ❌ Don't ignore timeout errors

9. SENSOR TIMEOUT HANDLING

   When sensor times out:
   - Default: Task fails, DAG fails
   - soft_fail=True: Task skipped, DAG continues
   - on_failure_callback: Custom error handling

10. COMMON USE CASES

    a) Data Pipeline:
       wait_for_file >> process_file >> load_to_db
    
    b) API Integration:
       wait_for_api >> fetch_data >> transform >> load
    
    c) Multi-DAG Workflow:
       wait_for_upstream_dag >> process_data >> downstream_tasks
    
    d) Scheduled Processing:
       wait_until_time >> batch_processing >> cleanup

11. TESTING SENSORS

    # Test sensor (will wait for condition)
    airflow tasks test sensors_example_dag wait_for_file 2024-01-01
    
    # Create test file
    touch /tmp/input_data.csv
    
    # Test again (should succeed immediately)
    airflow tasks test sensors_example_dag wait_for_file 2024-01-01

12. MONITORING SENSORS

    In Airflow UI:
    - Check sensor duration
    - Monitor timeout frequency
    - Review poke count
    - Analyze resource usage
    
    Metrics to track:
    - Average sensor duration
    - Timeout rate
    - Poke count per sensor
    - Worker slot utilization
"""
