#!/usr/bin/env python3
"""
下载剩余的4个重要接口
dividend, fina_audit, fina_mainbz, namechange
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

print("="*70)
print("下载剩余4个重要接口")
print("="*70)

apis = [
    ('dividend', '分红送股'),
    ('fina_audit', '财务审计意见'),
    ('fina_mainbz', '主营业务构成'),
    ('namechange', '股票曾用名'),
]

for api_name, desc in apis:
    print(f"\n{desc} ({api_name})...")
    CSV_PATH = f"E:/Quant_Production/Inbox/tushare_{api_name}.csv"
    
    try:
        # 获取函数
        func = getattr(pro, api_name)
        
        # 一次性下载全部
        if api_name in ['dividend', 'fina_audit', 'fina_mainbz']:
            df = func(ts_code='', start_date='20160101', end_date='20250324')
        else:  # namechange
            df = func(start_date='20160101', end_date='20250324')
        
        if df is not None and not df.empty:
            df.to_csv(CSV_PATH, index=False)
            print(f"   ✅ 完成: {len(df):,} 条")
        else:
            print(f"   ⚠️  无数据")
            
    except Exception as e:
        print(f"   ❌ 错误: {str(e)[:50]}")
    
    time.sleep(1)  # API间隔

print("\n" + "="*70)
print("剩余接口下载完成！")
print("="*70)
