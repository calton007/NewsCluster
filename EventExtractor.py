'''
@Descripttion: 事件抽取：根据聚类结果，提取同一簇中文章对应事件信息,即填充event表中title, keyWord, time, abstract, content字段
@version: 
@Author: 徐飞飞
@Date: 2019-12-31 09:55:26
@LastEditors  : 徐飞飞
@LastEditTime : 2019-12-31 16:59:01
'''

import pymysql
import config
from Extractor.ToyExtractor import ToyExtractor
from Extractor.Compress import Compress

class EventExtractor():

    def __init__(self, method="toy"):
        self.get_connector()
        self.extract_event(method)


    def get_connector(self, 
                      host=config.db_host,
                      user=config.db_user,
                      port=config.db_port, 
                      passwd=config.db_passwd, 
                      db=config.db_db):
        self.connector = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=db, charset='utf8')


    def extract_event(self, method="toy", sql = config.ee_sql):
        '''
        @msg: 提取事件详细信息。从数据库中读取事件的label和newsid字段，然后调用extractor提取事件的具体信息
        @param {str} sql: 从event表中 select label 和 newsid 字段
        @return: 
        '''  
        cur = self.connector.cursor()
        count = cur.execute(sql)
        if method == "toy":
            extractor = ToyExtractor()
        elif method =="compress":
	        extractor = Compress()           
        else:
            # to do 
            pass
        for _ in range(count):
            label, newsid= cur.fetchone()
            title, keyWord, abstract, time, content = extractor.extract(label, newsid)
            self.update_event(label, title=title, keyWord=keyWord, time=time, abstract=abstract, content=content)
            # self.toy_extractor(label, newsid.split(" "))
  

    def update_event(self, label, title=None, keyWord=None, time=None, abstract=None, content=None):
        cur = self.connector.cursor()
        sql = "update cluster set "
        if not title:
            title = "None"          # title字段不能为空
        title = title.replace("'", "\\\'")      # 
        sql += "title='" + title + "', "
        if time:
            sql += "time='" + str(time) + "', "
        if keyWord:
            keyWord = keyWord.replace("'", "\\\'")
            sql += "keyWord='" + keyWord + "', "
        if abstract:
            abstract = abstract.replace("'", "\\\'")
            sql += "abstract='" + abstract + "', "
        if content:
            content = content.replace("'", "\\\'")
            sql += "content='" + content + "', "

        sql = sql[:-2]
        sql += " where label='" + label + "';" 
        # print("update sql: ", sql)

        cur.execute(sql)
        self.connector.commit()
        cur.close()

if __name__ == "__main__":
    ee = EventExtractor()


