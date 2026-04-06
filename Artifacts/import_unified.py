#!/usr/bin/env python3
"""
导入所有数据到 DolphinDB - 统一数据库
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

# 创建统一数据库
print("\n2️⃣  创建统一数据库...")
db_script = """
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
} else {
    db = database("dfs://tushare")
}
"""
session.run(db_script)
print("   ✅ 数据库准备完成")

# 导入周线数据
print("\n3️⃣  导入周线数据...")
weekly_path = "E:/Quant_Production/Inbox/tushare_weekly.csv"
if os.path.exists(weekly_path):
    df = pd.read_csv(weekly_path)
    print(f"   CSV: {len(df):,} 条")
    df.to_csv("E:/Quant_Production/Inbox/temp_weekly.csv", index=False)
    
    script = """
    if(existsTable("dfs://tushare", "weekly")){
        dropTable(database("dfs://tushare"), `weekly)
    }
    t = loadText("E:/Quant_Production/Inbox/temp_weekly.csv")
    weekly = database("dfs://tushare").createPartitionedTable(t, `weekly, `date)
    append!(weekly, t)
    select count(*) from weekly
    """
    result = session.run(script)
    print(f"   ✅ 导入完成: {result.values[0][0]:,} 条")

# 导入月线数据
print("\n4️⃣  导入月线数据...")
monthly_path = "E:/Quant_Production/Inbox/tushare_monthly.csv"
if os.path.exists(monthly_path):
    df = pd.read_csv(monthly_path)
    print(f"   CSV: {len(df):,} 条")
    df.to_csv("E:/Quant_Production/Inbox/temp_monthly.csv", index=False)
    
    script = """
    if(existsTable("dfs://tushare", "monthly")){
        dropTable(database("dfs://tushare"), `monthly)
    }
    t = loadText("E:/Quant_Production/Inbox/temp_monthly.csv")
    monthly = database("dfs://tushare").createPartitionedTable(t, `monthly, `date)
    append!(monthly, t)
    select count(*) from monthly
    """
    result = session.run(script)
    print(f"   ✅ 导入完成: {result.values[0][0]:,} 条")

# 导入复权因子
print("\n5️⃣  导入复权因子...")
adj_path = "E:/Quant_Production/Inbox/tushare_adj_factor.csv"
if os.path.exists(adj_path):
    df = pd.read_csv(adj_path)
    print(f"   CSV: {len(df):,} 条")
    df.to_csv("E:/Quant_Production/Inbox/temp_adj_factor.csv", index=False)
    
    script = """
    if(existsTable("dfs://tushare", "adj_factor")){
        dropTable(database("dfs://tushare"), `adj_factor)
    }
    t = loadText("E:/Quant_Production/Inbox/temp_adj_factor.csv")
    adj_factor = database("dfs://tushare").createPartitionedTable(t, `adj_factor, `date)
    append!(adj_factor, t)
    select count(*) from adj_factor
    """
    result = session.run(script)
    print(f"   ✅ 导入完成: {result.values[0][0]:,} 条")

print("\n" + "="*70)
print("✅ 数据导入完成！")
print("="*70)

# 总结
print("\n📊 DolphinDB 数据库总结:")
tables = session.run("""
    tables = getTables(database("dfs://tushare"))
    select * from tables
""")
print(tables)
