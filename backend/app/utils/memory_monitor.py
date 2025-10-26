"""
全局内存监控模块
实时监控内存使用，防止内存泄漏
"""
import asyncio
import psutil
from typing import Dict, Any, Optional
from datetime import datetime
from collections import OrderedDict
from .logger import logger


class LRUCache:
    """
    线程安全的LRU缓存（全局复用）
    防止缓存无限增长导致内存泄漏
    """
    
    def __init__(self, max_size: int = 10000, name: str = "unnamed"):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存大小
            name: 缓存名称（用于日志）
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.name = name
        self.hits = 0
        self.misses = 0
    
    def add(self, key: str, value: Any = True):
        """
        添加键值对到缓存
        
        Args:
            key: 键
            value: 值（默认True）
        """
        if key in self.cache:
            # 已存在，移到末尾（最近使用）
            self.cache.move_to_end(key)
            self.hits += 1
        else:
            # 新增
            self.cache[key] = value
            self.misses += 1
            
            # 检查是否超出限制
            if len(self.cache) > self.max_size:
                # 删除最旧的项（最前面的）
                removed_key, _ = self.cache.popitem(last=False)
                logger.debug(f"LRU缓存[{self.name}]已满，移除最旧项: {removed_key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return default
    
    def __contains__(self, key: str) -> bool:
        """检查键是否存在"""
        exists = key in self.cache
        if exists:
            self.hits += 1
        else:
            self.misses += 1
        return exists
    
    def __len__(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def clear(self):
        """清空缓存"""
        size = len(self.cache)
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info(f"LRU缓存[{self.name}]已清空，释放 {size} 个项")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'name': self.name,
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate * 100:.2f}%",
            'usage_percent': f"{len(self.cache) / self.max_size * 100:.1f}%"
        }


class MemoryMonitor:
    """
    全局内存监控器
    定期检查内存使用，超限时自动清理
    """
    
    def __init__(self, max_memory_mb: int = 500, check_interval: int = 60):
        """
        初始化内存监控器
        
        Args:
            max_memory_mb: 最大内存限制（MB）
            check_interval: 检查间隔（秒）
        """
        self.max_memory_mb = max_memory_mb
        self.check_interval = check_interval
        self.process = psutil.Process()
        self.is_running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # 注册的LRU缓存
        self.registered_caches: Dict[str, LRUCache] = {}
        
        # 内存历史记录（最近100次）
        self.memory_history = OrderedDict()
        self.max_history = 100
        
        # 清理回调
        self.cleanup_callbacks = []
        
        logger.info(f"✅ 内存监控器已初始化：最大{max_memory_mb}MB，检查间隔{check_interval}秒")
    
    def register_cache(self, name: str, cache: LRUCache):
        """
        注册LRU缓存到监控器
        
        Args:
            name: 缓存名称
            cache: LRU缓存实例
        """
        self.registered_caches[name] = cache
        logger.info(f"✅ LRU缓存已注册: {name} (max_size={cache.max_size})")
    
    def register_cleanup_callback(self, callback):
        """
        注册清理回调函数
        
        Args:
            callback: 异步清理函数
        """
        self.cleanup_callbacks.append(callback)
    
    async def start(self):
        """启动内存监控"""
        if self.is_running:
            logger.warning("内存监控器已在运行")
            return
        
        self.is_running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("🔍 内存监控器已启动")
    
    async def stop(self):
        """停止内存监控"""
        self.is_running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("内存监控器已停止")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                await self.check_and_cleanup()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"内存监控异常: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def check_and_cleanup(self):
        """检查内存使用，超限时清理"""
        try:
            # 获取内存信息
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = self.process.memory_percent()
            
            # 记录历史
            timestamp = datetime.now().isoformat()
            self.memory_history[timestamp] = {
                'memory_mb': memory_mb,
                'memory_percent': memory_percent
            }
            
            # 限制历史记录数量
            if len(self.memory_history) > self.max_history:
                self.memory_history.popitem(last=False)
            
            # 检查是否超限
            if memory_mb > self.max_memory_mb:
                logger.warning(
                    f"⚠️ 内存使用过高: {memory_mb:.2f}MB / {self.max_memory_mb}MB "
                    f"({memory_percent:.1f}%)，开始清理..."
                )
                await self.cleanup_all()
            else:
                # 定期报告（每10次检查）
                if len(self.memory_history) % 10 == 0:
                    logger.info(
                        f"💾 内存使用: {memory_mb:.2f}MB / {self.max_memory_mb}MB "
                        f"({memory_percent:.1f}%)"
                    )
            
        except Exception as e:
            logger.error(f"内存检查失败: {str(e)}")
    
    async def cleanup_all(self):
        """清理所有缓存和资源"""
        logger.info("🧹 开始清理内存...")
        
        cleaned_items = 0
        
        # 1. 清理注册的LRU缓存
        for name, cache in self.registered_caches.items():
            size_before = len(cache)
            # 清理一半最旧的项
            items_to_remove = size_before // 2
            for _ in range(items_to_remove):
                if len(cache.cache) > 0:
                    cache.cache.popitem(last=False)
                    cleaned_items += 1
            
            logger.info(
                f"  清理缓存[{name}]: {size_before} -> {len(cache)} "
                f"(-{items_to_remove}项)"
            )
        
        # 2. 调用自定义清理回调
        for callback in self.cleanup_callbacks:
            try:
                await callback()
            except Exception as e:
                logger.error(f"清理回调失败: {str(e)}")
        
        # 3. 强制垃圾回收
        import gc
        gc.collect()
        
        # 4. 检查清理效果
        memory_after = self.process.memory_info().rss / (1024 * 1024)
        logger.info(
            f"✅ 清理完成：释放了 {cleaned_items} 个缓存项，"
            f"内存: {memory_after:.2f}MB"
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        memory_percent = self.process.memory_percent()
        
        # 获取所有缓存统计
        cache_stats = {}
        total_cache_size = 0
        for name, cache in self.registered_caches.items():
            cache_stats[name] = cache.get_stats()
            total_cache_size += len(cache)
        
        # 计算历史趋势
        if len(self.memory_history) > 1:
            recent_memories = list(self.memory_history.values())
            first_memory = recent_memories[0]['memory_mb']
            last_memory = recent_memories[-1]['memory_mb']
            trend = last_memory - first_memory
            trend_text = f"+{trend:.2f}MB" if trend > 0 else f"{trend:.2f}MB"
        else:
            trend_text = "N/A"
        
        return {
            'current_memory_mb': round(memory_mb, 2),
            'max_memory_mb': self.max_memory_mb,
            'memory_percent': round(memory_percent, 2),
            'usage_ratio': f"{memory_mb / self.max_memory_mb * 100:.1f}%",
            'total_cache_items': total_cache_size,
            'registered_caches': len(self.registered_caches),
            'cache_details': cache_stats,
            'trend': trend_text,
            'history_count': len(self.memory_history)
        }
    
    def get_recommendations(self) -> list:
        """获取优化建议"""
        recommendations = []
        
        memory_mb = self.process.memory_info().rss / (1024 * 1024)
        usage_ratio = memory_mb / self.max_memory_mb
        
        if usage_ratio > 0.9:
            recommendations.append("内存使用超过90%，建议重启应用")
        elif usage_ratio > 0.7:
            recommendations.append("内存使用较高，建议减少并发任务")
        
        # 检查缓存使用率
        for name, cache in self.registered_caches.items():
            cache_usage = len(cache) / cache.max_size
            if cache_usage > 0.9:
                recommendations.append(f"缓存[{name}]接近满载，建议增加max_size")
            
            stats = cache.get_stats()
            hit_rate = float(stats['hit_rate'].rstrip('%'))
            if hit_rate < 50:
                recommendations.append(f"缓存[{name}]命中率低({stats['hit_rate']})，建议优化")
        
        if not recommendations:
            recommendations.append("内存使用正常，无需优化")
        
        return recommendations


# 创建全局内存监控器实例
memory_monitor = MemoryMonitor(max_memory_mb=500, check_interval=60)


# 工厂函数：创建注册的LRU缓存
def create_lru_cache(name: str, max_size: int = 10000) -> LRUCache:
    """
    创建并注册LRU缓存
    
    Args:
        name: 缓存名称
        max_size: 最大大小
        
    Returns:
        LRU缓存实例
    """
    cache = LRUCache(max_size=max_size, name=name)
    memory_monitor.register_cache(name, cache)
    return cache
