import abc
from enum import Enum, unique
import os.path

@unique
class StorageType(Enum):
    log = 1
    model = 2
    file = 3

    def path(self) -> str:
        #TODO: REPLACE THIS PATHS FOR ENV VARIABLES
        if self.value == StorageType.log.value:
            return "../storage/logs/"
        elif self.value == StorageType.model.value:
            return "../storage/models/"
        elif self.value == StorageType.file.value:
            return "../storage/files/"

class StorageInterface(metaclass=abc.ABCMeta):

    """
        Mantiene una carpeta con los archivos a clasificar guardados, cada archivo tiene como nombre su id.

        Mantiene una carpeta con los logs del
            - web server y
            - el servicio de storage y clasificación.

        Mantiene una carpeta con los modelos para el servicio de clasificación.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_resource') and
                callable(subclass.get_resource) and
                hasattr(subclass, 'set_resource') and
                callable(subclass.set_resource) or
                NotImplemented)

    @abc.abstractmethod
    def get_resource(self, type: StorageType, resource_name: str):
        """Get resource from storage"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_resource(self, type: StorageType, resource_name: str, resource_text: str):
        """Save resource into storage"""
        raise NotImplementedError

class MyStorage(StorageInterface):

    def get_resource(self, type: StorageType, resource_name: str):
        """Overrides StorageInterface.get_resource()"""

        if type.value == StorageType.log.value:
            raise NotImplementedError
        elif type.value == StorageType.model.value:
            raise NotImplementedError
        elif type.value == StorageType.file.value:
            file_path = type.path() + resource_name + ".txt"
            with open(file_path, 'r') as f:
                file = f.read()
                return file

    def set_resource(self, type: StorageType, resource_name: str, resource_text: str):
        """Overrides StorageInterface.set_resource()"""

        if type.value == StorageType.log.value:
            raise NotImplementedError
        elif type.value == StorageType.model.value:
            raise NotImplementedError
        elif type.value == StorageType.file.value:

            save_path = type.path()
            name_of_file = resource_name
            to_file = resource_text

            complete_path = os.path.join(save_path, name_of_file + ".txt")
            file_to_save = open(complete_path, "w")
            file_to_save.write(to_file)
            file_to_save.close()
