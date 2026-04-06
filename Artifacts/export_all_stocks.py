#!/usr/bin/env python3
"""
Tushare 全量股票数据导出
导出所有 5491 只股票数据到 CSV
"""
import pandas as pd
import tushare as ts
import os
from datetime import datetime

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_all_stocks.csv"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 全量股票数据导出")
print("="*70)
print(f"开始时间: {datetime.now()}")

# 获取所有股票
print("\n📊 获取股票列表...")
stocks = pro.stock_basic(exchange='', list_status='L')['ts_code'].tolist()
print(f"📝 总计 {len(stocks)} 只股票")

# 分批导出（每批100只，避免内存溢出）
BATCH_SIZE = 100
all_data = []
total_records = 0

for batch_start in range(0, len(stocks), BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, len(stocks))
    batch_stocks = stocks[batch_start:batch_end]
    
    print(f"\n📦 处理批次 {batch_start//BATCH_SIZE + 1}/{(len(stocks)-1)//BATCH_SIZE + 1} ({batch_start+1}-{batch_end})")
    
    for i, ts_code in enumerate(batch_stocks, batch_start+1):
        try:
            # 获取日线数据（2024年至今）
            df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20250324')
            
            if df is not None and not df.empty:
                # 转换列名
                df = df.rename(columns={
                    'ts_code': 'symbol',
                    'trade_date': 'date',
                    'vol': 'volume'
                })
                # 日期格式
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                all_data.append(df)
                total_records += len(df)
                
                # 每10只显示进度
                if i % 10 == 0:
                    print(f"  [{i}/{len(stocks)}] {ts_code}: +{len(df)} 条 (累计 {total_records})")
            
        except Exception as e:
            print(f"  [{i}/{len(stocks)}] {ts_code}: 跳过 - {str(e)[:50]}")
        
        # 请求间隔
        import time
        time.sleep(0.05)
    
    # 每批次保存一次（防止内存溢出）
    if all_data:
        batch_combined = pd.concat(all_data, ignore_index=True)
        
        # 追加到 CSV
        if batch_start == 0:
            batch_combined.to_csv(CSV_PATH, index=False, mode='w')
        else:
            batch_combined.to_csv(CSV_PATH, index=False, mode='a', header=False)
        
        print(f"  💾 已保存 {len(batch_combined)} 条到 CSV (累计 {total_records})")
        all_data = []  # 清空内存

print(f"\n" + "="*70)
print("导出完成")
print(f"CSV 文件: {CSV_PATH}")
print(f"总计记录: {total_records:,}")
print(f"股票数量: {len(stocks)}")
print(f"结束时间: {datetime.now()}")
print("="*70)

# 生成 DolphinDB 导入脚本
print("\n" + "="*70)
print("DolphinDB 批量导入脚本")
print("="*70)
print(f"""
// 1. 加载 CSV
csvPath = "{CSV_PATH}"
t = loadText(csvPath)

// 2. 查看统计
select count(*) from t
select symbol, count(*) as cnt from t group by symbol order by cnt desc limit 10

// 3. 转换日期
t = select symbol, temporalParse(date, "yyyy-MM-dd") as date,
          open, high, low, close, pre_close, change, pct_chg, volume, amount
    from t

// 4. 创建数据库和表
if(!existsDatabase("dfs://tushare")){{
    db = database("dfs://tushare", VALUE, 2020.01M..2030.12M)
}} else {{
    db = database("dfs://tushare")
}}

if(!existsTable("dfs://tushare", "daily")){{
    schema = table(1:0, `symbol`date`open`high`low`close`pre_close`change`pct_chg`volume`amount,
                   [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    daily = db.createPartitionedTable(schema, `daily, `date)
}} else {{
    daily = loadTable("dfs://tushare", "daily")
}}

// 5. 批量导入
append!(daily, t)

// 6. 验证
select count(*) from daily
select top 10 * from daily
""")
print("="*70)
