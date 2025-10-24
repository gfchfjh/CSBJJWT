"""
单例基类
✅ P1-1优化: 全局变量改为单例模式
"""
from threading import Lock


class Singleton(type):
    """
    单例元类
    
    使用方式:
    ```python
    class MyClass(metaclass=Singleton):
        def __init__(self):
            if hasattr(self, '_initialized'):
                return
            self._initialized = True
            # 初始化代码
    
    # 每次调用都返回同一实例
    obj1 = MyClass()
    obj2 = MyClass()
    assert obj1 is obj2
    ```
    """
    
    _instances = {}
    _lock = Lock()
    
    def __call__(cls, *args, **kwargs):
        """创建或返回单例实例"""
        if cls not in cls._instances:
            with cls._lock:
                # 双重检查锁定
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
    @classmethod
    def reset(mcs, cls=None):
        """
        重置单例实例（测试用）
        
        Args:
            cls: 要重置的类，None表示重置所有
        """
        with mcs._lock:
            if cls is None:
                mcs._instances.clear()
            else:
                mcs._instances.pop(cls, None)


class SingletonMixin:
    """
    单例Mixin类（用于不能使用元类的场景）
    
    使用方式:
    ```python
    class MyClass(SingletonMixin):
        def __init__(self):
            if self._is_initialized():
                return
            self._mark_initialized()
            # 初始化代码
    ```
    """
    
    _instances = {}
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        """创建或返回单例实例"""
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[cls] = instance
                    instance._singleton_initialized = False
        return cls._instances[cls]
    
    def _is_initialized(self) -> bool:
        """检查是否已初始化"""
        return getattr(self, '_singleton_initialized', False)
    
    def _mark_initialized(self):
        """标记为已初始化"""
        self._singleton_initialized = True
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例（测试用）"""
        with cls._lock:
            cls._instances.pop(cls, None)
