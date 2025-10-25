#!/usr/bin/env python3
"""
Redis服务跨平台自动准备脚本（终极版）
=====================================
功能：
1. 自动检测操作系统
2. 下载对应平台的Redis二进制文件
3. 生成redis.conf配置文件
4. 验证Redis可用性
5. 支持Windows/Linux/macOS
6. 智能缓存避免重复下载

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import os
import sys
import platform
import subprocess
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Tuple

class RedisPreparer:
    """Redis服务准备器（终极版）"""
    
    # Redis版本和下载链接
    REDIS_VERSIONS = {
        'Windows': {
            'version': '5.0.14.1',
            'url': 'https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip',
            'filename': 'Redis-x64-5.0.14.1.zip'
        },
        'Linux': {
            'version': '7.2.5',
            'url': 'https://download.redis.io/releases/redis-7.2.5.tar.gz',
            'filename': 'redis-7.2.5.tar.gz'
        },
        'Darwin': {  # macOS
            'version': '7.2.5',
            'url': 'https://download.redis.io/releases/redis-7.2.5.tar.gz',
            'filename': 'redis-7.2.5.tar.gz'
        }
    }
    
    def __init__(self, build_dir: Path = None):
        self.system = platform.system()
        self.build_dir = build_dir or Path(__file__).parent.parent / "dist"
        self.redis_dir = self.build_dir / "redis"
        self.cache_dir = Path.home() / ".cache" / "kook-forwarder-build"
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def download_redis(self) -> Tuple[bool, Path]:
        """
        下载Redis二进制文件
        
        Returns:
            (是否成功, 下载文件路径)
        """
        print(f"\n📥 下载Redis二进制文件...")
        
        if self.system not in self.REDIS_VERSIONS:
            print(f"❌ 不支持的操作系统: {self.system}")
            return False, None
        
        version_info = self.REDIS_VERSIONS[self.system]
        url = version_info['url']
        filename = version_info['filename']
        cache_file = self.cache_dir / filename
        
        # 检查缓存
        if cache_file.exists():
            print(f"✅ 使用缓存文件: {cache_file}")
            return True, cache_file
        
        print(f"📦 版本: {version_info['version']}")
        print(f"🔗 URL: {url}")
        print(f"💾 保存到: {cache_file}")
        
        try:
            # 下载文件（带进度显示）
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                print(f"\r下载进度: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)", end='')
            
            urllib.request.urlretrieve(url, cache_file, reporthook=report_progress)
            print()  # 换行
            
            print(f"✅ 下载完成: {cache_file}")
            return True, cache_file
            
        except Exception as e:
            print(f"\n❌ 下载失败: {str(e)}")
            return False, None
    
    def extract_redis_windows(self, archive_path: Path) -> bool:
        """
        解压Windows版Redis（ZIP格式）
        
        Args:
            archive_path: ZIP文件路径
            
        Returns:
            是否成功
        """
        print("\n📦 解压Redis（Windows）...")
        
        try:
            # 删除旧的redis目录
            if self.redis_dir.exists():
                shutil.rmtree(self.redis_dir)
            
            self.redis_dir.mkdir(parents=True)
            
            # 解压ZIP文件
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(self.redis_dir)
            
            print(f"✅ 解压完成: {self.redis_dir}")
            
            # 验证文件
            redis_server = self.redis_dir / "redis-server.exe"
            redis_cli = self.redis_dir / "redis-cli.exe"
            
            if redis_server.exists() and redis_cli.exists():
                print("✅ Redis可执行文件验证通过")
                return True
            else:
                print("❌ Redis可执行文件缺失")
                return False
                
        except Exception as e:
            print(f"❌ 解压失败: {str(e)}")
            return False
    
    def compile_redis_unix(self, archive_path: Path) -> bool:
        """
        编译Unix版Redis（源码tar.gz格式）
        
        Args:
            archive_path: tar.gz文件路径
            
        Returns:
            是否成功
        """
        print("\n🔨 编译Redis（Linux/macOS）...")
        
        try:
            # 创建临时编译目录
            compile_dir = self.cache_dir / "redis_compile"
            if compile_dir.exists():
                shutil.rmtree(compile_dir)
            compile_dir.mkdir(parents=True)
            
            # 解压源码
            print("📦 解压源码...")
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(compile_dir)
            
            # 找到源码目录
            source_dirs = list(compile_dir.glob("redis-*"))
            if not source_dirs:
                print("❌ 未找到Redis源码目录")
                return False
            
            source_dir = source_dirs[0]
            print(f"📁 源码目录: {source_dir}")
            
            # 编译Redis
            print("🔨 开始编译（可能需要几分钟）...")
            result = subprocess.run(
                ["make"],
                cwd=source_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                print(f"❌ 编译失败: {result.stderr}")
                return False
            
            print("✅ 编译完成")
            
            # 复制可执行文件到redis目录
            if self.redis_dir.exists():
                shutil.rmtree(self.redis_dir)
            self.redis_dir.mkdir(parents=True)
            
            src_dir = source_dir / "src"
            executables = ["redis-server", "redis-cli", "redis-check-aof", "redis-check-rdb"]
            
            for exe in executables:
                src_file = src_dir / exe
                dst_file = self.redis_dir / exe
                
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    # 设置执行权限
                    os.chmod(dst_file, 0o755)
                    print(f"✅ 复制: {exe}")
            
            # 清理编译目录
            shutil.rmtree(compile_dir)
            
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 编译超时")
            return False
        except Exception as e:
            print(f"❌ 编译失败: {str(e)}")
            return False
    
    def generate_redis_conf(self) -> bool:
        """
        生成redis.conf配置文件
        
        Returns:
            是否成功
        """
        print("\n📝 生成redis.conf配置文件...")
        
        try:
            config_content = """# Redis配置文件（KOOK Forwarder定制版）
# 生成时间: 2025-10-25

# 基础配置
port 6379
bind 127.0.0.1
protected-mode yes
timeout 0
tcp-keepalive 300

# 持久化配置
save 60 1
save 300 10
save 900 100
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./data/redis

# AOF配置
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru

# 日志
loglevel notice
logfile "./data/redis/redis.log"

# 性能优化
tcp-backlog 511
databases 16
"""
            
            config_path = self.redis_dir / "redis.conf"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print(f"✅ 配置文件已生成: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成配置失败: {str(e)}")
            return False
    
    def verify_redis(self) -> bool:
        """
        验证Redis可用性
        
        Returns:
            是否可用
        """
        print("\n🔬 验证Redis可用性...")
        
        if self.system == "Windows":
            redis_server = self.redis_dir / "redis-server.exe"
        else:
            redis_server = self.redis_dir / "redis-server"
        
        if not redis_server.exists():
            print(f"❌ redis-server不存在: {redis_server}")
            return False
        
        try:
            # 获取版本信息
            result = subprocess.run(
                [str(redis_server), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Redis可用: {version}")
                return True
            else:
                print(f"❌ Redis无法运行: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 验证失败: {str(e)}")
            return False
    
    def prepare(self) -> bool:
        """
        完整准备流程
        
        Returns:
            是否准备成功
        """
        print("=" * 60)
        print("🚀 Redis服务跨平台自动准备系统（终极版）")
        print("=" * 60)
        print(f"操作系统: {self.system}")
        print(f"构建目录: {self.build_dir}")
        print()
        
        # 步骤1: 下载Redis
        success, archive_path = self.download_redis()
        if not success:
            print("\n❌ Redis下载失败")
            return False
        
        # 步骤2: 解压/编译Redis
        if self.system == "Windows":
            if not self.extract_redis_windows(archive_path):
                print("\n❌ Redis解压失败")
                return False
        else:
            if not self.compile_redis_unix(archive_path):
                print("\n❌ Redis编译失败")
                return False
        
        # 步骤3: 生成配置文件
        if not self.generate_redis_conf():
            print("\n❌ 配置生成失败")
            return False
        
        # 步骤4: 验证可用性
        if not self.verify_redis():
            print("\n❌ Redis验证失败")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Redis服务准备完成！")
        print("=" * 60)
        print(f"📁 Redis位置: {self.redis_dir}")
        
        if self.system == "Windows":
            print(f"📦 可执行文件: redis-server.exe, redis-cli.exe")
        else:
            print(f"📦 可执行文件: redis-server, redis-cli")
        
        print(f"📝 配置文件: redis.conf")
        print()
        print("🎯 下一步：将此目录打包进最终安装包")
        print()
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Redis服务跨平台自动准备系统')
    parser.add_argument(
        '--build-dir',
        type=Path,
        help='构建目录路径（默认: ../dist）'
    )
    
    args = parser.parse_args()
    
    preparer = RedisPreparer(build_dir=args.build_dir)
    success = preparer.prepare()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
