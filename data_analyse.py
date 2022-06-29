"""
数据分析程序。主要实现;
1、对爬取到的数据进行词频统计并生成词云图；
2、对标题进行情感分析，得出情感状态（正面，中性，负面）并将结果保存至csv文件；
3、对原始数据表进行汇总，并输出可以作为旭日图参数的字典列表
"""

# 库导入
import jieba
import pandas as pd
import operator
import data_save
import common_function as cf
import wordcloud
import numpy as np
from snownlp import SnowNLP


# function:词频统计
def word_count_and_cloud():
    # 登录mysql
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # sql语句:读取news中的title和date
    sql = cf.generate_select(columns=["title", "date"], table="news")

    # pandas读取信息
    cursor.execute(sql)
    data = pd.read_sql(sql=sql, con=connect)
    days = data["date"].unique().shape[0]  # 返回date去重行数（即总天数）

    # 获取标题字符串
    title_str = ""
    for d in data["title"]:
        title_str += str(d)
    words = jieba.lcut(title_str)

    # 获取屏蔽词
    ex = open("excludeWords.txt", "r", encoding="utf-8")
    exclude_words = ex.read().split("\n")
    ex.close()

    # 开始统计
    print("开始统计词频......", end="")
    word_counts = {}
    for w in words:
        if len(w) == 1:
            continue  # 直接忽略诸如“我”、“是”这一类单个词汇
        else:
            word_counts[w] = word_counts.get(w, 0) + 1  # 计数
    # 删除屏蔽词
    for e in exclude_words:
        del word_counts[e]
    # 排序
    sorted_counts = []
    for c in sorted(word_counts.items(), key=operator.itemgetter(1), reverse=True):
        sorted_counts.append(list(c))
    # 追加频率
    for s in sorted_counts:
        s.append(s[1] / days)

    print("统计完成。")

    # 另存为csv文件
    data_save.write_into_csv(data=sorted_counts,
                             initiate_header="word,count,frequency",
                             filename="newsWordCount")
    # 初始化并保存至数据库
    data_save.initiate_database(table_name="word_count",
                                table_config="("
                                             "id INT NOT NULL AUTO_INCREMENT,"
                                             "word VARCHAR(30) NOT NULL,"
                                             "count INT NOT NULL,"
                                             "frequency FLOAT NOT NULL,"
                                             "PRIMARY KEY(id)"
                                             ")ENGINE=InnoDB DEFAULT CHARSET=utf8")
    data_save.save_into_mysql(data=sorted_counts,
                              table_name="word_count",
                              columns="word,count,frequency")

    # 获取词云屏蔽词
    st = open("stopWords.txt", "r")
    stop_words = set(st.read().split("\n"))
    st.close()

    # 生成本地词云图
    cloud_txt = " ".join(words)
    word_cloud = wordcloud.WordCloud(
        width=3000, height=2100,
        background_color="black",
        stopwords=stop_words,
        font_path="shouJin.ttf",
    )
    print("词云图生成中......", end="")
    word_cloud.generate(cloud_txt)
    # 保存
    word_cloud.to_file("wordCloud.png")
    print("词云图已生成。")


# function:情感分析
def emotion_analyse():
    # 登录mysql
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # sql语句:读取news中的id和title
    sql = cf.generate_select(columns=["id", "title"], table="news")

    # pandas读取信息
    data = pd.read_sql(sql=sql, con=connect)

    # 情感分析
    print("开始进行情感分析......", end="")
    data["e_value"] = data["title"].apply(lambda x: SnowNLP(x).sentiments)
    # 将情感值离散化
    data["e_state"] = pd.cut(data["e_value"], bins=3, labels=["negative", "middle", "positive"])
    print("分析完成。")

    # 保存至csv
    data_list = np.array(data).tolist()  # 将dataframe转化成列表
    data_list = data_save.formative_data(data_list, title_index=1)
    data_save.write_into_csv(data=data_list,
                             initiate_header="id,title,emotion value,emotion state",
                             filename="emotionalAnalyse")
    # 保存至数据库
    data_save.initiate_database(table_name="emotion_analyse",
                                table_config="("
                                             "id INT NOT NULL AUTO_INCREMENT,"
                                             "title VARCHAR(150) NOT NULL,"
                                             "emotion_value FLOAT NOT NULL,"
                                             "emotion_state VARCHAR(15) NOT NULL,"
                                             "PRIMARY KEY(id)"
                                             ")ENGINE=InnoDB DEFAULT CHARSET=utf8")
    data_save.save_into_mysql(data_list,
                              table_name="emotion_analyse",
                              columns="id,title,emotion_value,emotion_state")


# function:原始数据汇总
def data_summarize():
    # 登录数据库
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    print("开始进行数据汇总......", end="")
    # 获取文章标签
    tag = pd.read_sql(sql=cf.generate_select(columns=["tag"], table="news"),
                      con=connect)

    # 将文章标签分级和词频
    split_tags = []
    for t in tag["tag"].value_counts().index.tolist():
        split_tags.append(str(t).split("-"))
    tag_counts = tag["tag"].value_counts().tolist()
    # 将末端tag和count制作成键值列表
    keys = []
    for s in split_tags:
        keys.append(s[-1])
    values_dict = dict(zip(keys, tag_counts))

    # 获取JSON
    json_list = cf.generate_dict(data=split_tags,
                                 values=values_dict)

    print("汇总完成。")
    return json_list
