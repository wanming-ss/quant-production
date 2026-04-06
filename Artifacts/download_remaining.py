#!/usr/bin/env python3
"""
继续下载未完成的数据
limit_list, fina_indicator
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("继续下载未完成数据")
print("="*70)

# 1. 下载 limit_list (涨跌停统计)
print("\n1️⃣  下载涨跌停统计...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_limit_list.csv"

# 生成日期列表
dates = pd.date_range('2024-01-01', '2025-03-24', freq='D')
dates = [d.strftime('%Y%m%d') for d in dates]

# 检查已有数据
if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    last_date = existing['trade_date'].max() if 'trade_date' in existing.columns else '20240101'
    dates = [d for d in dates if d > last_date]
    print(f"   已有数据到: {last_date}, 剩余 {len(dates)} 天")

all_data = []
for i, trade_date in enumerate(dates, 1):
    if i % 50 == 1:
        print(f"   [{i}/{len(dates)}] {trade_date}")
    
    try:
        df = pro.limit_list(trade_date=trade_date)
        if df is not None and not df.empty:
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            print(f"\n   ⛔ API限制，等待30秒...")
            time.sleep(30)
    
    time.sleep(0.2)
    
    if i % 100 == 0 and all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
        print(f"   💾 保存 {len(batch_df):,} 条")
        all_data = []

if all_data:
    batch_df = pd.concat(all_data, ignore_index=True)
    batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)

print(f"   ✅ limit_list 完成")

# 2. 下载 fina_indicator (财务指标)
print("\n2️⃣  下载财务指标...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_indicator.csv"

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    completed = set(existing['ts_code'].unique())
    stock_df = stock_df[~stock_df['ts_code'].isin(completed)]

remaining = len(stock_df)
print(f"   剩余: {remaining} 只")

if remaining > 0:
    all_data = []
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        
        if i % 50 == 1:
            print(f"   [{i}/{remaining}] {ts_code}")
        
        try:
            df = pro.fina_indicator(ts_code=ts_code)
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            if "500次" in str(e):
                time.sleep(30)
        
        time.sleep(0.2)
        
        if i % 100 == 0 and all_data:
            batch_df = pd.concat(all_data, ignore_index=True)
            batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
            print(f"   💾 保存 {len(batch_df):,} 条")
            all_data = []
    
    if all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)

print(f"   ✅ fina_indicator 完成")

print("\n" + "="*70)
print("下载完成!")
print("="*70)
