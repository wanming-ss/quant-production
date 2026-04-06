#!/usr/bin/env python3
"""
验证 DolphinDB 数据 - 简化版
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

# 样例数据
print("\n样例数据:")
sample = session.run("select top 5 * from loadTable('dfs://tushare', 'daily')")
print(sample)

# 简单统计
print("\n数据统计:")
stats = session.run("""
    select 
        min(date) as start_date,
        max(date) as end_date,
        min(close) as min_close,
        max(close) as max_close,
        avg(close) as avg_close
    from loadTable('dfs://tushare', 'daily')
""")
print(stats)

print("\n" + "="*70)
print("✅ 验证完成！")
print("="*70)
