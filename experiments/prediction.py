import abc

class ModelInfo:
    version = None
    name = None
    id = None


class ModelInterface(metaclass=abc.ABCMeta):

    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'info') and
                callable(subclass.info) and

                hasattr(subclass, 'predict') and
                callable(subclass.predict) or

                NotImplemented)

    @abc.abstractmethod
    def info(self):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, y_to_predict):
        raise NotImplementedError


class Result:
    time_spent = None
    value = None

class DummyModel(ModelInterface):

    def info(self):
        info = ModelInfo()
        info.name = "LSTM"
        info.version = "2.5"
        info.id = 1
        return info

    def predict(self, y_to_predict):
        result = Result()
        result.value = "some letter type"
        result.time_spent = 60
        return result

class ModelFactory:
    @classmethod
    def build(cls, model_name) -> ModelInterface:
        if model_name == "dummy":
            return DummyModel()
        else:
            raise Exception("model_name not defined")
