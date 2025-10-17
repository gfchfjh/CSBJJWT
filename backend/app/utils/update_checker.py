"""
自动更新检查模块
检查GitHub Releases获取最新版本
"""
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from packaging import version
from .logger import logger
from ..config import settings
from ..database import db


class UpdateChecker:
    """更新检查器"""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = settings.auto_update_check_interval
        self.github_repo = settings.github_repo
        self.current_version = settings.app_version
        self.last_check_time = None
        self.latest_version_info = None
    
    async def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        检查GitHub Releases获取最新版本
        
        Returns:
            版本信息字典，如果有更新则返回，否则返回None
        """
        try:
            logger.info("🔍 检查更新...")
            
            # 获取GitHub Releases API
            api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_url,
                    headers={
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': f'{settings.app_name}/{self.current_version}'
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        latest_version = data.get('tag_name', '').lstrip('v')
                        release_name = data.get('name', '')
                        release_body = data.get('body', '')
                        published_at = data.get('published_at', '')
                        html_url = data.get('html_url', '')
                        
                        # 获取下载链接
                        assets = data.get('assets', [])
                        downloads = {}
                        for asset in assets:
                            name = asset.get('name', '')
                            download_url = asset.get('browser_download_url', '')
                            
                            if 'Windows' in name or '.exe' in name:
                                downloads['windows'] = download_url
                            elif 'macOS' in name or '.dmg' in name:
                                downloads['macos'] = download_url
                            elif 'Linux' in name or '.AppImage' in name:
                                downloads['linux'] = download_url
                        
                        version_info = {
                            'latest_version': latest_version,
                            'current_version': self.current_version,
                            'release_name': release_name,
                            'release_notes': release_body,
                            'published_at': published_at,
                            'release_url': html_url,
                            'downloads': downloads,
                            'checked_at': datetime.now().isoformat()
                        }
                        
                        # 比较版本
                        if self._is_newer_version(latest_version, self.current_version):
                            logger.info(f"✨ 发现新版本: {latest_version} (当前: {self.current_version})")
                            version_info['has_update'] = True
                            self.latest_version_info = version_info
                            
                            # 保存到数据库
                            db.set_config('latest_version_info', str(version_info))
                            
                            return version_info
                        else:
                            logger.info(f"✅ 当前已是最新版本: {self.current_version}")
                            version_info['has_update'] = False
                            return version_info
                    
                    elif response.status == 404:
                        logger.warning("⚠️ 未找到GitHub Releases，可能仓库未发布版本")
                        return None
                    else:
                        logger.error(f"❌ GitHub API返回错误: {response.status}")
                        return None
        
        except asyncio.TimeoutError:
            logger.error("❌ 检查更新超时")
            return None
        except Exception as e:
            logger.error(f"❌ 检查更新失败: {str(e)}")
            return None
        finally:
            self.last_check_time = datetime.now()
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        比较版本号
        
        Args:
            latest: 最新版本
            current: 当前版本
            
        Returns:
            最新版本是否更新
        """
        try:
            # 移除可能的 'v' 前缀
            latest = latest.lstrip('v')
            current = current.lstrip('v')
            
            # 使用packaging库比较版本
            return version.parse(latest) > version.parse(current)
        except Exception as e:
            logger.error(f"❌ 版本比较失败: {str(e)}")
            return False
    
    def should_check(self) -> bool:
        """
        判断是否应该检查更新
        
        Returns:
            是否应该检查
        """
        if not settings.auto_update_enabled:
            return False
        
        if self.last_check_time is None:
            return True
        
        # 检查间隔时间是否已到
        elapsed = datetime.now() - self.last_check_time
        return elapsed.total_seconds() >= self.check_interval
    
    async def start(self):
        """启动定期检查"""
        if not settings.auto_update_enabled:
            logger.info("ℹ️ 自动更新检查已禁用")
            return
        
        logger.info(f"🚀 启动自动更新检查（间隔: {self.check_interval/3600:.1f}小时）")
        self.is_running = True
        
        # 首次启动时立即检查
        await self.check_for_updates()
        
        while self.is_running:
            try:
                # 等待检查间隔
                await asyncio.sleep(self.check_interval)
                
                # 执行检查
                await self.check_for_updates()
            
            except Exception as e:
                logger.error(f"❌ 更新检查循环异常: {str(e)}")
                await asyncio.sleep(60)  # 出错后等待1分钟再继续
    
    async def stop(self):
        """停止检查"""
        logger.info("⏹️ 停止自动更新检查")
        self.is_running = False
    
    def get_latest_version_info(self) -> Optional[Dict[str, Any]]:
        """
        获取最新版本信息（从缓存）
        
        Returns:
            版本信息字典
        """
        return self.latest_version_info
    
    async def manual_check(self) -> Optional[Dict[str, Any]]:
        """
        手动检查更新（忽略检查间隔）
        
        Returns:
            版本信息字典
        """
        logger.info("🔍 手动检查更新...")
        return await self.check_for_updates()
    
    def get_download_url(self, platform: str) -> Optional[str]:
        """
        获取指定平台的下载链接
        
        Args:
            platform: 平台名（windows/macos/linux）
            
        Returns:
            下载链接
        """
        if not self.latest_version_info:
            return None
        
        downloads = self.latest_version_info.get('downloads', {})
        return downloads.get(platform.lower())
    
    def format_release_notes(self, max_length: int = 500) -> str:
        """
        格式化发布说明（用于通知）
        
        Args:
            max_length: 最大长度
            
        Returns:
            格式化的发布说明
        """
        if not self.latest_version_info:
            return ""
        
        notes = self.latest_version_info.get('release_notes', '')
        
        if len(notes) > max_length:
            notes = notes[:max_length] + "..."
        
        return notes
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取更新检查状态
        
        Returns:
            状态信息
        """
        return {
            'enabled': settings.auto_update_enabled,
            'is_running': self.is_running,
            'current_version': self.current_version,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'check_interval_hours': self.check_interval / 3600,
            'has_update': self.latest_version_info is not None and self.latest_version_info.get('has_update', False),
            'latest_version': self.latest_version_info.get('latest_version') if self.latest_version_info else None
        }


# 创建全局更新检查器实例
update_checker = UpdateChecker()
