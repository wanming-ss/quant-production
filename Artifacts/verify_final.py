#!/usr/bin/env python3
"""
验证 DolphinDB 最终数据
"""
import dolphindb as ddb

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

print("="*70)
print("DolphinDB 最终数据验证")
print("="*70)

# 1. 总记录数
print("\n1️⃣  总记录数...")
count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
print(f"   总计: {count.values[0][0]:,} 条")

# 2. 股票数
print("\n2️⃣  股票数...")
stocks = session.run("""
    select count(*) from 
    (select distinct symbol from loadTable('dfs://tushare', 'daily'))
""")
print(f"   总计: {stocks.values[0][0]} 只股票")

# 3. 日期范围
print("\n3️⃣  日期范围...")
dates = session.run("""
    select min(date) as start_date, max(date) as end_date 
    from loadTable('dfs://tushare', 'daily')
""")
print(f"   从: {dates['start_date'][0]}")
print(f"   到: {dates['end_date'][0]}")

# 4. 数据统计
print("\n4️⃣  价格统计...")
stats = session.run("""
    select 
        min(close) as min_close,
        max(close) as max_close,
        avg(close) as avg_close,
        min(volume) as min_volume,
        max(volume) as max_volume
    from loadTable('dfs://tushare', 'daily')
""")
print(stats)

# 5. 样例数据
print("\n5️⃣  样例数据（前5条）...")
sample = session.run("select top 5 * from loadTable('dfs://tushare', 'daily')")
print(sample)

# 6. 数据量 Top 10 股票
print("\n6️⃣  数据量 Top 10 股票...")
top10 = session.run("""
    select symbol, count(*) as records 
    from loadTable('dfs://tushare', 'daily') 
    group by symbol 
    order by records desc 
    limit 10
""")
print(top10)

# 7. 分区统计
print("\n7️⃣  按年统计...")
yearly = session.run("""
    select year(date) as year, count(*) as records 
    from loadTable('dfs://tushare', 'daily') 
    group by year(date) 
    order by year
""")
print(yearly)

print("\n" + "="*70)
print("✅ 验证完成！")
print("="*70)
