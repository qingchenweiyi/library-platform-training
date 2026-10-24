# -*- coding: utf-8 -*-
"""
borrow_manager.py —— 借阅管理模块（ST-5.3）
借阅登记、归还处理、逾期查询。
"""
from datetime import datetime
from mongodb_connect import get_collection

logs = get_collection("borrow_logs")

def borrow_book(reader_card: str, book_isbn: str):
    """借阅登记，新增一条状态为'借出'的流水。"""
    doc = {
        "borrow_date": datetime.now(),
        "reader_card": reader_card,
        "book_isbn": book_isbn,
        "status": "借出",
    }
    return logs.insert_one(doc).inserted_id

def return_book(reader_card: str, book_isbn: str):
    """归还处理。

    注意：borrow_logs 是时间序列集合，MongoDB 时间序列集合为追加写模型，
    不支持对普通字段（status/return_date）执行更新，只允许修改 metaField。
    因此归还处理采用 MongoDB 7.0 允许的两种操作完成：
        1) deleteMany 删除该读者+该书在借的"借出"流水（7.0 已放开时间序列删除限制）；
        2) insert_one 追加一条"已归还"流水并记录归还时间。
    这样同一条借阅始终只保留一条记录，统计口径不变。
    返回被处理的在借记录条数。
    """
    removed = logs.delete_many(
        {"reader_card": reader_card, "book_isbn": book_isbn, "status": "借出"}
    ).deleted_count
    logs.insert_one({
        "borrow_date": datetime.now(),
        "reader_card": reader_card,
        "book_isbn": book_isbn,
        "status": "已归还",
        "return_date": datetime.now(),
    })
    return removed

def list_overdue():
    return list(logs.find({"status": "逾期"}, {"_id": 0}))

def count():
    return logs.count_documents({})
