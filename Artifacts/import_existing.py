#!/usr/bin/env python3
"""
DolphinDB 导入 - 已有 CSV（197万条，900只）
一次性导入
"""
import dolphindb as ddb
import pandas as pd

CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"

print("="*70)
print("DolphinDB 导入（已有数据）")
print("="*70)

# 1. 读取 CSV 统计
print("\n1️⃣  读取 CSV...")
df = pd.read_csv(CSV_PATH)
print(f"   记录数: {len(df):,}")
print(f"   股票数: {df['symbol'].nunique()}")
print(f"   日期范围: {df['date'].min()} ~ {df['date'].max()}")
print(f"   列: {list(df.columns)}")

# 2. 连接 DolphinDB
print("\n2️⃣  连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("   ✅ 连接成功")

# 3. 清空并重建表
print("\n3️⃣  准备表结构...")
script = """
// 创建数据库
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare")
}

// 删除旧表（如果存在）
if(existsTable("dfs://tushare", "daily")){
    dropTable(db, `daily)
}

// 创建新表
schema = table(1:0, `symbol`date`open`high`low`close`pre_close`change`pct_chg`volume`amount,
               [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
daily = db.createPartitionedTable(schema, `daily, `date)
"""

session.run(script)
print("   ✅ 表创建成功")

# 4. 使用 loadText 导入
print("\n4️⃣  导入数据（使用 loadText）...")
import_script = f"""
csvPath = "{CSV_PATH}"
t = loadText(csvPath)

// 选择需要的列
t = select symbol, date, open, high, low, close, pre_close, change, pct_chg, volume, amount from t

// 导入
daily = loadTable("dfs://tushare", "daily")
append!(daily, t)

// 返回统计
select count(*) as total from daily
"""

result = session.run(import_script)
print(f"   ✅ 导入完成！")
print(f"   📈 表中总记录: {result}")

# 5. 验证
print("\n5️⃣  验证数据...")
verify = session.run("""
    daily = loadTable("dfs://tushare", "daily")
    select 
        count(*) as total_records,
        count(distinct symbol) as stock_count,
        min(date) as start_date,
        max(date) as end_date
    from daily
""")
print(verify)

print("\n6️⃣  样例数据:")
sample = session.run('select top 5 * from loadTable("dfs://tushare", "daily")')
print(sample)

print("\n" + "="*70)
print("✅ 导入完成！")
print("="*70)
