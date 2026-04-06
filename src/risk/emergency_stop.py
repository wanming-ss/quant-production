#!/usr/bin/env python3
"""
紧急停止机制 - Emergency Stop

跑得久：极端情况下的硬保护
"""

from datetime import datetime
from typing import List, Dict
import json


class EmergencyStop:
    """紧急停止机制"""
    
    def __init__(self):
        self.emergency_level = 0  # 0=正常，1=警告，2=限制，3=停止
        self.stop_signals: List[Dict] = []
        self.triggered_at: datetime = None
        self.reason: str = ""
    
    def trigger(self, level: int, reason: str) -> None:
        """
        触发紧急停止
        
        Args:
            level: 紧急级别 (1=警告，2=限制，3=停止)
            reason: 停止原因
        """
        if level < 1 or level > 3:
            raise ValueError("Emergency level must be 1, 2, or 3")
        
        self.emergency_level = max(self.emergency_level, level)
        self.triggered_at = datetime.now()
        self.reason = reason
        
        signal = {
            "time": self.triggered_at.isoformat(),
            "level": level,
            "reason": reason
        }
        self.stop_signals.append(signal)
        
        actions = {
            1: "⚠️ WARNING: Risk elevated, monitoring increased",
            2: "🚫 RESTRICTED: Trading limited, reduce positions",
            3: "🛑 EMERGENCY STOP: All trading halted"
        }
        
        print("\n" + "="*70)
        print(actions.get(level, "Unknown level"))
        print(f"Reason: {reason}")
        print(f"Time: {self.triggered_at}")
        print("="*70)
    
    def is_trading_allowed(self) -> bool:
        """检查是否允许交易"""
        return self.emergency_level < 3
    
    def is_limited_trading(self) -> bool:
        """检查是否是限制交易模式"""
        return self.emergency_level == 2
    
    def reset(self) -> None:
        """重置紧急状态"""
        old_level = self.emergency_level
        self.emergency_level = 0
        self.stop_signals = []
        self.triggered_at = None
        self.reason = ""
        
        print(f"✅ Emergency stop reset (was level {old_level}) - Trading resumed")
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "level": self.emergency_level,
            "status": self._level_to_status(),
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "reason": self.reason,
            "total_triggers": len(self.stop_signals)
        }
    
    def _level_to_status(self) -> str:
        """级别转状态文本"""
        status_map = {
            0: "NORMAL",
            1: "WARNING",
            2: "RESTRICTED",
            3: "STOPPED"
        }
        return status_map.get(self.emergency_level, "UNKNOWN")
    
    def generate_report(self) -> Dict:
        """生成紧急停止报告"""
        return {
            "current_status": self.get_status(),
            "history": self.stop_signals,
            "last_reset": None  # 可添加重置时间追踪
        }


def main():
    """测试紧急停止机制"""
    print("="*70)
    print("EMERGENCY STOP SYSTEM - Test")
    print("="*70)
    
    emergency = EmergencyStop()
    
    # 测试各级别
    print("\n--- Level 1: Warning ---")
    emergency.trigger(1, "Market volatility increasing")
    print(f"Trading allowed: {emergency.is_trading_allowed()}")
    
    print("\n--- Level 2: Restricted ---")
    emergency.trigger(2, "Drawdown approaching limit")
    print(f"Trading allowed: {emergency.is_trading_allowed()}")
    print(f"Limited trading: {emergency.is_limited_trading()}")
    
    print("\n--- Level 3: Stop ---")
    emergency.trigger(3, "Circuit breaker triggered")
    print(f"Trading allowed: {emergency.is_trading_allowed()}")
    
    print("\n--- Status Report ---")
    print(json.dumps(emergency.generate_report(), indent=2, default=str))
    
    print("\n--- Reset ---")
    emergency.reset()
    print(f"Trading allowed: {emergency.is_trading_allowed()}")


if __name__ == "__main__":
    main()
