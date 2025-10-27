#!/usr/bin/env python3
"""
GitHub Actions 构建监控脚本
实时显示构建进度和状态
"""

import json
import subprocess
import time
from datetime import datetime

def get_latest_run():
    """获取最新的workflow运行"""
    cmd = 'curl -s "https://api.github.com/repos/gfchfjh/CSBJJWT/actions/runs?per_page=1"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get('workflow_runs'):
        return data['workflow_runs'][0]
    return None

def get_run_jobs(run_id):
    """获取运行的所有任务"""
    cmd = f'curl -s "https://api.github.com/repos/gfchfjh/CSBJJWT/actions/runs/{run_id}/jobs"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get('jobs', [])

def format_duration(started_at, completed_at=None):
    """格式化持续时间"""
    if not started_at:
        return "N/A"
    
    start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
    if completed_at:
        end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
    else:
        end = datetime.now(start.tzinfo)
    
    duration = (end - start).total_seconds()
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    return f"{minutes}分{seconds}秒"

def display_status(run, jobs):
    """显示构建状态"""
    print("\033[2J\033[H")  # 清屏
    print("=" * 80)
    print(f"  🚀 GitHub Actions 实时监控 - v1.14.0")
    print("=" * 80)
    print()
    print(f"运行ID: {run['id']}")
    print(f"工作流: {run['name']}")
    print(f"状态: {run['status']}")
    print(f"分支: {run['head_branch']}")
    print(f"开始时间: {run['created_at']}")
    print(f"查看详情: {run['html_url']}")
    print()
    print("=" * 80)
    print("  📊 任务详情")
    print("=" * 80)
    print()
    
    # 统计
    stats = {
        'queued': 0,
        'in_progress': 0,
        'completed_success': 0,
        'completed_failure': 0,
        'completed_cancelled': 0,
        'completed_skipped': 0
    }
    
    for job in jobs:
        status = job['status']
        conclusion = job.get('conclusion')
        
        if status == 'queued':
            stats['queued'] += 1
        elif status == 'in_progress':
            stats['in_progress'] += 1
        elif status == 'completed':
            if conclusion == 'success':
                stats['completed_success'] += 1
            elif conclusion == 'failure':
                stats['completed_failure'] += 1
            elif conclusion == 'cancelled':
                stats['completed_cancelled'] += 1
            elif conclusion == 'skipped':
                stats['completed_skipped'] += 1
    
    # 显示各个任务
    for job in sorted(jobs, key=lambda x: x['name']):
        status = job['status']
        conclusion = job.get('conclusion')
        name = job['name']
        started_at = job.get('started_at')
        completed_at = job.get('completed_at')
        
        # 状态图标
        if status == 'completed':
            if conclusion == 'success':
                icon = '✅'
            elif conclusion == 'failure':
                icon = '❌'
            elif conclusion == 'skipped':
                icon = '⏭️'
            elif conclusion == 'cancelled':
                icon = '⚠️'
            else:
                icon = '❔'
        elif status == 'in_progress':
            icon = '🔄'
        elif status == 'queued':
            icon = '⏳'
        else:
            icon = '❔'
        
        duration = format_duration(started_at, completed_at)
        
        print(f"{icon} {name}")
        print(f"   状态: {status}", end='')
        if conclusion:
            print(f" | 结论: {conclusion}", end='')
        print(f" | 耗时: {duration}")
        print()
    
    print("=" * 80)
    print("  📈 统计")
    print("=" * 80)
    print(f"✅ 成功: {stats['completed_success']}")
    print(f"🔄 进行中: {stats['in_progress']}")
    print(f"⏳ 排队中: {stats['queued']}")
    print(f"❌ 失败: {stats['completed_failure']}")
    print(f"⚠️  取消: {stats['completed_cancelled']}")
    print(f"⏭️  跳过: {stats['completed_skipped']}")
    print()
    
    total = len(jobs)
    completed = stats['completed_success'] + stats['completed_failure'] + stats['completed_cancelled'] + stats['completed_skipped']
    if total > 0:
        progress = (completed / total) * 100
        print(f"总进度: {completed}/{total} ({progress:.1f}%)")
        print(f"进度条: [{'█' * int(progress/5)}{'░' * (20-int(progress/5))}]")
    
    print()
    print("=" * 80)
    
    # 判断是否完成
    if run['status'] == 'completed':
        conclusion = run.get('conclusion', 'unknown')
        if conclusion == 'success':
            print("🎉 构建成功完成！")
            print()
            print("📦 下载安装包:")
            print("   https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0")
        else:
            print(f"⚠️  构建已完成，状态: {conclusion}")
        print()
        return True
    else:
        print("⏱️  构建进行中，30秒后自动刷新...")
        print("   (按 Ctrl+C 停止监控)")
    
    return False

def main():
    """主函数"""
    print("🔍 开始监控 GitHub Actions 构建...")
    print("⏱️  每30秒自动刷新一次")
    print()
    
    try:
        while True:
            run = get_latest_run()
            if not run:
                print("❌ 未找到构建运行")
                break
            
            jobs = get_run_jobs(run['id'])
            is_completed = display_status(run, jobs)
            
            if is_completed:
                break
            
            # 等待30秒后刷新
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  监控已停止")
        print()
        print("💡 继续查看构建进度:")
        print("   https://github.com/gfchfjh/CSBJJWT/actions")

if __name__ == '__main__':
    main()
