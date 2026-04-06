#!/usr/bin/env python3
"""
多线程补全剩余数据 - 使用多个 Token
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 多个 Token（如果有的话）
TOKENS = [
    "5bb803b4f1bdc5ed7762f89d9109a809",  # 主 Token
    # 可以添加更多 Token
]
URL = "http://119.45.170.23"

# 线程锁
lock = threading.Lock()

def download_stock(ts_code, name, api_name, csv_path, rename_cols, token):
    """下载单只股票数据"""
    try:
        pro = ts.pro_api(token)
        pro._DataApi__token = token
        pro._DataApi__http_url = URL
        
        if api_name == 'weekly':
            df = pro.weekly(ts_code=ts_code, start_date='20160101', end_date='20250324')
        elif api_name == 'monthly':
            df = pro.monthly(ts_code=ts_code, start_date='20160101', end_date='20250324')
        elif api_name == 'adj_factor':
            df = pro.adj_factor(ts_code=ts_code, start_date='20160101', end_date='20250324')
        else:
            return None
        
        if df is not None and not df.empty:
            df = df.rename(columns=rename_cols)
            if 'trade_date' in df.columns:
                df['date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            return df
        
    except Exception as e:
        print(f"   ❌ {ts_code}: {str(e)[:50]}")
    
    return None

def batch_download(api_name, csv_name, rename_cols):
    """批量下载"""
    CSV_PATH = f"E:/Quant_Production/Inbox/{csv_name}"
    
    print(f"\n{'='*70}")
    print(f"批量补全: {api_name}")
    print(f"{'='*70}")
    print(f"开始时间: {datetime.now()}")
    
    # 获取未完成的股票
    print("\n📊 获取未完成股票...")
    pro = ts.pro_api(TOKENS[0])
    pro._DataApi__token = TOKENS[0]
    pro._DataApi__http_url = URL
    
    stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH)
        completed_stocks = set(existing_df['symbol'].unique())
        stock_df = stock_df[~stock_df['ts_code'].isin(completed_stocks)]
    
    remaining = len(stock_df)
    print(f"   剩余: {remaining} 只股票")
    
    if remaining == 0:
        print("\n✅ 所有数据已完成！")
        return
    
    # 由于 API 限制，使用单线程慢速下载
    all_data = []
    total_new = 0
    
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        name = row['name']
        
        if i % 10 == 1:
            print(f"\n[{i}/{remaining}] {ts_code} {name}")
        
        df = download_stock(ts_code, name, api_name, CSV_PATH, rename_cols, TOKENS[0])
        
        if df is not None:
            with lock:
                all_data.append(df)
                total_new += len(df)
            
            if i % 10 == 0:
                print(f"   ✅ {len(df)} 条 (累计 +{total_new:,})")
        
        # 慢速间隔（0.5秒）
        time.sleep(0.5)
        
        # 每 50 只保存一次
        if i % 50 == 0 and all_data:
            with lock:
                batch_df = pd.concat(all_data, ignore_index=True)
                batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
                print(f"\n💾 保存 {len(batch_df):,} 条")
                all_data = []
                print(f"📊 进度: {i}/{remaining} ({i/remaining*100:.1f}%)")
    
    # 保存剩余
    if all_data:
        batch_df = pd.concat(all_data, ignore_index=True)
        batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
        print(f"\n💾 最终保存 {len(batch_df):,} 条")
    
    print(f"\n{'='*70}")
    print(f"✅ {api_name} 补全完成")
    print(f"结束时间: {datetime.now()}")
    print(f"{'='*70}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download_batch.py [weekly|monthly|adj_factor]")
        sys.exit(1)
    
    api = sys.argv[1]
    
    if api == 'weekly':
        batch_download('weekly', 'tushare_weekly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'monthly':
        batch_download('monthly', 'tushare_monthly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'adj_factor':
        batch_download('adj_factor', 'tushare_adj_factor.csv', {'ts_code': 'symbol', 'trade_date': 'date'})
    else:
        print(f"未知的 API: {api}")
        sys.exit(1)
