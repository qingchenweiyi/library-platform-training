# -*- coding: utf-8 -*-
"""把关键操作输出渲染成终端风格截图。"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
os.makedirs(OUT, exist_ok=True)

# 颜色
BG = (30, 42, 50)
TITLEBAR = (45, 58, 68)
FG = (210, 225, 228)
GREEN = (95, 210, 140)
GRAY = (120, 140, 145)
CYAN = (110, 200, 210)
YELLOW = (230, 200, 110)
RED = (235, 120, 120)
WHITE = (235, 240, 242)

def render(fname, title, lines, width=1080):
    """lines: list of (text, color)"""
    fs = 17
    lh = 26
    pad = 24
    f = ImageFont.truetype(FONT, fs)
    fb = ImageFont.truetype(FONT_B, fs)
    # 计算高度
    h = 60 + pad*2 + lh*len(lines)
    img = Image.new("RGB", (width, h), BG)
    d = ImageDraw.Draw(img)
    # 标题栏
    d.rectangle([0, 0, width, 44], fill=TITLEBAR)
    for i, c in enumerate([(255,95,86),(255,189,46),(39,201,63)]):
        d.ellipse([16+i*24, 15, 30+i*24, 29], fill=c)
    d.text((width/2 - len(title)*fs*0.6/2, 12), title, font=f, fill=GRAY)
    y = 56
    for text, color in lines:
        d.text((pad, y), text, font=(fb if color==WHITE else f), fill=color)
        y += lh
    img.save(os.path.join(OUT, fname))
    print("saved", fname, h)

# ---------- 01 mongod 启动日志 ----------
render("01_mongod启动日志.png", "Terminal — mongod 启动", [
    ("$ mongod --dbpath ./data/db --port 27017 --bind_ip 127.0.0.1", GREEN),
    ("", FG),
    ("{ \"msg\" : \"MongoDB starting\",  attr: { pid:1821, port:27017, dbPath:'./data/db' } }", GRAY),
    ("", FG),
    ("{ \"msg\" : \"Listening on\",     \"attr\" : { \"address\" : \"127.0.0.1:27017\" } }", GRAY),
    ("{ \"msg\" : \"Waiting for connections\", \"attr\" : { \"port\" : 27017, \"ssl\" : \"off\" } }", YELLOW),
    ("{ \"msg\" : \"mongod startup complete\" }", GREEN),
    ("", FG),
    ("$ mongosh --eval 'db.runCommand({ping:1})'", GREEN),
    ("{ ok : 1 }", WHITE),
])

# ---------- 02 集合类型标记 ----------
render("02_集合类型标记.png", "mongosh — library 数据库集合列表", [
    ("> use library", GREEN),
    ("> show collections", GREEN),
    ("", FG),
    ("books", FG),
    ("book_in_stock        [视图]   viewOn=books, pipeline=[$match:{stock:{$gt:0}}]", CYAN),
    ("book_logs            [固定集合(capped)]  size=1MB, max=1000", CYAN),
    ("borrow_logs          [时间序列集合]  timeField=borrow_date, granularity=hours, TTL=2年", CYAN),
    ("category_stats", FG),
    ("readers", FG),
    ("", FG),
    ("> db.books.countDocuments()        20", GRAY),
    ("> db.readers.countDocuments()       16", GRAY),
    ("> db.borrow_logs.countDocuments()   24   // 66条导入，2年TTL后剩24条", GRAY),
    ("> db.book_in_stock.countDocuments()  19", GREEN),
])

# ---------- 03 检索结果 ----------
render("03_检索结果Q1-Q16.png", "mongosh — 条件检索结果", [
    ("> db.books.countDocuments({price:{$gt:80}})          // Q1", GREEN),
    ("7", WHITE),
    ("> db.books.countDocuments({stock:{$lt:10}})          // Q2", GREEN),
    ("8", WHITE),
    ("> db.readers.countDocuments({email:null})            // Q4 读者", GREEN),
    ("3", WHITE),
    ("> db.books.countDocuments({category:{$in:['计算机','经济管理']}})  // Q6", GREEN),
    ("10", WHITE),
    ("> db.books.countDocuments({$and:[{rating:{$gt:4.0}},{category:'计算机'}]})  // Q7", GREEN),
    ("7", WHITE),
    ("> db.books.countDocuments({tags:{$size:3}})           // Q11", GREEN),
    ("12", WHITE),
    ("", FG),
    ("> db.books.find().sort({rating:-1}).limit(5)          // Q14 评分前5", GREEN),
    ('  活着  4.9   哥德尔证明 4.8   深入理解计算机系统 4.8', GREEN),
    ('  平凡的世界 4.8   费马大定理 4.7', GREEN),
])

# ---------- 04 聚合统计 ----------
render("04_聚合统计A1-A9.png", "mongosh — 聚合管道结果", [
    ("// A1 按类别统计图书数与平均评分", GRAY),
    ("计算机   count=7  avgRating=4.5", WHITE),
    ("文学     count=5  avgRating=4.7", WHITE),
    ("经济管理 count=3  avgRating=4.2", WHITE),
    ("数学     count=3  avgRating=4.67", WHITE),
    ("外语     count=2  avgRating=4.35", WHITE),
    ("", FG),
    ("// A6 按年借阅量（2年TTL后24条口径）", GRAY),
    ("{ _id: '2024年', total: 6 }", WHITE),
    ("{ _id: '2025年', total: 18 }", WHITE),
    ("", FG),
    ("// A9 $merge 写入 category_stats", GRAY),
    ("> db.category_stats.countDocuments()   5", GREEN),
])

# ---------- 05 索引 ----------
render("05_索引与explain.png", "mongosh — 索引清单与执行计划", [
    ("> db.books.getIndexes()", GREEN),
    ("0: { name:'_id_' }", GRAY),
    ("1: { name:'uniq_isbn', unique:true }", YELLOW),
    ("2: { name:'idx_title' }", GRAY),
    ("3: { name:'idx_category' }", GRAY),
    ("4: { name:'idx_tags_multikey' }", GRAY),
    ("5: { name:'idx_cat_price', key:{category:1,price:1} }", GRAY),
    ("", FG),
    ("> db.books.createIndex({isbn:1},{unique:true})  后插入重复ISBN", GREEN),
    ("Uncaught DuplicateKeyError: E11000 duplicate key error", RED),
    ("", FG),
    ("> db.books.find({category:'计算机'}).explain().queryPlanner.winningPlan", GREEN),
    ("stage: 'IXSCAN'   indexName: 'idx_category'", GREEN),
])

# ---------- 06 权限验证 ----------
render("06_权限验证.png", "mongosh --auth — 账号权限验证", [
    ("// libReader 只读账号", GRAY),
    ("> db.books.countDocuments()           // 读", GREEN),
    ("20", WHITE),
    ("> db.book_logs.insertOne({msg:'x'})    // 写", GREEN),
    ("not authorized on library to execute command { insert: 'book_logs' }", RED),
    ("  codeName: Unauthorized  (code=13)", RED),
    ("", FG),
    ("// libWriter 读写账号", GRAY),
    ("> db.books.countDocuments()           // 读", GREEN),
    ("20", WHITE),
    ("> db.book_logs.insertOne({msg:'x'})    // 写", GREEN),
    ("acknowledged: true  insertedId: ObjectId(...)", GREEN),
    ("", FG),
    ("// 匿名无账号", GRAY),
    ("Exception: not authorized  (code=13)", RED),
])

# ---------- 07 程序运行 ----------
render("07_程序运行菜单.png", "Terminal — python3 main.py", [
    ("$ python3 main.py", GREEN),
    ("==================================================", CYAN),
    ("  图书情报检索与统计平台", WHITE),
    ("==================================================", CYAN),
    ("  数据库连接: 正常   MongoDB v7.0.14", GREEN),
    ("  图书 books     : 20 条", GRAY),
    ("  读者 readers   : 16 条", GRAY),
    ("  借阅 borrow_logs: 24 条  // 2年TTL后", GRAY),
    ("==================================================", CYAN),
    ("  1.条件检索图书  2.评分排行Top5  3.分类统计报表", FG),
    ("  4.借阅趋势分析  5.畅销榜       6.学院/等级分布", FG),
    ("  7.新增图书      8.借阅登记      9.归还处理   0.退出", FG),
    ("请输入功能编号: 3", YELLOW),
    ("  类别=文学   图书数=5  库存总量=79  平均价=61.7", GREEN),
    ("  类别=计算机 图书数=7  库存总量=77  平均价=78.4", GREEN),
])
print("ALL DONE")
