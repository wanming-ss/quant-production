#!/usr/bin/env python3
"""
数据质量监控系统 - Data Quality Monitor
跑得稳：确保数据无误才能交易
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, data_path="E:/Quant_Production/Inbox"):
        self.data_path = data_path
        self.issues = []
        self.checks_passed = 0
        self.checks_failed = 0
    
    def log(self, level, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        if level == "ERROR":
            self.issues.append({
                "time": timestamp,
                "level": level,
                "message": message
            })
            self.checks_failed += 1
        else:
            self.checks_passed += 1
    
    def check_price_jump(self, df, symbol_col='symbol', price_col='close', threshold=0.11):
        """检测价格跳空（涨停/跌停/异常波动）"""
        self.log("INFO", f"Checking price jumps (threshold: {threshold*100}%)")
        
        df = df.sort_values([symbol_col, 'date'])
        df['price_change'] = df.groupby(symbol_col)[price_col].pct_change()
        
        # 检测异常跳空
        jumps = df[abs(df['price_change']) > threshold]
        
        if len(jumps) > 0:
            # 区分正常涨停和异常
            normal_limits = jumps[
                (jumps['price_change'].between(0.095, 0.105)) |  # 正常涨停
                (jumps['price_change'].between(-0.105, -0.095))   # 正常跌停
            ]
            abnormal = jumps[~jumps.index.isin(normal_limits.index)]
            
            if len(abnormal) > 0:
                self.log("ERROR", f"Found {len(abnormal)} abnormal price jumps")
                self.log("ERROR", f"Examples: {abnormal[[symbol_col, 'date', 'price_change']].head().to_dict()}")
            else:
                self.log("INFO", f"All {len(jumps)} jumps are within normal limit range")
        else:
            self.log("INFO", "No price jumps detected")
    
    def check_volume_anomaly(self, df, symbol_col='symbol', volume_col='volume'):
        """检测成交量异常"""
        self.log("INFO", "Checking volume anomalies")
        
        # 0成交量
        zero_volume = df[df[volume_col] == 0]
        if len(zero_volume) > 0:
            self.log("ERROR", f"Found {len(zero_volume)} zero-volume records")
        else:
            self.log("INFO", "No zero-volume records")
        
        # 天量（20日均量5倍以上）
        df = df.sort_values([symbol_col, 'date'])
        df['vol_ma20'] = df.groupby(symbol_col)[volume_col].transform(lambda x: x.rolling(20).mean())
        df['vol_ratio'] = df[volume_col] / df['vol_ma20']
        
        extreme_volume = df[df['vol_ratio'] > 5]
        if len(extreme_volume) > 100:  # 少量天量正常
            self.log("WARN", f"Found {len(extreme_volume)} extreme volume records (>5x average)")
        else:
            self.log("INFO", "Volume distribution normal")
    
    def check_adj_factor_continuity(self, df, symbol_col='symbol', adj_col='adj_factor'):
        """检测复权因子连续性"""
        self.log("INFO", "Checking adjustment factor continuity")
        
        df = df.sort_values([symbol_col, 'date'])
        
        # 检测复权因子突变
        df['adj_change'] = df.groupby(symbol_col)[adj_col].pct_change()
        
        # 除权除息日允许30%变化，其他时间应<1%
        abnormal_adj = df[
            (abs(df['adj_change']) > 0.01) & 
            (abs(df['adj_change']) < 0.30)
        ]
        
        if len(abnormal_adj) > 0:
            self.log("ERROR", f"Found {len(abnormal_adj)} suspicious adj_factor changes")
        else:
            self.log("INFO", "Adj factor continuity OK")
    
    def check_data_completeness(self, df, symbol_col='symbol', date_col='date'):
        """检测数据完整性"""
        self.log("INFO", "Checking data completeness")
        
        # 每只股票应有连续交易日
        df[date_col] = pd.to_datetime(df[date_col])
        
        completeness_report = []
        for symbol in df[symbol_col].unique()[:10]:  # 抽查10只
            symbol_df = df[df[symbol_col] == symbol]
            date_range = symbol_df[date_col].max() - symbol_df[date_col].min()
            expected_days = date_range.days * 0.7  # 假设70%为交易日
            actual_days = len(symbol_df)
            
            if actual_days < expected_days * 0.9:
                completeness_report.append(f"{symbol}: {actual_days}/{int(expected_days)} days")
        
        if completeness_report:
            self.log("WARN", f"Data completeness issues: {completeness_report}")
        else:
            self.log("INFO", "Data completeness OK (sampled 10 stocks)")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("="*70)
        print("DATA QUALITY MONITOR - Production Grade")
        print("="*70)
        print(f"Time: {datetime.now()}")
        print(f"Data Path: {self.data_path}")
        print("="*70)
        
        # 1. 检查日线数据
        daily_path = os.path.join(self.data_path, "tushare_all_2016_2025.csv")
        if os.path.exists(daily_path):
            self.log("INFO", "Loading daily data...")
            daily_df = pd.read_csv(daily_path, usecols=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
            
            self.check_price_jump(daily_df)
            self.check_volume_anomaly(daily_df)
            self.check_data_completeness(daily_df)
        else:
            self.log("ERROR", f"Daily data not found: {daily_path}")
        
        # 2. 检查复权因子
        adj_path = os.path.join(self.data_path, "tushare_adj_factor.csv")
        if os.path.exists(adj_path):
            self.log("INFO", "Loading adjustment factor...")
            adj_df = pd.read_csv(adj_path, usecols=['symbol', 'date', 'adj_factor'])
            self.check_adj_factor_continuity(adj_df)
        else:
            self.log("ERROR", f"Adj factor not found: {adj_path}")
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成质量报告"""
        print("\n" + "="*70)
        print("QUALITY REPORT")
        print("="*70)
        
        total_checks = self.checks_passed + self.checks_failed
        pass_rate = self.checks_passed / total_checks * 100 if total_checks > 0 else 0
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {self.checks_passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.checks_failed}")
        
        if self.issues:
            print(f"\n⚠️  Issues Found: {len(self.issues)}")
            for issue in self.issues[:5]:  # 显示前5个
                print(f"  - {issue['message']}")
        else:
            print("\n✅ No critical issues found")
        
        # 保存报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks_total": total_checks,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "pass_rate": pass_rate,
            "issues": self.issues
        }
        
        report_path = "E:/Quant_Production/Production/DataQuality/quality_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
        
        # 数据质量门控
        if pass_rate < 95:
            print("\n❌ DATA QUALITY CHECK FAILED - Trading halted")
            return False
        else:
            print("\n✅ DATA QUALITY CHECK PASSED - Ready for trading")
            return True

def main():
    monitor = DataQualityMonitor()
    return monitor.run_all_checks()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
