# -*- coding: utf-8 -*-
"""
S3 权限验证：在 mongod 以 --auth 启动后运行。
- libReader（只读）：读应成功，写应被拒绝
- libWriter（读写）：读、写均应成功
"""
from pymongo import MongoClient
from pymongo.errors import OperationFailure

READER = "mongodb://libReader:Reader%40123@127.0.0.1:27017/library?authSource=admin"
WRITER = "mongodb://libWriter:Writer%40123@127.0.0.1:27017/library?authSource=admin"

def try_read(uri, label):
    try:
        n = MongoClient(uri)["library"]["books"].count_documents({})
        print(f"  [{label}] 读 books 成功，文档数={n}  OK")
    except OperationFailure as e:
        print(f"  [{label}] 读被拒绝 code={e.code}: {e}")

def try_write(uri, label):
    try:
        MongoClient(uri)["library"]["book_logs"].insert_one(
            {"msg": f"write test by {label}", "ok": 1})
        print(f"  [{label}] 写(insert)成功  OK")
    except OperationFailure as e:
        print(f"  [{label}] 写被拒绝 code={e.code}: {e}")

print("=" * 60)
print("以只读账号 libReader 验证")
print("=" * 60)
try_read(READER, "libReader")
try_write(READER, "libReader")

print()
print("=" * 60)
print("以读写账号 libWriter 验证")
print("=" * 60)
try_read(WRITER, "libWriter")
try_write(WRITER, "libWriter")

print()
print("=" * 60)
print("无账号匿名访问验证")
print("=" * 60)
try:
    n = MongoClient("mongodb://127.0.0.1:27017/")["library"]["books"].count_documents({})
    print(f"  [匿名] 竟然能读，文档数={n}（异常）")
except OperationFailure as e:
    print(f"  [匿名] 读被拒绝 code={e.code}（启用访问控制后匿名不可访问）OK")
