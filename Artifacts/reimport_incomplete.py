#!/usr/bin/env python3
"""
重新导入不完整的表
moneyflow, weekly, monthly - 使用超大内存批次
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("重新导入不完整的表")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 需要重新导入的表
TABLES = [
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow", "trade_date", 5511346),
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date", 1854341),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date", 434409),
]

for filename, db_name, table_name, date_col, expected in TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在")
        continue
    
    try:
        # 获取文件大小
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"  文件大小: {size_mb:.1f} MB")
        
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
        
        # 使用超大批次（100万条）
        BATCH_SIZE = 1000000 if "moneyflow" in filename else 500000
        temp_file = base_path + f"temp_{table_name}_large.csv"
        
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
            
            # 保存
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
                
                pct = total / expected * 100
                print(f"    批次 {batch_num}: {total:,} 条 ({pct:.1f}%)")
                
            except Exception as e:
                print(f"    批次 {batch_num} 错误: {str(e)[:60]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        imported = result.values[0][0]
        pct = imported / expected * 100
        print(f"  完成: {imported:,} 条 ({pct:.1f}%)")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("重新导入完成!")
print("="*70)
