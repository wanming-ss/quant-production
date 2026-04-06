# Install Auto Commit Scheduler
# 一键安装自动提交任务计划程序

$TASK_NAME = "Quant Production Auto Commit"
$SCRIPT_PATH = "E:\Quant_Production\scripts\auto_commit.ps1"
$PROJECT_ROOT = "E:\Quant_Production"

Write-Host "=========================================="
Write-Host " Installing Auto Commit Scheduler"
Write-Host "=========================================="

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run as Administrator!" -ForegroundColor Red
    exit 1
}

# 创建日志目录
$logDir = "$PROJECT_ROOT\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Write-Host "Created log directory: $logDir"
}

# 删除旧任务（如果存在）
$existingTask = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
}

# 创建任务操作
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$SCRIPT_PATH`"" `
    -WorkingDirectory $PROJECT_ROOT

# 创建每天 3 次的触发器
$triggers = @()

# 早上 9 点
$triggers += New-ScheduledTaskTrigger -Daily -At 9am -RandomDelay (New-TimeSpan -Minutes 5)

# 下午 2 点
$triggers += New-ScheduledTaskTrigger -Daily -At 2pm -RandomDelay (New-TimeSpan -Minutes 5)

# 晚上 8 点
$triggers += New-ScheduledTaskTrigger -Daily -At 8pm -RandomDelay (New-TimeSpan -Minutes 5)

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 创建主体（使用最高权限）
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# 注册任务
try {
    Register-ScheduledTask `
        -TaskName $TASK_NAME `
        -Action $action `
        -Trigger $triggers `
        -Settings $settings `
        -Principal $principal `
        -Description "Automatically commit and push code to GitHub every day" `
        -ErrorAction Stop
    
    Write-Host "Task registered successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================="
Write-Host " Installation Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Task Name: $TASK_NAME"
Write-Host "Script: $SCRIPT_PATH"
Write-Host "Schedule: Daily at 09:00, 14:00, 20:00"
Write-Host "Log: $PROJECT_ROOT\logs\auto_commit_YYYYMMDD.log"
Write-Host ""
Write-Host "To view task:"
Write-Host "  Get-ScheduledTask -TaskName `"$TASK_NAME`""
Write-Host ""
Write-Host "To run manually:"
Write-Host "  Start-ScheduledTask -TaskName `"$TASK_NAME`""
Write-Host ""
Write-Host "To view logs:"
Write-Host "  Get-ScheduledTaskInfo -TaskName `"$TASK_NAME`""
Write-Host "=========================================="
