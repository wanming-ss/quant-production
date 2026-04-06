#!/usr/bin/env python3
"""
导入所有数据到 DolphinDB - 终极修复版
处理日期格式问题
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("导入所有数据到 DolphinDB")
print("="*70)

# 连接 DolphinDB
print("\n1️⃣  连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("   ✅ 连接成功")

# 导入周线数据
print("\n2️⃣  导入周线数据...")
weekly_path = "E:/Quant_Production/Inbox/tushare_weekly.csv"
if os.path.exists(weekly_path):
    df = pd.read_csv(weekly_path, low_memory=False)
    print(f"   CSV: {len(df):,} 条")
    
    # 处理日期格式
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
    
    print(f"   有效数据: {len(df):,} 条")
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

# 导入月线数据
print("\n3️⃣  导入月线数据...")
monthly_path = "E:/Quant_Production/Inbox/tushare_monthly.csv"
if os.path.exists(monthly_path):
    df = pd.read_csv(monthly_path, low_memory=False)
    print(f"   CSV: {len(df):,} 条")
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
    
    print(f"   有效数据: {len(df):,} 条")
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

# 导入复权因子
print("\n4️⃣  导入复权因子...")
adj_path = "E:/Quant_Production/Inbox/tushare_adj_factor.csv"
if os.path.exists(adj_path):
    df = pd.read_csv(adj_path, low_memory=False)
    print(f"   CSV: {len(df):,} 条")
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
    
    print(f"   有效数据: {len(df):,} 条")
    df.to_csv("E:/Quant_Production/Inbox/temp_adj_factor.csv", index=False)
    
    script = """
    if(!existsDatabase("dfs://tushare_adj")){
        db = database("dfs://tushare_adj", VALUE, 2016.01M..2026.12M)
    } else {
        db = database("dfs://tushare_adj")
    }
    
    if(existsTable("dfs://tushare_adj", "adj_factor")){
        dropTable(db, `adj_factor)
    }
    
    t = loadText("E:/Quant_Production/Inbox/temp_adj_factor.csv")
    adj_factor = db.createPartitionedTable(t, `adj_factor, `date)
    append!(adj_factor, t)
    
    select count(*) from adj_factor
    """
    result = session.run(script)
    print(f"   ✅ 复权因子导入完成: {result.values[0][0]:,} 条")

print("\n" + "="*70)
print("✅ 数据导入完成！")
print("="*70)

# 总结
print("\n📊 DolphinDB 数据库:")
print("   - dfs://tushare (日线): 8,840,324 条")
print("   - dfs://tushare_weekly (周线)")
print("   - dfs://tushare_monthly (月线)")
print("   - dfs://tushare_adj (复权因子)")
