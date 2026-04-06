#!/usr/bin/env python3
"""
分批导入数据到 DolphinDB
解决内存限制问题
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("分批导入数据到 DolphinDB")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

BATCH_SIZE = 500000  # 每批50万条

def import_in_batches(csv_path, db_name, table_name, date_col='date'):
    """分批导入数据"""
    print(f"\n导入: {os.path.basename(csv_path)}")
    
    # 读取CSV
    df = pd.read_csv(csv_path, low_memory=False)
    total = len(df)
    print(f"   总计: {total:,} 条")
    
    # 处理日期
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
    
    # 创建数据库和表（只创建一次）
    temp_file = "E:/Quant_Production/Inbox/temp_batch.csv"
    
    # 第一批：创建表结构
    first_batch = df.iloc[:min(BATCH_SIZE, len(df))]
    first_batch.to_csv(temp_file, index=False)
    
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
    session.run(script)
    print(f"   批次 1/{(total//BATCH_SIZE)+1}: {len(first_batch):,} 条")
    
    # 后续批次：追加
    imported = len(first_batch)
    batch_num = 2
    
    while imported < total:
        end_idx = min(imported + BATCH_SIZE, total)
        batch = df.iloc[imported:end_idx]
        batch.to_csv(temp_file, index=False)
        
        script = f"""
        t = loadText("{temp_file}")
        {table_name} = loadTable("{db_name}", "{table_name}")
        append!({table_name}, t)
        """
        session.run(script)
        
        print(f"   批次 {batch_num}/{(total//BATCH_SIZE)+1}: {len(batch):,} 条")
        imported += len(batch)
        batch_num += 1
    
    # 验证
    result = session.run(f"select count(*) from loadTable('{db_name}', '{table_name}')")
    print(f"   验证: {result.values[0][0]:,} 条")
    print(f"   完成!")

# 1. 导入日线数据
import_in_batches(
    "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv",
    "dfs://tushare",
    "daily"
)

# 2. 导入周线数据
import_in_batches(
    "E:/Quant_Production/Inbox/tushare_weekly.csv",
    "dfs://tushare_weekly",
    "weekly"
)

# 3. 导入月线数据
import_in_batches(
    "E:/Quant_Production/Inbox/tushare_monthly.csv",
    "dfs://tushare_monthly",
    "monthly"
)

# 4. 导入复权因子
import_in_batches(
    "E:/Quant_Production/Inbox/tushare_adj_factor.csv",
    "dfs://tushare_adj",
    "adj_factor"
)

print("\n" + "="*70)
print("导入完成!")
print("="*70)
