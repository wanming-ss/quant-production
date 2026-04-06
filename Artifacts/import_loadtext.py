#!/usr/bin/env python3
"""
DolphinDB 导入 - 使用 loadText + append!
通过 Python 调用 DolphinDB 脚本
"""
import dolphindb as ddb
import pandas as pd

CSV_PATH = "E:/Quant_Production/Inbox/tushare_2016_2025.csv"

print("="*70)
print("DolphinDB 导入 (loadText + append!)")
print("="*70)

# 连接
print("\n🔌 连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("✅ 连接成功")

# 使用脚本方式导入
print(f"\n📊 导入 CSV: {CSV_PATH}")

script = f"""
// 1. 加载 CSV
csvPath = "{CSV_PATH}"
t = loadText(csvPath)

// 2. 查看列名和类型
// print("列名: " + string(columnNames(t)))
// print("类型: " + string(columnTypes(t)))

// 3. 直接使用（date 列已是 DATE 类型）
// 如果需要转换: t = select symbol, date(date) as date, ... from t

// 4. 创建数据库
if(!existsDatabase("dfs://tushare")){{
    db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
}} else {{
    db = database("dfs://tushare")
}}

// 5. 创建表
if(!existsTable("dfs://tushare", "daily")){{
    schema = table(1:0, `symbol`date`open`high`low`close`pre_close`change`pct_chg`volume`amount,
                   [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    daily = db.createPartitionedTable(schema, `daily, `date)
}} else {{
    daily = loadTable("dfs://tushare", "daily")
}}

// 6. 导入
append!(daily, t)

// 7. 返回统计
select count(*) as total_records from daily
"""

try:
    result = session.run(script)
    print(f"✅ 导入成功!")
    print(f"📈 表中总记录: {result}")
    
    # 验证
    sample = session.run('select top 5 * from loadTable("dfs://tushare", "daily")')
    print(f"\n样例数据:")
    print(sample)
    
    stats = session.run('select symbol, count(*) as cnt from loadTable("dfs://tushare", "daily") group by symbol order by cnt desc limit 10')
    print(f"\n数据量 Top 10:")
    print(stats)
    
except Exception as e:
    print(f"❌ 导入失败: {e}")

print("\n" + "="*70)
