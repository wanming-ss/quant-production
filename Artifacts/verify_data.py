#!/usr/bin/env python3
"""
验证 DolphinDB 数据
"""
import dolphindb as ddb

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

print("="*70)
print("DolphinDB 数据验证")
print("="*70)

# 总记录
count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
print(f"\n📈 总记录: {count.values[0][0]:,}")

# 股票数
stocks = session.run("exec count(distinct symbol) from loadTable('dfs://tushare', 'daily')")
print(f"📊 股票数: {stocks}")

# 日期范围
dates = session.run("select min(date) as start, max(date) as end from loadTable('dfs://tushare', 'daily')")
print(f"📅 日期范围: {dates['start'][0]} ~ {dates['end'][0]}")

# 样例数据
print("\n样例数据:")
sample = session.run("select top 5 * from loadTable('dfs://tushare', 'daily')")
print(sample)

# 数据量 Top 10
print("\n数据量 Top 10:")
top10 = session.run("select symbol, count(*) as cnt from loadTable('dfs://tushare', 'daily') group by symbol order by cnt desc limit 10")
print(top10)

print("\n" + "="*70)
print("✅ 验证完成！数据已成功导入 DolphinDB")
print("="*70)
