#!/usr/bin/env python3
"""
修复失败的表和小批次导入未完成数据
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("修复失败的表和继续导入")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"
BATCH_SIZE = 25000  # 更小的批次

# 需要修复的表
FIX_TABLES = [
    # 失败的表
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor", "trade_date"),
    ("tushare_income.csv", "dfs://tushare_income", "income", "ann_date"),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet", "ann_date"),
    # 未完成的表
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date"),
    ("tushare_cashflow.csv", "dfs://tushare_cashflow", "cashflow", "ann_date"),
]

for filename, db_name, table_name, date_col in FIX_TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在")
        continue
    
    try:
        # 获取文件大小
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"  文件大小: {size_mb:.1f} MB")
        
        # 分块读取大文件
        print(f"  分块读取...")
        chunks = []
        for chunk in pd.read_csv(path, chunksize=100000, low_memory=False, on_bad_lines='skip'):
            if date_col in chunk.columns:
                chunk[date_col] = pd.to_datetime(chunk[date_col], errors='coerce')
                chunk = chunk.dropna(subset=[date_col])
            chunks.append(chunk)
            print(f"    已读取 {sum(len(c) for c in chunks):,} 条")
        
        df = pd.concat(chunks, ignore_index=True)
        total = len(df)
        print(f"  总行数: {total:,}")
        
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
        
        # 分批导入
        temp_file = base_path + "temp_fix.csv"
        batches = (len(df) // BATCH_SIZE) + 1
        print(f"  分批导入 ({batches} 批, 每批{BATCH_SIZE:,}条)...")
        
        for i in range(batches):
            start = i * BATCH_SIZE
            end = min((i + 1) * BATCH_SIZE, len(df))
            batch = df.iloc[start:end]
            
            if len(batch) == 0:
                break
            
            batch.to_csv(temp_file, index=False)
            
            try:
                if i == 0:
                    script = f'''
                    db = database("{db_name}")
                    t = loadText("{temp_file}")
                    {table_name} = db.createPartitionedTable(t, `{table_name}, `{date_col})
                    append!({table_name}, t)
                    '''
                else:
                    script = f'''
                    t = loadText("{temp_file}")
                    {table_name} = loadTable("{db_name}", "{table_name}")
                    append!({table_name}, t)
                    '''
                
                session.run(script)
                
                if (i + 1) % 5 == 0 or (i + 1) == batches:
                    print(f"    进度: {i+1}/{batches} ({end:,}条)")
                    
            except Exception as e:
                print(f"    批次 {i+1} 错误: {str(e)[:80]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 验证
        try:
            result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
            imported = result.values[0][0]
            print(f"  导入完成: {imported:,} 条 ({imported/total*100:.1f}%)")
        except:
            print(f"  验证失败")
        
    except Exception as e:
        print(f"  错误: {str(e)[:100]}")

print("\n" + "="*70)
print("修复完成!")
print("="*70)
