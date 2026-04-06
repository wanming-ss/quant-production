
import tushare as ts
import pandas as pd
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

CSV_PATH = "E:/Quant_Production/Inbox/tushare_cashflow.csv"

print(f"[{datetime.now()}] 开始 cashflow...")

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

if os.path.exists(CSV_PATH):
    try:
        existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
        if 'ts_code' in existing.columns:
            completed = set(existing['ts_code'].unique())
        else:
            completed = set()
        stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
        print(f"  已完成: {len(completed)} 只")
    except:
        pass

remaining = len(stock_df)
print(f"  剩余: {remaining} 只")

if remaining == 0:
    print("  ✅ 完成！")
    exit(0)

all_data = []
for j, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    
    if j % 50 == 1:
        print(f"  [{j}/{remaining}] {ts_code}")
    
    try:
        if 'cashflow' == 'limit_list':
            continue  # skip
        else:
            df = getattr(pro, 'cashflow')(ts_code=ts_code, start_date='20160101', end_date='20250324')
        
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.2)
    
    if j % 100 == 0 and all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
        print(f"  💾 保存 {len(batch):,} 条")
        all_data = []

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

print(f"[{datetime.now()}] cashflow 完成")
