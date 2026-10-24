# -*- coding: utf-8 -*-
"""
任务三：检索功能实现（Q1-Q16）+ 更新删除（U1-U4, D1-D3）
对应课件 3.3.6 查询/更新/删除。
运行前请先执行 01_setup_import.py。
"""
import json
from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]
books, readers, logs = db["books"], db["readers"], db["borrow_logs"]

R = {}   # 结果记录
def line(k, v):
    R[k] = v
    print(f"  {k}: {v}")

print("=" * 64)
print("基础检索 Q1-Q6")
print("=" * 64)
line("Q1 price>80 ($gt)", books.count_documents({"price": {"$gt": 80}}))
line("Q2 stock<10 ($lt)", books.count_documents({"stock": {"$lt": 10}}))
isbn_target = "9787115428028"
line(f"Q3 isbn={isbn_target} ($eq)", books.count_documents({"isbn": isbn_target}))
line("Q4 email为空 ($eq:null)", readers.count_documents({"email": {"$eq": None}}))
line("Q5 排除'人民邮电出版社' ($ne)", books.count_documents({"publisher": {"$ne": "人民邮电出版社"}}))
line("Q6 category in [计算机,经济管理] ($in)",
     books.count_documents({"category": {"$in": ["计算机", "经济管理"]}}))

print()
print("=" * 64)
print("组合与高级检索 Q7-Q12")
print("=" * 64)
line("Q7 rating>4.0 且 category=计算机 ($and)",
     books.count_documents({"$and": [{"rating": {"$gt": 4.0}}, {"category": "计算机"}]}))
line("Q8 rating<3.5 或 stock=0 ($or)",
     books.count_documents({"$or": [{"rating": {"$lt": 3.5}}, {"stock": 0}]}))
line("Q9 title 含 Python ($regex)",
     books.count_documents({"title": {"$regex": "Python"}}))
line("Q10 tags 同时含 编程,入门 ($all)",
     books.count_documents({"tags": {"$all": ["编程", "入门"]}}))
line("Q11 tags 恰好3个 ($size:3)", books.count_documents({"tags": {"$size": 3}}))
line("Q12 存在 tags 字段 ($exists:true)",
     books.count_documents({"tags": {"$exists": True}}))

print()
print("=" * 64)
print("结果处理 Q13-Q16")
print("=" * 64)
line("Q13 _id 为字符串类型 ($type:string)", books.count_documents({"_id": {"$type": "string"}}))

print("  Q14 评分降序前5 (sort+limit):")
top5 = list(books.find({}, {"title": 1, "rating": 1, "_id": 0})
            .sort("rating", -1).limit(5))
for i, b in enumerate(top5, 1):
    print(f"     {i}. {b['title']}  评分={b['rating']}")
line("Q14 条数", len(top5))

print("  Q15 投影：只返回 title/price/rating（不含_id）前3条:")
proj = list(books.find({}, {"title": 1, "price": 1, "rating": 1, "_id": 0}).limit(3))
for b in proj:
    print(f"     {b}")
line("Q15 投影样例条数", len(proj))

cats = books.distinct("category")
line("Q16 全部图书类别清单 (distinct)", cats)

print()
print("=" * 64)
print("更新 U1-U4")
print("=" * 64)
# U1：把指定图书库存减少 5
r = books.update_one({"isbn": isbn_target}, {"$inc": {"stock": -5}})
line("U1 stock-5 update_one 匹配/修改数", f"matched={r.matched_count}, modified={r.modified_count}")

# U2：经济管理类所有图书价格打9折
r = books.update_many({"category": "经济管理"}, {"$mul": {"price": 0.9}})
line("U2 经济管理类9折 update_many", f"matched={r.matched_count}, modified={r.modified_count}")

# U3：为图书新增字段并自动记录当前时间 ($currentDate)
r = books.update_one({"isbn": isbn_target},
                     {"$currentDate": {"last_modified": True},
                      "$set": {"note": "实训演示更新"}})
line("U3 新增时间戳字段 ($currentDate)", f"matched={r.matched_count}, modified={r.modified_count}")
doc = books.find_one({"isbn": isbn_target}, {"last_modified": 1, "note": 1, "_id": 0})
print(f"     校验: {doc}")

# U4：删除某本图书的 tags 字段
r = books.update_one({"isbn": isbn_target}, {"$unset": {"tags": ""}})
line("U4 删除 tags 字段 ($unset)", f"matched={r.matched_count}, modified={r.modified_count}")

print()
print("=" * 64)
print("删除 D1-D3")
print("=" * 64)
# D1：删除一条已归还的借阅记录
one_returned = logs.find_one({"status": "已归还"})
if one_returned:
    r = logs.delete_one({"_id": one_returned["_id"]})
    line("D1 删除一条已归还记录 delete_one", f"deleted={r.deleted_count}")
else:
    line("D1 删除一条已归还记录", "无可删除记录")

# D2：先预览，再删除逾期未还记录
overdue_preview = list(logs.find({"status": "逾期"}, {"borrow_date": 1, "reader_card": 1, "book_isbn": 1}))
print(f"  D2 执行前预览：逾期记录共 {len(overdue_preview)} 条")
r = logs.delete_many({"status": "逾期"})
line("D2 清理逾期记录 delete_many", f"deleted={r.deleted_count}")

# D3：整体替换某位读者信息（保留 _id）
victim = readers.find_one({"name": "张明"})
if victim:
    new_info = {
        "card_no": victim["card_no"],
        "name": "张明（已更新）",
        "college": "计算机学院",
        "email": "zhangming_new@example.edu",
        "phone": "13900001111",
        "level": "教师",
        "register_date": victim["register_date"],
        "fav_categories": ["计算机", "数学"],
    }
    r = readers.replace_one({"_id": victim["_id"]}, new_info)
    line("D3 replaceOne 替换读者信息", f"matched={r.matched_count}, modified={r.modified_count}")
else:
    line("D3 replaceOne", "未找到目标读者")

with open("results_task3.json", "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2, default=str)

client.close()
print("\n任务三完成，结果已写入 results_task3.json")
