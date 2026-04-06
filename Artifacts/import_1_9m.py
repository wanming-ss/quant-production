#!/usr/bin/env python3
"""
导入新增数据到 DolphinDB
从 394万 导入到 587万
"""
import dolphindb as ddb
import pandas as pd

CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
BATCH_SIZE = 100000

print("="*70)
print("导入新增数据到 DolphinDB (193万条)")
print("="*70)

# 1. 连接 DolphinDB
print("\n1️⃣  连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 2. 获取当前 DolphinDB 记录数
current = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
current_count = current.values[0][0]
print(f"   DolphinDB 当前: {current_count:,} 条")

# 3. 获取 CSV 总行数
print(f"\n2️⃣  读取 CSV 总行数...")
df_total = pd.read_csv(CSV_PATH, usecols=[0])  # 只读第一列，加快速度
csv_total = len(df_total)
print(f"   CSV 总行数: {csv_total:,} 条")

new_records = csv_total - current_count
print(f"   需要导入: {new_records:,} 条")

if new_records <= 0:
    print("\n✅ 无新增数据需要导入")
    exit(0)

# 4. 分批读取并导入
print(f"\n3️⃣  分批导入（每批 {BATCH_SIZE:,} 条）...")

batches = (new_records // BATCH_SIZE) + 1
for batch_num in range(batches):
    start_row = current_count + batch_num * BATCH_SIZE
    end_row = min(start_row + BATCH_SIZE, csv_total)
    
    if start_row >= csv_total:
        break
    
    print(f"\n   批次 {batch_num + 1}/{batches}: {start_row:,}-{end_row:,}")
    
    # 读取指定范围（跳过已导入的，+1 是 header）
    skip = start_row + 1
    nrows = end_row - start_row
    
    batch_df = pd.read_csv(CSV_PATH, skiprows=range(1, skip), nrows=nrows)
    batch_df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'volume', 'amount']
    
    # 保存临时文件
    temp_csv = f"E:/Quant_Production/Inbox/temp_batch_{batch_num}.csv"
    batch_df.to_csv(temp_csv, index=False)
    
    # 导入 DolphinDB
    script = f"""
    t = loadText("{temp_csv}")
    t = select symbol, date, open, high, low, close, pre_close, change, pct_chg, volume, amount from t
    daily = loadTable("dfs://tushare", "daily")
    append!(daily, t)
    """
    
    try:
        session.run(script)
        print(f"   ✅ 完成 {len(batch_df):,} 条")
    except Exception as e:
        print(f"   ❌ 失败: {str(e)[:100]}")

# 5. 验证
print("\n4️⃣  验证...")
final_count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
actual_imported = final_count.values[0][0] - current_count
print(f"   导入前: {current_count:,} 条")
print(f"   导入后: {final_count.values[0][0]:,} 条")
print(f"   实际新增: {actual_imported:,} 条")
print(f"   预期新增: {new_records:,} 条")

print("\n" + "="*70)
print("✅ 新增数据导入完成！")
print("="*70)
