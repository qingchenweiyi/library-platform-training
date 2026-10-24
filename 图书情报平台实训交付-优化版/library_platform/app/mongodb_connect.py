# -*- coding: utf-8 -*-
"""
mongodb_connect.py —— 数据库连接模块（ST-5.2）
统一封装 MongoClient 连接逻辑，后续所有模块都从这里获取数据库句柄。
若 mongod 未开启 --auth，可把 URI 改为 "mongodb://127.0.0.1:27017/"。
"""
from pymongo import MongoClient

# 连接参数在此统一定义（读写账号 libWriter，authSource=admin）
MONGO_URI = "mongodb://libWriter:Writer%40123@127.0.0.1:27017/?authSource=admin"
DB_NAME = "library"

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    """返回 library 数据库对象。"""
    return get_client()[DB_NAME]

def get_collection(name):
    return get_db()[name]

def server_status():
    """返回 (是否正常, 版本号)。"""
    try:
        info = get_client().server_info()
        return True, info.get("version", "unknown")
    except Exception as e:
        return False, str(e)

def close():
    global _client
    if _client is not None:
        _client.close()
        _client = None
