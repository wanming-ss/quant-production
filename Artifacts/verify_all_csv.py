#!/usr/bin/env python3
"""
验证所有 CSV 文件数据量
"""
import pandas as pd
import os

files = {
    'tushare_weekly.csv': 'symbol',
    'tushare_monthly.csv': 'symbol', 
    'tushare_adj_factor.csv': 'symbol',
    'tushare_moneyflow.csv': 'ts_code',
    'tushare_limit_list.csv': 'ts_code',
    'tushare_fina_indicator.csv': 'ts_code'
}

print("="*70)
print("各 CSV 文件数据量验证")
print("="*70)

for fname, id_col in files.items():
    path = f'E:/Quant_Production/Inbox/{fname}'
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, low_memory=False)
            print(f"\n{fname}:")
            print(f"  记录数: {len(df):,} 条")
            if id_col in df.columns:
                print(f"  {id_col}数: {df[id_col].nunique()} 只")
        except Exception as e:
            print(f"\n{fname}: 读取错误 - {e}")
    else:
        print(f"\n{fname}: 不存在")

print("\n" + "="*70)
