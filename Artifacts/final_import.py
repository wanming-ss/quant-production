#!/usr/bin/env python3
"""
最后尝试：直接Python逐行插入到DolphinDB
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("最终导入尝试")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 最后2个表
TABLES = [
    ("tushare_income.csv", "dfs://tushare_income", "income", "ann_date"),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet", "ann_date"),
]

for filename, db_name, table_name, date_col in TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在")
        continue
    
    try:
        # 获取文件大小
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"  文件大小: {size_mb:.1f} MB")
        
        # 先删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print(f"  删除旧表")
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
        
        # 使用pandas逐块读取并直接插入
        print(f"  逐块导入...")
        chunk_size = 20000
        total = 0
        first = True
        
        for i, chunk in enumerate(pd.read_csv(path, chunksize=chunk_size, low_memory=False, on_bad_lines='skip')):
            # 处理日期
            if date_col in chunk.columns:
                chunk[date_col] = pd.to_datetime(chunk[date_col], errors='coerce')
                chunk = chunk.dropna(subset=[date_col])
            
            if len(chunk) == 0:
                continue
            
            # 保存到临时文件
            temp_file = f"{base_path}temp_{table_name}.csv"
            chunk.to_csv(temp_file, index=False)
            
            # 导入
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
                total += len(chunk)
                
                if (i + 1) % 50 == 0:
                    print(f"    已导入 {total:,} 条")
                    
            except Exception as e:
                print(f"    批次 {i+1} 错误: {str(e)[:60]}")
                continue
        
        # 清理
        temp_file = f"{base_path}temp_{table_name}.csv"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print(f"  完成: {total:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("导入完成!")
print("="*70)
