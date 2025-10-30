"""
批量写入Worker
✅ P0-2优化: 数据库异步化临时方案，减少阻塞
"""
import asyncio
from typing import Dict, Any, List, Callable
from datetime import datetime
from collections import defaultdict


class BatchWriter:
    """
    批量写入Worker - 减少数据库写入次数
    
    功能:
    1. 缓冲写入请求
    2. 达到批次大小或超时后批量写入
    3. 支持不同类型的数据批量写入
    
    使用方式:
    ```python
    # 创建批量写入器
    writer = BatchWriter(
        batch_size=50,
        flush_interval=5,
        write_func=db.add_message_logs_batch
    )
    
    # 启动
    await writer.start()
    
    # 添加数据
    await writer.add({
        'message_id': '123',
        'content': 'test',
        ...
    })
    
    # 停止
    await writer.stop()
    ```
    """
    
    def __init__(
        self, 
        batch_size: int = 50,
        flush_interval: float = 5.0,
        write_func: Callable = None,
        data_type: str = 'default'
    ):
        """
        初始化批量写入器
        
        Args:
            batch_size: 批次大小（达到该数量立即写入）
            flush_interval: 刷新间隔（秒，超时后强制写入）
            write_func: 批量写入函数
            data_type: 数据类型（用于分类缓冲区）
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.write_func = write_func
        self.data_type = data_type
        
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_lock = asyncio.Lock()
        self.is_running = False
        self.flush_task = None
        self.last_flush_time = datetime.now()
        
        # 统计信息
        self.stats = {
            'total_added': 0,
            'total_flushed': 0,
            'total_batches': 0,
            'failed_batches': 0
        }
    
    async def start(self):
        """启动批量写入器"""
        if self.is_running:
            return
        
        self.is_running = True
        self.flush_task = asyncio.create_task(self._flush_loop())
        
        from ..utils.logger import logger
        logger.info(
            f"✅ 批量写入器已启动 [{self.data_type}]: "
            f"batch_size={self.batch_size}, "
            f"flush_interval={self.flush_interval}s"
        )
    
    async def stop(self):
        """停止批量写入器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消刷新任务
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # 刷新剩余数据
        await self.flush()
        
        from ..utils.logger import logger
        logger.info(
            f"✅ 批量写入器已停止 [{self.data_type}]: "
            f"total_added={self.stats['total_added']}, "
            f"total_flushed={self.stats['total_flushed']}, "
            f"total_batches={self.stats['total_batches']}"
        )
    
    async def add(self, data: Dict[str, Any]):
        """
        添加数据到缓冲区
        
        Args:
            data: 要写入的数据
        """
        async with self.buffer_lock:
            self.buffer.append(data)
            self.stats['total_added'] += 1
            
            # 如果达到批次大小，立即刷新
            if len(self.buffer) >= self.batch_size:
                await self._do_flush()
    
    async def flush(self, force: bool = True):
        """
        手动刷新缓冲区
        
        Args:
            force: 是否强制刷新（即使缓冲区为空）
        """
        async with self.buffer_lock:
            await self._do_flush(force=force)
    
    async def _flush_loop(self):
        """定时刷新循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.flush_interval)
                
                # 检查是否需要刷新
                async with self.buffer_lock:
                    if len(self.buffer) > 0:
                        time_since_last_flush = (datetime.now() - self.last_flush_time).total_seconds()
                        if time_since_last_flush >= self.flush_interval:
                            await self._do_flush()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                from ..utils.logger import logger
                logger.error(f"批量写入器刷新循环异常 [{self.data_type}]: {str(e)}")
                await asyncio.sleep(1)
    
    async def _do_flush(self, force: bool = False):
        """
        执行刷新（内部方法，需要持有锁）
        
        Args:
            force: 是否强制刷新
        """
        if not force and len(self.buffer) == 0:
            return
        
        if len(self.buffer) == 0:
            return
        
        # 取出当前缓冲区数据
        data_to_write = self.buffer.copy()
        self.buffer.clear()
        
        # 更新刷新时间
        self.last_flush_time = datetime.now()
        
        # 执行批量写入（释放锁后执行，避免阻塞）
        try:
            if self.write_func:
                # 同步函数包装为异步
                if asyncio.iscoroutinefunction(self.write_func):
                    await self.write_func(data_to_write)
                else:
                    # 在线程池中执行同步函数
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.write_func, data_to_write)
                
                self.stats['total_flushed'] += len(data_to_write)
                self.stats['total_batches'] += 1
                
                from ..utils.logger import logger
                logger.debug(
                    f"批量写入成功 [{self.data_type}]: {len(data_to_write)}条记录"
                )
            
        except Exception as e:
            self.stats['failed_batches'] += 1
            from ..utils.logger import logger
            logger.error(f"批量写入失败 [{self.data_type}]: {str(e)}")
            
            # 写入失败，重新加入缓冲区（避免数据丢失）
            self.buffer.extend(data_to_write)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.stats.copy()
    
    def get_buffer_size(self) -> int:
        """获取当前缓冲区大小"""
        return len(self.buffer)


class BatchWriterManager:
    """
    批量写入器管理器 - 管理多个批量写入器
    
    使用方式:
    ```python
    manager = BatchWriterManager()
    
    # 注册写入器
    manager.register(
        'message_logs',
        batch_size=50,
        flush_interval=5,
        write_func=db.add_message_logs_batch
    )
    
    # 启动所有
    await manager.start_all()
    
    # 使用
    await manager.add('message_logs', data)
    
    # 停止所有
    await manager.stop_all()
    ```
    """
    
    def __init__(self):
        """初始化管理器"""
        self.writers: Dict[str, BatchWriter] = {}
    
    def register(
        self,
        name: str,
        batch_size: int = 50,
        flush_interval: float = 5.0,
        write_func: Callable = None
    ):
        """
        注册批量写入器
        
        Args:
            name: 写入器名称
            batch_size: 批次大小
            flush_interval: 刷新间隔
            write_func: 写入函数
        """
        if name in self.writers:
            raise ValueError(f"批量写入器已存在: {name}")
        
        writer = BatchWriter(
            batch_size=batch_size,
            flush_interval=flush_interval,
            write_func=write_func,
            data_type=name
        )
        self.writers[name] = writer
    
    async def start_all(self):
        """启动所有写入器"""
        for writer in self.writers.values():
            await writer.start()
    
    async def stop_all(self):
        """停止所有写入器"""
        for writer in self.writers.values():
            await writer.stop()
    
    async def add(self, name: str, data: Dict[str, Any]):
        """
        添加数据
        
        Args:
            name: 写入器名称
            data: 数据
        """
        if name not in self.writers:
            raise ValueError(f"批量写入器不存在: {name}")
        
        await self.writers[name].add(data)
    
    async def flush(self, name: str = None):
        """
        刷新缓冲区
        
        Args:
            name: 写入器名称，None表示刷新所有
        """
        if name:
            if name in self.writers:
                await self.writers[name].flush()
        else:
            for writer in self.writers.values():
                await writer.flush()
    
    def get_stats(self, name: str = None) -> Dict[str, Dict[str, int]]:
        """
        获取统计信息
        
        Args:
            name: 写入器名称，None表示获取所有
            
        Returns:
            统计信息字典
        """
        if name:
            if name in self.writers:
                return {name: self.writers[name].get_stats()}
            return {}
        else:
            return {name: writer.get_stats() for name, writer in self.writers.items()}


# 全局批量写入器管理器实例
batch_writer_manager = BatchWriterManager()
