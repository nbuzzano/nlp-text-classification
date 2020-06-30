import logging.config
import pika
import os
import json
import abc

class MessageBrokerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'connect') and
                callable(subclass.connect) and
                hasattr(subclass, 'start_consuming') and
                callable(subclass.start_consuming) or
                NotImplemented)

    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError

    @abc.abstractmethod
    def start_consuming(self, callback):
        raise NotImplementedError

class RabbitMQ(MessageBrokerInterface):

    channel = None
    logger = logging.getLogger('simpleExample')
    custom_callback = None

    def connect(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)
        self.channel = channel

    def start_consuming(self, custom_callback):
        self.custom_callback = custom_callback
        channel = self.channel
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=self.callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def send_message(self, message):
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        log = " [x] Sent %r" % message
        self.logger.info(log)

    def callback(self, ch, method, properties, body):
        self.logger.info(" [x] Received %r" % body)
        self.logger.info(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

        data = json.loads(body)
        self.custom_callback(ch, method, properties, data)

class CustomRabbitMQ(RabbitMQ):

    def enqueue_classification_task(self, id):
        """El web server manda dos tipos de mensajes
            ● Clasificación: contienen un id para clasificar.
        """
        dic_msg = {"req_type": "clasif", "id": id}
        self.send_message(dic_msg)
        return dic_msg

    def enqueue_storage_task(self, id, doc_text):
        """El web server manda dos tipos de mensajes
            ● Storage: contiene un id y un texto para almacenar y clasificar.
        """
        dic_msg = {"req_type": "storage", "id": id, "text": doc_text}
        self.send_message(dic_msg)
        return dic_msg

    def enqueue_error_task(self, error_msg):
        """Cola de errores:
            - Recibe mensajes de error del servicio de storage y clasificación.
        """
        self.logger.error(error_msg)
        pass