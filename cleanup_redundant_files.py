#!/usr/bin/env python3
"""
代码清理脚本 - 删除冗余版本文件
✅ P0-9优化：清理 *_v2.py, *_enhanced.py, *_ultimate.py 等冗余文件

使用方法:
    python cleanup_redundant_files.py --dry-run  # 预览将要删除的文件
    python cleanup_redundant_files.py --execute  # 实际删除文件
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 冗余文件后缀模式
REDUNDANT_PATTERNS = [
    '_v2.py',
    '_v3.py',
    '_ultimate.py',
    '_async_complete.py',
    '_complete.py',
]

# 需要保留的特殊文件（即使匹配模式也不删除）
KEEP_FILES = [
    'smart_mapping_v2.py',  # 保留，可能在使用
    'filter_enhanced.py',   # 保留，可能在使用
    'worker_enhanced.py',   # 保留，可能在使用
]

# 扫描目录
SCAN_DIRS = [
    'backend/app',
]


class FileCleanup:
    """文件清理器"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.redundant_files = []
        self.total_size = 0
        
    def scan(self):
        """扫描冗余文件"""
        print("🔍 正在扫描冗余文件...\n")
        
        for scan_dir in SCAN_DIRS:
            full_path = self.workspace_root / scan_dir
            if not full_path.exists():
                print(f"⚠️  目录不存在: {scan_dir}")
                continue
                
            print(f"📂 扫描目录: {scan_dir}")
            self._scan_directory(full_path, scan_dir)
        
        print(f"\n✅ 扫描完成！找到 {len(self.redundant_files)} 个冗余文件")
        print(f"💾 预计释放空间: {self.total_size / 1024:.2f} KB")
        
    def _scan_directory(self, directory: Path, rel_path: str):
        """递归扫描目录"""
        for item in directory.iterdir():
            if item.is_dir():
                # 跳过 __pycache__ 和 .git
                if item.name in ['__pycache__', '.git', 'node_modules']:
                    continue
                self._scan_directory(item, str(Path(rel_path) / item.name))
            elif item.is_file():
                self._check_file(item, rel_path)
    
    def _check_file(self, file_path: Path, rel_path: str):
        """检查文件是否为冗余文件"""
        filename = file_path.name
        
        # 检查是否匹配冗余模式
        is_redundant = False
        matched_pattern = None
        
        for pattern in REDUNDANT_PATTERNS:
            if filename.endswith(pattern):
                is_redundant = True
                matched_pattern = pattern
                break
        
        if not is_redundant:
            return
        
        # 检查是否在保留列表中
        if filename in KEEP_FILES:
            print(f"  ⚠️  跳过（保留）: {rel_path}/{filename}")
            return
        
        # 检查基础文件是否存在
        base_name = filename.replace(matched_pattern, '.py')
        base_file = file_path.parent / base_name
        
        if base_file.exists():
            file_size = file_path.stat().st_size
            self.redundant_files.append({
                'path': file_path,
                'rel_path': f"{rel_path}/{filename}",
                'size': file_size,
                'pattern': matched_pattern,
                'base_file': base_name,
                'base_exists': True
            })
            self.total_size += file_size
            print(f"  ✅ 找到: {rel_path}/{filename} ({file_size} bytes, 基础文件存在)")
        else:
            print(f"  ⚠️  跳过: {rel_path}/{filename} (基础文件不存在，可能在使用)")
    
    def print_summary(self):
        """打印汇总信息"""
        print("\n" + "=" * 70)
        print("📋 冗余文件汇总")
        print("=" * 70)
        
        if not self.redundant_files:
            print("✅ 未发现冗余文件！代码库已经很干净了。")
            return
        
        # 按模式分组
        by_pattern = {}
        for file_info in self.redundant_files:
            pattern = file_info['pattern']
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(file_info)
        
        for pattern, files in by_pattern.items():
            print(f"\n📦 模式: {pattern} ({len(files)}个文件)")
            for file_info in files:
                print(f"   - {file_info['rel_path']}")
        
        print(f"\n📊 统计:")
        print(f"   - 冗余文件总数: {len(self.redundant_files)}")
        print(f"   - 预计释放空间: {self.total_size / 1024:.2f} KB")
        print("=" * 70)
    
    def backup_files(self):
        """备份文件到backup目录"""
        backup_dir = self.workspace_root / 'backup' / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 正在备份文件到: {backup_dir}")
        
        for file_info in self.redundant_files:
            src = file_info['path']
            rel = Path(file_info['rel_path'])
            dst = backup_dir / rel
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            import shutil
            shutil.copy2(src, dst)
            print(f"  ✅ 已备份: {file_info['rel_path']}")
        
        print(f"✅ 备份完成！备份位置: {backup_dir}")
        return backup_dir
    
    def delete_files(self, create_backup=True):
        """删除冗余文件"""
        if not self.redundant_files:
            print("✅ 没有需要删除的文件")
            return
        
        # 创建备份
        if create_backup:
            backup_dir = self.backup_files()
            print(f"\n📋 备份已创建，如需恢复请访问: {backup_dir}")
        
        print("\n🗑️  正在删除冗余文件...")
        deleted_count = 0
        
        for file_info in self.redundant_files:
            try:
                file_info['path'].unlink()
                print(f"  ✅ 已删除: {file_info['rel_path']}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file_info['rel_path']} - {str(e)}")
        
        print(f"\n✅ 清理完成！删除了 {deleted_count}/{len(self.redundant_files)} 个文件")
        print(f"💾 释放空间: {self.total_size / 1024:.2f} KB")


def main():
    parser = argparse.ArgumentParser(description='清理冗余代码文件')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际删除文件')
    parser.add_argument('--execute', action='store_true', help='执行删除操作')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份（危险）')
    
    args = parser.parse_args()
    
    # 获取工作区根目录
    workspace_root = Path(__file__).parent
    
    print("=" * 70)
    print("🧹 KOOK消息转发系统 - 代码清理工具")
    print("=" * 70)
    print(f"📁 工作区: {workspace_root}")
    print()
    
    # 创建清理器
    cleanup = FileCleanup(workspace_root)
    
    # 扫描文件
    cleanup.scan()
    
    # 打印汇总
    cleanup.print_summary()
    
    # 执行操作
    if args.dry_run or not args.execute:
        print("\n💡 这是预览模式，未实际删除文件。")
        print("💡 如需删除，请运行: python cleanup_redundant_files.py --execute")
    else:
        print("\n⚠️  即将删除冗余文件！")
        response = input("确定要继续吗？(yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            cleanup.delete_files(create_backup=not args.no_backup)
            print("\n✅ 代码清理完成！")
        else:
            print("\n❌ 操作已取消")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
