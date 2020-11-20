import os
import pickle
from scipy import sparse
import ast

class DataLake:
    
    main_path = '../../source/'
    
    def __init__(self, version):
        self.version = version 
        features_path = 'features/'
        self.version_path = self.main_path + features_path + version + "/"
        
        #create version folder if not exists
        if not os.path.exists(self.version_path[:-1]):
            try:
                os.makedirs(self.version_path[:-1])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
    
    def save_obj(self, obj, file_name):
        with open(self.version_path + file_name, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
    
    def save_npz(self, obj, file_name):
        sparse.save_npz(self.version_path + file_name, obj)
    
    def load_npz(self, file_name):
        return sparse.load_npz(self.version_path + file_name)
    
    def load_obj(self, obj_name):
        with open(self.version_path + obj_name, 'rb') as input:
            return pickle.load(input)
        
    def load_config(self, file_name):
        config_path = self.main_path + 'configs/' + self.version + "/"
        file = open(config_path + file_name, "r")
        contents = file.read()
        return ast.literal_eval(contents)

