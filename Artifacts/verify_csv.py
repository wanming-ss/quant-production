#!/usr/bin/env python3
"""
验证各 CSV 文件数据量
"""
import pandas as pd
import os

files = ['tushare_weekly.csv', 'tushare_monthly.csv', 'tushare_adj_factor.csv']

print("="*70)
print("各 CSV 文件数据量验证")
print("="*70)

for f in files:
    path = f'E:/Quant_Production/Inbox/{f}'
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"\n{f}:")
        print(f"  记录数: {len(df):,} 条")
        print(f"  股票数: {df['symbol'].nunique()} 只")
    else:
        print(f"\n{f}: 不存在")

print("\n" + "="*70)
