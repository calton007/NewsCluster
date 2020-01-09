'''
@Descripttion: 配置文件
@version: 
@Author: 徐飞飞
@Date: 2019-12-18 07:33:01
@LastEditors  : 徐飞飞
@LastEditTime : 2019-12-31 11:05:46
'''

# 数据库
db_host='192.168.171.49'
db_user='root'
db_port=33306
db_passwd='123456'
db_db='news4primer'

# DataLoader相关参数
# 数据读取sql
dl_read_data_sql = "select news_id, content from newsapi where date_format(publishedAt, '%Y-%m-%d') between '2019-12-17' and '2019-12-18';"


doc2vec_min_count = 2
doc2vec_window = 3
doc2vec_size = 100
doc2vec_sample = 1e-3
doc2vec_negative = 5
doc2vec_workers = 4
doc2vec_epochs = 20

dbscan_eps = 4
dbscan_min_samples = 1
