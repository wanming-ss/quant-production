#!/usr/bin/env python3
"""
导入所有完成数据到 DolphinDB
跳过损坏数据
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("导入所有完成数据到 DolphinDB")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 1. 日线数据（已完成）
print("\n1️⃣  日线数据...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_all_2016_2025.csv", usecols=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
df['date'] = pd.to_datetime(df['date'])
df.to_csv("E:/Quant_Production/Inbox/temp_daily.csv", index=False)
print(f"   CSV: {len(df):,} 条")

# 分批导入（避免内存问题）
batch_size = 500000
total = len(df)
batches = (total // batch_size) + 1

print(f"   分批导入（{batches} 批，每批 {batch_size:,} 条）...")

for i in range(batches):
    start = i * batch_size
    end = min((i + 1) * batch_size, total)
    batch = df.iloc[start:end]
    batch.to_csv("E:/Quant_Production/Inbox/temp_batch.csv", index=False)
    
    script = f"""
    t = loadText("E:/Quant_Production/Inbox/temp_batch.csv")
    if(!existsDatabase("dfs://tushare")){{
        db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
    }} else {{
        db = database("dfs://tushare")
    }}
    if(!existsTable("dfs://tushare", "daily")){{
        daily = db.createPartitionedTable(t, `daily, `date)
    }}
    daily = loadTable("dfs://tushare", "daily")
    append!(daily, t)
    """
    session.run(script)
    print(f"   ✅ 批次 {i+1}/{batches}: {len(batch):,} 条")

result = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
print(f"   ✅ 日线总计: {result.values[0][0]:,} 条")

print("\n" + "="*70)
print("✅ 数据导入完成！")
print("="*70)

print("\n📊 DolphinDB 数据库:")
print("   - dfs://tushare/daily (日线)")
