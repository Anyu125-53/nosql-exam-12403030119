# NoSQL 数据库上机测验 — 源代码与报告

- 姓名：吴湘渝　学号：12403030119　班级：本人班级（占位）
- 实验名称：《NoSQL数据库》上机测验
- 个人参数：S=19，A=1，B=3，C=4；Stock=9，Buy=2，本人成绩=74；N=1419，Q=100

## 目录结构

| 目录 | 内容 |
|---|---|
| task1/ | MongoDB 课程信息查询与维护（init.py 初始化，main.py 业务操作） |
| task2/ | MongoDB 原子扣减与事务验证（四场景 T1~T4） |
| task3/ | Redis 学生信息 Hash / 章节 Set / 排行榜 ZSet / 会话 String |
| task4/ | 选做题：逐条写入 vs Pipeline 分批写入性能对比 |
| result.txt / 说明.md | 各题预期结果、选型与运行说明 |

## 运行环境

- Python 3.8+；依赖：`pymongo`、`redis`（`pip install pymongo redis`）
- MongoDB：localhost:27017，库 `exam_12403030119`；Redis：localhost:6379，键前缀 `exam:12403030119:`
- 源码不含任何账号、密码等凭据；连接常量在各脚本顶部 HOST、PORT 中修改

## 运行方法

```bash
python3 task1/init.py && python3 task1/main.py
python3 task2/init.py && python3 task2/main.py
python3 task3/main.py
python3 task4/main.py
```

## 实测说明

- task1、task3 已在本人本机核验通过；task2 四场景中 T1/T2/T4 通过，T3 因本机为单机 standalone（不支持多文档事务回滚）未回滚，副本集环境下预期库存恢复 9、订单 0。
- result.txt 中耗时/结果项为预期值，真机运行截图补入实验报告 docx；报告 docx 提交至学习通。
