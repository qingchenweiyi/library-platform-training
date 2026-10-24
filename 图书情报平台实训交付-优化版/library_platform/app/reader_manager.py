# -*- coding: utf-8 -*-
"""
reader_manager.py —— 读者管理模块（ST-5.3）
读者信息管理、学院统计、等级分布。
"""
from mongodb_connect import get_collection

readers = get_collection("readers")

def find_readers(query: dict = None):
    return list(readers.find(query or {}, {"_id": 0}))

def count():
    return readers.count_documents({})

def distinct_colleges():
    return readers.distinct("college")

def college_distribution():
    """各学院读者人数。"""
    return list(readers.aggregate([
        {"$group": {"_id": "$college", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))

def level_distribution():
    """借阅等级分布。"""
    return list(readers.aggregate([
        {"$group": {"_id": "$level", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))
