import abc
import logging.config
from time import sleep
import mysql.connector
from datetime import datetime
import os

logger = logging.getLogger('simpleExample')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBaseInterface(metaclass=Singleton):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'connect') and
                callable(subclass.connect) or
                NotImplemented)

    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError


class DataBase(DataBaseInterface):
    mydb = None

    def connect(self,
                host=os.environ["MYSQL_HOST"],
                user=os.environ["MYSQL_USER"],
                passwd=os.environ["MYSQL_PASSWD"],
                database=os.environ["MYSQL_DB"]):

        dbup = False
        max_attempts = 3
        current_attempt = 0
        while not dbup and max_attempts > current_attempt:
            try:
                mydb = mysql.connector.connect(
                    host=host,
                    user=user,
                    passwd=passwd,
                    database=database
                )
                dbup = True
                self.mydb = mydb

            except mysql.connector.errors.InterfaceError:
                sleep(5)
                current_attempt += 1
                print("reconnecting")

    def get_categories(self, args):
        if 'id' not in args:
            return "Error: No id field provided. Please specify an id."

        query = "SELECT * FROM models WHERE"
        query += ' id='
        query += str(args['id'])

        query += ' ORDER BY version DESC'
        query += ' LIMIT 1'
        query += ';'

        logger.info(query)
        mycursor = self.mydb.cursor()
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        return myresult

    def get_prediction(self, model_name, model_version):
        return "some letter prediction"

    def get_latest_version(self, model_name):
        # TODO: should look in DB predictions TABLE for the latest versino of model_name
        return "2.4"

    def insert_prediction(self, result, text_id, model_info):
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO predictions (document_id, predicted_class, date_created, time_spent, model_id) "
        sql += "VALUES (%s, %s, %s, %s, %s)"
        val = (text_id, result.value, date_time, result.time_spent, model_info.id)

        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)
        self.mydb.commit()

    def print_all(self, table_name):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM " + table_name)
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
