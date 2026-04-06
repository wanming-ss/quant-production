# AI Agent Commands - AI 可执行命令列表

> 本文件定义了 AI Agent 可以安全执行的所有命令

---

## 📋 命令分类

| 分类 | 前缀 | 风险等级 | 需要确认 |
|------|------|----------|----------|
| 数据操作 | `data:*` | 🟡 中 | 是 |
| 策略操作 | `strategy:*` | 🟡 中 | 是 |
| 风控操作 | `risk:*` | 🔴 高 | 必须 |
| 监控操作 | `monitor:*` | 🟢 低 | 否 |
| 系统操作 | `system:*` | 🟢 低 | 否 |

---

## 🔍 监控命令 (Monitor)

### `monitor:health`
**描述**: 执行系统健康检查

**参数**: 无

**输出**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "checks": {
    "disk_space": {"status": "pass|fail", "value": "150GB free"},
    "data_freshness": {"status": "pass|fail", "value": "2h old"},
    "pipeline_health": {"status": "pass|fail"}
  }
}
```

**执行方式**:
```bash
python src/monitoring/production_monitor.py
```

---

### `monitor:backup`
**描述**: 执行数据备份

**参数**:
- `--retention <days>`: 备份保留天数（默认：7）

**输出**: 备份路径和验证结果

**执行方式**:
```bash
python src/monitoring/backup_manager.py --retention 7
```

---

### `monitor:logs`
**描述**: 查看系统日志

**参数**:
- `--date <YYYYMMDD>`: 指定日期（默认：今天）
- `--level <INFO|WARN|ERROR>`: 日志级别过滤

**执行方式**:
```bash
cat logs/quant_20260406.log | grep ERROR
```

---

## 📊 数据命令 (Data)

### `data:download`
**描述**: 从 Tushare 下载数据

**参数**:
- `--api <api_name>`: API 接口名称（如 `daily`, `weekly`）
- `--start <YYYY-MM-DD>`: 开始日期
- `--end <YYYY-MM-DD>`: 结束日期
- `--output <path>`: 输出路径

**执行方式**:
```bash
python artifacts/download_daily.py --start 2026-01-01 --end 2026-04-06
```

**⚠️ 注意**: 需要 Tushare API Token

---

### `data:verify`
**描述**: 验证数据质量

**参数**:
- `--path <data_path>`: 数据文件路径
- `--full`: 执行完整检查（默认：快速检查）

**输出**: 质量报告 JSON

**执行方式**:
```bash
python src/data/quality_monitor.py --path data/inbox/tushare_all_2016_2025.csv
```

---

### `data:sync`
**描述**: 同步数据到 DolphinDB

**参数**:
- `--source <csv_path>`: 源 CSV 文件
- `--table <table_name>`: 目标表名
- `--mode <append|replace>`: 写入模式

**执行方式**:
```bash
python src/data/dolphindb_bridge.py --source data/inbox/daily.csv --table daily --mode append
```

**⚠️ 注意**: 需要 DolphinDB 服务运行

---

## 🧠 策略命令 (Strategy)

### `strategy:train`
**描述**: 训练 ML 模型

**参数**:
- `--config <config_file>`: 训练配置文件
- `--output <model_path>`: 模型输出路径
- `--retrain`: 强制重新训练（默认：增量训练）

**执行方式**:
```bash
python artifacts/train_lightgbm_simple.py --config config/qlib_config.yaml
```

---

### `strategy:backtest`
**描述**: 执行回测

**参数**:
- `--model <model_path>`: 模型文件路径
- `--start <YYYY-MM-DD>`: 回测开始日期
- `--end <YYYY-MM-DD>`: 回测结束日期
- `--initial_cash <amount>`: 初始资金（默认：1000000）

**输出**: 回测报告（夏普比率、最大回撤等）

**执行方式**:
```bash
python src/strategy/qlib_workflow.py backtest --model models/lightgbm_model.pkl --start 2024-01-01 --end 2026-04-06
```

---

### `strategy:generate_factors`
**描述**: 生成 Alpha 因子

**参数**:
- `--type <factor_type>`: 因子类型（`price_volume`, `fundamental`, `technical`）
- `--output <output_path>`: 输出路径

**执行方式**:
```bash
python src/strategy/factors/generate_factors.py --type price_volume
```

---

## 🛡️ 风控命令 (Risk)

### `risk:check`
**描述**: 执行交易前风控检查

**参数**:
- `--order <order_json>`: 订单信息（JSON 格式）

**订单格式**:
```json
{
  "symbol": "000001.SZ",
  "current_position": 0.05,
  "target_position": 0.08,
  "industry": "银行",
  "is_st": false,
  "amount": 100000
}
```

**输出**:
```json
{
  "approved": true|false,
  "reason": "All checks passed|具体拒绝原因"
}
```

**执行方式**:
```bash
python src/risk/risk_controller.py check --order '{"symbol":"000001.SZ",...}'
```

**⚠️ 警告**: 此命令必须执行，禁止绕过！

---

### `risk:emergency_stop`
**描述**: 触发紧急停止

**参数**:
- `--level <1|2|3>`: 紧急级别
  - 1: 警告（加强监控）
  - 2: 限制（限制交易）
  - 3: 停止（所有交易 halted）
- `--reason <reason>`: 停止原因

**执行方式**:
```bash
python src/risk/risk_controller.py emergency_stop --level 3 --reason "Market crash detected"
```

**⚠️ 警告**: 级别 3 会立即停止所有交易！

---

### `risk:report`
**描述**: 生成风控报告

**参数**:
- `--date <YYYY-MM-DD>`: 报告日期（默认：今天）
- `--output <output_path>`: 输出路径

**输出**: 风控报告 JSON

**执行方式**:
```bash
python src/risk/risk_controller.py report --date 2026-04-06
```

---

## ⚙️ 系统命令 (System)

### `system:status`
**描述**: 显示系统状态

**参数**: 无

**输出**:
```
Quant Production Status
=======================
Version: 1.0.0
Data Files: 15
Models: 3
Last Backup: 2026-04-05 23:00
Risk Status: NORMAL
```

**执行方式**:
```bash
python src/production/production_master.py status
```

---

### `system:production_check`
**描述**: 执行生产就绪检查

**参数**: 无

**输出**: 生产就绪报告

**执行方式**:
```bash
python src/production/production_master.py
```

---

## 📝 命令执行规范

### 执行前检查
1. 确认命令风险等级
2. 检查是否需要用户确认
3. 验证参数完整性

### 执行中记录
1. 记录命令开始时间
2. 记录命令参数
3. 记录中间状态（长任务）

### 执行后验证
1. 验证命令执行结果
2. 更新系统状态
3. 更新 `agents/context.md`

---

## 🔐 权限说明

| 命令类别 | AI 自主执行 | 需用户确认 | 禁止执行 |
|----------|-------------|------------|----------|
| `monitor:*` | ✅ | - | - |
| `system:*` | ✅ | - | - |
| `data:verify` | ✅ | - | - |
| `data:download` | - | ✅ | - |
| `data:sync` | - | ✅ | - |
| `strategy:*` | - | ✅ | - |
| `risk:check` | ✅ | - | - |
| `risk:emergency_stop` | - | ✅ (级别 2+) | - |
| `risk:*` (修改参数) | - | - | ❌ |

---

> **版本**: 1.0.0  
> **最后更新**: 2026-04-06
