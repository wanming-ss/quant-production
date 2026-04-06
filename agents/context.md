# AI Agent Context - 项目上下文

> **AI Agent 必读** - 在操作本项目前，请先阅读此文件
>
> **相关文档**: [AGENT_ROLES.md](AGENT_ROLES.md) - Agent 角色与职责说明

---

## 📋 项目身份

- **名称**: AI-Native Quant Framework
- **版本**: 1.0.0
- **类型**: 生产级量化交易框架
- **目标用户**: AI Agent（Claude、Codex、GPT-4 等）和人类开发者

---

## 🎯 当前状态

### 已完成 ✅
- [x] 数据下载脚本 (100+ 个 Tushare API 接口)
- [x] 数据质量监控系统
- [x] 风控系统（仓位/回撤/合规）
- [x] 生产监控与备份
- [x] DolphinDB 数据存储
- [x] Qlib 集成（LightGBM 模型）
- [x] 1 个 Alpha 因子（量价背离）

### 进行中 ⏳
- [ ] 项目文档完善
- [ ] 配置中心统一
- [ ] AI Agent 接口规范化

### 待办 📝
- [ ] 扩展 Alpha 因子库（目标：10+ 因子）
- [ ] 完善回测系统
- [ ] 实盘交易接口对接
- [ ] 模型版本管理

---

## 📁 关键文件位置

### 配置文件
| 文件 | 说明 | 状态 |
|------|------|------|
| `config.yaml` | 统一配置中心 | ⚠️ 需从 example 复制 |
| `config/tushare.yaml` | Tushare API 配置 | ❌ 待创建 |
| `config/database.yaml` | 数据库配置 | ❌ 待创建 |

### 核心代码
| 文件 | 说明 | 状态 |
|------|------|------|
| `src/data/quality_monitor.py` | 数据质量监控 | ✅ 已完成 |
| `src/risk/risk_controller.py` | 风控核心 | ✅ 已完成 |
| `src/monitoring/production_monitor.py` | 生产监控 | ✅ 已完成 |
| `src/strategy/factors/` | Alpha 因子 | ⚠️ 需扩展 |

### 数据文件
| 位置 | 说明 | 大小 |
|------|------|------|
| `data/inbox/tushare_all_2016_2025.csv` | 日线数据 | ~680 MB |
| `data/inbox/tushare_adj_factor.csv` | 复权因子 | ~249 MB |
| `data/inbox/tushare_weekly.csv` | 周线数据 | ~145 MB |

---

## 🤖 AI 可执行操作

### 数据操作
```
download_data --api <api_name> --start <date> --end <date>
verify_data --path <data_path>
sync_to_dolphindb --source <csv_path> --table <table_name>
```

### 策略操作
```
train_model --config <config_file> --output <model_path>
backtest --model <model_path> --start <date> --end <date>
generate_factors --type <factor_type> --output <output_path>
```

### 风控操作
```
risk_check --order <order_json>
emergency_stop --level <1|2|3> --reason <reason>
```

### 监控操作
```
system_health
backup_data --retention <days>
check_logs --date <date>
```

---

## ⚠️ 重要注意事项

### 数据安全
1. **不要提交数据文件到 Git** - 所有数据文件已在 .gitignore 中
2. **不要硬编码 API Token** - 使用环境变量或配置文件
3. **备份优先** - 修改数据前先备份

### 风控红线
1. **禁止绕过风控检查** - 所有交易必须通过 pre_trade_check
2. **禁止修改风控参数** - 除非通过配置中心并记录
3. **紧急停止优先** - 触发紧急停止时，所有交易立即停止

### 代码质量
1. **遵循奥卡姆剃刀原则** - 如无必要，勿增实体
2. **必须有测试** - 新功能必须附带单元测试
3. **文档同步更新** - 代码变更后更新相关文档

---

## 📊 系统依赖

### 外部服务
- **Tushare API** - 行情数据源（需要 Token）
- **DolphinDB** - 时序数据库（本地服务）

### Python 环境
- Python 3.10+
- 虚拟环境：`.venv/`
- 依赖：`pip install -r requirements.txt`

---

## 🔧 快速命令参考

```bash
# 环境设置
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 运行生产检查
python src/production/production_master.py

# 数据质量检查
python src/data/quality_monitor.py

# 风控测试
python src/risk/risk_controller.py

# 备份数据
python src/monitoring/backup_manager.py
```

---

## 📞 遇到问题？

1. **查看日志**: `logs/quant_YYYYMMDD.log`
2. **检查配置**: `config.yaml`
3. **查看文档**: `docs/`
4. **提交 Issue**: GitHub Issues

---

## 🧠 AI 工作流建议

### 接手新项目时
1. 阅读 `agents/context.md`（本文件）
2. 阅读 `docs/ARCHITECTURE.md`
3. 检查 `config.yaml` 配置
4. 运行 `system_health` 检查状态

### 执行任务时
1. 记录任务开始状态
2. 执行任务
3. 验证结果
4. 更新 `agents/context.md` 的待办列表
5. 记录任务完成状态

### 离开前
1. 保存所有更改
2. 更新上下文文件
3. 留下清晰的下一步说明

---

> **最后更新**: 2026-04-06  
> **更新者**: AI Agent
