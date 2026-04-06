#!/usr/bin/env python3
"""
Tushare 数据下载 - 慢速续传（避免 API 限制）
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os
import sys

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

def download_slow(api_name, csv_name, rename_cols):
    """慢速下载（0.5秒间隔）"""
    CSV_PATH = f"E:/Quant_Production/Inbox/{csv_name}"
    
    print("="*70)
    print(f"Tushare {api_name} 数据下载 - 慢速续传")
    print("="*70)
    print(f"开始时间: {datetime.now()}")
    
    # 获取股票列表
    print("\n📊 获取股票列表...")
    stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    total_stocks = len(stock_df)
    print(f"   总计: {total_stocks} 只股票")
    
    # 检查已有数据
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH)
        completed_stocks = set(existing_df['symbol'].unique())
        print(f"   已完成: {len(completed_stocks)} 只")
        stock_df = stock_df[~stock_df['ts_code'].isin(completed_stocks)]
    
    remaining = len(stock_df)
    print(f"   剩余: {remaining} 只")
    
    if remaining == 0:
        print("\n✅ 所有数据已下载完成！")
        return
    
    # 慢速下载
    all_data = []
    total_new = 0
    processed = 0
    failed = []
    
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        name = row['name']
        
        if i % 20 == 1:
            print(f"\n[{i}/{remaining}] {ts_code} {name}")
        
        try:
            if api_name == 'weekly':
                df = pro.weekly(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name == 'monthly':
                df = pro.monthly(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name == 'adj_factor':
                df = pro.adj_factor(ts_code=ts_code, start_date='20160101', end_date='20250324')
            
            if df is not None and not df.empty:
                df = df.rename(columns=rename_cols)
                if 'trade_date' in df.columns:
                    df['date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                all_data.append(df)
                total_new += len(df)
                processed += 1
                
                if i % 20 == 0:
                    print(f"   ✅ {len(df)} 条 (累计 +{total_new:,})")
            
        except Exception as e:
            error = str(e)
            print(f"   ❌ {error[:60]}")
            if "500次" in error:
                print("\n⛔ API 限制，等待 60 秒...")
                time.sleep(60)
                continue
            failed.append(ts_code)
        
        # 慢速间隔（0.5秒）
        time.sleep(0.5)
        
        # 每 50 只保存一次
        if i % 50 == 0 and all_data:
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
    
    print(f"\n" + "="*70)
    print(f"✅ {api_name} 完成")
    print(f"成功: {processed}, 失败: {len(failed)}")
    print(f"结束时间: {datetime.now()}")
    print("="*70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download_slow.py [weekly|monthly|adj_factor]")
        sys.exit(1)
    
    api = sys.argv[1]
    
    if api == 'weekly':
        download_slow('weekly', 'tushare_weekly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'monthly':
        download_slow('monthly', 'tushare_monthly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'adj_factor':
        download_slow('adj_factor', 'tushare_adj_factor.csv', {'ts_code': 'symbol', 'trade_date': 'date'})
    else:
        print(f"未知的 API: {api}")
        sys.exit(1)
