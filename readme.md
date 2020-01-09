# 简介

新闻事件挖掘。通过聚合公开的新闻数据，聚合描述相同事件的新闻并生成相关事件信息。

# 数据库

目前有两个表结构：原始新闻表（news) 存储原始新闻信息，事件信息表（event）存储聚类分析后的事件信息。

### 原始新闻表(news)

表结构：

| Field | Type | Null | Key | Default | Extra |
| --- |  --- |  --- |  --- |  --- |  --- |
| news_id      | int(10) unsigned | NO   | PRI | <null>  | auto_increment |
| source       | varchar(1000)    | YES  |     | <null>  |                |
| author       | varchar(1000)    | YES  |     | <null>  |                |
| title        | varchar(1000)    | YES  |     | <null>  |                |
| queryKeyWord | varchar(100)     | YES  |     | <null>  |                |
| description  | varchar(2000)    | YES  |     | <null>  |                |
| url          | varchar(1000)    | YES  |     | <null>  |                |
| urlToImage   | varchar(1000)    | YES  |     | <null>  |                |
| publishedAt  | datetime         | YES  |     | <null>  |                |
| content      | text             | YES  |     | <null>  |                |

字段说明：

| 字段         | 说明                                                         | 示例                 |
| ------------ | ------------------------------------------------------------ | -------------------- |
| news_id      |                                                              | 106511               |
| source       | The identifier display name for the source this <br />article came from | "The New York Times" |
| author       | The author of the article                                    | "Michael Levenson"   |
| title        | The headline or title of the article                         |                      |
| queryKeyWord | Keywords or phrases to search for in the article <br />title and body | "Donald Trump"       |
| description  | A description or snippet from the article                    |                      |
| url          | The direct URL to the article                                |                      |
| urlToImage   | The URL to a relevant image for the article                  |                      |
| publishedAt  | The date and time  the article was published                 | 2019-12-17 11:26:36  |
| content      | The unformatted content of the article.<br />This is truncated to 260 chars for Developer plan users |                      |

### 事件信息表(event)

表结构：
| Field    | Type          | Null | Key | Default | Extra |
| ---    | ---          | --- | --- | ---| ---|
| label    | varchar(20)   | NO   | PRI | <null>  |       |
| newsid   | varchar(2000) | NO   |     | <null>  |       |
| title    | varchar(1000) | YES |     | <null>  |       |
| keyWord  | varchar(100)  | YES  |     | <null>  |       |
| time     | datetime      | YES  |     | <null>  |       |
| abstract | varchar(2000) | YES  |     | <null>  |       |
| content  | text          | YES  |     | <null>  |       |

字段说明：

| 字段     | 说明                             | 示例                    |
| -------- | -------------------------------- | ----------------------- |
| label    | 簇标记/事件id                    |                         |
| newsid   | 该事件包含的news_id，用空格分隔  | "106511 106522"         |
| title    | 事件标题                         |                         |
| keyWord  | 事件关键字，多个关键字用 \| 分隔 | “ keyword1 \| keyword2" |
| time     | 事件发生时间                     | 2019-12-17 11:26:36     |
| abstract | 事件摘要                         |                         |
| content  | 事件详细描述                     |                         |

