# 🤖 自动提交脚本

> 定时自动提交代码到 GitHub

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `auto_commit.ps1` | PowerShell 自动提交脚本 |
| `auto_commit.bat` | 批处理启动脚本 |
| `auto_commit.py` | Python 自动提交脚本 |
| `install-scheduler.ps1` | 一键安装任务计划程序 |
| `SETUP_SCHEDULER.md` | 详细配置指南 |

---

## 🚀 快速开始

### 方法 1: 一键安装（推荐）

以**管理员身份**运行 PowerShell：

```powershell
cd E:\Quant_Production\scripts
powershell.exe -ExecutionPolicy Bypass -File "install-scheduler.ps1"
```

**效果**:
- ✅ 创建 Windows 任务计划程序
- ✅ 每天自动执行 3 次（09:00、14:00、20:00）
- ✅ 系统权限运行

---

### 方法 2: 手动配置

参考 `SETUP_SCHEDULER.md` 详细指南

---

## ⏰ 执行时间

默认每天 3 次：

| 时间 | 说明 |
|------|------|
| 09:00 | 早上提交（前一天晚上到今天早上的更改） |
| 14:00 | 下午提交（上午的更改） |
| 20:00 | 晚上提交（下午的更改） |

---

## 📝 日志文件

位置：`E:\Quant_Production\logs\auto_commit_YYYYMMDD.log`

示例：
```
[2026-04-06 09:00:01] Starting Auto Commit...
[2026-04-06 09:00:01] Directory: E:\Quant_Production
[2026-04-06 09:00:02] Checking Git status...
[2026-04-06 09:00:02] Found 3 changed files
[2026-04-06 09:00:02] Adding files...
[2026-04-06 09:00:03] Committing: chore: Auto commit 2026-04-06 09:00
[2026-04-06 09:00:04] Pushing to GitHub...
[2026-04-06 09:00:06] Auto commit completed successfully!
```

---

## 🔧 管理任务

### 查看任务

```powershell
Get-ScheduledTask -TaskName "Quant Production Auto Commit"
```

### 手动运行任务

```powershell
Start-ScheduledTask -TaskName "Quant Production Auto Commit"
```

### 查看任务历史

```powershell
Get-ScheduledTaskInfo -TaskName "Quant Production Auto Commit"
```

### 禁用任务

```powershell
Disable-ScheduledTask -TaskName "Quant Production Auto Commit"
```

### 启用任务

```powershell
Enable-ScheduledTask -TaskName "Quant Production Auto Commit"
```

### 删除任务

```powershell
Unregister-ScheduledTask -TaskName "Quant Production Auto Commit" -Confirm:$false
```

---

## ⚙️ 自定义配置

### 修改执行时间

编辑 `install-scheduler.ps1`，修改触发器时间：

```powershell
# 修改这些行
$triggers += New-ScheduledTaskTrigger -Daily -At 9am   # 改为你的时间
$triggers += New-ScheduledTaskTrigger -Daily -At 2pm
$triggers += New-ScheduledTaskTrigger -Daily -At 8pm
```

然后重新运行安装脚本。

### 修改执行频率

**每小时执行**:
```powershell
$triggers += New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration ([TimeSpan]::MaxValue)
```

**仅工作日执行**:
在任务计划程序中编辑任务，触发器 → 高级设置 → 每周 → 勾选周一到周五

---

## 🔍 故障排查

### 问题：任务不执行

**检查**:
1. 任务是否启用
2. 查看任务历史记录
3. 检查日志文件

### 问题：推送失败

**检查**:
1. 网络连接
2. 代理配置
3. Git 凭证

**解决**:
编辑 `auto_commit.ps1`，在开头添加代理配置：

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:20808"
$env:HTTPS_PROXY = "http://127.0.0.1:20808"
```

### 问题：没有日志

**检查**:
1. 日志目录是否存在：`E:\Quant_Production\logs`
2. 脚本是否有写入权限

---

## 📊 监控

### 查看最近的提交

```powershell
cd E:\Quant_Production
git log --oneline -10
```

### 查看本周提交统计

```powershell
cd E:\Quant_Production
git log --since="1 week ago" --oneline
```

### 查看日志文件大小

```powershell
Get-ChildItem "E:\Quant_Production\logs" | Select-Object Name, Length
```

---

## 🛡️ 安全说明

1. **Git 凭证**: 使用 Personal Access Token，不要使用密码
2. **任务权限**: 使用 SYSTEM 账户运行，确保有足够权限
3. **日志清理**: 定期清理旧日志（建议保留 30 天）

---

## 📞 需要帮助？

1. 查看详细指南：`SETUP_SCHEDULER.md`
2. 查看日志：`logs\auto_commit_YYYYMMDD.log`
3. 查看任务历史：任务计划程序 → 任务历史

---

> **提示**: 建议先手动测试脚本，确认无误后再安装定时任务！
