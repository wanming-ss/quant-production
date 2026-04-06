#!/usr/bin/env python3
"""
Tushare 全接口并行下载
同时下载多个接口，不限速
"""
import subprocess
import sys
import os

# 定义所有要下载的接口
APIS = [
    ('income', 'tushare_income.csv'),
    ('balancesheet', 'tushare_balancesheet.csv'),
    ('cashflow', 'tushare_cashflow.csv'),
    ('fina_indicator', 'tushare_fina_indicator.csv'),
    ('forecast', 'tushare_forecast.csv'),
    ('express', 'tushare_express.csv'),
    ('limit_list', 'tushare_limit_list.csv'),
    ('top_list', 'tushare_top_list.csv'),
    ('stk_pledge', 'tushare_stk_pledge.csv'),
    ('block_trade', 'tushare_block_trade.csv'),
]

print("="*70)
print("Tushare 全接口并行下载")
print("="*70)
print(f"同时启动 {len(APIS)} 个下载进程")
print("="*70)

# 同时启动所有下载
processes = []
for api, csv in APIS:
    print(f"\n🚀 启动 {api} -> {csv}")
    
    # 创建简单下载脚本
    script_content = f'''
import tushare as ts
import pandas as pd
import time
from datetime import datetime

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

CSV_PATH = "E:/Quant_Production/Inbox/{csv}"

print(f"[{{datetime.now()}}] 开始下载 {api}...")

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

# 检查已有数据
if os.path.exists(CSV_PATH):
    try:
        existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
        if 'ts_code' in existing.columns:
            completed = set(existing['ts_code'].unique())
        elif 'symbol' in existing.columns:
            completed = set(existing['symbol'].unique())
        else:
            completed = set()
        stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
        print(f"  已完成: {{len(completed)}} 只，剩余: {{len(stock_df)}} 只")
    except:
        pass

all_data = []
for i, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    
    try:
        df = pro.{api}(ts_code=ts_code, start_date='20160101', end_date='20250324')
        if df is not None and not df.empty:
            all_data.append(df)
        
        if i % 100 == 0:
            print(f"  [{{i}}/{{len(stock_df)}}] {{ts_code}}")
            if all_data:
                batch = pd.concat(all_data, ignore_index=True)
                batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
                all_data = []
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    # 无延迟
    # time.sleep(0)

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

print(f"[{{datetime.now()}}] {api} 完成!")
'''
    
    # 保存临时脚本
    script_file = f"E:/Quant_Production/Artifacts/download_{api}.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 启动进程
    p = subprocess.Popen(
        [sys.executable, script_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    processes.append((api, p))
    print(f"   ✅ PID: {p.pid}")

print(f"\n{'='*70}")
print(f"已启动 {len(processes)} 个并行下载进程")
print(f"{'='*70}")

# 等待所有进程完成
print("\n⏳ 等待所有下载完成...")
for api, p in processes:
    p.wait()
    print(f"✅ {api} 完成 (退出码: {p.returncode})")

print(f"\n{'='*70}")
print("所有下载完成！")
print(f"{'='*70}")
