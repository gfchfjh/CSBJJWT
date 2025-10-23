#!/usr/bin/env python3
"""
Redis嵌入式准备工具（增强版）
自动下载和配置Redis for Windows/Linux/macOS
"""
import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
import subprocess
from pathlib import Path

def print_info(msg):
    print(f"\033[94mℹ️  {msg}\033[0m")

def print_success(msg):
    print(f"\033[92m✅ {msg}\033[0m")

def print_error(msg):
    print(f"\033[91m❌ {msg}\033[0m")

def print_warning(msg):
    print(f"\033[93m⚠️  {msg}\033[0m")

def detect_platform():
    """检测操作系统平台"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'windows':
        return 'windows', 'x64' if '64' in machine else 'x86'
    elif system == 'darwin':
        return 'macos', 'arm64' if 'arm' in machine else 'x64'
    elif system == 'linux':
        return 'linux', 'x64' if '64' in machine else 'x86'
    else:
        return 'unknown', 'unknown'

def download_file(url, dest):
    """下载文件"""
    print_info(f"下载: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(dest, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  进度: {percent:.1f}% ({downloaded}/{total_size})", end='', flush=True)
            
            print()  # 换行
            return True
    except Exception as e:
        print_error(f"下载失败: {e}")
        return False

def download_redis_windows(dest_dir: Path):
    """下载Windows版Redis"""
    print_info("下载Windows版Redis...")
    
    # 使用Redis for Windows（非官方但稳定）
    version = "5.0.14.1"
    url = f"https://github.com/tporadowski/redis/releases/download/v{version}/Redis-x64-{version}.zip"
    zip_file = dest_dir / "redis-windows.zip"
    
    if not download_file(url, zip_file):
        print_warning("从GitHub下载失败，尝试备用源...")
        # 可以添加备用下载地址
        return False
    
    # 解压
    print_info("解压Redis...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(dest_dir / "redis-windows-temp")
    
    # 移动文件
    redis_dir = dest_dir / "redis-windows"
    if redis_dir.exists():
        shutil.rmtree(redis_dir)
    
    shutil.move(dest_dir / "redis-windows-temp", redis_dir)
    zip_file.unlink()
    
    print_success(f"Windows版Redis已准备: {redis_dir}")
    return True

def download_redis_linux(dest_dir: Path):
    """下载Linux版Redis"""
    print_info("编译Linux版Redis...")
    
    # Redis官方源码
    version = "7.0.15"
    url = f"https://download.redis.io/releases/redis-{version}.tar.gz"
    tar_file = dest_dir / "redis-linux.tar.gz"
    
    if not download_file(url, tar_file):
        return False
    
    # 解压
    print_info("解压Redis源码...")
    with tarfile.open(tar_file, 'r:gz') as tar_ref:
        tar_ref.extractall(dest_dir)
    
    # 编译
    redis_src = dest_dir / f"redis-{version}"
    print_info("编译Redis（这可能需要几分钟）...")
    
    try:
        subprocess.run(
            ["make"],
            cwd=redis_src,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        print_error(f"编译失败: {e}")
        return False
    
    # 复制可执行文件
    redis_dir = dest_dir / "redis-linux"
    redis_dir.mkdir(exist_ok=True)
    
    shutil.copy(redis_src / "src" / "redis-server", redis_dir)
    shutil.copy(redis_src / "src" / "redis-cli", redis_dir)
    
    # 清理
    shutil.rmtree(redis_src)
    tar_file.unlink()
    
    print_success(f"Linux版Redis已准备: {redis_dir}")
    return True

def download_redis_macos(dest_dir: Path):
    """下载macOS版Redis"""
    print_info("准备macOS版Redis...")
    
    # macOS通常使用Homebrew安装，这里提供预编译版本
    # 或者从源码编译（类似Linux）
    
    print_info("macOS建议使用Homebrew安装Redis:")
    print_info("  brew install redis")
    print_warning("这里创建Homebrew安装脚本...")
    
    redis_dir = dest_dir / "redis-macos"
    redis_dir.mkdir(exist_ok=True)
    
    # 创建安装脚本
    install_script = '''#!/bin/bash
# macOS Redis安装脚本

if command -v brew >/dev/null 2>&1; then
    echo "📥 使用Homebrew安装Redis..."
    brew install redis
    
    # 复制到应用目录
    REDIS_PATH=$(brew --prefix redis)
    cp "$REDIS_PATH/bin/redis-server" ./redis-server
    cp "$REDIS_PATH/bin/redis-cli" ./redis-cli
    
    echo "✅ Redis安装完成"
else
    echo "❌ 未安装Homebrew"
    echo "请访问 https://brew.sh 安装Homebrew"
    exit 1
fi
'''
    
    script_path = redis_dir / "install_redis.sh"
    script_path.write_text(install_script)
    script_path.chmod(0o755)
    
    print_success(f"macOS Redis安装脚本已创建: {script_path}")
    return True

def create_redis_config(dest_dir: Path):
    """创建Redis配置文件"""
    print_info("创建Redis配置文件...")
    
    config_content = '''# Redis配置文件（KOOK消息转发系统）

# 绑定地址
bind 127.0.0.1

# 端口
port 6379

# 工作目录
dir ./

# 日志文件
logfile "redis.log"

# 日志级别
loglevel notice

# 数据库数量
databases 16

# 持久化
save 900 1
save 300 10
save 60 10000

# RDB文件名
dbfilename dump.rdb

# AOF持久化
appendonly yes
appendfilename "appendonly.aof"

# 最大内存（512MB）
maxmemory 512mb
maxmemory-policy allkeys-lru

# 禁用保护模式（仅本地访问）
protected-mode no

# 超时时间
timeout 0

# TCP keepalive
tcp-keepalive 300

# 密码（可选，留空表示无密码）
# requirepass your_password_here
'''
    
    for platform in ['windows', 'linux', 'macos']:
        redis_dir = dest_dir / f"redis-{platform}"
        if redis_dir.exists():
            config_file = redis_dir / "redis.conf"
            config_file.write_text(config_content)
            print_success(f"配置文件已创建: {config_file}")

def create_redis_manager_scripts(dest_dir: Path):
    """创建Redis管理脚本"""
    print_info("创建Redis管理脚本...")
    
    # Windows启动脚本
    windows_start = '''@echo off
REM Redis启动脚本（Windows）

echo 启动Redis服务器...
start /B redis-server.exe redis.conf

echo Redis已启动（端口6379）
echo 日志文件: redis.log
'''
    
    # Linux/macOS启动脚本
    unix_start = '''#!/bin/bash
# Redis启动脚本（Linux/macOS）

echo "启动Redis服务器..."
./redis-server redis.conf &

echo "Redis已启动（端口6379）"
echo "日志文件: redis.log"
'''
    
    # Windows停止脚本
    windows_stop = '''@echo off
REM Redis停止脚本（Windows）

echo 停止Redis服务器...
redis-cli.exe shutdown

echo Redis已停止
'''
    
    # Linux/macOS停止脚本
    unix_stop = '''#!/bin/bash
# Redis停止脚本（Linux/macOS）

echo "停止Redis服务器..."
./redis-cli shutdown

echo "Redis已停止"
'''
    
    # 创建脚本文件
    platforms = {
        'windows': (windows_start, windows_stop, '.bat'),
        'linux': (unix_start, unix_stop, '.sh'),
        'macos': (unix_start, unix_stop, '.sh'),
    }
    
    for platform, (start_script, stop_script, ext) in platforms.items():
        redis_dir = dest_dir / f"redis-{platform}"
        if redis_dir.exists():
            start_file = redis_dir / f"start_redis{ext}"
            stop_file = redis_dir / f"stop_redis{ext}"
            
            start_file.write_text(start_script)
            stop_file.write_text(stop_script)
            
            if platform != 'windows':
                start_file.chmod(0o755)
                stop_file.chmod(0o755)
            
            print_success(f"{platform}管理脚本已创建")

def verify_redis(redis_dir: Path):
    """验证Redis是否可用"""
    print_info(f"验证Redis: {redis_dir}")
    
    system, _ = detect_platform()
    
    if system == 'windows':
        redis_server = redis_dir / "redis-server.exe"
    else:
        redis_server = redis_dir / "redis-server"
    
    if not redis_server.exists():
        print_error(f"Redis服务器不存在: {redis_server}")
        return False
    
    # 尝试获取版本
    try:
        result = subprocess.run(
            [str(redis_server), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Redis版本: {version}")
            return True
    except Exception as e:
        print_warning(f"无法获取版本: {e}")
    
    return True  # 文件存在即视为可用

def main():
    """主函数"""
    print("=" * 60)
    print("📦 Redis嵌入式准备工具（增强版）")
    print("=" * 60)
    print()
    
    # 检测平台
    system, arch = detect_platform()
    print_info(f"检测到系统: {system} ({arch})")
    
    # 创建目标目录
    dest_dir = Path("redis-packages")
    dest_dir.mkdir(exist_ok=True)
    
    # 询问要准备哪些平台
    print()
    print("选择要准备的平台:")
    print("  1) 当前平台 ({})".format(system))
    print("  2) 所有平台（Windows + Linux + macOS）")
    print("  3) 自定义选择")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    platforms_to_prepare = []
    
    if choice == '1':
        platforms_to_prepare = [system]
    elif choice == '2':
        platforms_to_prepare = ['windows', 'linux', 'macos']
    elif choice == '3':
        if input("准备Windows版？(y/N): ").lower() == 'y':
            platforms_to_prepare.append('windows')
        if input("准备Linux版？(y/N): ").lower() == 'y':
            platforms_to_prepare.append('linux')
        if input("准备macOS版？(y/N): ").lower() == 'y':
            platforms_to_prepare.append('macos')
    else:
        print_error("无效选择")
        return 1
    
    if not platforms_to_prepare:
        print_warning("未选择任何平台")
        return 0
    
    # 下载Redis
    print()
    success_count = 0
    
    for plat in platforms_to_prepare:
        print(f"\n{'='*60}")
        print(f"准备 {plat.upper()} 版Redis")
        print('='*60)
        
        if plat == 'windows':
            if download_redis_windows(dest_dir):
                success_count += 1
        elif plat == 'linux':
            if download_redis_linux(dest_dir):
                success_count += 1
        elif plat == 'macos':
            if download_redis_macos(dest_dir):
                success_count += 1
    
    # 创建配置文件和脚本
    if success_count > 0:
        create_redis_config(dest_dir)
        create_redis_manager_scripts(dest_dir)
    
    # 验证
    print()
    print("="*60)
    print("验证Redis安装")
    print("="*60)
    
    for plat in platforms_to_prepare:
        redis_dir = dest_dir / f"redis-{plat}"
        if redis_dir.exists():
            verify_redis(redis_dir)
    
    # 复制到项目redis目录
    project_redis = Path("redis")
    if success_count > 0:
        print()
        response = input(f"是否复制到项目redis目录？(Y/n): ")
        if response.lower() != 'n':
            for plat in platforms_to_prepare:
                src = dest_dir / f"redis-{plat}"
                if src.exists():
                    dest = project_redis / plat
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    print_success(f"已复制到: {dest}")
    
    # 总结
    print()
    print("="*60)
    print_success(f"✅ Redis准备完成（成功: {success_count}/{len(platforms_to_prepare)}）")
    print("="*60)
    print()
    print_info("Redis文件位置:")
    print(f"  源文件: {dest_dir}")
    if success_count > 0:
        print(f"  项目目录: {project_redis}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
