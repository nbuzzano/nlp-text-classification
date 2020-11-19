import utils.airflow_features as Features
import utils.data_lake_helper as dl_helper
from functools import partial

import airflow
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

from features_utils import get_main_df

main_path = None
data_lake = None
file_extension = None

def init(main_path_, data_lake_, file_extension_):
	global main_path
	global data_lake
	global file_extension
	
	main_path = main_path_
	data_lake = data_lake_
	file_extension = file_extension_


def fit_vector(vector):
    f_name = 'text_normalized'
    df = get_main_df()
    df[f_name] = data_lake.load_obj(f_name + '.pkl')
    train_x = df[df.path == (main_path + 'train_set/')][f_name]
    valid_x = df[df.path == (main_path + 'test_set/')][f_name]

    vector.model.fit(df[f_name])
    xtrain_v = vector.transform(train_x)
    xvalid_v = vector.transform(valid_x)

    #saving matrices
    data_lake.save_npz(xvalid_v, vector.xvalid_name + ".npz")
    data_lake.save_npz(xtrain_v, vector.xtrain_name + ".npz")
    data_lake.save_obj(vector, vector.name + ".pkl")


def vector_extr_sub_dag(parent_dag_name, child_dag_name, args, schedule_interval):

	vectors = []
	vectors.append(Features.MyCountVectorizer(config=data_lake.load_config('count_vect_config.txt')))
	vectors.append(Features.MyWordTfidfVectorizer(config=data_lake.load_config('tf_idf_word_vect_config.txt')))
	vectors.append(Features.MyNGramTfidfVectorizer(config=data_lake.load_config('tf_idf_n_gram_vect_config.txt')))
	vectors.append(Features.MyCharTfidfVectorizer(config=data_lake.load_config('tf_idf_char_vect_config.txt')))
	
	dag = DAG('%s.%s' % (parent_dag_name, child_dag_name),
			default_args=args,
			start_date=args['start_date'],
			max_active_runs=1)

	start = DummyOperator(task_id="start", dag=dag)

	feature_nodes = []
	for vector in vectors:

	    fnode = PythonOperator(
	        task_id= 'get_' + vector.name,
	        python_callable=partial(fit_vector, vector),
	        dag=dag)

	    feature_nodes.append(fnode)

	start >> feature_nodes

	return dag
