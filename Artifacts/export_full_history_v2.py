#!/usr/bin/env python3
"""
Tushare 全历史数据导出
使用 pro.daily 从上市日期获取全部数据
"""
import pandas as pd
import tushare as ts
from datetime import datetime

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_full_history.csv"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 全历史数据导出")
print("="*70)

# 获取股票列表（含上市日期）
print("\n📊 获取股票列表...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,list_date,name')
print(f"📝 总计 {len(stock_df)} 只股票")

# 测试20只（完整导出需要很长时间）
test_stocks = stock_df.head(20)
print(f"⚡ 测试模式: 前 {len(test_stocks)} 只股票")

all_data = []

for i, (_, row) in enumerate(test_stocks.iterrows(), 1):
    ts_code = row['ts_code']
    list_date = row['list_date']
    name = row['name']
    
    print(f"\n[{i}/{len(test_stocks)}] {ts_code} {name}")
    print(f"   上市日期: {list_date} (~{2025-1990}年历史)")
    
    try:
        # 获取从上市至今的全部日线数据
        df = pro.daily(
            ts_code=ts_code,
            start_date=list_date,
            end_date='20250324'
        )
        
        if df is not None and not df.empty:
            # 转换列名
            df = df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'vol': 'volume'
            })
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            
            all_data.append(df)
            
            # 计算历史长度
            days = len(df)
            years = days / 252
            print(f"   ✅ 获取 {days} 条 (~{years:.1f} 年)")
        else:
            print(f"   ⚠️ 无数据")
        
    except Exception as e:
        print(f"   ❌ 失败: {str(e)[:80]}")
    
    import time
    time.sleep(0.15)

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
    
    print(f"\n各股票数据量:")
    summary = combined.groupby('symbol').agg({
        'date': ['count', 'min', 'max']
    }).round(2)
    print(summary)
    print("="*70)
else:
    print("❌ 无数据导出")
