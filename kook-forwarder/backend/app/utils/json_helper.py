"""
统一JSON处理工具
✅ P1-2优化: 使用orjson提升性能3-5倍
"""
from typing import Any, Union

try:
    import orjson
    
    def loads(data: Union[bytes, str]) -> Any:
        """
        解析JSON数据
        
        Args:
            data: JSON字符串或字节
            
        Returns:
            解析后的Python对象
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return orjson.loads(data)
    
    def dumps(obj: Any, **kwargs) -> str:
        """
        序列化为JSON字符串
        
        Args:
            obj: Python对象
            **kwargs: 额外参数（兼容标准json.dumps）
            
        Returns:
            JSON字符串
        """
        # orjson返回bytes，需要解码
        return orjson.dumps(obj).decode('utf-8')
    
    def dumps_bytes(obj: Any) -> bytes:
        """
        序列化为JSON字节（orjson原生格式）
        
        Args:
            obj: Python对象
            
        Returns:
            JSON字节
        """
        return orjson.dumps(obj)
    
    JSON_BACKEND = "orjson"
    PERFORMANCE_MULTIPLIER = "3-5x"
    
    # 初始化日志
    def _log_backend():
        from .logger import logger
        logger.info(f"✅ 使用{JSON_BACKEND}加速JSON解析（性能提升{PERFORMANCE_MULTIPLIER}）")
    
    try:
        _log_backend()
    except:
        pass  # 日志初始化失败不影响功能

except ImportError:
    # orjson未安装，使用标准json库
    import json
    
    def loads(data: Union[bytes, str]) -> Any:
        """解析JSON数据（标准库fallback）"""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return json.loads(data)
    
    def dumps(obj: Any, **kwargs) -> str:
        """序列化为JSON字符串（标准库fallback）"""
        return json.dumps(obj, **kwargs)
    
    def dumps_bytes(obj: Any) -> bytes:
        """序列化为JSON字节（标准库fallback）"""
        return json.dumps(obj).encode('utf-8')
    
    JSON_BACKEND = "json"
    PERFORMANCE_MULTIPLIER = "1x"
    
    # 初始化日志
    def _log_backend():
        from .logger import logger
        logger.warning(f"⚠️ orjson未安装，使用标准json库（建议: pip install orjson）")
    
    try:
        _log_backend()
    except:
        pass


# 兼容性别名
load = loads
dump = dumps


def get_backend() -> str:
    """获取当前使用的JSON后端"""
    return JSON_BACKEND


def is_orjson_available() -> bool:
    """检查orjson是否可用"""
    return JSON_BACKEND == "orjson"
