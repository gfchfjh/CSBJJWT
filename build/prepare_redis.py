#!/usr/bin/env python3
"""
Redis准备脚本 - 下载并准备Redis二进制文件用于打包

支持的平台：
- Windows: 下载Redis for Windows
- Linux: 下载官方Redis或使用系统包管理器
- macOS: 使用Homebrew或下载编译
"""

import os
import sys
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path

# Redis版本配置
REDIS_VERSION = "7.2.3"

# 下载URL
REDIS_URLS = {
    'windows': f'https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip',
    'linux': f'https://download.redis.io/releases/redis-{REDIS_VERSION}.tar.gz',
    'macos': f'https://download.redis.io/releases/redis-{REDIS_VERSION}.tar.gz',
}

def detect_platform():
    """检测当前平台"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        raise Exception(f"不支持的平台: {system}")

def download_file(url, output_path):
    """下载文件"""
    print(f"📥 正在下载: {url}")
    print(f"   目标路径: {output_path}")
    
    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        
        print()
        print(f"✅ 下载完成: {output_path.name}")
        return True
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        return False

def prepare_windows_redis(redis_dir):
    """准备Windows版Redis"""
    print("\n🪟 准备Windows版Redis...")
    print("-" * 60)
    
    # 下载目录
    download_dir = redis_dir / 'download'
    download_dir.mkdir(exist_ok=True)
    
    # 下载ZIP文件
    zip_path = download_dir / 'redis-windows.zip'
    if not zip_path.exists():
        if not download_file(REDIS_URLS['windows'], zip_path):
            return False
    else:
        print(f"✅ 已存在: {zip_path}")
    
    # 解压
    print("📦 正在解压...")
    extract_dir = download_dir / 'redis-extracted'
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # 复制必要的文件
    print("📋 复制文件...")
    for item in extract_dir.rglob('*'):
        if item.name in ['redis-server.exe', 'redis-cli.exe']:
            shutil.copy(item, redis_dir / item.name)
            print(f"   ✅ {item.name}")
    
    # 创建配置文件（如果不存在）
    config_path = redis_dir / 'redis.conf'
    if not config_path.exists():
        config_content = """# Redis配置文件（最小配置）
port 6379
bind 127.0.0.1
protected-mode yes
timeout 0
tcp-keepalive 300
daemonize no
supervised no
loglevel notice
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
"""
        config_path.write_text(config_content)
        print(f"   ✅ redis.conf")
    
    print("✅ Windows版Redis准备完成！")
    return True

def prepare_linux_redis(redis_dir):
    """准备Linux版Redis"""
    print("\n🐧 准备Linux版Redis...")
    print("-" * 60)
    
    # 方案1: 检查系统是否已安装Redis
    redis_server_path = shutil.which('redis-server')
    if redis_server_path:
        print(f"✅ 检测到系统Redis: {redis_server_path}")
        print("   将使用系统Redis...")
        
        # 复制到项目目录
        shutil.copy(redis_server_path, redis_dir / 'redis-server')
        os.chmod(redis_dir / 'redis-server', 0o755)
        print(f"   ✅ 已复制: redis-server")
        return True
    
    # 方案2: 下载并编译
    print("ℹ️  系统未安装Redis，尝试下载编译...")
    
    download_dir = redis_dir / 'download'
    download_dir.mkdir(exist_ok=True)
    
    # 下载源码
    tar_path = download_dir / f'redis-{REDIS_VERSION}.tar.gz'
    if not tar_path.exists():
        if not download_file(REDIS_URLS['linux'], tar_path):
            return False
    else:
        print(f"✅ 已存在: {tar_path}")
    
    # 解压
    print("📦 正在解压...")
    extract_dir = download_dir / f'redis-{REDIS_VERSION}'
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(download_dir)
    
    # 编译
    print("🔨 正在编译Redis...")
    print("   这可能需要几分钟，请耐心等待...")
    
    import subprocess
    try:
        # 编译
        result = subprocess.run(
            ['make'], 
            cwd=extract_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 编译失败:")
            print(result.stderr)
            return False
        
        # 复制编译好的文件
        src_dir = extract_dir / 'src'
        shutil.copy(src_dir / 'redis-server', redis_dir / 'redis-server')
        shutil.copy(src_dir / 'redis-cli', redis_dir / 'redis-cli')
        
        # 设置执行权限
        os.chmod(redis_dir / 'redis-server', 0o755)
        os.chmod(redis_dir / 'redis-cli', 0o755)
        
        print("✅ Linux版Redis编译完成！")
        return True
        
    except Exception as e:
        print(f"❌ 编译失败: {e}")
        return False

def prepare_macos_redis(redis_dir):
    """准备macOS版Redis"""
    print("\n🍎 准备macOS版Redis...")
    print("-" * 60)
    
    # 方案1: 使用Homebrew安装的Redis
    redis_server_path = shutil.which('redis-server')
    if redis_server_path:
        print(f"✅ 检测到Homebrew Redis: {redis_server_path}")
        
        # 复制到项目目录
        shutil.copy(redis_server_path, redis_dir / 'redis-server')
        os.chmod(redis_dir / 'redis-server', 0o755)
        print(f"   ✅ 已复制: redis-server")
        return True
    
    # 方案2: 下载并编译（与Linux相同）
    print("ℹ️  未检测到Homebrew Redis，建议运行: brew install redis")
    print("   或使用编译方式...")
    
    return prepare_linux_redis(redis_dir)

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Redis准备脚本")
    print("=" * 60)
    print()
    
    # 检测平台
    try:
        platform_name = detect_platform()
        print(f"📍 检测到平台: {platform_name}")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Redis目录
    redis_dir = Path('redis')
    redis_dir.mkdir(exist_ok=True)
    print(f"📁 Redis目录: {redis_dir.absolute()}")
    
    # 根据平台准备Redis
    success = False
    if platform_name == 'windows':
        success = prepare_windows_redis(redis_dir)
    elif platform_name == 'linux':
        success = prepare_linux_redis(redis_dir)
    elif platform_name == 'macos':
        success = prepare_macos_redis(redis_dir)
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ Redis准备失败")
        print("=" * 60)
        print("\n💡 解决方案：")
        print("   1. 手动安装Redis到系统")
        print("   2. 将redis-server复制到redis/目录")
        print("   3. 或在构建时使用系统Redis")
        sys.exit(1)
    
    # 检查结果
    print("\n" + "=" * 60)
    print("✅ Redis准备完成！")
    print("=" * 60)
    print("\n📋 已准备的文件：")
    
    files_to_check = [
        'redis-server.exe' if platform_name == 'windows' else 'redis-server',
        'redis-cli.exe' if platform_name == 'windows' else 'redis-cli',
        'redis.conf',
    ]
    
    for filename in files_to_check:
        file_path = redis_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024 / 1024
            print(f"  ✅ {filename}: {size:.2f} MB")
        else:
            print(f"  ⚠️  {filename}: 未找到（可选）")
    
    print("\n💡 后续步骤：")
    print("   1. 运行构建脚本: ./build_installer.sh")
    print("   2. Redis将自动打包到安装包中")
    print()

if __name__ == '__main__':
    main()
