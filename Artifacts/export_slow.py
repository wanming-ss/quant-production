#!/usr/bin/env python3
"""
Tushare 慢速导出 - 避免 IP 限制
每 0.5 秒请求一次，处理剩余 2,063 只
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import sys

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 慢速导出 - 避免 IP 限制")
print("="*70)
print(f"开始时间: {datetime.now()}")

# 读取已有 CSV
print("\n📊 检查已有数据...")
existing_df = pd.read_csv(CSV_PATH)
completed_stocks = set(existing_df['symbol'].unique())
print(f"   已完成: {len(completed_stocks)} 只股票")

# 获取所有股票
print("\n📊 获取股票列表...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

# 过滤已完成的
remaining_df = stock_df[~stock_df['ts_code'].isin(completed_stocks)]
remaining = len(remaining_df)
print(f"   剩余: {remaining} 只股票")

if remaining == 0:
    print("\n✅ 所有股票已导出完成！")
    sys.exit(0)

# 处理剩余股票（慢速模式）
all_data = []
total_new = 0
processed = 0
failed = []

for i, (_, row) in enumerate(remaining_df.iterrows(), 1):
    ts_code = row['ts_code']
    name = row['name']
    
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
            print(f"   ✅ {len(df)} 条")
        else:
            print(f"   ⚠️ 无数据")
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ {error_msg[:80]}")
        if "IP数量超限" in error_msg:
            print(f"\n⛔ IP 限制触发，保存当前进度...")
            break
        failed.append(ts_code)
    
    # 慢速间隔（0.5 秒）
    time.sleep(0.5)
    
    # 每 20 只保存一次
    if i % 20 == 0 and all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
        print(f"\n💾 保存 {len(batch_df):,} 条 (累计 +{total_new:,})")
        all_data = []
        print(f"📊 进度: {i}/{remaining} ({i/remaining*100:.1f}%)")

# 保存剩余
if all_data:
    batch_df = pd.concat(all_data, ignore_index=True)
    batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
    print(f"\n💾 最终保存 {len(batch_df):,} 条")

# 统计
final_df = pd.read_csv(CSV_PATH)
print(f"\n" + "="*70)
print("导出完成")
print(f"本次成功: {processed} 只")
print(f"本次失败: {len(failed)} 只")
print(f"总计: {final_df['symbol'].nunique()} 只股票, {len(final_df):,} 条记录")
print(f"结束时间: {datetime.now()}")
print("="*70)
