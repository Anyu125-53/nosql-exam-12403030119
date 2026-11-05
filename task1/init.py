# -*- coding: utf-8 -*-
"""
第一题初始化脚本（可独立运行）。
连接个人数据库 exam_12403030119，清空并重建 courses 集合。
注意：本脚本只负责初始化，业务操作请在 main.py 中完成，不要在业务代码里再次调用本脚本。
"""

from pymongo import MongoClient

# ===== 连接常量（可按真机环境修改）=====
HOST = "localhost"
PORT = 27017
DB_NAME = "exam_12403030119"

# 个人学号参数
SID = "12403030119"

COURSE_01 = "COURSE-" + SID + "-01"
COURSE_02 = "COURSE-" + SID + "-02"
COURSE_03 = "COURSE-" + SID + "-03"


def main():
    client = MongoClient(HOST, PORT)
    db = client[DB_NAME]

    courses = [
        {
            "_id": COURSE_01,
            "title": "NoSQL数据库",
            "teacher": "张老师",
            "status": "OPEN",
            "chapters": [
                {"chapterId": "CH01", "title": "MongoDB基础", "hours": 2},
                {"chapterId": "CH02", "title": "Redis基础", "hours": 2},
            ],
        },
        {
            "_id": COURSE_02,
            "title": "数据库原理",
            "teacher": "张老师",
            "status": "CLOSED",
            "chapters": [
                {"chapterId": "CH01", "title": "关系模型", "hours": 2},
            ],
        },
        {
            "_id": COURSE_03,
            "title": "机器学习",
            "teacher": "李老师",
            "status": "OPEN",
            "chapters": [
                {"chapterId": "CH01", "title": "分类", "hours": 2},
                {"chapterId": "CH02", "title": "聚类", "hours": 2},
            ],
        },
    ]

    # 先清空再插入，保证初始化结果可重复
    db.courses.delete_many({})
    db.courses.insert_many(courses)

    print("初始化完成，courses 集合现有文档数：", db.courses.count_documents({}))
    client.close()


if __name__ == "__main__":
    main()
