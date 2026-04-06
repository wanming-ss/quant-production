#!/usr/bin/env python3
"""
DolphinDB 导入 - 使用 tableInsert
逐条插入（较慢但稳定）
"""
import dolphindb as ddb
import pandas as pd

CSV_PATH = "E:/Quant_Production/Inbox/tushare_full_history.csv"

print("="*70)
print("DolphinDB 导入 (tableInsert)")
print("="*70)

# 连接
print("\n🔌 连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("✅ 连接成功")

# 读取 CSV
print(f"\n📊 读取 CSV...")
df = pd.read_csv(CSV_PATH)
print(f"✅ {len(df):,} 条记录，{df['symbol'].nunique()} 只股票")

# 建表
print("\n🗄️  创建表...")
session.run("""
if(!existsDatabase("dfs://tushare")){
    db = database("dfs://tushare", VALUE, 1990.01M..2030.12M)
} else {
    db = database("dfs://tushare")
}

if(!existsTable("dfs://tushare", "daily")){
    schema = table(1:0, `symbol`date`open`high`low`close`pre_close`change`pct_chg`volume`amount,
                   [SYMBOL, DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE])
    daily = db.createPartitionedTable(schema, `daily, `date)
} else {
    daily = loadTable("dfs://tushare", "daily")
}
""")
print("✅ 表就绪")

# 逐条插入
print(f"\n🚀 开始导入...")
df['date'] = pd.to_datetime(df['date'])

total = len(df)
success = 0
failed = 0

for i, (_, row) in enumerate(df.iterrows(), 1):
    try:
        date_str = row['date'].strftime('%Y.%m.%d')
        
        # 构建插入脚本 - 使用 tableInsert
        script = f"""
        t = loadTable("dfs://tushare", "daily")
        tableInsert(t, "{row['symbol']}", date({date_str}), 
                    {row['open']}, {row['high']}, {row['low']}, {row['close']},
                    {row['pre_close']}, {row['change']}, {row['pct_chg']},
                    {row['volume']}, {row['amount']})
        """
        
        session.run(script)
        success += 1
        
        if i % 1000 == 0:
            print(f"  ✅ {i}/{total} ({i/total*100:.1f}%)")
        
    except Exception as e:
        failed += 1
        if failed <= 5:  # 只显示前5个错误
            print(f"  ❌ {i}: {str(e)[:80]}")

print(f"\n" + "="*70)
print("导入完成")
print(f"成功: {success:,}")
print(f"失败: {failed}")

# 验证
count = session.run('exec count(*) from loadTable("dfs://tushare", "daily")')
print(f"表中记录: {count}")
print("="*70)
