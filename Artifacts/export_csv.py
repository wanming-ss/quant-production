#!/usr/bin/env python3
"""
Tushare 数据导出 CSV + DolphinDB 导入
使用 DolphinDB 的 loadText 和 append!
"""
import pandas as pd
import tushare as ts
import os

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"
CSV_PATH = "E:/Quant_Production/Inbox/tushare_daily.csv"

# 初始化 Tushare
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("📊 获取股票列表...")
stocks = pro.stock_basic(exchange='', list_status='L')['ts_code'].tolist()[:50]  # 测试50只

print(f"📝 开始导出 {len(stocks)} 只股票数据到 CSV...")

all_data = []
for i, ts_code in enumerate(stocks, 1):
    try:
        df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20240324')
        if df is not None and not df.empty:
            # 转换列名
            df = df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'vol': 'volume'
            })
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            all_data.append(df)
            print(f"  [{i}/{len(stocks)}] {ts_code}: {len(df)} 条")
    except Exception as e:
        print(f"  [{i}/{len(stocks)}] {ts_code}: 失败 - {e}")

# 合并并保存 CSV
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
    print(f"\n✅ CSV 导出完成: {CSV_PATH}")
    print(f"📈 总计: {len(combined)} 条记录")
    print(f"📊 股票数: {combined['symbol'].nunique()}")
    print(f"\n字段: {list(combined.columns)}")
else:
    print("❌ 无数据导出")

# 生成 DolphinDB 导入脚本
print("\n" + "="*60)
print("DolphinDB 导入脚本 (请复制到 DolphinDB GUI 执行):")
print("="*60)
print(f"""
// 1. 加载 CSV
csvPath = "{CSV_PATH}"
t = loadText(csvPath)

// 2. 查看数据结构
select top 10 * from t

// 3. 转换日期格式（如果需要）
t = select symbol, temporalParse(date, "yyyy-MM-dd") as date, 
          open, high, low, close, volume, amount 
    from t

// 4. 确保目标表存在
if(!existsDatabase("dfs://tushare")){{
    db = database("dfs://tushare", VALUE, 2020.01M..2030.12M)
}} else {{
    db = database("dfs://tushare")
}}

if(!existsTable("dfs://tushare", "daily")){{
    schema = table(1:0, `symbol`date`open`high`low`close`volume`amount,
                   [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    daily = db.createPartitionedTable(schema, `daily, `date)
}} else {{
    daily = loadTable("dfs://tushare", "daily")
}}

// 5. 追加数据
append!(daily, t)

// 6. 验证
select count(*) from daily
select top 10 * from daily
""")
print("="*60)
