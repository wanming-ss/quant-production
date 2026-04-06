@echo off
REM 自动提交批处理文件
cd /d "E:\Quant_Production"
powershell.exe -ExecutionPolicy Bypass -File "scripts\auto_commit.ps1"
