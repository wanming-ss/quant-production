#!/usr/bin/env python3
"""
快速下载最后3个接口
top_inst, stk_reward, stk_pledge
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
print("快速下载最后3个接口")
print("="*70)

# 1. stk_reward (股票回购) - 一次性下载
print("\n1️⃣  股票回购 (stk_reward)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_reward.csv"

try:
    df = pro.stk_reward()
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条, {len(df)*200/1024/1024:.2f} MB")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. top_inst (龙虎榜机构) - 只下载2024-2025年
print("\n2️⃣  龙虎榜机构 (top_inst)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_top_inst.csv"

# 只下载最近1年数据，加快速度
dates = pd.date_range('2024-01-01', '2025-03-24', freq='D')
dates = [d.strftime('%Y%m%d') for d in dates]
print(f"   下载 {len(dates)} 天（2024-2025）")

all_data = []
for i, trade_date in enumerate(dates, 1):
    if i % 50 == 1:
        print(f"   [{i}/{len(dates)}] {trade_date}")
    
    try:
        df = pro.top_inst(trade_date=trade_date)
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.1)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

# 3. stk_pledge (股权质押) - 只下载前1000只股票
print("\n3️⃣  股权质押 (stk_pledge)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_pledge.csv"

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
stock_df = stock_df.head(1000)  # 只下载前1000只
print(f"   下载前 {len(stock_df)} 只股票")

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
    
    time.sleep(0.1)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

print("\n" + "="*70)
print("最后3个接口下载完成！")
print("="*70)
