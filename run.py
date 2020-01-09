from DataLoader import DataLoader
from Text2Vector import Text2Vector
from Cluster import Cluster
from EventExtractor import EventExtractor

# 获取数据并分词
dl = DataLoader()
id_list, content_list = dl.read_raw_data()
id_list, content_list = dl.tokenizer(id_list, content_list)
print("++++++++++++++++ data loaded ++++++++++++++++")

# 向量化
t2v = Text2Vector(id_list, content_list)
id_list, vectors = t2v.doc2vec()
print("++++++++++++++++ Vectorizing Finished ++++++++++++++++")

# 聚类
cluster = Cluster(id_list, vectors)
cluster.dbscan()        # 聚类结果写到数据库中了，不获取返回值
print("++++++++++++++++ Cluster Finished ++++++++++++++++")

ee = EventExtractor(method="toy") 
print("++++++++++++++++ Event Extract Finished ++++++++++++++++")