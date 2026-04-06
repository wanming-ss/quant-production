#!/usr/bin/env python3
"""
高效下载剩余接口
stk_pledge, stk_reward, top_list, top_inst
按日期批量下载，提高效率
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
print("高效下载剩余接口")
print("="*70)

# 1. stk_reward (股票回购) - 一次性下载
print("\n1️⃣  股票回购 (stk_reward)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_reward.csv"

try:
    df = pro.stk_reward()
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. top_list (龙虎榜) - 按日期下载
print("\n2️⃣  龙虎榜 (top_list)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_top_list.csv"

if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    last_date = str(existing['trade_date'].max()) if 'trade_date' in existing.columns else '20160101'
    print(f"   已有数据到: {last_date}")
else:
    last_date = '20160101'
    existing = None

dates = pd.date_range('2016-01-01', '2025-03-24', freq='D')
dates = [d.strftime('%Y%m%d') for d in dates if d.strftime('%Y%m%d') > last_date]
print(f"   剩余 {len(dates)} 天")

if len(dates) > 0:
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
                print(f"\n   ⛔ API限制，等待30秒...")
                time.sleep(30)
        
        time.sleep(0.15)
        
        if i % 200 == 0 and all_data:
            batch = pd.concat(all_data, ignore_index=True)
            batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
            print(f"   💾 保存 {len(batch):,} 条")
            all_data = []
    
    if all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
    
    print(f"   ✅ 完成")

# 3. top_inst (龙虎榜机构) - 按日期下载
print("\n3️⃣  龙虎榜机构 (top_inst)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_top_inst.csv"

if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    last_date = str(existing['trade_date'].max()) if 'trade_date' in existing.columns else '20160101'
else:
    last_date = '20160101'

dates = pd.date_range('2016-01-01', '2025-03-24', freq='D')
dates = [d.strftime('%Y%m%d') for d in dates if d.strftime('%Y%m%d') > last_date]
print(f"   剩余 {len(dates)} 天")

if len(dates) > 0:
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
        
        time.sleep(0.15)
        
        if i % 200 == 0 and all_data:
            batch = pd.concat(all_data, ignore_index=True)
            batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
            print(f"   💾 保存 {len(batch):,} 条")
            all_data = []
    
    if all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
    
    print(f"   ✅ 完成")

# 4. stk_pledge (股权质押) - 按股票下载
print("\n4️⃣  股权质押 (stk_pledge)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_stk_pledge.csv"

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
print(f"   总计 {len(stock_df)} 只")

if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    completed = set(existing['ts_code'].unique()) if 'ts_code' in existing.columns else set()
    stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
    print(f"   已完成: {len(completed)} 只")

remaining = len(stock_df)
print(f"   剩余: {remaining} 只")

if remaining > 0:
    all_data = []
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        if i % 100 == 1:
            print(f"   [{i}/{remaining}] {row['ts_code']}")
        
        try:
            df = pro.stk_pledge(ts_code=row['ts_code'])
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            if "500次" in str(e):
                time.sleep(30)
        
        time.sleep(0.15)
        
        if i % 200 == 0 and all_data:
            batch = pd.concat(all_data, ignore_index=True)
            batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
            print(f"   💾 保存 {len(batch):,} 条")
            all_data = []
    
    if all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
    
    print(f"   ✅ 完成")

print("\n" + "="*70)
print("所有剩余接口下载完成！")
print("="*70)
