#!/usr/bin/env python3
"""
使用替代方法导入失败的表
直接读取并分批插入
"""
import dolphindb as ddb
import pandas as pd
import os

print("="*70)
print("使用替代方法导入")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 尝试导入失败的表
FAILED_TABLES = [
    ("tushare_adj_factor.csv", "dfs://tushare_adj", "adj_factor"),
    ("tushare_income.csv", "dfs://tushare_income", "income"),
    ("tushare_balancesheet.csv", "dfs://tushare_balancesheet", "balancesheet"),
    ("tushare_moneyflow_fixed.csv", "dfs://tushare_moneyflow", "moneyflow"),
]

for filename, db_name, table_name in FAILED_TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    if not os.path.exists(path):
        print(f"  文件不存在")
        continue
    
    try:
        # 使用最简单的读取方式
        print(f"  读取CSV...")
        
        # 对于大文件，只读取必要列
        if "adj_factor" in filename:
            df = pd.read_csv(path, usecols=['ts_code', 'trade_date', 'adj_factor'], low_memory=False)
            date_col = 'trade_date'
        elif "income" in filename:
            df = pd.read_csv(path, usecols=['ts_code', 'ann_date', 'end_date', 'total_revenue', 'net_income'], low_memory=False)
            date_col = 'ann_date'
        elif "balancesheet" in filename:
            df = pd.read_csv(path, usecols=['ts_code', 'ann_date', 'end_date', 'total_assets', 'total_liabilities'], low_memory=False)
            date_col = 'ann_date'
        elif "moneyflow" in filename:
            df = pd.read_csv(path, usecols=['ts_code', 'trade_date', 'buy_sm_vol', 'sell_sm_vol'], low_memory=False, nrows=2000000)  # 限制行数
            date_col = 'trade_date'
        else:
            df = pd.read_csv(path, low_memory=False)
            date_col = 'trade_date' if 'trade_date' in df.columns else 'ann_date'
        
        total = len(df)
        print(f"  读取行数: {total:,}")
        
        # 处理日期
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # 保存到临时文件
        temp_file = base_path + f"temp_{table_name}_simple.csv"
        df.to_csv(temp_file, index=False)
        print(f"  临时文件: {os.path.getsize(temp_file)/1024/1024:.1f} MB")
        
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
        except:
            pass
        
        # 创建数据库
        try:
            session.run(f'''
            if(!existsDatabase("{db_name}")){{
                db = database("{db_name}", VALUE, 2016.01M..2026.12M)
            }}
            ''')
        except:
            pass
        
        # 导入
        print(f"  导入中...")
        script = f'''
        db = database("{db_name}")
        t = loadText("{temp_file}")
        {table_name} = db.createPartitionedTable(t, `{table_name}, `{date_col})
        append!({table_name}, t)
        '''
        
        session.run(script)
        
        # 清理
        os.remove(temp_file)
        
        # 验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        imported = result.values[0][0]
        print(f"  导入完成: {imported:,} 条")
        
    except Exception as e:
        print(f"  错误: {str(e)[:100]}")

print("\n" + "="*70)
print("导入完成!")
print("="*70)
