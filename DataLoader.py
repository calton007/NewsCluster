'''
@Descripttion: 数据拉取及分词相关操作
@version: 
@Author: 徐飞飞
@Date: 2019-12-18 01:54:39
@LastEditors  : 徐飞飞
@LastEditTime : 2019-12-31 16:05:58
'''
import pymysql
import re
import string
import nltk         # 使用sudo python3 -m nltk.downloader all 安装资源
import tqdm
import pickle
import config

class DataLoader(object):
    
    def __init__(self,
                host=config.db_host,
                user=config.db_user,
                port=config.db_port, 
                passwd=config.db_passwd, 
                db=config.db_db):
        self.connector = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=db, charset='utf8')
        self.cur = self.connector.cursor()
        self.get_stopwords()     # 生成停用词表


    def get_stopwords(self):
        '''
        @msg: 生成停用词表
        @param {type} 
        @return: 
        '''
        self.stop_words = nltk.corpus.stopwords.words('english')
        self.stop_words += ['(',')','!',',','.','?','-s','-ly','</s>','s']


    def read_raw_data(self, sql=config.dl_read_data_sql):
        '''
        @msg: 从数据库拉取新闻数据
        @param {str} sql：要执行的sql语句.该语句应 select news_id 和 content 两个字段
        @return: 新闻id列表、内容列表 
        '''
        # sql = "select news_id, content from newsapi where date_format(publishedAt, '%Y-%m-%d') between '" + from_date + "' and '" + to_date +"' ;"
        # print(sql)
        self.cur.execute(sql)
        id_list, content_list = zip(*self.cur.fetchall())
        return list(id_list), list(content_list)


    def clean_content(self, content):
        '''
        @msg: 文本清洗，待完善
        @param {str} content: 新闻文本 
        @return: 清洗后文本字符串
        ''' 
        content = re.sub('\n+', " ", content).lower()
        content = re.sub(' +', " ", content)
        # more process to do
        # ...
        return content
 
    def tokenizer(self, id_list, content_list, min_len=None, max_len=None):
        '''
        @msg: 分词器
        @param {list} id_list: 新闻id列表
        @param {list} content_list: 新闻内容列表
        @param {int} min_len: 文本的最小长度
        @param {int} max_len:文本的最大长度
        @return: 
        '''
        new_id_list = []            # 过滤后的文本id列表
        cut_content_list = []       # 切词后的文本列表
        # origin_content_list = []    # 过滤后的原始文本列表
        for i in tqdm.tqdm(range(len(id_list))):
            clean_content = self.clean_content(content_list[i])
            # 先分句再分词
            sens = nltk.sent_tokenize(clean_content)
            cut_content_ = []
            for sent in sens:
                cut_content_ += nltk.word_tokenize(sent)
            # 去除停用词
            cut_content = [ word for word in cut_content_ if not word in self.stop_words]
            # print("id: ", id_list[i], "cut_content:", cut_content)
            if min_len:             # 去掉短于min_len的文本
                if len(cut_content) < min_len:
                    continue
            if max_len:             # 去掉长于max_len的文本
                if len(cut_content) > max_len:
                    continue
            
            new_id_list.append(id_list[i])
            cut_content_list.append(' '.join(cut_content))
            # origin_content_list.append(content_list[i])

        # 保存处理后的数据
        with open('./data/tokenizer_result.pkl', 'wb') as f:
            pickle.dump(new_id_list, f)
            pickle.dump(cut_content_list, f)
            # pickle.dump(origin_content_list, f)

        return new_id_list, cut_content_list


if __name__ == "__main__":
    dl = DataLoader()
    id_list, content_list = dl.read_raw_data()
    id_list, cut_content_list = dl.tokenizer(id_list, content_list)
    print(len(id_list), id_list[1], cut_content_list[1])