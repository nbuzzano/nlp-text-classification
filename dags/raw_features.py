import utils.airflow_features as Features
import utils.data_lake_helper as dl_helper

from functools import partial

import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

from features_utils import get_main_spark_df

from pyspark.sql.functions import udf
from pyspark.sql.types import *
from pyspark.sql.functions import *

main_path = None
data_lake = None
file_extension = None

#loading features to extract from letters
features = [Features.Length(),
		Features.Word_Count(),
		Features.Enum_Presence(),
		Features.Enum_Count(),
		Features.Enum_Repeated(),
		Features.SEC_Header(),
		Features.Response_Text(),
		Features.Comment_Text(),
		Features.Text_Normalizer()]


def init(main_path_, data_lake_, file_extension_):
	global main_path
	global data_lake
	global file_extension
	
	main_path = main_path_
	data_lake = data_lake_
	file_extension = file_extension_


def extract_feature(f, pk_id, path_):
	text_path = path_ + str(pk_id) + '.txt'
	text = open(text_path).read()
	t = f.transform(text)
	return t


def map_feature(feature):
    df = get_main_spark_df()
    
    partial_extract_feature = partial(extract_feature, feature)
	udf_partial_extract_feature = udf(partial_extract_feature, StringType())
	feature_extracted = df.withColumn(feature.name, udf_partial_extract_feature("pk_id", "path"))

	cols = ['category','master_tree','file_type','path']
	for c in cols:
		feature_extracted = feature_extracted.drop(c)
	
	#p = 'source/features/' + data_lake.version + <feature-name>
	feature_extracted.repartition(10, col("pk_id"))\
						.write.parquet("data/" + feature.name + "_parquet", mode="overwrite")


def get_raw_features(dag):
	nodes = []
	for feature in features:

		node = PythonOperator(
			task_id= 'get_' + feature.name,
			python_callable=partial(map_feature, feature),
			dag=dag)

		nodes.append(node)

	return nodes


def get_prefix_features(features):
	prefix_nodes = []
	for n in features:
		if n.task_id == 'get_' + Features.Word_Count().name:
			prefix_nodes.append(n)
		if n.task_id == 'get_' + Features.Length().name:
			prefix_nodes.append(n)

	return prefix_nodes


def get_word_density():
	
	#p = 'source/features/' + data_lake.version + <feature-name>
	
	path = "data/" + Features.Length().name + "_parquet"
    letter_lenght = pd.read_parquet(path, engine='pyarrow')#fastparquet
    letter_lenght["letter_lenght"] = letter_lenght["letter_lenght"].astype(int) 
    
    path = "data/" + Features.Word_Count().name + "_parquet"
    word_count = pd.read_parquet(path, engine='pyarrow')#fastparquet
    word_count["word_count"] = word_count["word_count"].astype(int) 
    
    word_density = letter_lenght["letter_lenght"]/(word_count["word_count"]+1)
    word_density = pd.DataFrame(word_density)
    word_density.index = letter_lenght.pk_id
    word_density.columns = ['word_density']
    
    wd_name = 'word_density'
    word_density.to_parquet("data/" + wd_name + "_parquet", engine='pyarrow')


def feature_extr_sub_dag(parent_dag_name, child_dag_name, args, schedule_interval):

	dag = DAG('%s.%s' % (parent_dag_name, child_dag_name),
			default_args=args,
			start_date=args['start_date'],
			max_active_runs=1)

	start = DummyOperator(task_id="start", dag=dag)
	
	raw_features = get_raw_features(dag)
	
	start >> raw_features

#================#

	word_density_node = PythonOperator(
		task_id= 'get_word_density',
		python_callable=get_word_density,
		dag=dag)

	get_prefix_features(raw_features) >> word_density_node

#================#

	return dag
