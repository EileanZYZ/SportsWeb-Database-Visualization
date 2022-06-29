# 导入库

import web_crawler
import data_analyse
import common_function as cf
import data_visualization as dv

# 主程序
if __name__ == "__main__":
    # 设置标头
    header = {  # 爬取网站的标头
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39"
    }

    # 登录mysql
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # 文件路径
    json = "webs.json"

    # 读取存放网址的json文件
    url_list = cf.read_json(json)

    # 爬取网页内容并保存
    web_crawler.get_data(url_list, headers=header)

    # 由于“广东...大数据”一栏的自tag与其他tag有重合，需要进行修改
    # sql1 = "UPDATE news SET " \
    #        "tag=\"体育新闻-广东体育发展大数据-竞技体育大数据\" " \
    #        "WHERE " \
    #        "tag=\"体育新闻-广东体育发展大数据-竞技体育\";"
    # sql2 = "UPDATE news SET " \
    #        "tag=\"体育新闻-广东体育发展大数据-体育产业大数据\" " \
    #        "WHERE " \
    #        "tag=\"体育新闻-广东体育发展大数据-体育产业\";"
    # cursor.execute(sql1)
    # cursor.execute(sql2)

    # 统计词频与生成词云
    data_analyse.word_count_and_cloud()

    # 情感分析
    data_analyse.emotion_analyse()

    # 可视化
    dv.data_visualization()
