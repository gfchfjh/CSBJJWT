"""
选择器配置管理器
支持热更新和多种配置格式
"""
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from .logger import logger
from ..config import settings


class SelectorManager:
    """选择器配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or settings.selector_config_path
        self.config = self._load_default_config()
        self.last_modified = None
        self._load_from_file()
    
    def _load_default_config(self) -> Dict:
        """加载默认选择器配置"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "description": "KOOK页面选择器配置",
            
            # 服务器列表容器选择器（多个备选）
            "server_container": [
                ".guild-list",
                "[class*='guild-list']",
                "[class*='GuildList']",
                "[class*='server-list']",
                "nav[class*='guild']",
            ],
            
            # 服务器项选择器
            "server_item": [
                ".guild-item",
                "[class*='guild-item']",
                "[class*='GuildItem']",
                "[class*='server-item']",
                "[data-guild-id]",
                "[data-server-id]",
                "a[href*='/guild/']",
                "div[class*='guild'][class*='item']",
            ],
            
            # 服务器名称选择器
            "server_name": [
                ".guild-name",
                "[class*='guild-name']",
                "[class*='GuildName']",
                "[class*='name']",
                ".server-name",
                "span",
                "div",
            ],
            
            # 频道列表容器选择器
            "channel_container": [
                ".channel-list",
                "[class*='channel-list']",
                "[class*='ChannelList']",
                "[class*='channels']",
                "nav[class*='channel']",
                "div[class*='sidebar']",
            ],
            
            # 频道项选择器
            "channel_item": [
                ".channel-item",
                "[class*='channel-item']",
                "[class*='ChannelItem']",
                "[data-channel-id]",
                "a[href*='/channel/']",
                "div[class*='channel'][class*='item']",
            ],
            
            # 频道名称选择器
            "channel_name": [
                ".channel-name",
                "[class*='channel-name']",
                "[class*='ChannelName']",
                "[class*='name']",
                "span",
                "div",
            ],
            
            # 登录表单选择器
            "login": {
                "email_input": "input[type='email']",
                "password_input": "input[type='password']",
                "submit_button": "button[type='submit']",
                "captcha_input": "input[name='captcha']",
                "captcha_image": [
                    "img.captcha-image",
                    "img[alt*='验证码']",
                    ".captcha-container img",
                ]
            },
            
            # 消息相关选择器
            "message": {
                "message_list": [
                    ".message-list",
                    "[class*='message-list']",
                    "[class*='MessageList']",
                ],
                "message_item": [
                    ".message-item",
                    "[class*='message-item']",
                    "[data-message-id]",
                ]
            }
        }
    
    def _load_from_file(self):
        """从文件加载配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
                        file_config = yaml.safe_load(f)
                    elif self.config_path.suffix == '.json':
                        file_config = json.load(f)
                    else:
                        # 默认尝试YAML
                        file_config = yaml.safe_load(f)
                    
                    # 合并配置（文件配置优先）
                    self._merge_config(file_config)
                    self.last_modified = datetime.fromtimestamp(
                        self.config_path.stat().st_mtime
                    )
                    logger.info(f"✅ 成功加载选择器配置: {self.config_path}")
            else:
                # 首次运行，创建默认配置文件
                self.save_to_file()
                logger.info(f"✅ 创建默认选择器配置: {self.config_path}")
        except Exception as e:
            logger.error(f"❌ 加载选择器配置失败: {str(e)}")
            logger.info("使用默认配置")
    
    def _merge_config(self, file_config: Dict):
        """合并配置（文件配置优先）"""
        if not file_config:
            return
        
        for key, value in file_config.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    # 递归合并字典
                    self.config[key].update(value)
                else:
                    # 直接覆盖
                    self.config[key] = value
            else:
                # 新增键
                self.config[key] = value
    
    def save_to_file(self):
        """保存配置到文件"""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    # 默认保存为YAML（更易读）
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"✅ 选择器配置已保存: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 保存选择器配置失败: {str(e)}")
            return False
    
    def reload(self) -> bool:
        """重新加载配置"""
        try:
            logger.info("🔄 重新加载选择器配置...")
            self._load_from_file()
            return True
        except Exception as e:
            logger.error(f"❌ 重新加载配置失败: {str(e)}")
            return False
    
    def check_and_reload(self) -> bool:
        """检查文件是否修改，如果修改则重新加载"""
        try:
            if not self.config_path.exists():
                return False
            
            current_mtime = datetime.fromtimestamp(
                self.config_path.stat().st_mtime
            )
            
            if self.last_modified is None or current_mtime > self.last_modified:
                logger.info("📝 检测到选择器配置文件变更")
                return self.reload()
            
            return False
        except Exception as e:
            logger.error(f"❌ 检查配置文件失败: {str(e)}")
            return False
    
    def get_selectors(self, category: str) -> List[str]:
        """
        获取指定类别的选择器列表
        
        Args:
            category: 类别名（如 'server_container', 'channel_item'）
            
        Returns:
            选择器列表
        """
        value = self.config.get(category, [])
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value]
        else:
            logger.warning(f"⚠️ 无效的选择器类别: {category}")
            return []
    
    def get_selector_dict(self, category: str) -> Dict:
        """
        获取指定类别的选择器字典
        
        Args:
            category: 类别名（如 'login', 'message'）
            
        Returns:
            选择器字典
        """
        value = self.config.get(category, {})
        if isinstance(value, dict):
            return value
        else:
            logger.warning(f"⚠️ 无效的选择器类别: {category}")
            return {}
    
    def update_selector(self, category: str, selectors: List[str]) -> bool:
        """
        更新选择器配置
        
        Args:
            category: 类别名
            selectors: 选择器列表
            
        Returns:
            是否成功
        """
        try:
            self.config[category] = selectors
            return self.save_to_file()
        except Exception as e:
            logger.error(f"❌ 更新选择器失败: {str(e)}")
            return False
    
    def add_selector(self, category: str, selector: str, position: int = 0) -> bool:
        """
        添加选择器（插入到指定位置，默认最前面）
        
        Args:
            category: 类别名
            selector: 选择器
            position: 插入位置
            
        Returns:
            是否成功
        """
        try:
            if category not in self.config:
                self.config[category] = []
            
            if not isinstance(self.config[category], list):
                logger.error(f"❌ {category} 不是列表类型")
                return False
            
            # 避免重复
            if selector in self.config[category]:
                logger.warning(f"⚠️ 选择器已存在: {selector}")
                return False
            
            self.config[category].insert(position, selector)
            return self.save_to_file()
        except Exception as e:
            logger.error(f"❌ 添加选择器失败: {str(e)}")
            return False
    
    def remove_selector(self, category: str, selector: str) -> bool:
        """
        删除选择器
        
        Args:
            category: 类别名
            selector: 选择器
            
        Returns:
            是否成功
        """
        try:
            if category not in self.config:
                return False
            
            if not isinstance(self.config[category], list):
                return False
            
            if selector in self.config[category]:
                self.config[category].remove(selector)
                return self.save_to_file()
            
            return False
        except Exception as e:
            logger.error(f"❌ 删除选择器失败: {str(e)}")
            return False
    
    def export_config(self) -> str:
        """导出配置为JSON字符串"""
        return json.dumps(self.config, indent=2, ensure_ascii=False)
    
    def import_config(self, config_str: str, format: str = 'json') -> bool:
        """
        导入配置
        
        Args:
            config_str: 配置字符串
            format: 格式（'json' 或 'yaml'）
            
        Returns:
            是否成功
        """
        try:
            if format == 'json':
                imported_config = json.loads(config_str)
            elif format == 'yaml':
                imported_config = yaml.safe_load(config_str)
            else:
                logger.error(f"❌ 不支持的格式: {format}")
                return False
            
            self._merge_config(imported_config)
            return self.save_to_file()
        except Exception as e:
            logger.error(f"❌ 导入配置失败: {str(e)}")
            return False


# 创建全局选择器管理器实例
selector_manager = SelectorManager()
