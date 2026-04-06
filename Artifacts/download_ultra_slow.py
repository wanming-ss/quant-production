#!/usr/bin/env python3
"""
Tushare 数据下载 - 超慢速续传（1秒间隔，自动重试）
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

def download_ultra_slow(api_name, csv_name, rename_cols):
    """超慢速下载（1秒间隔）"""
    CSV_PATH = f"E:/Quant_Production/Inbox/{csv_name}"
    
    print("="*70)
    print(f"Tushare {api_name} 数据下载 - 超慢速续传")
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
    
    # 超慢速下载
    all_data = []
    total_new = 0
    processed = 0
    failed = []
    api_limit_count = 0
    
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        name = row['name']
        
        if i % 10 == 1:
            print(f"\n[{i}/{remaining}] {ts_code} {name}")
        
        # 重试机制
        retry = 0
        success = False
        
        while retry < 3 and not success:
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
                    success = True
                    
                    if i % 10 == 0:
                        print(f"   ✅ {len(df)} 条 (累计 +{total_new:,})")
                else:
                    success = True  # 无数据也算成功
                    
            except Exception as e:
                error = str(e)
                if "500次" in error or "IP数量" in error:
                    api_limit_count += 1
                    if api_limit_count >= 5:
                        print(f"\n⛔ API 限制太频繁，保存进度并退出...")
                        # 保存已有数据
                        if all_data:
                            batch_df = pd.concat(all_data, ignore_index=True)
                            batch_df.to_csv(CSV_PATH, index=False, mode='a', header=False)
                            print(f"💾 保存 {len(batch_df):,} 条")
                        print(f"📊 完成: {i-1}/{remaining}")
                        return
                    wait_time = 30 * (2 ** retry)  # 30, 60, 120秒
                    print(f"\n⛔ API 限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    retry += 1
                else:
                    print(f"   ❌ {error[:60]}")
                    retry += 1
                    time.sleep(2)
        
        if not success:
            failed.append(ts_code)
        
        # 超慢速间隔（1秒）
        time.sleep(1)
        
        # 每 30 只保存一次
        if i % 30 == 0 and all_data:
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
        print("用法: python download_ultra_slow.py [weekly|monthly|adj_factor]")
        sys.exit(1)
    
    api = sys.argv[1]
    
    if api == 'weekly':
        download_ultra_slow('weekly', 'tushare_weekly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'monthly':
        download_ultra_slow('monthly', 'tushare_monthly.csv', {'ts_code': 'symbol', 'trade_date': 'date', 'vol': 'volume'})
    elif api == 'adj_factor':
        download_ultra_slow('adj_factor', 'tushare_adj_factor.csv', {'ts_code': 'symbol', 'trade_date': 'date'})
    else:
        print(f"未知的 API: {api}")
        sys.exit(1)
