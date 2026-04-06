#!/usr/bin/env python3
"""
导入最新数据到 DolphinDB
"""
import dolphindb as ddb
import pandas as pd

print("="*70)
print("导入最新数据到 DolphinDB")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 导入周线
print("\n1️⃣  周线数据...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_weekly.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df.to_csv("E:/Quant_Production/Inbox/temp_weekly.csv", index=False)

script = """
if(!existsDatabase("dfs://tushare_weekly")){
    db = database("dfs://tushare_weekly", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare_weekly")
}
if(existsTable("dfs://tushare_weekly", "weekly")){
    dropTable(db, `weekly)
}
t = loadText("E:/Quant_Production/Inbox/temp_weekly.csv")
weekly = db.createPartitionedTable(t, `weekly, `date)
append!(weekly, t)
select count(*) from weekly
"""
result = session.run(script)
print(f"   ✅ 周线: {result.values[0][0]:,} 条")

# 导入月线
print("\n2️⃣  月线数据...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_monthly.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df.to_csv("E:/Quant_Production/Inbox/temp_monthly.csv", index=False)

script = """
if(!existsDatabase("dfs://tushare_monthly")){
    db = database("dfs://tushare_monthly", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare_monthly")
}
if(existsTable("dfs://tushare_monthly", "monthly")){
    dropTable(db, `monthly)
}
t = loadText("E:/Quant_Production/Inbox/temp_monthly.csv")
monthly = db.createPartitionedTable(t, `monthly, `date)
append!(monthly, t)
select count(*) from monthly
"""
result = session.run(script)
print(f"   ✅ 月线: {result.values[0][0]:,} 条")

# 导入复权因子
print("\n3️⃣  复权因子...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_adj_factor.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df.to_csv("E:/Quant_Production/Inbox/temp_adj.csv", index=False)

script = """
if(!existsDatabase("dfs://tushare_adj")){
    db = database("dfs://tushare_adj", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare_adj")
}
if(existsTable("dfs://tushare_adj", "adj_factor")){
    dropTable(db, `adj_factor)
}
t = loadText("E:/Quant_Production/Inbox/temp_adj.csv")
adj = db.createPartitionedTable(t, `adj_factor, `date)
append!(adj, t)
select count(*) from adj_factor
"""
result = session.run(script)
print(f"   ✅ 复权因子: {result.values[0][0]:,} 条")

print("\n" + "="*70)
print("✅ 最新数据导入完成！")
print("="*70)

print("\n📊 DolphinDB 数据库:")
print("   - dfs://tushare (日线): 8,840,324 条")
print("   - dfs://tushare_weekly (周线)")
print("   - dfs://tushare_monthly (月线)")
print("   - dfs://tushare_adj (复权因子)")
