#!/usr/bin/env python3
"""
Tushare 股票接口完整清单
"""
import tushare as ts

TOKEN = "5bb803b4f1bdc5ed7762f89d9109a809"
URL = "http://119.45.170.23"

pro = ts.pro_api(TOKEN)
pro._DataApi__token = TOKEN
pro._DataApi__http_url = URL

interfaces = {
    "基础数据": [
        ("stock_basic", "股票基础信息"),
        ("trade_cal", "交易日历"),
        ("stock_company", "上市公司基本信息"),
        ("stk_managers", "上市公司管理层"),
        ("stk_rewards", "上市公司管理层薪酬和持股"),
    ],
    "行情数据": [
        ("daily", "日线行情 ✅"),
        ("weekly", "周线行情 ✅"),
        ("monthly", "月线行情 ✅"),
        ("adj_factor", "复权因子 ✅"),
        ("suspend", "停牌信息"),
        ("suspend_d", "每日停复牌信息"),
        ("stk_limit", "涨跌停价格"),
    ],
    "财务数据": [
        ("income", "利润表"),
        ("balancesheet", "资产负债表"),
        ("cashflow", "现金流量表"),
        ("forecast", "业绩预告"),
        ("express", "业绩快报"),
        ("fina_indicator", "财务指标数据"),
        ("fina_audit", "财务审计意见"),
        ("fina_mainbz", "主营业务构成"),
    ],
    "市场数据": [
        ("moneyflow", "个股资金流向"),
        ("limit_list", "涨跌停股票统计"),
        ("top_list", "龙虎榜每日详情"),
        ("top_inst", "龙虎榜机构详情"),
        ("stk_holdernumber", "股东人数"),
        ("stk_holdertrade", "股东增减持"),
    ],
    "股本相关": [
        ("stk_pledge", "股权质押统计"),
        ("stk_pledge_detail", "股权质押详情"),
        ("stk_reward", "股票回购"),
        ("new_share", "新股上市"),
    ],
    "其他": [
        ("block_trade", "大宗交易"),
        ("stk_account", "股票账户统计"),
        ("ggt_daily", "港股通每日成交"),
        ("ggt_monthly", "港股通每月成交"),
    ]
}

print("="*70)
print("Tushare 股票接口完整清单")
print("="*70)

for category, apis in interfaces.items():
    print(f"\n【{category}】")
    for api, desc in apis:
        print(f"  - {api:25s} {desc}")

print("\n" + "="*70)
print("总计: 30+ 个接口")
print("="*70)
print("\n✅ 已完成: daily, weekly, monthly, adj_factor")
print("🔄 进行中: moneyflow, limit_list, fina_indicator")
print("⏳ 未开始: income, balancesheet, cashflow, forecast, ...")
