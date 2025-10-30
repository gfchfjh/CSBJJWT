"""
Redis嵌入式管理器
自动启动和管理本地Redis服务
"""
import os
import sys
import subprocess
import time
import platform
import socket
from pathlib import Path
from typing import Optional
from ..config import settings, REDIS_DIR
from .logger import logger


class RedisManager:
    """Redis服务管理器"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.redis_executable = self._find_redis_executable()
        self.redis_conf = Path(__file__).parent.parent.parent.parent / "redis" / "redis.conf"
        self.pid_file = REDIS_DIR / "redis.pid"
        self.log_file = REDIS_DIR / "redis.log"
        
        # 确保Redis数据目录存在
        REDIS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _find_redis_executable(self) -> Optional[Path]:
        """
        查找Redis可执行文件
        优先级：
        1. 项目内置Redis (redis/redis-server 或 redis/redis-server.exe)
        2. 系统已安装的Redis
        3. Docker Redis容器
        """
        system = platform.system()
        
        # 1. 查找项目内置Redis
        project_root = Path(__file__).parent.parent.parent.parent
        if system == "Windows":
            redis_path = project_root / "redis" / "redis-server.exe"
        else:
            redis_path = project_root / "redis" / "redis-server"
        
        if redis_path.exists():
            logger.info(f"✅ 找到内置Redis: {redis_path}")
            return redis_path
        
        # 2. 查找系统Redis
        try:
            if system == "Windows":
                # Windows系统检查
                result = subprocess.run(
                    ["where", "redis-server"],
                    capture_output=True,
                    text=True
                )
            else:
                # Unix系统检查
                result = subprocess.run(
                    ["which", "redis-server"],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0 and result.stdout.strip():
                redis_path = Path(result.stdout.strip().split('\n')[0])
                logger.info(f"✅ 找到系统Redis: {redis_path}")
                return redis_path
        except Exception as e:
            logger.debug(f"系统Redis查找失败: {str(e)}")
        
        logger.warning("⚠️ 未找到Redis可执行文件")
        return None
    
    def is_redis_running(self, host: str = "127.0.0.1", port: int = 6379) -> bool:
        """检查Redis是否正在运行"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def start(self, host: str = "127.0.0.1", port: int = 6379) -> bool:
        """
        启动Redis服务
        
        Returns:
            是否启动成功
        """
        try:
            # 检查是否已经运行
            if self.is_redis_running(host, port):
                logger.info(f"✅ Redis已在运行: {host}:{port}")
                return True
            
            # 检查是否有Redis可执行文件
            if not self.redis_executable:
                logger.error("❌ Redis启动失败: 未找到Redis可执行文件")
                logger.info("💡 解决方案:")
                logger.info("   1. 使用Docker运行: docker-compose up -d redis")
                logger.info("   2. 手动安装Redis:")
                logger.info("      - Windows: https://github.com/tporadowski/redis/releases")
                logger.info("      - macOS: brew install redis")
                logger.info("      - Linux: sudo apt install redis-server")
                return False
            
            logger.info(f"🚀 启动内置Redis服务: {host}:{port}")
            
            # 准备启动参数
            cmd = [
                str(self.redis_executable),
                "--port", str(port),
                "--bind", host,
                "--dir", str(REDIS_DIR),
                "--pidfile", str(self.pid_file),
                "--logfile", str(self.log_file),
                "--save", "60", "1",  # 60秒内有1个key变化就保存
                "--appendonly", "yes",  # 启用AOF持久化
                "--appendfilename", "appendonly.aof",
                "--daemonize", "no" if platform.system() == "Windows" else "yes"
            ]
            
            # 如果有配置文件，使用配置文件
            if self.redis_conf.exists():
                cmd = [str(self.redis_executable), str(self.redis_conf)]
                logger.info(f"使用配置文件: {self.redis_conf}")
            
            # 启动Redis
            if platform.system() == "Windows":
                # Windows需要保持进程运行
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Unix系统使用daemonize
                subprocess.run(cmd, check=True)
            
            # 等待Redis启动
            for i in range(10):
                time.sleep(0.5)
                if self.is_redis_running(host, port):
                    logger.info(f"✅ Redis启动成功: {host}:{port}")
                    return True
            
            logger.error("❌ Redis启动超时")
            return False
            
        except Exception as e:
            logger.error(f"❌ Redis启动失败: {str(e)}")
            logger.info("💡 建议使用Docker模式: docker-compose up -d")
            return False
    
    def stop(self) -> bool:
        """停止Redis服务"""
        try:
            if self.process:
                logger.info("停止Redis进程...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.process = None
                logger.info("✅ Redis已停止")
                return True
            
            # 尝试通过PID文件停止
            if self.pid_file.exists():
                try:
                    with open(self.pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    if platform.system() == "Windows":
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)])
                    else:
                        os.kill(pid, 15)  # SIGTERM
                    
                    logger.info("✅ Redis已停止")
                    return True
                except Exception as e:
                    logger.warning(f"通过PID停止Redis失败: {str(e)}")
            
            logger.warning("Redis进程未运行")
            return True
            
        except Exception as e:
            logger.error(f"停止Redis失败: {str(e)}")
            return False
    
    def restart(self) -> bool:
        """重启Redis服务"""
        logger.info("重启Redis服务...")
        self.stop()
        time.sleep(1)
        return self.start()
    
    def get_status(self) -> dict:
        """获取Redis状态信息"""
        return {
            "running": self.is_redis_running(
                settings.redis_host, 
                settings.redis_port
            ),
            "host": settings.redis_host,
            "port": settings.redis_port,
            "executable": str(self.redis_executable) if self.redis_executable else None,
            "pid_file": str(self.pid_file),
            "log_file": str(self.log_file),
            "data_dir": str(REDIS_DIR)
        }


# 创建全局Redis管理器实例
redis_manager = RedisManager()
