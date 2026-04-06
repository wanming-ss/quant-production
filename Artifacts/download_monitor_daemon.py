#!/usr/bin/env python3
"""
自动监控下载守护进程
自动重启失败的下载任务
"""
import subprocess
import time
import os
import sys
from datetime import datetime

LOG_FILE = "E:/Quant_Production/Inbox/download_monitor.log"

def log(msg):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def check_and_restart():
    """检查并重启下载"""
    import psutil
    
    # 检查是否有 Python 进程在运行
    python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                       if p.info['name'] == 'python.exe' and 'download' in str(p.info['cmdline'])]
    
    if not python_processes:
        log("⚠️  无下载进程，准备重启...")
        
        # 检查哪些文件未完成
        missing = []
        if not os.path.exists("E:/Quant_Production/Inbox/tushare_stk_reward.csv"):
            missing.append("stk_reward")
        if not os.path.exists("E:/Quant_Production/Inbox/tushare_stk_pledge.csv"):
            missing.append("stk_pledge")
        
        if missing:
            log(f"🔄 重启下载: {', '.join(missing)}")
            
            # 启动下载脚本
            subprocess.Popen(
                [sys.executable, "E:/Quant_Production/Artifacts/download_last_3.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )
        else:
            log("✅ 所有下载完成")
            return False
    else:
        log(f"✅ 下载进程运行中 (PID: {python_processes[0].info['pid']})")
    
    return True

def main():
    """主循环"""
    log("="*70)
    log("下载监控守护进程启动")
    log("="*70)
    
    while True:
        running = check_and_restart()
        if not running:
            log("✅ 所有任务完成，守护进程退出")
            break
        
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
