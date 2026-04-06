#!/usr/bin/env python3
"""
终极修复 - 逐行读取CSV并导入DolphinDB
避免pandas内存问题
"""
import dolphindb as ddb
import csv
from datetime import datetime
import os

print("="*70)
print("终极修复 - 逐行导入weekly和monthly")
print("="*70)

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

base_path = "E:/Quant_Production/Inbox/"

TABLES = [
    ("tushare_weekly.csv", "dfs://tushare_weekly", "weekly"),
    ("tushare_monthly.csv", "dfs://tushare_monthly", "monthly"),
]

for filename, db_name, table_name in TABLES:
    print(f"\n{'='*70}")
    print(f"{filename}:")
    print(f"{'='*70}")
    
    path = base_path + filename
    
    try:
        # 删除旧表
        try:
            session.run(f'dropTable(database("{db_name}"), `{table_name})')
            print(f"  删除旧表")
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
        
        # 使用csv模块逐行读取
        print(f"  逐行读取并导入...")
        
        valid_rows = []
        total = 0
        valid = 0
        batch_size = 50000
        batch_num = 0
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                total += 1
                
                # 验证日期
                try:
                    date_str = row.get('date', '')
                    if date_str:
                        # 尝试解析日期
                        datetime.strptime(date_str, '%Y-%m-%d')
                        valid_rows.append(row)
                        valid += 1
                except:
                    pass
                
                # 批量导入
                if len(valid_rows) >= batch_size:
                    batch_num += 1
                    
                    # 保存为临时CSV
                    temp_file = f"{base_path}temp_{table_name}_{batch_num}.csv"
                    with open(temp_file, 'w', newline='', encoding='utf-8') as temp_f:
                        writer = csv.DictWriter(temp_f, fieldnames=valid_rows[0].keys())
                        writer.writeheader()
                        writer.writerows(valid_rows)
                    
                    # 导入到DolphinDB
                    try:
                        if batch_num == 1:
                            script = f'''
                            db = database("{db_name}")
                            t = loadText("{temp_file}")
                            {table_name} = db.createPartitionedTable(t, `{table_name}, `date)
                            append!({table_name}, t)
                            '''
                        else:
                            script = f'''
                            t = loadText("{temp_file}")
                            {table_name} = loadTable("{db_name}", "{table_name}")
                            append!({table_name}, t)
                            '''
                        
                        session.run(script)
                        print(f"    批次 {batch_num}: {valid:,} / {total:,} 有效 ({valid/total*100:.1f}%)")
                        
                    except Exception as e:
                        print(f"    批次 {batch_num} 错误: {str(e)[:50]}")
                    
                    # 清理
                    os.remove(temp_file)
                    valid_rows = []
        
        # 导入最后一批
        if valid_rows:
            batch_num += 1
            temp_file = f"{base_path}temp_{table_name}_{batch_num}.csv"
            with open(temp_file, 'w', newline='', encoding='utf-8') as temp_f:
                writer = csv.DictWriter(temp_f, fieldnames=valid_rows[0].keys())
                writer.writeheader()
                writer.writerows(valid_rows)
            
            try:
                script = f'''
                t = loadText("{temp_file}")
                {table_name} = loadTable("{db_name}", "{table_name}")
                append!({table_name}, t)
                '''
                session.run(script)
            except:
                pass
            
            os.remove(temp_file)
        
        # 最终验证
        result = session.run(f'select count(*) from loadTable("{db_name}", "{table_name}")')
        final = result.values[0][0]
        print(f"\n  完成: {final:,} / {total:,} ({final/total*100:.1f}%)")
        
    except Exception as e:
        print(f"  错误: {str(e)[:100]}")

print(f"\n{'='*70}")
print("修复完成!")
print(f"{'='*70}")
