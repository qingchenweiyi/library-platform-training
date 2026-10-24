# -*- coding: utf-8 -*-
"""
任务四（上）：聚合管道 A1-A9
运行前先执行 01_setup_import.py、02_queries.py。
"""
import json
from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]
books, logs = db["books"], db["borrow_logs"]

def show(title, cursor):
    print("-" * 60)
    print(title)
    rows = list(cursor)
    for r in rows:
        print("   ", json.dumps(r, ensure_ascii=False, default=str))
    print(f"   -> 共 {len(rows)} 行")
    return rows

print("=" * 64)
print("A1 按类别统计数量与平均评分 ($group+$sum/$avg)")
print("=" * 64)
a1 = list(books.aggregate([
    {"$group": {"_id": "$category",
                "book_count": {"$sum": 1},
                "avg_rating": {"$avg": "$rating"}}},
    {"$sort": {"book_count": -1}},
]))
for r in a1:
    print(f"   {r['_id']:6s} 图书数={r['book_count']:2d}  平均评分={round(r['avg_rating'],2)}")
print(f"   -> 共 {len(a1)} 组")

print()
print("=" * 64)
print("A2 各出版社图书数量 Top5 ($group+$sort/$limit)")
print("=" * 64)
show("publisher top5", books.aggregate([
    {"$group": {"_id": "$publisher", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5},
]))

print()
print("=" * 64)
print("A3 文档数最多的类别 ($sortByCount)")
print("=" * 64)
show("sortByCount category", books.aggregate([{"$sortByCount": "$category"}]))

print()
print("=" * 64)
print("A4 评分最高的3本图书：书名+借阅次数 ($sort+$limit+$project)")
print("=" * 64)
show("top rating books", books.aggregate([
    {"$sort": {"rating": -1}},
    {"$limit": 3},
    {"$project": {"_id": 0, "title": 1, "borrow_count": 1, "rating": 1}},
]))

print()
print("=" * 64)
print("A5 每本书销售额=单价*借阅次数，保留两位 ($multiply+$round)")
print("=" * 64)
a5 = list(books.aggregate([
    {"$project": {"_id": 0, "title": 1,
                 "sales": {"$round": [{"$multiply": ["$price", "$borrow_count"]}, 2]}}},
    {"$sort": {"sales": -1}},
]))
for r in a5[:5]:
    print(f"   {r['title'][:20]:22s} 销售额={r['sales']}")
print(f"   -> 共 {len(a5)} 行")

print()
print("=" * 64)
print("A6 按借阅年份分组借阅量，格式化为'2024年' ($dateToString)")
print("=" * 64)
a6 = list(logs.aggregate([
    {"$group": {"_id": {"$dateToString": {"format": "%Y年", "date": "$borrow_date"}},
                "borrow_total": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
]))
for r in a6:
    print(f"   {r['_id']}  借阅量={r['borrow_total']}")

print()
print("=" * 64)
print("A7 每位读者借阅次数 Top5 ($group+$sort+$limit)")
print("=" * 64)
show("top readers", logs.aggregate([
    {"$group": {"_id": "$reader_card", "cnt": {"$sum": 1}}},
    {"$sort": {"cnt": -1}},
    {"$limit": 5},
]))

print()
print("=" * 64)
print("A8 关联读者与借阅流水：学院借阅量排行榜 ($lookup)")
print("=" * 64)
a8 = list(logs.aggregate([
    {"$lookup": {"from": "readers",
                  "localField": "reader_card",
                  "foreignField": "card_no",
                  "as": "reader"}},
    {"$unwind": "$reader"},
    {"$group": {"_id": "$reader.college", "borrow_total": {"$sum": 1}}},
    {"$sort": {"borrow_total": -1}},
]))
for r in a8:
    print(f"   {r['_id']:14s} 借阅量={r['borrow_total']}")

print()
print("=" * 64)
print("A9 把 A1 分类统计结果写入 category_stats ($merge)")
print("=" * 64)
db.category_stats.delete_many({})  # 演示前清空，保证幂等
list(books.aggregate([
    {"$group": {"_id": "$category",
                "book_count": {"$sum": 1},
                "avg_rating": {"$avg": "$rating"}}},
    {"$merge": {"into": "category_stats", "whenMatched": "replace", "whenNotMatched": "insert"}},
]))
print(f"   category_stats 现有文档数: {db.category_stats.count_documents({})}")
for r in db.category_stats.find():
    print("   ", json.dumps(r, ensure_ascii=False, default=str))

client.close()
print("\nA1-A9 完成。")
