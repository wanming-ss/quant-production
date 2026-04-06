#!/usr/bin/env python3
"""
训练模拟 - 使用CSV文件
不依赖DolphinDB
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

print("="*70)
print("训练模拟 - 使用CSV文件")
print("="*70)

base_path = "E:/Quant_Production/Inbox/"

# 1. 读取核心数据
print("\n1. 读取核心数据...")

print("  读取日线数据...")
daily = pd.read_csv(base_path + "tushare_all_2016_2025.csv", nrows=100000)
print(f"    日线: {len(daily):,} 条")

print("  读取资金流向...")
moneyflow = pd.read_csv(base_path + "tushare_moneyflow_fixed.csv", nrows=100000)
print(f"    资金流向: {len(moneyflow):,} 条")

print("  读取财务指标...")
fina = pd.read_csv(base_path + "tushare_fina_indicator.csv", nrows=100000)
print(f"    财务指标: {len(fina):,} 条")

# 2. 数据预处理
print("\n2. 数据预处理...")

# 处理日期
daily['date'] = pd.to_datetime(daily['date'])
moneyflow['trade_date'] = pd.to_datetime(moneyflow['trade_date'])
fina['ann_date'] = pd.to_datetime(fina['ann_date'], errors='coerce')

# 3. 特征工程（简化版）
print("\n3. 特征工程...")

# 计算收益率
daily['returns'] = daily.groupby('symbol')['close'].pct_change()

# 计算移动平均线
daily['ma5'] = daily.groupby('symbol')['close'].transform(lambda x: x.rolling(5).mean())
daily['ma20'] = daily.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())

# 计算波动率
daily['volatility'] = daily.groupby('symbol')['returns'].transform(lambda x: x.rolling(20).std())

print(f"  特征数量: {len(daily.columns)}")

# 4. 标签制作
print("\n4. 制作标签...")

# 未来20日收益率作为标签
daily['future_returns'] = daily.groupby('symbol')['returns'].shift(-20)
daily['label'] = (daily['future_returns'] > 0).astype(int)

# 5. 数据分割
print("\n5. 数据分割...")

# 去除NaN
df_model = daily.dropna()

# 训练集: 测试集 = 8:2
split_date = df_model['date'].quantile(0.8)
train_data = df_model[df_model['date'] < split_date]
test_data = df_model[df_model['date'] >= split_date]

print(f"  训练集: {len(train_data):,} 条")
print(f"  测试集: {len(test_data):,} 条")

# 6. 特征选择
print("\n6. 特征选择...")

feature_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 
                'returns', 'ma5', 'ma20', 'volatility']

X_train = train_data[feature_cols]
y_train = train_data['label']
X_test = test_data[feature_cols]
y_test = test_data['label']

print(f"  特征: {feature_cols}")

# 7. 简单模型训练（模拟）
print("\n7. 模型训练（使用简单规则模拟）...")

# 使用简单规则：MA5 > MA20 且波动率低 则买入
train_pred = ((X_train['ma5'] > X_train['ma20']) & (X_train['volatility'] < 0.02)).astype(int)
test_pred = ((X_test['ma5'] > X_test['ma20']) & (X_test['volatility'] < 0.02)).astype(int)

# 8. 评估
print("\n8. 模型评估...")

train_acc = (train_pred == y_train).mean()
test_acc = (test_pred == y_test).mean()

print(f"  训练集准确率: {train_acc:.4f}")
print(f"  测试集准确率: {test_acc:.4f}")

# 9. 回测（简化）
print("\n9. 回测（简化）...")

# 计算策略收益
strategy_returns = test_data['future_returns'] * test_pred
sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)

cumulative_returns = (1 + strategy_returns).cumprod() - 1
total_return = cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0

print(f"  总收益率: {total_return:.2%}")
print(f"  夏普比率: {sharpe:.2f}")
print(f"  交易次数: {test_pred.sum()}")

print("\n" + "="*70)
print("训练模拟完成!")
print("="*70)
