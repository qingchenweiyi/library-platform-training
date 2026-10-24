# -*- coding: utf-8 -*-
"""
任务四（尾）：用户与权限 S1-S3。
先在未开启认证时创建账号；随后需以 --auth 重启 mongod 再运行权限验证。
"""
from pymongo import MongoClient

# 连接（创建账号阶段，本地未开认证）
admin_client = MongoClient("mongodb://127.0.0.1:27017/")
admin_db = admin_client["admin"]

# S1：只读账号 libReader，角色 read
try:
    admin_db.command("createUser", "libReader",
                      pwd="Reader@123",
                      roles=[{"role": "read", "db": "library"}])
    print("S1 创建只读账号 libReader (read@library) 成功")
except Exception as e:
    print("S1 已存在或失败:", e)

# S2：读写账号 libWriter，角色 readWrite + dbAdmin
try:
    admin_db.command("createUser", "libWriter",
                      pwd="Writer@123",
                      roles=[{"role": "readWrite", "db": "library"},
                             {"role": "dbAdmin", "db": "library"}])
    print("S2 创建读写账号 libWriter (readWrite+dbAdmin@library) 成功")
except Exception as e:
    print("S2 已存在或失败:", e)

# 列出当前用户
print("\n当前 admin 库用户清单:")
for u in admin_db.command("usersInfo")["users"]:
    print("  ", u["user"], [r["role"] for r in u["roles"]])

admin_client.close()
print("\n账号创建完成。下一步请用 --auth 重启 mongod 后运行 05b_auth_verify.py")
