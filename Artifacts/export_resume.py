#!/usr/bin/env python3
"""
Tushare 全量导出 - 续传模式
从第 901 只继续导出，追加到已有 CSV
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
BATCH_SIZE = 100

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 全量导出 - 续传模式")
print("="*70)
print(f"开始时间: {datetime.now()}")

# 读取已有 CSV 获取已完成的股票
print("\n📊 检查已有数据...")
if os.path.exists(CSV_PATH):
    existing_df = pd.read_csv(CSV_PATH)
    completed_stocks = set(existing_df['symbol'].unique())
    print(f"   已完成: {len(completed_stocks)} 只股票")
    print(f"   已有记录: {len(existing_df):,} 条")
else:
    completed_stocks = set()
    print("   无已有数据")

# 获取所有股票
print("\n📊 获取股票列表...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
total_stocks = len(stock_df)
print(f"   总计: {total_stocks} 只股票")

# 过滤已完成的
remaining_df = stock_df[~stock_df['ts_code'].isin(completed_stocks)]
remaining = len(remaining_df)
print(f"   剩余: {remaining} 只股票")

if remaining == 0:
    print("\n✅ 所有股票已导出完成！")
    exit(0)

# 处理剩余股票
all_data = []
total_new = 0
processed = 0

for i, (_, row) in enumerate(remaining_df.iterrows(), 1):
    ts_code = row['ts_code']
    name = row['name']
    
    if i % 10 == 1:
        print(f"\n[{i}/{remaining}] {ts_code} {name}")
    
    try:
        df = pro.daily(
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
            total_new += len(df)
            processed += 1
            
            if i % 10 == 0:
                print(f"   ✅ {len(df)} 条 (累计 +{total_new:,})")
        
    except Exception as e:
        print(f"   ❌ {str(e)[:50]}")
    
    time.sleep(0.08)
    
    # 每 BATCH_SIZE 保存一次
    if i % BATCH_SIZE == 0 and all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
        print(f"\n💾 追加保存 {len(batch_df):,} 条 (新累计 +{total_new:,})")
        all_data = []
        print(f"📊 进度: {i}/{remaining} ({i/remaining*100:.1f}%)")

# 保存剩余
if all_data:
    batch_df = pd.concat(all_data, ignore_index=True)
    batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
    print(f"\n💾 最终追加 {len(batch_df):,} 条")

# 统计
final_df = pd.read_csv(CSV_PATH)
print(f"\n" + "="*70)
print("✅ 续传导出完成")
print(f"CSV: {CSV_PATH}")
print(f"本次新增: {processed} 只股票, {total_new:,} 条记录")
print(f"总计: {final_df['symbol'].nunique()} 只股票, {len(final_df):,} 条记录")
print(f"结束时间: {datetime.now()}")
print("="*70)
