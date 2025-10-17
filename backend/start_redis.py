#!/usr/bin/env python3
"""
Redis服务启动脚本
自动检测并启动Redis服务，支持Windows/Linux/macOS
"""
import os
import sys
import subprocess
import platform
import time
import socket
from pathlib import Path


def is_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except (socket.error, ConnectionRefusedError):
            return False


def find_redis_executable():
    """查找Redis可执行文件"""
    system = platform.system()
    
    # 项目内的Redis路径
    project_redis_dir = Path(__file__).parent.parent / 'redis'
    
    if system == 'Windows':
        redis_names = ['redis-server.exe', 'redis-server']
        # 搜索路径
        search_paths = [
            project_redis_dir,
            Path('C:/Program Files/Redis'),
            Path('C:/Redis'),
        ]
    else:  # Linux/macOS
        redis_names = ['redis-server']
        search_paths = [
            project_redis_dir,
            Path('/usr/local/bin'),
            Path('/usr/bin'),
            Path('/opt/redis/bin'),
        ]
    
    # 在搜索路径中查找
    for search_path in search_paths:
        if not search_path.exists():
            continue
        for redis_name in redis_names:
            redis_path = search_path / redis_name
            if redis_path.exists():
                return redis_path
    
    # 尝试从PATH中查找
    try:
        result = subprocess.run(
            ['which', 'redis-server'] if system != 'Windows' else ['where', 'redis-server'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().split('\n')[0])
    except Exception:
        pass
    
    return None


def start_redis_server(redis_path: Path, port: int = 6379, config_file: Path = None) -> subprocess.Popen:
    """启动Redis服务器"""
    system = platform.system()
    
    # 构建启动命令
    cmd = [str(redis_path)]
    
    # 如果提供了配置文件
    if config_file and config_file.exists():
        cmd.append(str(config_file))
    else:
        # 使用命令行参数配置
        cmd.extend([
            '--port', str(port),
            '--bind', '127.0.0.1',
            '--protected-mode', 'yes',
            '--daemonize', 'no',  # 前台运行，便于管理
            '--loglevel', 'notice',
        ])
    
    print(f"启动Redis服务器: {' '.join(cmd)}")
    
    # 启动进程
    if system == 'Windows':
        # Windows下需要特殊处理
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        )
    
    return process


def main():
    """主函数"""
    port = int(os.getenv('REDIS_PORT', '6379'))
    
    print("=" * 50)
    print("Redis服务启动脚本")
    print("=" * 50)
    
    # 1. 检查端口是否已被占用
    if is_port_in_use(port):
        print(f"✓ Redis服务已在端口 {port} 上运行")
        return 0
    
    print(f"端口 {port} 未被占用，准备启动Redis服务...")
    
    # 2. 查找Redis可执行文件
    redis_path = find_redis_executable()
    
    if not redis_path:
        print("=" * 50)
        print("❌ 错误：未找到Redis服务器")
        print("=" * 50)
        print("请选择以下方法之一安装Redis：")
        print("")
        print("Windows:")
        print("  1. 下载预编译版本: https://github.com/tporadowski/redis/releases")
        print("  2. 解压到项目的redis目录")
        print("  3. 或安装到 C:\\Redis")
        print("")
        print("Linux:")
        print("  sudo apt install redis-server  (Ubuntu/Debian)")
        print("  sudo yum install redis          (CentOS/RHEL)")
        print("")
        print("macOS:")
        print("  brew install redis")
        print("")
        return 1
    
    print(f"✓ 找到Redis服务器: {redis_path}")
    
    # 3. 查找配置文件
    config_file = Path(__file__).parent.parent / 'redis' / 'redis.conf'
    if not config_file.exists():
        config_file = None
        print("  使用默认配置（无配置文件）")
    else:
        print(f"  使用配置文件: {config_file}")
    
    # 4. 启动Redis
    try:
        process = start_redis_server(redis_path, port, config_file)
        
        # 等待服务启动
        print("等待Redis服务启动...", end='', flush=True)
        max_retries = 10
        for i in range(max_retries):
            time.sleep(0.5)
            print('.', end='', flush=True)
            if is_port_in_use(port):
                print()
                print(f"✓ Redis服务已成功启动在端口 {port}")
                print(f"  进程ID: {process.pid}")
                print("=" * 50)
                
                # 持续运行，监控进程
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n正在停止Redis服务...")
                    process.terminate()
                    process.wait(timeout=5)
                    print("✓ Redis服务已停止")
                
                return 0
        
        print()
        print("❌ Redis服务启动超时")
        
        # 打印错误输出
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                print(f"错误输出:\n{stderr.decode('utf-8', errors='ignore')}")
        
        process.terminate()
        return 1
        
    except Exception as e:
        print(f"\n❌ 启动Redis失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
