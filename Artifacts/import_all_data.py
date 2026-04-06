#!/usr/bin/env python3
"""
导入所有已完成数据到 DolphinDB
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("导入所有数据到 DolphinDB")
print("="*70)

# 连接 DolphinDB
print("\n1️⃣  连接 DolphinDB...")
session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")
print("   ✅ 连接成功")

# 定义要导入的文件
files_to_import = [
    ('tushare_weekly.csv', 'weekly', {'symbol': 'SYMBOL', 'date': 'DATE'}),
    ('tushare_monthly.csv', 'monthly', {'symbol': 'SYMBOL', 'date': 'DATE'}),
    ('tushare_adj_factor.csv', 'adj_factor', {'symbol': 'SYMBOL', 'date': 'DATE'}),
    ('tushare_moneyflow.csv', 'moneyflow', {'ts_code': 'SYMBOL', 'trade_date': 'DATE'}),
    ('tushare_limit_list.csv', 'limit_list', {'ts_code': 'SYMBOL', 'trade_date': 'DATE'}),
    ('tushare_fina_indicator.csv', 'fina_indicator', {'ts_code': 'SYMBOL', 'end_date': 'DATE'}),
]

for csv_name, table_name, rename_map in files_to_import:
    csv_path = f"E:/Quant_Production/Inbox/{csv_name}"
    
    if not os.path.exists(csv_path):
        print(f"\n⚠️  {csv_name} 不存在，跳过")
        continue
    
    print(f"\n2️⃣  导入 {csv_name} -> {table_name}...")
    
    # 读取数据
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"   CSV 记录: {len(df):,} 条")
    
    if len(df) == 0:
        print(f"   ⚠️  无数据，跳过")
        continue
    
    # 重命名列
    df = df.rename(columns=rename_map)
    
    # 转换日期
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    elif 'trade_date' in df.columns:
        df['date'] = pd.to_datetime(df['trade_date'], format='%Y-%m-%d')
    elif 'end_date' in df.columns:
        df['date'] = pd.to_datetime(df['end_date'], format='%Y-%m-%d')
    
    # 保存临时 CSV
    temp_csv = f"E:/Quant_Production/Inbox/temp_{table_name}.csv"
    df.to_csv(temp_csv, index=False)
    
    # 创建数据库和表
    db_path = f"dfs://tushare_{table_name}"
    script = f"""
    // 创建数据库
    if(!existsDatabase("{db_path}")){{
        db = database("{db_path}", VALUE, 2016.01M..2026.12M)
    }} else {{
        db = database("{db_path}")
    }}
    
    // 删除旧表
    if(existsTable("{db_path}", "{table_name}")){{
        dropTable(db, `{table_name})
    }}
    """
    session.run(script)
    
    # 加载数据
    load_script = f"""
    t = loadText("{temp_csv}")
    """
    
    try:
        session.run(load_script)
        print(f"   ✅ {table_name} 导入完成")
        
        # 验证
        count = session.run(f"select count(*) from loadTable('{db_path}', '{table_name}')")
        print(f"   📊 表中记录: {count.values[0][0]:,} 条")
    except Exception as e:
        print(f"   ❌ 失败: {str(e)[:100]}")

print("\n" + "="*70)
print("✅ 所有数据导入完成！")
print("="*70)
