import pandas as pd
import os

print("=== 数据完整性验证 ===\n")

# 检查日线
df = pd.read_csv('E:/Quant_Production/Inbox/tushare_all_2016_2025.csv', nrows=50000, low_memory=False)
df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')

print("日线数据:")
print(f"  样本股票数: {df['ts_code'].nunique()}")
print(f"  日期范围: {df['trade_date'].min()} ~ {df['trade_date'].max()}")
print(f"  列数: {len(df.columns)}")
print(f"  总大小: {os.path.getsize('E:/Quant_Production/Inbox/tushare_all_2016_2025.csv')/1024/1024:.1f} MB")

# 检查每日股本
df2 = pd.read_csv('E:/Quant_Production/Inbox/tushare_daily_basic.csv', nrows=50000, low_memory=False)
df2['trade_date'] = pd.to_datetime(df2['trade_date'], errors='coerce')

print("\n每日股本:")
print(f"  样本股票数: {df2['ts_code'].nunique()}")
print(f"  日期范围: {df2['trade_date'].min()} ~ {df2['trade_date'].max()}")
print(f"  总大小: {os.path.getsize('E:/Quant_Production/Inbox/tushare_daily_basic.csv')/1024/1024:.1f} MB")

print("\n=== 完成 ===")
