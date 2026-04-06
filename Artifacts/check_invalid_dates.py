#!/usr/bin/env python3
"""
检查weekly和monthly中的无效日期
"""
import pandas as pd

print("="*70)
print("检查无效日期")
print("="*70)

base_path = "E:/Quant_Production/Inbox/"

for csv_file in ['tushare_weekly.csv', 'tushare_monthly.csv']:
    print(f"\n{csv_file}:")
    path = base_path + csv_file
    
    try:
        # 读取前10万行检查
        df = pd.read_csv(path, nrows=100000, low_memory=False)
        print(f"  读取行数: {len(df)}")
        
        # 解析日期
        df['parsed_date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 统计
        valid = df['parsed_date'].notna().sum()
        invalid = df['parsed_date'].isna().sum()
        
        print(f"  有效日期: {valid:,}")
        print(f"  无效日期: {invalid:,} ({invalid/len(df)*100:.2f}%)")
        
        if invalid > 0:
            print(f"  无效日期样本:")
            print(f"    {df[df['parsed_date'].isna()]['date'].head(10).tolist()}")
            
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "="*70)
