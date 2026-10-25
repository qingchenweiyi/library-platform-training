# 图书情报检索与统计平台 · 运行说明

## 目录结构

```
library_platform/
├── data/                     # 配套数据集（Extended JSON）
│   ├── books.txt             # 20 本图书
│   ├── readers.txt            # 16 位读者
│   └── borrow_logs.txt        # 借阅流水
├── scripts/                  # 可复现脚本（按编号顺序执行）
│   ├── 01_setup_import.py     # 建库+三种特殊集合+导入数据
│   ├── 02_queries.py          # Q1-Q16 检索 + U1-U4/D1-D3 更新删除
│   ├── 03_aggregation.py       # A1-A9 聚合管道
│   ├── 04_indexes.py         # I1-I5 索引 + 唯一约束 + explain
│   ├── 05a_create_users.py     # S1/S2 创建只读/读写账号
│   ├── 05b_auth_verify.py      # S3 权限验证（需以 --auth 启动）
│   └── 06_export.py           # 导出 category_stats / books
├── app/                      # 任务五 PyMongo 应用（6 个源文件）
│   ├── mongodb_connect.py
│   ├── book_manager.py
│   ├── reader_manager.py
│   ├── borrow_manager.py
│   ├── stat_manager.py
│   └── main.py
├── export/                   # 任务六导出的数据文件
│   ├── books.json
│   └── category_stats.json
└── 技术文档.md
```

## 快速开始

1. 启动 MongoDB（开发模式，不开启认证）：
   ```bash
   mongod --dbpath ./data/db --port 27017
   ```
2. 按顺序执行脚本，建库并导入数据：
   ```bash
   cd scripts
   python3 01_setup_import.py   # 建库+特殊集合+导入（导入后 borrow_logs=66）
   python3 02_queries.py        # Q1-Q16 检索 + U1-U4/D1-D3 更新删除
   python3 03_aggregation.py    # A1-A9 聚合管道
   python3 04_indexes.py        # I1-I5 索引 + 唯一约束 + explain
   ```
3. 运行应用程序：
   ```bash
   cd ../app
   python3 main.py
   ```

> 说明：`borrow_logs` 时间序列集合设置了 5 年 TTL（expireAfterSeconds=157680000）。
> 由于借阅日期分布在 2023—2025 年，在 2026-10 环境下 5 年保留期可完整覆盖全部数据，
> TTL 不会清理任何记录，导入的 66 条流水全部保留。
> 任务三的 D1/D2（删除演示）会删除 1 条已归还 + 13 条逾期，使流水变为 52 条。
> 任务四 A6-A8 按此 52 条流水呈现（见《技术文档》第三节）。

## 权限验证（S3）

```bash
# 先创建账号
python3 05a_create_users.py
# 以 --auth 重启 mongod 后验证
python3 05b_auth_verify.py
```

账号：只读 `libReader / Reader@123`，读写 `libWriter / Writer@123`（authSource=admin）。

> 说明：本实例已实测通过——libReader 可读不可写（code 13），libWriter 可读可写，匿名访问被拒。

## 实测结果摘要

- 集合文档数：books=20，readers=16，borrow_logs=66（5 年 TTL 完整保留；D1/D2 删除演示后剩 52），book_in_stock 视图=19，category_stats=5。
- 检索：Q1=7、Q2=8、Q6=10、Q7=7、Q11=12、Q12=17；完整结果见《技术文档》第三节。
- 聚合：5 个类别分组；计算机类图书最多（7 本）；畅销榜首《活着》243 次；借阅趋势 2023 年 15 次、2024 年 23 次、2025 年 14 次（D1/D2 后 52 条口径）。
- 索引：isbn 唯一索引已验证重复插入被拒；category 查询走 IXSCAN。
