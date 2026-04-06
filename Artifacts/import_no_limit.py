#!/usr/bin/env python3
"""
无内存限制导入 weekly 和 monthly
"""
import dolphindb as ddb

print("="*70)
print("无内存限制导入 weekly 和 monthly")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 直接使用 DolphinDB loadText 导入
for csv_file, db_name, table_name in [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly"),
]:
    print(f"\n{csv_file}:")
    path = base_path + csv_file
    
    try:
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print("  删除旧表")
        except:
            pass
        
        # 直接使用 loadText 导入整个文件
        print("  直接导入整个文件...")
        script = f'''
        if(!existsDatabase("{db_name}")){{
            db = database("{db_name}", VALUE, 2016.01M..2026.12M)
        }} else {{
            db = database("{db_name}")
        }}
        
        t = loadText("{path}")
        {table_name} = db.createPartitionedTable(t, `{table_name}, `date)
        append!({table_name}, t)
        '''
        
        session.run(script)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        count = result.values[0][0]
        print(f"  导入完成: {count:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("导入完成!")
print("="*70)
