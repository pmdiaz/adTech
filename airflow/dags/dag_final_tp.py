import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


ruta_real = os.path.realpath(__file__)
directorio_dags = os.path.dirname(ruta_real)
directorio_base = os.path.dirname(directorio_dags)
directorio_tasks = os.path.join(directorio_base, "tasks")
sys.path.append(directorio_tasks)

import filter_data
import top_ctr
import top_product
import db_writing

default_args = {
    "owner": "valen",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dag_final_tp",
    default_args=default_args,
    description="Pipeline final TP",
    schedule="0 5 * * *",
    start_date=datetime(2026, 4, 20),
    catchup=False,
    tags=["tp", "final"],
) as dag:

    filter_data_task = PythonOperator(
        task_id="filter_data",
        python_callable=filter_data.run,
        op_kwargs={'ds': '{{ ds }}'}
    )

    top_ctr_task = PythonOperator(
        task_id="top_ctr",
        python_callable=top_ctr.run,
        op_kwargs={'ds': '{{ ds }}'}
    )

    top_product_task = PythonOperator(
        task_id="top_product",
        python_callable=top_product.run,
        op_kwargs={'ds': '{{ ds }}'}
    )

    db_writing_task = PythonOperator(
        task_id="db_writing",
        python_callable=db_writing.run,
        op_kwargs={'ds': '{{ ds }}'}
    )

    filter_data_task >> [top_ctr_task, top_product_task]
    [top_ctr_task, top_product_task] >> db_writing_task
