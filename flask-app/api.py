import logging.config
import os

import flask
from flask import request

from utils import db_utils
from utils import storage
from utils import rabbitmq

app = flask.Flask(__name__)
app.config["DEBUG"] = True
# if app.config["DEBUG"] = True then I can change function return and will be automatically changes on the browser,
# without neccesity of rerunning the file

logging.config.fileConfig('logger.conf')
logger = logging.getLogger('simpleExample')

db_utils.DataBase().connect()
database = db_utils.DataBase()

storage = storage.MyStorage()

broker = rabbitmq.CustomRabbitMQ()
broker.connect()

@app.route('/', methods=['GET'])
def home():
    return '''<h1>HOME</h1>'''


@app.route('/api/v1/file', methods=['GET', 'POST'])
def file():

    args = request.args

    if request.method == 'GET':
        """ Returns a file from the storage, or an error if it's the case.
                :param id: the text id which is desired to be returned    
        """
        if 'id' in args:
            id = args['id']
        else:
            return "Error: wrong parameters"

        try:
            return storage.get_resource(storage.StorageType.file, resource_name=id)
        except:
            return "Error: using storage"


    elif request.method == 'POST':
        """ Sends a file to the message broker queue to be saved on the storage
                :param id: the text id which is desired to be stored
                :param text: the text which is desired to be stored
        """
        if 'id' in args and 'text' in args:
            id = args['id']
            text = args['text']
        else:
            return "Error: wrong parameters"

        try:
            result = broker.enqueue_storage_task(id=id, doc_text=text)
            return result
        except:
            return "Error using message broker"


@app.route('/api/v1/category', methods=['GET'])
def category():
    """Returns the text classification for the a certain text id.
    If the text id wasn't found OR the classifier version is old,
    then a request to message broker to classify that text should be made.

    :param id: the text id which classification is desired to be returned
    """

    args = request.args

    if 'id' in args:
        id = args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    try:
        result = database.get_categories(args)
    except:
        return "Error using database"

    if len(result) > 0:
        newest_category = result[0]
        newest_category_name = newest_category[1]
        newest_category_version = newest_category[2]
        try:
            if newest_category_version == database.get_latest_version(newest_category_name):
                return database.get_prediction(model_name=newest_category_name, model_version=newest_category_version)
        except:
            return "Error using database"

        result = enqueue_classification_task(id=id)
        return result

    else:
        result = enqueue_classification_task(id=id)
        return result


def enqueue_classification_task(id):
    try:
        result = broker.enqueue_classification_task(id=id)
        return result
    except:
        return "Error using broker"

app.run(host=os.environ["WEB_SERVER_HOST"])
