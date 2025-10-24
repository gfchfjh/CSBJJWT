"""
依赖注入容器
✅ P0-1优化: 解决循环依赖问题
"""
from typing import Dict, Any, Optional, Callable
from threading import Lock


class Container:
    """
    依赖注入容器 - 管理全局依赖
    
    使用方式:
    ```python
    # 注册
    container.register('db', database_instance)
    container.register_factory('logger', lambda: create_logger())
    
    # 获取
    db = container.get('db')
    logger = container.get('logger')
    ```
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化容器"""
        if self._initialized:
            return
        
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lock = Lock()
        self._initialized = True
    
    def register(self, name: str, instance: Any):
        """
        注册实例
        
        Args:
            name: 依赖名称
            instance: 实例对象
        """
        with self._lock:
            self._instances[name] = instance
    
    def register_factory(self, name: str, factory: Callable):
        """
        注册工厂函数（延迟实例化）
        
        Args:
            name: 依赖名称
            factory: 工厂函数
        """
        with self._lock:
            self._factories[name] = factory
    
    def get(self, name: str) -> Optional[Any]:
        """
        获取依赖
        
        Args:
            name: 依赖名称
            
        Returns:
            依赖实例，不存在返回None
        """
        # 先查找已实例化的对象
        if name in self._instances:
            return self._instances[name]
        
        # 查找工厂函数
        if name in self._factories:
            with self._lock:
                # 双重检查锁定
                if name not in self._instances:
                    self._instances[name] = self._factories[name]()
                return self._instances[name]
        
        return None
    
    def has(self, name: str) -> bool:
        """检查依赖是否存在"""
        return name in self._instances or name in self._factories
    
    def clear(self):
        """清空所有依赖（测试用）"""
        with self._lock:
            self._instances.clear()
            self._factories.clear()
    
    def unregister(self, name: str):
        """注销依赖"""
        with self._lock:
            self._instances.pop(name, None)
            self._factories.pop(name, None)


# 全局容器实例
container = Container()
