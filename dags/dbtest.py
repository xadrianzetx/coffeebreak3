from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from modules import modules


setup = {
    'owner': 'xadrianzetx',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(minutes=2),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'redis_test',
    default_args=setup,
    schedule_interval=timedelta(minutes=5)
)

t1 = PythonOperator(
    task_id='ping',
    provide_context=False,
    python_callable=modules.redis_ping_test,
    dag=dag
)

t2 = PythonOperator(
    task_id='set',
    provide_context=False,
    python_callable=modules.redis_set_test,
    dag=dag
)

t3 = PythonOperator(
    task_id='get',
    provide_context=False,
    python_callable=modules.redis_get_test,
    dag=dag
)

t2.set_upstream(t1)
t3.set_upstream(t2)
