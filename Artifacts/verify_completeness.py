import pandas as pd
import dolphindb as ddb
import os

print("="*80)
print("数据完整性对比验证")
print("="*80)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 已导入的表对比
COMPARE_TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly"),
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor"),
    ("tushare_daily_basic.csv", "dfs://tushare_daily_basic", "daily_basic"),
    ("tushare_cashflow.csv", "dfs://tushare_cashflow", "cashflow"),
    ("tushare_forecast.csv", "dfs://tushare_forecast", "forecast"),
    ("tushare_express.csv", "dfs://tushare_express", "express"),
    ("tushare_fina_indicator.csv", "dfs://tushare_fina_indicator", "fina_indicator"),
    ("tushare_fina_audit.csv", "dfs://tushare_fina_audit", "fina_audit"),
    ("tushare_fina_mainbz.csv", "dfs://tushare_fina_mainbz", "fina_mainbz"),
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow"),
    ("tushare_block_trade.csv", "dfs://tushare_block_trade", "block_trade"),
    ("tushare_limit_list.csv", "dfs://tushare_limit_list", "limit_list"),
    ("tushare_top_list.csv", "dfs://tushare_top_list", "top_list"),
    ("tushare_top_inst.csv", "dfs://tushare_top_inst", "top_inst"),
    ("tushare_new_share.csv", "dfs://tushare_new_share", "new_share"),
    ("tushare_holdernumber.csv", "dfs://tushare_holdernumber", "holdernumber"),
    ("tushare_holdertrade.csv", "dfs://tushare_holdertrade", "holdertrade"),
]

print("\n对比CSV和DolphinDB数据量:\n")

all_complete = True

for csv_file, db_name, table_name in COMPARE_TABLES:
    csv_path = base_path + csv_file
    
    if not os.path.exists(csv_path):
        print(f"{csv_file}: CSV文件不存在")
        continue
    
    try:
        # CSV行数
        csv_rows = sum(1 for _ in open(csv_path, 'r', encoding='utf-8', errors='ignore')) - 1
        
        # DolphinDB行数
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        ddb_rows = result.values[0][0]
        
        # 计算百分比
        pct = (ddb_rows / csv_rows * 100) if csv_rows > 0 else 0
        status = "OK" if pct >= 95 else "INCOMPLETE"
        
        print(f"{status:10s} {table_name:20s}: CSV={csv_rows:>10,}, DDB={ddb_rows:>10,} ({pct:5.1f}%)")
        
        if pct < 95:
            all_complete = False
            
    except Exception as e:
        print(f"ERROR      {table_name:20s}: {str(e)[:40]}")
        all_complete = False

print("\n" + "="*80)
if all_complete:
    print("Result: All tables complete (>=95%)")
else:
    print("Result: Some tables incomplete (<95%)")
print("="*80)
