# NLP: texts classification ! 

In this repository you can find the development of a service for an application that analyzes public documents. The solutions covers preprocessing and classification of texts.

To build it, different technologies were used. For example Apache Airflow, Docker and Spark regarding to data engineering side. Also, Keras and sklearn regarding to machine learning side.

Several ML algorithms were trained and tested. Some of them were: 

1. Self Normalizing NN
1. Feed Forward NN + LDA topics
1. Recurrent NN: LSTM, GRU, LSTM & GRU bidirectional


.


1. Naive Bayes model
1. Xgboost
1. Stacking Ensemble algorithms

### Discussion:

- `dags`: Airflow pipeline can be found here. Also `script` and `config` folders are consumed at Airflow init.

- `notebooks`: Here we explore the dataset, we look for insights that provide information to the business and to the modeling stage.

- `source`: Here you can find custom tools, prediction machine learning models. The input dataset is stored here.

- `resources`: Take a look to the architecture plan and how the Airflow pipeline looks here!

### How can I test this?:
1. Go to `source/` directory and store there the texts that you want to classify. A `README.md` file with an in deep explanation can be found there.
2. run `docker-compose up` and docker will do all the work for you. Just wait a little until all the services are up and running.
3. Paste `localhost:8081` url in your browser to open Airflow UI and run the pipeline.

### Next releases:

For a second stage, the plan is to migrate to a cloud solution. This is, integrate **AWS S3** and migrate Airflow to **Google Cloud Composer**. Also integrate **MLflow** in order to manage better reproducibility, deployment, and a central model registry.


### Airflow credits

- [Apache Airflow](https://github.com/apache/incubator-airflow)
- [docker-airflow](https://github.com/puckel/docker-airflow)
