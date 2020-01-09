'''
@Descripttion: 文本转化为向量相关的操作
@version: 
@Author: 徐飞飞
@Date: 2019-12-18 07:09:31
@LastEditors  : 徐飞飞
@LastEditTime : 2019-12-26 14:26:27
'''

import pickle
import config
from gensim.models.doc2vec import TaggedDocument
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import Doc2Vec
import numpy as np
from collections import defaultdict
from gensim import corpora
from gensim import models


class Text2Vector(object):
    
    def __init__(self, id_list=None, content_list=None):
        if id_list == None or content_list == None:
            id_list, content_list =  self.load_tokenizer()
        self.id_list = id_list
        self.corpus = [[word for word in doc.lower().split()] for doc in content_list]
        self.dictionary = corpora.Dictionary(self.corpus)
    
    
    def load_tokenizer(self, path=config.t2v_tokenizer_path):
        '''
        @msg: 加载分词后的数据
        @param {str} path：数据存放路径 
        @return: 
        '''
        with open(path, 'rb') as f:
            id_list = pickle.load(f)
            content_list = pickle.load(f)
            return id_list, content_list


    def doc2vec(self,
                epochs=config.t2v_doc2vec_epochs,
                min_count=config.t2v_doc2vec_min_count,
                size=config.t2v_doc2vec_size):
            '''
            @msg: 采用doc2vec将文本转换为向量
            @param {int} epochs: epochs
            @param {int} min_count: 最低词频. 
            @param {int} size: doc2vec向量的维度大小.   
            @return:
            '''
            tagged_corpus = []
            for i in range(len(self.id_list)):
                text = self.corpus[i]
                # print(self.id_list[i])
                tagged_corpus.append(TaggedDocument(words=text, tags=[i]))
            # print(tagged_corpus[:1])  # 111 第二维 x 对应tags=x-1
            # print(tagged_corpus[0].words)
            model = Doc2Vec(vector_size=size, min_count=min_count, epochs=epochs)
            model.build_vocab(tagged_corpus)
            model.train(tagged_corpus, total_examples=model.corpus_count, epochs=model.epochs)
            model.save('./model/doc2vec_model')
            vectors = []
            for doc_id in range(len(tagged_corpus)):
                vec = model.infer_vector(tagged_corpus[doc_id].words)
                vectors.append(vec)
            self.vectors = vectors

            # 本地保存
            with open('./data/doc2vec_vectors.pkl', 'wb') as f:
                pickle.dump(self.id_list, f)
                pickle.dump(self.vectors, f)
            
            return self.id_list, self.vectors
            
    def tfidf_vector(self):
        '''
        @msg: 使用tfidf将文本转化为向量
        @param {type} 
        @return: 
        '''        
        pass


t2v = Text2Vector()
t2v.doc2vec()