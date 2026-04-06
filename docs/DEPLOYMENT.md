# 部署指南

---

## 📋 部署前检查

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| OS | Windows 10 / Linux | Windows 11 / Ubuntu 22.04 |
| CPU | 4 核心 | 8 核心+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 100GB 可用 | 500GB+ SSD |
| Python | 3.10 | 3.11+ |

### 外部依赖

- [ ] Tushare API Token（https://tushare.pro/）
- [ ] DolphinDB（https://dolphindb.com/）
- [ ] Git

---

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/quant-production.git
cd quant-production
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# Windows (PowerShell)
$env:TUSHARE_TOKEN = "your_token_here"
$env:DOLPHINDB_PASSWORD = "your_password_here"

# Linux/Mac
export TUSHARE_TOKEN="your_token_here"
export DOLPHINDB_PASSWORD="your_password_here"
```

### 5. 复制配置文件

```bash
# 主配置
cp config.yaml.example config.yaml

# 数据库配置
cp config/database.yaml.example config/database.yaml

# Tushare 配置
cp config/tushare.yaml.example config/tushare.yaml
```

### 6. 编辑配置

编辑 `config.yaml`，确保路径和参数正确：

```yaml
project:
  name: "quant-production"
  version: "1.0.0"
  
data:
  tushare:
    enabled: true
    token: "${TUSHARE_TOKEN}"
    
database:
  dolphindb:
    enabled: true
    host: "localhost"
    port: 8848
```

---

## 🗄️ DolphinDB 部署

### 1. 下载 DolphinDB

从官网下载：https://dolphindb.com/downloads.html

### 2. 启动服务

```bash
# Windows
cd dolphindb-windows
dolphindb.exe

# Linux
cd dolphindb-linux
./dolphindb
```

### 3. 验证连接

```python
import dolphindb as ddb

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("✅ Connected to DolphinDB")
```

---

## ✅ 验证部署

### 运行生产就绪检查

```bash
python src/production/production_master.py
```

**预期输出**:
```
======================================================================
 QUANT PRODUCTION - PRODUCTION GRADE SYSTEM
======================================================================
Time: 2026-04-06 16:00:00
======================================================================

======================================================================
 STAGE 1: DATA QUALITY CHECK
======================================================================
...
✅ DATA QUALITY CHECK PASSED

======================================================================
 STAGE 2: RISK CONTROL TEST
======================================================================
...
✅ Risk control system operational

======================================================================
 STAGE 3: MONITORING & BACKUP
======================================================================
...
✅ Backup verification PASSED

======================================================================
 PRODUCTION READINESS REPORT
======================================================================
✅ data_quality: PASS
✅ risk_control: PASS
✅ monitoring: PASS

======================================================================
🎉 SYSTEM IS PRODUCTION READY
🏆 跑得稳、跑得久、跑得合规
======================================================================
```

---

## 🔧 故障排查

### 问题：Tushare API 调用失败

**检查**:
1. Token 是否正确
2. 积分是否足够
3. 网络是否通畅

**解决**:
```bash
# 测试 API 连接
python -c "import tushare as ts; ts.set_token('your_token'); print(ts.pro_api())"
```

### 问题：DolphinDB 连接失败

**检查**:
1. 服务是否运行
2. 端口是否正确（默认 8848）
3. 用户名密码是否正确

**解决**:
```bash
# 检查端口
netstat -ano | findstr 8848

# 重启 DolphinDB
# Windows: 关闭后重新运行 dolphindb.exe
```

### 问题：依赖安装失败

**解决**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📊 生产环境配置

### 1. 日志配置

确保日志目录存在且有写入权限：

```bash
mkdir logs
```

### 2. 备份策略

配置自动备份（建议使用系统定时任务）：

```bash
# Windows 任务计划程序
# Linux crontab
0 23 * * * cd /path/to/quant-production && python src/monitoring/backup_manager.py
```

### 3. 监控告警

配置监控告警（邮件/短信/钉钉）：

```yaml
# config.yaml
monitoring:
  alerts:
    enabled: true
    channels:
      - type: email
        to: admin@example.com
      - type: dingtalk
        webhook: https://oapi.dingtalk.com/robot/send?access_token=xxx
```

---

## 🔄 更新部署

### 从 Git 更新

```bash
git pull origin main

# 重新安装依赖（如有更新）
pip install -r requirements.txt --upgrade

# 运行迁移（如有）
python scripts/migrate.py

# 验证部署
python src/production/production_master.py
```

---

## 📝 部署清单

部署完成后，确认以下项目：

- [ ] Python 虚拟环境已创建
- [ ] 所有依赖已安装
- [ ] 配置文件已复制并编辑
- [ ] 环境变量已设置
- [ ] DolphinDB 服务已启动
- [ ] 生产就绪检查通过
- [ ] 日志目录已创建
- [ ] 备份策略已配置

---

> **版本**: 1.0.0  
> **最后更新**: 2026-04-06
