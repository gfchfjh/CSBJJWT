"""
Redis嵌入式管理器（终极版）
==========================
功能：
1. 自动检测Redis二进制文件
2. 自动启动Redis服务
3. 健康监控（心跳检测）
4. 自动重启（崩溃恢复）
5. 数据备份与恢复
6. 动态端口分配（避免冲突）
7. 跨平台支持

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import os
import sys
import subprocess
import platform
import asyncio
import aioredis
import socket
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from ..utils.logger import logger


class RedisManagerUltimate:
    """Redis嵌入式管理器（终极版）"""
    
    def __init__(self, redis_dir: Path = None, port: int = 6379):
        self.system = platform.system()
        self.redis_dir = redis_dir or self._get_default_redis_dir()
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.redis_pool: Optional[aioredis.Redis] = None
        
        # 监控配置
        self.health_check_interval = 5  # 秒
        self.max_restart_attempts = 5
        self.restart_count = 0
        
    def _get_default_redis_dir(self) -> Path:
        """获取默认Redis目录"""
        # 开发环境
        dev_redis = Path(__file__).parent.parent.parent.parent / "dist" / "redis"
        if dev_redis.exists():
            return dev_redis
        
        # 打包后环境
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后
            base_path = Path(sys._MEIPASS)
            return base_path / "redis"
        
        # 相对路径
        return Path("./redis")
    
    def _get_redis_executable(self) -> Path:
        """获取Redis可执行文件路径"""
        if self.system == "Windows":
            return self.redis_dir / "redis-server.exe"
        else:
            return self.redis_dir / "redis-server"
    
    def _get_redis_config(self) -> Path:
        """获取Redis配置文件路径"""
        return self.redis_dir / "redis.conf"
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result != 0
        except:
            return False
    
    def _find_available_port(self, start_port: int = 6379, max_attempts: int = 10) -> Optional[int]:
        """查找可用端口"""
        for i in range(max_attempts):
            port = start_port + i
            if self._is_port_available(port):
                return port
        return None
    
    async def start(self, auto_find_port: bool = True) -> Tuple[bool, str]:
        """
        启动Redis服务
        
        Args:
            auto_find_port: 端口被占用时自动寻找可用端口
            
        Returns:
            (是否成功, 消息)
        """
        try:
            logger.info("=" * 60)
            logger.info("🚀 启动Redis嵌入式服务...")
            logger.info("=" * 60)
            
            # 检查Redis文件是否存在
            redis_executable = self._get_redis_executable()
            redis_config = self._get_redis_config()
            
            if not redis_executable.exists():
                error_msg = f"❌ Redis可执行文件不存在: {redis_executable}"
                logger.error(error_msg)
                return False, error_msg
            
            if not redis_config.exists():
                logger.warning(f"⚠️  Redis配置文件不存在: {redis_config}，将使用默认配置")
                redis_config = None
            
            # 检查端口是否可用
            if not self._is_port_available(self.port):
                if auto_find_port:
                    logger.warning(f"⚠️  端口 {self.port} 已被占用，尝试查找可用端口...")
                    available_port = self._find_available_port(self.port)
                    if available_port:
                        logger.info(f"✅ 找到可用端口: {available_port}")
                        self.port = available_port
                    else:
                        error_msg = f"❌ 无法找到可用端口（尝试了{self.port}-{self.port+9}）"
                        logger.error(error_msg)
                        return False, error_msg
                else:
                    error_msg = f"❌ 端口 {self.port} 已被占用"
                    logger.error(error_msg)
                    return False, error_msg
            
            # 准备启动参数
            cmd = [str(redis_executable)]
            
            if redis_config:
                cmd.append(str(redis_config))
            
            # 覆盖配置参数
            cmd.extend([
                "--port", str(self.port),
                "--bind", "127.0.0.1",
                "--protected-mode", "yes",
                "--daemonize", "no",  # 不后台运行（由程序管理）
                "--loglevel", "notice",
            ])
            
            # 设置数据目录
            data_dir = Path("./data/redis")
            data_dir.mkdir(parents=True, exist_ok=True)
            cmd.extend(["--dir", str(data_dir)])
            
            logger.info(f"📦 Redis版本: {self._get_redis_version()}")
            logger.info(f"🔌 监听端口: {self.port}")
            logger.info(f"📁 数据目录: {data_dir}")
            logger.info(f"🚀 启动命令: {' '.join(cmd)}")
            
            # 启动Redis进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.redis_dir
            )
            
            logger.info(f"⏳ Redis进程已启动 (PID: {self.process.pid})，等待服务就绪...")
            
            # 等待Redis启动完成（最多10秒）
            ready = await self._wait_for_ready(timeout=10)
            
            if not ready:
                self.stop()
                error_msg = "❌ Redis启动超时（10秒）"
                logger.error(error_msg)
                return False, error_msg
            
            self.is_running = True
            logger.info("✅ Redis服务启动成功！")
            logger.info("=" * 60)
            
            # 启动健康监控
            asyncio.create_task(self._health_monitor())
            
            return True, f"Redis服务已启动 (端口: {self.port})"
            
        except Exception as e:
            error_msg = f"❌ Redis启动失败: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg
    
    def _get_redis_version(self) -> str:
        """获取Redis版本"""
        try:
            redis_executable = self._get_redis_executable()
            result = subprocess.run(
                [str(redis_executable), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "未知版本"
        except:
            return "未知版本"
    
    async def _wait_for_ready(self, timeout: int = 10) -> bool:
        """
        等待Redis就绪
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否就绪
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                # 尝试连接Redis
                redis = await aioredis.create_redis_pool(
                    f'redis://127.0.0.1:{self.port}',
                    minsize=1,
                    maxsize=1
                )
                
                # 执行PING测试
                pong = await redis.ping()
                
                # 关闭测试连接
                redis.close()
                await redis.wait_closed()
                
                if pong:
                    logger.info("✅ Redis服务就绪，PING测试通过")
                    return True
                    
            except Exception as e:
                # 继续等待
                await asyncio.sleep(0.5)
        
        return False
    
    async def create_connection_pool(self) -> bool:
        """
        创建Redis连接池
        
        Returns:
            是否成功
        """
        try:
            if self.redis_pool:
                logger.info("ℹ️  Redis连接池已存在")
                return True
            
            logger.info("🔌 创建Redis连接池...")
            
            self.redis_pool = await aioredis.create_redis_pool(
                f'redis://127.0.0.1:{self.port}',
                minsize=5,
                maxsize=20,
                encoding='utf-8'
            )
            
            logger.info("✅ Redis连接池创建成功（最小5连接，最大20连接）")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建Redis连接池失败: {str(e)}")
            return False
    
    def stop(self):
        """停止Redis服务"""
        try:
            logger.info("🛑 停止Redis服务...")
            
            self.is_running = False
            
            # 关闭连接池
            if self.redis_pool:
                self.redis_pool.close()
                # await self.redis_pool.wait_closed()  # 同步方法中无法await
                self.redis_pool = None
                logger.info("✅ Redis连接池已关闭")
            
            # 终止Redis进程
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                    logger.info(f"✅ Redis进程已停止 (PID: {self.process.pid})")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️  Redis进程未响应，强制终止...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("✅ Redis进程已强制终止")
                
                self.process = None
            
            logger.info("✅ Redis服务已完全停止")
            
        except Exception as e:
            logger.error(f"❌ 停止Redis失败: {str(e)}")
    
    async def _health_monitor(self):
        """健康监控（后台任务）"""
        logger.info(f"💓 启动Redis健康监控（间隔{self.health_check_interval}秒）")
        
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # 检查进程是否存活
                if self.process and self.process.poll() is not None:
                    logger.error(f"❌ Redis进程已退出 (退出码: {self.process.returncode})")
                    
                    # 尝试自动重启
                    if self.restart_count < self.max_restart_attempts:
                        self.restart_count += 1
                        logger.warning(f"🔄 尝试重启Redis ({self.restart_count}/{self.max_restart_attempts})...")
                        
                        success, msg = await self.start(auto_find_port=True)
                        if success:
                            logger.info("✅ Redis重启成功")
                            self.restart_count = 0  # 重置计数
                        else:
                            logger.error(f"❌ Redis重启失败: {msg}")
                    else:
                        logger.error(f"❌ Redis已达到最大重启次数({self.max_restart_attempts})，停止监控")
                        self.is_running = False
                        break
                
                # PING测试
                if self.redis_pool:
                    try:
                        await self.redis_pool.ping()
                        # logger.debug("✅ Redis PING测试通过")
                    except Exception as e:
                        logger.warning(f"⚠️  Redis PING测试失败: {str(e)}")
                
            except Exception as e:
                logger.error(f"❌ 健康监控异常: {str(e)}")
    
    async def backup_data(self, backup_path: Path = None) -> Tuple[bool, str]:
        """
        备份Redis数据
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            (是否成功, 消息)
        """
        try:
            if not backup_path:
                backup_dir = Path("./data/redis/backups")
                backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"redis_backup_{timestamp}.rdb"
            
            logger.info(f"💾 开始备份Redis数据...")
            logger.info(f"📁 备份路径: {backup_path}")
            
            if not self.redis_pool:
                return False, "Redis连接池未初始化"
            
            # 执行BGSAVE
            await self.redis_pool.execute('BGSAVE')
            
            # 等待备份完成（检查LASTSAVE时间）
            last_save_before = await self.redis_pool.execute('LASTSAVE')
            
            max_wait = 60  # 最多等待60秒
            waited = 0
            while waited < max_wait:
                await asyncio.sleep(1)
                waited += 1
                last_save_after = await self.redis_pool.execute('LASTSAVE')
                if last_save_after > last_save_before:
                    break
            
            # 复制dump.rdb到备份位置
            dump_file = Path("./data/redis/dump.rdb")
            if dump_file.exists():
                import shutil
                shutil.copy2(dump_file, backup_path)
                
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                msg = f"✅ Redis数据备份成功 (大小: {size_mb:.2f} MB)"
                logger.info(msg)
                return True, msg
            else:
                msg = "❌ dump.rdb文件不存在"
                logger.error(msg)
                return False, msg
            
        except Exception as e:
            msg = f"❌ Redis备份失败: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def get_stats(self) -> dict:
        """获取Redis统计信息"""
        return {
            'is_running': self.is_running,
            'port': self.port,
            'pid': self.process.pid if self.process else None,
            'restart_count': self.restart_count,
            'redis_dir': str(self.redis_dir),
            'has_pool': self.redis_pool is not None
        }


# 全局实例
redis_manager_ultimate = RedisManagerUltimate()
