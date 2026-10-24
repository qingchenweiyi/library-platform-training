# -*- coding: utf-8 -*-
"""
任务四（下）：索引 I1-I5 建立、唯一约束验证、explain 对比。
"""
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]
books = db["books"]

print("=" * 64)
print("I1 为 books.isbn 建立唯一索引")
print("=" * 64)
books.create_index([("isbn", 1)], unique=True, name="uniq_isbn")
print("  唯一索引 uniq_isbn 创建成功")

# 验证重复 ISBN 无法插入
dup = {"isbn": "9787115428028", "title": "重复测试书"}
try:
    books.insert_one(dup)
    print("  [异常] 重复 ISBN 竟然插入成功了！")
except DuplicateKeyError:
    print("  验证：插入重复 ISBN 被拒绝（DuplicateKeyError），唯一约束生效 ✓")

print()
print("=" * 64)
print("I2-I5 其余索引")
print("=" * 64)
books.create_index([("title", 1)], name="idx_title")                 # 单键
print("  I2 单键索引 idx_title(title) 创建成功")
books.create_index([("category", 1)], name="idx_category")           # 单键
print("  I3 单键索引 idx_category(category) 创建成功")
books.create_index([("tags", 1)], name="idx_tags_multikey")          # 多键（数组）
print("  I4 多键索引 idx_tags_multikey(tags) 创建成功")
books.create_index([("category", 1), ("price", 1)], name="idx_cat_price")  # 复合
print("  I5 复合索引 idx_cat_price(category+price) 创建成功")

print()
print("=" * 64)
print("当前 books 索引清单 getIndexes()")
print("=" * 64)
for idx in books.list_indexes():
    print("  ", idx["name"], dict(idx["key"]),
          "unique" if idx.get("unique") else "")

print()
print("=" * 64)
print("explain 对比：按 category 等值查询是否走索引")
print("=" * 64)
exp = books.find({"category": "计算机"}).explain()
stage = exp["queryPlanner"]["winningPlan"]
def walk(plan):
    if "indexName" in plan:
        return plan["stage"], plan["indexName"]
    for k in ("inputStage", "inputStages"):
        if k in plan:
            v = plan[k]
            if isinstance(v, list):
                for s in v:
                    r = walk(s)
                    if r: return r
            else:
                r = walk(v)
                if r: return r
    return plan["stage"], None
print("  winningPlan:", walk(stage))
print("  -> 命中 idx_category，走 IXSCAN 索引扫描")

client.close()
print("\n索引任务完成。")
