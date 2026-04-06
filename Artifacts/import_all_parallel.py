#!/usr/bin/env python3
"""
并行导入所有CSV到DolphinDB
使用多进程加速
"""
import dolphindb as ddb
import pandas as pd
import os
from multiprocessing import Pool, cpu_count

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 导入配置
IMPORT_CONFIG = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly", "date"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly", "date"),
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor", "date"),
    ("tushare_daily_basic.csv", "dfs://tushare_daily_basic", "daily_basic", "trade_date"),
    ("tushare_income.csv", "dfs://tushare_income", "income", "ann_date"),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet", "ann_date"),
    ("tushare_cashflow.csv", "dfs://tushare_cashflow", "cashflow", "ann_date"),
    ("tushare_forecast.csv", "dfs://tushare_forecast", "forecast", "ann_date"),
    ("tushare_express.csv", "dfs://tushare_express", "express", "ann_date"),
    ("tushare_fina_indicator.csv", "dfs://tushare_fina_indicator", "fina_indicator", "ann_date"),
    ("tushare_fina_audit.csv", "dfs://tushare_fina_audit", "fina_audit", "ann_date"),
    ("tushare_fina_mainbz.csv", "dfs://tushare_fina_mainbz", "fina_mainbz", "end_date"),
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow", "trade_date"),
    ("tushare_block_trade.csv", "dfs://tushare_block_trade", "block_trade", "trade_date"),
    ("tushare_limit_list.csv", "dfs://tushare_limit_list", "limit_list", "trade_date"),
    ("tushare_top_list.csv", "dfs://tushare_top_list", "top_list", "trade_date"),
    ("tushare_top_inst.csv", "dfs://tushare_top_inst", "top_inst", "trade_date"),
    ("tushare_new_share.csv", "dfs://tushare_new_share", "new_share", "ipo_date"),
    ("tushare_holdernumber.csv", "dfs://tushare_holdernumber", "holdernumber", "ann_date"),
    ("tushare_holdertrade.csv", "dfs://tushare_holdertrade", "holdertrade", "ann_date"),
    ("tushare_namechange.csv", "dfs://tushare_namechange", "namechange", "start_date"),
    ("tushare_trade_cal.csv", "dfs://tushare_trade_cal", "trade_cal", "cal_date"),
    ("tushare_repurchase.csv", "dfs://tushare_repurchase", "repurchase", "ann_date"),
]

base_path = "E:/Quant_Production/Inbox/"
BATCH_SIZE = 100000

def import_single(config):
    """导入单个文件"""
    filename, db_name, table_name, date_col = config
    path = base_path + filename
    
    if not os.path.exists(path):
        return (filename, "文件不存在", 0)
    
    try:
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        total = len(df)
        
        # 处理日期
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # 分批导入
        temp_file = base_path + "temp_" + table_name + ".csv"
        batches = (len(df) // BATCH_SIZE) + 1
        
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
            
            session.run(script)
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return (filename, "成功", total)
        
    except Exception as e:
        return (filename, f"错误: {str(e)[:30]}", 0)

print("="*70)
print("并行导入所有数据到 DolphinDB")
print(f"总计 {len(IMPORT_CONFIG)} 个表")
print("="*70)

# 串行导入（DolphinDB不支持并发）
results = []
for i, config in enumerate(IMPORT_CONFIG, 1):
    filename, status, count = import_single(config)
    results.append((filename, status, count))
    print(f"[{i}/{len(IMPORT_CONFIG)}] {filename}: {status} ({count:,} 条)")

print("\n" + "="*70)
print("导入完成!")
print("="*70)

success = sum(1 for r in results if r[1] == "成功")
print(f"成功: {success}/{len(IMPORT_CONFIG)}")
