import dolphindb as ddb

session = ddb.session()
session.connect("localhost", 8848, "admin", "123456")

print("=== DolphinDB 完整数据验证 ===\n")

tables = [
    ("dfs://tushare", "daily"),
    ("dfs://tushare_weekly", "weekly"),
    ("dfs://tushare_monthly", "monthly"),
    ("dfs://tushare_adj", "adj_factor"),
    ("dfs://tushare_daily_basic", "daily_basic"),
    ("dfs://tushare_income", "income"),
    ("dfs://tushare_balancesheet", "balancesheet"),
    ("dfs://tushare_cashflow", "cashflow"),
    ("dfs://tushare_forecast", "forecast"),
    ("dfs://tushare_express", "express"),
    ("dfs://tushare_fina_indicator", "fina_indicator"),
    ("dfs://tushare_fina_audit", "fina_audit"),
    ("dfs://tushare_fina_mainbz", "fina_mainbz"),
    ("dfs://tushare_moneyflow", "moneyflow"),
    ("dfs://tushare_block_trade", "block_trade"),
    ("dfs://tushare_limit_list", "limit_list"),
    ("dfs://tushare_top_list", "top_list"),
    ("dfs://tushare_top_inst", "top_inst"),
    ("dfs://tushare_new_share", "new_share"),
    ("dfs://tushare_holdernumber", "holdernumber"),
    ("dfs://tushare_holdertrade", "holdertrade"),
    ("dfs://tushare_namechange", "namechange"),
    ("dfs://tushare_trade_cal", "trade_cal"),
    ("dfs://tushare_repurchase", "repurchase"),
]

total = 0
success = 0

for db, table in tables:
    try:
        result = session.run(f'select count(*) from loadTable("{db}", "{table}")')
        count = result.values[0][0]
        print(f"{db}/{table}: {count:,} 条")
        total += count
        success += 1
    except Exception as e:
        print(f"{db}/{table}: 错误 - {str(e)[:30]}")

print(f"\n总计: {success}/{len(tables)} 个表, {total:,} 条记录")
print("=== 完成 ===")
