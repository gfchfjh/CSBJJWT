"""
KOOK Forwarder - 完整问题修复脚本
一次性修复所有已知的代码问题
"""
import os
import re
from pathlib import Path

print("=" * 60)
print("KOOK Forwarder - 完整修复脚本")
print("=" * 60)
print()

# 基础目录
base_dir = Path(__file__).parent / "KOOK-Build" / "CSBJJWT" / "backend"

fixes_applied = 0
files_processed = 0

def apply_fixes(filepath, fixes):
    """应用修复到文件"""
    global fixes_applied, files_processed
    
    if not filepath.exists():
        print(f"[跳过] {filepath.relative_to(base_dir)} - 文件不存在")
        return False
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new, 1)
                fixes_applied += 1
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            files_processed += 1
            print(f"[✓] {filepath.relative_to(base_dir)} - 已修复")
            return True
        else:
            print(f"[OK] {filepath.relative_to(base_dir)} - 无需修复")
            return False
            
    except Exception as e:
        print(f"[✗] {filepath.relative_to(base_dir)} - 错误: {e}")
        return False

# 定义所有修复
print("开始应用修复...\n")

# 1. accounts.py - 添加 Request 导入
apply_fixes(base_dir / "app/api/accounts.py", [
    ('from fastapi import APIRouter, HTTPException',
     'from fastapi import APIRouter, HTTPException, Request'),
])

# 2. password_reset_enhanced.py - 添加 Dict 导入
pfile = base_dir / "app/api/password_reset_enhanced.py"
if pfile.exists():
    content = pfile.read_text(encoding='utf-8')
    if 'from typing import' not in content or 'Dict' not in content.split('\n')[10]:
        # 在第一个 import 前添加
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('from fastapi') or line.strip().startswith('from pydantic'):
                lines.insert(i, 'from typing import Dict, Any, Optional')
                pfile.write_text('\n'.join(lines), encoding='utf-8')
                print(f"[✓] password_reset_enhanced.py - 已添加 Dict 导入")
                fixes_applied += 1
                files_processed += 1
                break

# 3. environment_autofix.py - 修复 redis_manager 导入
apply_fixes(base_dir / "app/api/environment_autofix.py", [
    ('from ..utils.redis_manager_ultimate import redis_manager',
     'from ..utils.redis_manager import redis_manager'),
])

# 4. performance.py - 修复 redis_queue
pfile = base_dir / "app/api/performance.py"
if pfile.exists():
    content = pfile.read_text(encoding='utf-8')
    # 只修复导入行
    content = content.replace(
        'from ..queue.redis_client import redis_client',
        'from ..queue.redis_client import redis_queue'
    )
    # 修复使用的地方（但要小心不破坏其他代码）
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if 'import' not in line and 'def ' not in line and 'class ' not in line:
            line = line.replace('redis_client.', 'redis_queue.')
            line = line.replace('redis_client)', 'redis_queue)')
            line = line.replace('redis_client,', 'redis_queue,')
            line = line.replace(' redis_client ', ' redis_queue ')
        new_lines.append(line)
    pfile.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"[✓] performance.py - 已修复 redis_queue")
    fixes_applied += 1
    files_processed += 1

# 5. 修复所有导入层级问题（from ... 改成 from ..）
api_files = [
    'wizard_testing_enhanced.py',
    'image_storage_manager.py', 
    'rate_limit_monitor.py',
    'message_search.py',
]

for filename in api_files:
    filepath = base_dir / "app/api" / filename
    if filepath.exists():
        content = filepath.read_text(encoding='utf-8')
        new_content = content.replace('from ...', 'from ..')
        if new_content != content:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"[✓] {filename} - 已修复导入层级")
            fixes_applied += 1
            files_processed += 1

# 6. middleware/auth_middleware.py - 添加 Optional 导入
mfile = base_dir / "app/middleware/auth_middleware.py"
if mfile.exists():
    content = mfile.read_text(encoding='utf-8')
    if 'from typing import' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('from starlette') or line.strip().startswith('from fastapi'):
                lines.insert(i, 'from typing import Optional, Dict, Any')
                mfile.write_text('\n'.join(lines), encoding='utf-8')
                print(f"[✓] auth_middleware.py - 已添加 typing 导入")
                fixes_applied += 1
                files_processed += 1
                break

# 7. kook/scraper.py - 修复 parse_message 为异步
apply_fixes(base_dir / "app/kook/scraper.py", [
    ('    def parse_message(self, data: Dict)', '    async def parse_message(self, data: Dict)'),
    ('                message = self.parse_message(data)', '                message = await self.parse_message(data)'),
])

# 8. processors/image.py - 注释掉清理任务
apply_fixes(base_dir / "app/processors/image.py", [
    ('        self.start_cleanup_task()',
     '        # self.start_cleanup_task()  # Disabled: no event loop during init'),
])

# 9. utils/rate_limiter.py - 添加 RateLimiterManager
rfile = base_dir / "app/utils/rate_limiter.py"
if rfile.exists():
    content = rfile.read_text(encoding='utf-8')
    if 'RateLimiterManager' not in content:
        manager_code = '''


class RateLimiterManager:
    """速率限制器管理器"""
    
    def __init__(self):
        self.limiters = {}
    
    def get_limiter(self, name: str, calls: int, period: int) -> 'RateLimiter':
        """获取或创建限流器"""
        if name not in self.limiters:
            self.limiters[name] = RateLimiter(calls, period)
        return self.limiters[name]


# 全局管理器实例
rate_limiter_manager = RateLimiterManager()
'''
        content += manager_code
        rfile.write_text(content, encoding='utf-8')
        print(f"[✓] rate_limiter.py - 已添加 RateLimiterManager")
        fixes_applied += 1
        files_processed += 1

print()
print("=" * 60)
print(f"修复完成！共修复 {files_processed} 个文件，应用 {fixes_applied} 处修复")
print("=" * 60)
