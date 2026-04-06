#!/usr/bin/env python3
"""
重新导入weekly和monthly - 正确处理日期
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("重新导入weekly和monthly")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", 1854341),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", 434409),
]

for filename, db_name, table_name, expected in TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    try:
        print(f"  读取CSV...")
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        total = len(df)
        print(f"  总行数: {total:,}")
        
        # 处理日期 - 使用原始日期列
        print(f"  处理日期...")
        df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d')
        valid_before = len(df)
        df = df.dropna(subset=['date'])
        valid_after = len(df)
        print(f"  有效日期: {valid_after:,} / {valid_before:,}")
        
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
        BATCH_SIZE = 200000
        temp_file = base_path + f"temp_{table_name}.csv"
        batches = (len(df) // BATCH_SIZE) + 1
        
        print(f"  导入 ({batches} 批)...")
        first = True
        imported = 0
        
        for i in range(batches):
            start = i * BATCH_SIZE
            end = min((i + 1) * BATCH_SIZE, len(df))
            batch = df.iloc[start:end]
            
            if len(batch) == 0:
                break
            
            batch.to_csv(temp_file, index=False)
            
            try:
                if first:
                    script = f'''
                    db = database("{db_name}")
                    t = loadText("{temp_file}")
                    {table_name} = db.createPartitionedTable(t, `{table_name}, `date)
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
                imported += len(batch)
                
                if (i + 1) % 5 == 0 or (i + 1) == batches:
                    pct = imported / len(df) * 100
                    print(f"    批次 {i+1}/{batches}: {imported:,} ({pct:.1f}%)")
                
            except Exception as e:
                print(f"    批次 {i+1} 错误: {str(e)[:60]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        final = result.values[0][0]
        pct = final / total * 100
        print(f"\n  完成: {final:,} / {total:,} ({pct:.1f}%)")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("导入完成!")
print("="*70)
