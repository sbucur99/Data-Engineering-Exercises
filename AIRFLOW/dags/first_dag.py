from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(
    dag_id="first_dag",
    start_date=datetime(2026,10,1),
    schedule="@daily",
    catchup=False
) as dag:

    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="end")

    start >> end