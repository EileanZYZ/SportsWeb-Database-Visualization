"""
常用功能。
"""

# 库导入
import json
import pymysql

# 旭日图颜色集
tag_colors = {
    0: {"体育新闻": "#0000CD", "省局政务": "#DC143C"},  # 一级tag

    1: {"地方新闻": "#4169E1", "足球新闻": "#6495ED", "通知公告": "#B0C4DE", "重要新闻": "#778899", "直击奥运": "#708090",
        "全运会": "#1E90FF", "二青会": "#F0F8FF", "体育扶贫": "#4682B4", "战疫": "#87CEFA",
        "人物故事": "#87CEEB", "北京冬奥会": "#00BFFF", "全民健身": "#ADD8E6", "科学健身": "#B0E0E6", "健身指导": "#5F9EA0",
        "健身气功": "#F0FFFF", "科学健身一分钟": "#E1FFFF", "竞技体育": "#AFEEEE", "体育产业": "#00FFFF",
        "观点声音": "#D4F2E7", "新闻发布会": "#00CED1", "广东体育发展大数据": "#008B8B",  # “体育新闻”二级tag，共21个

        "政策法规": "#FF1493", "政务动态": "#FF69B4", "招标采购": "#DA70D6", "规范性文件": "#EE82EE", "政策解读": "#FF00FF",
        "人事信息": "#FF00FF"},  # ”省局政务“二级tag，共6个

    2: {"群众体育": "#9400D3", "竞技体育大数据": "#9932CC", "青少年体育": "#4B0082", "体育产业大数据": "#8A2BE2", "体育彩票": "#9370DB"}
    # “体育新闻-大数据”三级tag，共5个
}


# function:读取JSON
def read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.loads(file.read())


# function:登录数据库
def sign_in_mysql(config=None, used_database=str):
    # 设定默认参数
    if config is None:
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '1123581321',
            'charset': 'utf8'
        }
    # 链接数据库
    connect = pymysql.connect(**config)
    # 获取游标
    cursor = connect.cursor()

    # 选择数据库
    exe_sql = "USE " + str(used_database) + ";"
    cursor.execute(exe_sql)

    return connect, cursor


# 查询语句生成器，功能为生成sql查询语句
def generate_select(columns=list, table=str):
    sql = "SELECT "
    for c in columns[:-1]:
        sql += str(c) + ","
    sql += str(columns[-1])
    sql += " FROM " + str(table)
    return sql


# function:字典生成器
# 功能为将传入的多位列表转化为可以作为Echarts旭日图的字典列表并返回
def generate_dict(data, values, decker=0):
    dict_list = []
    global tag_colors

    # 所有标签集
    all_type = set()
    type_list = []
    for d in data:
        if len(d) != 0:
            type_list.append(d[0])
    all_type.update(type_list)
    type_list = list(all_type)

    # 制作字典
    for tl in type_list:  # 遍历该层
        # 要追加的字典
        app_dict = {
            "name": tl,  # 传入一级tag
            "itemStyle": {"color": tag_colors[decker][tl]},  # 传入对应颜色
        }

        # 找出底层tag符合的记录
        checked_data = []
        for c in data:
            if c[0] == tl:
                checked_data.append(c)
        for sub_d in checked_data:  # 在检查表中添加
            if tl == sub_d[-1]:  # 如果与最后一个元素相等，说明已经到末端
                app_dict["value"] = values[tl]  # 赋值
            else:
                # 制作下一级的data列表
                sub_data = []
                for d in data:
                    if d[0] == tl:
                        sub_data.append(d[1:])  # 将后续数据传入
                app_dict["children"] = generate_dict(data=sub_data,
                                                     values=values,
                                                     decker=decker + 1)
        dict_list.append(app_dict)  # 字典列表追加

    return dict_list  # 返回字典列表
