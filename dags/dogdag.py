from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from modules import modules


setup = {
    'owner': 'xadrianzetx',
    'depends_on_past': False,
    'start_date': datetime(2019, 12, 30),
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_doggos',
    description="Daily reddit doggos. use r.get('%d.%m.%Y') to get metadata",
    default_args=setup,
    schedule_interval='00 12 * * *'
)


t1 = PythonOperator(
    task_id='get_reddit_hot',
    provide_context=True,
    python_callable=modules.get_subreddit_top,
    dag=dag
)

t2 = PythonOperator(
    task_id='send_messages',
    provide_context=True,
    python_callable=modules.push_message,
    dag=dag
)

t2.set_upstream(t1)
