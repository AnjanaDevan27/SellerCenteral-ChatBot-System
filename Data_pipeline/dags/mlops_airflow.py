from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from dataflow_processing import read_csv_from_gcp, create_bigquery_dataset, upload_to_bigquery #, validate_data_with_tfdv
from fetch_data import upload_to_gcs_from_url
from data_process import save_csv_to_gcs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),  
    'email': ['kaviarasu666@gmail.com'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    "mlops_csv_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,  
)
fetch_data = PythonOperator(
    task_id="fetch_data",
    python_callable=upload_to_gcs_from_url,
    provide_context=True, 
    dag=dag
)
data_processing = PythonOperator(
    task_id="data_processing",
    python_callable=save_csv_to_gcs,
    provide_context=True, 
    dag=dag
)
read_csv = PythonOperator(
    task_id="read_csv",
    python_callable=read_csv_from_gcp,
    provide_context=True, 
    dag=dag
)

create_dataset = PythonOperator(
    task_id='create_dataset',
    python_callable=create_bigquery_dataset,
    dag=dag,
)
# Anamoly = PythonOperator(
#     task_id='Anamoly',
#     python_callable=validate_data_with_tfdv,
#     op_kwargs={"df": "{{ task_instance.xcom_pull(task_ids='read_csv') }}"},  
#     dag=dag,
# )

upload_bigquery = PythonOperator(
    task_id='upload_bigquery',
    python_callable=upload_to_bigquery,
    provide_context=True,
    dag=dag,
)

fetch_data >> data_processing >> read_csv >> create_dataset >> upload_bigquery
