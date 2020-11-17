import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.functions import lit

# Create Spark session
spark = SparkSession.builder \
    .master("local") \
    .config("spark.sql.autoBroadcastJoinThreshold", -1) \
    .config("spark.executor.memory", "500mb") \
    .appName("Test01") \
    .getOrCreate()


def get_main_spark_df():
    
    main_path = 'source/dataset/'
    
    #setting up dataframe 
    df_train_table = spark.read.options(header='True', inferSchema='True').csv(main_path + 'train_set.csv')
    df_train_table = df_train_table.withColumn('path', lit(main_path + 'train_set/'))
    
    df_test_table = spark.read.options(header='True', inferSchema='True').csv(main_path + 'test_set.csv')
    df_test_table = df_test_table.withColumn('path', lit(main_path + 'test_set/'))
    
    df = df_train_table.union(df_test_table)

    df = df.drop('master_tree')

    return df


def get_main_df():
    
    #setting up dataframe 
    main_path = 'source/dataset/'
    df_train_table = pd.read_csv(main_path + 'train_set.csv')
    df_train_table.index = df_train_table.pk_id
    df_train_table['path'] = main_path + 'train_set/'
    del df_train_table['pk_id']

    df_test_table = pd.read_csv(main_path + 'test_set.csv')
    df_test_table.index = df_test_table.pk_id
    df_test_table['path'] = main_path + 'test_set/'
    del df_test_table['pk_id']

    df = df_train_table.append(df_test_table, sort=False)

    del df['master_tree']
    del df['file_type']
    del df['category']

    return df



class ModelTemplate():
    def __init__(self, name, xvalid, xtrain, classifier):
        self.xvalid_value = xvalid
        self.xtrain_value = xtrain
        self.name_value = name
        self.classifier = classifier