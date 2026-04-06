# 工作流对比：自创 vs 开源标准

## 自创工作流 (之前)

| 组件 | 实现 | 问题 |
|------|------|------|
| 数据下载 | 自定义脚本 `download_all_apis.py` | 维护成本高 |
| 特征工程 | 自定义因子 `price_volume_divergence.dos` | 未经市场验证 |
| 数据存储 | 自定义 DolphinDB 结构 | 非标准 |
| 模型训练 | 自定义配置 | 可能非最优 |
| 回测 | 自定义 `kernel.py` | 可能存在漏洞 |
| 风控 | 自定义 `risk_control_system.py` | 未经实盘检验 |

**自创比例**: ~70%

---

## 开源标准工作流 (重构后)

| 组件 | 实现 | 来源 |
|------|------|------|
| 数据下载 | `qlib.run.get_data` | Qlib 官方 |
| 特征工程 | `Alpha158` / `Alpha360` | Qlib 官方 |
| 数据存储 | Qlib 标准格式 | Qlib 官方 |
| 模型训练 | `LGBModel` (官方示例) | Qlib 官方 |
| 回测 | `PortAnaRecord` | Qlib 官方 |
| 风控 | Pyfolio / Qlib Risk | 开源社区 |

**自创比例**: ~5% (仅剩配置文件)

---

## 推荐的标准工作流

```
数据获取:
  └── Qlib 官方数据 (qlib_data) ✅
  └── 或 Yahoo Finance (yfinance) ✅
  └── 或 AKShare (开源免费) ✅

特征工程:
  └── Alpha158 (官方158个因子) ✅
  └── Alpha360 (官方360个因子) ✅
  └── 不复自创因子 ❌

模型训练:
  └── LightGBM (官方示例) ✅
  └── XGBoost (官方示例) ✅
  └── Transformer (官方示例) ✅
  └── 不复自创模型 ❌

回测:
  └── PortAnaRecord (官方) ✅
  └── SignalRecord (官方) ✅
  └── 不复自创回测 ❌

风控:
  └── Pyfolio (Quantopian开源) ✅
  └── Qlib Risk (官方) ✅
  └── 不复自创风控 ❌
```

---

## 执行命令

### 1. 下载官方数据
```bash
# 方法1: Qlib 官方数据
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/cn_data

# 方法2: Yahoo Finance
python scripts/get_data.py yahoo --start 2016-01-01 --end 2025-03-24

# 方法3: AKShare
python -c "import akshare as ak; df = ak.stock_zh_a_hist()"
```

### 2. 运行官方工作流
```bash
# 进入 Qlib 官方示例目录
cd examples/benchmarks/LightGBM

# 运行官方工作流
qrun workflow_config_lightgbm_Alpha158.yaml
```

### 3. 使用 Pyfolio 风控
```python
import pyfolio as pf
pf.create_full_tear_sheet(returns)
```

---

## 核心原则

> **"Don't reinvent the wheel"**

1. **数据**: 用官方提供的标准数据
2. **特征**: 用 Alpha158/Alpha360 等成熟因子库
3. **模型**: 用官方验证过的模型配置
4. **回测**: 用经过千万次测试的官方回测
5. **风控**: 用 Pyfolio 等成熟风控框架

**只有配置是自创的，其他全部用开源标准。**
