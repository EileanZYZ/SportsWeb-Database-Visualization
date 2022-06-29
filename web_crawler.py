"""
爬虫程序。主要实现：
1、对于有分页的网页进行自动浏览和爬取；
2、将爬取到的网页按照元素进行分拣，获得目标信息；
3、将爬取到的信息以“页”为单位，以列表形式进行进一步处理和存储
"""

# 库导入
import data_save
import requests
from bs4 import BeautifulSoup
import time


# function:自动翻页
def auto_browsing(url, tag, headers):
    # 获取参数
    web = requests.get(url, headers=headers)  # 爬取网页
    data = []
    if web.status_code == 200:
        print("访问成功：{}".format(url))
        web.encoding = 'utf-8'
        html = web.text

        # 分拣
        soup = BeautifulSoup(html, "lxml")
        news_list = soup.find(class_="doc_list list-4294324").select("li")  # 新闻列表

        # 获取标题和发布时间
        for article in news_list:
            title = article.find(name="span", class_="").get_text()
            date = article.find(class_="right date").get_text()
            data.append([title, date, tag])

        # 将data推入函数进行数据处理
        data = data_save.formative_data(data, title_index=0)

        # 保存数据
        data_save.write_into_csv(data=data,
                                 initiate_header="url,title,date,tag",
                                 filename="news")
        data_save.save_into_mysql(data,
                                  table_name="news",
                                  columns="url,title,date,tag")

        time.sleep(1)  # 等待1秒

        # 判断是否有“下一页”，若有则自动跳转
        try:
            next_page_link = soup.find(name="a", class_="next").get("href")
            auto_browsing(next_page_link, tag, headers=headers)
        except AttributeError:
            print("——————爬取完成——————")

    else:  # 访问失败时，报错并返回状态码
        print("访问失败。代码：{}".format(web.status_code))


# function:爬取网页
def get_data(urls, headers):
    # 初始化数据库
    data_save.initiate_database(table_name="news",
                                table_config="("
                                             "id INT NOT NULL AUTO_INCREMENT,"
                                             "url VARCHAR(150) NOT NULL,"
                                             "title VARCHAR(150) NOT NULL,"
                                             "date DATE NOT NULL,"
                                             "tag VARCHAR(30) NOT NULL,"
                                             "PRIMARY KEY(id)"
                                             ")ENGINE=InnoDB DEFAULT CHARSET=utf8")

    print("\n——————开始爬取——————")
    for url in urls:
        auto_browsing(url=url["url"], tag=url["tag"], headers=headers)
        time.sleep(1)  # 等待1秒，防止网站服务器负荷过大
    print("——————所有网页爬取完成——————")
