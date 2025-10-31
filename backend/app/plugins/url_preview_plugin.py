"""
URL预览插件
自动提取消息中的链接并生成预览卡片
"""
import re
import aiohttp
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .plugin_system import PluginBase, PluginInfo, PluginHook, plugin_manager
from ..utils.logger import logger


class URLPreviewPlugin(PluginBase):
    """URL预览插件"""
    
    def __init__(self):
        super().__init__()
        
        # URL正则
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # 配置
        self.max_previews = 3  # 每条消息最多提取3个链接
        self.timeout = 10  # 超时时间（秒）
        
        # 统计
        self.stats = {
            'total_urls': 0,
            'previews_generated': 0,
            'failed': 0
        }
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            id='url_preview',
            name='URL预览',
            version='1.0.0',
            author='KOOK Forwarder Team',
            description='自动提取消息中的URL并生成预览卡片'
        )
    
    async def on_load(self):
        """插件加载"""
        # 注册钩子
        plugin_manager.register_hook(
            PluginHook.AFTER_MESSAGE_PROCESS,
            self.extract_and_preview_urls
        )
        
        logger.info("URL预览插件已加载")
    
    async def extract_and_preview_urls(self, message: Dict) -> Dict:
        """
        提取并预览URL
        
        Args:
            message: 消息对象
            
        Returns:
            处理后的消息对象
        """
        content = message.get('content', '')
        
        if not content:
            return message
        
        # 提取所有URL
        urls = self.url_pattern.findall(content)
        
        if not urls:
            return message
        
        # 限制数量
        urls = urls[:self.max_previews]
        self.stats['total_urls'] += len(urls)
        
        # 生成预览
        previews = []
        
        for url in urls:
            try:
                preview = await self._fetch_url_metadata(url)
                
                if preview:
                    previews.append(preview)
                    self.stats['previews_generated'] += 1
                    
            except Exception as e:
                logger.warning(f"提取URL预览失败: {url} - {str(e)}")
                self.stats['failed'] += 1
        
        if previews:
            message['url_previews'] = previews
            logger.info(f"已生成 {len(previews)} 个URL预览")
        
        return message
    
    async def _fetch_url_metadata(self, url: str) -> Optional[Dict]:
        """
        获取URL元数据
        
        Args:
            url: 目标URL
            
        Returns:
            元数据字典 {title, description, image, url}
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; KOOKForwarder/1.0; +https://github.com/gfchfjh/CSBJJWT)'
                    }
                ) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 提取标题
                    title = None
                    og_title = soup.find('meta', property='og:title')
                    if og_title:
                        title = og_title.get('content')
                    else:
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.string
                    
                    # 提取描述
                    description = None
                    og_description = soup.find('meta', property='og:description')
                    if og_description:
                        description = og_description.get('content')
                    else:
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc:
                            description = meta_desc.get('content')
                    
                    # 提取图片
                    image = None
                    og_image = soup.find('meta', property='og:image')
                    if og_image:
                        image = og_image.get('content')
                    
                    # 限制长度
                    if title and len(title) > 100:
                        title = title[:97] + '...'
                    
                    if description and len(description) > 200:
                        description = description[:197] + '...'
                    
                    return {
                        'url': url,
                        'title': title or url,
                        'description': description or '',
                        'image': image or ''
                    }
                    
        except asyncio.TimeoutError:
            logger.warning(f"URL预览超时: {url}")
            return None
        except Exception as e:
            logger.warning(f"获取URL元数据失败: {url} - {str(e)}")
            return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['previews_generated'] / self.stats['total_urls'] * 100
                if self.stats['total_urls'] > 0 else 0
            )
        }
    
    def add_rule(self, keywords: List[str], reply: str, 
                 match_type: str = 'contains') -> bool:
        """
        添加新的关键词回复规则
        
        Args:
            keywords: 关键词列表
            reply: 回复内容
            match_type: 匹配类型
            
        Returns:
            是否成功
        """
        try:
            rule = {
                'keywords': keywords,
                'reply': reply,
                'match_type': match_type,
                'enabled': True
            }
            
            self.reply_rules.insert(0, rule)
            logger.info(f"已添加URL预览规则: {keywords}")
            
            # 保存到配置
            self._save_rules()
            
            return True
            
        except Exception as e:
            logger.error(f"添加URL预览规则失败: {str(e)}")
            return False
    
    def _save_rules(self):
        """保存规则到数据库"""
        try:
            import json
            from ..database import db
            
            db.set_config('url_preview_rules', json.dumps(self.reply_rules, ensure_ascii=False))
            
        except Exception as e:
            logger.error(f"保存URL预览规则失败: {str(e)}")


# 自动注册插件
url_preview_plugin = URLPreviewPlugin()
