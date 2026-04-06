#!/usr/bin/env python3
"""
检查weekly和monthly的日期数据
"""
import pandas as pd

print("="*70)
print("检查weekly和monthly的日期数据")
print("="*70)

base_path = "E:/Quant_Production/Inbox/"

for file, name in [('tushare_weekly.csv', 'weekly'), ('tushare_monthly.csv', 'monthly')]:
    print(f"\n{name}:")
    path = base_path + file
    
    try:
        # 读取前1000行检查
        df = pd.read_csv(path, nrows=5000, low_memory=False)
        print(f"  总行数: {len(df)}")
        print(f"  列名: {df.columns.tolist()}")
        
        # 检查日期列
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        print(f"  日期列: {date_cols}")
        
        if date_cols:
            date_col = date_cols[0]
            print(f"  日期列 '{date_col}':")
            print(f"    样本值: {df[date_col].head(10).tolist()}")
            print(f"    空值数: {df[date_col].isnull().sum()}")
            print(f"    唯一值数: {df[date_col].nunique()}")
            
            # 尝试解析日期
            try:
                df['parsed_date'] = pd.to_datetime(df[date_col], errors='coerce')
                null_dates = df['parsed_date'].isnull().sum()
                print(f"    解析后无效日期: {null_dates} ({null_dates/len(df)*100:.1f}%)")
            except Exception as e:
                print(f"    日期解析错误: {e}")
                
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "="*70)
