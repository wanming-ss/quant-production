#!/usr/bin/env python3
"""
终极修复 - 使用最简单的方式导入
只读取存在的列
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("终极修复导入")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 修复失败的表
FAILED_TABLES = [
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor"),
    ("tushare_income.csv", "dfs://tushare_income", "income"),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet"),
]

for filename, db_name, table_name in FAILED_TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在")
        continue
    
    try:
        # 先读取查看列名
        print(f"  检查列名...")
        df_sample = pd.read_csv(path, nrows=2)
        columns = df_sample.columns.tolist()
        print(f"  列名: {columns[:5]}...")
        
        # 确定日期列
        date_col = None
        for col in columns:
            if 'date' in col.lower():
                date_col = col
                break
        
        if not date_col:
            date_col = columns[1]  # 假设第二列是日期
        
        print(f"  日期列: {date_col}")
        
        # 使用chunksize读取
        print(f"  分批导入...")
        temp_file = base_path + f"temp_{table_name}_final.csv"
        
        # 删除旧表
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
        
        first = True
        total = 0
        
        for i, chunk in enumerate(pd.read_csv(path, chunksize=50000, low_memory=False)):
            # 处理日期
            if date_col in chunk.columns:
                chunk[date_col] = pd.to_datetime(chunk[date_col], errors='coerce')
                chunk = chunk.dropna(subset=[date_col])
            
            if len(chunk) == 0:
                continue
            
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
                total += len(chunk)
                
                if (i + 1) % 10 == 0:
                    print(f"    已导入 {total:,} 条")
                    
            except Exception as e:
                print(f"    批次 {i+1} 错误: {str(e)[:60]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print(f"  导入完成: {total:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:100]}")

print("\n" + "="*70)
print("修复完成!")
print("="*70)
