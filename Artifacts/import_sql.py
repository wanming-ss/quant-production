#!/usr/bin/env python3
"""
Tushare 导入 - SQL 方式
直接执行 DolphinDB 脚本
"""
import pandas as pd
import tushare as ts
import dolphindb as ddb

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

# 建表
session.run("""
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 2020.01M..2030.12M)
} else {
    db = database("dfs://tushare")
}
if(!existsTable("dfs://tushare", "daily")){
    schema = table(1:0, `symbol`date`open`high`low`close`volume`amount,
                   [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    db.createPartitionedTable(schema, `daily, `date)
}
""")

print("✅ 表就绪")

# 导入数据
ts_code = "000001.SZ"
df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20240131')

if df is not None and not df.empty:
    print(f"📊 {ts_code}: {len(df)} 条")
    
    # 构建批量插入脚本
    rows = []
    for _, row in df.iterrows():
        date_str = row['trade_date']  # 20240102
        year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
        ddb_date = f"{year}.{month}.{day}"
        
        rows.append(f"('{row['ts_code']}', date({ddb_date}), {row['open']}, {row['high']}, {row['low']}, {row['close']}, {row['vol']}, {row['amount']})")
    
    # 分批插入（每批10条）
    batch_size = 10
    total_inserted = 0
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        values_str = ", ".join(batch)
        
        script = f"""
        t = loadTable("dfs://tushare", "daily")
        insert into t values {values_str}
        """
        
        try:
            session.run(script)
            total_inserted += len(batch)
            print(f"✅ 批量插入 {i//batch_size + 1}: {len(batch)} 条")
        except Exception as e:
            print(f"❌ 插入失败: {e}")
            break
    
    print(f"\n🎉 总计写入: {total_inserted} 条")

# 查询验证
count = session.run('select count(*) from loadTable("dfs://tushare", "daily")')
print(f"📈 表中总记录: {count}")
