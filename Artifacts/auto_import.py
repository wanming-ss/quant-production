#!/usr/bin/env python3
"""
DolphinDB 自动增量导入
监控 CSV 变化，自动导入新数据
"""
import dolphindb as ddb
import pandas as pd
import time
import os
from datetime import datetime

CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_2016_2025.csv"
CHECK_INTERVAL = 60  # 每分钟检查一次

def get_file_size():
    """获取文件大小"""
    try:
        return os.path.getsize(CSV_PATH)
    except:
        return 0

def import_to_dolphindb():
    """导入数据到 DolphinDB"""
    print(f"\n{'='*70}")
    print(f"DolphinDB 自动导入 - {datetime.now()}")
    print(f"{'='*70}")
    
    # 连接
    session = ddb.session()
    session.connect("localhost", 8848, "admin", "123456")
    print("✅ 连接成功")
    
    # 读取 CSV 获取统计
    print(f"\n📊 读取 CSV...")
    df = pd.read_csv(CSV_PATH)
    print(f"   记录数: {len(df):,}")
    print(f"   股票数: {df['symbol'].nunique()}")
    
    # 使用脚本导入
    script = f"""
    csvPath = "{CSV_PATH}"
    t = loadText(csvPath)
    t = select symbol, date, open, high, low, close, pre_close, change, pct_chg, volume, amount from t
    
    if(!existsDatabase("dfs://tushare")){{
        db = database("dfs://tushare", VALUE, 2016.01M..2026.12M)
    }} else {{
        db = database("dfs://tushare")
    }}
    
    if(!existsTable("dfs://tushare", "daily")){{
        schema = table(1:0, `symbol`date`open`high`low`close`pre_close`change`pct_chg`volume`amount,
                       [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
        daily = db.createPartitionedTable(schema, `daily, `date)
    }} else {{
        daily = loadTable("dfs://tushare", "daily")
        // 清空旧数据
        truncate(daily)
    }}
    
    append!(daily, t)
    select count(*) as total from daily
    """
    
    try:
        result = session.run(script)
        print(f"\n✅ 导入成功!")
        print(f"📈 表中总记录: {result}")
        return True
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        return False

def main():
    """主循环"""
    print("="*70)
    print("DolphinDB 自动增量导入")
    print("="*70)
    print(f"监控文件: {CSV_PATH}")
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("="*70)
    
    last_size = 0
    last_import_time = 0
    
    while True:
        try:
            current_size = get_file_size()
            
            if current_size > last_size:
                print(f"\n📈 文件增长: {last_size:,} → {current_size:,} bytes (+{current_size-last_size:,})")
                
                # 等待 10 秒让写入完成
                time.sleep(10)
                
                # 导入
                if import_to_dolphindb():
                    last_import_time = time.time()
                    last_size = current_size
            else:
                # 检查是否导出完成（5分钟无变化）
                if last_import_time > 0 and time.time() - last_import_time > 300:
                    print(f"\n✅ 导出似乎已完成，最后一次导入")
                    import_to_dolphindb()
                    break
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n停止监控")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
