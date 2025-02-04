from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowFailException
from ai_agent import analyze_logs_and_act

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,  # Allow retry once
}

def extract_data():
    print("Extracting data...")
    # Simulate a failure
    # raise AirflowFailException("Extraction failed!")  # More specific than Exception

def transform_data():
    print("Transforming data...")
    

def load_data():
    print("Loading data...")
    raise AirflowFailException("Temporary disconnection with the target!")

def handle_failure(context):
    """Handles failure by consulting the AI agent."""
    task_instance = context['task_instance']
    ai_decision = analyze_logs_and_act(context)

    if ai_decision == "restart":
        if task_instance.try_number <= task_instance.max_tries:
            print("AI Agent decided to restart. Marking task for retry.")
            task_instance.xcom_push(key="ai_decision", value="restart")
        else:
            print("Max retries reached. Escalating issue.")
            task_instance.xcom_push(key="ai_decision", value="escalate")
    elif ai_decision == "ignore":
        print("AI suggested ignoring the error. Marking as successful.")
        task_instance.xcom_push(key="ai_decision", value="ignore")
    else:
        print("Escalating issue to engineers.")
        task_instance.xcom_push(key="ai_decision", value="escalate")

with DAG(
    'etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        on_failure_callback=handle_failure,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        on_failure_callback=handle_failure,
    )

    extract_task >> transform_task >> load_task
