#!/usr/bin/env python3
"""
Tushare 股票接口清单
列出所有股票相关接口
"""
import tushare as ts

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

# 初始化
pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

print("="*70)
print("Tushare 股票相关接口清单")
print("="*70)

# 主要股票数据接口
interfaces = [
    # 基础数据
    ("stock_basic", "股票基础信息", " ts_code, name, industry"),
    ("trade_cal", "交易日历", " exchange, cal_date, is_open"),
    ("stock_company", "公司信息", " ts_code, chairman, manager"),
    
    # 行情数据
    ("daily", "日线数据", "日线行情（已下载）"),
    ("weekly", "周线数据", "周线行情"),
    ("monthly", "月线数据", "月线行情"),
    ("adj_factor", "复权因子", "复权因子数据"),
    ("suspend", "停牌信息", "停牌复牌信息"),
    ("suspend_d", "每日停牌", "每日停复牌信息"),
    
    # 财务数据
    ("income", "利润表", "上市公司财务利润表"),
    ("balancesheet", "资产负债表", "上市公司资产负债表"),
    ("cashflow", "现金流量表", "上市公司现金流量表"),
    ("forecast", "业绩预告", "业绩预告"),
    ("express", "业绩快报", "业绩快报"),
    ("fina_indicator", "财务指标", "财务指标数据"),
    ("fina_audit", "财务审计", "财务审计意见"),
    ("fina_mainbz", "主营业务构成", "主营业务构成"),
    
    # 市场数据
    ("moneyflow", "个股资金流向", "个股资金流向"),
    ("limit_list", "涨跌停股票", "每日涨跌停股票统计"),
    ("top_list", "龙虎榜每日详情", "龙虎榜每日交易详情"),
    ("top_inst", "龙虎榜机构详情", "龙虎榜机构交易详情"),
    ("stk_holdernumber", "股东人数", "股东人数及持股集中度"),
    ("stk_holdertrade", "股东增减持", "股东增减持数据"),
    ("ggt_daily", "港股通每日成交", "港股通每日成交数据"),
    ("ggt_monthly", "港股通每月成交", "港股通每月成交统计"),
    
    # 股本相关
    ("stk_reward", "股票回购", "股票回购数据"),
    ("new_share", "新股上市", "新股上市列表"),
    ("stk_pledge", "股权质押", "股权质押统计"),
    ("stk_pledge_detail", "股权质押详情", "股权质押详情"),
    ("stk_jump", "跳跃表", "跳跃表数据"),
    
    # 其他
    ("block_trade", "大宗交易", "大宗交易数据"),
    ("stk_account", "股票账户统计", "股票账户统计信息"),
    ("stk_account_old", "老股票账户统计", "老股票账户统计"),
    ("broker_recommend", "券商推荐", "券商推荐数据"),
]

print("\n股票数据接口:")
print("-" * 70)
for i, (code, name, desc) in enumerate(interfaces, 1):
    print(f"{i:2d}. {code:20s} - {name:15s} ({desc})")

print("\n" + "="*70)
print(f"总计: {len(interfaces)} 个接口")
print("="*70)
print("\n当前已下载: daily (日线数据)")
print("建议优先下载:")
print("  1. weekly/monthly (周/月线)")
print("  2. adj_factor (复权因子)")
print("  3. moneyflow (资金流向)")
print("  4. fina_indicator (财务指标)")
print("  5. limit_list (涨跌停)")
