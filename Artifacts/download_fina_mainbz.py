#!/usr/bin/env python3
"""
下载主营业务构成 (fina_mainbz)
支持续传
"""
import pandas as pd
import tushare as ts
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

CSV_PATH = "E:/Quant_Production/Inbox/tushare_fina_mainbz.csv"

print("="*70)
print("下载主营业务构成 (fina_mainbz)")
print("="*70)

# 获取股票列表
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
print(f"总计 {len(stock_df)} 只股票")

# 检查已有进度
if os.path.exists(CSV_PATH):
    try:
        existing = pd.read_csv(CSV_PATH, low_memory=False)
        completed = set(existing['ts_code'].unique()) if 'ts_code' in existing.columns else set()
        stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
        print(f"已完成: {len(completed)} 只，剩余: {len(stock_df)} 只")
    except:
        pass

all_data = []
batch_size = 100

for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    if i % 100 == 1:
        print(f"[{i}/{len(stock_df)}] {row['ts_code']}")
    
    try:
        df = pro.fina_mainbz(ts_code=row['ts_code'])
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            print("\n⛔ API限制，等待30秒...")
            time.sleep(30)
    
    time.sleep(0.1)
    
    # 每100只保存一次
    if i % batch_size == 0 and all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
        print(f"💾 保存 {len(batch):,} 条")
        all_data = []

# 保存最后一批
if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

print("\n" + "="*70)
print("下载完成！")
print("="*70)
