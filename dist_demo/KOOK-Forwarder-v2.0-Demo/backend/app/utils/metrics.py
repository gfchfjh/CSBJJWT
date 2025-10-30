"""
Prometheus监控指标模块
提供应用性能和业务指标的收集
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_client import CollectorRegistry, REGISTRY
from typing import Optional
import time


# 创建自定义Registry（避免与其他模块冲突）
registry = CollectorRegistry()

# ============= 业务指标 =============

# 消息处理计数器
messages_processed = Counter(
    'kook_forwarder_messages_processed_total',
    'Total number of messages processed',
    ['platform', 'status', 'message_type'],
    registry=registry
)

# 消息处理延迟
message_latency = Histogram(
    'kook_forwarder_message_processing_seconds',
    'Message processing latency in seconds',
    ['platform', 'operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    registry=registry
)

# 当前队列大小
queue_size = Gauge(
    'kook_forwarder_queue_size',
    'Current message queue size',
    registry=registry
)

# 活跃账号数
active_accounts = Gauge(
    'kook_forwarder_active_accounts',
    'Number of active KOOK accounts',
    registry=registry
)

# 活跃Bot数
active_bots = Gauge(
    'kook_forwarder_active_bots',
    'Number of active bots',
    ['platform'],
    registry=registry
)

# ============= 系统指标 =============

# 应用信息
app_info = Info(
    'kook_forwarder_app',
    'Application information',
    registry=registry
)

# 数据库操作计数器
db_operations = Counter(
    'kook_forwarder_db_operations_total',
    'Total database operations',
    ['operation', 'table', 'status'],
    registry=registry
)

# Redis操作计数器
redis_operations = Counter(
    'kook_forwarder_redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=registry
)

# 图片处理计数器
image_operations = Counter(
    'kook_forwarder_image_operations_total',
    'Total image operations',
    ['operation', 'status'],
    registry=registry
)

# 图片处理延迟
image_processing_time = Histogram(
    'kook_forwarder_image_processing_seconds',
    'Image processing time in seconds',
    ['operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=registry
)

# 图床存储大小
image_storage_size = Gauge(
    'kook_forwarder_image_storage_bytes',
    'Image storage size in bytes',
    registry=registry
)

# ============= 错误指标 =============

# 错误计数器
errors_total = Counter(
    'kook_forwarder_errors_total',
    'Total errors',
    ['error_type', 'module'],
    registry=registry
)

# 重试计数器
retries_total = Counter(
    'kook_forwarder_retries_total',
    'Total retry attempts',
    ['reason', 'platform'],
    registry=registry
)


class MetricsCollector:
    """指标收集器"""
    
    @staticmethod
    def record_message_processed(platform: str, status: str, message_type: str = 'text'):
        """
        记录消息处理
        
        Args:
            platform: 目标平台
            status: 处理状态 (success/failed)
            message_type: 消息类型
        """
        messages_processed.labels(
            platform=platform,
            status=status,
            message_type=message_type
        ).inc()
    
    @staticmethod
    def record_message_latency(platform: str, operation: str, duration: float):
        """
        记录消息处理延迟
        
        Args:
            platform: 目标平台
            operation: 操作类型 (download/process/forward)
            duration: 耗时（秒）
        """
        message_latency.labels(
            platform=platform,
            operation=operation
        ).observe(duration)
    
    @staticmethod
    def update_queue_size(size: int):
        """
        更新队列大小
        
        Args:
            size: 队列中的消息数
        """
        queue_size.set(size)
    
    @staticmethod
    def update_active_accounts(count: int):
        """
        更新活跃账号数
        
        Args:
            count: 活跃账号数量
        """
        active_accounts.set(count)
    
    @staticmethod
    def update_active_bots(platform: str, count: int):
        """
        更新活跃Bot数
        
        Args:
            platform: 平台名称
            count: Bot数量
        """
        active_bots.labels(platform=platform).set(count)
    
    @staticmethod
    def record_db_operation(operation: str, table: str, status: str = 'success'):
        """
        记录数据库操作
        
        Args:
            operation: 操作类型 (select/insert/update/delete)
            table: 表名
            status: 状态
        """
        db_operations.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
    
    @staticmethod
    def record_redis_operation(operation: str, status: str = 'success'):
        """
        记录Redis操作
        
        Args:
            operation: 操作类型 (get/set/delete/publish)
            status: 状态
        """
        redis_operations.labels(
            operation=operation,
            status=status
        ).inc()
    
    @staticmethod
    def record_image_operation(operation: str, status: str = 'success'):
        """
        记录图片操作
        
        Args:
            operation: 操作类型 (download/compress/upload)
            status: 状态
        """
        image_operations.labels(
            operation=operation,
            status=status
        ).inc()
    
    @staticmethod
    def record_image_processing_time(operation: str, duration: float):
        """
        记录图片处理时间
        
        Args:
            operation: 操作类型
            duration: 耗时（秒）
        """
        image_processing_time.labels(operation=operation).observe(duration)
    
    @staticmethod
    def update_image_storage_size(size_bytes: int):
        """
        更新图床存储大小
        
        Args:
            size_bytes: 存储大小（字节）
        """
        image_storage_size.set(size_bytes)
    
    @staticmethod
    def record_error(error_type: str, module: str):
        """
        记录错误
        
        Args:
            error_type: 错误类型
            module: 模块名
        """
        errors_total.labels(
            error_type=error_type,
            module=module
        ).inc()
    
    @staticmethod
    def record_retry(reason: str, platform: str):
        """
        记录重试
        
        Args:
            reason: 重试原因
            platform: 平台名称
        """
        retries_total.labels(
            reason=reason,
            platform=platform
        ).inc()
    
    @staticmethod
    def set_app_info(version: str, environment: str = 'production'):
        """
        设置应用信息
        
        Args:
            version: 应用版本
            environment: 运行环境
        """
        app_info.info({
            'version': version,
            'environment': environment
        })


# 导出便捷函数
def get_metrics() -> bytes:
    """
    获取Prometheus格式的指标数据
    
    Returns:
        Prometheus文本格式的指标
    """
    return generate_latest(registry)


# 上下文管理器：自动记录操作耗时
class measure_time:
    """
    上下文管理器：自动记录操作耗时
    
    使用示例:
        with measure_time('discord', 'forward'):
            await discord_forwarder.send_message(...)
    """
    
    def __init__(self, platform: str, operation: str):
        self.platform = platform
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        MetricsCollector.record_message_latency(
            self.platform,
            self.operation,
            duration
        )


# 异步上下文管理器版本
class async_measure_time:
    """
    异步上下文管理器：自动记录操作耗时
    
    使用示例:
        async with async_measure_time('discord', 'forward'):
            await discord_forwarder.send_message(...)
    """
    
    def __init__(self, platform: str, operation: str):
        self.platform = platform
        self.operation = operation
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        MetricsCollector.record_message_latency(
            self.platform,
            self.operation,
            duration
        )


# 创建全局收集器实例
metrics = MetricsCollector()
