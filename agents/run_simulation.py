#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quant Trading Simulation - Live Run
使用 Agent 系统执行模拟量化交易（最多 5 支股票）
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "E:/Quant_Production")
from agents.executor import KernelAgent, LibrarianAgent, AuditorAgent, StrategistAgent, TraderAgent, MonitorAgent


class QuantSimulationKernel(KernelAgent):
    """量化交易模拟核心"""
    
    def __init__(self, max_stocks: int = 5):
        super().__init__()
        self.max_stocks = max_stocks
    
    def run(self):
        """执行完整的量化交易流程"""
        print("\n" + "="*70)
        print(" QUANT TRADING SIMULATION - LIVE RUN")
        print("="*70)
        print(f" Time: {datetime.now()}")
        print(f" Max Stocks: {self.max_stocks}")
        print("="*70)
        
        # Stage 1: 数据检查
        print("\n" + "="*70)
        print(" STAGE 1: DATA QUALITY CHECK")
        print("="*70)
        data_result = self.agents["Librarian"].execute("check_data")
        
        if not data_result["files"]:
            print("[ERROR] No data files found!")
            return None
        
        # Stage 2: 风控测试
        print("\n" + "="*70)
        print(" STAGE 2: RISK CONTROL TEST")
        print("="*70)
        risk_result = self.agents["Auditor"].execute("test_risk")
        print(f" Tests: {len(risk_result['tests'])}, Violations: {risk_result['violations']}")
        
        # Stage 3: 生成交易信号（最多 5 支股票）
        print("\n" + "="*70)
        print(" STAGE 3: TRADING SIGNALS (Max 5 Stocks)")
        print("="*70)
        signals_result = self.agents["Strategist"].execute("generate_signals_limited", {"max_stocks": self.max_stocks})
        signals = signals_result["signals"][:self.max_stocks]
        print(f" Generated {len(signals)} signals")
        
        # Stage 4: 风控合规检查
        print("\n" + "="*70)
        print(" STAGE 4: RISK COMPLIANCE CHECK")
        print("="*70)
        approved = []
        for signal in signals:
            result = self.agents["Auditor"].execute("check_order", {
                "order": {
                    "symbol": signal["symbol"],
                    "target_position": signal["target"],
                    "is_st": "ST" in signal["symbol"]
                }
            })
            if result["approved"]:
                approved.append(signal)
        
        print(f" Approved: {len(approved)}/{len(signals)}")
        
        # Stage 5: 执行交易
        print("\n" + "="*70)
        print(" STAGE 5: TRADE EXECUTION")
        print("="*70)
        trades_result = self.agents["Trader"].execute("execute_trades", {"signals": approved})
        
        # Stage 6: 生成报告
        print("\n" + "="*70)
        print(" STAGE 6: TRADING REPORT")
        print("="*70)
        report_result = self.agents["Monitor"].execute("generate_report", {
            "trade_count": len(approved),
            "stocks": [s["symbol"] for s in approved]
        })
        
        # Final Summary
        print("\n" + "="*70)
        print(" SIMULATION COMPLETED")
        print("="*70)
        print(f" Stocks analyzed: {len(signals)}")
        print(f" Trades executed: {trades_result['executed']}")
        print(f" Stocks: {', '.join([t['symbol'] for t in trades_result['trades']])}")
        print(f" P&L: RMB {report_result['report']['pnl']:,}")
        print(f" Sharpe: {report_result['report']['sharpe']}")
        print("="*70 + "\n")
        
        return {
            "signals": signals,
            "approved": approved,
            "trades": trades_result["trades"],
            "report": report_result["report"]
        }


def main():
    """主函数"""
    kernel = QuantSimulationKernel(max_stocks=5)
    results = kernel.run()
    
    if results:
        print("[OK] Simulation successful!")
        return 0
    else:
        print("[ERROR] Simulation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
