import re
import os
import time
import numpy as np
from random import randint
from functools import partial
import pickle
import ast
import string

from sklearn import decomposition, ensemble
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from nltk.stem import PorterStemmer 
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

punctuation_without_dot = list(filter(lambda x: x != '.' or x != ',' , string.punctuation))
STOPWORDS = list(set(stopwords.words('english'))) + punctuation_without_dot
#WARNING ! ! ! 
#There are several known issues with ‘english’ and you should consider an alternative.
#-> https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words

class Feature:
    
    def __init__(self):
        self.values = []
        self.name = ''
    
    def transform(self, text):
        pass

class Length(Feature):
    def __init__(self):
        self.name = 'letter_lenght'
        self.values = []
    
    def transform(self, text):
        return len(text)

class Word_Count(Feature):
    def __init__(self):
        self.name = 'word_count'
        self.values = []
    
    def transform(self, text):
        return len(text.split())

enumeration_regex = "\n[0-9]{1,2}[.]\s[a-zA-Z]"
enumeration_regex_2 = "\n[0-9]{1,2}[.]"

class Enum_Presence(Feature):
    def __init__(self):
        self.name = 'enumeration_presence'
        self.values = []
    
    def transform(self, text):
        enums = re.findall(enumeration_regex, text)
        enums_len = len(enums)
        return enums_len > 0

class Enum_Count(Feature):
    def __init__(self):
        self.name = 'enumeration_count'
        self.values = []
    
    def transform(self, text):
        enums = re.findall(enumeration_regex, text)
        enums_len = len(enums)
        return enums_len

class Enum_Repeated(Feature):
    def __init__(self):
        self.name = 'enumeration_repeated'
        self.values = []
    
    def transform(self, text):
        enums = re.findall(enumeration_regex, text)
        enums = re.findall(enumeration_regex_2, ' '.join(enums))
        
        unique_enums = list(set(enums))
        has_repeated_enums = not len(unique_enums) == len(enums)
        return has_repeated_enums

def look_for_text_list(text_list, text):
    text = text.lower()
    has_text = False
    for text_to_look_for in text_list:
        has_text = (text_to_look_for in text) or has_text
    return has_text

class SEC_Header(Feature):
    def __init__(self):
        self.name = 'sec_header_presence'
        self.values = []
        
        header_sentence_1 = 'UNITED STATES SECURITIES AND EXCHANGE COMMISSION'.lower()
        header_sentence_2 = 'WASHINGTON, D.C. 20549-4628'.lower()
        header_sentence_3 = 'DIVISION OF CORPORATION FINANCE'.lower()
        sec_headers = [header_sentence_1, header_sentence_2, header_sentence_3]
        sec_headers = ' '.join(sec_headers)

        self.look_for_sec_headers = partial(look_for_text_list, sec_headers)
    
    def transform(self, text):
        return look_for_sec_headers(text)

class Response_Text(Feature):
    def __init__(self):
        self.name = 'response_presence'
        self.values = []
        
        rl_sentence_2 = 'response :'.lower()
        rl_sentence_4 = 'responses :'.lower()
        rl_headers = [rl_sentence_2, rl_sentence_4]
        self.look_for_rl_headers = partial(look_for_text_list, rl_headers)
    
    def transform(self, text):
        return look_for_rl_headers(text)

class Comment_Text(Feature):
    def __init__(self):
        self.name = 'cl_sentence_presence'
        self.values = []
        
        cl_sentence_1 = 'We have reviewed your filing and have the following comments.'.lower()
        cl_sentence_2 = 'After reviewing your response to these comments, we may have additional comments.'.lower()
        cl_headers = [cl_sentence_1, cl_sentence_2]

        self.look_for_cl_headers = partial(look_for_text_list, cl_headers)
    
    def transform(self, text):
        return look_for_cl_headers(text)


#=========#=========#=========#=========#=========#=========#=========#=========#=========#=========#

class TextToLower(TransformerMixin, BaseEstimator):
    def fit(self, x, y=None):
        return self
    def transform(self, texts):
        return [text.lower() for text in texts]
        
class TextWithOutStopWords(TransformerMixin, BaseEstimator):
    def fit(self, x, y=None):
        return self
    def transform(self, texts):
        texts_ = []
        for text in texts:
            text = text.replace('\n', ' ')
            text = " ".join([i for i in word_tokenize(text) if i not in STOPWORDS])
            texts_.append(text)
        
        return texts_

class TextWithOutNonASCII(TransformerMixin, BaseEstimator):
    def fit(self, x, y=None):
        return self
    def transform(self, texts):
        texts_ = []
        for text in texts:
            text = text.encode("ascii", "ignore").decode()
            texts_.append(text)
        
        return texts_
    
ps = PorterStemmer() 
class TextStemming(TransformerMixin, BaseEstimator):
    def fit(self, x, y=None):
        return self
    def transform(self, texts):
        texts_ = []
        for text in texts:
            tokenized_words = word_tokenize(text)
            for i, w in enumerate(tokenized_words):
                tokenized_words[i] = ps.stem(w)
                text = ' '.join(tokenized_words)
            
            texts_.append(text)
        
        return texts_

class Text_Normalizer(Feature):
    def __init__(self):
        self.name = 'text_normalized'
        self.values = []
        self.pipeline = Pipeline([
            ("T_to_L", TextToLower()),
            ("T_no_SW", TextWithOutStopWords()),
            ("T_no_ascii", TextWithOutNonASCII()),
            ("TS", TextStemming())#PROBAR TMB CON Lemmatization !!!
            ])
    
    def transform(self, text):
        return self.pipeline.transform([text])[0]

#=========#=========#=========#=========#=========#=========#=========#=========#=========#=========#

class MyCountVectorizer():
    def __init__(self, config):
        self.xvalid_name = 'xvalid_count'
        self.xtrain_name = 'xtrain_count'
        self.name = 'count_vect'
        #TODO: probar otros valores para max_features, 1D uso 50.000
        self.model = CountVectorizer(analyzer=config['analyzer'],
                                    token_pattern=config['token_pattern'],
                                    ngram_range=config['ngram_range'])
    
    def transform(self, texts):
        return self.model.transform(texts)

#=========#

class MyWordTfidfVectorizer():
    def __init__(self, config):
        self.xvalid_name = 'xvalid_tfidf'
        self.xtrain_name = 'xtrain_tfidf'
        self.name = 'tf_idf_word_vect'
        #TODO: probar otros valores para max_features, 1D uso 50.000
        self.model = TfidfVectorizer(analyzer=config['analyzer'],
                                    token_pattern=config['token_pattern'],
                                    max_features=config['max_features'])
    
    def transform(self, texts):
        return self.model.transform(texts)

#=========#

class MyNGramTfidfVectorizer():
    def __init__(self, config):
        self.xvalid_name = 'xvalid_tfidf_ngram'
        self.xtrain_name = 'xtrain_tfidf_ngram'
        self.name = 'tfidf_vect_ngram'
        #TODO: probar otros valores para max_features, 1D uso 50.000
        self.model = TfidfVectorizer(analyzer=config['analyzer'],
                                    token_pattern=config['token_pattern'],
                                    ngram_range=config['ngram_range'],
                                    max_features=config['max_features'])
    
    def transform(self, texts):
        return self.model.transform(texts)

#=========#

class MyCharTfidfVectorizer():
    def __init__(self, config):
        self.xvalid_name = 'xvalid_tfidf_ngram_chars'
        self.xtrain_name = 'xtrain_tfidf_ngram_chars'
        self.name = 'tfidf_vect_char'
        #TODO: probar otros valores para max_features, 1D uso 50.000
        self.model = TfidfVectorizer(analyzer=config['analyzer'],
                                    token_pattern=config['token_pattern'],
                                    ngram_range=config['ngram_range'],
                                    max_features=config['max_features'])
    
    def transform(self, texts):
        return self.model.transform(texts)

#=========#

class MyLDA():
    def __init__(self, config):
        self.topics_name = 'X_topics'
        self.name = 'lda_model'
        self.model = decomposition.LatentDirichletAllocation(n_components=config['n_components'],
                                                            learning_method=config['learning_method'],
                                                            max_iter=config['max_iter'])
    
    def transform(self, texts):
        return self.model.fit_transform(texts)


