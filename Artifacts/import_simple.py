#!/usr/bin/env python3
"""
Tushare 导入测试 - 简化版
使用 DolphinDB Python API 直接写入
"""
import pandas as pd
import tushare as ts
import dolphindb as ddb
from datetime import datetime

# 配置
TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

# 初始化 Tushare
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

# 初始化 DolphinDB
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 确保表存在
session.run("""
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 2020.01M..2030.12M)
} else {
    db = database("dfs://tushare")
}

if(!existsTable("dfs://tushare", "daily")){
    schema = table(1:0, `symbol`date`open`high`low`close`volume`amount, [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    db.createPartitionedTable(schema, `daily, `date)
}
""")

print("✅ DolphinDB 表已就绪")

# 获取股票列表
stocks = pro.stock_basic(exchange='', list_status='L')['ts_code'].tolist()[:10]  # 测试10只
print(f"📊 获取 {len(stocks)} 只股票")

# 导入数据
total = 0
for ts_code in stocks:
    try:
        # 获取日线数据
        df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20240324')
        
        if df is None or df.empty:
            continue
        
        # 转换格式
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        # 使用 tableInsert 逐条写入（简化版）
        for _, row in df.iterrows():
            script = f"""
            t = loadTable("dfs://tushare", "daily")
            insert into t values(
                '{row['ts_code']}', 
                date({row['trade_date'].year}.{row['trade_date'].month}.{row['trade_date'].day}),
                {row['open']}, {row['high']}, {row['low']}, {row['close']},
                {row['vol']}, {row['amount']}
            )
            """
            session.run(script)
        
        total += len(df)
        print(f"✅ {ts_code}: {len(df)} 条记录")
        
    except Exception as e:
        print(f"❌ {ts_code}: {e}")

print(f"\n🎉 导入完成！总计: {total} 条记录")
