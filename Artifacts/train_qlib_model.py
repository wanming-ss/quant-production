"""
Qlib Model Training Pipeline
使用 LightGBM 训练量化模型

@Synthesizer: 整合 DolphinDB 因子数据与 Qlib 框架
"""
import qlib
from qlib.config import REG_CN
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP
from qlib.model import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord
from qlib.utils import flatten_dict
import pandas as pd
import numpy as np
import os
from pathlib import Path

# 初始化 Qlib
qlib.init(provider_uri='E:/Quant_Production/Artifacts', region=REG_CN)

print("="*70)
print("Qlib Model Training Pipeline")
print("="*70)

# ==================== 配置部分 ====================

# 数据处理器配置
DATA_HANDLER_CONFIG = {
    "start_time": "2016-01-01",
    "end_time": "2025-03-24",
    "fit_start_time": "2016-01-01",
    "fit_end_time": "2022-12-31",
    "instruments": "all",  # 或指定股票池
    
    # 加载自定义因子数据
    "data_loader": {
        "class": "QlibDataLoader",
        "kwargs": {
            "config": {
                "feature": [
                    # 价格因子
                    "$close", "$open", "$high", "$low", "$volume",
                    "$vwap", "$change", "$turnover",
                    
                    # 技术指标 (TA-Lib)
                    "MA($close, 5)", "MA($close, 10)", "MA($close, 20)",
                    "EMA($close, 12)", "EMA($close, 26)",
                    "RSI($close, 14)",
                    "MACD($close, 12, 26, 9)",
                    "BBANDS($close, 20, 2)",
                    "ATR($high, $low, $close, 14)",
                    
                    # 自定义因子 (从 CSV 加载)
                    "$pv_divergence_zscore",  # 量价背离因子
                    "$pv_corr",               # 量价相关系数
                    "$rel_volume",            # 相对成交量
                ],
                "label": [
                    # 标签: 未来 20 日收益率
                    "Ref($close, -20) / $close - 1"
                ]
            }
        }
    },
    
    # 数据预处理
    "learn_processors": [
        {"class": "DropnaLabel"},
        {"class": "CSZScoreNorm", "kwargs": {"fields_group": "feature"}},
        {"class": "CSZScoreNorm", "kwargs": {"fields_group": "label"}},
    ],
    "infer_processors": [
        {"class": "CSZScoreNorm", "kwargs": {"fields_group": "feature"}},
    ],
}

# 数据集配置
DATASET_CONFIG = {
    "class": "DatasetH",
    "module_path": "qlib.data.dataset",
    "kwargs": {
        "handler": {
            "class": "Alpha158",  # 或使用自定义 handler
            "module_path": "qlib.contrib.data.handler",
            "kwargs": DATA_HANDLER_CONFIG,
        },
        "segments": {
            "train": ("2016-01-01", "2022-12-31"),
            "valid": ("2023-01-01", "2023-12-31"),
            "test": ("2024-01-01", "2025-03-24"),
        }
    }
}

# LightGBM 模型配置
MODEL_CONFIG = {
    "class": "LGBModel",
    "module_path": "qlib.contrib.model.gbdt",
    "kwargs": {
        "loss": "mse",
        "colsample_bytree": 0.8879,
        "learning_rate": 0.0421,
        "subsample": 0.8789,
        "lambda_l1": 205.6999,
        "lambda_l2": 580.9768,
        "max_depth": 8,
        "num_leaves": 210,
        "num_threads": 20,
        "n_estimators": 500,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1,
        "seed": 42,
    }
}

# 回测配置
BACKTEST_CONFIG = {
    "start_time": "2024-01-01",
    "end_time": "2025-03-24",
    "account": 100000000,  # 初始资金 1亿
    "benchmark": "SH000300",  # 沪深300基准
    "exchange_kwargs": {
        "freq": "DAY",
        "limit_threshold": 0.095,  # 涨跌停限制
        "deal_price": "close",
        "open_cost": 0.0005,      # 开仓成本
        "close_cost": 0.0015,     # 平仓成本
        "min_cost": 5,            # 最小手续费
    }
}

# 策略配置
STRATEGY_CONFIG = {
    "class": "TopkDropoutStrategy",
    "module_path": "qlib.contrib.strategy",
    "kwargs": {
        "model": MODEL_CONFIG,
        "dataset": DATASET_CONFIG,
        "topk": 50,              # 持仓数量
        "n_drop": 10,            # 每日调仓数量
    }
}

# ==================== 训练流程 ====================

def load_custom_factors():
    """加载自定义因子数据"""
    print("\n1️⃣  Loading custom factors...")
    
    # 从 Vault 加载因子数据
    factor_path = "E:/Quant_Production/Vault/qlib_data/pv_divergence_factor.csv"
    
    if os.path.exists(factor_path):
        df = pd.read_csv(factor_path, parse_dates=['datetime'])
        print(f"   ✅ Loaded {len(df):,} factor records")
        return df
    else:
        print(f"   ⚠️ Factor file not found: {factor_path}")
        print("   Will use built-in factors only")
        return None

def prepare_data():
    """准备数据集"""
    print("\n2️⃣  Preparing dataset...")
    
    # 创建数据处理器
    from qlib.contrib.data.handler import Alpha158
    handler = Alpha158(**DATA_HANDLER_CONFIG)
    
    # 创建数据集
    dataset = DatasetH(
        handler=handler,
        segments=DATASET_CONFIG['kwargs']['segments']
    )
    
    print("   ✅ Dataset prepared")
    print(f"   Train: {len(dataset.prepare('train')):,} samples")
    print(f"   Valid: {len(dataset.prepare('valid')):,} samples")
    print(f"   Test:  {len(dataset.prepare('test')):,} samples")
    
    return dataset

def train_model(dataset):
    """训练模型"""
    print("\n3️⃣  Training LightGBM model...")
    
    # 初始化模型
    model = init_instance_by_config(MODEL_CONFIG)
    
    # 准备训练数据
    df_train = dataset.prepare("train", col_set=["feature", "label"], data_key="learn")
    df_valid = dataset.prepare("valid", col_set=["feature", "label"], data_key="learn")
    
    # 分离 X, y
    X_train = df_train['feature']
    y_train = df_train['label']
    X_valid = df_valid['feature']
    y_valid = df_valid['label']
    
    # 训练
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
    
    print("   ✅ Model trained")
    
    # 保存模型
    model_path = "E:/Quant_Production/Artifacts/Models/lightgbm_model.pkl"
    import pickle
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"   💾 Model saved to {model_path}")
    
    return model

def backtest(model, dataset):
    """回测"""
    print("\n4️⃣  Running backtest...")
    
    # 使用 Recorder 记录实验
    with R.start(experiment_name="qlib_model_training"):
        # 记录参数
        R.log_params(**flatten_dict({
            "model": MODEL_CONFIG,
            "dataset": DATASET_CONFIG,
            "backtest": BACKTEST_CONFIG,
        }))
        
        # 生成预测信号
        sr = SignalRecord(model, dataset)
        sr.generate()
        
        # 策略回测
        par = PortAnaRecord(sr, BACKTEST_CONFIG, STRATEGY_CONFIG)
        par.generate()
        
        # 获取回测结果
        results = par.get_portfolio_analyser()
        
        print("\n" + "="*70)
        print("Backtest Results")
        print("="*70)
        print(f"Cumulative Return: {results['cum_returns']:.4f}")
        print(f"Annual Return:     {results['annual_return']:.4f}")
        print(f"Max Drawdown:      {results['max_drawdown']:.4f}")
        print(f"Sharpe Ratio:      {results['sharpe']:.4f}")
        print(f"Information Ratio: {results.get('information_ratio', 'N/A')}")
        print("="*70)
        
        return results

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Qlib Model Training Pipeline - Starting")
    print("="*70)
    
    # 1. 加载自定义因子
    factors = load_custom_factors()
    
    # 2. 准备数据
    dataset = prepare_data()
    
    # 3. 训练模型
    model = train_model(dataset)
    
    # 4. 回测
    results = backtest(model, dataset)
    
    print("\n" + "="*70)
    print("Training Pipeline Completed!")
    print("="*70)
    print(f"\n📁 Model saved: E:/Quant_Production/Artifacts/Models/")
    print(f"📊 Results available in Qlib Recorder")
    
    return model, results

if __name__ == "__main__":
    model, results = main()
