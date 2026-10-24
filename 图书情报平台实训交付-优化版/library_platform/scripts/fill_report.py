# -*- coding: utf-8 -*-
"""按实验报告模板生成最终报告（数科2班-202414870218-白岩松），并嵌入修正后的截图。"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../library_platform
SHOT = os.path.join(ROOT, "screenshots")
TEMPLATE = os.path.join(ROOT, "_report_template.docx")
OUT = os.path.join(os.path.dirname(ROOT), "实验报告-数科2班-202414870218-白岩松.docx")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = Document(TEMPLATE)

def set_font(run, size=10.5, bold=False, font="宋体"):
    run.font.size = Pt(size); run.font.bold = bold
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)

def para(cell, text, size=10.5, bold=False, first=False):
    if first and not cell.paragraphs[0].runs:
        p = cell.paragraphs[0]
    else:
        p = cell.add_paragraph()
    r = p.add_run(text); set_font(r, size, bold)
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = 1.3
    return p

# ---- 页眉：班级 / 学号 / 姓名 / 实验日期 / 第X次报告 ----
def rewrite_para(p, text, size=10.5, bold=False):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    r = p.add_run(text); set_font(r, size, bold)
    return p

rewrite_para(doc.paragraphs[1],
             "班  级：数科2班       学号：202414870218       姓名：白岩松")
rewrite_para(doc.paragraphs[2],
             "实验日期：2026年10月12日       第1次报告")

t = doc.tables[0]

def pic(cell, name):
    p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    p.add_run().add_picture(os.path.join(SHOT, name), width=Cm(13.5))

# 0 课程名称 / 1 实验题目
r0 = t.rows[0].cells[0].paragraphs[0]; r0.add_run("  NoSQL数据库技术与应用（第2版）")
for run in r0.runs: set_font(run)
r1 = t.rows[1].cells[0].paragraphs[0]; r1.add_run("  图书情报检索与统计平台——MongoDB基础操作综合实训")
for run in r1.runs: set_font(run)

# 2 实验目的与要求
c = t.rows[2].cells[1]
for line in [
    "1. 掌握 MongoDB 的安装部署及 mongod 启动参数（端口、数据目录）；",
    "2. 掌握数据库、普通集合、固定集合、时间序列集合与视图的创建与验证；",
    "3. 掌握文档的增删改查，以及比较、逻辑、数组、正则、$exists、$type 等查询操作符；",
    "4. 掌握聚合管道（$group/$sort/$lookup/$merge 等）、单键/唯一/多键/复合索引及 explain 执行计划；",
    "5. 掌握数据库用户与读写权限的创建与验证；",
    "6. 使用 PyMongo 开发菜单式命令行应用，完成图书、读者、借阅、统计四大模块。",
]:
    para(c, line)

# 3 实验环境配置
c = t.rows[3].cells[1]
for line in [
    "· 计算机：华硕 ASUS Vivobook S 15，内存 32GB；",
    "· 操作系统：Windows 11；",
    "· 数据库：MongoDB Community Server 7.0.14，监听端口 27017，自定义数据目录；",
    "· 编程语言：Python 3.12；数据库驱动：PyMongo 4.18.3；",
    "· 开发工具：PyCharm；图形化工具：MongoDB Compass 1.40。",
]:
    para(c, line)

# 实验内容与实验步骤和结果
c = t.rows[4].cells[1]
for p in list(c.paragraphs):
    p._element.getparent().remove(p._element)
def step(title, text):
    para(c, title, bold=True)
    for ln in text:
        para(c, ln)

step("（1）环境部署与建库", [
    "安装并启动 mongod（端口 27017，自定义数据目录），日志出现 Waiting for connections 与 startup complete 即成功。",
    "创建 library 库；创建固定集合 book_logs（1MB、最多1000条）、时间序列集合 borrow_logs（时间字段 borrow_date、粒度 hours、2年过期）、视图 book_in_stock（stock>0）。",
    "导入 books(20)、readers(16)、borrow_logs(66) 三个数据集并核对文档数（borrow_logs 因 2 年 TTL 清理后剩 24 条）。",
])
pic(c, "01_mongod启动日志.png")
pic(c, "02_集合类型标记.png")

step("（2）检索功能实现", [
    "Q1 定价>80元=7条；Q2 库存<10=8条；Q4 email为空读者=3条；Q6 计算机或经济管理=10条；",
    "Q7 评分>4.0且计算机类=7条；Q10 tags含编程与入门=1条；Q11 恰好3个标签=12条；Q12 存在tags字段=17条；",
    "Q14 评分降序前5：活着4.9、哥德尔证明4.8、深入理解计算机系统4.8、平凡的世界4.8、费马大定理4.7。",
    "完成更新删除：库存$inc、分类$mul打折、$currentDate时间戳、$unset删字段、deleteOne/deleteMany、replaceOne。",
])
pic(c, "03_检索结果Q1-Q16.png")

step("（3）统计分析与索引", [
    "A1 按类别分组：计算机7本、文学5、经济管理3、数学3、外语2；A3 最多类别为计算机；",
    "A4 评分最高：活着243次、平凡的世界167次、深入理解计算机系统156次；",
    "A6 按年借阅量（格式化“2024年”）：2024年6次、2025年18次（2年TTL后24条口径）；A9 用 $merge 将结果写入 category_stats。",
    "建立 isbn 唯一索引（重复ISBN被拒）、title/category单键索引、tags多键索引、category+price复合索引；explain 显示走 IXSCAN。",
])
pic(c, "04_聚合统计A1-A9.png")
pic(c, "05_索引与explain.png")

step("（4）权限管理", [
    "创建只读账号 libReader(read) 与读写账号 libWriter(readWrite+dbAdmin)；以 --auth 重启后验证：",
    "libReader 可读但写被拒（code=13 Unauthorized），libWriter 可读可写，匿名访问被拒。",
])
pic(c, "06_权限验证.png")

step("（5）PyMongo 应用程序", [
    "编写 mongodb_connect/book_manager/reader_manager/borrow_manager/stat_manager/main 共6个文件；",
    "启动时打印连接状态与各集合文档数；菜单含9个功能项，覆盖检索、统计、更新、删除，变更打印受影响条数。",
    "说明：borrow_logs 为时间序列集合，MongoDB 不支持对其普通字段更新，故“归还处理”采用 deleteMany 删除在借记录 + insert_one 追加“已归还”流水的方式实现（同一条借阅仅保留一条记录）。",
])
pic(c, "07_程序运行菜单.png")

# 5 心得体会
c = t.rows[5].cells[1]
para(c, "通过本次实训，我完整走通了从 MongoDB 部署、数据建模、条件检索、聚合统计、索引优化到权限控制和 PyMongo 应用开发的全过程。")
para(c, "最大的收获有三点：一是理解了固定集合、时间序列集合与视图三种特殊集合的适用场景；二是通过聚合管道完成了分类统计与借阅趋势分析，体会到文档型数据库灵活模式的优势；三是在开启访问控制后通过账号权限验证，直观理解了 read/readWrite 角色的区别。")
para(c, "遇到的主要问题：一是时间序列集合“数据变少”，排查发现是 2 年 TTL 自动清理了 2024-10 之前的历史记录，属于预期生命周期机制；二是时间序列集合不支持普通字段更新，导致“归还处理”最初报错，最终改用删除在借记录并追加“已归还”流水的方式解决；三是开启 --auth 后程序连接被拒，通过统一配置账号并对特殊字符做 URL 编码解决。")

# 删除模板中重复的“实验内容”行
if len(t.rows) > 6:
    dup_row = t.rows[6]
    dup_row._element.getparent().remove(dup_row._element)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print("saved:", os.path.abspath(OUT))
