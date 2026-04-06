# 🤖 自动提交配置指南

> 设置定时任务，每天自动提交代码到 GitHub

---

## 📋 方案选择

### 方案 1: Windows 任务计划程序（推荐）⭐
- ✅ 系统自带
- ✅ 稳定可靠
- ✅ 图形界面配置

### 方案 2: Python 脚本 + cron（Linux/Mac）
- ✅ 跨平台
- ✅ 配置简单

### 方案 3: GitHub Actions
- ✅ 云端执行
- ✅ 无需本地运行

---

## 🪟 方案 1: Windows 任务计划程序

### 步骤 1: 打开任务计划程序

1. 按 `Win + R`
2. 输入 `taskschd.msc`
3. 回车

---

### 步骤 2: 创建基本任务

1. 点击 **"创建基本任务..."**
2. 填写：
   - **名称**: `Quant Production Auto Commit`
   - **描述**: `每天自动提交代码到 GitHub`
3. 点击 **"下一步"**

---

### 步骤 3: 设置触发器

选择 **"每天"**，然后点击 **"下一步"**

设置时间：
- **开始时间**: `08:00:00`
- **重复间隔**: `1` 天

点击 **"下一步"**

---

### 步骤 4: 设置操作

选择 **"启动程序"**，点击 **"下一步"**

填写：
- **程序/脚本**: `powershell.exe`
- **添加参数**: 
```powershell
-ExecutionPolicy Bypass -File "E:\Quant_Production\scripts\auto_commit.ps1"
```
- **起始于**: `E:\Quant_Production`

点击 **"下一步"**

---

### 步骤 5: 完成

1. 勾选 **"当单击完成时，打开此任务的属性对话框"**
2. 点击 **"完成"**

---

### 步骤 6: 高级设置

在属性对话框中：

1. **常规** 选项卡:
   - ✅ 勾选 **"使用最高权限运行"**
   - ✅ 勾选 **"不管用户是否登录都要运行"**
   - 配置：`Windows 10`

2. **条件** 选项卡:
   - ❌ 取消勾选 **"只有在计算机使用交流电源时才启动此任务"**
   - ✅ 勾选 **"如果计算机改用电池电源，则停止"**（笔记本）

3. **设置** 选项卡:
   - ✅ 勾选 **"如果任务运行时间超过以下时间，停止任务"**: `1 小时`
   - ✅ 勾选 **"如果任务失败，重新启动每隔"**: `5 分钟`
   - ✅ 勾选 **"尝试重新启动次数"**: `3`

点击 **"确定"**

---

## 📝 创建 PowerShell 脚本

创建文件：`E:\Quant_Production\scripts\auto_commit.ps1`

```powershell
# 自动提交脚本 - PowerShell 版本

$ErrorActionPreference = "Stop"

# 项目目录
$PROJECT_ROOT = "E:\Quant_Production"
$LOG_FILE = "$PROJECT_ROOT\logs\auto_commit_$(Get-Date -Format 'yyyyMMdd').log"

# 创建日志目录
$logDir = Split-Path $LOG_FILE -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$timestamp] $Message"
    Add-Content -Path $LOG_FILE -Value $logLine
    Write-Host $logLine
}

try {
    Write-Log "=========================================="
    Write-Log "🤖 Auto Commit Started"
    Write-Log "=========================================="
    
    # 进入项目目录
    Set-Location $PROJECT_ROOT
    Write-Log "📁 目录：$PROJECT_ROOT"
    
    # 检查 Git 状态
    Write-Log "🔍 检查 Git 状态..."
    $status = git status --porcelain
    
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Log "✅ 没有更改，无需提交"
        Write-Log "=========================================="
        exit 0
    }
    
    $fileCount = ($status -split "`n").Count
    Write-Log "📝 发现 $fileCount 个更改的文件"
    
    # 添加文件
    Write-Log "📦 添加文件..."
    git add -A
    if ($LASTEXITCODE -ne 0) {
        throw "Git add 失败"
    }
    
    # 提交
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $commitMsg = "chore: Auto commit $timestamp`n`n🤖 Automated update by CI/CD bot"
    Write-Log "💾 提交：$commitMsg"
    
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ℹ️  没有新更改或提交失败"
        Write-Log "=========================================="
        exit 0
    }
    
    # 推送
    Write-Log "🚀 推送到 GitHub..."
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        throw "Git push 失败"
    }
    
    Write-Log "✅ 自动提交成功！"
    Write-Log "=========================================="
    
} catch {
    Write-Log "❌ 错误：$($_.Exception.Message)"
    Write-Log "=========================================="
    exit 1
}
```

---

## 📊 推荐执行时间

### 方案 A: 每天 3 次（推荐）

创建 3 个任务：

| 任务名 | 时间 | 说明 |
|--------|------|------|
| Auto Commit - Morning | 09:00 | 早上提交 |
| Auto Commit - Afternoon | 14:00 | 下午提交 |
| Auto Commit - Evening | 20:00 | 晚上提交 |

### 方案 B: 每小时提交

在任务属性的 **"触发器"** 中：
- 选择 **"高级设置"**
- 勾选 **"重复任务间隔"**: `1 小时`
- 持续时间：`无限期`

### 方案 C: 工作日提交

在任务属性的 **"触发器"** 中：
- 选择 **"每周"**
- 勾选：**周一、周二、周三、周四、周五**

---

## 🔧 测试任务

### 手动运行任务

1. 在任务计划程序中找到任务
2. 右键点击任务
3. 选择 **"运行"**
4. 查看日志：`E:\Quant_Production\logs\auto_commit_YYYYMMDD.log`

### 查看任务历史

1. 双击任务
2. 点击 **"历史记录"** 选项卡
3. 查看执行记录

---

## 📝 日志文件

日志位置：`E:\Quant_Production\logs\auto_commit_YYYYMMDD.log`

示例内容：
```
[2026-04-06 09:00:01] ==========================================
[2026-04-06 09:00:01] 🤖 Auto Commit Started
[2026-04-06 09:00:01] ==========================================
[2026-04-06 09:00:01] 📁 目录：E:\Quant_Production
[2026-04-06 09:00:02] 🔍 检查 Git 状态...
[2026-04-06 09:00:02] 📝 发现 3 个更改的文件
[2026-04-06 09:00:02] 📦 添加文件...
[2026-04-06 09:00:03] 💾 提交：chore: Auto commit 2026-04-06 09:00
[2026-04-06 09:00:04] 🚀 推送到 GitHub...
[2026-04-06 09:00:06] ✅ 自动提交成功！
[2026-04-06 09:00:06] ==========================================
```

---

## 🐍 方案 2: 使用 Python 脚本 + 任务计划程序

如果你更喜欢 Python 版本：

### 创建批处理文件

`E:\Quant_Production\scripts\auto_commit.bat`

```batch
@echo off
cd /d "E:\Quant_Production"
python scripts\auto_commit.py >> logs\auto_commit.log 2>&1
```

### 在任务计划程序中配置

- **程序/脚本**: `E:\Quant_Production\scripts\auto_commit.bat`
- **起始于**: `E:\Quant_Production`

---

## ☁️ 方案 3: GitHub Actions（云端）

创建文件：`.github/workflows/auto-sync.yml`

```yaml
name: Auto Sync

on:
  schedule:
    # 每天 09:00, 14:00, 20:00 (UTC+8)
    - cron: '0 1 * * *'   # 09:00 Beijing
    - cron: '0 6 * * *'   # 14:00 Beijing
    - cron: '0 12 * * *'  # 20:00 Beijing

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Check for changes
        run: |
          git status
          # 这里可以添加检查本地更改的逻辑
      
      - name: Commit and push if changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --quiet && git diff --staged --quiet || (
            git commit -m "chore: Auto sync $(date -u)"
            git push
          )
```

---

## ✅ 验证清单

设置完成后，检查：

- [ ] 任务已创建
- [ ] 任务权限正确（最高权限运行）
- [ ] 触发器时间设置正确
- [ ] 脚本路径正确
- [ ] 日志目录存在
- [ ] 手动测试运行成功
- [ ] 查看历史记录确认执行

---

## 🔍 故障排查

### 问题：任务不执行

**检查**:
1. 任务是否启用
2. 用户权限是否正确
3. 脚本路径是否正确
4. 查看任务历史记录

### 问题：Git 推送失败

**检查**:
1. 网络连接
2. Git 凭证是否有效
3. 代理配置是否正确

### 问题：没有日志

**检查**:
1. 日志目录是否存在
2. 脚本是否有写入权限
3. PowerShell 执行策略

---

## 📞 需要帮助？

查看日志文件：
`E:\Quant_Production\logs\auto_commit_YYYYMMDD.log`

---

> **提示**: 建议先手动测试脚本，确认无误后再设置定时任务！
