import time
import math
import redis

HOST = "localhost"
PORT = 6379
SID = "12403030119"
PREFIX = f"exam:{SID}:"
N = 1419
Q = 100


def conn():
    return redis.Redis(host=HOST, port=PORT, decode_responses=True)


def write_sequential(r):
    key_prefix = PREFIX + "seq:"
    r.delete(*[key_prefix + str(i) for i in range(1, N + 1)])

    t0 = time.perf_counter()
    for i in range(1, N + 1):
        r.set(key_prefix + str(i), f"value-{SID}-{i}")
    t1 = time.perf_counter()
    return (t1 - t0) * 1000


def write_pipeline(r):
    key_prefix = PREFIX + "pipe:"
    pipe = r.pipeline(transaction=False)
    for i in range(1, N + 1):
        pipe.delete(key_prefix + str(i))
    pipe.execute()

    t0 = time.perf_counter()
    batches = math.ceil(N / Q)
    for b in range(batches):
        start = b * Q + 1
        end = min(start + Q - 1, N)
        p = r.pipeline(transaction=False)
        for i in range(start, end + 1):
            p.set(key_prefix + str(i), f"value-{SID}-{i}")
        p.execute()
    t1 = time.perf_counter()
    return (t1 - t0) * 1000


def verify(r):
    seq_prefix = PREFIX + "seq:"
    pipe_prefix = PREFIX + "pipe:"

    p = r.pipeline(transaction=False)
    for i in range(1, N + 1):
        p.exists(seq_prefix + str(i))
        p.exists(pipe_prefix + str(i))
    results = p.execute()
    seq_count = sum(results[0::2])
    pipe_count = sum(results[1::2])

    print(f"  seq key 数量: {seq_count} (预期 {N})")
    print(f"  pipe key 数量: {pipe_count} (预期 {N})")

    samples = [1, 100, N]
    p2 = r.pipeline(transaction=False)
    for i in samples:
        p2.get(seq_prefix + str(i))
        p2.get(pipe_prefix + str(i))
    svs = p2.execute()
    for idx, i in enumerate(samples):
        sv = svs[idx * 2]
        pv = svs[idx * 2 + 1]
        expect = f"value-{SID}-{i}"
        ok = sv == expect and pv == expect
        print(f"  第{i}条: seq={sv}  pipe={pv}  预期={expect}  一致={ok}")


def main():
    r = conn()
    print(f"命令总数 N = {N}")
    print(f"Pipeline 批次数 = ceil({N}/{Q}) = {math.ceil(N / Q)}")
    print(f"最后一批数量 = {N - (math.ceil(N / Q) - 1) * Q}")
    print()

    t_seq = write_sequential(r)
    print(f"方案甲(逐条 SET) 耗时: {t_seq:.2f} ms")

    t_pipe = write_pipeline(r)
    print(f"方案乙(Pipeline) 耗时: {t_pipe:.2f} ms")
    print()

    print("数据完整核验:")
    verify(r)
    print()

    if t_pipe < t_seq:
        speedup = t_seq / t_pipe
        print(f"结论: Pipeline 更快, 约 {speedup:.2f}x。")
    else:
        print("结论: Pipeline 未明显快于逐条写入。")
    print("可能原因分析:")
    print("  1. 本地/同机网络开销极小, RTT 优势被稀释;")
    print("  2. 每条 SET 命令体积极小, 单条本身就快;")
    print("  3. 批大小 Q=100 可能不是最优, 过大或过小都影响吞吐;")
    print("  4. redis-py 客户端序列化/缓冲开销在小命令下占比相对高;")
    print("  5. 系统抖动 (CPU、调度) 影响短耗时测量精度。")


if __name__ == "__main__":
    main()
