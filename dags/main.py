import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

from datetime import timedelta
import utils.data_lake_helper as dl_helper

import raw_features
from raw_features import feature_extr_sub_dag

import vector_features
from vector_features import vector_extr_sub_dag

import xgboost_subdag
from xgboost_subdag import xgboost_sub_dag

import naive_bayes_subdag
from naive_bayes_subdag import naive_bayes_sub_dag

from report_subdag import report_sub_dag

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

parent_dag_name = 'nlp_text_classification'

dag = DAG(
    parent_dag_name,
    default_args=default_args,
    schedule_interval="@once")

start = DummyOperator(
    task_id="start",
    dag=dag
)

main_path = 'source/dataset/'
data_lake = dl_helper.DataLake(version='v3')
file_extension = '.txt'

raw_features.init(main_path, data_lake, file_extension)
vector_features.init(main_path, data_lake, file_extension)
xgboost_subdag.init(main_path, data_lake, file_extension)
naive_bayes_subdag.init(main_path, data_lake, file_extension)

#================#

child_dag_name = 'raw_features_extraction'
raw_extr_subdag = SubDagOperator(
    subdag=feature_extr_sub_dag(parent_dag_name, child_dag_name, default_args, dag.schedule_interval),
    task_id=child_dag_name,
    default_args=default_args,
    dag=dag)

start >> raw_extr_subdag

#================#

child_dag_name = 'vector_features_extraction'
vector_extr_subdag = SubDagOperator(
    subdag=vector_extr_sub_dag(parent_dag_name, child_dag_name, default_args, dag.schedule_interval),
    task_id=child_dag_name,
    default_args=default_args,
    dag=dag)

start >> vector_extr_subdag

#================#

def fit_lda():
    lda_model = Feature.MyLDA(config=data_lake.load_config('lda_config.txt'))
    xtrain_tfidf_ngram = data_lake.load_npz('xtrain_tfidf_ngram' + '.npz')

    X_topics = lda_model.model.fit_transform(xtrain_tfidf_ngram)

    data_lake.save_obj(X_topics, 'X_topics' + '.pkl')
    data_lake.save_obj(lda_model, 'lda_model' + '.pkl')

ldanode = PythonOperator(
            task_id= 'get_lda_topics',
            python_callable=fit_lda,
            dag=dag)

vector_extr_subdag >> ldanode

#================#

stage_1 = DummyOperator(
    task_id="stage_1",
    dag=dag
)

[raw_extr_subdag, ldanode] >> stage_1

#================#

child_dag_name = 'xgboost_subdag'
xgboost_subdag = SubDagOperator(
    subdag=xgboost_sub_dag(parent_dag_name, child_dag_name, default_args, dag.schedule_interval),
    task_id=child_dag_name,
    default_args=default_args,
    dag=dag)

stage_1 >> xgboost_subdag

#================#

child_dag_name = 'naive_bayes_subdag'
naive_bayes_subdag = SubDagOperator(
    subdag=naive_bayes_sub_dag(parent_dag_name, child_dag_name, default_args, dag.schedule_interval),
    task_id=child_dag_name,
    default_args=default_args,
    dag=dag)

stage_1 >> naive_bayes_subdag

#================#

stage_2 = DummyOperator(
    task_id="stage_2",
    dag=dag
)

[xgboost_subdag, naive_bayes_subdag] >> stage_2

#================#

child_dag_name = 'report_subdag'
report_subdag = SubDagOperator(
    subdag=report_sub_dag(parent_dag_name, child_dag_name, default_args, dag.schedule_interval),
    task_id=child_dag_name,
    default_args=default_args,
    dag=dag)

stage_2 >> report_subdag


