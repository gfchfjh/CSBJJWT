"""
插件系统
✅ P1-1: 可扩展的插件架构
"""
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..utils.logger import logger


@dataclass
class PluginInfo:
    """插件信息"""
    id: str
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True
    

class PluginHook:
    """插件钩子类型"""
    # 消息处理钩子
    BEFORE_MESSAGE_PROCESS = 'before_message_process'
    AFTER_MESSAGE_PROCESS = 'after_message_process'
    
    # 消息转发钩子
    BEFORE_MESSAGE_FORWARD = 'before_message_forward'
    AFTER_MESSAGE_FORWARD = 'after_message_forward'
    
    # 图片处理钩子
    BEFORE_IMAGE_PROCESS = 'before_image_process'
    AFTER_IMAGE_PROCESS = 'after_image_process'
    
    # 配置钩子
    ON_CONFIG_CHANGE = 'on_config_change'
    
    # 系统钩子
    ON_STARTUP = 'on_startup'
    ON_SHUTDOWN = 'on_shutdown'


class PluginBase(ABC):
    """插件基类"""
    
    def __init__(self):
        self.info: Optional[PluginInfo] = None
        self.enabled = True
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    async def on_load(self):
        """插件加载时调用"""
        pass
    
    async def on_unload(self):
        """插件卸载时调用"""
        pass
    
    async def on_enable(self):
        """插件启用时调用"""
        pass
    
    async def on_disable(self):
        """插件禁用时调用"""
        pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.plugin_dir = Path('plugins')
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计
        self.stats = {
            'total_plugins': 0,
            'enabled_plugins': 0,
            'disabled_plugins': 0,
            'total_hooks': 0
        }
    
    async def load_plugin(self, plugin_path: Path) -> bool:
        """
        加载插件
        
        Args:
            plugin_path: 插件文件路径
            
        Returns:
            是否加载成功
        """
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                plugin_path.stem,
                plugin_path
            )
            
            if not spec or not spec.loader:
                logger.error(f"无法加载插件: {plugin_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"插件中未找到PluginBase子类: {plugin_path}")
                return False
            
            # 实例化插件
            plugin = plugin_class()
            
            # 获取插件信息
            info = plugin.get_info()
            plugin.info = info
            
            # 检查插件ID是否已存在
            if info.id in self.plugins:
                logger.warning(f"插件ID已存在，将被覆盖: {info.id}")
            
            # 注册插件
            self.plugins[info.id] = plugin
            
            # 调用加载钩子
            await plugin.on_load()
            
            # 更新统计
            self.stats['total_plugins'] = len(self.plugins)
            self.stats['enabled_plugins'] = sum(
                1 for p in self.plugins.values() if p.enabled
            )
            
            logger.info(f"插件加载成功: {info.name} v{info.version} by {info.author}")
            
            return True
            
        except Exception as e:
            logger.error(f"加载插件失败 {plugin_path}: {str(e)}")
            return False
    
    async def load_all_plugins(self):
        """加载所有插件"""
        plugin_files = list(self.plugin_dir.glob('*.py'))
        
        logger.info(f"发现{len(plugin_files)}个插件文件")
        
        for plugin_file in plugin_files:
            await self.load_plugin(plugin_file)
        
        logger.info(f"插件加载完成，共{len(self.plugins)}个插件")
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            是否卸载成功
        """
        if plugin_id not in self.plugins:
            logger.warning(f"插件不存在: {plugin_id}")
            return False
        
        try:
            plugin = self.plugins[plugin_id]
            
            # 调用卸载钩子
            await plugin.on_unload()
            
            # 移除插件
            del self.plugins[plugin_id]
            
            # 移除相关钩子
            for hook_name in list(self.hooks.keys()):
                self.hooks[hook_name] = [
                    hook for hook in self.hooks[hook_name]
                    if not hasattr(hook, '__self__') or hook.__self__ != plugin
                ]
            
            # 更新统计
            self.stats['total_plugins'] = len(self.plugins)
            
            logger.info(f"插件卸载成功: {plugin_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"卸载插件失败 {plugin_id}: {str(e)}")
            return False
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        
        if plugin.enabled:
            return True
        
        try:
            await plugin.on_enable()
            plugin.enabled = True
            
            self.stats['enabled_plugins'] += 1
            self.stats['disabled_plugins'] -= 1
            
            logger.info(f"插件已启用: {plugin_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"启用插件失败 {plugin_id}: {str(e)}")
            return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """禁用插件"""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        
        if not plugin.enabled:
            return True
        
        try:
            await plugin.on_disable()
            plugin.enabled = False
            
            self.stats['enabled_plugins'] -= 1
            self.stats['disabled_plugins'] += 1
            
            logger.info(f"插件已禁用: {plugin_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"禁用插件失败 {plugin_id}: {str(e)}")
            return False
    
    def register_hook(self, hook_name: str, callback: Callable):
        """
        注册钩子
        
        Args:
            hook_name: 钩子名称
            callback: 回调函数
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
        
        self.stats['total_hooks'] = sum(len(hooks) for hooks in self.hooks.values())
        
        logger.debug(f"钩子已注册: {hook_name}")
    
    async def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        调用钩子
        
        Args:
            hook_name: 钩子名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            所有钩子的返回值列表
        """
        if hook_name not in self.hooks:
            return []
        
        results = []
        
        for callback in self.hooks[hook_name]:
            try:
                # 检查插件是否启用
                if hasattr(callback, '__self__'):
                    plugin = callback.__self__
                    if isinstance(plugin, PluginBase) and not plugin.enabled:
                        continue
                
                # 调用钩子
                if inspect.iscoroutinefunction(callback):
                    result = await callback(*args, **kwargs)
                else:
                    result = callback(*args, **kwargs)
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"钩子调用失败 {hook_name}: {str(e)}")
        
        return results
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """获取所有插件信息"""
        return [plugin.info for plugin in self.plugins.values() if plugin.info]
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """获取已启用的插件"""
        return [
            plugin.info for plugin in self.plugins.values()
            if plugin.enabled and plugin.info
        ]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'disabled_plugins': self.stats['total_plugins'] - self.stats['enabled_plugins']
        }


# 全局插件管理器
plugin_manager = PluginManager()


# 装饰器：注册钩子
def hook(hook_name: str):
    """
    钩子装饰器
    
    用法:
    @hook(PluginHook.BEFORE_MESSAGE_PROCESS)
    async def my_hook(self, message):
        # 处理消息
        return message
    """
    def decorator(func):
        plugin_manager.register_hook(hook_name, func)
        return func
    return decorator
