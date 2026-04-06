#!/usr/bin/env python3
"""
Tushare 全接口批量下载
按优先级逐个下载所有接口
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

# 定义所有接口（按优先级排序）
APIS = [
    # 已完成的核心数据
    # ('daily', 'tushare_all_2016_2025.csv', 'daily'),
    # ('weekly', 'tushare_weekly.csv', 'weekly'),
    # ('monthly', 'tushare_monthly.csv', 'monthly'),
    # ('adj_factor', 'tushare_adj_factor.csv', 'adj_factor'),
    
    # 财务数据（优先级1）
    ('income', 'tushare_income.csv', 'financial'),
    ('balancesheet', 'tushare_balancesheet.csv', 'financial'),
    ('cashflow', 'tushare_cashflow.csv', 'financial'),
    ('fina_indicator', 'tushare_fina_indicator.csv', 'financial'),
    ('forecast', 'tushare_forecast.csv', 'financial'),
    ('express', 'tushare_express.csv', 'financial'),
    
    # 市场数据（优先级2）
    ('moneyflow', 'tushare_moneyflow.csv', 'market'),
    ('limit_list', 'tushare_limit_list.csv', 'market'),
    ('top_list', 'tushare_top_list.csv', 'market'),
    ('top_inst', 'tushare_top_inst.csv', 'market'),
    ('stk_holdernumber', 'tushare_holdernumber.csv', 'market'),
    ('stk_holdertrade', 'tushare_holdertrade.csv', 'market'),
    
    # 股本相关（优先级3）
    ('stk_pledge', 'tushare_stk_pledge.csv', 'equity'),
    ('stk_pledge_detail', 'tushare_stk_pledge_detail.csv', 'equity'),
    ('stk_reward', 'tushare_stk_reward.csv', 'equity'),
    ('new_share', 'tushare_new_share.csv', 'equity'),
    
    # 其他（优先级4）
    ('block_trade', 'tushare_block_trade.csv', 'other'),
    ('stk_limit', 'tushare_stk_limit.csv', 'other'),
    ('suspend', 'tushare_suspend.csv', 'other'),
    ('suspend_d', 'tushare_suspend_d.csv', 'other'),
]

def download_api(api_name, csv_name, category):
    """下载单个接口"""
    CSV_PATH = f"E:/Quant_Production/Inbox/{csv_name}"
    
    print(f"\n{'='*70}")
    print(f"下载: {api_name} ({category})")
    print(f"{'='*70}")
    print(f"开始: {datetime.now()}")
    
    # 获取股票列表
    stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    
    # 检查已有数据
    if os.path.exists(CSV_PATH):
        try:
            existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
            if 'ts_code' in existing.columns:
                completed = set(existing['ts_code'].unique())
            elif 'symbol' in existing.columns:
                completed = set(existing['symbol'].unique())
            else:
                completed = set()
            stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
            print(f"已完成: {len(completed)} 只")
        except:
            pass
    
    remaining = len(stock_df)
    print(f"剩余: {remaining} 只")
    
    if remaining == 0:
        print("✅ 跳过（已完成）")
        return True
    
    # 下载数据
    all_data = []
    total_new = 0
    
    for i, (_, row) in enumerate(stock_df.iterrows(), 1):
        ts_code = row['ts_code']
        
        if i % 50 == 1:
            print(f"\n[{i}/{remaining}] {ts_code}")
        
        try:
            # 调用 API
            if api_name in ['income', 'balancesheet', 'cashflow', 'fina_indicator']:
                # 财务数据有季度数据
                df = getattr(pro, api_name)(ts_code=ts_code, start_date='20160101', end_date='20250324')
            elif api_name in ['forecast', 'express']:
                # 业绩预告/快报按日期
                df = getattr(pro, api_name)(ts_code=ts_code)
            elif api_name in ['limit_list', 'top_list', 'top_inst']:
                # 这些按日期，不循环股票
                continue
            else:
                df = getattr(pro, api_name)(ts_code=ts_code, start_date='20160101', end_date='20250324')
            
            if df is not None and not df.empty:
                all_data.append(df)
                total_new += len(df)
                
                if i % 50 == 0:
                    print(f"   ✅ +{total_new:,}")
        
        except Exception as e:
            if "500次" in str(e) or "IP数量" in str(e):
                print(f"\n⛔ API限制，保存进度并退出")
                if all_data:
                    batch = pd.concat(all_data, ignore_index=True)
                    batch.to_csv(CSV_PATH, index=False, mode='a', header=False)
                return False
        
        time.sleep(0.3)
        
        if i % 100 == 0 and all_data:
            batch = pd.concat(all_data, ignore_index=True)
            batch.to_csv(CSV_PATH, index=False, mode='a', header=False)
            print(f"\n💾 保存 {len(batch):,} 条")
            all_data = []
            print(f"📊 {i}/{remaining} ({i/remaining*100:.1f}%)")
    
    # 保存剩余
    if all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=False)
    
    print(f"\n✅ {api_name} 完成")
    return True

# 主程序
print("="*70)
print("Tushare 全接口批量下载")
print("="*70)
print(f"开始时间: {datetime.now()}")
print(f"总计: {len(APIS)} 个接口")
print("="*70)

completed = 0
failed = []

for i, (api, csv, cat) in enumerate(APIS, 1):
    print(f"\n\n{'#'*70}")
    print(f"# 进度: {i}/{len(APIS)} - {api}")
    print(f"{'#'*70}")
    
    success = download_api(api, csv, cat)
    
    if success:
        completed += 1
        print(f"\n✅ {api} 成功")
    else:
        failed.append(api)
        print(f"\n❌ {api} 失败（API限制）")
        print("等待 60 秒后继续...")
        time.sleep(60)

print("\n" + "="*70)
print("批量下载完成")
print(f"成功: {completed}/{len(APIS)}")
print(f"失败: {failed}")
print(f"结束时间: {datetime.now()}")
print("="*70)
