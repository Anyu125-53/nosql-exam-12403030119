# -*- coding: utf-8 -*-
"""
第一题业务操作代码。
约定：本脚本不调用 init，不重置数据；可重复执行（第(3)步使用 $addToSet 天然幂等）。
运行前请先执行一次 init.py 完成初始化。
"""

from pymongo import MongoClient

# ===== 连接常量（与 init.py 保持一致）=====
HOST = "localhost"
PORT = 27017
DB_NAME = "exam_12403030119"

SID = "12403030119"
COURSE_01 = "COURSE-" + SID + "-01"

# 个人参数：S=19，A=1
S = 19
A = 1
NEW_CH02_TITLE = "Redis基础与应用-" + str(S)
NEW_CH03 = {"chapterId": "CH03", "title": "Redis高级操作", "hours": 2 + A}


def step1_query_open_courses(db):
    print("=" * 60)
    print("(1) 查询 teacher=张老师 且 status=OPEN 的课程")
    # 章节数量用聚合表达式 $size 在投影中计算，不写死
    cursor = db.courses.find(
        {"teacher": "张老师", "status": "OPEN"},
        {
            "_id": 1,
            "title": 1,
            "chapterCount": {"$size": "$chapters"},
        },
    )
    for doc in cursor:
        print("课程编号：%s" % doc["_id"])
        print("课程名称：%s" % doc["title"])
        print("章节数量：%d" % doc["chapterCount"])
        print("-" * 40)


def step2_update_ch02_title(db):
    print("=" * 60)
    print("(2) 局部更新第01门课 CH02 章节标题为：%s" % NEW_CH02_TITLE)
    # $set + arrayFilters 精确定位 chapters 数组中 chapterId=CH02 的元素
    res = db.courses.update_one(
        {"_id": COURSE_01},
        {"$set": {"chapters.$[elem].title": NEW_CH02_TITLE}},
        array_filters=[{"elem.chapterId": "CH02"}],
    )
    print("matchedCount = %d" % res.matched_count)
    print("modifiedCount = %d" % res.modified_count)
    print("更新后的完整课程文档：")
    print(db.courses.find_one({"_id": COURSE_01}))


def step3_add_ch03_twice(db):
    print("=" * 60)
    print("(3) 连续两次用 $addToSet 增加 CH03 章节：%s" % NEW_CH03)
    for i in (1, 2):
        res = db.courses.update_one(
            {"_id": COURSE_01},
            {"$addToSet": {"chapters": NEW_CH03}},
        )
        print("第%d次新增：matchedCount=%d, modifiedCount=%d"
              % (i, res.matched_count, res.modified_count))


def step4_verify(db):
    print("=" * 60)
    print("(4) 核验结果")
    doc = db.courses.find_one({"_id": COURSE_01})

    ch02 = [c for c in doc["chapters"] if c["chapterId"] == "CH02"]
    ch03_list = [c for c in doc["chapters"] if c["chapterId"] == "CH03"]
    print("修改后 CH02 的标题：%s" % (ch02[0]["title"] if ch02 else "未找到"))
    print("两次新增后 CH03 的数量：%d" % len(ch03_list))
    print("最终章节总数：%d" % len(doc["chapters"]))
    print("teacher 是否保持原值：%s（当前值=%s）"
          % (doc["teacher"] == "张老师", doc["teacher"]))
    print("status 是否保持原值：%s（当前值=%s）"
          % (doc["status"] == "OPEN", doc["status"]))

    print("-" * 60)
    print("书面回答：为什么本题适合局部更新，而不宜直接替换整个课程文档？")
    print("1) 本题只需要改动 chapters 数组中的某个元素（CH02 标题）或向数组尾部")
    print("   追加一个元素（CH03），其余字段（teacher/status/其他章节）均不能受影响。")
    print("2) 若读出整文档、在客户端拼接后 replace 整个文档：")
    print("   - 需要把 teacher、status、全部其他章节原样回写，代码繁琐且易出错；")
    print("   - 读与写之间存在时间窗，并发下会覆盖他人修改，丢失更新；")
    print("   - 传输与写入的数据量大，浪费资源。")
    print("3) 使用 $set（配合 arrayFilters）与 $addToSet 这类局部更新操作：")
    print("   - 只在服务端修改目标字段，天然保留其他字段，语义精确；")
    print("   - 单次原子操作，无需读出再写回，避免并发覆盖；")
    print("   - $addToSet 还自带按整个元素去重的能力，正好满足"
          "“连续执行两次 CH03 只出现一次”的要求。")


def main():
    client = MongoClient(HOST, PORT)
    db = client[DB_NAME]
    step1_query_open_courses(db)
    step2_update_ch02_title(db)
    step3_add_ch03_twice(db)
    step4_verify(db)
    client.close()


if __name__ == "__main__":
    main()
