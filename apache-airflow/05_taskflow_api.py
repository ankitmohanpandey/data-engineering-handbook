"""
TaskFlow API Example - Apache Airflow 2.0+

This example demonstrates:
1. @task decorator
2. @dag decorator
3. Automatic XCom handling
4. Task dependencies via function calls
5. Multiple outputs
6. Task groups with TaskFlow

Run this example:
    airflow dags test taskflow_api_dag 2024-01-01
"""

from airflow.decorators import dag, task, task_group
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ============================================================================
# EXAMPLE 1: Basic TaskFlow API
# ============================================================================

@dag(
    dag_id='taskflow_api_dag',
    default_args=default_args,
    description='TaskFlow API demonstration',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow'],
)
def taskflow_example():
    """
    Modern way to define DAGs using TaskFlow API
    """
    
    # Task 1: Extract data
    @task
    def extract():
        """
        Extract data from source
        Return value automatically pushed to XCom
        """
        data = {
            'users': [
                {'id': 1, 'name': 'Alice', 'age': 30},
                {'id': 2, 'name': 'Bob', 'age': 25},
                {'id': 3, 'name': 'Charlie', 'age': 35},
            ]
        }
        print(f"Extracted {len(data['users'])} users")
        return data
    
    # Task 2: Transform data
    @task
    def transform(data: dict):
        """
        Transform extracted data
        Input automatically pulled from XCom
        """
        users = data['users']
        
        # Add new field
        for user in users:
            user['age_group'] = 'adult' if user['age'] >= 18 else 'minor'
        
        transformed_data = {
            'users': users,
            'total_count': len(users),
            'avg_age': sum(u['age'] for u in users) / len(users)
        }
        
        print(f"Transformed data: {transformed_data}")
        return transformed_data
    
    # Task 3: Load data
    @task
    def load(data: dict):
        """
        Load transformed data to destination
        """
        print(f"Loading {data['total_count']} users")
        print(f"Average age: {data['avg_age']:.1f}")
        print("Data loaded successfully!")
        return "Load complete"
    
    # Define task dependencies via function calls
    # Data flows automatically through XCom
    extracted_data = extract()
    transformed_data = transform(extracted_data)
    load(transformed_data)

# Instantiate the DAG
dag_instance = taskflow_example()


# ============================================================================
# EXAMPLE 2: Multiple Outputs
# ============================================================================

@dag(
    dag_id='taskflow_multiple_outputs',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow'],
)
def multiple_outputs_example():
    """
    Task with multiple outputs
    """
    
    @task(multiple_outputs=True)
    def extract_multiple_sources():
        """
        Return dictionary with multiple outputs
        Each key becomes a separate XCom
        """
        return {
            'database_data': {'records': 100, 'source': 'postgres'},
            'api_data': {'records': 50, 'source': 'rest_api'},
            'file_data': {'records': 75, 'source': 'csv'}
        }
    
    @task
    def process_database(data: dict):
        print(f"Processing {data['records']} records from {data['source']}")
        return f"Processed {data['records']} database records"
    
    @task
    def process_api(data: dict):
        print(f"Processing {data['records']} records from {data['source']}")
        return f"Processed {data['records']} API records"
    
    @task
    def process_file(data: dict):
        print(f"Processing {data['records']} records from {data['source']}")
        return f"Processed {data['records']} file records"
    
    @task
    def combine_results(db_result: str, api_result: str, file_result: str):
        print("Combining all results:")
        print(f"  - {db_result}")
        print(f"  - {api_result}")
        print(f"  - {file_result}")
        return "All data processed"
    
    # Extract returns multiple outputs
    sources = extract_multiple_sources()
    
    # Access individual outputs
    db_processed = process_database(sources['database_data'])
    api_processed = process_api(sources['api_data'])
    file_processed = process_file(sources['file_data'])
    
    # Combine results
    combine_results(db_processed, api_processed, file_processed)

dag_multiple = multiple_outputs_example()


# ============================================================================
# EXAMPLE 3: Task Groups with TaskFlow
# ============================================================================

@dag(
    dag_id='taskflow_with_groups',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow', 'groups'],
)
def taskflow_groups_example():
    """
    Organize tasks using task groups
    """
    
    @task
    def start():
        print("Starting pipeline")
        return {'status': 'started'}
    
    @task_group
    def data_extraction_group():
        """
        Group of extraction tasks
        """
        @task
        def extract_customers():
            return {'customers': 100}
        
        @task
        def extract_orders():
            return {'orders': 500}
        
        @task
        def extract_products():
            return {'products': 50}
        
        # Return all extractions
        return {
            'customers': extract_customers(),
            'orders': extract_orders(),
            'products': extract_products()
        }
    
    @task_group
    def data_transformation_group(extracted_data):
        """
        Group of transformation tasks
        """
        @task
        def transform_customers(data):
            print(f"Transforming {data['customers']} customers")
            return {'transformed_customers': data['customers']}
        
        @task
        def transform_orders(data):
            print(f"Transforming {data['orders']} orders")
            return {'transformed_orders': data['orders']}
        
        @task
        def transform_products(data):
            print(f"Transforming {data['products']} products")
            return {'transformed_products': data['products']}
        
        return {
            'customers': transform_customers(extracted_data['customers']),
            'orders': transform_orders(extracted_data['orders']),
            'products': transform_products(extracted_data['products'])
        }
    
    @task
    def load_all(transformed_data):
        print("Loading all transformed data")
        print(f"Data: {transformed_data}")
        return "Load complete"
    
    @task
    def end(load_result):
        print(f"Pipeline completed: {load_result}")
        return "Success"
    
    # Define workflow
    start_result = start()
    extracted = data_extraction_group()
    transformed = data_transformation_group(extracted)
    loaded = load_all(transformed)
    end(loaded)

dag_groups = taskflow_groups_example()


# ============================================================================
# EXAMPLE 4: Error Handling with TaskFlow
# ============================================================================

@dag(
    dag_id='taskflow_error_handling',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow', 'error-handling'],
)
def error_handling_example():
    """
    Error handling in TaskFlow API
    """
    
    @task
    def risky_operation():
        """
        Task that might fail
        """
        import random
        
        if random.random() > 0.5:
            print("Operation successful")
            return {'status': 'success', 'data': [1, 2, 3]}
        else:
            raise Exception("Random failure occurred")
    
    @task
    def handle_success(data: dict):
        print(f"Handling successful operation: {data}")
        return "Success handled"
    
    @task(trigger_rule='all_failed')
    def handle_failure():
        """
        Runs only if upstream task fails
        """
        print("Handling failure - sending alert")
        return "Failure handled"
    
    @task(trigger_rule='all_done')
    def cleanup():
        """
        Always runs regardless of success/failure
        """
        print("Performing cleanup")
        return "Cleanup complete"
    
    # Define workflow
    result = risky_operation()
    success = handle_success(result)
    failure = handle_failure()
    cleanup()

dag_error = error_handling_example()


# ============================================================================
# EXAMPLE 5: Dynamic Task Mapping (Airflow 2.3+)
# ============================================================================

@dag(
    dag_id='taskflow_dynamic_mapping',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow', 'dynamic'],
)
def dynamic_mapping_example():
    """
    Dynamic task mapping - create tasks at runtime
    """
    
    @task
    def get_file_list():
        """
        Return list of files to process
        """
        files = [
            'file1.csv',
            'file2.csv',
            'file3.csv',
            'file4.csv',
        ]
        return files
    
    @task
    def process_file(filename: str):
        """
        Process individual file
        This task will be dynamically mapped for each file
        """
        print(f"Processing {filename}")
        # Simulate processing
        record_count = len(filename) * 10
        return {'file': filename, 'records': record_count}
    
    @task
    def summarize_results(results: list):
        """
        Summarize all processing results
        """
        total_records = sum(r['records'] for r in results)
        print(f"Processed {len(results)} files")
        print(f"Total records: {total_records}")
        return total_records
    
    # Dynamic mapping
    files = get_file_list()
    # expand() creates one task instance per file
    processed = process_file.expand(filename=files)
    summarize_results(processed)

dag_dynamic = dynamic_mapping_example()


# ============================================================================
# EXAMPLE 6: Using Context in TaskFlow
# ============================================================================

@dag(
    dag_id='taskflow_with_context',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'taskflow', 'context'],
)
def context_example():
    """
    Access Airflow context in TaskFlow tasks
    """
    
    @task
    def use_context(execution_date=None, ds=None, **context):
        """
        Access context variables
        """
        print(f"Execution Date: {execution_date}")
        print(f"Date String: {ds}")
        print(f"DAG ID: {context['dag'].dag_id}")
        print(f"Task ID: {context['task'].task_id}")
        print(f"Run ID: {context['run_id']}")
        
        return {
            'execution_date': str(execution_date),
            'ds': ds
        }
    
    @task
    def process_with_date(date_info: dict):
        print(f"Processing data for {date_info['ds']}")
        return f"Processed {date_info['ds']}"
    
    date_info = use_context()
    process_with_date(date_info)

dag_context = context_example()


"""
DETAILED EXPLANATION
====================

1. TASKFLOW API BENEFITS

   Traditional way:
   def extract():
       return data
   
   extract_task = PythonOperator(
       task_id='extract',
       python_callable=extract
   )
   
   TaskFlow way:
   @task
   def extract():
       return data
   
   extract_task = extract()

   Benefits:
   - Less boilerplate code
   - Automatic XCom handling
   - Type hints for better IDE support
   - Cleaner dependency definition

2. @task DECORATOR

   Converts Python function to Airflow task:
   
   @task
   def my_task(param1, param2):
       # Task logic
       return result
   
   Parameters:
   - task_id: Override default task ID
   - multiple_outputs: Return dict as multiple XComs
   - retries: Number of retries
   - retry_delay: Delay between retries
   - trigger_rule: When to run task

3. @dag DECORATOR

   Converts function to DAG:
   
   @dag(
       dag_id='my_dag',
       schedule_interval='@daily',
       start_date=datetime(2024, 1, 1)
   )
   def my_dag_function():
       # Define tasks
       pass
   
   dag = my_dag_function()

4. AUTOMATIC XCOM HANDLING

   Traditional:
   ti.xcom_push(key='data', value=data)
   data = ti.xcom_pull(task_ids='task1', key='data')
   
   TaskFlow:
   data = extract()  # Automatically pushed
   transform(data)   # Automatically pulled

5. MULTIPLE OUTPUTS

   @task(multiple_outputs=True)
   def extract():
       return {
           'key1': value1,
           'key2': value2
       }
   
   result = extract()
   process1(result['key1'])
   process2(result['key2'])

6. TASK GROUPS

   @task_group
   def my_group():
       @task
       def task1():
           pass
       
       @task
       def task2():
           pass
       
       task1() >> task2()
   
   my_group()

7. DYNAMIC TASK MAPPING

   @task
   def get_items():
       return [1, 2, 3, 4, 5]
   
   @task
   def process_item(item):
       return item * 2
   
   items = get_items()
   process_item.expand(item=items)
   
   Creates 5 task instances dynamically

8. CONTEXT ACCESS

   @task
   def my_task(execution_date=None, **context):
       # Access context variables
       pass

9. ERROR HANDLING

   @task(trigger_rule='all_failed')
   def handle_error():
       # Runs only on failure
       pass

10. BEST PRACTICES

    ✅ Use TaskFlow for new DAGs
    ✅ Use type hints for parameters
    ✅ Keep task functions pure
    ✅ Use task groups for organization
    ✅ Leverage automatic XCom handling
    
    ❌ Don't mix TaskFlow and traditional operators unnecessarily
    ❌ Don't pass large data between tasks
    ❌ Don't use mutable default arguments
    ❌ Don't perform heavy computation in DAG file

11. TESTING

    # Test TaskFlow DAG
    airflow dags test taskflow_api_dag 2024-01-01
    
    # Test individual task
    airflow tasks test taskflow_api_dag extract 2024-01-01

12. MIGRATION FROM TRADITIONAL

    Before:
    def extract():
        return data
    
    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract
    )
    
    After:
    @task
    def extract():
        return data
    
    extract()
"""
