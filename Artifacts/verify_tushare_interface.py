#!/usr/bin/env python3
"""
Tushare 股票接口对照验证
对照官方文档检查下载完整性
"""
import os

print("="*80)
print("Tushare 股票接口对照验证")
print("="*80)

# Tushare 官方股票接口列表（按文档分类）
tushare_interfaces = {
    "基础数据": [
        ("stock_basic", "股票列表", "tushare_all_stocks.csv"),
        ("trade_cal", "交易日历", None),
        ("namechange", "股票曾用名", "tushare_namechange.csv"),
        ("stk_holdernumber", "股东人数", "tushare_holdernumber.csv"),
        ("stk_holdertrade", "股东增减持", "tushare_holdertrade.csv"),
        ("new_share", "IPO新股上市", "tushare_new_share.csv"),
    ],
    "行情数据": [
        ("daily", "历史日线", "tushare_all_2016_2025.csv"),
        ("weekly", "周线行情", "tushare_weekly.csv"),
        ("monthly", "月线行情", "tushare_monthly.csv"),
        ("adj_factor", "复权因子", "tushare_adj_factor.csv"),
        ("daily_basic", "每日指标", "tushare_daily_basic.csv"),
        ("limit_list", "涨跌停数据", "tushare_limit_list.csv"),
    ],
    "财务数据": [
        ("income", "利润表", "tushare_income.csv"),
        ("balancesheet", "资产负债表", "tushare_balancesheet.csv"),
        ("cashflow", "现金流量表", "tushare_cashflow.csv"),
        ("fina_indicator", "财务指标", "tushare_fina_indicator.csv"),
        ("fina_audit", "财务审计", "tushare_fina_audit.csv"),
        ("fina_mainbz", "主营业务", "tushare_fina_mainbz.csv"),
        ("forecast", "业绩预告", "tushare_forecast.csv"),
        ("express", "业绩快报", "tushare_express.csv"),
    ],
    "市场数据": [
        ("moneyflow", "个股资金流向", "tushare_moneyflow_fixed.csv"),
        ("block_trade", "大宗交易", "tushare_block_trade.csv"),
        ("top_list", "龙虎榜", "tushare_top_list.csv"),
        ("top_inst", "龙虎榜机构", "tushare_top_inst.csv"),
    ],
}

base_path = "E:/Quant_Production/Inbox/"

# 统计
total = 0
completed = 0
missing = []

for category, interfaces in tushare_interfaces.items():
    print(f"\n【{category}】")
    for api, name, filename in interfaces:
        total += 1
        if filename and os.path.exists(base_path + filename):
            size = os.path.getsize(base_path + filename) / 1024 / 1024
            print(f"  ✓ {api} ({name}): {size:.1f} MB")
            completed += 1
        elif filename:
            print(f"  ✗ {api} ({name}): 文件缺失")
            missing.append((category, api, name))
        else:
            print(f"  - {api} ({name}): 未下载")
            missing.append((category, api, name))

print("\n" + "="*80)
print(f"总结: {completed}/{total} 接口已下载 ({completed/total*100:.1f}%)")
print("="*80)

if missing:
    print("\n缺失接口:")
    for cat, api, name in missing[:10]:
        print(f"  - {cat}/{api} ({name})")
