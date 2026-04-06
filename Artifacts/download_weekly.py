#!/usr/bin/env python3
"""
Tushare 周线数据下载
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_weekly.csv"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 周线数据下载")
print("="*70)
print(f"开始时间: {datetime.now()}")

# 获取所有股票
print("\n📊 获取股票列表...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
total_stocks = len(stock_df)
print(f"   总计: {total_stocks} 只股票")

# 处理所有股票
all_data = []
total_records = 0
processed = 0

for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    name = row['name']
    
    if i % 50 == 1 or i == total_stocks:
        print(f"\n[{i}/{total_stocks}] {ts_code} {name}")
    
    try:
        # 获取周线数据
        df = pro.weekly(
            ts_code=ts_code,
            start_date='20160101',
            end_date='20250324'
        )
        
        if df is not None and not df.empty:
            df = df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'vol': 'volume'
            })
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            all_data.append(df)
            total_records += len(df)
            processed += 1
            
            if i % 50 == 0:
                print(f"   ✅ {len(df)} 条 (累计 {total_records:,})")
        
    except Exception as e:
        print(f"   ❌ {str(e)[:50]}")
    
    # 请求间隔
    time.sleep(0.2)
    
    # 每 100 只保存一次
    if i % 100 == 0 and all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        
        if i == 100:
            batch_df.to_csv(CSV_PATH, index=False, mode='w')
            print(f"\n💾 首次保存 {len(batch_df):,} 条")
        else:
            batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
            print(f"\n💾 追加保存 {len(batch_df):,} 条 (累计 {total_records:,})")
        
        all_data = []
        print(f"📊 进度: {i}/{total_stocks} ({i/total_stocks*100:.1f}%)")

# 保存剩余
if all_data:
    batch_df = pd.concat(all_data, ignore_index=True)
    if total_stocks <= 100:
        batch_df.to_csv(CSV_PATH, index=False, mode='w')
    else:
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
    print(f"\n💾 最终保存 {len(batch_df):,} 条")

print(f"\n" + "="*70)
print("✅ 周线数据下载完成")
print(f"CSV: {CSV_PATH}")
print(f"成功: {processed}/{total_stocks}")
print(f"总记录: {total_records:,}")
print(f"结束时间: {datetime.now()}")
print("="*70)
