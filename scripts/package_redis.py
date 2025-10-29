#!/usr/bin/env python3
"""
Redis打包工具
自动下载和准备嵌入式Redis
"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
REDIS_DIR = ROOT_DIR / "redis"
REDIS_DIR.mkdir(parents=True, exist_ok=True)

# Redis下载链接
REDIS_URLS = {
    "windows": "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip",
    "linux": "http://download.redis.io/releases/redis-7.0.15.tar.gz",
    "macos": "http://download.redis.io/releases/redis-7.0.15.tar.gz",
}


def download_file(url, dest):
    """下载文件"""
    print(f"正在下载: {url}")
    urllib.request.urlretrieve(url, dest, reporthook=_download_progress)
    print("\n下载完成")


def _download_progress(block_num, block_size, total_size):
    """下载进度回调"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(downloaded * 100 / total_size, 100)
        print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="")


def extract_archive(archive_path, extract_to):
    """解压文件"""
    print(f"正在解压: {archive_path}")
    
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(extract_to)
    elif archive_path.suffix == ".gz":
        with tarfile.open(archive_path, 'r:gz') as tf:
            tf.extractall(extract_to)
    
    print("解压完成")


def compile_redis_linux():
    """在Linux上编译Redis"""
    print("开始编译Redis...")
    
    # 查找解压后的目录
    redis_src = None
    for item in REDIS_DIR.iterdir():
        if item.is_dir() and item.name.startswith("redis-"):
            redis_src = item
            break
    
    if not redis_src:
        print("错误：未找到Redis源码目录")
        return False
    
    # 编译
    result = subprocess.run(["make"], cwd=redis_src)
    if result.returncode != 0:
        print("编译失败")
        return False
    
    # 复制可执行文件
    redis_server = redis_src / "src" / "redis-server"
    redis_cli = redis_src / "src" / "redis-cli"
    
    if redis_server.exists():
        import shutil
        shutil.copy(redis_server, REDIS_DIR / "redis-server")
        if redis_cli.exists():
            shutil.copy(redis_cli, REDIS_DIR / "redis-cli")
        
        # 赋予执行权限
        (REDIS_DIR / "redis-server").chmod(0o755)
        if (REDIS_DIR / "redis-cli").exists():
            (REDIS_DIR / "redis-cli").chmod(0o755)
        
        print("Redis编译完成")
        return True
    
    return False


def package_redis():
    """打包Redis"""
    os_name = platform.system().lower()
    
    if os_name == "windows":
        url = REDIS_URLS["windows"]
        archive_name = "redis-windows.zip"
    elif os_name == "darwin":
        url = REDIS_URLS["macos"]
        archive_name = "redis-macos.tar.gz"
    else:
        url = REDIS_URLS["linux"]
        archive_name = "redis-linux.tar.gz"
    
    archive_path = REDIS_DIR / archive_name
    
    # 下载
    if not archive_path.exists():
        download_file(url, archive_path)
    
    # 解压
    extract_archive(archive_path, REDIS_DIR)
    
    # Linux/macOS需要编译
    if os_name in ["linux", "darwin"]:
        if not compile_redis_linux():
            print("Redis编译失败，将在安装时提示用户使用系统Redis")
    
    # 创建默认配置文件
    if not (REDIS_DIR / "redis.conf").exists():
        (REDIS_DIR / "redis.conf").write_text("""
# Redis配置文件 - KOOK消息转发系统专用

# 端口
port 6379

# 绑定地址（仅本地）
bind 127.0.0.1

# 数据持久化
save 900 1
save 300 10
save 60 10000

# 日志
loglevel notice

# 数据库数量
databases 16

# 最大内存（512MB）
maxmemory 512mb
maxmemory-policy allkeys-lru
""")
    
    print(f"✅ Redis打包完成：{REDIS_DIR}")


if __name__ == "__main__":
    try:
        package_redis()
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)
