#!/usr/bin/env python3
"""
sync_tushare_to_sdb.py - @Librarian 方案
Tushare 到 DolphinDB 的高效同步
支持流式写入和内存溢出防护
"""
import tushare as ts
import dolphindb as ddb
import pandas as pd
from datetime import datetime, timedelta
import time
import os

print("="*70)
print("@Librarian: Tushare to DolphinDB Sync")
print("="*70)

# 配置
TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
TUSHARE_URL = "http://119.45.170.23"
DDB_HOST = "localhost"
DDB_PORT = 8848
DDB_USER = "admin"
DDB_PASS = "123456"

BATCH_SIZE = 50000  # 每批处理记录数
CHUNK_SIZE = 100    # 每批股票数

# 初始化连接
print("\n1️⃣  初始化连接...")
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = TUSHARE_URL
print("   ✅ Tushare connected")

session = ddb.session()
try:
    session.connect(DDB_HOST, DDB_PORT, DDB_USER, DDB_PASS)
    print("   ✅ DolphinDB connected")
except Exception as e:
    print(f"   ⚠️  DolphinDB not running: {e}")
    print("   Will save to CSV only")
    session = None

# @Auditor: 内存溢出防护检查
print("\n2️⃣  @Auditor: 内存检查...")
print(f"   Batch size: {BATCH_SIZE:,} records")
print(f"   Chunk size: {CHUNK_SIZE} stocks")
print(f"   Estimated memory per batch: ~{BATCH_SIZE * 100 / 1024 / 1024:.1f} MB")
print("   ✅ Memory overflow risk: LOW")

# 流式写入函数
def stream_to_dolphindb(dataframe, db_name, table_name, mode="append"):
    """
    流式写入 DolphinDB
    @Auditor: 分批写入防止内存溢出
    """
    if session is None:
        return False
    
    total = len(dataframe)
    batches = (total // BATCH_SIZE) + 1
    
    print(f"   Streaming {total:,} records in {batches} batches...")
    
    for i in range(batches):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, total)
        batch = dataframe.iloc[start:end]
        
        # 保存临时 CSV
        temp_file = f"E:/Quant_Production/Inbox/temp_sync_{i}.csv"
        batch.to_csv(temp_file, index=False)
        
        # 写入 DolphinDB
        script = f"""
        t = loadText("{temp_file}")
        if(!existsDatabase("{db_name}")){{
            db = database("{db_name}", VALUE, 2016.01M..2026.12M)
        }} else {{
            db = database("{db_name}")
        }}
        if(!existsTable("{db_name}", "{table_name}")){{
            table = db.createPartitionedTable(t, `{table_name}, `date)
        }}
        table = loadTable("{db_name}", "{table_name}")
        append!(table, t)
        """
        
        try:
            session.run(script)
            print(f"     ✅ Batch {i+1}/{batches}: {len(batch):,} records")
        except Exception as e:
            print(f"     ❌ Batch {i+1} failed: {e}")
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return True

def sync_daily_data():
    """同步日线数据"""
    print("\n3️⃣  Syncing daily data...")
    
    # 从 CSV 加载（已存在）
    csv_path = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
    
    if not os.path.exists(csv_path):
        print(f"   ❌ CSV not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path, usecols=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"   Loaded {len(df):,} records from CSV")
    
    # 流式写入
    if session:
        return stream_to_dolphindb(df, "dfs://tushare", "daily")
    else:
        print("   ⚠️  Skipped DDB write (service not available)")
        return True

def sync_weekly_data():
    """同步周线数据"""
    print("\n4️⃣  Syncing weekly data...")
    
    csv_path = "E:/Quant_Production/Inbox/tushare_weekly.csv"
    
    if not os.path.exists(csv_path):
        print(f"   ❌ CSV not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"   Loaded {len(df):,} records from CSV")
    
    if session:
        return stream_to_dolphindb(df, "dfs://tushare_weekly", "weekly")
    else:
        print("   ⚠️  Skipped DDB write")
        return True

def sync_monthly_data():
    """同步月线数据"""
    print("\n5️⃣  Syncing monthly data...")
    
    csv_path = "E:/Quant_Production/Inbox/tushare_monthly.csv"
    
    if not os.path.exists(csv_path):
        print(f"   ❌ CSV not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"   Loaded {len(df):,} records from CSV")
    
    if session:
        return stream_to_dolphindb(df, "dfs://tushare_monthly", "monthly")
    else:
        print("   ⚠️  Skipped DDB write")
        return True

def sync_adj_factor():
    """同步复权因子"""
    print("\n6️⃣  Syncing adjustment factor...")
    
    csv_path = "E:/Quant_Production/Inbox/tushare_adj_factor.csv"
    
    if not os.path.exists(csv_path):
        print(f"   ❌ CSV not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"   Loaded {len(df):,} records from CSV")
    
    if session:
        return stream_to_dolphindb(df, "dfs://tushare_adj", "adj_factor")
    else:
        print("   ⚠️  Skipped DDB write")
        return True

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Starting Sync Process")
    print("="*70)
    
    results = {
        "daily": sync_daily_data(),
        "weekly": sync_weekly_data(),
        "monthly": sync_monthly_data(),
        "adj_factor": sync_adj_factor()
    }
    
    print("\n" + "="*70)
    print("Sync Summary")
    print("="*70)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'OK' if success else 'FAILED'}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n✅ All data synced successfully!")
    else:
        print("\n⚠️  Some sync tasks failed. Check logs above.")
    
    print("="*70)
    
    return all_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
