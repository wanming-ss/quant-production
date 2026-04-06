#!/usr/bin/env python3
"""
下载剩余接口
stk_pledge, stk_reward, top_list, top_inst
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

print("="*70)
print("下载剩余接口")
print("="*70)

# 1. stk_pledge (股权质押)
print("\n1️⃣  股权质押...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_pledge.csv"

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
print(f"   总计: {len(stock_df)} 只")

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    if i % 100 == 1:
        print(f"   [{i}/{len(stock_df)}] {row['ts_code']}")
    
    try:
        df = pro.stk_pledge(ts_code=row['ts_code'])
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.2)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

# 2. stk_reward (股票回购)
print("\n2️⃣  股票回购...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_reward.csv"

try:
    df = pro.stk_reward()
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
except Exception as e:
    print(f"   ⚠️  {e}")

# 3. top_list (龙虎榜)
print("\n3️⃣  龙虎榜...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_top_list.csv"

dates = pd.date_range('2016-01-01', '2025-03-24', freq='D')
dates = [d.strftime('%Y%m%d') for d in dates]

all_data = []
for i, trade_date in enumerate(dates, 1):
    if i % 100 == 1:
        print(f"   [{i}/{len(dates)}] {trade_date}")
    
    try:
        df = pro.top_list(trade_date=trade_date)
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.2)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

# 4. top_inst (龙虎榜机构)
print("\n4️⃣  龙虎榜机构...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_top_inst.csv"

all_data = []
for i, trade_date in enumerate(dates, 1):
    if i % 100 == 1:
        print(f"   [{i}/{len(dates)}] {trade_date}")
    
    try:
        df = pro.top_inst(trade_date=trade_date)
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.2)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

print("\n" + "="*70)
print("剩余接口下载完成！")
print("="*70)
