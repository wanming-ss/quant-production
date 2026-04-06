#!/usr/bin/env python3
"""
紧急补充 - 完整导入weekly和monthly
使用最可靠的导入方式
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("紧急补充 - weekly和monthly完整导入")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 需要补充的表
TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date", 1854341),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date", 434409),
]

for filename, db_name, table_name, date_col, expected in TABLES:
    print(f"\n{'='*70}")
    print(f"{filename}:")
    print(f"{'='*70}")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在!")
        continue
    
    try:
        # 获取CSV总行数
        print(f"  统计CSV总行数...")
        csv_rows = sum(1 for _ in open(path, 'r', encoding='utf-8', errors='ignore')) - 1
        print(f"  CSV总行数: {csv_rows:,}")
        
        # 删除旧表
        print(f"  删除旧表...")
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
        
        # 读取整个CSV到内存
        print(f"  读取整个CSV到内存...")
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        total = len(df)
        print(f"  读取完成: {total:,} 条")
        
        # 处理日期
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        print(f"  有效数据: {len(df):,} 条")
        
        # 分批导入（中等批次）
        BATCH_SIZE = 200000
        temp_file = base_path + f"temp_{table_name}_final.csv"
        batches = (len(df) // BATCH_SIZE) + 1
        
        print(f"  开始导入 ({batches} 批)...")
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
                imported += len(batch)
                pct = imported / total * 100
                print(f"    批次 {i+1}/{batches}: {imported:,} 条 ({pct:.1f}%)")
                
            except Exception as e:
                print(f"    批次 {i+1} 错误: {str(e)[:60]}")
                continue
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 最终验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        final_count = result.values[0][0]
        final_pct = final_count / csv_rows * 100
        print(f"\n  导入完成: {final_count:,} / {csv_rows:,} ({final_pct:.1f}%)")
        
        if final_pct >= 95:
            print(f"  ✓ {table_name} 导入成功!")
        else:
            print(f"  ✗ {table_name} 导入不完整")
        
    except Exception as e:
        print(f"  错误: {str(e)[:100]}")

print(f"\n{'='*70}")
print("紧急补充完成!")
print(f"{'='*70}")
