# -*- coding: utf-8 -*-
"""
任务一 & 任务二：环境部署验证 + 建库建集合 + 导入数据集
对应 ST-1（连接验证）、ST-2.1/ST-2.2/ST-2.3
运行：python3 01_setup_import.py
"""
import json
import os
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from bson import json_util

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]

# 为保证可重复执行，先清空（实训演示环境，正式数据请勿随意 drop）
for name in ["books", "readers", "borrow_logs", "category_stats", "book_logs"]:
    try:
        db[name].drop()
    except OperationFailure:
        pass
# 删除视图（视图不是普通集合，需要通过 system 视图删除）
try:
    db.command("drop", "book_in_stock")
except OperationFailure:
    pass


def load(fn):
    with open(os.path.join(DATA, fn), "r", encoding="utf-8") as f:
        return json.load(f, object_hook=json_util.object_hook)


print("=" * 60)
print("ST-2.1 创建业务数据库与普通集合")
print("=" * 60)
# 普通集合（显式创建；即使为空也会立即建立）
for c in ["books", "readers", "category_stats"]:
    db.create_collection(c)
    print(f"  普通集合已创建: {c}")

print()
print("=" * 60)
print("ST-2.2 创建三种特殊集合")
print("=" * 60)
# (1) 固定集合 book_logs：容量 1MB，最多 1000 条
db.create_collection(
    "book_logs",
    capped=True,
    size=1048576,   # 1MB
    max=1000,       # 最多 1000 条文档
)
print("  固定集合 book_logs 创建成功 (capped=True, size=1MB, max=1000)")

# (2) 时间序列集合 borrow_logs：时间字段 borrow_date，粒度 hours，5 年过期
db.create_collection(
    "borrow_logs",
    timeseries={
        "timeField": "borrow_date",
        "metaField": "reader_card",      # 用借阅证号作为元数据
        "granularity": "hours",
    },
    expireAfterSeconds=157680000,          # 5 年（5×365×24×3600）
)
print("  时间序列集合 borrow_logs 创建成功 (timeField=borrow_date, granularity=hours, expireAfter=5年)")

# (3) 视图 book_in_stock：基于 books，过滤 stock > 0
db.create_collection(
    "book_in_stock",
    viewOn="books",
    pipeline=[{"$match": {"stock": {"$gt": 0}}}],
)
print("  视图 book_in_stock 创建成功 (基于 books, stock>0)")

print()
print("  --- 各集合选项 / 类型标记 ---")
for c in db.list_collections():
    name = c["name"]
    info = c["options"]
    type_mark = []
    if info.get("capped"):
        type_mark.append("固定集合(capped)")
    if "timeseries" in info:
        type_mark.append("时间序列集合")
    if c["type"] == "view":
        type_mark.append("视图")
    mark = "[" + "/".join(type_mark) + "]" if type_mark else "[普通集合]"
    print(f"  {name:16s} {mark}  options={info}")

print()
print("=" * 60)
print("ST-2.3 录入配套数据集")
print("=" * 60)

# ---- books：insertOne 单独录第一条，其余 insertMany ----
books = load("books.txt")
first, rest = books[0], books[1:]
r = db.books.insert_one(first)
print(f"  books.insert_one() -> 插入 1 条, _id={r.inserted_id}")
r = db.books.insert_many(rest)
print(f"  books.insert_many() -> 插入 {len(r.inserted_ids)} 条")

# ---- readers ----
readers = load("readers.txt")
first, rest = readers[0], readers[1:]
r = db.readers.insert_one(first)
print(f"  readers.insert_one() -> 插入 1 条, _id={r.inserted_id}")
r = db.readers.insert_many(rest)
print(f"  readers.insert_many() -> 插入 {len(r.inserted_ids)} 条")

# ---- borrow_logs（时间序列集合）----
logs = load("borrow_logs.txt")
first, rest = logs[0], logs[1:]
r = db.borrow_logs.insert_one(first)
print(f"  borrow_logs.insert_one() -> 插入 1 条, _id={r.inserted_id}")
r = db.borrow_logs.insert_many(rest)
print(f"  borrow_logs.insert_many() -> 插入 {len(r.inserted_ids)} 条")

print()
print("=" * 60)
print("各集合文档数量核对")
print("=" * 60)
for c in ["books", "readers", "borrow_logs", "category_stats", "book_logs"]:
    print(f"  {c:16s}: {db[c].count_documents({})} 条")
print(f"  book_in_stock(视图): {db.book_in_stock.count_documents({})} 条")

client.close()
print("\n导入完成，连接已关闭。")
