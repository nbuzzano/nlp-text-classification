import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def report_sub_dag(parent_dag_name, child_dag_name, args, schedule_interval):
    dag = DAG(
        '%s.%s' % (parent_dag_name, child_dag_name),
        default_args=args,
        start_date=args['start_date'],
        max_active_runs=1,
    )

    start = DummyOperator(
        task_id="start",
        dag=dag
    )
    
    task_1 = DummyOperator(
        task_id="post_notifications",
        dag=dag
    )

    task_2 = DummyOperator(
        task_id="make_reports",
        dag=dag
    )

    task_3 = DummyOperator(
        task_id="create_dashboards",
        dag=dag
    )
    
    start >> [task_1, task_2, task_3]

    return dag