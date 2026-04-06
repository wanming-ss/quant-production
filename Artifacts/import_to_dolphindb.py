#!/usr/bin/env python3
"""
导入已完成数据到 DolphinDB
分批导入避免内存问题
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("导入已完成数据到 DolphinDB")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 1. 导入日线数据
print("\n1️⃣  日线数据 (tushare_all_2016_2025.csv)...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_all_2016_2025.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

df.to_csv("E:/Quant_Production/Inbox/temp_daily.csv", index=False)

script = """
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare")
}

if(existsTable("dfs://tushare", "daily")){
    dropTable(db, `daily)
}

t = loadText("E:/Quant_Production/Inbox/temp_daily.csv")
daily = db.createPartitionedTable(t, `daily, `date)
append!(daily, t)

select count(*) from daily
"""
result = session.run(script)
print(f"   ✅ 日线导入完成: {result.values[0][0]:,} 条")

# 2. 导入周线数据
print("\n2️⃣  周线数据 (tushare_weekly.csv)...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_weekly.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")

if 'date' in df.columns:
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
print(f"   ✅ 周线导入完成: {result.values[0][0]:,} 条")

# 3. 导入月线数据
print("\n3️⃣  月线数据 (tushare_monthly.csv)...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_monthly.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")

if 'date' in df.columns:
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
print(f"   ✅ 月线导入完成: {result.values[0][0]:,} 条")

# 4. 导入复权因子
print("\n4️⃣  复权因子 (tushare_adj_factor.csv)...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_adj_factor.csv", low_memory=False)
print(f"   CSV: {len(df):,} 条")

if 'date' in df.columns:
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
print(f"   ✅ 复权因子导入完成: {result.values[0][0]:,} 条")

# 5. 导入利润表（进行中）
print("\n5️⃣  利润表 (tushare_income.csv)...")
df = pd.read_csv("E:/Quant_Production/Inbox/tushare_income.csv", low_memory=False, on_bad_lines='skip')
print(f"   CSV: {len(df):,} 条")

if 'ann_date' in df.columns or 'f_ann_date' in df.columns:
    date_col = 'ann_date' if 'ann_date' in df.columns else 'f_ann_date'
    df['date'] = pd.to_datetime(df[date_col], errors='coerce', format='%Y%m%d')
    df = df.dropna(subset=['date'])

df.to_csv("E:/Quant_Production/Inbox/temp_income.csv", index=False)

script = """
if(!existsDatabase("dfs://tushare_income")){
    db = database("dfs://tushare_income", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare_income")
}

if(existsTable("dfs://tushare_income", "income")){
    dropTable(db, `income)
}

t = loadText("E:/Quant_Production/Inbox/temp_income.csv")
income = db.createPartitionedTable(t, `income, `date)
append!(income, t)

select count(*) from income
"""
result = session.run(script)
print(f"   ✅ 利润表导入完成: {result.values[0][0]:,} 条")

print("\n" + "="*70)
print("✅ 数据导入完成！")
print("="*70)

print("\n📊 DolphinDB 数据库:")
print("   - dfs://tushare/daily (日线)")
print("   - dfs://tushare_weekly/weekly (周线)")
print("   - dfs://tushare_monthly/monthly (月线)")
print("   - dfs://tushare_adj/adj_factor (复权因子)")
print("   - dfs://tushare_income/income (利润表)")
