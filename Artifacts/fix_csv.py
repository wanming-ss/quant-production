#!/usr/bin/env python3
"""
修复损坏的 CSV 文件
"""
import pandas as pd

# 修复 moneyflow
print("修复 moneyflow...")
input_file = "E:/Quant_Production/Inbox/tushare_moneyflow.csv"
output_file = "E:/Quant_Production/Inbox/tushare_moneyflow_fixed.csv"

# 读取有效行
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 获取表头
header = lines[0].strip().split(',')
print(f"表头: {header}")
print(f"期望列数: {len(header)}")

# 过滤有效行
valid_lines = [lines[0]]  # 保留表头
for i, line in enumerate(lines[1:], 1):
    cols = line.strip().split(',')
    if len(cols) == len(header):
        valid_lines.append(line)
    elif i % 10000 == 0:
        print(f"处理到第 {i} 行，有效行 {len(valid_lines)-1}")

# 保存修复后的文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(valid_lines)

print(f"\n修复完成:")
print(f"  原文件行数: {len(lines)}")
print(f"  有效行数: {len(valid_lines)}")
print(f"  删除行数: {len(lines) - len(valid_lines)}")
print(f"  输出: {output_file}")

# 验证
df = pd.read_csv(output_file, low_memory=False)
print(f"\n验证: {len(df):,} 条记录")
