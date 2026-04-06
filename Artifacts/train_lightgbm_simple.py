#!/usr/bin/env python3
"""
Qlib LightGBM 训练 - 简化版
直接使用 CSV 数据训练
"""
import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os
from datetime import datetime

print("="*70)
print("Qlib LightGBM Model Training (Simplified)")
print("="*70)

# 配置
DATA_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
MODEL_DIR = "E:/Quant_Production/Artifacts/Models"

# 确保模型目录存在
os.makedirs(MODEL_DIR, exist_ok=True)

# ==================== 1. 加载数据 ====================
print("\n1️⃣  Loading data...")

if not os.path.exists(DATA_PATH):
    print(f"❌ Data file not found: {DATA_PATH}")
    print("Please ensure data is downloaded first.")
    exit(1)

df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"   ✅ Loaded {len(df):,} records")
print(f"   Columns: {list(df.columns)}")

# ==================== 2. 特征工程 ====================
print("\n2️⃣  Feature engineering...")

# 确保数据有序
df = df.sort_values(['symbol', 'date'])

# 计算收益率（标签）
df['returns'] = df.groupby('symbol')['close'].pct_change(20)  # 20日收益率

# 计算技术特征
df['ma5'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(5).mean())
df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).mean())
df['vol_ma20'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())

# 价格动量特征
df['momentum_5'] = df.groupby('symbol')['close'].transform(lambda x: x.pct_change(5))
df['momentum_20'] = df.groupby('symbol')['close'].transform(lambda x: x.pct_change(20))

# 波动率特征
df['volatility_20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20).std() / x.rolling(20).mean())

# 成交量特征
df['volume_ratio'] = df['volume'] / df['vol_ma20']
df['volume_change'] = df.groupby('symbol')['volume'].pct_change()

# 量价背离特征（核心 alpha 因子）
df['price_change'] = df.groupby('symbol')['close'].pct_change()
df['pv_divergence'] = df['price_change'] * df['volume_change'].apply(lambda x: -1 if x > 0 else 1)

# RSI 特征
def calc_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['rsi'] = df.groupby('symbol')['close'].transform(lambda x: calc_rsi(x))

# 清理数据
df = df.dropna()
print(f"   ✅ After feature engineering: {len(df):,} records")

# ==================== 3. 准备训练数据 ====================
print("\n3️⃣  Preparing training data...")

# 特征列
feature_cols = [
    'open', 'high', 'low', 'close', 'volume',
    'ma5', 'ma20', 'vol_ma20',
    'momentum_5', 'momentum_20', 'volatility_20',
    'volume_ratio', 'volume_change', 'pv_divergence', 'rsi'
]

# 标签列
target_col = 'returns'

# 时间分割
df['date'] = pd.to_datetime(df['date'])
train_df = df[df['date'] < '2023-01-01']
valid_df = df[(df['date'] >= '2023-01-01') & (df['date'] < '2024-01-01')]
test_df = df[df['date'] >= '2024-01-01']

X_train = train_df[feature_cols]
y_train = train_df[target_col]
X_valid = valid_df[feature_cols]
y_valid = valid_df[target_col]
X_test = test_df[feature_cols]
y_test = test_df[target_col]

print(f"   Train: {len(X_train):,} samples")
print(f"   Valid: {len(X_valid):,} samples")
print(f"   Test:  {len(X_test):,} samples")

# ==================== 4. 训练模型 ====================
print("\n4️⃣  Training LightGBM model...")

model = LGBMRegressor(
    objective='regression',
    metric='rmse',
    boosting_type='gbdt',
    num_leaves=31,
    learning_rate=0.05,
    n_estimators=500,
    feature_fraction=0.8,
    bagging_fraction=0.8,
    bagging_freq=5,
    verbose=-1,
    random_state=42,
    n_jobs=-1
)

# 训练（带早停）
model.fit(
    X_train, y_train,
    eval_set=[(X_valid, y_valid)],
    callbacks=[],
    eval_metric='rmse'
)

print("   ✅ Model trained")

# ==================== 5. 评估模型 ====================
print("\n5️⃣  Evaluating model...")

# 预测
train_pred = model.predict(X_train)
valid_pred = model.predict(X_valid)
test_pred = model.predict(X_test)

# 计算指标
def print_metrics(y_true, y_pred, name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    ic = np.corrcoef(y_true, y_pred)[0, 1]
    print(f"   {name}:")
    print(f"     RMSE: {rmse:.6f}")
    print(f"     R²:   {r2:.6f}")
    print(f"     IC:   {ic:.6f}")

print_metrics(y_train, train_pred, "Train")
print_metrics(y_valid, valid_pred, "Valid")
print_metrics(y_test, test_pred, "Test")

# ==================== 6. 特征重要性 ====================
print("\n6️⃣  Feature importance...")

importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("   Top 10 features:")
for _, row in importance.head(10).iterrows():
    print(f"     {row['feature']:20s} {row['importance']:.2f}")

# ==================== 7. 保存模型 ====================
print("\n7️⃣  Saving model...")

# 保存模型
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_path = f"{MODEL_DIR}/lightgbm_model_{timestamp}.pkl"

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"   ✅ Model saved: {model_path}")

# 保存特征重要性
importance_path = f"{MODEL_DIR}/feature_importance_{timestamp}.csv"
importance.to_csv(importance_path, index=False)
print(f"   ✅ Feature importance saved: {importance_path}")

# 保存预测结果
predictions = test_df[['symbol', 'date', 'close', 'returns']].copy()
predictions['predicted_returns'] = test_pred
predictions_path = f"{MODEL_DIR}/predictions_{timestamp}.csv"
predictions.to_csv(predictions_path, index=False)
print(f"   ✅ Predictions saved: {predictions_path}")

# ==================== 8. 简单回测 ====================
print("\n8️⃣  Simple backtest...")

# 按预测收益率排序，取 top 50 只股票
test_df['predicted_returns'] = test_pred
daily_returns = []

for date in sorted(test_df['date'].unique()):
    day_df = test_df[test_df['date'] == date]
    if len(day_df) >= 50:
        top50 = day_df.nlargest(50, 'predicted_returns')
        avg_return = top50['returns'].mean()
        daily_returns.append(avg_return)

if daily_returns:
    cumulative_return = np.prod([1 + r for r in daily_returns]) - 1
    annual_return = np.mean(daily_returns) * 252
    sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
    
    print(f"   Cumulative Return: {cumulative_return:.4f}")
    print(f"   Annual Return:     {annual_return:.4f}")
    print(f"   Sharpe Ratio:      {sharpe:.4f}")

print("\n" + "="*70)
print("Training completed!")
print("="*70)
