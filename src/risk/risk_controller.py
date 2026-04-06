#!/usr/bin/env python3
"""
风控系统 - Risk Control System
跑得久：防止爆仓，硬限制保护
"""
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class RiskLimits:
    """风控限制配置"""
    # 仓位限制
    max_single_stock_position: float = 0.10  # 单票最大10%
    max_industry_position: float = 0.30      # 行业最大30%
    max_total_position: float = 0.95         # 总仓位最大95%
    min_cash_ratio: float = 0.05             # 最小现金5%
    
    # 回撤控制
    max_daily_drawdown: float = 0.03         # 单日最大回撤3%
    max_total_drawdown: float = 0.15         # 总回撤最大15%
    
    # 交易限制
    max_daily_turnover: float = 0.50         # 日换手率最大50%
    max_orders_per_minute: int = 10          # 每分钟最大订单数
    max_orders_per_day: int = 100            # 每日最大订单数
    
    # 异常检测
    price_limit_threshold: float = 0.095     # 涨跌停阈值
    volume_spike_threshold: float = 5.0      # 成交量异动阈值
    
    # 合规检查
    forbid_st stocks: bool = True            # 禁止ST股
    forbid_new_stocks_days: int = 60         # 新股禁买天数
    forbid_suspended: bool = True            # 禁止停牌股

class RiskController:
    """风控控制器"""
    
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self.violations = []
        self.daily_stats = {
            "orders_today": 0,
            "orders_this_minute": 0,
            "turnover_today": 0.0,
            "max_drawdown_today": 0.0
        }
    
    def log(self, level: str, message: str):
        """记录风控日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [RISK-{level}] {message}"
        print(log_msg)
        
        if level in ["BLOCK", "ALERT"]:
            self.violations.append({
                "time": timestamp,
                "level": level,
                "message": message
            })
    
    def check_position_limit(self, symbol: str, current_position: float, 
                            new_position: float, industry: str = None) -> bool:
        """检查仓位限制"""
        # 单票限制
        if new_position > self.limits.max_single_stock_position:
            self.log("BLOCK", f"Position limit exceeded for {symbol}: "
                     f"{new_position:.2%} > {self.limits.max_single_stock_position:.2%}")
            return False
        
        # 行业限制
        if industry and new_position > self.limits.max_industry_position:
            self.log("BLOCK", f"Industry limit exceeded for {industry}: "
                     f"{new_position:.2%} > {self.limits.max_industry_position:.2%}")
            return False
        
        return True
    
    def check_drawdown(self, current_drawdown: float) -> bool:
        """检查回撤限制"""
        if current_drawdown > self.limits.max_total_drawdown:
            self.log("BLOCK", f"Max drawdown exceeded: {current_drawdown:.2%} > "
                     f"{self.limits.max_total_drawdown:.2%}")
            return False
        
        if current_drawdown > self.daily_stats["max_drawdown_today"]:
            self.daily_stats["max_drawdown_today"] = current_drawdown
            
        if self.daily_stats["max_drawdown_today"] > self.limits.max_daily_drawdown:
            self.log("BLOCK", f"Daily drawdown exceeded: {self.daily_stats['max_drawdown_today']:.2%}")
            return False
        
        return True
    
    def check_order_rate(self) -> bool:
        """检查订单频率"""
        if self.daily_stats["orders_this_minute"] > self.limits.max_orders_per_minute:
            self.log("BLOCK", f"Order rate limit: {self.daily_stats['orders_this_minute']} orders/min")
            return False
        
        if self.daily_stats["orders_today"] > self.limits.max_orders_per_day:
            self.log("BLOCK", f"Daily order limit: {self.daily_stats['orders_today']} orders")
            return False
        
        return True
    
    def check_compliance(self, symbol: str, is_st: bool = False, 
                        is_suspended: bool = False, days_since_listing: int = 999) -> bool:
        """合规检查"""
        if self.limits.forbid_st_stocks and is_st:
            self.log("BLOCK", f"ST stock forbidden: {symbol}")
            return False
        
        if self.limits.forbid_suspended and is_suspended:
            self.log("BLOCK", f"Suspended stock forbidden: {symbol}")
            return False
        
        if days_since_listing < self.limits.forbid_new_stocks_days:
            self.log("BLOCK", f"New stock forbidden (<{self.limits.forbid_new_stocks_days} days): {symbol}")
            return False
        
        return True
    
    def pre_trade_check(self, order: Dict) -> bool:
        """交易前检查"""
        self.log("INFO", f"Pre-trade check for {order.get('symbol', 'UNKNOWN')}")
        
        checks = [
            ("Position Limit", lambda: self.check_position_limit(
                order.get('symbol'), 
                order.get('current_position', 0),
                order.get('target_position', 0),
                order.get('industry')
            )),
            ("Order Rate", self.check_order_rate),
            ("Compliance", lambda: self.check_compliance(
                order.get('symbol'),
                order.get('is_st', False),
                order.get('is_suspended', False),
                order.get('days_since_listing', 999)
            ))
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                self.log("BLOCK", f"{check_name} check FAILED - Order REJECTED")
                return False
        
        # 更新统计
        self.daily_stats["orders_today"] += 1
        self.daily_stats["orders_this_minute"] += 1
        self.daily_stats["turnover_today"] += order.get('amount', 0)
        
        self.log("PASS", "All checks passed - Order APPROVED")
        return True
    
    def reset_daily_stats(self):
        """重置日统计"""
        self.daily_stats = {
            "orders_today": 0,
            "orders_this_minute": 0,
            "turnover_today": 0.0,
            "max_drawdown_today": 0.0
        }
        self.violations = []
        self.log("INFO", "Daily stats reset")
    
    def generate_risk_report(self) -> Dict:
        """生成风控报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "limits": self.limits.__dict__,
            "daily_stats": self.daily_stats,
            "violations_today": len(self.violations),
            "violation_details": self.violations
        }

class EmergencyStop:
    """紧急停止机制"""
    
    def __init__(self):
        self.emergency_level = 0  # 0=正常, 1=警告, 2=限制, 3=停止
        self.stop_signals = []
    
    def trigger(self, level: int, reason: str):
        """触发紧急停止"""
        self.emergency_level = max(self.emergency_level, level)
        self.stop_signals.append({
            "time": datetime.now().isoformat(),
            "level": level,
            "reason": reason
        })
        
        actions = {
            1: "⚠️ WARNING: Risk elevated, monitoring increased",
            2: "🚫 RESTRICTED: Trading limited, reduce positions",
            3: "🛑 EMERGENCY STOP: All trading halted"
        }
        
        print(f"\n{'='*70}")
        print(actions.get(level, "Unknown level"))
        print(f"Reason: {reason}")
        print(f"Time: {datetime.now()}")
        print('='*70)
    
    def is_trading_allowed(self) -> bool:
        """检查是否允许交易"""
        return self.emergency_level < 3
    
    def reset(self):
        """重置紧急状态"""
        self.emergency_level = 0
        self.stop_signals = []
        print("✅ Emergency stop reset - Trading resumed")

def main():
    """测试风控系统"""
    print("="*70)
    print("RISK CONTROL SYSTEM - Production Grade")
    print("="*70)
    
    # 初始化风控
    limits = RiskLimits(
        max_single_stock_position=0.10,
        max_total_drawdown=0.15
    )
    
    risk_ctrl = RiskController(limits)
    emergency = EmergencyStop()
    
    # 测试案例1: 正常交易
    print("\n--- Test 1: Normal Order ---")
    order1 = {
        "symbol": "000001.SZ",
        "current_position": 0.05,
        "target_position": 0.08,
        "industry": "银行",
        "is_st": False,
        "amount": 100000
    }
    result = risk_ctrl.pre_trade_check(order1)
    assert result == True, "Normal order should pass"
    
    # 测试案例2: 超仓位
    print("\n--- Test 2: Position Limit ---")
    order2 = {
        "symbol": "000002.SZ",
        "current_position": 0.08,
        "target_position": 0.15,  # 超过10%限制
        "amount": 200000
    }
    result = risk_ctrl.pre_trade_check(order2)
    assert result == False, "Over-position should be blocked"
    
    # 测试案例3: ST股
    print("\n--- Test 3: ST Stock ---")
    order3 = {
        "symbol": "ST0001.SZ",
        "is_st": True,
        "amount": 50000
    }
    result = risk_ctrl.pre_trade_check(order3)
    assert result == False, "ST stock should be blocked"
    
    # 测试紧急停止
    print("\n--- Test 4: Emergency Stop ---")
    emergency.trigger(2, "Market volatility spike detected")
    assert emergency.is_trading_allowed() == True, "Level 2 allows limited trading"
    
    emergency.trigger(3, "Circuit breaker triggered")
    assert emergency.is_trading_allowed() == False, "Level 3 stops all trading"
    
    # 生成报告
    print("\n" + "="*70)
    print("RISK REPORT")
    print("="*70)
    report = risk_ctrl.generate_risk_report()
    print(json.dumps(report, indent=2, default=str))
    
    # 保存报告
    report_path = "E:/Quant_Production/Production/RiskControl/risk_report.json"
    import os
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Report saved: {report_path}")
    print("\n✅ Risk control system operational")

if __name__ == "__main__":
    main()
