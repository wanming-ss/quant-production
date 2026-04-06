#!/usr/bin/env python3
"""
Tushare 2016-2025 数据导出
约 10 年历史数据
"""
import pandas as pd
import tushare as ts
from datetime import datetime

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_2016_2025.csv"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 2016-2025 数据导出")
print("="*70)

# 获取股票列表
print("\n📊 获取股票列表...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
print(f"📝 总计 {len(stock_df)} 只股票")

# 测试50只
test_stocks = stock_df.head(50)
print(f"⚡ 导出前 {len(test_stocks)} 只 (2016-2025)")

all_data = []

for i, (_, row) in enumerate(test_stocks.iterrows(), 1):
    ts_code = row['ts_code']
    name = row['name']
    
    if i % 10 == 1:
        print(f"\n[{i}/{len(test_stocks)}] {ts_code} {name}")
    
    try:
        # 获取 2016-2025 数据
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
            
            if i % 10 == 0:
                print(f"   ✅ {len(df)} 条")
        
    except Exception as e:
        print(f"   ❌ {str(e)[:50]}")
    
    import time
    time.sleep(0.1)

# 保存
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
    
    print(f"\n" + "="*70)
    print("✅ 导出完成")
    print(f"CSV: {CSV_PATH}")
    print(f"股票数: {combined['symbol'].nunique()}")
    print(f"总记录: {len(combined):,}")
    print(f"日期范围: {combined['date'].min().date()} ~ {combined['date'].max().date()}")
    print(f"平均每只: {len(combined) // combined['symbol'].nunique()} 条")
    print("="*70)
