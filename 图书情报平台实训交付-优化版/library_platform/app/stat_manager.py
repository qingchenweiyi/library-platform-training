# -*- coding: utf-8 -*-
"""
stat_manager.py —— 统计模块（ST-5.4 聚合管道编程）
分类统计、借阅趋势、畅销榜。
"""
from mongodb_connect import get_collection

books = get_collection("books")
logs = get_collection("borrow_logs")

def category_stat():
    """按类别分组：库存总量、平均价格、图书数量，按库存总量降序。"""
    return list(books.aggregate([
        {"$group": {
            "_id": "$category",
            "book_count": {"$sum": 1},
            "total_stock": {"$sum": "$stock"},
            "avg_price": {"$avg": "$price"},
        }},
        {"$sort": {"total_stock": -1}},
    ]))

def borrow_trend():
    """按年份分组统计借阅量，格式化为 '2024年'。"""
    return list(logs.aggregate([
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y年", "date": "$borrow_date"}},
            "total": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))

def bestseller(limit=5):
    """借阅次数最多的图书。"""
    return list(books.find({}, {"title": 1, "borrow_count": 1, "_id": 0})
                .sort("borrow_count", -1).limit(limit))
