#!/usr/bin/env python3
"""
最后尝试：确保100%完整导入
weekly, monthly, moneyflow
"""
import dolphindb as ddb
import os

print("="*70)
print("最后尝试：确保100%完整")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 需要达到100%的表
TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date"),
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow", "trade_date"),
]

for csv_file, db_name, table_name, date_col in TABLES:
    print(f"\n{'='*70}")
    print(f"{csv_file}:")
    print(f"{'='*70}")
    
    path = base_path + csv_file
    
    # 获取CSV总行数
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        csv_total = sum(1 for _ in f) - 1
    print(f"  CSV总行数: {csv_total:,}")
    
    try:
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print("  删除旧表")
        except:
            pass
        
        # 使用DolphinDB直接导入整个文件
        print("  直接导入整个CSV...")
        script = f'''
        if(!existsDatabase("{db_name}")){{
            db = database("{db_name}", VALUE, 2016.01M..2026.12M)
        }} else {{
            db = database("{db_name}")
        }}
        
        t = loadText("{path}")
        {table_name} = db.createPartitionedTable(t, `{table_name}, `{date_col})
        append!({table_name}, t)
        '''
        
        session.run(script)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        imported = result.values[0][0]
        pct = imported / csv_total * 100
        
        print(f"  导入完成: {imported:,} / {csv_total:,} ({pct:.1f}%)")
        
        if pct >= 99:
            print(f"  ✓ {table_name} 成功!")
        else:
            print(f"  ✗ {table_name} 不完整")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print(f"\n{'='*70}")
print("完成!")
print(f"{'='*70}")
