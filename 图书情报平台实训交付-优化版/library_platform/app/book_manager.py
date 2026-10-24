# -*- coding: utf-8 -*-
"""
book_manager.py —— 图书管理模块（ST-5.3）
实现图书增删改查、条件检索、评分排行。
"""
from mongodb_connect import get_collection

books = get_collection("books")

def add_book(book: dict):
    """新增单本图书，返回 inserted_id。"""
    return books.insert_one(book).inserted_id

def add_books(list_books: list):
    """批量新增，返回插入条数。"""
    return len(books.insert_many(list_books).inserted_ids)

def find_books(query: dict = None, projection=None, limit=0):
    """条件检索，返回列表。"""
    cursor = books.find(query or {}, projection)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

def find_one(query: dict):
    return books.find_one(query)

def update_book(isbn: str, update: dict):
    """更新指定图书，返回 (matched, modified)。"""
    r = books.update_one({"isbn": isbn}, update)
    return r.matched_count, r.modified_count

def delete_book(isbn: str):
    return books.delete_one({"isbn": isbn}).deleted_count

def delete_books(query: dict):
    return books.delete_many(query).deleted_count

def rating_rank(limit=5):
    """按评分降序取前 N 本。"""
    return list(books.find({}, {"title": 1, "rating": 1, "price": 1, "_id": 0})
                .sort("rating", -1).limit(limit))

def count():
    return books.count_documents({})
