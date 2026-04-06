#!/usr/bin/env python3
"""
Tushare 数据导入测试 - 限制100只
"""
import sys
sys.path.insert(0, 'E:/Quant_Production/Artifacts')

exec(open('20260324_Tushare日线数据同步_v2.py').read())

# 修改 main() 限制100只
if __name__ == "__main__":
    TUSHARE_TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
    TUSHARE_URL = "http://119.45.170.23"
    
    syncer = TushareToDolphinDB(
        tushare_token=TUSHARE_TOKEN,
        tushare_url=TUSHARE_URL,
        dolphindb_host="localhost",
        dolphindb_port=8848,
        batch_size=5000
    )
    
    # 限制100只测试
    result = syncer.sync(
        start_date="20240101",
        end_date="20250324",
        max_stocks=100
    )
    
    print("\n" + "="*50)
    print("测试导入完成 (100只股票)")
    print("="*50)
    print(f"股票数: {result['total_stocks']}")
    print(f"总记录: {result['total_records']:,}")
    print(f"成功写入: {result['success_records']:,}")
    print(f"耗时: {result['elapsed_seconds']:.2f}s")
    print(f"速度: {result['records_per_second']:.0f} 条/秒")
    print("="*50)
