#!/usr/bin/env python3
"""
分批读取导入 - 使用迭代器避免内存问题
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("分批读取导入 weekly 和 monthly")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date"),
]

for csv_file, db_name, table_name, date_col in TABLES:
    print(f"\n{'='*70}")
    print(f"{csv_file}:")
    print(f"{'='*70}")
    path = base_path + csv_file
    
    try:
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print("  删除旧表")
        except:
            pass
        
        # 创建数据库
        try:
            session.run(f'''
            if(!existsDatabase("{db_name}")){{
                db = database("{db_name}", VALUE, 2016.01M..2026.12M)
            }}
            ''')
        except:
            pass
        
        # 使用迭代器分批读取
        print("  使用迭代器分批读取...")
        chunk_size = 50000  # 每批5万行
        first = True
        total_imported = 0
        batch_num = 0
        temp_file = base_path + f"temp_{table_name}_batch.csv"
        
        for chunk in pd.read_csv(path, chunksize=chunk_size, low_memory=False, iterator=True):
            batch_num += 1
            
            # 不转换日期，直接保存
            chunk.to_csv(temp_file, index=False)
            
            try:
                if first:
                    script = f'''
                    db = database("{db_name}")
                    t = loadText("{temp_file}")
                    {table_name} = db.createPartitionedTable(t, `{table_name}, `{date_col})
                    append!({table_name}, t)
                    '''
                    first = False
                else:
                    script = f'''
                    t = loadText("{temp_file}")
                    {table_name} = loadTable("{db_name}", "{table_name}")
                    append!({table_name}, t)
                    '''
                
                session.run(script)
                total_imported += len(chunk)
                
                if batch_num % 10 == 0:
                    print(f"    批次 {batch_num}: {total_imported:,} 条")
                    
            except Exception as e:
                print(f"    批次 {batch_num} 错误: {str(e)[:50]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        final = result.values[0][0]
        print(f"\n  导入完成: {final:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print(f"\n{'='*70}")
print("导入完成!")
print(f"{'='*70}")
