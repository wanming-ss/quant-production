#!/usr/bin/env python3
"""
增量导入剩余数据
只导入未完成或数据量不足的表
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("增量导入剩余数据")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"
BATCH_SIZE = 100000

# 需要重新导入的表（数据量不足）
REIMPORT_CONFIG = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date", 1854341),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date", 434409),
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor", "date", 9825377),
    ("tushare_income.csv", "dfs://tushare_income", "income", "ann_date", 908663),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet", "ann_date", 166249),
    ("tushare_cashflow.csv", "dfs://tushare_cashflow", "cashflow", "ann_date", 153683),
    ("tushare_forecast.csv", "dfs://tushare_forecast", "forecast", "ann_date", 74163),
    ("tushare_express.csv", "dfs://tushare_express", "express", "ann_date", 13291),
    ("tushare_fina_indicator.csv", "dfs://tushare_fina_indicator", "fina_indicator", "ann_date", 590892),
    ("tushare_fina_audit.csv", "dfs://tushare_fina_audit", "fina_audit", "ann_date", 33639),
    ("tushare_fina_mainbz.csv", "dfs://tushare_fina_mainbz", "fina_mainbz", "end_date", 311164),
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow", "trade_date", 5511346),
    ("tushare_block_trade.csv", "dfs://tushare_block_trade", "block_trade", "trade_date", 163788),
    ("tushare_limit_list.csv", "dfs://tushare_limit_list", "limit_list", "trade_date", 143508),
    ("tushare_top_list.csv", "dfs://tushare_top_list", "top_list", "trade_date", 122769),
    ("tushare_top_inst.csv", "dfs://tushare_top_inst", "top_inst", "trade_date", 254190),
    ("tushare_new_share.csv", "dfs://tushare_new_share", "new_share", "ipo_date", 4800000),
]

def import_table(config):
    """导入单个表"""
    filename, db_name, table_name, date_col, expected_count = config
    path = base_path + filename
    
    if not os.path.exists(path):
        return (filename, "文件不存在", 0)
    
    try:
        # 读取CSV
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        total = len(df)
        
        print(f"\n{filename}:")
        print(f"  CSV行数: {total:,} (预期 {expected_count:,})")
        
        # 处理日期
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print(f"  删除旧表")
        except:
            pass
        
        # 分批导入
        temp_file = base_path + "temp_import.csv"
        batches = (len(df) // BATCH_SIZE) + 1
        print(f"  分批导入 ({batches} 批)...")
        
        for i in range(batches):
            start = i * BATCH_SIZE
            end = min((i + 1) * BATCH_SIZE, len(df))
            batch = df.iloc[start:end]
            
            if len(batch) == 0:
                break
            
            batch.to_csv(temp_file, index=False)
            
            if i == 0:
                script = f"""
                if(!existsDatabase("{db_name}")){{
                    db = database("{db_name}", VALUE, 2016.01M..2026.12M)
                }} else {{
                    db = database("{db_name}")
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
            
            session.run(script)
            
            if (i + 1) % 10 == 0:
                print(f"    批次 {i+1}/{batches}")
        
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        imported = result.values[0][0]
        print(f"  导入完成: {imported:,} 条")
        
        return (filename, "成功", imported)
        
    except Exception as e:
        return (filename, f"错误: {str(e)[:50]}", 0)

# 导入所有表
print(f"需要导入 {len(REIMPORT_CONFIG)} 个表\n")

for i, config in enumerate(REIMPORT_CONFIG, 1):
    filename, status, count = import_table(config)
    print(f"[{i}/{len(REIMPORT_CONFIG)}] {filename}: {status}")

print("\n" + "="*70)
print("增量导入完成!")
print("="*70)
