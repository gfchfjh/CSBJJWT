"""
✅ P0-12优化: 智能默认配置系统
根据用户系统自动推荐合理的配置，无需理解技术细节
"""
import psutil
import platform
from typing import Dict, Any
from ..utils.logger import logger


class SmartDefaultsManager:
    """智能默认配置管理器"""
    
    def __init__(self):
        self.system_info = self._detect_system()
        logger.info(f"✅ 智能默认配置系统已初始化: {self.system_info['summary']}")
    
    def _detect_system(self) -> Dict[str, Any]:
        """
        检测系统配置
        
        Returns:
            系统信息字典
        """
        try:
            # CPU信息
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024 ** 3)
            memory_available_gb = memory.available / (1024 ** 3)
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024 ** 3)
            disk_free_gb = disk.free / (1024 ** 3)
            
            # 系统类型
            system = platform.system()
            system_version = platform.version()
            
            # 系统性能分类
            if memory_gb >= 16 and cpu_count >= 8:
                performance_level = 'high'
                summary = '高性能系统（推荐配置：高并发）'
            elif memory_gb >= 8 and cpu_count >= 4:
                performance_level = 'medium'
                summary = '中等性能系统（推荐配置：标准）'
            else:
                performance_level = 'low'
                summary = '低性能系统（推荐配置：节能模式）'
            
            return {
                'cpu_count': cpu_count,
                'cpu_count_physical': cpu_count_physical,
                'cpu_percent': cpu_percent,
                'memory_gb': round(memory_gb, 2),
                'memory_available_gb': round(memory_available_gb, 2),
                'memory_percent': memory.percent,
                'disk_total_gb': round(disk_total_gb, 2),
                'disk_free_gb': round(disk_free_gb, 2),
                'disk_percent': disk.percent,
                'system': system,
                'system_version': system_version,
                'performance_level': performance_level,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"检测系统配置失败: {str(e)}")
            return {
                'performance_level': 'medium',
                'summary': '无法检测系统配置，使用默认配置'
            }
    
    def get_recommended_config(self) -> Dict[str, Any]:
        """
        获取推荐配置
        
        Returns:
            推荐配置字典
        """
        perf_level = self.system_info.get('performance_level', 'medium')
        memory_gb = self.system_info.get('memory_gb', 8)
        disk_free_gb = self.system_info.get('disk_free_gb', 100)
        cpu_count = self.system_info.get('cpu_count', 4)
        
        # 基础配置
        config = {
            # ===== 图片处理配置 =====
            'image_strategy': 'smart',  # 智能模式（优先直传，失败用图床）
            'image_storage_max_gb': self._recommend_image_storage(disk_free_gb),
            'image_auto_cleanup_days': 7,  # 7天自动清理
            'image_compression_quality': 85,  # 压缩质量
            'image_max_size_mb': 10.0,  # 最大10MB
            
            # ===== 并发配置 =====
            'max_concurrent_forwarders': self._recommend_concurrency(perf_level, cpu_count),
            'max_queue_size': self._recommend_queue_size(memory_gb),
            
            # ===== 限流配置（自动配置，用户无需设置） =====
            'discord_rate_limit_calls': 5,
            'discord_rate_limit_period': 5,
            'telegram_rate_limit_calls': 30,
            'telegram_rate_limit_period': 1,
            'feishu_rate_limit_calls': 20,
            'feishu_rate_limit_period': 1,
            
            # ===== 日志配置 =====
            'log_retention_days': 3,  # 保留3天
            'log_level': 'INFO',
            'log_max_size_mb': 100,  # 单个日志文件最大100MB
            
            # ===== 验证码配置 =====
            'captcha_mode': 'smart',  # 智能模式（优先2Captcha，失败切换手动）
            'captcha_timeout': 120,  # 120秒超时
            
            # ===== 性能配置 =====
            'use_process_pool': perf_level in ['medium', 'high'],  # 中高性能使用多进程
            'process_pool_workers': self._recommend_workers(cpu_count),
            'enable_caching': True,  # 启用缓存
            'cache_ttl': 300,  # 缓存5分钟
            
            # ===== 安全配置 =====
            'enable_master_password': True,  # 启用主密码
            'session_timeout_minutes': 30,  # 会话超时30分钟
            'remember_me_days': 30,  # 记住我30天
            
            # ===== 备份配置 =====
            'auto_backup_enabled': True,  # 自动备份
            'auto_backup_frequency': 'daily',  # 每天备份
            'backup_retention_days': 7,  # 保留7天
            
            # ===== 通知配置 =====
            'desktop_notification_enabled': True,  # 桌面通知
            'notify_on_error': True,  # 错误时通知
            'notify_on_account_offline': True,  # 账号离线通知
            'notify_on_forward_failed': False,  # 转发失败不通知（太频繁）
        }
        
        # 添加配置说明
        config['_recommendations'] = {
            'performance_level': perf_level,
            'summary': self.system_info.get('summary', ''),
            'reasons': self._get_config_reasons(config, perf_level, memory_gb, disk_free_gb, cpu_count)
        }
        
        return config
    
    def _recommend_image_storage(self, disk_free_gb: float) -> int:
        """
        推荐图床存储大小
        
        Args:
            disk_free_gb: 可用磁盘空间（GB）
            
        Returns:
            推荐的图床大小（GB）
        """
        if disk_free_gb < 20:
            return 2  # 磁盘空间紧张，最多2GB
        elif disk_free_gb < 50:
            return 5
        elif disk_free_gb < 100:
            return 10
        elif disk_free_gb < 200:
            return 20
        else:
            return 30  # 空间充足，最多30GB
    
    def _recommend_concurrency(self, perf_level: str, cpu_count: int) -> int:
        """
        推荐并发数
        
        Args:
            perf_level: 性能级别
            cpu_count: CPU核心数
            
        Returns:
            推荐的并发数
        """
        if perf_level == 'high':
            return min(20, cpu_count * 2)  # 高性能：CPU核心数x2，最多20
        elif perf_level == 'medium':
            return min(10, cpu_count)  # 中等性能：CPU核心数，最多10
        else:
            return min(5, max(2, cpu_count // 2))  # 低性能：CPU核心数/2，最少2，最多5
    
    def _recommend_queue_size(self, memory_gb: float) -> int:
        """
        推荐队列大小
        
        Args:
            memory_gb: 内存大小（GB）
            
        Returns:
            推荐的队列大小
        """
        if memory_gb >= 16:
            return 10000  # 大内存：1万条消息
        elif memory_gb >= 8:
            return 5000  # 中等内存：5千条
        else:
            return 2000  # 小内存：2千条
    
    def _recommend_workers(self, cpu_count: int) -> int:
        """
        推荐工作进程数
        
        Args:
            cpu_count: CPU核心数
            
        Returns:
            推荐的工作进程数
        """
        # 多进程池工作进程数：CPU核心数-1，至少1个
        return max(1, cpu_count - 1)
    
    def _get_config_reasons(self, config: Dict, perf_level: str, 
                           memory_gb: float, disk_free_gb: float, 
                           cpu_count: int) -> Dict[str, str]:
        """
        生成配置推荐理由
        
        Returns:
            配置理由字典
        """
        reasons = {}
        
        # 图床大小理由
        image_gb = config['image_storage_max_gb']
        if disk_free_gb < 20:
            reasons['image_storage'] = f'磁盘空间紧张（剩余{disk_free_gb:.1f}GB），建议图床大小为{image_gb}GB'
        elif disk_free_gb >= 100:
            reasons['image_storage'] = f'磁盘空间充足（剩余{disk_free_gb:.1f}GB），可设置较大图床{image_gb}GB'
        else:
            reasons['image_storage'] = f'根据可用空间（{disk_free_gb:.1f}GB），推荐图床大小{image_gb}GB'
        
        # 并发数理由
        concurrent = config['max_concurrent_forwarders']
        if perf_level == 'high':
            reasons['concurrency'] = f'高性能系统（{cpu_count}核CPU，{memory_gb:.1f}GB内存），可支持{concurrent}个并发转发'
        elif perf_level == 'low':
            reasons['concurrency'] = f'系统资源有限（{cpu_count}核CPU，{memory_gb:.1f}GB内存），建议{concurrent}个并发以保证稳定'
        else:
            reasons['concurrency'] = f'中等性能系统，{concurrent}个并发可兼顾性能与稳定性'
        
        # 多进程理由
        if config['use_process_pool']:
            workers = config['process_pool_workers']
            reasons['process_pool'] = f'系统性能良好，启用{workers}个工作进程可大幅提升图片处理速度'
        else:
            reasons['process_pool'] = '系统资源有限，暂不启用多进程以节省资源'
        
        # 日志理由
        reasons['log_retention'] = '保留3天日志可满足调试需求，同时避免占用过多空间'
        
        # 验证码理由
        reasons['captcha'] = '智能模式优先使用2Captcha自动识别，失败时切换到手动输入，兼顾便利性和可靠性'
        
        return reasons
    
    def apply_to_settings(self, settings):
        """
        将推荐配置应用到settings对象
        
        Args:
            settings: Settings配置对象
        """
        config = self.get_recommended_config()
        
        # 应用配置
        for key, value in config.items():
            if key.startswith('_'):
                continue  # 跳过内部字段
            
            if hasattr(settings, key):
                setattr(settings, key, value)
                logger.debug(f"应用智能配置: {key} = {value}")
        
        logger.info("✅ 智能默认配置已应用")
        
        return config
    
    def get_config_summary(self) -> str:
        """
        获取配置摘要（用于日志）
        
        Returns:
            配置摘要字符串
        """
        config = self.get_recommended_config()
        recommendations = config.get('_recommendations', {})
        
        summary = f"""
╔════════════════════════════════════════════════════════╗
║          智能默认配置推荐                              ║
╠════════════════════════════════════════════════════════╣
║ 系统性能: {recommendations.get('summary', 'N/A')}
║                                                        ║
║ 核心配置:                                              ║
║   图床大小: {config['image_storage_max_gb']}GB          ║
║   并发转发: {config['max_concurrent_forwarders']}个     ║
║   队列大小: {config['max_queue_size']}条                ║
║   工作进程: {config['process_pool_workers']}个          ║
║   日志保留: {config['log_retention_days']}天            ║
║                                                        ║
║ 推荐理由:                                              ║
"""
        
        reasons = recommendations.get('reasons', {})
        for key, reason in reasons.items():
            summary += f"║   • {reason}\n"
        
        summary += "╚════════════════════════════════════════════════════════╝"
        
        return summary


# 创建全局实例
smart_defaults = SmartDefaultsManager()


def get_smart_defaults() -> Dict[str, Any]:
    """获取智能默认配置（便捷函数）"""
    return smart_defaults.get_recommended_config()


def apply_smart_defaults(settings):
    """应用智能默认配置到settings（便捷函数）"""
    return smart_defaults.apply_to_settings(settings)


def print_config_summary():
    """打印配置摘要（便捷函数）"""
    print(smart_defaults.get_config_summary())
