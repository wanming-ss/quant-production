#!/usr/bin/env python3
"""
下载剩余重要接口
dividend, trade_cal, pledge_stat, pledge_detail, repurchase, stk_restricted
"""
import pandas as pd
import tushare as ts
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

print("="*70)
print("下载剩余重要接口")
print("="*70)

# 1. 交易日历 (trade_cal)
print("\n1. 交易日历 (trade_cal)...")
try:
    df = pro.trade_cal(start_date='20160101', end_date='20251231')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_trade_cal.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

# 2. 分红送股数据 (dividend)
print("\n2. 分红送股数据 (dividend)...")
try:
    df = pro.dividend(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_dividend.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

# 3. 股权质押统计 (pledge_stat)
print("\n3. 股权质押统计 (pledge_stat)...")
try:
    df = pro.pledge_stat(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_pledge_stat.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

# 4. 股权质押明细 (pledge_detail)
print("\n4. 股权质押明细 (pledge_detail)...")
try:
    df = pro.pledge_detail(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_pledge_detail.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

# 5. 股票回购 (repurchase)
print("\n5. 股票回购 (repurchase)...")
try:
    df = pro.repurchase(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_repurchase.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

# 6. 限售股解禁 (stk_restricted)
print("\n6. 限售股解禁 (stk_restricted)...")
try:
    df = pro.stk_restricted(ts_code='', start_date='20160101', end_date='20250324')
    if df is not None and not df.empty:
        df.to_csv("E:/Quant_Production/Inbox/tushare_stk_restricted.csv", index=False)
        print(f"   OK: {len(df):,} 条")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
print("完成!")
print("="*70)
