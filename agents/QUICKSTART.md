# 🚀 Agent 快速入门

> **给 AI 的 1 分钟快速入门指南**

---

## 📋 你是？

### A. AI 开发者（人类）
想在这个框架上实现 Agent 系统？

👉 **阅读**: [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md)

**内容**:
- ✅ 完整的代码模板
- ✅ 6 个 Agent 的详细实现
- ✅ 测试脚本
- ✅ 快速启动脚本
- ✅ 30 分钟实现计划

---

### B. AI Agent（LLM）
需要理解项目并执行任务？

👉 **按顺序阅读**:

1. [`AGENT_ROLES.md`](AGENT_ROLES.md) - 你的角色是什么？
2. [`context.md`](context.md) - 项目当前状态
3. [`agent_commands.md`](agent_commands.md) - 你能执行什么命令

---

## 🎯 快速导航

| 我想... | 阅读这个 |
|---------|----------|
| 实现 Agent 系统 | `IMPLEMENTATION_GUIDE.md` |
| 了解我的职责 | `AGENT_ROLES.md` |
| 查看项目状态 | `context.md` |
| 知道能做什么 | `agent_commands.md` |
| 了解系统架构 | `../docs/ARCHITECTURE.md` |
| 部署项目 | `../docs/DEPLOYMENT.md` |

---

## 🤖 6 个 Agent 角色

```
@Librarian   📚 - 数据管理员     (下载、验证、同步数据)
@Auditor     🔍 - 风控审计员     (风控检查、紧急停止)
@Strategist  🧠 - 策略研究员    (因子开发、模型训练)
@Trader      💼 - 交易执行员     (订单执行、仓位管理)
@Monitor     📊 - 系统监控员     (健康检查、数据备份)
@Kernel      🎯 - 总协调员      (任务分发、状态汇总)
```

---

## ⚡ 5 分钟速览

### 1. 项目结构（1 分钟）

```
quant-production/
├── agents/              # ← 你在这里
│   ├── IMPLEMENTATION_GUIDE.md  # 实现指南 ⭐
│   ├── AGENT_ROLES.md           # 角色定义
│   ├── context.md               # 项目上下文
│   └── agent_commands.md        # 命令列表
├── src/                 # 源代码
├── docs/                # 文档
└── config/              # 配置
```

### 2. Agent 架构（2 分钟）

```
用户请求
    ↓
@Kernel (分发任务)
    ↓
┌───────┬────────┬──────────┐
│       │        │          │
@Librarian @Auditor @Strategist ...
```

### 3. 开始工作（2 分钟）

#### 如果你是开发者：
```bash
# 1. 阅读实现指南
cat agents/IMPLEMENTATION_GUIDE.md

# 2. 创建 Agent 文件
# 按照指南中的代码模板

# 3. 运行测试
python tests/test_agents.py

# 4. 启动系统
python scripts/run_agents.py
```

#### 如果你是 AI Agent：
```bash
# 1. 确认你的角色
cat agents/AGENT_ROLES.md

# 2. 查看项目状态
cat agents/context.md

# 3. 执行任务
# 参考 agent_commands.md 中的命令
```

---

## 🎓 学习路径

### 开发者路径
```
IMPLEMENTATION_GUIDE.md
    ↓
实现 6 个 Agent
    ↓
运行测试
    ↓
扩展功能
```

### AI Agent 路径
```
AGENT_ROLES.md (了解职责)
    ↓
context.md (了解状态)
    ↓
agent_commands.md (执行任务)
```

---

## 🔗 相关资源

- **完整文档**: [`../README.md`](../README.md)
- **架构说明**: [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- **部署指南**: [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md)

---

## ❓ 常见问题

### Q: 我应该实现所有 6 个 Agent 吗？
A: 建议全部实现，但可以分阶段：
1. 第一阶段：@Kernel + @Monitor（基础功能）
2. 第二阶段：@Librarian + @Auditor（数据 + 风控）
3. 第三阶段：@Strategist + @Trader（策略 + 交易）

### Q: 必须用 LLM 实现 Agent 吗？
A: 不必须。可以用：
- LLM（灵活，适合决策）
- 规则式（快速，适合确定性任务）
- 混合式（推荐）

### Q: 如何测试我的实现？
A: 运行测试脚本：
```bash
python tests/test_agents.py
```

---

## 🎯 下一步

- **开发者**: 开始实现 → `IMPLEMENTATION_GUIDE.md`
- **AI Agent**: 开始工作 → `AGENT_ROLES.md`

---

> **最后更新**: 2026-04-06  
> **目标**: 1 分钟理解，30 分钟实现 ✅
