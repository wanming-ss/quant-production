#!/usr/bin/env python3
"""
下载需要按股票的接口
fina_audit, fina_mainbz
"""
import pandas as pd
import tushare as ts
import time

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

print("="*70)
print("下载需要按股票的接口")
print("="*70)

# 获取股票列表
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
print(f"总计 {len(stock_df)} 只股票\n")

# 1. 财务审计意见
print("1️⃣  财务审计意见 (fina_audit)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_audit.csv"

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    if i % 500 == 1:
        print(f"   [{i}/{len(stock_df)}] {row['ts_code']}")
    
    try:
        df = pro.fina_audit(ts_code=row['ts_code'])
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        pass
    
    time.sleep(0.1)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

# 2. 主营业务构成
print("\n2️⃣  主营业务构成 (fina_mainbz)...")
CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_mainbz.csv"

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    if i % 500 == 1:
        print(f"   [{i}/{len(stock_df)}] {row['ts_code']}")
    
    try:
        df = pro.fina_mainbz(ts_code=row['ts_code'])
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        pass
    
    time.sleep(0.1)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False)
    print(f"   ✅ 完成: {len(batch):,} 条")

print("\n" + "="*70)
print("下载完成！")
print("="*70)
