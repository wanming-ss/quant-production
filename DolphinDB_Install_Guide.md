# DolphinDB 安装与启动指南

## 当前状态

❌ **DolphinDB 未安装**

## 安装步骤

### 1. 下载 DolphinDB

访问官网: https://www.dolphindb.com/

下载 Windows 版本:
- 文件名: `DolphinDB_Win64_V2.00.9.1.zip`
- 解压到: `C:\DolphinDB`

### 2. 启动服务

```powershell
# 单节点模式
cd C:\DolphinDB\server
dolphindb.exe -localHost 0.0.0.0:8848
```

### 3. 验证连接

```python
import dolphindb as ddb
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("Connected!")
```

## 当前替代方案

由于 DolphinDB 未安装，当前使用:

1. **CSV 数据文件** - 已完成下载 (2.5GB+)
2. **Qlib 官方数据** - 已配置 (~/.qlib/qlib_data/cn_data)
3. **LightGBM 训练** - 可直接从 CSV 训练

## 建议

**短期**: 使用 Qlib + CSV 继续训练
**长期**: 安装 DolphinDB 实现分布式计算

---
当前时间: 2026-03-25 00:10
