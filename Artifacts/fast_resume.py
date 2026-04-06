#!/usr/bin/env python3
"""
快速续传 - 单接口慢速模式
每 0.3 秒请求一次
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os
import sys

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

def fast_resume(api_name, csv_name, rename_cols):
    CSV_PATH = f"E:/Quant_Production/Inbox/{csv_name}"
    
    print(f"\n{'='*70}")
    print(f"快速续传: {api_name}")
    print(f"{'='*70}")
    print(f"开始: {datetime.now()}")
    
    # 获取未完成股票
    stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH, low_memory=False)
        completed_stocks = set(existing_df['symbol'].unique() if 'symbol' in existing_df.columns else existing_df['ts_code'].unique())
        stock_df = stock_df[~stock_df['ts_code'].isin(completed_stocks)]
    
    remaining = len(stock_df)
    print(f"剩余: {remaining} 只")
    
    if remaining == 0:
        print("✅ 完成！")
        return
    
    all_data = []
    total_new = 0
    
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        name = row['name']
        
        if i % 20 == 1:
            print(f"\n[{i}/{remaining}] {ts_code}")
        
        try:
            if api_name == 'weekly':
                df = pro.weekly(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name == 'monthly':
                df = pro.monthly(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name == 'adj_factor':
                df = pro.adj_factor(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name == 'moneyflow':
                df = pro.moneyflow(ts_code=ts_code, start_date='20160101', end_date='20250324')
            
            if df is not None and not df.empty:
                df = df.rename(columns=rename_cols)
                if 'trade_date' in df.columns:
                    df['date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                all_data.append(df)
                total_new += len(df)
                
                if i % 20 == 0:
                    print(f"   ✅ +{total_new:,}")
        
        except Exception as e:
            if "500次" in str(e):
                print(f"\n⛔ API限制，等待30秒...")
                time.sleep(30)
        
        time.sleep(0.3)
        
        if i % 50 == 0 and all_data:
            batch_df = pd.concat(all_data, ignore_index=True)
            batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
            print(f"\n💾 保存 {len(batch_df):,} 条")
            all_data = []
            print(f"📊 {i}/{remaining} ({i/remaining*100:.1f}%)")
    
    if all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
    
    print(f"\n✅ {api_name} 完成")
    print(f"结束: {datetime.now()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fast_resume.py [weekly|monthly|adj_factor|moneyflow]")
        sys.exit(1)
    
    api = sys.argv[1]
    
    if api == 'weekly':
        fast_resume('weekly', 'tushare_weekly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'monthly':
        fast_resume('monthly', 'tushare_monthly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'adj_factor':
        fast_resume('adj_factor', 'tushare_adj_factor.csv', {'ts_code': 'symbol', 'trade_date': 'date'})
    elif api == 'moneyflow':
        fast_resume('moneyflow', 'tushare_moneyflow.csv', {'ts_code': 'ts_code', 'trade_date': 'trade_date'})
    else:
        print(f"未知: {api}")
