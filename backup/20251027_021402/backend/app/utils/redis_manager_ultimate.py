"""
Redis管理器 - 终极版本
功能：完全嵌入式，自动下载、安装、启动、健康检查
用户完全无感知
"""

import os
import sys
import platform
import subprocess
import asyncio
import time
import shutil
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional, Tuple
from ..utils.logger import logger
from ..config import settings


class RedisManagerUltimate:
    """Redis管理器 - 终极版本（用户无感知）"""
    
    def __init__(self):
        self.redis_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.host = settings.redis_host
        self.port = settings.redis_port
        
        # Redis可执行文件路径
        self.redis_dir = Path(settings.data_dir) / "redis"
        self.redis_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据平台确定Redis可执行文件名
        if platform.system() == "Windows":
            self.redis_executable = self.redis_dir / "redis-server.exe"
            self.download_url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
        else:
            self.redis_executable = self.redis_dir / "redis-server"
            # Linux/macOS使用不同的下载源
            if platform.system() == "Darwin":
                self.download_url = "https://download.redis.io/redis-stable.tar.gz"
            else:
                self.download_url = "https://download.redis.io/redis-stable.tar.gz"
        
        # Redis配置文件
        self.redis_conf = self.redis_dir / "redis.conf"
        
        # Redis日志文件
        self.redis_log = self.redis_dir / "redis.log"
        
        # Redis PID文件
        self.redis_pid = self.redis_dir / "redis.pid"
        
        logger.info(f"Redis管理器初始化: {self.host}:{self.port}")
    
    def _check_redis_installed(self) -> bool:
        """检查Redis是否已安装"""
        return self.redis_executable.exists()
    
    async def _download_redis(self) -> bool:
        """自动下载Redis"""
        logger.info("📥 Redis未安装，开始自动下载...")
        logger.info(f"   下载地址: {self.download_url}")
        
        try:
            # 显示下载进度
            def show_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded / total_size * 100, 100)
                logger.info(f"   下载进度: {percent:.1f}% ({downloaded / 1024 / 1024:.1f}MB / {total_size / 1024 / 1024:.1f}MB)")
            
            # 下载文件
            download_file = self.redis_dir / "redis_download.zip"
            
            logger.info("   正在下载Redis...")
            await asyncio.to_thread(
                urllib.request.urlretrieve,
                self.download_url,
                download_file,
                show_progress
            )
            
            logger.info("✅ Redis下载完成，开始解压...")
            
            # 解压
            if platform.system() == "Windows":
                await self._extract_redis_windows(download_file)
            else:
                await self._extract_redis_unix(download_file)
            
            # 删除下载的压缩包
            download_file.unlink()
            
            logger.info("✅ Redis安装完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis下载失败: {str(e)}")
            logger.error("   请手动下载Redis并放置到: " + str(self.redis_dir))
            return False
    
    async def _extract_redis_windows(self, zip_file: Path):
        """解压Redis（Windows）"""
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(self.redis_dir)
        
        # 查找redis-server.exe
        for file in self.redis_dir.rglob("redis-server.exe"):
            # 移动到根目录
            shutil.move(str(file), str(self.redis_executable))
            break
    
    async def _extract_redis_unix(self, tar_file: Path):
        """解压并编译Redis（Linux/macOS）"""
        import tarfile
        
        # 解压
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(self.redis_dir)
        
        # 查找redis目录
        redis_source_dir = None
        for dir in self.redis_dir.iterdir():
            if dir.is_dir() and dir.name.startswith('redis'):
                redis_source_dir = dir
                break
        
        if redis_source_dir:
            logger.info("   正在编译Redis...")
            
            # 编译
            result = await asyncio.to_thread(
                subprocess.run,
                ["make"],
                cwd=redis_source_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 复制可执行文件
                src_exec = redis_source_dir / "src" / "redis-server"
                shutil.copy(str(src_exec), str(self.redis_executable))
                os.chmod(self.redis_executable, 0o755)
                logger.info("✅ Redis编译完成")
            else:
                logger.error(f"❌ Redis编译失败: {result.stderr}")
                raise Exception("Redis编译失败")
    
    def _create_redis_config(self):
        """创建Redis配置文件"""
        if not self.redis_conf.exists():
            logger.info("创建Redis配置文件...")
            
            config_content = f"""
# Redis配置文件（自动生成）
# KOOK消息转发系统专用

# 网络配置
bind {self.host}
port {self.port}
timeout 0
tcp-keepalive 300

# 通用配置
daemonize no
supervised no
pidfile {self.redis_pid}
loglevel notice
logfile {self.redis_log}

# 持久化配置
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir {self.redis_dir}

# 内存配置
maxmemory 256mb
maxmemory-policy allkeys-lru

# 安全配置
# requirepass your-password-here

# 限制
maxclients 10000

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# 事件通知
notify-keyspace-events ""
"""
            
            self.redis_conf.write_text(config_content)
            logger.info(f"✅ Redis配置文件已创建: {self.redis_conf}")
    
    async def start(self) -> Tuple[bool, str]:
        """
        启动Redis服务（智能模式）
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 检查是否已在运行
            if await self._check_redis_running():
                logger.info("✅ 检测到Redis已在运行")
                self.is_running = True
                return True, "Redis已在运行"
            
            # 2. 检查是否已安装
            if not self._check_redis_installed():
                logger.warning("⚠️ Redis未安装，将自动下载...")
                
                # 自动下载
                download_success = await self._download_redis()
                if not download_success:
                    return False, "Redis自动下载失败，请检查网络连接"
            
            # 3. 创建配置文件
            self._create_redis_config()
            
            # 4. 启动Redis
            logger.info("🚀 启动Redis服务...")
            
            self.redis_process = subprocess.Popen(
                [str(self.redis_executable), str(self.redis_conf)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.redis_dir
            )
            
            # 5. 等待启动并验证
            await asyncio.sleep(2)
            
            if await self._check_redis_running():
                self.is_running = True
                logger.info("✅ Redis启动成功")
                logger.info(f"   进程ID: {self.redis_process.pid}")
                logger.info(f"   监听地址: {self.host}:{self.port}")
                logger.info(f"   日志文件: {self.redis_log}")
                return True, f"Redis启动成功 (PID: {self.redis_process.pid})"
            else:
                logger.error("❌ Redis启动失败")
                return False, "Redis启动失败"
            
        except FileNotFoundError:
            logger.error(f"❌ Redis可执行文件不存在: {self.redis_executable}")
            return False, "Redis可执行文件不存在"
        except Exception as e:
            logger.error(f"❌ 启动Redis异常: {str(e)}")
            return False, f"启动失败: {str(e)}"
    
    async def _check_redis_running(self) -> bool:
        """检查Redis是否在运行"""
        try:
            import redis
            
            # 尝试连接
            client = redis.Redis(
                host=self.host,
                port=self.port,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Ping测试
            await asyncio.to_thread(client.ping)
            return True
            
        except Exception:
            return False
    
    def stop(self):
        """停止Redis服务"""
        try:
            if self.redis_process:
                logger.info("🛑 停止Redis服务...")
                
                self.redis_process.terminate()
                
                # 等待进程结束
                try:
                    self.redis_process.wait(timeout=5)
                    logger.info("✅ Redis已停止")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Redis未响应，强制终止...")
                    self.redis_process.kill()
                    self.redis_process.wait()
                    logger.info("✅ Redis已强制终止")
                
                self.redis_process = None
                self.is_running = False
            
            # 清理PID文件
            if self.redis_pid.exists():
                self.redis_pid.unlink()
            
        except Exception as e:
            logger.error(f"❌ 停止Redis失败: {str(e)}")
    
    async def health_check(self) -> dict:
        """健康检查"""
        try:
            import redis
            
            client = redis.Redis(
                host=self.host,
                port=self.port,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # 获取info
            info = await asyncio.to_thread(client.info)
            
            return {
                'status': 'healthy',
                'version': info.get('redis_version'),
                'uptime_seconds': info.get('uptime_in_seconds'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'total_commands_processed': info.get('total_commands_processed'),
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def auto_restart_on_failure(self):
        """自动重启（当检测到故障时）"""
        logger.warning("⚠️ 检测到Redis故障，尝试自动重启...")
        
        # 停止旧进程
        self.stop()
        
        # 等待2秒
        await asyncio.sleep(2)
        
        # 重新启动
        success, message = await self.start()
        
        if success:
            logger.info("✅ Redis自动重启成功")
        else:
            logger.error("❌ Redis自动重启失败")
        
        return success


# 全局实例
redis_manager_ultimate = RedisManagerUltimate()
