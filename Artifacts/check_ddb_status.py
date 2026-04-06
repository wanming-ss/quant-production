#!/usr/bin/env python3
"""
检查 DolphinDB 数据状态
"""
import dolphindb as ddb

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

print("="*70)
print("DolphinDB 数据状态检查")
print("="*70)

# 检查各表数据量
tables = [
    ("dfs://tushare", "daily"),
    ("dfs://tushare_weekly", "weekly"),
    ("dfs://tushare_monthly", "monthly"),
    ("dfs://tushare_adj", "adj_factor"),
]

for db, table in tables:
    try:
        result = session.run(f'select count(*) from loadTable("{db}", "{table}")')
        count = result.values[0][0]
        print(f"{db}/{table}: {count:,} 条")
    except Exception as e:
        print(f"{db}/{table}: 未找到或错误")

print("="*70)
