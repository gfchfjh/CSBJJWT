"""
缓存管理器 - 性能优化
提供内存缓存、Redis缓存等多种缓存机制
"""
import asyncio
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import json
import hashlib
from ..utils.logger import logger


class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        
        # 检查是否过期
        if item['expires_at'] < datetime.now():
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        # 更新访问时间
        self.access_times[key] = datetime.now()
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        # 如果缓存满了，移除最久未访问的
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        self.access_times[key] = datetime.now()
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'usage': f"{len(self.cache) / self.max_size * 100:.2f}%"
        }


class RedisCache:
    """Redis缓存（异步）"""
    
    def __init__(self, redis_client, prefix: str = "cache:"):
        self.redis = redis_client
        self.prefix = prefix
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await self.redis.get(self.prefix + key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis缓存获取失败: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        try:
            await self.redis.setex(
                self.prefix + key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {str(e)}")
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            await self.redis.delete(self.prefix + key)
        except Exception as e:
            logger.error(f"Redis缓存删除失败: {str(e)}")
    
    async def clear(self, pattern: str = "*"):
        """清空匹配的缓存"""
        try:
            keys = await self.redis.keys(self.prefix + pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis缓存清空失败: {str(e)}")


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.memory_cache = MemoryCache(max_size=1000, default_ttl=300)
        self.redis_cache = None
    
    def set_redis(self, redis_client):
        """设置Redis客户端"""
        self.redis_cache = RedisCache(redis_client)
    
    async def get(self, key: str, use_redis: bool = False) -> Optional[Any]:
        """获取缓存（先内存后Redis）"""
        # 先查内存缓存
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # 再查Redis缓存
        if use_redis and self.redis_cache:
            value = await self.redis_cache.get(key)
            if value is not None:
                # 回填到内存缓存
                self.memory_cache.set(key, value)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300, use_redis: bool = False):
        """设置缓存"""
        # 设置内存缓存
        self.memory_cache.set(key, value, ttl)
        
        # 设置Redis缓存
        if use_redis and self.redis_cache:
            await self.redis_cache.set(key, value, ttl)
    
    async def delete(self, key: str, use_redis: bool = False):
        """删除缓存"""
        self.memory_cache.delete(key)
        
        if use_redis and self.redis_cache:
            await self.redis_cache.delete(key)
    
    async def clear(self, use_redis: bool = False):
        """清空所有缓存"""
        self.memory_cache.clear()
        
        if use_redis and self.redis_cache:
            await self.redis_cache.clear()


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(ttl: int = 300, use_redis: bool = False, key_prefix: str = ""):
    """
    缓存装饰器
    
    用法:
        @cached(ttl=60)
        async def get_user(user_id: int):
            # ... 查询数据库
            return user
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # 尝试从缓存获取
            cached_value = await cache_manager.get(cache_key, use_redis=use_redis)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 调用原函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache_manager.set(cache_key, result, ttl=ttl, use_redis=use_redis)
            
            return result
        
        return wrapper
    return decorator


# 使用示例
"""
from app.utils.cache_manager import cached

@cached(ttl=60)
async def get_server_list(account_id: int):
    # 这个函数的结果会被缓存60秒
    return await fetch_servers_from_db(account_id)
"""
