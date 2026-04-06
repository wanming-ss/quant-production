# 贡献指南

欢迎贡献！本文件说明如何参与项目开发。

---

## 🚀 快速开始

### 1. Fork 项目

```bash
# GitHub 上点击 Fork 按钮
```

### 2. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/quant-production.git
cd quant-production
```

### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install -e .  # 可编辑模式安装
```

### 4. 创建分支

```bash
git checkout -b feature/your-feature-name
```

---

## 📝 开发规范

### 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 `black` 格式化代码
- 使用 `flake8` 检查代码质量
- 使用 `mypy` 进行类型检查

```bash
# 格式化代码
black src/ tests/

# 检查代码
flake8 src/ tests/

# 类型检查
mypy src/
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件/模块 | snake_case | `quality_monitor.py` |
| 类 | PascalCase | `DataQualityMonitor` |
| 函数/变量 | snake_case | `check_price_jump` |
| 常量 | UPPER_CASE | `MAX_POSITION` |
| 私有成员 | 前缀 `_` | `_internal_method` |

### 文档规范

- 所有公共函数必须有 docstring
- 使用 Google 风格 docstring

```python
def check_price_jump(df, threshold=0.11):
    """
    检测价格跳空（涨停/跌停/异常波动）
    
    Args:
        df (pd.DataFrame): 包含价格数据的 DataFrame
        threshold (float): 跳空阈值，默认 11%
    
    Returns:
        dict: 检测结果，包含异常记录
    
    Raises:
        ValueError: 当数据格式不正确时
    """
    pass
```

---

## 🧪 测试规范

### 编写测试

- 所有新功能必须附带测试
- 测试文件放在 `tests/` 目录
- 测试函数以 `test_` 开头

```python
# tests/test_quality_monitor.py
def test_price_jump_detection():
    """测试价格跳空检测"""
    monitor = DataQualityMonitor()
    # ... 测试逻辑
    assert result["abnormal_count"] == expected
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_risk_control.py

# 带覆盖率报告
pytest --cov=src tests/
```

---

## 📤 提交流程

### 1. 提交前检查

```bash
# 运行测试
pytest tests/

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/
```

### 2. 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)

```
feat: 添加新的 Alpha 因子
fix: 修复数据下载 bug
docs: 更新 README
test: 添加风控测试
refactor: 重构数据质量模块
```

### 3. 创建 Pull Request

1. Push 到 Fork 仓库
2. GitHub 上创建 Pull Request
3. 填写 PR 描述（说明变更内容、测试情况）
4. 等待 Code Review

---

## 🔍 Code Review 标准

### 代码质量

- [ ] 代码遵循风格指南
- [ ] 无明显的性能问题
- [ ] 错误处理完善

### 功能完整性

- [ ] 功能按预期工作
- [ ] 边界情况已处理
- [ ] 有充分的测试覆盖

### 文档

- [ ] 代码有适当的注释
- [ ] 更新了相关文档
- [ ] 添加了使用示例（如适用）

---

## 📋 贡献类型

### 报告 Bug

使用 GitHub Issues，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、OS 等）

### 提出新功能

使用 GitHub Issues 或 Discussions，包含：
- 功能描述
- 使用场景
- 实现思路（可选）

### 提交代码

- 修复 Bug
- 添加新功能
- 改进文档
- 优化性能
- 添加测试

---

## 🤝 行为准则

- 尊重他人观点
- 建设性反馈
- 开放包容
- 专注技术问题

---

## 📞 联系方式

- **Issues**: https://github.com/YOUR_USERNAME/quant-production/issues
- **Discussions**: https://github.com/YOUR_USERNAME/quant-production/discussions

---

感谢你的贡献！🎉
