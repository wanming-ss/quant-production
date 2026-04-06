# Auto Commit Script - PowerShell Version
$ErrorActionPreference = "Stop"

$PROJECT_ROOT = "E:\Quant_Production"
$LOG_FILE = "$PROJECT_ROOT\logs\auto_commit_$(Get-Date -Format 'yyyyMMdd').log"

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
    Write-Log "Starting Auto Commit..."
    Set-Location $PROJECT_ROOT
    Write-Log "Directory: $PROJECT_ROOT"
    
    git config user.name "AI-Native Quant Team" 2>$null
    git config user.email "quant@example.com" 2>$null
    
    Write-Log "Checking Git status..."
    $status = git status --porcelain
    
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Log "No changes to commit"
        exit 0
    }
    
    $fileCount = ($status -split "`n").Count
    Write-Log "Found $fileCount changed files"
    
    Write-Log "Adding files..."
    git add -A
    if ($LASTEXITCODE -ne 0) { throw "Git add failed" }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $commitMsg = "chore: Auto commit $timestamp"
    Write-Log "Committing: $commitMsg"
    
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Write-Log "No new changes or commit failed"
        exit 0
    }
    
    Write-Log "Pushing to GitHub..."
    git push origin main
    if ($LASTEXITCODE -ne 0) { throw "Git push failed" }
    
    Write-Log "Auto commit completed successfully!"
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
