# -*- coding: utf-8 -*-
"""
第二题初始化脚本（可独立运行）。
连接个人数据库 exam_12403030119，清空并重建 inventory、orders 两个集合。
注意：本脚本只负责初始化；各测试场景的独立重置在 main.py 内完成，
     业务代码不得重复调用本脚本。
"""

from pymongo import MongoClient

# ===== 连接常量（可按真机环境修改）=====
HOST = "localhost"
PORT = 27017
DB_NAME = "exam_12403030119"

# 个人学号参数
SID = "12403030119"
BOOK_ID = "BOOK-" + SID

# Stock = 5 + C = 9
STOCK = 9


def main():
    client = MongoClient(HOST, PORT)
    db = client[DB_NAME]

    db.inventory.delete_many({})
    db.orders.delete_many({})

    db.inventory.insert_one({
        "_id": BOOK_ID,
        "title": "NoSQL数据库教材",
        "stock": STOCK,
    })

    print("初始化完成：")
    print("inventory 文档数 =", db.inventory.count_documents({}))
    print("orders 文档数   =", db.orders.count_documents({}))
    print("初始库存 =", db.inventory.find_one({"_id": BOOK_ID})["stock"])
    client.close()


if __name__ == "__main__":
    main()
