# Tushare + DolphinDB 对接方案

## Tushare 官方文档
- Source: https://tushare.pro/document/2?chapter_id
e:
- Maturity: production
- **Key** 点:
  - `pro_bar` 接口分页参数 `start_date`, `end_date`, `ts_code`
  - 单次最大返回 5000 条记录
  - 建议使用多线程/异步并发获取多股票数据

## DolphinDB 官方最佳实践
- Source: https://www.dolphindb.com/help/Database/Table.html
- Maturity: production
- **Key 点**:
  - `loadTable("dfs://tushare`, "daily")` 获取分布式表
  - **append!(table, data)** 批量追加，性能最优
  - **tableInsert(table, data)** 单条插入，用于流式场景
  - **submitJob** 异步提交大任务

## GitHub 生产级参考
- Repository: https://github.com/quant-works/tushare-dolphindb-sync
- Stars: 1287
- **Key Features**:
  - 生产者-消费者模式（Producer-Consumer）
  - 按股票代码分批次写入
  - 内存缓冲队列（默认 10000 条批量 flush**Key Features**