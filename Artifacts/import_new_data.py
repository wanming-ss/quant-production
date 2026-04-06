#!/usr/bin/env python3
"""
导入新增数据到 DolphinDB
从已有 197万 导入到 394万
"""
import dolphindb as ddb
import pandas as pd

CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
BATCH_SIZE = 100000

print("="*70)
print("导入新增数据到 DolphinDB")
print("="*70)

# 1. 连接 DolphinDB
print("\n1️⃣  连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 2. 获取当前 DolphinDB 记录数
current = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
current_count = current.values[0][0]
print(f"   DolphinDB 当前: {current_count:,} 条")

# 3. 读取 CSV 从 current_count 行开始
print(f"\n2️⃣  读取 CSV（从第 {current_count+1:,} 行开始）...")

# 跳过已导入的行，读取剩余部分
skip_rows = current_count + 1  # +1 for header
df = pd.read_csv(CSV_PATH, skiprows=range(1, skip_rows))
df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'volume', 'amount']

new_records = len(df)
print(f"   新记录: {new_records:,} 条")
print(f"   新股票: {df['symbol'].nunique()}")

if new_records == 0:
    print("\n✅ 无新增数据需要导入")
    exit(0)

# 4. 分批导入
print(f"\n3️⃣  分批导入（每批 {BATCH_SIZE:,} 条）...")

total = len(df)
for i in range(0, total, BATCH_SIZE):
    batch = df.iloc[i:i+BATCH_SIZE]
    temp_csv = f"E:/Quant_Production/Inbox/temp_new_{i//BATCH_SIZE}.csv"
    batch.to_csv(temp_csv, index=False)
    
    script = f"""
    t = loadText("{temp_csv}")
    t = select symbol, date, open, high, low, close, pre_close, change, pct_chg, volume, amount from t
    daily = loadTable("dfs://tushare", "daily")
    append!(daily, t)
    """
    
    try:
        session.run(script)
        print(f"   ✅ {i+1:,}-{min(i+BATCH_SIZE, total):,}")
    except Exception as e:
        print(f"   ❌ 失败: {str(e)[:80]}")

# 5. 验证
print("\n4️⃣  验证...")
final_count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
print(f"   导入前: {current_count:,} 条")
print(f"   导入后: {final_count.values[0][0]:,} 条")
print(f"   新增: {final_count.values[0][0] - current_count:,} 条")

print("\n" + "="*70)
print("✅ 新增数据导入完成！")
print("="*70)
