"""
链接预览处理模块
自动提取链接的标题、描述、图片等元数据
"""
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from ..utils.logger import logger


class LinkPreviewGenerator:
    """链接预览生成器"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    async def extract_preview(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取链接预览信息
        
        Args:
            url: 链接URL
            
        Returns:
            预览信息字典，包含title、description、image、url等
        """
        try:
            logger.info(f"正在提取链接预览: {url}")
            
            # 下载页面
            html = await self._fetch_html(url)
            if not html:
                return None
            
            # 解析页面
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取元数据
            preview_data = {
                'url': url,
                'title': None,
                'description': None,
                'image': None,
                'site_name': None,
                'type': 'website'
            }
            
            # 1. 优先尝试Open Graph协议
            og_data = self._extract_opengraph(soup)
            if og_data:
                preview_data.update(og_data)
            
            # 2. 如果没有OG数据，尝试Twitter Card
            if not preview_data['title']:
                twitter_data = self._extract_twitter_card(soup)
                if twitter_data:
                    preview_data.update(twitter_data)
            
            # 3. 如果仍然没有，尝试HTML标签
            if not preview_data['title']:
                html_data = self._extract_html_meta(soup)
                if html_data:
                    preview_data.update(html_data)
            
            # 4. 处理相对URL
            if preview_data['image']:
                preview_data['image'] = urljoin(url, preview_data['image'])
            
            # 5. 如果有标题，说明提取成功
            if preview_data['title']:
                logger.info(f"✅ 链接预览提取成功: {preview_data['title']}")
                return preview_data
            else:
                logger.warning(f"⚠️ 未能提取链接预览: {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 链接预览提取失败: {url}, 错误: {str(e)}")
            return None
    
    async def _fetch_html(self, url: str) -> Optional[str]:
        """
        下载网页HTML
        
        Args:
            url: 网页URL
            
        Returns:
            HTML内容
        """
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        # 检查Content-Type
                        content_type = response.headers.get('Content-Type', '')
                        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                            logger.warning(f"URL不是HTML页面: {content_type}")
                            return None
                        
                        html = await response.text()
                        return html
                    else:
                        logger.error(f"下载失败: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"下载超时: {url}")
            return None
        except Exception as e:
            logger.error(f"下载异常: {url}, {str(e)}")
            return None
    
    def _extract_opengraph(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        提取Open Graph元数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            OG元数据字典
        """
        og_data = {}
        
        # 查找所有og:meta标签
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            
            if property_name == 'title':
                og_data['title'] = content
            elif property_name == 'description':
                og_data['description'] = content
            elif property_name == 'image':
                og_data['image'] = content
            elif property_name == 'site_name':
                og_data['site_name'] = content
            elif property_name == 'type':
                og_data['type'] = content
        
        return og_data if og_data else None
    
    def _extract_twitter_card(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        提取Twitter Card元数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Twitter Card元数据字典
        """
        twitter_data = {}
        
        # 查找所有twitter:meta标签
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            
            if name == 'title':
                twitter_data['title'] = content
            elif name == 'description':
                twitter_data['description'] = content
            elif name == 'image':
                twitter_data['image'] = content
            elif name == 'site':
                twitter_data['site_name'] = content
        
        return twitter_data if twitter_data else None
    
    def _extract_html_meta(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        从HTML标准标签提取元数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            元数据字典
        """
        html_data = {}
        
        # 标题
        title_tag = soup.find('title')
        if title_tag:
            html_data['title'] = title_tag.get_text().strip()
        
        # 描述
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            html_data['description'] = desc_tag.get('content', '').strip()
        
        # 尝试查找第一张有意义的图片
        # 优先查找meta标签中的image
        image_tag = soup.find('link', rel='image_src')
        if image_tag:
            html_data['image'] = image_tag.get('href')
        else:
            # 查找页面中的第一张较大的图片
            for img in soup.find_all('img'):
                src = img.get('src', '')
                width = img.get('width', '')
                height = img.get('height', '')
                
                # 跳过小图标和Logo
                try:
                    if width and height:
                        w = int(width.replace('px', ''))
                        h = int(height.replace('px', ''))
                        if w >= 200 and h >= 200:
                            html_data['image'] = src
                            break
                except:
                    pass
        
        return html_data if html_data else None
    
    def extract_urls_from_text(self, text: str) -> list:
        """
        从文本中提取所有URL
        
        Args:
            text: 文本内容
            
        Returns:
            URL列表
        """
        # URL正则表达式
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # 去重并保持顺序
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    async def process_message_links(self, message_content: str, max_previews: int = 3) -> list:
        """
        处理消息中的链接，生成预览
        
        Args:
            message_content: 消息内容
            max_previews: 最多生成几个预览
            
        Returns:
            预览列表
        """
        # 提取所有URL
        urls = self.extract_urls_from_text(message_content)
        
        if not urls:
            return []
        
        # 限制数量
        urls = urls[:max_previews]
        
        # 为每个URL生成预览
        previews = []
        for url in urls:
            preview = await self.extract_preview(url)
            if preview:
                previews.append(preview)
        
        return previews
    
    def format_preview_for_discord(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化预览为Discord Embed
        
        Args:
            preview: 预览数据
            
        Returns:
            Discord Embed字典
        """
        embed = {
            'title': preview['title'] or 'Link Preview',
            'url': preview['url'],
            'color': 0x5865F2  # Discord蓝色
        }
        
        if preview['description']:
            # 限制描述长度
            desc = preview['description'][:300]
            if len(preview['description']) > 300:
                desc += '...'
            embed['description'] = desc
        
        if preview['image']:
            embed['image'] = {'url': preview['image']}
        
        if preview['site_name']:
            embed['footer'] = {'text': preview['site_name']}
        
        return embed
    
    def format_preview_for_telegram(self, preview: Dict[str, Any]) -> str:
        """
        格式化预览为Telegram HTML
        
        Args:
            preview: 预览数据
            
        Returns:
            HTML格式文本
        """
        html_parts = []
        
        html_parts.append(f'<b><a href="{preview["url"]}">{preview["title"] or "链接"}</a></b>')
        
        if preview['description']:
            desc = preview['description'][:200]
            if len(preview['description']) > 200:
                desc += '...'
            html_parts.append(f'\n{desc}')
        
        if preview['site_name']:
            html_parts.append(f'\n<i>{preview["site_name"]}</i>')
        
        return ''.join(html_parts)
    
    def format_preview_for_feishu(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化预览为飞书卡片
        
        Args:
            preview: 预览数据
            
        Returns:
            飞书卡片字典
        """
        card = {
            'config': {
                'wide_screen_mode': True
            },
            'elements': []
        }
        
        # 标题
        card['elements'].append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': f'**[{preview["title"] or "链接"}]({preview["url"]})**'
            }
        })
        
        # 描述
        if preview['description']:
            desc = preview['description'][:200]
            if len(preview['description']) > 200:
                desc += '...'
            card['elements'].append({
                'tag': 'div',
                'text': {
                    'tag': 'plain_text',
                    'content': desc
                }
            })
        
        # 图片
        if preview['image']:
            card['elements'].append({
                'tag': 'img',
                'img_key': preview['image'],
                'alt': {
                    'tag': 'plain_text',
                    'content': preview['title'] or '图片'
                }
            })
        
        # 来源
        if preview['site_name']:
            card['elements'].append({
                'tag': 'note',
                'elements': [{
                    'tag': 'plain_text',
                    'content': preview['site_name']
                }]
            })
        
        return card


# 全局实例
link_preview_generator = LinkPreviewGenerator()
