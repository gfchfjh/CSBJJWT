"""
Redis 管理器（最终版）
P1-11~13: Redis 稳定性优化

功能：
1. 跨平台路径检测
2. 动态端口分配
3. 数据自动备份
4. 健康监控
"""
import os
import sys
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple
import redis.asyncio as aioredis
from ..utils.logger import logger
from ..config import settings


class RedisManagerFinal:
    """Redis 管理器（最终版）"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.redis_host = settings.redis_host
        self.redis_port = settings.redis_port
        self.data_dir = Path(settings.data_dir) / "redis"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Redis 二进制文件路径（跨平台）
        self.redis_server_path = self._find_redis_server()
        self.redis_cli_path = self._find_redis_cli()
        
        # 配置文件路径
        self.config_path = self.data_dir / "redis.conf"
        
    def _find_redis_server(self) -> Optional[Path]:
        """查找 Redis Server 路径（跨平台）"""
        possible_paths = []
        
        if sys.platform == "win32":
            # Windows
            possible_paths = [
                Path("redis/redis-server.exe"),
                Path("dist/redis/redis-server.exe"),
                Path(__file__).parent.parent.parent.parent / "redis/redis-server.exe",
            ]
        else:
            # Linux/macOS
            possible_paths = [
                Path("redis/redis-server"),
                Path("dist/redis/redis-server"),
                Path(__file__).parent.parent.parent.parent / "redis/redis-server",
                Path("/usr/local/bin/redis-server"),
                Path("/usr/bin/redis-server"),
            ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ 找到 Redis Server: {path}")
                return path
        
        logger.warning("⚠️ 未找到 Redis Server")
        return None
    
    def _find_redis_cli(self) -> Optional[Path]:
        """查找 Redis CLI 路径"""
        if not self.redis_server_path:
            return None
        
        cli_name = "redis-cli.exe" if sys.platform == "win32" else "redis-cli"
        cli_path = self.redis_server_path.parent / cli_name
        
        if cli_path.exists():
            return cli_path
        return None
    
    def _find_available_port(self, start_port: int = 6379) -> int:
        """查找可用端口"""
        import socket
        
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    if result != 0:
                        # 端口未被占用
                        logger.info(f"✅ 找到可用端口: {port}")
                        return port
            except:
                continue
        
        logger.error("❌ 未找到可用端口（6379-6388）")
        return start_port
    
    def generate_config(self):
        """生成 Redis 配置文件"""
        config_content = f"""# Redis 配置文件（v3.1 自动生成）
# 数据目录: {self.data_dir}
# 端口: {self.redis_port}

# 基础配置
port {self.redis_port}
bind 127.0.0.1
protected-mode yes
timeout 0
tcp-keepalive 300

# 数据持久化（P1-12 优化）
dir {self.data_dir}
dbfilename dump.rdb
save 900 1
save 300 10
save 60 10000

# 日志
loglevel notice
logfile "{self.data_dir}/redis.log"

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru

# 安全：禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""

# 客户端
maxclients 100

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# RDB 压缩
rdbcompression yes
rdbchecksum yes

# 后台保存失败时停止写入
stop-writes-on-bgsave-error yes
"""
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        logger.info(f"✅ Redis 配置文件已生成: {self.config_path}")
    
    async def start(self) -> Tuple[bool, str]:
        """启动 Redis（跨平台优化版）"""
        try:
            logger.info("🚀 启动 Redis 服务...")
            
            # 1. 检查 Redis Server 是否存在
            if not self.redis_server_path:
                logger.error("❌ Redis Server 未找到")
                return False, "Redis Server 未找到，请运行 build/prepare_redis_complete.py"
            
            # 2. 检查端口是否可用
            original_port = self.redis_port
            self.redis_port = self._find_available_port(self.redis_port)
            
            if self.redis_port != original_port:
                logger.warning(f"⚠️ 端口 {original_port} 被占用，使用端口 {self.redis_port}")
            
            # 3. 生成配置文件
            self.generate_config()
            
            # 4. 启动 Redis
            cmd = [
                str(self.redis_server_path),
                str(self.config_path)
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.data_dir
            )
            
            # 5. 等待启动完成
            await asyncio.sleep(2)
            
            # 6. 验证连接
            if await self.check_connection():
                logger.info(f"✅ Redis 已启动: 127.0.0.1:{self.redis_port}")
                return True, f"Redis 已启动在端口 {self.redis_port}"
            else:
                logger.error("❌ Redis 启动失败：无法连接")
                return False, "Redis 启动失败：无法连接"
                
        except Exception as e:
            logger.error(f"❌ Redis 启动异常: {str(e)}")
            return False, f"Redis 启动异常: {str(e)}"
    
    async def check_connection(self) -> bool:
        """检查 Redis 连接"""
        try:
            redis_client = aioredis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/0",
                encoding="utf-8",
                decode_responses=True
            )
            
            await redis_client.ping()
            await redis_client.close()
            return True
            
        except Exception as e:
            logger.error(f"Redis 连接检查失败: {str(e)}")
            return False
    
    async def backup_data(self) -> Tuple[bool, str]:
        """备份 Redis 数据（P1-13）"""
        try:
            if not self.redis_cli_path:
                return False, "Redis CLI 未找到"
            
            logger.info("💾 开始备份 Redis 数据...")
            
            # 创建备份目录
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份文件名（带时间戳）
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"redis_backup_{timestamp}.rdb"
            
            # 执行 BGSAVE
            result = subprocess.run(
                [str(self.redis_cli_path), "-p", str(self.redis_port), "BGSAVE"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 等待保存完成
                await asyncio.sleep(2)
                
                # 复制 dump.rdb 到备份目录
                dump_file = self.data_dir / "dump.rdb"
                if dump_file.exists():
                    shutil.copy2(dump_file, backup_file)
                    
                    file_size = backup_file.stat().st_size / 1024
                    logger.info(f"✅ Redis 数据已备份: {backup_file} ({file_size:.2f} KB)")
                    
                    return True, f"备份成功: {backup_file.name}"
                else:
                    return False, "dump.rdb 文件不存在"
            else:
                return False, f"BGSAVE 命令失败: {result.stderr}"
                
        except Exception as e:
            logger.error(f"备份失败: {str(e)}")
            return False, f"备份失败: {str(e)}"
    
    async def restore_data(self, backup_file: Path) -> Tuple[bool, str]:
        """恢复 Redis 数据"""
        try:
            logger.info(f"📥 恢复 Redis 数据: {backup_file}")
            
            if not backup_file.exists():
                return False, "备份文件不存在"
            
            # 停止 Redis
            await self.stop()
            await asyncio.sleep(1)
            
            # 复制备份文件到数据目录
            dump_file = self.data_dir / "dump.rdb"
            shutil.copy2(backup_file, dump_file)
            
            # 重新启动 Redis
            success, msg = await self.start()
            
            if success:
                logger.info("✅ Redis 数据已恢复")
                return True, "数据恢复成功"
            else:
                return False, f"恢复后启动失败: {msg}"
                
        except Exception as e:
            logger.error(f"恢复失败: {str(e)}")
            return False, f"恢复失败: {str(e)}"
    
    def stop(self):
        """停止 Redis"""
        try:
            if self.process:
                logger.info("🛑 停止 Redis 服务...")
                self.process.terminate()
                self.process.wait(timeout=10)
                self.process = None
                logger.info("✅ Redis 已停止")
        except Exception as e:
            logger.error(f"停止 Redis 失败: {str(e)}")
    
    async def get_info(self) -> Dict[str, Any]:
        """获取 Redis 信息"""
        try:
            redis_client = aioredis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/0",
                encoding="utf-8",
                decode_responses=True
            )
            
            info = await redis_client.info()
            await redis_client.close()
            
            return {
                'version': info.get('redis_version'),
                'uptime_seconds': info.get('uptime_in_seconds'),
                'connected_clients': info.get('connected_clients'),
                'used_memory': info.get('used_memory_human'),
                'total_commands_processed': info.get('total_commands_processed'),
            }
            
        except Exception as e:
            logger.error(f"获取 Redis 信息失败: {str(e)}")
            return {}


# 全局实例
redis_manager_final = RedisManagerFinal()
