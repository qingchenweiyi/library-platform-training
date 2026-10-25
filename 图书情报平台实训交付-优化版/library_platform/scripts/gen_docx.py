# -*- coding: utf-8 -*-
"""生成《图书情报检索与统计平台·技术文档》.docx（修正版：借阅流水/TTL/A6-A8 数字已核对）"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "技术文档.docx")
doc = Document()

sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.top_margin = sec.bottom_margin = Cm(2.2)
sec.left_margin = sec.right_margin = Cm(2.4)

normal = doc.styles["Normal"]
normal.font.name = "宋体"
normal.font.size = Pt(10.5)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

def set_cn(run, font="宋体", size=10.5, bold=False, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    if color:
        run.font.color.rgb = RGBColor(*color)

def title(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); set_cn(r, "黑体", 18, True)
    p.paragraph_format.space_after = Pt(4)

def subtitle(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); set_cn(r, "宋体", 10.5, False, (90, 90, 90))
    p.paragraph_format.space_after = Pt(10)

def h1(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); set_cn(r, "黑体", 14, True, (38, 70, 83))

def h2(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text); set_cn(r, "黑体", 11.5, True, (42, 109, 99))

def body(text):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Pt(21)
    p.paragraph_format.line_spacing = 1.4; p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text); set_cn(r, "宋体", 10.5)
    return p

def bullet(text):
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(18)
    p.paragraph_format.line_spacing = 1.35
    r = p.add_run("· " + text); set_cn(r, "宋体", 10.5)

def code(text):
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text); set_cn(r, "Consolas", 9, False, (40, 40, 40))
    shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "F2F4F4")
    p._p.get_or_add_pPr().append(shd)

def add_table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(htext); set_cn(r, "黑体", 9.5, True, (255, 255, 255))
        shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "264653")
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val)); set_cn(r, "宋体", 9.5)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ============ 内容 ============
title("图书情报检索与统计平台 · 技术文档")
subtitle("《NoSQL 数据库技术与应用（第 2 版）》第 3 章 MongoDB 基础操作 · 实训项目\n"
         "运行环境：Ubuntu 22.04 / MongoDB Community Server v7.0.14 / Python 3.12 + PyMongo 4.18")

h1("一、项目概述")
body("项目背景：某高校图书馆需建设“图书情报检索与统计平台”，统一管理馆藏图书、读者信息与借阅流水，"
     "并提供多维度检索、分类统计与借阅趋势分析服务。")
body("业务目标：基于 MongoDB 完成数据库部署、数据建模、条件检索、聚合统计、索引优化与访问控制，"
     "并使用 PyMongo 开发菜单式命令行应用，覆盖图书、读者、借阅、统计四大模块。")
h2("组内分工")
body("本项目由白岩松独自完成，独立承担任务一至任务六全部工作：环境部署、建库与数据导入、条件检索与更新删除、聚合统计与索引优化、PyMongo 程序开发、权限验证与文档整理。")

h1("二、环境与数据建模")
h2("2.1 部署关键参数")
bullet("数据库进程 mongod，监听端口 27017，绑定 127.0.0.1；自定义数据目录 ./data/db。")
bullet("验收模式以 --auth 启动，创建只读账号 libReader(read) 与读写账号 libWriter(readWrite+dbAdmin)。")
code("mongod --dbpath ./data/db --port 27017 --bind_ip 127.0.0.1 --auth")
body("启动成功标志为日志出现 Waiting for connections 与 mongod startup complete。")

h2("2.2 数据库与集合设计")
body("数据库名 library，共 4 个业务集合与 3 个特殊集合：")
add_table(["集合", "类型", "关键字段", "文档数"],
          [["books", "普通集合", "isbn,title,author,category,price,stock,rating,tags", "20"],
           ["readers", "普通集合", "card_no,name,college,level,register_date", "16"],
           ["borrow_logs", "时间序列集合", "borrow_date(time),reader_card,book_isbn,status", "66→52*"],
           ["category_stats", "普通集合", "聚合结果（_id=类别）", "5"],
           ["book_logs", "固定集合(capped)", "容量 1MB、最多 1000 条", "0"],
           ["book_in_stock", "视图", "基于 books 过滤 stock>0", "19"]],
          widths=[2.8, 2.6, 7.6, 2])
body("* borrow_logs 导入 66 条流水；时间序列集合设置 expireAfterSeconds=157680000（5 年自动过期）。"
     "借阅日期分布在 2023—2025 年，系统当前为 2026-10，5 年保留期完整覆盖全部数据，TTL 不清理任何记录，导入即 66 条。"
     "任务三 D1/D2 删除演示后再删 1 条已归还 + 13 条逾期，变为 52 条。")
code('db.createCollection("book_logs",{capped:true,size:1048576,max:1000});\n'
     'db.createCollection("borrow_logs",{timeseries:{timeField:"borrow_date",\n'
     '  metaField:"reader_card",granularity:"hours"},expireAfterSeconds:157680000});\n'
     'db.createCollection("book_in_stock",{viewOn:"books",\n'
     '  pipeline:[{$match:{stock:{$gt:0}}}]});')

h2("2.3 索引设计")
add_table(["索引名", "字段", "类型"],
          [["uniq_isbn", "isbn", "唯一索引（重复 ISBN 插入被拒）"],
           ["idx_title", "title", "单键索引"],
           ["idx_category", "category", "单键索引"],
           ["idx_tags_multikey", "tags", "多键索引（数组）"],
           ["idx_cat_price", "category+price", "复合索引"]],
          widths=[4.2, 3.5, 8.3])
body("explain() 验证：按 category 等值查询命中 idx_category，执行阶段为 IXSCAN 索引扫描，而非全表 COLLSCAN。")

h1("三、功能实现")
h2("3.1 检索结果（任务三）")
add_table(["编号", "业务需求", "操作符", "结果条数"],
          [["Q1", "定价 > 80 元", "$gt", "7"],
           ["Q2", "库存 < 10 本", "$lt", "8"],
           ["Q3", "ISBN 精确查找", "$eq", "1"],
           ["Q4", "email 为空的读者", "$eq:null", "3"],
           ["Q5", "排除人民邮电出版社", "$ne", "16"],
           ["Q6", "类别∈{计算机,经济管理}", "$in", "10"],
           ["Q7", "评分>4.0 且 计算机类", "$and", "7"],
           ["Q8", "评分<3.5 或 库存=0", "$or", "1"],
           ["Q9", "书名含 Python", "$regex", "1"],
           ["Q10", "tags 含编程与入门", "$all", "1"],
           ["Q11", "恰好 3 个标签", "$size", "12"],
           ["Q12", "存在 tags 字段", "$exists", "17"],
           ["Q13", "_id 为字符串类型", "$type", "1"],
           ["Q14", "评分降序前 5", "sort+limit", "活着/哥德尔证明/深入理解CS/平凡的世界/费马大定理"],
           ["Q16", "类别清单", "distinct", "外语、数学、文学、经济管理、计算机"]],
          widths=[1.6, 5.4, 2.6, 6.4])
body("更新删除：U1 指定书库存 -5（$inc）；U2 经济管理类 9 折（$mul，matched=3）；"
     "U3 $currentDate 写时间戳；U4 $unset 删除某书 tags；D1 删 1 条已归还记录；"
     "D2 用 deleteMany 删除全部 13 条逾期记录；D3 replaceOne 整体替换读者信息（保留 _id）。"
     "注：borrow_logs 为时间序列集合，D1/D2 依赖 MongoDB 7.0 放开的时间序列删除限制。")

h2("3.2 聚合统计结果（任务四 A1-A9，D1/D2 后 52 条借阅流水口径）")
bullet("A1 分类统计 5 组：计算机 7 本/均分4.5、文学 5/4.7、经济管理 3/4.2、数学 3/4.67、外语 2/4.35。")
bullet("A2 出版社 Top5：人民邮电 4、北京大学 3、清华大学 2、中国人民大学 2、电子工业 2。")
bullet("A3 文档数最多类别（$sortByCount）：计算机（7）。")
bullet("A4 评分最高 3 本：活着(243)、平凡的世界(167)、深入理解计算机系统(156)。")
bullet("A5 销售额=price×borrow_count 保留两位，最高《深入理解计算机系统》21684.0 元。")
bullet("A6 按年借阅量：2023 年 15 条、2024 年 23 条、2025 年 14 条（$dateToString 格式化）。")
bullet("A7 活跃读者 Top5：R20240001(4)、R20240016(4)、R20240009(4)、R20240002(4)、R20240005(3)。")
bullet("A8 $lookup 关联读者，学院借阅排行：计算机 13、数学与统计 9、文学 9、管理 7、外国语 7、经济管理 7（共 52）。")
bullet("A9 用 $merge 将 A1 结果写入 category_stats（5 条）。")

h2("3.3 权限验证（S3）")
add_table(["账号", "读 books", "写 insert", "结论"],
          [["libReader (read)", "成功（20 条）", "被拒 code=13 Unauthorized", "只读生效"],
           ["libWriter (readWrite+dbAdmin)", "成功", "成功", "读写生效"],
           ["匿名无账号", "被拒 code=13", "—", "访问控制生效"]],
          widths=[4.5, 3.5, 5.5, 2.5])

h2("3.4 PyMongo 应用（任务五）")
body("共 6 个源文件：mongodb_connect.py（连接封装）、book_manager.py、reader_manager.py、"
     "borrow_manager.py、stat_manager.py、main.py。启动时打印连接状态与三集合文档数；"
     "菜单含 9 个功能项，覆盖检索、评分排行、分类统计、借阅趋势、畅销榜、读者分布、新增、借阅、归还；"
     "每次变更打印受影响文档数，无结果给出提示，退出前关闭连接。实测启动显示 books 20、readers 16、borrow_logs 52（D1/D2 后）。")
body("时间序列集合约束处理：borrow_logs 为时间序列集合，MongoDB 不支持对其普通字段更新，"
     "故“归还处理”未用 update_many，而改为 deleteMany 删除在借“借出”记录 + insert_one 追加“已归还”流水，"
     "同一条借阅只保留一条记录（见 borrow_manager.return_book 注释）。")

h1("四、问题与核对")
h2("4.1 调试难点与排查")
bullet("时间序列集合“数据变少”：最初 borrow_logs 只能查到 26 条，与导入的 66 条不符。排查为 2 年 TTL"
       "（expireAfterSeconds=63072000）自动清理了 2024-10 前记录；按要求改为 5 年保留期（157680000），"
       "重建集合重新导入后 66 条全部保留。这是生命周期参数设置问题，非操作错误。")
bullet("时间序列集合不支持普通字段更新：最初“归还处理”用 update_many 改 status/return_date 被拒，"
       "改为 deleteMany + insert_one 追加“已归还”流水后正常。")
bullet("开启 --auth 后程序连不上库：在 mongodb_connect.py 统一使用 libWriter 账号并指定 authSource=admin，"
       "特殊字符 @ 需 URL 编码为 %40。")
bullet("唯一索引冲突：为 isbn 建唯一索引后，重复插入测试 ISBN 正确抛出 DuplicateKeyError，约束生效。")

h2("4.2 命令行与 Compass 结果核对")
add_table(["验证内容", "命令行结果", "Compass 核对"],
          [["Q1 定价>80", "7 条", "一致"],
           ["Q2 库存<10", "8 条", "一致"],
           ["Q7 评分与类别组合", "7 条", "一致"],
           ["Q14 评分前 5", "活着等 5 本", "一致"],
           ["A1 分类统计", "5 组", "一致"],
           ["视图 book_in_stock", "19 条", "一致"]],
          widths=[5.5, 5.5, 5])

h2("4.3 交付物清单")
bullet("数据文件：export/books.json、export/category_stats.json（含全字段）。")
bullet("Python 源代码：app/ 目录下 6 个文件，可直接运行。")
bullet("可复现脚本：scripts/ 下建库导入、检索、聚合、索引、权限、导出共 8 个脚本。")
bullet("技术文档：本文档（四节，约 3—4 页）。")

doc.save(OUT)
print("saved:", os.path.abspath(OUT))
