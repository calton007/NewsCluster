import config
import pymysql

class ToyExtractor():

    # def __init__(self):
    #     self.get_connector()

    # def get_connector(self, 
    #                 host=config.db_host,
    #                 user=config.db_user,
    #                 port=config.db_port, 
    #                 passwd=config.db_passwd, 
    #                 db=config.db_db):
    #     self.connector = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=db, charset='utf8')


    def extract(self, connector, label, id_list):
        '''
        @msg: 提取id_list中新闻对应事件信息。直接取第一条新闻对应的信息
        @param {str} label: 簇标记/事件id
        @param (list) id_list: 事件相关新闻的id列表 
        @return: 
        '''  
        id = id_list[0]
        cur = connector.cursor()
        sql = "select title, queryKeyWord, description, publishedAt, content from newsapi where news_id='" + id + "';"
        # print("query sql: ",query_sql)
        cur.execute(sql)
        title, keyWord, abstract, time, content = cur.fetchone()
        cur.close()
        return title, keyWord, abstract, time, content