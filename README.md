# 🚀 AI-Native Quant Framework

> **生产级量化交易框架，专为 AI Agent 设计**  
> 跑得稳 · 跑得久 · 跑得合规

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![DolphinDB](https://img.shields.io/badge/DolphinDB-1.30+-green.svg)](https://dolphindb.com/)

[![GitHub stars](https://img.shields.io/github/stars/wanming-ss/quant-production)](https://github.com/wanming-ss/quant-production)
[![GitHub forks](https://img.shields.io/github/forks/wanming-ss/quant-production)](https://github.com/wanming-ss/quant-production/network)
[![GitHub issues](https://img.shields.io/github/issues/wanming-ss/quant-production)](https://github.com/wanming-ss/quant-production/issues)

---

## 🎯 项目定位

这是一个 **AI-Native** 的量化交易框架，设计目标：

1. **AI 可读** - 任何 AI Agent（Claude、Codex、GPT-4）都能理解项目结构并自主操作
2. **生产就绪** - 数据质量监控、风控系统、备份机制完整
3. **快速复用** - 新 AI 接手后 5 分钟内理解架构，30 分钟内开始工作

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Interface                        │
│  (Natural Language → Actions → Results)                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌───────────────┐
│  Data Layer   │   │  Strategy Layer │   │  Exec Layer   │
│               │   │                 │   │               │
│ • Tushare API │   │ • Alpha Factors │   │ • Risk Ctrl   │
│ • DolphinDB   │   │ • ML Models     │   │ • Order Mgmt  │
│ • Data Quality│   │ • Qlib Integration│ │ • Monitoring  │
└───────────────┘   └─────────────────┘   └───────────────┘
```

---

## 📁 目录结构

```
quant-production/
├── README.md                    # 本文件
├── config.yaml                  # 统一配置中心
├── .gitignore                   # Git 忽略规则
├── requirements.txt             # Python 依赖
│
├── docs/                        # 文档
│   ├── ARCHITECTURE.md          # 架构说明
│   ├── AI_AGENT_GUIDE.md        # AI Agent 使用指南
│   └── DEPLOYMENT.md            # 部署指南
│
├── config/                      # 配置文件
│   ├── database.yaml            # 数据库配置
│   ├── tushare.yaml             # Tushare API 配置
│   └── risk_limits.yaml         # 风控参数
│
├── src/                         # 源代码
│   ├── data/                    # 数据层
│   │   ├── downloader.py        # 数据下载
│   │   ├── quality_monitor.py   # 数据质量监控
│   │   └── dolphindb_bridge.py  # DolphinDB 桥接
│   │
│   ├── strategy/                # 策略层
│   │   ├── factors/             # Alpha 因子
│   │   ├── models/              # ML 模型
│   │   └── qlib_workflow.py     # Qlib 工作流
│   │
│   ├── risk/                    # 风控层
│   │   ├── risk_controller.py   # 风控核心
│   │   └── emergency_stop.py    # 紧急停止
│   │
│   └── monitoring/              # 监控层
│       ├── production_monitor.py # 生产监控
│       └── backup_manager.py    # 备份管理
│
├── agents/                      # AI Agent 接口
│   ├── agent_commands.md        # AI 可执行命令列表
│   └── context.md               # 项目上下文（AI 必读）
│
├── data/                        # 数据目录（.gitignore）
│   ├── inbox/                   # 原始数据
│   ├── processed/               # 处理后数据
│   └── backup/                  # 备份
│
├── artifacts/                   # 脚本和工具
│   ├── download_*.py            # 数据下载脚本
│   └── train_*.py               # 模型训练脚本
│
└── tests/                       # 测试
    ├── test_data_quality.py
    └── test_risk_control.py
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/wanming-ss/quant-production.git
cd quant-production

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置模板
cp config.yaml.example config.yaml
cp config/tushare.yaml.example config/tushare.yaml

# 编辑配置，填入你的 API Key
# - Tushare API Token
# - DolphinDB 连接信息
```

### 3. 验证安装

```bash
# 运行生产就绪检查
python src/production/production_master.py
```

### 4. AI Agent 快速上手

#### 🤖 AI 开发者 - 快速实现 Agent

```bash
# 30 分钟实现指南
cat agents/IMPLEMENTATION_GUIDE.md

# 包含：
# - 完整代码模板
# - 6 个 Agent 实现
# - 测试脚本
# - 快速启动脚本
```

#### 🤖 AI Agent - 理解项目

```bash
# Agent 角色与职责
cat agents/AGENT_ROLES.md

# 项目上下文
cat agents/context.md

# 可执行命令列表
cat agents/agent_commands.md
```

---

## 🤖 AI Agent 集成

### AI 可以执行的操作

| 类别 | 命令 | 说明 |
|------|------|------|
| **数据** | `download_data` | 下载 Tushare 数据 |
| | `verify_data` | 验证数据完整性 |
| | `sync_to_dolphindb` | 同步到 DolphinDB |
| **策略** | `train_model` | 训练 ML 模型 |
| | `backtest` | 执行回测 |
| | `generate_factors` | 生成 Alpha 因子 |
| **风控** | `risk_check` | 风控检查 |
| | `emergency_stop` | 紧急停止 |
| **监控** | `system_health` | 系统健康检查 |
| | `backup_data` | 数据备份 |

### AI 上下文文件

AI Agent 在操作本项目前，应先阅读：

1. `agents/AGENT_ROLES.md` - **Agent 角色定义**（确认你的职责）
2. `agents/context.md` - 项目上下文、当前状态、待办事项
3. `config.yaml` - 当前配置
4. `docs/ARCHITECTURE.md` - 系统架构

---

## 📊 核心功能

### 1. 数据质量监控

```python
from src.data.quality_monitor import DataQualityMonitor

monitor = DataQualityMonitor()
monitor.run_all_checks()

# 检查项：
# - 价格跳空检测
# - 成交量异常检测
# - 复权因子连续性
# - 数据完整性验证
```

### 2. 风控系统

```python
from src.risk.risk_controller import RiskController

risk_ctrl = RiskController()

order = {
    "symbol": "000001.SZ",
    "current_position": 0.05,
    "target_position": 0.08,
    "industry": "银行",
    "is_st": False,
    "amount": 100000
}

if risk_ctrl.pre_trade_check(order):
    print("✅ 订单批准")
else:
    print("❌ 订单拒绝")
```

### 3. 生产监控

```python
from src.monitoring.production_monitor import ProductionMonitor

monitor = ProductionMonitor()
monitor.check_disk_space()
monitor.check_data_freshness()
monitor.check_pipeline_health()
```

---

## 📋 生产就绪检查清单

在实盘部署前，确保完成以下检查：

### 数据层
- [ ] Tushare API 配置正确
- [ ] DolphinDB 服务运行正常
- [ ] 历史数据完整（2016-2025）
- [ ] 数据质量监控通过

### 策略层
- [ ] Alpha 因子无未来函数
- [ ] 模型回测完成
- [ ] 夏普比率 > 1.0
- [ ] 最大回撤 < 15%

### 风控层
- [ ] 仓位限制配置合理
- [ ] 紧急停止机制测试通过
- [ ] 合规检查启用

### 监控层
- [ ] 磁盘空间 > 100GB
- [ ] 备份策略配置
- [ ] 日志记录启用

---

## 🔧 开发指南

### 添加新的 Alpha 因子

1. 在 `src/strategy/factors/` 创建因子脚本
2. 编写因子单元测试
3. 通过 `@Auditor` 审计（无未来函数）
4. 更新因子注册表

### 添加新的 AI 命令

1. 在 `agents/agent_commands.md` 添加命令定义
2. 实现命令处理函数
3. 更新 `agents/context.md`

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎贡献！请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📞 联系

- **Issues**: https://github.com/wanming-ss/quant-production/issues
- **Discussions**: https://github.com/wanming-ss/quant-production/discussions
- **Email**: [你的邮箱]

---

> **设计理念**: "Entities should not be multiplied unnecessarily." - 奥卡姆剃刀原则  
> **目标**: 让 AI 和人类开发者都能高效协作
