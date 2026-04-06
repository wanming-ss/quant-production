#!/usr/bin/env python3
"""
极简修复 - 使用最小批次导入最后2个表
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("极简修复最后2个表")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 最后2个失败的表
FAILED_TABLES = [
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
        # 查看列名
        print(f"  检查列名...")
        df_sample = pd.read_csv(path, nrows=2)
        columns = df_sample.columns.tolist()
        print(f"  列数: {len(columns)}")
        
        # 找到日期列
        date_col = None
        for col in columns:
            if 'ann_date' in col.lower():
                date_col = col
                break
        if not date_col:
            date_col = columns[1]
        print(f"  日期列: {date_col}")
        
        # 超小批次读取
        BATCH_SIZE = 10000
        temp_file = base_path + f"temp_{table_name}_mini.csv"
        
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
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
        
        print(f"  分批导入 (每批{BATCH_SIZE:,}条)...")
        first = True
        total = 0
        batch_num = 0
        
        for chunk in pd.read_csv(path, chunksize=BATCH_SIZE, low_memory=False, on_bad_lines='skip'):
            batch_num += 1
            
            # 处理日期
            if date_col in chunk.columns:
                chunk[date_col] = pd.to_datetime(chunk[date_col], errors='coerce')
                chunk = chunk.dropna(subset=[date_col])
            
            if len(chunk) == 0:
                continue
            
            # 只保留关键列减少内存
            key_cols = [c for c in ['ts_code', date_col, 'total_revenue', 'net_income', 'total_assets', 'total_liabilities'] if c in chunk.columns]
            if len(key_cols) < 3:
                key_cols = chunk.columns.tolist()[:10]  # 只保留前10列
            
            chunk = chunk[key_cols]
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
                
                if batch_num % 50 == 0:
                    print(f"    批次 {batch_num}: {total:,} 条")
                    
            except Exception as e:
                print(f"    批次 {batch_num} 错误: {str(e)[:50]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print(f"  完成: {total:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("修复完成!")
print("="*70)
