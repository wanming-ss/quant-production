#!/usr/bin/env python3
"""
Tushare 下载监控守护进程
自动监控并在失败时重启
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

def check_csv_growth():
    """检查 CSV 文件是否在增长"""
    import glob
    
    csv_files = glob.glob("E:/Quant_Production/Inbox/tushare_*.csv")
    sizes = {}
    
    for f in csv_files:
        sizes[f] = os.path.getsize(f)
    
    return sizes

def main():
    log("="*70)
    log("Tushare 下载监控守护进程启动")
    log("="*70)
    
    # 启动批量下载
    log("启动全接口批量下载...")
    process = subprocess.Popen(
        [sys.executable, "E:/Quant_Production/Artifacts/download_all_apis.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    
    last_sizes = check_csv_growth()
    last_check_time = time.time()
    restart_count = 0
    
    while True:
        time.sleep(60)  # 每分钟检查一次
        
        # 检查进程状态
        if process.poll() is not None:
            # 进程已结束
            restart_count += 1
            log(f"⚠️  下载进程已结束（退出码: {process.returncode}）")
            log(f"🔄 第 {restart_count} 次重启...")
            
            # 等待 30 秒让 API 限制重置
            time.sleep(30)
            
            # 重启进程
            process = subprocess.Popen(
                [sys.executable, "E:/Quant_Production/Artifacts/download_all_apis.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )
            log("✅ 已重启")
        
        # 检查文件增长
        current_time = time.time()
        if current_time - last_check_time >= 300:  # 每 5 分钟检查文件增长
            current_sizes = check_csv_growth()
            
            total_growth = 0
            for f, new_size in current_sizes.items():
                old_size = last_sizes.get(f, 0)
                growth = new_size - old_size
                if growth > 0:
                    total_growth += growth
                    log(f"📈 {os.path.basename(f)}: +{growth/1024/1024:.2f} MB")
            
            if total_growth > 0:
                log(f"📊 总计增长: {total_growth/1024/1024:.2f} MB")
            else:
                log("⚠️  5分钟内无文件增长")
            
            last_sizes = current_sizes
            last_check_time = current_time

if __name__ == "__main__":
    main()
