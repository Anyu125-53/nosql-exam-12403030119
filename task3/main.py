import time
import redis

HOST = "localhost"
PORT = 6379
SID = "12403030119"
PREFIX = f"exam:{SID}:"

STUDENT_KEY = PREFIX + "student"
DONE_KEY = PREFIX + "done"
RANK_KEY = PREFIX + "rank"
SESSION_KEY = PREFIX + "session"


def conn():
    return redis.Redis(host=HOST, port=PORT, decode_responses=True)


def task_hash(r):
    print("=" * 50)
    print("[子项1] 学生信息 Hash")
    r.delete(STUDENT_KEY)
    r.hset(STUDENT_KEY, mapping={
        "studentId": SID,
        "name": "张三",
        "className": "本人班级",
        "courseId": f"COURSE-{SID}-01",
        "status": "learning",
    })
    print("创建后 status =", r.hget(STUDENT_KEY, "status"))

    r.hset(STUDENT_KEY, "status", "completed")
    print("改为 completed 后:")
    print("  name   =", r.hget(STUDENT_KEY, "name"))
    print("  status =", r.hget(STUDENT_KEY, "status"))
    print("  完整 Hash (hgetall):")
    for k, v in r.hgetall(STUDENT_KEY).items():
        print(f"    {k} = {v}")


def task_set(r):
    print("=" * 50)
    print("[子项2] 已完成章节 Set")
    r.delete(DONE_KEY)
    for ch in ["CH01", "CH02", "CH02", "CH03"]:
        r.sadd(DONE_KEY, ch)
        print(f"  提交 {ch} 后 scard = {r.scard(DONE_KEY)}")
    print("  最终全部成员:", sorted(r.smembers(DONE_KEY)))
    print("  CH02 是否完成:", r.sismember(DONE_KEY, "CH02"))
    print("  CH04 是否完成:", r.sismember(DONE_KEY, "CH04"))
    before = r.scard(DONE_KEY)
    r.sadd(DONE_KEY, "CH02")
    after = r.scard(DONE_KEY)
    print(f"  重复提交 CH02: scard {before} -> {after} (未增加={before == after})")


def task_zset(r):
    print("=" * 50)
    print("[子项3] 成绩排行榜 Sorted Set")
    r.delete(RANK_KEY)
    members = {
        f"Student:{SID}": 74,
        "demo:01": 85,
        "demo:02": 90,
        "demo:03": 60,
        "demo:04": 80,
    }
    r.zadd(RANK_KEY, members)

    print("  加分前 前3名 (zrevrange):")
    for name, score in r.zrevrange(RANK_KEY, 0, 2, withscores=True):
        print(f"    {name} = {int(score)}")

    r.zincrby(RANK_KEY, 20, f"Student:{SID}")

    print("  加分后 前3名 (zrevrange):")
    for name, score in r.zrevrange(RANK_KEY, 0, 2, withscores=True):
        print(f"    {name} = {int(score)}")

    my_score = r.zscore(RANK_KEY, f"Student:{SID}")
    my_rank = r.zrevrank(RANK_KEY, f"Student:{SID}") + 1
    print(f"  本人分数: {int(my_score)}, 名次: 第{my_rank}名")


def task_string(r):
    print("=" * 50)
    print("[子项4] 会话 String 键 (TTL=5s)")
    r.delete(SESSION_KEY)
    session_val = f"session-{SID}-01"
    r.set(SESSION_KEY, session_val, ex=5)
    val = r.get(SESSION_KEY)
    ttl = r.ttl(SESSION_KEY)
    print(f"  创建后: value={val}, ttl={ttl}s")

    print("  等待 6 秒...")
    time.sleep(6)

    exists = r.exists(SESSION_KEY)
    ttl_after = r.ttl(SESSION_KEY)
    print(f"  6秒后: exists={bool(exists)}, ttl={ttl_after}")
    print(f"  过期验证: {'通过 (键已自动过期)' if not exists else '未通过 (键仍存在)'}")


def task_type(r):
    print("=" * 50)
    print("[子项5] 数据类型核验")
    r.set(SESSION_KEY, f"session-{SID}-01", ex=60)
    print(f"  {STUDENT_KEY}      TYPE = {r.type(STUDENT_KEY)}")
    print(f"  {DONE_KEY}      TYPE = {r.type(DONE_KEY)}")
    print(f"  {RANK_KEY}      TYPE = {r.type(RANK_KEY)}")
    print(f"  {SESSION_KEY}  TYPE = {r.type(SESSION_KEY)}")
    print()
    print("  Hash: 学生信息是多字段结构化记录，Hash 可按字段读写，避免整体序列化。")
    print("  Set: 章节完成情况只需去重记录，不关心顺序，Set 天然去重。")
    print("  Sorted Set: 成绩需要按分数排序排行，Sorted Set 自动维护有序分数表。")
    print("  String: 会话标识是单个字符串值，String 最简单且支持 TTL 过期。")


def main():
    r = conn()
    task_hash(r)
    task_set(r)
    task_zset(r)
    task_string(r)
    task_type(r)


if __name__ == "__main__":
    main()
