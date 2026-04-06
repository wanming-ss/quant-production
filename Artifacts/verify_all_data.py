import pandas as pd
import os

print("=== 全数据完整性验证 ===\n")

files = {
    '日线': ('tushare_all_2016_2025.csv', 'symbol'),
    '周线': ('tushare_weekly.csv', 'ts_code'),
    '月线': ('tushare_monthly.csv', 'ts_code'),
    '复权因子': ('tushare_adj_factor.csv', 'ts_code'),
    '每日股本': ('tushare_daily_basic.csv', 'ts_code'),
    '财务指标': ('tushare_fina_indicator.csv', 'ts_code'),
    '利润表': ('tushare_income.csv', 'ts_code'),
    '资产负债表': ('tushare_balancesheet.csv', 'ts_code'),
    '现金流量表': ('tushare_cashflow.csv', 'ts_code'),
    '业绩预告': ('tushare_forecast.csv', 'ts_code'),
    '业绩快报': ('tushare_express.csv', 'ts_code'),
    '资金流向': ('tushare_moneyflow_fixed.csv', 'ts_code'),
    '新股上市': ('tushare_new_share.csv', 'ts_code'),
    '大宗交易': ('tushare_block_trade.csv', 'ts_code'),
    '涨跌停': ('tushare_limit_list.csv', 'ts_code'),
    '龙虎榜': ('tushare_top_list.csv', 'ts_code'),
    '龙虎榜机构': ('tushare_top_inst.csv', 'ts_code'),
    '股东人数': ('tushare_holdernumber.csv', 'ts_code'),
    '股东增减持': ('tushare_holdertrade.csv', 'ts_code'),
    '财务审计': ('tushare_fina_audit.csv', 'ts_code'),
    '主营业务': ('tushare_fina_mainbz.csv', 'ts_code'),
    '股票曾用名': ('tushare_namechange.csv', 'ts_code'),
}

base_path = 'E:/Quant_Production/Inbox/'

for name, (filename, code_col) in files.items():
    path = base_path + filename
    print(f'{name}:')
    
    if not os.path.exists(path):
        print('  文件不存在')
        continue
    
    try:
        # 读取统计
        df = pd.read_csv(path, low_memory=False, on_bad_lines='skip')
        size_mb = os.path.getsize(path) / 1024 / 1024
        
        print(f'  大小: {size_mb:.2f} MB')
        print(f'  行数: {len(df):,}')
        print(f'  列数: {len(df.columns)}')
        
        # 股票数量
        if code_col in df.columns:
            stock_count = df[code_col].nunique()
            print(f'  股票数: {stock_count:,}')
        
        # 日期列检查
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        if date_cols:
            print(f'  日期列: {date_cols}')
        
    except Exception as e:
        print(f'  错误: {str(e)[:50]}')
    
    print()

print('=== 验证完成 ===')
