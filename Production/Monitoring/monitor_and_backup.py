#!/usr/bin/env python3
"""
监控与备份系统 - Monitoring & Backup
跑得合规：数据不可丢，操作可追溯
"""
import os
import json
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

class ProductionMonitor:
    """生产监控系统"""
    
    def __init__(self, base_path="E:/Quant_Production"):
        self.base_path = Path(base_path)
        self.metrics = {}
        self.alerts = []
    
    def log(self, level, message):
        """记录监控日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [MONITOR-{level}] {message}"
        print(log_msg)
        
        log_file = self.base_path / "Production" / "Monitoring" / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def check_disk_space(self, threshold_gb=100):
        """检查磁盘空间"""
        stat = shutil.disk_usage(self.base_path)
        free_gb = stat.free / (1024**3)
        
        self.metrics['disk_free_gb'] = free_gb
        
        if free_gb < threshold_gb:
            self.log("ALERT", f"Low disk space: {free_gb:.1f}GB < {threshold_gb}GB")
            return False
        else:
            self.log("INFO", f"Disk space OK: {free_gb:.1f}GB free")
            return True
    
    def check_data_freshness(self, max_age_hours=24):
        """检查数据新鲜度"""
        data_files = [
            "Inbox/tushare_all_2016_2025.csv",
            "Inbox/tushare_weekly.csv",
            "Inbox/tushare_monthly.csv"
        ]
        
        all_fresh = True
        for file in data_files:
            file_path = self.base_path / file
            if file_path.exists():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_hours = (datetime.now() - mtime).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    self.log("ALERT", f"Stale data: {file} ({age_hours:.1f}h old)")
                    all_fresh = False
                else:
                    self.log("INFO", f"Data fresh: {file} ({age_hours:.1f}h old)")
            else:
                self.log("ALERT", f"Missing data file: {file}")
                all_fresh = False
        
        return all_fresh
    
    def check_pipeline_health(self):
        """检查流水线健康状态"""
        required_files = [
            "Artifacts/train_lightgbm_simple.py",
            "Production/DataQuality/data_quality_monitor.py",
            "Production/RiskControl/risk_control_system.py"
        ]
        
        healthy = True
        for file in required_files:
            file_path = self.base_path / file
            if not file_path.exists():
                self.log("ALERT", f"Missing critical file: {file}")
                healthy = False
        
        if healthy:
            self.log("INFO", "Pipeline health check: OK")
        
        return healthy
    
    def generate_metrics(self):
        """生成监控指标"""
        # 数据量统计
        inbox_size = sum(
            f.stat().st_size for f in (self.base_path / "Inbox").rglob("*") if f.is_file()
        ) / (1024**3)  # GB
        
        self.metrics['data_size_gb'] = inbox_size
        self.metrics['check_time'] = datetime.now().isoformat()
        
        self.log("INFO", f"Total data size: {inbox_size:.2f} GB")
        
        return self.metrics

class BackupManager:
    """备份管理器"""
    
    def __init__(self, base_path="E:/Quant_Production", backup_path="E:/Quant_Production/Production/Backup"):
        self.base_path = Path(base_path)
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def calculate_hash(self, file_path):
        """计算文件哈希"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def backup_data(self, retention_days=7):
        """执行数据备份"""
        print("="*70)
        print("BACKUP MANAGER")
        print("="*70)
        
        backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_path / f"backup_{backup_time}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份清单
        backup_items = [
            ("Inbox/tushare_all_2016_2025.csv", "data"),
            ("Inbox/tushare_weekly.csv", "data"),
            ("Inbox/tushare_monthly.csv", "data"),
            ("Vault/price_volume_divergence.dos", "factor"),
            ("Artifacts/Models/model_config.json", "config"),
        ]
        
        manifest = {
            "backup_time": backup_time,
            "items": []
        }
        
        for item, item_type in backup_items:
            src = self.base_path / item
            if src.exists():
                dst = backup_dir / src.name
                shutil.copy2(src, dst)
                
                file_hash = self.calculate_hash(src)
                manifest["items"].append({
                    "file": item,
                    "type": item_type,
                    "size": src.stat().st_size,
                    "hash": file_hash,
                    "backup_path": str(dst.relative_to(self.backup_path))
                })
                print(f"✅ Backed up: {item} ({src.stat().st_size / 1024**2:.1f} MB)")
            else:
                print(f"⚠️  Missing: {item}")
        
        # 保存清单
        manifest_path = backup_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n📄 Manifest saved: {manifest_path}")
        
        # 清理旧备份
        self.clean_old_backups(retention_days)
        
        return backup_dir
    
    def clean_old_backups(self, retention_days):
        """清理旧备份"""
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for backup_dir in self.backup_path.glob("backup_*"):
            if backup_dir.is_dir():
                dir_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                if dir_time < cutoff:
                    shutil.rmtree(backup_dir)
                    print(f"🗑️  Cleaned old backup: {backup_dir.name}")
    
    def verify_backup(self, backup_dir):
        """验证备份完整性"""
        manifest_path = backup_dir / "manifest.json"
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        all_valid = True
        for item in manifest["items"]:
            file_path = self.backup_path / item["backup_path"]
            if file_path.exists():
                current_hash = self.calculate_hash(file_path)
                if current_hash == item["hash"]:
                    print(f"✅ Verified: {item['file']}")
                else:
                    print(f"❌ Corrupted: {item['file']}")
                    all_valid = False
            else:
                print(f"❌ Missing: {item['file']}")
                all_valid = False
        
        return all_valid

class ComplianceLogger:
    """合规日志记录器"""
    
    def __init__(self, log_path="E:/Quant_Production/Production/Compliance"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
    
    def log_trade(self, trade_info: dict):
        """记录交易日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "TRADE",
            **trade_info
        }
        
        log_file = self.log_path / f"trades_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_decision(self, decision_info: dict):
        """记录决策日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "DECISION",
            **decision_info
        }
        
        log_file = self.log_path / f"decisions_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def main():
    """主函数"""
    print("\n" + "="*70)
    print("PRODUCTION MONITORING & BACKUP SYSTEM")
    print("="*70)
    
    # 1. 监控检查
    monitor = ProductionMonitor()
    monitor.check_disk_space()
    monitor.check_data_freshness()
    monitor.check_pipeline_health()
    monitor.generate_metrics()
    
    # 2. 执行备份
    backup_mgr = BackupManager()
    backup_dir = backup_mgr.backup_data(retention_days=7)
    
    # 3. 验证备份
    print("\n" + "="*70)
    print("VERIFYING BACKUP")
    print("="*70)
    valid = backup_mgr.verify_backup(backup_dir)
    
    if valid:
        print("\n✅ Backup verification PASSED")
    else:
        print("\n❌ Backup verification FAILED")
    
    # 4. 生成最终报告
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70)
    print(f"Backup Location: {backup_dir}")
    print(f"Backup Time: {datetime.now()}")
    print(f"Status: {'✅ OPERATIONAL' if valid else '❌ FAILED'}")
    print("="*70)

if __name__ == "__main__":
    main()
