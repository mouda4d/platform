from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'mouda',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='fx_rates_dag',
    default_args=default_args,
    schedule='30 08 * * 2-6',  # Tuesday through Saturday at 08:30 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    run_ingestion = BashOperator(
        task_id='run_fx_rates_python_script',
        bash_command='python /opt/airflow/dags/xrate_api_request.py'
    )