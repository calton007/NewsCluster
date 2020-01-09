'''
@Descripttion: 文本聚类相关算法。根据聚类结果填充event表中label, newsid字段
@version: 
@Author: 徐飞飞
@Date: 2019-12-18 13:21:08
@LastEditors  : 徐飞飞
@LastEditTime : 2019-12-31 16:58:49
'''

import numpy as np
import pickle
from sklearn.cluster import DBSCAN, KMeans
import config
from collections import defaultdict
import pymysql


class Cluster():

    def __init__(self, id_list=None, vectors=None):
        if id_list == None or vectors == None:
            id_list, vectors = self.load_data()
        self.id_list = id_list
        self.vectors = vectors
        self.connector = None

    def get_connector(self,
                    host=config.db_host,
                    user=config.db_user,
                    port=config.db_port, 
                    passwd=config.db_passwd, 
                    db=config.db_db):
        if not self.connector:
            self.connector = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=db, charset='utf8')

    def load_data(self, path=config.cluster_vec_path):
        with open(path, 'rb') as f:
            id_list = pickle.load(f)   # 文章id列表
            vectors = pickle.load(f)   # 文章对应向量
        return id_list, vectors
    
    def dbscan(self,
              eps=config.cluster_dbscan_eps, 
              min_samples=config.cluster_dbscan_min_samples):
        # 聚类
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(self.vectors)
        self.labels = clustering.labels_
        
        # 本地存储
        with open('./data/dbscan_id2label', 'wb') as f:
                pickle.dump(self.id_list, f)
                pickle.dump(self.labels, f)
               
        # 获得{"447" : [332980 333058 921944 922046]}形式的聚类结果，即簇447中包含news_id为
        # 332980 333058 921944 922046的四篇文章
        lable2id = defaultdict(list)
        for i in range(len(self.id_list)):
            lable2id[self.labels[i]].append(self.id_list[i])
        # print(len(lable2id[6]))
        # 写入数据库
        self.get_connector()
        cur = self.connector.cursor()
        prefix = "insert into cluster(label, newsid) values ("
        for label, id_list_ in lable2id.items():
            id_list = [str(id) for id in id_list_]
            # sql eg: insert into cluster(label, newsid) values ('dbscan_447', '332980 333058 921944 922046')
            sql = prefix + "\'dbscan_" + str(label) + "\', \'" + " ".join(id_list) + "\');"
            print(sql)
            cur.execute(sql)
        self.connector.commit()
        return self.id_list, self.labels

    def KMeans(self):
        pass
        
cluster = Cluster()
cluster.dbscan()