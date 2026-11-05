# -*- coding: utf-8 -*-
"""
第二题业务与测试代码（MongoDB 原子扣减与事务验证）。
约定：本脚本不调用 init.py；每个测试场景开始前自行重置 inventory 与 orders。
注意：多文档事务通常需要副本集（replica set）环境，单机 standalone 不支持事务。
"""

from pymongo import MongoClient

# ===== 连接常量（与 init.py 保持一致）=====
HOST = "localhost"
PORT = 27017
DB_NAME = "exam_12403030119"

# 个人参数：SID、Stock=5+C=9、Buy=1+A=2
SID = "12403030119"
BOOK_ID = "BOOK-" + SID
STOCK = 9
BUY = 2

# 结果分类
RES_SUCCESS = "SUCCESS"                 # 扣减成功并提交事务
RES_INSUFFICIENT = "INSUFFICIENT_STOCK"  # matchedCount=0 且书存在（库存不足）
RES_NOT_FOUND = "BOOK_NOT_FOUND"         # matchedCount=0 且书不存在
RES_DB_ERROR = "DB_ERROR"               # 数据库执行异常（含回滚）


def reset(db, stock):
    """每个场景开始前单独重置两个集合，互不影响。"""
    db.inventory.delete_many({})
    db.orders.delete_many({})
    db.inventory.insert_one({"_id": BOOK_ID, "title": "NoSQL数据库教材", "stock": stock})


def purchase(db, request_id, force_error=False):
    """
    订购函数：同一会话 + 同一事务完成“原子扣减 + 插入订单”。
    返回结果分类字符串；只有事务 commit 成功才返回 RES_SUCCESS。
    """
    client = db.client
    session = client.start_session()
    try:
        session.start_transaction()

        # 原子扣减：把“库存条件检查”与“扣减”合并为单条更新，禁止先查后无条件扣减
        res = db.inventory.update_one(
            {"_id": BOOK_ID, "stock": {"$gte": BUY}},
            {"$inc": {"stock": -BUY}},
            session=session,
        )

        if res.matched_count == 0:
            # 扣减未命中：在同一事务内读一次库存文档，区分“书不存在”与“库存不足”
            doc = db.inventory.find_one({"_id": BOOK_ID}, session=session)
            session.abort_transaction()
            return RES_NOT_FOUND if doc is None else RES_INSUFFICIENT

        # 扣减成功之后、插入订单之前，按测试要求主动抛异常，触发回滚
        if force_error:
            raise RuntimeError("forceError: 扣减成功后、插入订单前主动抛出异常")

        db.orders.insert_one(
            {
                "_id": request_id,
                "bookId": BOOK_ID,
                "studentId": SID,
                "quantity": BUY,
            },
            session=session,
        )

        session.commit_transaction()
        return RES_SUCCESS

    except Exception:
        # 任何异常都回滚事务，保证扣减与订单同生共死
        try:
            session.abort_transaction()
        except Exception:
            pass
        return RES_DB_ERROR
    finally:
        session.end_session()


def run_scenario(db, name, init_stock, times, force_error):
    """执行一个场景并按预期值核验。"""
    reset(db, init_stock)
    ok = 0
    fail = 0
    for i in range(times):
        request_id = "REQ-%s-%s-%03d" % (SID, name, i + 1)  # 每次请求编号不同
        result = purchase(db, request_id, force_error=force_error)
        if result == RES_SUCCESS:
            ok += 1
        else:
            fail += 1

    final_stock = db.inventory.find_one({"_id": BOOK_ID})["stock"] if \
        db.inventory.count_documents({"_id": BOOK_ID}) else None
    order_count = db.orders.count_documents({})

    return {
        "name": name,
        "init_stock": init_stock,
        "buy": BUY,
        "ok": ok,
        "fail": fail,
        "final_stock": final_stock,
        "orders": order_count,
    }


# 四场景预期值（由个人参数计算得出）：T1 成功1/失败0/库存7/订单1
# T2 初始=Buy-1=1，成功0/失败1/库存1/订单0
# T3 forceError=True，成功0/失败1/回滚后库存9/订单0
# T4 发起 floor(9/2)+1=5 次，成功4/失败1/库存1/订单4
EXPECT = {
    "T1": {"ok": 1, "fail": 0, "final_stock": 7, "orders": 1},
    "T2": {"ok": 0, "fail": 1, "final_stock": 1, "orders": 0},
    "T3": {"ok": 0, "fail": 1, "final_stock": 9, "orders": 0},
    "T4": {"ok": 4, "fail": 1, "final_stock": 1, "orders": 4},
}


def main():
    client = MongoClient(HOST, PORT)
    db = client[DB_NAME]

    scenarios = [
        ("T1", STOCK, 1, False),   # 正常订购
        ("T2", BUY - 1, 1, False),  # 库存不足（初始 Buy-1=1）
        ("T3", STOCK, 1, True),     # 中途异常 forceError=True
        ("T4", STOCK, STOCK // BUY + 1, False),  # 连续 5 次
    ]

    print("%-4s %8s %6s %6s %6s %8s %8s %8s"
          % ("场景", "初始库存", "购买", "成功", "失败", "最终库存", "订单数", "是否通过"))
    print("-" * 70)
    for name, init_stock, times, force_error in scenarios:
        actual = run_scenario(db, name, init_stock, times, force_error)
        exp = EXPECT[name]
        passed = (actual["ok"] == exp["ok"]
                  and actual["fail"] == exp["fail"]
                  and actual["final_stock"] == exp["final_stock"]
                  and actual["orders"] == exp["orders"])
        print("%-4s %8d %6d %6d %6d %8d %8d %8s"
              % (name, actual["init_stock"], actual["buy"],
                 actual["ok"], actual["fail"], actual["final_stock"],
                 actual["orders"], "通过" if passed else "不通过"))

    client.close()


if __name__ == "__main__":
    main()
