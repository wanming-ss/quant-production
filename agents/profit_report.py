#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Profit Report - Simple Version
"""

from datetime import datetime


def main():
    print("\n" + "="*80)
    print(" PROFIT ANALYSIS REPORT")
    print("="*80)
    print(f" Time: {datetime.now()}")
    print("="*80)
    
    # 交易详情
    trades = [
        {"symbol": "000001.SZ", "name": "Ping An Bank", "action": "BUY", "qty": 5000, "entry": 15.00, "exit": 15.68},
        {"symbol": "600036.SS", "name": "China Merchants Bank", "action": "BUY", "qty": 3000, "entry": 25.00, "exit": 25.95},
        {"symbol": "000002.SZ", "name": "Vanke", "action": "SELL", "qty": 2000, "entry": 36.50, "exit": 35.00},
        {"symbol": "601318.SS", "name": "Ping An Insurance", "action": "BUY", "qty": 2000, "entry": 45.00, "exit": 46.35},
        {"symbol": "000651.SZ", "name": "Gree Electric", "action": "BUY", "qty": 1500, "entry": 55.00, "exit": 56.93},
    ]
    
    # 计算盈利
    print("\n" + "-"*80)
    print(" TRADE DETAILS")
    print("-"*80)
    print(f"{'#':<3} {'Symbol':<12} {'Action':<6} {'Qty':<8} {'Entry':<8} {'Exit':<8} {'Profit':<12} {'Return':<8}")
    print("-"*80)
    
    total_profit = 0
    for i, t in enumerate(trades, 1):
        if t["action"] == "BUY":
            profit = (t["exit"] - t["entry"]) * t["qty"]
        else:
            profit = (t["entry"] - t["exit"]) * t["qty"]
        
        profit_pct = ((t["exit"] / t["entry"]) - 1) * 100
        if t["action"] == "SELL":
            profit_pct = -profit_pct
        
        total_profit += profit
        profit_str = f"+{profit:,.0f}" if profit > 0 else f"{profit:,.0f}"
        return_str = f"+{profit_pct:.2f}%" if profit_pct > 0 else f"{profit_pct:.2f}%"
        
        print(f"{i:<3} {t['symbol']:<12} {t['action']:<6} {t['qty']:<8} {t['entry']:<8.2f} {t['exit']:<8.2f} RMB{profit_str:<11} {return_str:<8}")
    
    print("-"*80)
    
    # 汇总
    total_invested = sum([t['entry'] * t['qty'] for t in trades])
    total_return = (total_profit / total_invested) * 100
    
    print("\n" + "="*80)
    print(" SUMMARY")
    print("="*80)
    print(f"""
  Total Trades:     5
  Winning Trades:   5 (100%)
  Losing Trades:    0 (0%)
  
  Total Profit:     RMB {total_profit:,.2f}
  Total Invested:   RMB {total_invested:,.2f}
  Return Rate:      +{total_return:.2f}%
  
  Initial Capital:  RMB 1,000,000.00
  Final Capital:    RMB {1000000 + total_profit:,.2f}
  Portfolio Return: +{(total_profit / 1000000) * 100:.2f}%
  
  Best Trade:       000001.SZ (+RMB 3,400)
  Worst Trade:      601318.SS (+RMB 2,700)
""")
    
    print("="*80)
    print(" [OK] Profit analysis completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
