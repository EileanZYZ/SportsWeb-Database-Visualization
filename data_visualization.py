"""
数据可视化程序。主要实现数据的可视化。
"""

# 库导入
import pandas as pd
import common_function as cf
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Bar, Line, WordCloud, Pie, Page, Sunburst
import data_analyse as da


# function:词频统计和情感分析可视化
def data_visualization():
    # 获取参数
    table1 = "word_count"
    table2 = "emotion_analyse"

    # 登录数据库
    connect, cursor = cf.sign_in_mysql(used_database="guangdong_sport_gov")

    # 读取数据
    word_count = pd.read_sql(sql=cf.generate_select(table=table1,
                                                    columns=("word", "count", "frequency")),
                             con=connect)
    emotion = pd.read_sql(sql=cf.generate_select(table=table2,
                                                 columns=("title", "emotion_value", "emotion_state")),
                          con=connect)
    summary = da.data_summarize()

    print("开始可视化......", end="")
    # 绘制所有tag的汇总旭日图
    sun = (
        Sunburst(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("",
             data_pair=summary,
             highlight_policy="descendant",
             radius=["20%", "100%"],
             sort_="asc",)
        .set_global_opts(title_opts=opts.TitleOpts(title="数据汇总",
                                                   title_textstyle_opts=opts.TextStyleOpts(
                                                       color="#000080",
                                                       font_size=30),
                                                   pos_left="center"),
                         tooltip_opts=opts.TooltipOpts(trigger="item"),
                         )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
    )

    # 绘制词频统计条形图和词频折线图
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(word_count["word"].tolist())  # 以词为X轴
        .add_yaxis("计数", word_count["count"].tolist())  # 以计数为Y轴
        .set_global_opts(title_opts=opts.TitleOpts(title="词频统计",
                                                   title_textstyle_opts=opts.TextStyleOpts(
                                                       color="#000080",
                                                       font_size=30)),  # 标题
                         tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),  # 指示器
                         datazoom_opts=[opts.DataZoomOpts(range_start=0,
                                                          range_end=0.5,
                                                          is_zoom_lock=True)],  # 区域缩放
                         visualmap_opts=[opts.VisualMapOpts()]
                         )
        .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value}"), interval=0.05
            )
        )
    )
    line = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(word_count["word"].tolist())
        .add_yaxis("词频", word_count["frequency"].tolist(), yaxis_index=1)
        .set_global_opts(title_opts=opts.TitleOpts(title="词频统计",
                                                   title_textstyle_opts=opts.TextStyleOpts(
                                                       color="#000080",
                                                       font_size=30)),  # 标题
                         tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),  # 指示器
                         datazoom_opts=[opts.DataZoomOpts(range_start=0,
                                                          range_end=0.5,
                                                          is_zoom_lock=True)],  # 区域缩放
                         visualmap_opts=[opts.VisualMapOpts()],
                         toolbox_opts=opts.ToolboxOpts(
                             is_show=True,
                             orient="vertical",
                             feature=opts.ToolBoxFeatureOpts(
                                 magic_type=opts.ToolBoxFeatureMagicTypeOpts()
                             )
                         )
                         )
    )

    # 绘制情感等级饼图
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add(series_name="情感等级",
             data_pair=[list(z) for z in zip(
                ["好评如潮", "多数差评", "褒贬不一"], emotion["emotion_state"].value_counts().values.tolist())],
             label_opts=opts.LabelOpts(
                 is_show=True,
                 position="bottom",
                 font_size=25
             ))
        .set_colors(["#1E90FF", "#CD5C5C", "#FF8C00"])
        .set_global_opts(title_opts=opts.TitleOpts(title="情感分析-情感等级",
                                                   title_textstyle_opts=opts.TextStyleOpts(
                                                       color="#000080",
                                                       font_size=30),
                                                   pos_left="center"),
                         tooltip_opts=opts.TooltipOpts(trigger="item"),
                         legend_opts=opts.LegendOpts(pos_top="bottom")
                         )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )

    # 绘制词云图
    word_cloud = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add(series_name="",
             data_pair=[list(z) for z in zip(
                 word_count["word"].tolist(),
                 word_count["count"].tolist()
             )])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图",
                                                   title_textstyle_opts=opts.TextStyleOpts(
                                                       color="#000080",
                                                       font_size=30))
                         )
    )

    # 设置网页基本属性
    web_page = (
        Page(layout=Page.DraggablePageLayout,
             page_title="广东省体育局新闻标题数据可视化")
        .add(sun, bar.overlap(line), word_cloud, pie)
    )
    # 网页渲染
    # web_page.render("render.html")

    # 渲染好网页之后保存配置JSON文件，生成最终的图表
    web_page.save_resize_html(source="render.html",
                              cfg_file="chart_config.json",
                              dest="广东省体育局新闻标题数据可视化.html")

    print("可视化完成。")
