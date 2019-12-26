from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from modules import modules


setup = {
    'owner': 'xadrianzetx',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(minutes=1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('scheduler_test', default_args=setup, schedule_interval=timedelta(minutes=1))

t1 = PythonOperator(
    task_id='test',
    provide_context=False,
    python_callable=modules.check_scheduler,
    dag=dag
)