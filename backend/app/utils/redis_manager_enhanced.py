"""
✅ P0-3深度优化: Redis嵌入式管理器（增强版）
自动检测、下载、启动和管理Redis服务

新功能：
- 自动检测系统Redis
- 自动下载内置Redis（如未安装）
- 实时下载进度
- 跨平台支持
- 完整错误处理
"""
import os
import sys
import subprocess
import platform
import time
import socket
import asyncio
from pathlib import Path
from typing import Optional, Tuple, Callable, Dict, Any
from .logger import logger
from .redis_auto_installer import ensure_redis_installed  # ✅ P0-3新增


class RedisManager:
    """
    Redis嵌入式管理器
    
    功能：
    - 自动检测Redis是否已运行
    - 自动查找Redis可执行文件
    - 启动和停止Redis服务
    - 健康检查
    """
    
    def __init__(self, port: int = 6379, host: str = '127.0.0.1'):
        self.port = port
        self.host = host
        self.process: Optional[subprocess.Popen] = None
        self.redis_path: Optional[Path] = None
        self.config_file: Optional[Path] = None
        self.is_managed = False  # 是否由本管理器启动
        
        # ✅ P0-3新增：下载进度回调
        self.download_progress_callback: Optional[Callable] = None
        
        # Redis安装目录
        self.redis_install_dir = Path(__file__).parent.parent.parent.parent / 'redis'
        
    def is_port_in_use(self) -> bool:
        """
        检查Redis端口是否被占用
        
        Returns:
            是否被占用
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.port))
                return True
            except (socket.error, ConnectionRefusedError):
                return False
    
    def find_redis_executable(self) -> Optional[Path]:
        """
        查找Redis可执行文件
        
        搜索顺序：
        1. 项目redis目录
        2. 系统标准路径
        3. PATH环境变量
        
        Returns:
            Redis可执行文件路径，未找到返回None
        """
        system = platform.system()
        
        # 项目内的Redis路径
        project_root = Path(__file__).parent.parent.parent.parent
        project_redis_dir = project_root / 'redis'
        
        if system == 'Windows':
            redis_names = ['redis-server.exe', 'redis-server']
            search_paths = [
                project_redis_dir,
                Path('C:/Program Files/Redis'),
                Path('C:/Redis'),
                Path(os.path.expandvars('%LOCALAPPDATA%/Redis')),
            ]
        else:  # Linux/macOS
            redis_names = ['redis-server']
            search_paths = [
                project_redis_dir,
                Path('/usr/local/bin'),
                Path('/usr/bin'),
                Path('/opt/redis/bin'),
                Path(os.path.expanduser('~/redis/bin')),
            ]
        
        # 在搜索路径中查找
        for search_path in search_paths:
            if not search_path.exists():
                continue
            for redis_name in redis_names:
                redis_path = search_path / redis_name
                if redis_path.exists() and os.access(redis_path, os.X_OK):
                    logger.info(f"✅ 找到Redis可执行文件: {redis_path}")
                    return redis_path
        
        # 尝试从PATH中查找
        try:
            if system == 'Windows':
                result = subprocess.run(
                    ['where', 'redis-server'],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ['which', 'redis-server'],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5
                )
            
            if result.returncode == 0 and result.stdout.strip():
                path = Path(result.stdout.strip().split('\n')[0])
                if path.exists():
                    logger.info(f"✅ 从PATH找到Redis: {path}")
                    return path
        except Exception as e:
            logger.debug(f"从PATH查找Redis失败: {e}")
        
        logger.warning("⚠️ 未找到Redis可执行文件")
        return None
    
    def find_config_file(self) -> Optional[Path]:
        """
        查找Redis配置文件
        
        Returns:
            配置文件路径，未找到返回None
        """
        project_root = Path(__file__).parent.parent.parent.parent
        config_paths = [
            project_root / 'redis' / 'redis.conf',
            Path('/etc/redis/redis.conf'),
            Path('/usr/local/etc/redis.conf'),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                logger.info(f"✅ 找到Redis配置文件: {config_path}")
                return config_path
        
        logger.info("ℹ️ 未找到Redis配置文件，将使用默认配置")
        return None
    
    async def start(self, force_start: bool = False, auto_install: bool = True) -> Tuple[bool, str]:
        """
        启动Redis服务（✅ P0-3增强：支持自动下载）
        
        Args:
            force_start: 是否强制启动（即使端口已被占用）
            auto_install: 是否自动下载安装Redis（默认True）
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 检查是否已运行
            if self.is_port_in_use():
                if not force_start:
                    logger.info(f"✅ Redis已在端口 {self.port} 上运行")
                    return True, f"Redis已在端口 {self.port} 上运行"
                else:
                    logger.warning(f"⚠️ 端口 {self.port} 已被占用，但force_start=True")
            
            # 查找Redis可执行文件
            self.redis_path = self.find_redis_executable()
            
            # ✅ P0-3新增：如果未找到且允许自动安装，则下载
            if not self.redis_path and auto_install:
                logger.info("📥 未找到Redis，开始自动下载安装...")
                
                success, msg = await ensure_redis_installed(
                    self.redis_install_dir,
                    progress_callback=self.download_progress_callback
                )
                
                if not success:
                    error_msg = f"Redis自动安装失败: {msg}\n\n{self._get_install_instructions()}"
                    logger.error(error_msg)
                    return False, error_msg
                
                logger.info("✅ Redis自动安装成功")
                
                # 重新查找Redis
                self.redis_path = self.find_redis_executable()
            
            if not self.redis_path:
                error_msg = self._get_install_instructions()
                logger.error(f"❌ 未找到Redis服务器\n{error_msg}")
                return False, error_msg
            
            # 查找配置文件
            self.config_file = self.find_config_file()
            
            # 构建启动命令
            cmd = [str(self.redis_path)]
            
            if self.config_file:
                cmd.append(str(self.config_file))
            else:
                # 使用命令行参数配置
                cmd.extend([
                    '--port', str(self.port),
                    '--bind', self.host,
                    '--protected-mode', 'yes',
                    '--daemonize', 'no',
                    '--loglevel', 'notice',
                    '--save', '900 1',
                    '--save', '300 10',
                    '--save', '60 10000',
                ])
            
            logger.info(f"🚀 启动Redis服务器: {' '.join(cmd)}")
            
            # 启动进程
            system = platform.system()
            if system == 'Windows':
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp
                )
            
            self.is_managed = True
            
            # 等待服务启动
            logger.info("⏳ 等待Redis服务启动...")
            max_retries = 20
            for i in range(max_retries):
                await asyncio.sleep(0.5)
                if self.is_port_in_use():
                    logger.info(f"✅ Redis服务已成功启动在端口 {self.port}，进程ID: {self.process.pid}")
                    return True, f"Redis服务已启动（PID: {self.process.pid}）"
            
            # 启动超时
            logger.error("❌ Redis服务启动超时")
            
            # 尝试获取错误输出
            if self.process.poll() is not None:
                try:
                    stdout, stderr = self.process.communicate(timeout=1)
                    error_output = stderr.decode('utf-8', errors='ignore')
                    if error_output:
                        logger.error(f"Redis错误输出:\n{error_output}")
                        return False, f"Redis启动失败: {error_output[:200]}"
                except:
                    pass
            
            self.process.terminate()
            self.process = None
            self.is_managed = False
            return False, "Redis服务启动超时"
            
        except Exception as e:
            logger.error(f"❌ 启动Redis失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, f"启动Redis失败: {str(e)}"
    
    async def stop(self, timeout: int = 10) -> Tuple[bool, str]:
        """
        停止Redis服务
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            (是否成功, 消息)
        """
        if not self.is_managed or not self.process:
            logger.info("ℹ️ Redis服务不是由本管理器启动的，跳过停止")
            return True, "Redis服务不是由本管理器启动"
        
        try:
            logger.info("⏳ 正在停止Redis服务...")
            
            # 尝试优雅关闭
            self.process.terminate()
            
            # 等待进程结束
            for i in range(timeout * 2):
                if self.process.poll() is not None:
                    logger.info("✅ Redis服务已停止")
                    self.process = None
                    self.is_managed = False
                    return True, "Redis服务已停止"
                await asyncio.sleep(0.5)
            
            # 强制kill
            logger.warning("⚠️ 优雅关闭超时，强制终止...")
            self.process.kill()
            await asyncio.sleep(1)
            
            if self.process.poll() is not None:
                logger.info("✅ Redis服务已强制停止")
                self.process = None
                self.is_managed = False
                return True, "Redis服务已强制停止"
            else:
                logger.error("❌ 无法停止Redis服务")
                return False, "无法停止Redis服务"
                
        except Exception as e:
            logger.error(f"❌ 停止Redis失败: {str(e)}")
            return False, f"停止Redis失败: {str(e)}"
    
    async def restart(self) -> Tuple[bool, str]:
        """
        重启Redis服务
        
        Returns:
            (是否成功, 消息)
        """
        logger.info("🔄 重启Redis服务...")
        
        # 停止
        if self.is_managed:
            success, msg = await self.stop()
            if not success:
                return False, f"停止失败: {msg}"
        
        # 启动
        await asyncio.sleep(1)
        return await self.start()
    
    async def health_check(self) -> Tuple[bool, str]:
        """
        健康检查
        
        Returns:
            (是否健康, 消息)
        """
        # 检查端口
        if not self.is_port_in_use():
            return False, f"Redis端口 {self.port} 未响应"
        
        # 检查进程（如果是由本管理器启动）
        if self.is_managed and self.process:
            if self.process.poll() is not None:
                return False, f"Redis进程已退出（退出码: {self.process.poll()}）"
        
        # 尝试连接Redis
        try:
            import redis
            r = redis.Redis(host=self.host, port=self.port, socket_timeout=2)
            r.ping()
            return True, "Redis健康"
        except Exception as e:
            return False, f"Redis连接失败: {str(e)}"
    
    def get_status(self) -> dict:
        """
        获取Redis状态
        
        Returns:
            状态字典
        """
        is_running = self.is_port_in_use()
        
        status = {
            'running': is_running,
            'port': self.port,
            'host': self.host,
            'managed': self.is_managed,
            'pid': self.process.pid if self.process else None,
            'redis_path': str(self.redis_path) if self.redis_path else None,
            'config_file': str(self.config_file) if self.config_file else None,
        }
        
        # 如果运行中，尝试获取更多信息
        if is_running:
            try:
                import redis
                r = redis.Redis(host=self.host, port=self.port, socket_timeout=2)
                info = r.info()
                status.update({
                    'version': info.get('redis_version'),
                    'uptime_seconds': info.get('uptime_in_seconds'),
                    'connected_clients': info.get('connected_clients'),
                    'used_memory_human': info.get('used_memory_human'),
                })
            except:
                pass
        
        return status
    
    def set_download_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        ✅ P0-3新增：设置下载进度回调
        
        Args:
            callback: 回调函数，接收进度信息字典
        """
        self.download_progress_callback = callback
    
    def _get_install_instructions(self) -> str:
        """
        获取Redis安装说明
        
        Returns:
            安装说明文本
        """
        system = platform.system()
        
        instructions = [
            "✨ 推荐方式：系统会自动下载安装Redis（无需手动操作）",
            "",
            "如果自动下载失败，您也可以手动安装：",
            ""
        ]
        
        if system == 'Windows':
            instructions.extend([
                "Windows:",
                "  1. 下载: https://github.com/tporadowski/redis/releases",
                "  2. 解压到项目的redis目录或C:\\Redis",
                "  3. 重新启动应用",
            ])
        elif system == 'Darwin':  # macOS
            instructions.extend([
                "macOS:",
                "  brew install redis",
                "  或下载: https://download.redis.io/redis-stable.tar.gz",
            ])
        else:  # Linux
            instructions.extend([
                "Linux:",
                "  Ubuntu/Debian: sudo apt install redis-server",
                "  CentOS/RHEL: sudo yum install redis",
                "  或下载: https://download.redis.io/redis-stable.tar.gz",
            ])
        
        return "\n".join(instructions)
    
    def __del__(self):
        """析构函数，确保进程被清理"""
        if self.is_managed and self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass


# 全局单例
redis_manager = RedisManager()
