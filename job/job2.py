import sys
import logging

import utils.db_utils as db_utils
import utils.storage as storage
import utils.rabbitmq as rabbitmq

sys.path.append('../experiments')
import prediction

class Job:

    logging.config.fileConfig('logger.conf')
    logger = logging.getLogger('simpleExample')

    db_utils.DataBase().connect()
    database = db_utils.DataBase()

    storage = storage.MyStorage()

    broker = rabbitmq.CustomRabbitMQ()
    broker.connect()

    model = prediction.ModelFactory.build(model_name='dummy')

    def connect(self):
        self.broker.start_consuming(custom_callback=self.callback)

    def callback(self, ch, method, properties, data):

        req_type = data["req_type"]

        if req_type == "clasif":
            self.handle_clasif_request(data)
        elif req_type == "storage":
            self.handle_storage_request(data)

    def handle_clasif_request(self, data):
        """
        Classifier
        Escucha la cola de mensajes, clasifica los ids que recibe si se encuentran en el storage,
         guarda en la base de datos el id con los resultados y la versión del clasificador,
         caso contrario escribe en una cola de errores.
        """
        self.logger.info("handle_clasif_request STARTED")

        if 'id' in data:
            id = data['id']
        else:
            self.broker.enqueue_error_task(error_msg="handle_clasif_request :: missing parameter")

        try:
            text = self.storage.get_resource(type=storage.StorageType.file, resource_name=id)
        except:
            self.broker.enqueue_error_task(error_msg="Error using storage")
            return

        result = self.model.predict(text)

        try:
            self.database.insert_prediction(result=result, text_id=id, model_info=self.model.info())
        except:
            self.broker.enqueue_error_task(error_msg="Error using database")
            return

        self.logger.info("handle_clasif_request FINISHED")

    def handle_storage_request(self, data):
        """
        Storage
        Escucha la cola de mensajes, guarda los textos que recibe con los ids como nombre en el storage.
        También los clasifica y guarda en la base de datos el id con los resultados y la versión del clasificador.
        """
        self.logger.info("handle_storage_request STARTED")

        if 'id' in data and 'text' in data:
            id = data['id']
            text = data['text']
        else:
            self.broker.enqueue_error_task(error_msg="handle_storage_request :: missing parameter")

        try:
            self.storage.set_resource(type=storage.StorageType.file, resource_name=id, resource_text=text)
        except:
            self.broker.enqueue_error_task(error_msg="Error using storage")

        result = self.model.predict(text)

        try:
            self.database.insert_prediction(result=result, text_id=id, model_info=self.model.info())
        except:
            self.broker.enqueue_error_task(error_msg="Error using database")

        self.logger.info("handle_storage_request FINISHED")


job = Job()
job.connect()