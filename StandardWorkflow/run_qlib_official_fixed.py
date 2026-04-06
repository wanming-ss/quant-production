#!/usr/bin/env python3
"""
执行 Qlib 官方工作流 - Windows 兼容版
使用 freeze_support 修复多进程问题
"""
import multiprocessing
multiprocessing.freeze_support()

import qlib
from qlib.config import REG_CN
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord
from qlib.utils import flatten_dict
import json

print("="*70)
print("Qlib 官方标准工作流 (Windows Compatible)")
print("="*70)

def main():
    # 1. 初始化 Qlib
    print("\n1️⃣  初始化 Qlib...")
    qlib.init(
        provider_uri='~/.qlib/qlib_data/cn_data',
        region=REG_CN
    )
    print("   ✅ Qlib initialized")
    
    # 2. 使用官方 Alpha158 特征
    print("\n2️⃣  使用官方 Alpha158 特征...")
    
    handler_config = {
        "start_time": "2016-01-01",
        "end_time": "2025-03-24",
        "fit_start_time": "2016-01-01",
        "fit_end_time": "2022-12-31",
        "instruments": "csi300",
        "infer_processors": [
            {"class": "FilterCol", "kwargs": {"fields_group": "feature"}},
            {"class": "CSZScoreNorm", "kwargs": {"fields_group": "feature"}},
        ],
        "learn_processors": [
            {"class": "DropnaLabel"},
            {"class": "CSZScoreNorm", "kwargs": {"fields_group": "feature"}},
            {"class": "CSZScoreNorm", "kwargs": {"fields_group": "label"}},
        ],
    }
    
    handler = Alpha158(**handler_config)
    print("   ✅ Alpha158 handler created")
    
    # 3. 数据集划分
    print("\n3️⃣  创建数据集...")
    dataset = DatasetH(
        handler=handler,
        segments={
            "train": ("2016-01-01", "2022-12-31"),
            "valid": ("2023-01-01", "2023-12-31"),
            "test": ("2024-01-01", "2025-03-24"),
        }
    )
    print(f"   Train: {len(dataset.prepare('train')):,} samples")
    print(f"   Valid: {len(dataset.prepare('valid')):,} samples")
    print(f"   Test:  {len(dataset.prepare('test')):,} samples")
    
    # 4. 官方 LightGBM 模型
    print("\n4️⃣  训练官方 LightGBM 模型...")
    model = LGBModel(
        loss="mse",
        colsample_bytree=0.8879,
        learning_rate=0.0421,
        subsample=0.8789,
        lambda_l1=205.6999,
        lambda_l2=580.9768,
        max_depth=8,
        num_leaves=210,
        num_threads=1,  # Windows 兼容性：单线程
    )
    model.fit(dataset)
    print("   ✅ Model trained")
    
    # 5. 官方回测
    print("\n5️⃣  执行官方回测...")
    with R.start(experiment_name="qlib_official_workflow"):
        R.log_params(**flatten_dict({
            "model": "LGBModel",
            "handler": "Alpha158",
            "dataset": "csi300"
        }))
        
        sr = SignalRecord(model, dataset)
        sr.generate()
        
        strategy = TopkDropoutStrategy(topk=50, n_drop=10)
        port_analysis_config = {
            "executor": {
                "class": "SimulatorExecutor",
                "module_path": "qlib.backtest.executor",
                "kwargs": {
                    "time_per_step": "day",
                    "generate_portfolio_metrics": True,
                }
            },
            "strategy": strategy,
            "backtest": {
                "start_time": "2024-01-01",
                "end_time": "2025-03-24",
                "account": 100000000,
                "benchmark": "SH000300",
                "exchange_kwargs": {
                    "freq": "DAY",
                    "limit_threshold": 0.095,
                    "deal_price": "close",
                    "open_cost": 0.0005,
                    "close_cost": 0.0015,
                    "min_cost": 5,
                }
            }
        }
        par = PortAnaRecord(sr, port_analysis_config)
        par.generate()
        print("   ✅ Backtest completed")
    
    # 6. 结果
    print("\n6️⃣  结果分析...")
    recorder = R.get_recorder()
    
    print("\n" + "="*70)
    print("官方标准工作流完成!")
    print("="*70)
    print("\n📊 所有组件均来自 Qlib 官方:")
    print("   - 数据: Qlib 官方数据集")
    print("   - 特征: Alpha158 (官方)")
    print("   - 模型: LGBModel (官方)")
    print("   - 回测: PortAnaRecord (官方)")
    print("   - 策略: TopkDropoutStrategy (官方)")
    print("\n✅ 无自创代码")
    print("✅ 完全基于开源标准")
    
    return True

if __name__ == "__main__":
    main()
