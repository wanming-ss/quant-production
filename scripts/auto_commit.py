#!/usr/bin/env python3
"""
自动提交脚本 - Auto Commit Script

功能:
1. 检查是否有新文件/修改
2. 自动添加、提交、推送
3. 生成提交日志
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("E:/Quant_Production")

# 需要忽略的文件模式
IGNORE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    "*.log",
    "*.tmp",
    ".git/",
    "data/",
    "Inbox/*.csv",
    "Production/Backup/",
]

def run_command(cmd, cwd=None):
    """运行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_status():
    """检查 Git 状态"""
    print("🔍 检查 Git 状态...")
    success, stdout, stderr = run_command("git status --porcelain")
    
    if not success:
        print(f"❌ Git 状态检查失败：{stderr}")
        return None
    
    changed_files = [line for line in stdout.strip().split('\n') if line.strip()]
    return changed_files

def add_files():
    """添加文件到暂存区"""
    print("📦 添加文件...")
    success, stdout, stderr = run_command("git add -A")
    return success

def commit_changes():
    """提交更改"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"chore: Auto commit {timestamp}\n\n🤖 Automated update by CI/CD bot"
    
    print(f"💾 提交更改：{commit_msg}")
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    
    if not success and "nothing to commit" in stderr:
        print("ℹ️  没有需要提交的内容")
        return False
    
    return success

def push_changes():
    """推送到 GitHub"""
    print("🚀 推送到 GitHub...")
    success, stdout, stderr = run_command("git push origin main")
    return success

def get_commit_stats():
    """获取提交统计"""
    success, stdout, stderr = run_command("git log --oneline -5")
    if success:
        print("\n📊 最近 5 次提交:")
        print(stdout)

def main():
    """主函数"""
    print("="*70)
    print(" 🤖 Auto Commit Script")
    print("="*70)
    print(f"⏰ 时间：{datetime.now()}")
    print(f"📁 目录：{PROJECT_ROOT}")
    print("="*70)
    
    # 1. 检查状态
    changed_files = check_git_status()
    
    if not changed_files:
        print("✅ 没有更改，无需提交")
        return 0
    
    print(f"📝 发现 {len(changed_files)} 个更改的文件:")
    for file in changed_files[:10]:  # 只显示前 10 个
        print(f"   {file}")
    if len(changed_files) > 10:
        print(f"   ... 还有 {len(changed_files) - 10} 个文件")
    
    # 2. 添加文件
    if not add_files():
        print("❌ 添加文件失败")
        return 1
    
    # 3. 提交
    if not commit_changes():
        print("ℹ️  提交跳过（无更改）")
        return 0
    
    # 4. 推送
    if not push_changes():
        print("❌ 推送失败")
        return 1
    
    # 5. 显示统计
    get_commit_stats()
    
    print("\n" + "="*70)
    print(" ✅ 自动提交完成！")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
