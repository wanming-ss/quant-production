import pandas as pd
import dolphindb as ddb
import time

print("="*70)
print("完整导入最后2个表 - 逐行导入")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

# 最后2个表
TABLES = [
    ("tushare_income.csv", "income", "ann_date"),
    ("tushare_balancesheet.csv", "balancesheet", "ann_date"),
]

for filename, table_name, date_col in TABLES:
    print(f"\n{filename}:")
    path = base_path + filename
    
    try:
        # 读取并检查
        print(f"  读取CSV...")
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        total = len(df)
        print(f"  总行数: {total:,}")
        
        # 处理日期
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # 分批保存到多个小文件
        batch_size = 50000
        batches = (len(df) // batch_size) + 1
        print(f"  分成{batches}个小文件...")
        
        for i in range(batches):
            start = i * batch_size
            end = min((i + 1) * batch_size, len(df))
            batch = df.iloc[start:end]
            
            if len(batch) == 0:
                continue
            
            # 保存到小文件
            small_file = f"{base_path}small_{table_name}_{i:04d}.csv"
            batch.to_csv(small_file, index=False)
            
            if (i + 1) % 10 == 0:
                print(f"    已保存 {i+1}/{batches}")
        
        print(f"  小文件已保存，请手动导入到DolphinDB")
        print(f"  文件位置: {base_path}small_{table_name}_*.csv")
        
    except Exception as e:
        print(f"  错误: {str(e)[:80]}")

print("\n" + "="*70)
print("CSV分割完成，请手动导入小文件")
print("="*70)
