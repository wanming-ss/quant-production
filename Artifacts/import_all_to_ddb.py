#!/usr/bin/env python3
"""
完整导入所有数据到 DolphinDB
分批导入避免内存问题
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("完整导入所有数据到 DolphinDB")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

BATCH_SIZE = 100000  # 每批10万条

def import_csv_to_ddb(csv_path, db_name, table_name, date_col='date'):
    """导入CSV到DolphinDB"""
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        return False
    
    print(f"\n导入: {os.path.basename(csv_path)}")
    
    # 读取CSV
    df = pd.read_csv(csv_path, low_memory=False)
    total = len(df)
    print(f"   CSV: {total:,} 条")
    
    # 处理日期
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
    
    # 分批导入
    temp_file = "E:/Quant_Production/Inbox/temp_import.csv"
    batches = (len(df) // BATCH_SIZE) + 1
    
    print(f"   分批导入 ({batches} 批)...")
    
    for i in range(batches):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, len(df))
        batch = df.iloc[start:end]
        
        if len(batch) == 0:
            break
        
        # 保存临时文件
        batch.to_csv(temp_file, index=False)
        
        # 第一批创建表，后续追加
        if i == 0:
            script = f"""
            if(!existsDatabase("{db_name}")){{
                db = database("{db_name}", VALUE, 2016.01M..2026.12M)
            }} else {{
                db = database("{db_name}")
            }}
            
            if(existsTable("{db_name}", "{table_name}")){{
                dropTable(db, `{table_name})
            }}
            
            t = loadText("{temp_file}")
            {table_name} = db.createPartitionedTable(t, `{table_name}, `{date_col})
            append!({table_name}, t)
            """
        else:
            script = f"""
            t = loadText("{temp_file}")
            {table_name} = loadTable("{db_name}", "{table_name}")
            append!({table_name}, t)
            """
        
        try:
            session.run(script)
            print(f"   批次 {i+1}/{batches}: {len(batch):,} 条 ✓")
        except Exception as e:
            print(f"   批次 {i+1} 错误: {e}")
            continue
    
    # 验证
    try:
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        count = result.values[0][0]
        print(f"   ✅ 导入完成: {count:,} 条")
        return True
    except:
        print(f"   ⚠️  验证失败")
        return False

# 导入所有数据
imports = [
    ("E:/Quant_Production/Inbox/tushare_weekly.csv", "dfs://tushare_weekly", "weekly"),
    ("E:/Quant_Production/Inbox/tushare_monthly.csv", "dfs://tushare_monthly", "monthly"),
    ("E:/Quant_Production/Inbox/tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor"),
    ("E:/Quant_Production/Inbox/tushare_income.csv", "dfs://tushare_income", "income"),
    ("E:/Quant_Production/Inbox/tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet"),
    ("E:/Quant_Production/Inbox/tushare_cashflow.csv", "dfs://tushare_cashflow", "cashflow"),
]

results = {}
for csv, db, table in imports:
    success = import_csv_to_ddb(csv, db, table)
    results[f"{db}/{table}"] = success

print("\n" + "="*70)
print("导入完成!")
print("="*70)

for name, success in results.items():
    status = "✓" if success else "✗"
    print(f"{status} {name}")
