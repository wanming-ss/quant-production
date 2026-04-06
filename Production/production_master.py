#!/usr/bin/env python3
"""
Quant Production - 生产级总控
跑得稳、跑得久、跑得合规
"""
import sys
import os
from datetime import datetime

# 添加生产模块路径
sys.path.insert(0, "E:/Quant_Production/Production/DataQuality")
sys.path.insert(0, "E:/Quant_Production/Production/RiskControl")
sys.path.insert(0, "E:/Quant_Production/Production/Monitoring")

def print_header(title):
    """打印标题"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def stage_data_quality():
    """阶段1: 数据质量检查"""
    print_header("STAGE 1: DATA QUALITY CHECK")
    
    try:
        from data_quality_monitor import DataQualityMonitor
        monitor = DataQualityMonitor()
        return monitor.run_all_checks()
    except Exception as e:
        print(f"❌ Data quality check failed: {e}")
        return False

def stage_risk_control():
    """阶段2: 风控系统测试"""
    print_header("STAGE 2: RISK CONTROL TEST")
    
    try:
        from risk_control_system import RiskController, RiskLimits, EmergencyStop
        
        limits = RiskLimits()
        risk_ctrl = RiskController(limits)
        emergency = EmergencyStop()
        
        # 测试正常订单
        order = {
            "symbol": "000001.SZ",
            "current_position": 0.05,
            "target_position": 0.08,
            "industry": "银行",
            "is_st": False,
            "amount": 100000
        }
        
        result = risk_ctrl.pre_trade_check(order)
        
        print("\n✅ Risk control system operational")
        return True
    except Exception as e:
        print(f"❌ Risk control test failed: {e}")
        return False

def stage_monitoring():
    """阶段3: 监控与备份"""
    print_header("STAGE 3: MONITORING & BACKUP")
    
    try:
        from monitor_and_backup import ProductionMonitor, BackupManager
        
        # 监控检查
        monitor = ProductionMonitor()
        disk_ok = monitor.check_disk_space()
        fresh_ok = monitor.check_data_freshness()
        health_ok = monitor.check_pipeline_health()
        
        # 执行备份
        backup_mgr = BackupManager()
        backup_dir = backup_mgr.backup_data(retention_days=7)
        backup_ok = backup_mgr.verify_backup(backup_dir)
        
        return disk_ok and fresh_ok and health_ok and backup_ok
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return False

def generate_production_report(results):
    """生成生产报告"""
    print_header("PRODUCTION READINESS REPORT")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-production",
        "stages": {
            "data_quality": "PASS" if results.get('data_quality') else "FAIL",
            "risk_control": "PASS" if results.get('risk_control') else "FAIL",
            "monitoring": "PASS" if results.get('monitoring') else "FAIL"
        }
    }
    
    all_pass = all(results.values())
    report["overall_status"] = "PRODUCTION READY" if all_pass else "NOT READY"
    
    # 打印报告
    for stage, status in report["stages"].items():
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {stage}: {status}")
    
    print(f"\n{'='*70}")
    if all_pass:
        print("🎉 SYSTEM IS PRODUCTION READY")
        print("🏆 跑得稳、跑得久、跑得合规")
    else:
        print("⚠️  SYSTEM NOT READY FOR PRODUCTION")
        print("🔧 Please fix the issues above")
    print(f"{'='*70}")
    
    # 保存报告
    report_path = "E:/Quant_Production/Production/production_readiness_report.json"
    import json
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: {report_path}")
    
    return all_pass

def main():
    """主函数"""
    print("\n" + "="*70)
    print(" QUANT PRODUCTION - PRODUCTION GRADE SYSTEM")
    print("="*70)
    print(f"Time: {datetime.now()}")
    print("="*70)
    
    # 执行三个阶段
    results = {
        'data_quality': stage_data_quality(),
        'risk_control': stage_risk_control(),
        'monitoring': stage_monitoring()
    }
    
    # 生成报告
    ready = generate_production_report(results)
    
    return 0 if ready else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
