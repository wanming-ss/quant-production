# 🚀 AI-Native Quant Framework v1.0.0

## 📋 版本说明

这是 **AI-Native Quant Framework** 的首个公开发布版本！

---

## ✨ 核心特性

### 🤖 AI-Native 设计
- **AI 可读架构** - 任何 AI Agent（Claude、Codex、GPT-4）都能理解并操作
- **标准化命令接口** - 定义 AI 可执行的安全命令集
- **上下文感知** - AI 可快速理解项目状态和待办事项

### 📊 数据层
- **Tushare 集成** - 100+ API 接口数据下载脚本
- **DolphinDB 存储** - 高性能时序数据库
- **数据质量监控** - 自动检测异常数据

### 🛡️ 风控系统
- **仓位限制** - 单票/行业/总仓位硬限制
- **回撤控制** - 日/周/总回撤监控
- **合规检查** - ST/新股/停牌自动过滤
- **紧急停止** - 极端情况硬保护

### 📈 策略层
- **Alpha 因子** - 量价背离因子（已审计无未来函数）
- **ML 模型** - LightGBM 集成
- **Qlib 工作流** - 官方标准流程

### 🔍 监控与备份
- **系统健康检查** - 磁盘/数据/流水线监控
- **自动备份** - 带哈希验证
- **合规日志** - 操作可追溯

---

## 📦 安装

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/quant-production.git
cd quant-production

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置
cp config.yaml.example config.yaml
# 编辑 config.yaml 填入你的配置
```

详细部署指南见：[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🚀 快速开始

### 1. 系统健康检查

```bash
python src/monitoring/production_monitor.py
```

### 2. 数据质量检查

```bash
python src/data/quality_monitor.py
```

### 3. 风控测试

```bash
python src/risk/risk_controller.py
```

### 4. 生产就绪检查

```bash
python src/production/production_master.py
```

---

## 📁 项目结构

```
quant-production/
├── README.md                    # 项目说明
├── config.yaml.example          # 配置模板
├── requirements.txt             # Python 依赖
├── .gitignore                   # Git 忽略规则
│
├── docs/                        # 文档
│   ├── ARCHITECTURE.md          # 系统架构
│   ├── DEPLOYMENT.md            # 部署指南
│   └── ...
│
├── config/                      # 配置文件
│   ├── database.yaml.example
│   ├── tushare.yaml.example
│   └── risk_limits.yaml
│
├── src/                         # 源代码
│   ├── data/                    # 数据层
│   ├── strategy/                # 策略层
│   ├── risk/                    # 风控层
│   └── monitoring/              # 监控层
│
├── agents/                      # AI Agent 接口
│   ├── context.md               # 项目上下文
│   └── agent_commands.md        # 可执行命令
│
└── tests/                       # 测试
```

---

## 🤖 AI Agent 使用

### AI 必读文件

1. `agents/context.md` - 项目上下文和当前状态
2. `agents/agent_commands.md` - AI 可执行命令列表
3. `docs/ARCHITECTURE.md` - 系统架构

### AI 可执行操作

| 类别 | 示例命令 |
|------|----------|
| 数据 | `data:download`, `data:verify`, `data:sync` |
| 策略 | `strategy:train`, `strategy:backtest` |
| 风控 | `risk:check`, `risk:emergency_stop` |
| 监控 | `monitor:health`, `monitor:backup` |

---

## 📊 已知限制

- 目前仅支持 A 股市场
- 实盘交易接口待开发
- Alpha 因子库需扩展（当前 1 个因子）

---

## 🗺️ 路线图

### v1.1.0 (计划中)
- [ ] 扩展 Alpha 因子库（目标：10+ 因子）
- [ ] 完善回测系统
- [ ] 添加更多 ML 模型支持

### v1.2.0 (计划中)
- [ ] 实盘交易接口
- [ ] 实时数据流处理
- [ ] 策略组合优化

### v2.0.0 (未来)
- [ ] 多市场支持（港股、美股）
- [ ] 深度学习模型
- [ ] 分布式训练

---

## 🐛 已知问题

暂无

---

## 📞 反馈与支持

- **Issues**: https://github.com/YOUR_USERNAME/quant-production/issues
- **Discussions**: https://github.com/YOUR_USERNAME/quant-production/discussions

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

感谢以下开源项目：

- [Tushare](https://tushare.pro/) - 金融数据接口
- [DolphinDB](https://dolphindb.com/) - 时序数据库
- [Qlib](https://qlib.readthedocs.io/) - AI 量化投资平台

---

**Happy Quanting! 📈**
