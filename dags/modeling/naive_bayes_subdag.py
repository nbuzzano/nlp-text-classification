import airflow
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

from sklearn import naive_bayes
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score

import os
from datetime import datetime
from sklearn.metrics import classification_report

from sklearn.preprocessing import LabelEncoder
from features_utils import ModelTemplate
import utils.data_lake_helper as dl_helper
from functools import partial
import pandas as pd

import mlflow
import mlflow.sklearn

main_path = None
data_lake = None
file_extension = None

templates = None

mlflow.set_experiment(experiment_name='NLP text classifier')


def init(main_path_, data_lake_, file_extension_):
    global main_path
    global data_lake
    global file_extension
    
    main_path = main_path_
    data_lake = data_lake_
    file_extension = file_extension_

    create_templates()

def get_nb_model():
    params = data_lake.load_config('nb_config.txt')
    nb = naive_bayes.MultinomialNB()
    nb.set_params(**params)
    return nb

def create_templates():

    global templates

    # Count Vectors as features
    ########################################

    nb_count_template = ModelTemplate(name='NB_Count_Vectors', 
                                    xvalid='xvalid_count.npz', 
                                    xtrain='xtrain_count.npz',
                                    classifier=get_nb_model())

    # word level tf-idf
    ###################

    nb_word_level_tfidf_template = ModelTemplate(name='NB_WordLevel_TF-IDF', 
                                                xvalid='xvalid_tfidf.npz', 
                                                xtrain='xtrain_tfidf.npz',
                                                classifier=get_nb_model())

    # ngram level tf-idf 
    ####################

    nb_ngram_level_tfidf_template = ModelTemplate(name='NB_NGramLevel_Vectors', 
                                                xvalid='xvalid_tfidf_ngram.npz', 
                                                xtrain='xtrain_tfidf_ngram.npz',
                                                classifier=get_nb_model())

    # characters level tf-idf
    #########################

    nb_char_level_tfidf_template = ModelTemplate(name='NB_CharLevel_Vectors', 
                                                xvalid='xvalid_tfidf_ngram_chars.npz', 
                                                xtrain='xtrain_tfidf_ngram_chars.npz',
                                                classifier=get_nb_model())


    templates = [nb_count_template,
                nb_word_level_tfidf_template,
                nb_ngram_level_tfidf_template,
                nb_char_level_tfidf_template]


def prepare_data(df_):
    train_x = df_['text_normalized'].tolist()
    train_y = df_.category.tolist()
    return (train_x, train_y)


def get_cleaned_df():

    df = pd.read_csv('source/features/' + data_lake.version + '/df-cleaned.csv')

    feature = 'text_normalized'
    df[feature] = data_lake.load_obj(feature + '.pkl')

    df_train_table = df[df.path == (main_path + 'train_set/')]
    df_test_table = df[df.path == (main_path + 'test_set/')]

    _, train_y = prepare_data(df_train_table)
    _, valid_y = prepare_data(df_test_table)

    # label encode the target variable 
    encoder = LabelEncoder()
    train_y = encoder.fit_transform(train_y)
    valid_y = encoder.fit_transform(valid_y)

    return train_y, valid_y


def create_report_folder():
    #create version folder if not exists
    path = 'source/ml-reports'
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def train_model(classifier, feature_vector_train, label, feature_vector_valid, valid_y, is_neural_net=False):

    df = pd.read_csv('source/features/' + data_lake.version + '/df-cleaned.csv')
    letter_types = sorted(df.category.unique().tolist())

    # fit the training dataset on the classifier
    classifier.fit(feature_vector_train, label)
    
    # predict the labels on validation dataset
    predictions = classifier.predict(feature_vector_valid)
    recall = recall_score(valid_y, predictions, average=None)
    
    if len(letter_types) != len(recall):
        raise Exception('len(letter_types) != len(recall) ' + str(len(letter_types)) + ' != '+ str(len(recall)))
        
    report = classification_report(valid_y, predictions, target_names=letter_types)
    
    path = 'source/ml-reports/'
    report_name = 'nb-report-' + datetime.today().strftime('%Y-%m-%d-%Hhr%Mmin')
    report_path = path + report_name + '.txt'
    
    try:
        create_report_folder()
        file = open(report_path, "w") 
        file.write(report) 
        file.close() 
    
    except:
        raise Exception('problem opening and/or saving algorithm report')
    
    with mlflow.start_run():
        #MLflow
        mlflow.sklearn.log_model(classifier, "nb-model")
        mlflow.log_artifact('source/configs/nb_config.txt')
        mlflow.log_artifact(report_path)
        
    
    return report

def create_trainable_model_node(get_df_fc, model_template):
    train_y, valid_y = get_df_fc()
    xvalid = data_lake.load_npz(model_template.xvalid_value)
    xtrain = data_lake.load_npz(model_template.xtrain_value)
    accuracy = train_model(model_template.classifier, xtrain.tocsc(), train_y, xvalid.tocsc(), valid_y)
    print(model_template.name_value + ": ", accuracy) 


def naive_bayes_sub_dag(parent_dag_name, child_dag_name, args, schedule_interval):

    dag = DAG('%s.%s' % (parent_dag_name, child_dag_name),
            default_args=args,
            start_date=args['start_date'],
            max_active_runs=1)

    start = DummyOperator(task_id="start", dag=dag)

    template_nodes = []
    for t in templates:
        partial_fc = partial(create_trainable_model_node, get_cleaned_df)
        node = PythonOperator(
            task_id= 'train_' + t.name_value,
            python_callable=partial(partial_fc, t),
            dag=dag)
        template_nodes.append(node)

    start >> template_nodes

    return dag