#!/usr/bin/env python3
"""
DolphinDB 自动增量导入
监控 CSV 变化，导入新增数据
"""
import dolphindb as ddb
import pandas as pd
import time
import os
from datetime import datetime

CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
CHECK_INTERVAL = 120  # 每 2 分钟检查一次
BATCH_SIZE = 100000

def get_csv_info():
    """获取 CSV 信息"""
    try:
        df = pd.read_csv(CSV_PATH)
        return len(df), df['symbol'].nunique()
    except:
        return 0, 0

def import_batch(start_row, end_row):
    """导入指定范围的数据"""
    print(f"\n{'='*70}")
    print(f"导入批次 {datetime.now()}")
    print(f"行范围: {start_row:,} - {end_row:,}")
    
    # 读取指定范围
    df = pd.read_csv(CSV_PATH, skiprows=range(1, start_row+1), nrows=end_row-start_row)
    df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'volume', 'amount']
    
    # 连接 DolphinDB
    session = ddb.session()
    session.connect("localhost", 8848, "admin", "123456")
    
    # 分批导入
    total = len(df)
    for i in range(0, total, BATCH_SIZE):
        batch = df.iloc[i:i+BATCH_SIZE]
        temp_csv = f"E:/Quant_Production/Inbox/temp_import_{i//BATCH_SIZE}.csv"
        batch.to_csv(temp_csv, index=False)
        
        script = f"""
        t = loadText("{temp_csv}")
        t = select symbol, date, open, high, low, close, pre_close, change, pct_chg, volume, amount from t
        daily = loadTable("dfs://tushare", "daily")
        append!(daily, t)
        """
        
        try:
            session.run(script)
            print(f"  ✅ {i+1}-{min(i+BATCH_SIZE, total):,}")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)[:80]}")
    
    # 验证
    count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
    print(f"\n✅ 导入完成！表中总记录: {count.values[0][0]:,}")
    return end_row

print("="*70)
print("DolphinDB 自动增量导入")
print("="*70)
print(f"监控: {CSV_PATH}")
print(f"检查间隔: {CHECK_INTERVAL} 秒")
print("="*70)

# 获取当前已导入的记录数
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
current_count = session.run("select count(*) from loadTable('dfs://tushare', 'daily')")
last_imported = current_count.values[0][0]
print(f"\n📊 当前已导入: {last_imported:,} 条")

while True:
    try:
        total_rows, total_stocks = get_csv_info()
        
        if total_rows > last_imported:
            print(f"\n📈 发现新数据: {last_imported:,} → {total_rows:,} (+{total_rows-last_imported:,})")
            last_imported = import_batch(last_imported, total_rows)
        else:
            print(f"\n⏳ {datetime.now().strftime('%H:%M:%S')} 无变化 ({total_rows:,} 条)")
        
        time.sleep(CHECK_INTERVAL)
        
    except KeyboardInterrupt:
        print("\n\n停止监控")
        break
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        time.sleep(CHECK_INTERVAL)
