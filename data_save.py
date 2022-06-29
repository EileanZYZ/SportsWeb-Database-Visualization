"""
数据存储程序。主要实现：
1、将爬虫获取的数据进行规范化；
2、将数据存入特定csv文件；
3、将爬取到的数据存入数据库以便进一步分析
"""
# 库导入
import os.path
from opencc import OpenCC
import common_function as cf

# 设置参数
database_name = "Guangdong_sport_gov"
csv_filepath = "D:\\My\\Code\\Code by Python\\PyCharm\\SportsWeb&Database"


# function:规范化数据，实现功能：
#   1、标题字体繁→简转换；
#   2、标题删除空格与换行，并将单引号替换为双引号（英文），英文逗号变为中文逗号；
#   3、查重。删除（万一）多爬一遍的数据；
def formative_data(data, title_index=int):
    # data = [[url,title, date, tag],...]
    print("开始规范化数据......", end="")

    # 繁简转换
    for d in data:
        d[title_index] = OpenCC("t2s").convert(d[1])

    # 字符替换
    for d in data:
        d[title_index] = d[title_index].replace(" ", "")
        d[title_index] = d[title_index].replace("\n", "")
        d[title_index] = d[title_index].replace("\'", "\"")
        d[title_index] = d[title_index].replace(",", "，")

    # 查重
    clean_data = []
    for d in data:
        if d not in clean_data:
            clean_data.append(d)

    print("规范化完成。")
    return clean_data


# function:初始化csv文件
def initiate_csv(filename,  # 需要初始化的csv文件名
                 header_text):  # 需要初始化的文件属性栏
    # 获取参数
    global csv_filepath

    # 初始化csv文件：创建文件并添加标头
    with open(csv_filepath + "\\" + filename + ".csv", "a", encoding="utf-8-sig") as file:
        file.write(header_text)
        file.write("\n")


# function:爬取数据写入csv
def write_into_csv(data,  # 需要存入的数据。data = [[data1, data2, ...],...]
                   initiate_header,  # 以防文件不存在时准备的初始化标头。initiate_header = "text,text,text"
                   filename="data"):  # 需要保存的文件名
    # 获取参数
    global csv_filepath

    print("保存至csv文件......", end="")

    # 判断csv文件是否被初始化
    if os.path.exists(filename + ".csv"):
        with open(csv_filepath + "\\" + filename + ".csv", "a", encoding="utf-8-sig") as file:
            # 写入
            for d in data:
                for i in range(len(d) - 1):
                    file.write(str(d[i]))
                    file.write(",")
                file.write(str(d[-1]))
                file.write("\n")
            print("成功保存。")
    else:  # 不存在指定文件时，初始化该文件并写入
        initiate_csv(filename, initiate_header)
        write_into_csv(data, csv_filepath, filename)


# function:初始化数据库
def initiate_database(table_name="", table_config=""):
    # 登录mysql
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # sql语句
    sql_1 = "CREATE DATABASE IF NOT EXISTS " + database_name + ";"  # 创建数据库，(如果数据库存在就不创建，防止异常)
    sql_2 = "USE " + database_name + ";"  # 选择数据库
    sql_3 = "CREATE TABLE IF NOT EXISTS " + table_name + table_config + ";"  # 创建表格

    # 执行语句
    cursor.execute(sql_1)
    cursor.execute(sql_2)
    cursor.execute(sql_3)

    # 关闭游标与连接
    cursor.close()
    connect.close()


# function:数据存入mysql库
def save_into_mysql(data, table_name="", columns=""):
    # columns = "text,text,text"
    # 登录mysql
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # 将列表中的记录子列表转化为元祖
    print("保存至数据库......", end="")
    data_list = []
    for i in range(len(data)):
        data_list.append(tuple(data[i]))

    # 计算一行有多少value值需要用字符串占位
    s_count = (len(data_list[0]) - 1) * "%s," + "%s"

    # sql语句
    sql_1 = "USE " + database_name + ";"  # 选择数据库
    sql_2 = "INSERT INTO " + table_name + "(" + columns + ") VALUES(" + s_count + ")"

    # 插入数据
    try:
        cursor.execute(sql_1)
        cursor.executemany(sql_2, data)
        print("成功保存。")
    except Exception as e:
        # 进行回滚操作
        connect.rollback()
        print("\n发生错误：", end="")
        print(e)  # 打印错误
    finally:
        connect.commit()  # 提交数据
        cursor.close()  # 关闭游标
        connect.close()  # 关闭连接
