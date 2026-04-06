
import tushare as ts
import pandas as pd
import time
from datetime import datetime

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

CSV_PATH = "E:/Quant_Production/Inbox/tushare_limit_list.csv"

print(f"[{datetime.now()}] 开始下载 limit_list...")

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

# 检查已有数据
if os.path.exists(CSV_PATH):
    try:
        existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
        if 'ts_code' in existing.columns:
            completed = set(existing['ts_code'].unique())
        elif 'symbol' in existing.columns:
            completed = set(existing['symbol'].unique())
        else:
            completed = set()
        stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
        print(f"  已完成: {len(completed)} 只，剩余: {len(stock_df)} 只")
    except:
        pass

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    
    try:
        df = pro.limit_list(ts_code=ts_code, start_date='20160101', end_date='20250324')
        if df is not None and not df.empty:
            all_data.append(df)
        
        if i % 100 == 0:
            print(f"  [{i}/{len(stock_df)}] {ts_code}")
            if all_data:
                batch = pd.concat(all_data, ignore_index=True)
                batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
                all_data = []
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    # 无延迟
    # time.sleep(0)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

print(f"[{datetime.now()}] limit_list 完成!")
