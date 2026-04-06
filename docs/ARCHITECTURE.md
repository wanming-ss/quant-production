# 系统架构文档

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Agent Interface                        │
│                                                                  │
│  Natural Language → Command Parser → Action Executor → Results  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌───────────────┐
│   Data Layer  │     │ Strategy Layer  │     │  Exec Layer   │
│               │     │                 │     │               │
│ ┌───────────┐ │     │ ┌─────────────┐ │     │ ┌───────────┐ │
│ │ Tushare   │ │     │ │ Alpha       │ │     │ │ Risk      │ │
│ │ Downloader│ │     │ │ Factors     │ │     │ │ Control   │ │
│ └───────────┘ │     │ └─────────────┘ │     │ └───────────┘ │
│ ┌───────────┐ │     │ ┌─────────────┐ │     │ ┌───────────┐ │
│ │ DolphinDB │ │     │ │ ML Models   │ │     │ │ Order     │ │
│ │ Storage   │ │     │ │ (LightGBM)  │ │     │ │ Execution │ │
│ └───────────┘ │     │ └─────────────┘ │     │ └───────────┘ │
│ ┌───────────┐ │     │ ┌─────────────┐ │     │ ┌───────────┐ │
│ │ Quality   │ │     │ │ Qlib        │ │     │ │ Monitoring│ │
│ │ Monitor   │ │     │ │ Integration │ │     │ │ & Backup  │ │
│ └───────────┘ │     │ └─────────────┘ │     │ └───────────┘ │
└───────────────┘     └─────────────────┘     └───────────────┘
```

---

## 📦 模块详解

### 1. Data Layer（数据层）

**职责**: 数据获取、存储、质量保障

#### 组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Downloader | `src/data/downloader.py` | 从 Tushare 下载数据 |
| QualityMonitor | `src/data/quality_monitor.py` | 数据质量检查 |
| DolphinDBBridge | `src/data/dolphindb_bridge.py` | DolphinDB 数据同步 |

#### 数据流

```
Tushare API → Downloader → CSV (Inbox) → Quality Check → DolphinDB
```

#### 质量检查项

1. **价格跳空检测** - 识别异常波动
2. **成交量异常检测** - 识别 0 成交量和天量
3. **复权因子连续性** - 确保复权数据正确
4. **数据完整性** - 检查缺失交易日

---

### 2. Strategy Layer（策略层）

**职责**: Alpha 因子、模型训练、回测

#### 组件

| 组件 | 文件 | 职责 |
|------|------|------|
| FactorEngine | `src/strategy/factors/` | Alpha 因子计算 |
| ModelTrainer | `src/strategy/model_trainer.py` | ML 模型训练 |
| QlibWorkflow | `src/strategy/qlib_workflow.py` | Qlib 集成 |
| Backtester | `src/strategy/backtester.py` | 回测引擎 |

#### 因子类型

1. **量价因子** - 基于价格、成交量
2. **基本面因子** - 基于财务报表
3. **技术指标** - MA、MACD、RSI 等

#### 模型训练流程

```
数据准备 → 特征工程 → 模型训练 → 验证 → 保存
```

---

### 3. Exec Layer（执行层）

**职责**: 风控、订单执行、监控

#### 组件

| 组件 | 文件 | 职责 |
|------|------|------|
| RiskController | `src/risk/risk_controller.py` | 交易前风控检查 |
| EmergencyStop | `src/risk/emergency_stop.py` | 紧急停止机制 |
| ProductionMonitor | `src/monitoring/production_monitor.py` | 系统监控 |
| BackupManager | `src/monitoring/backup_manager.py` | 数据备份 |

#### 风控检查流程

```
订单 → 仓位检查 → 回撤检查 → 合规检查 → 批准/拒绝
```

#### 风控限制

| 类型 | 限制 | 默认值 |
|------|------|--------|
| 单票仓位 | 最大持仓比例 | 10% |
| 行业仓位 | 最大行业暴露 | 30% |
| 总仓位 | 最大持仓比例 | 95% |
| 日回撤 | 最大单日亏损 | 3% |
| 总回撤 | 最大累计亏损 | 15% |

---

## 🔄 核心工作流

### 1. 数据下载工作流

```
1. AI 执行：data:download --api daily --start 2026-01-01 --end 2026-04-06
2. 下载数据到：data/inbox/tushare_daily_20260101_20260406.csv
3. 执行质量检查：data:verify --path <file>
4. 同步到 DolphinDB：data:sync --source <file> --table daily
```

### 2. 模型训练工作流

```
1. 准备数据：从 DolphinDB 加载特征
2. AI 执行：strategy:train --config config/qlib_config.yaml
3. 模型保存：models/lightgbm_20260406.pkl
4. 记录实验参数到：experiments/experiment_001.json
```

### 3. 交易执行工作流

```
1. 生成交易信号：模型预测
2. 风控检查：risk:check --order <order_json>
3. 如果批准：执行订单
4. 记录日志：交易日志 + 合规日志
```

### 4. 监控工作流（心跳）

```
1. 每小时执行：monitor:health
2. 检查项：磁盘空间、数据新鲜度、系统健康
3. 如果异常：发送告警
4. 每日执行：monitor:backup --retention 7
```

---

## 📊 数据模型

### 订单结构

```json
{
  "symbol": "000001.SZ",
  "side": "buy|sell",
  "current_position": 0.05,
  "target_position": 0.08,
  "amount": 100000,
  "price": 10.50,
  "industry": "银行",
  "is_st": false,
  "is_suspended": false,
  "days_since_listing": 999
}
```

### 风控报告结构

```json
{
  "timestamp": "2026-04-06T16:00:00",
  "limits": {
    "max_single_stock_position": 0.10,
    "max_total_drawdown": 0.15
  },
  "daily_stats": {
    "orders_today": 15,
    "turnover_today": 1500000,
    "max_drawdown_today": 0.01
  },
  "violations_today": 2,
  "violation_details": [...]
}
```

---

## 🔐 安全设计

### 1. 配置安全

- API Token 通过环境变量管理
- 敏感配置不提交到 Git
- 配置文件模板化（`.example`）

### 2. 数据安全

- 数据文件 .gitignore
- 备份带哈希验证
- 操作日志可追溯

### 3. 交易安全

- 所有交易必须通过风控检查
- 紧急停止机制
- 交易日志不可篡改

---

## 🧪 测试策略

### 单元测试

```python
# tests/test_risk_control.py
def test_position_limit_check():
    risk_ctrl = RiskController()
    order = {"symbol": "000001.SZ", "target_position": 0.15}
    assert risk_ctrl.check_position_limit(order) == False
```

### 集成测试

```python
# tests/test_pipeline.py
def test_full_pipeline():
    # 下载 → 验证 → 同步 → 训练 → 回测
    pass
```

---

## 📈 性能指标

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| 数据下载速度 | > 100K 记录/秒 | - |
| 风控检查延迟 | < 10ms | - |
| 模型训练时间 | < 1 小时 | - |
| 回测执行时间 | < 5 分钟 | - |

---

> **版本**: 1.0.0  
> **最后更新**: 2026-04-06
