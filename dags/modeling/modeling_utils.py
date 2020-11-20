
class ModelTemplate():
    def __init__(self, name, xvalid, xtrain, classifier):
        self.xvalid_value = xvalid
        self.xtrain_value = xtrain
        self.name_value = name
        self.classifier = classifier