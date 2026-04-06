#!/usr/bin/env python3
"""
数据完整性验证
检查年份覆盖、股票数量、数据量
"""
import pandas as pd
import os

print("="*70)
print("数据完整性验证")
print("="*70)

# 关键文件检查
files = {
    '日线': 'E:/Quant_Production/Inbox/tushare_all_2016_2025.csv',
    '周线': 'E:/Quant_Production/Inbox/tushare_weekly.csv',
    '月线': 'E:/Quant_Production/Inbox/tushare_monthly.csv',
    '复权因子': 'E:/Quant_Production/Inbox/tushare_adj_factor.csv',
    '财务指标': 'E:/Quant_Production/Inbox/tushare_fina_indicator.csv',
    '每日股本': 'E:/Quant_Production/Inbox/tushare_daily_basic.csv',
}

for name, path in files.items():
    print(f"\n{name}:")
    if not os.path.exists(path):
        print(f"   ❌ 文件不存在")
        continue
    
    try:
        # 读取样本数据
        df = pd.read_csv(path, nrows=1000, low_memory=False)
        size_mb = os.path.getsize(path) / 1024 / 1024
        
        print(f"   ✅ 大小: {size_mb:.1f} MB")
        print(f"   ✅ 列数: {len(df.columns)}")
        
        # 检查日期范围
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            print(f"   ✅ 日期样本: {df['trade_date'].min()} ~ {df['trade_date'].max()}")
        
        # 检查股票数量
        if 'ts_code' in df.columns:
            print(f"   ✅ 股票样本数: {df['ts_code'].nunique()}")
            
    except Exception as e:
        print(f"   ⚠️  错误: {str(e)[:50]}")

print("\n" + "="*70)
print("验证完成!")
print("="*70)
