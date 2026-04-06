#!/usr/bin/env python3
"""
Tushare 全历史数据导出
使用 Tushare pro_bar 接口获取全部历史数据
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

# 获取股票列表（包含上市日期）
print("\n📊 获取股票列表及上市日期...")
stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,list_date')
print(f"📝 总计 {len(stock_df)} 只股票")

# 只取前10只测试（避免时间过长）
stock_df = stock_df.head(10)
print(f"⚡ 测试模式: 前 {len(stock_df)} 只股票")

all_data = []
total_records = 0

for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    list_date = row['list_date']  # 上市日期
    
    print(f"\n[{i}/{len(stock_df)}] {ts_code} (上市: {list_date})")
    
    try:
        # 使用 pro_bar 获取全部历史数据
        # 参数: ts_code, pro_api, start_date, end_date, freq='D', asset='E'
        df = ts.pro_bar(
            ts_code=ts_code,
            pro_api=pro,
            start_date=list_date,
            end_date='20250324',
            freq='D',
            asset='E'
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
            total_records += len(df)
            print(f"  ✅ 获取 {len(df)} 条数据 (累计 {total_records})")
        else:
            print(f"  ⚠️ 无数据")
        
    except Exception as e:
        print(f"  ❌ 失败: {str(e)[:100]}")
    
    import time
    time.sleep(0.2)  # 请求间隔

# 保存 CSV
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
    
    print(f"\n" + "="*70)
    print("✅ 导出完成")
    print(f"CSV: {CSV_PATH}")
    print(f"记录数: {len(combined):,}")
    print(f"股票数: {combined['symbol'].nunique()}")
    print(f"日期范围: {combined['date'].min()} ~ {combined['date'].max()}")
    print(f"\n各股票数据量:")
    print(combined.groupby('symbol').size().sort_values(ascending=False))
    print("="*70)
