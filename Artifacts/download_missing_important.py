#!/usr/bin/env python3
"""
下载缺失的重要接口
优先级：分红送股、每日指标、每日股本、财务审计、主营业务
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
print("下载缺失的重要接口")
print("="*70)

# 1. 分红送股数据 (dividend)
print("\n1️⃣  分红送股数据 (dividend)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_dividend.csv"

try:
    df = pro.dividend(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    time.sleep(5)

# 2. 每日股本 (daily_basic)
print("\n2️⃣  每日股本 (daily_basic)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_daily_basic.csv"

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
print(f"   总计 {len(stock_df)} 只股票")

if os.path.exists(CSV_PATH):
    existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
    completed = set(existing['ts_code'].unique()) if 'ts_code' in existing.columns else set()
    stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
    print(f"   已完成: {len(completed)} 只，剩余: {len(stock_df)} 只")

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    if i % 100 == 1:
        print(f"   [{i}/{len(stock_df)}] {row['ts_code']}")
    
    try:
        df = pro.daily_basic(ts_code=row['ts_code'], start_date='20160101', end_date='20250324')
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            print("\n   ⛔ API限制，等待30秒...")
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

# 3. 财务审计意见 (fina_audit)
print("\n3️⃣  财务审计意见 (fina_audit)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_audit.csv"

try:
    df = pro.fina_audit(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 4. 主营业务构成 (fina_mainbz)
print("\n4️⃣  主营业务构成 (fina_mainbz)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_mainbz.csv"

try:
    df = pro.fina_mainbz(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 5. 股票曾用名 (namechange)
print("\n5️⃣  股票曾用名 (namechange)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_namechange.csv"

try:
    df = pro.namechange(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv(CSV_PATH, index=False)
        print(f"   ✅ 完成: {len(df):,} 条")
    else:
        print(f"   ⚠️  无数据")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "="*70)
print("重要接口下载完成！")
print("="*70)
