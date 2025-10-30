"""
Redis连接池管理器（终极版）
=========================
功能：
1. 连接池复用（5-20连接）
2. 自动重连机制
3. 健康检查
4. 性能监控
5. 连接统计

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import asyncio
import aioredis
from typing import Optional, Any
from datetime import datetime
from ..utils.logger import logger


class RedisPoolUltimate:
    """Redis连接池管理器（终极版）"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        self.pool: Optional[aioredis.Redis] = None
        self.is_connected = False
        
        # 统计信息
        self.stats = {
            'total_commands': 0,
            'failed_commands': 0,
            'reconnect_count': 0,
            'created_at': None,
            'last_ping': None
        }
    
    async def connect(self, minsize: int = 5, maxsize: int = 20):
        """
        创建连接池
        
        Args:
            minsize: 最小连接数
            maxsize: 最大连接数
        """
        if self.pool:
            logger.warning("Redis连接池已存在")
            return
        
        try:
            logger.info(f"创建Redis连接池（{minsize}-{maxsize}连接）...")
            
            url = f'redis://{self.host}:{self.port}/{self.db}'
            if self.password:
                url = f'redis://:{self.password}@{self.host}:{self.port}/{self.db}'
            
            self.pool = await aioredis.create_redis_pool(
                url,
                minsize=minsize,
                maxsize=maxsize,
                encoding='utf-8'
            )
            
            # 测试连接
            await self.pool.ping()
            
            self.is_connected = True
            self.stats['created_at'] = datetime.now()
            self.stats['last_ping'] = datetime.now()
            
            logger.info(f"✅ Redis连接池创建成功 ({self.host}:{self.port})")
            
        except Exception as e:
            logger.error(f"❌ Redis连接池创建失败: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """关闭连接池"""
        if self.pool:
            logger.info("关闭Redis连接池...")
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            self.is_connected = False
            logger.info("✅ Redis连接池已关闭")
    
    async def execute(self, command: str, *args, **kwargs) -> Any:
        """
        执行Redis命令（带重试）
        
        Args:
            command: Redis命令名
            *args: 命令参数
            **kwargs: 额外参数
            
        Returns:
            命令结果
        """
        if not self.pool:
            raise Exception("Redis连接池未初始化")
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 执行命令
                result = await self.pool.execute(command, *args, **kwargs)
                
                # 统计
                self.stats['total_commands'] += 1
                
                return result
                
            except (aioredis.ConnectionError, aioredis.ConnectionClosedError) as e:
                self.stats['failed_commands'] += 1
                
                if attempt < max_retries - 1:
                    logger.warning(f"Redis命令执行失败，重试 ({attempt+1}/{max_retries}): {e}")
                    
                    # 尝试重连
                    await self.reconnect()
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Redis命令执行失败，已达最大重试次数: {e}")
                    raise
            
            except Exception as e:
                self.stats['failed_commands'] += 1
                logger.error(f"Redis命令执行异常: {e}")
                raise
    
    async def reconnect(self):
        """重新连接"""
        try:
            logger.info("尝试重新连接Redis...")
            
            await self.disconnect()
            await asyncio.sleep(2)
            await self.connect()
            
            self.stats['reconnect_count'] += 1
            logger.info("✅ Redis重连成功")
            
        except Exception as e:
            logger.error(f"❌ Redis重连失败: {e}")
            raise
    
    # ==================== 常用操作封装 ====================
    
    async def enqueue(self, queue_name: str, message: Dict[str, Any]):
        """入队（右侧push）"""
        import json
        await self.execute('RPUSH', queue_name, json.dumps(message, ensure_ascii=False))
    
    async def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """出队（左侧阻塞pop）"""
        import json
        result = await self.execute('BLPOP', queue_name, timeout)
        if result:
            _, data = result
            return json.loads(data)
        return None
    
    async def dequeue_batch(self, queue_name: str, count: int = 10, timeout: int = 0) -> List[Dict[str, Any]]:
        """
        批量出队（优化版）
        
        Args:
            queue_name: 队列名
            count: 批量数量
            timeout: 超时时间（秒）
            
        Returns:
            消息列表
        """
        import json
        messages = []
        
        # 第一次使用阻塞pop
        result = await self.execute('BLPOP', queue_name, timeout)
        if not result:
            return []
        
        _, data = result
        messages.append(json.loads(data))
        
        # 剩余使用非阻塞pop
        for _ in range(count - 1):
            result = await self.execute('LPOP', queue_name)
            if not result:
                break
            messages.append(json.loads(result))
        
        return messages
    
    async def get_queue_length(self, queue_name: str = 'message_queue') -> int:
        """获取队列长度"""
        return await self.execute('LLEN', queue_name)
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """设置键值"""
        if expire:
            await self.execute('SETEX', key, expire, value)
        else:
            await self.execute('SET', key, value)
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        return await self.execute('GET', key)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        result = await self.execute('EXISTS', key)
        return bool(result)
    
    async def delete(self, key: str):
        """删除键"""
        await self.execute('DEL', key)
    
    async def ping(self) -> bool:
        """健康检查"""
        try:
            result = await self.execute('PING')
            self.stats['last_ping'] = datetime.now()
            return result == b'PONG' or result == 'PONG'
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = None
        if self.stats['created_at']:
            uptime = (datetime.now() - self.stats['created_at']).total_seconds()
        
        return {
            **self.stats,
            'is_connected': self.is_connected,
            'uptime_seconds': uptime
        }


# 全局连接池实例
redis_pool_ultimate = RedisPoolUltimate()
