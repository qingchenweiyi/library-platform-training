# -*- coding: utf-8 -*-
"""ST-6.3 数据导出：把 category_stats 与 books 导出为 JSON 文件。"""
import json
from bson import json_util
from pymongo import MongoClient

db = MongoClient("mongodb://libWriter:Writer%40123@127.0.0.1:27017/library?authSource=admin")["library"]

for name in ["category_stats", "books"]:
    rows = list(db[name].find())
    out = f"../export/{name}.json"
    with open(out, "w", encoding="utf-8") as f:
        f.write(json_util.dumps(rows, ensure_ascii=False, indent=2))
    print(f"导出 {name}: {len(rows)} 条 -> {out}")
