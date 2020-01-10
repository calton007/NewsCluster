'''
@Descripttion: 文本对齐：将同一个新闻事件的多篇新闻文本句子对齐
@version: 
@Author: 李观波
@Date: 2020-01-10 10:01:01
@LastEditors  : 李观波
@LastEditTime : 2020-01-10 15:15:15
'''

import pymysql
import config
import spacy
import numpy as np
from tqdm import tqdm
import random


class Compress():
	def __init__(self):
		self.retry = False
		self.connector = self.get_connector()
		self.nlp = spacy.load('en_trf_bertbaseuncased_lg')
	
	def disconnect(self):
		try:
			if not self.connector:
				self.connector.close()
		except:
			pass
		exit(1)
		
	def get_connector(self, host=config.db_host,
                      user=config.db_user,
                      port=config.db_port, 
                      passwd=config.db_passwd, 
                      db=config.db_db):
		'''
		@msg:连接数据库。如果数据库连接失败，重试一次，再次失败退出程序
		@return: connector
		'''
		# 判断是否重连
		if not self.retry:
			connector = pymysql.connect(
				host=host, 
				user=user, 
				port=port, 
				passwd=passwd, 
				db=db, 
				charset='utf8')
			# 判断数据库是否连接成功
			if not connector.server_status:
				print("数据库连接成功！")
				return connector
			# 如果数据库连接失败，重试一次
			else:
				print("数据库连接错误，正在重试！")
				self.retry = True
				self.get_connector()
		else:
			print("数据库连接错误，程序即将关闭！")
			self.disconnect()
	
	def get_all_clusters(self):
		'''
		@msg:查询聚类结果，返回聚类结果各 Cluster 的 Label 列表
		@return: cluster_labels
		'''
		sql = "select label from cluster order by time desc;"
		try:
			assert not self.connector.server_status		# 判断数据库连接状态
			cursor = self.connector.cursor()
			cursor.execute(sql)
			query_results = cursor.fetchall()
			cluster_labels = []
			for item in query_results:
				cluster_labels.append(item[0])
		except:
			print("服务器状态异常")
			self.disconnect()
		finally:
			cursor.close()
		return cluster_labels
	
	def get_cluster_by_id(self, id):
		'''
		@msg:根据 Cluster 的 Label 查询包含的 newsid 列表
		@param {str} id: Cluster 的 Label
		@return: newsid
		'''
		sql = "select newsid from cluster where label = '%s'; " % (id, )
		try:
			assert not self.connector.server_status
			cursor = self.connector.cursor()
			cursor.execute(sql)
			query_results = cursor.fetchall()
			newsid = []
			for item in query_results[0][0].split(' '):
				newsid.append(item)
		except:
			print("服务器状态异常")
			self.disconnect()
		finally:
			cursor.close()
		return newsid
	
	def get_news_by_id(self, id):
		'''
		@msg:根据 news_id 查询新闻内容并返回
		@param {str} id: 新闻的 news_id
		@return: news
		'''
		sql = "select content from newsapi where news_id = %s ;" % (id, )
		try:
			assert not self.connector.server_status
			cursor = self.connector.cursor()
			cursor.execute(sql)
			query_results = cursor.fetchall()
			news = query_results[0][0]
		except:
			print("服务器状态异常")
			self.disconnect()
		finally:			
			cursor.close()
		return news

	def get_news(self, ids):
		'''
		@msg:根据 ids 查询所有新闻内容，返回所有新闻内容 news 的列表
		@param {list} ids: 所有新闻的 news_id
		@return: news
		'''
		news = []
		for id in ids:
			news.append(self.get_news_by_id(id))
		return news
		
	def get_sentences(self, txt):
		'''
		@msg:处理 txt 的内容，划分句子，返回 sentences 列表
		@param {str} txt: 文本
		@return: sentences
		'''
		temp = txt.replace('\r', '')
		temp = temp.replace('\n', '')
		doc = self.nlp(temp)
		sentences = []
		for sen in doc.sents:
			sentences.append(str(sen))
		return sentences

	def merge_sentence(self, txt_a, txt_b):
		'''
		@msg:压缩合并两个新闻文本内容
		@param {str} txt_a, txt_b: 新闻文本 a, 新闻文本 b
		@return: sentences
		'''
		# 句子划分
		doc_a = self.get_sentences(txt_a)
		doc_b = self.get_sentences(txt_b)	
		
		doc = doc_a + doc_b # 合并两篇新闻文本
		
		index = [i for i in range(len(doc))] # 索引记录，用于判断是否保留句子
		
		nlp_list = []		
		
		# 句子编码
		for item in doc:
			nlp_list.append(self.nlp(item))
		
		# 句子压缩
		for i in tqdm(range(len(doc))):
			sentence_1 = nlp_list[i]
			# 句子对比
			for j in range(max(len(doc_a), i + 1), len(doc)):
				sentence_2 = nlp_list[j]
				local_sim = 0	# 局部相似度
				
				# 计算局部相似度
				for wi in sentence_1:
					for wj in sentence_2:
						a = np.linalg.norm(wi.vector)
						b = np.linalg.norm(wj.vector)
						sim = wi.vector.dot(wj.vector)/ a / b
						if sim > 0.75:
							local_sim += 1			
				sign = 1 if len(sentence_1) >= len(sentence_2) else -1 # 计算方向				
				local_sim = local_sim / len(sentence_1) / len(sentence_2) * 5
				
				global_sim = sentence_1.similarity(sentence_2)	# 全局相似度
				
				total_sim = sign * (local_sim * 0.6 + global_sim * 0.4)
				
				# 删除冗余句子
				if total_sim > 0.4 or total_sim < - 0.45:
					# print(i, j, total_sim)
					try:
						if total_sim > 0:
							index.remove(j)
						elif total_sim < 0:
							index.remove(i)
					except ValueError:
						pass
		
		return [doc[i] for i in index]

	def list_to_txt(self, i):
		'''
		@msg:新闻句子列表 i 转字符串 txt
		@param {list} i:新闻文本列表
		@return: txt
		'''
		txt = ""
		for item in i:
			txt += (item + ' ')
		return txt
	
	def merge_all(self, news):
		'''
		@msg:压缩同一个 Cluster 下的所有新闻 news
		@param {list} news:新闻文本列表
		@return: result
		'''
		length = len(news)
		if length > 0:
			result = news[0]
			for item in news:
				result = self.list_to_txt(self.merge_sentence(result, item))
			return result
		else:
			return ""
	
	def update_data(self, label, result):
		'''
		@msg:按 label 查询记录，将压缩结果 result 更新到数据库中 
		@param {str} label: Cluster 的 label
		@param {str} result: 文本压缩结果
		@return: result
		'''	
		sql = "UPDATE cluster SET content = '%s' WHERE (label = '%s');" % (result, label)
		try:
			cursor = self.connector.cursor()
			cursor.execute(sql)
			self.connector.commit()
			print("更新成功！")
		except:
			print("更新失败！")
			self.connector.rollback()
		finally:
			cursor.close()
