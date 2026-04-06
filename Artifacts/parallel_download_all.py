#!/usr/bin/env python3
"""
Tushare 全接口并行下载 - 终极版
同时下载所有未完成接口
"""
import subprocess
import sys
import os
from datetime import datetime

# 所有要下载的接口配置
APIS = [
    # 财务数据（优先级1）
    ('income', 'tushare_income.csv', '财务利润表'),
    ('balancesheet', 'tushare_balancesheet.csv', '资产负债表'),
    ('cashflow', 'tushare_cashflow.csv', '现金流量表'),
    ('fina_indicator', 'tushare_fina_indicator.csv', '财务指标'),
    ('forecast', 'tushare_forecast.csv', '业绩预告'),
    ('express', 'tushare_express.csv', '业绩快报'),
    
    # 市场数据（优先级2）
    ('moneyflow', 'tushare_moneyflow.csv', '资金流向'),
    ('stk_holdernumber', 'tushare_holdernumber.csv', '股东人数'),
    ('stk_holdertrade', 'tushare_holdertrade.csv', '股东增减持'),
    
    # 股本相关（优先级3）
    ('stk_pledge', 'tushare_stk_pledge.csv', '股权质押'),
    ('stk_reward', 'tushare_stk_reward.csv', '股票回购'),
    ('new_share', 'tushare_new_share.csv', '新股上市'),
    
    # 其他（优先级4）
    ('block_trade', 'tushare_block_trade.csv', '大宗交易'),
    ('top_list', 'tushare_top_list.csv', '龙虎榜'),
    ('top_inst', 'tushare_top_inst.csv', '龙虎榜机构'),
]

print("="*70)
print("Tushare 全接口并行下载")
print(f"总计: {len(APIS)} 个接口")
print("="*70)

processes = []

for i, (api, csv, desc) in enumerate(APIS, 1):
    print(f"\n[{i}/{len(APIS)}] 启动 {api}: {desc}")
    
    # 创建下载脚本
    script = f'''
import tushare as ts
import pandas as pd
from datetime import datetime
import time
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = "http://119.45.170.23"

CSV_PATH = "E:/Quant_Production/Inbox/{csv}"

print(f"[{{datetime.now()}}] 开始 {api}...")

stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

if os.path.exists(CSV_PATH):
    try:
        existing = pd.read_csv(CSV_PATH, low_memory=False, on_bad_lines='skip')
        if 'ts_code' in existing.columns:
            completed = set(existing['ts_code'].unique())
        else:
            completed = set()
        stock_df = stock_df[~stock_df['ts_code'].isin(completed)]
        print(f"  已完成: {{len(completed)}} 只")
    except:
        pass

remaining = len(stock_df)
print(f"  剩余: {{remaining}} 只")

if remaining == 0:
    print("  ✅ 完成！")
    exit(0)

all_data = []
for j, (_, row) in enumerate(stock_df.iterrows(), 1):
    ts_code = row['ts_code']
    
    if j % 50 == 1:
        print(f"  [{{j}}/{{remaining}}] {{ts_code}}")
    
    try:
        if '{api}' == 'limit_list':
            continue  # skip
        else:
            df = getattr(pro, '{api}')(ts_code=ts_code, start_date='20160101', end_date='20250324')
        
        if df is not None and not df.empty:
            all_data.append(df)
    except Exception as e:
        if "500次" in str(e):
            time.sleep(30)
    
    time.sleep(0.2)
    
    if j % 100 == 0 and all_data:
        batch = pd.concat(all_data, ignore_index=True)
        batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))
        print(f"  💾 保存 {{len(batch):,}} 条")
        all_data = []

if all_data:
    batch = pd.concat(all_data, ignore_index=True)
    batch.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

print(f"[{{datetime.now()}}] {api} 完成")
'''
    
    # 保存脚本
    script_file = f"E:/Quant_Production/Artifacts/download_{api}.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    # 启动进程
    p = subprocess.Popen(
        [sys.executable, script_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    processes.append((api, desc, p))
    print(f"   ✅ PID: {p.pid}")

print(f"\n{'='*70}")
print(f"已启动 {len(processes)} 个并行下载进程")
print(f"{'='*70}")

# 等待所有完成
print("\n⏳ 等待所有下载完成...")
for api, desc, p in processes:
    p.wait()
    print(f"{'✅' if p.returncode == 0 else '❌'} {api}: {desc} (退出码: {p.returncode})")

print(f"\n{'='*70}")
print("所有下载完成！")
print(f"{'='*70}")
