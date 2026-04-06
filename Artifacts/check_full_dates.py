#!/usr/bin/env python3
"""
检查完整CSV的日期问题
"""
import pandas as pd

print("="*70)
print("检查完整CSV的日期问题")
print("="*70)

base_path = "E:/Quant_Production/Inbox/"

for file, name in [('tushare_weekly.csv', 'weekly'), ('tushare_monthly.csv', 'monthly')]:
    print(f"\n{name}:")
    path = base_path + file
    
    try:
        # 使用chunksize读取整个文件
        total_rows = 0
        null_dates = 0
        
        print(f"  开始读取整个文件...")
        for i, chunk in enumerate(pd.read_csv(path, chunksize=100000, low_memory=False)):
            total_rows += len(chunk)
            
            # 检查日期
            if 'date' in chunk.columns:
                chunk['parsed'] = pd.to_datetime(chunk['date'], errors='coerce')
                null_dates += chunk['parsed'].isnull().sum()
            
            if (i + 1) % 10 == 0:
                print(f"    已读取 {total_rows:,} 行, 无效日期: {null_dates:,}")
        
        print(f"\n  总计:")
        print(f"    总行数: {total_rows:,}")
        print(f"    无效日期: {null_dates:,} ({null_dates/total_rows*100:.2f}%)")
        print(f"    有效数据: {total_rows - null_dates:,}")
                
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "="*70)
