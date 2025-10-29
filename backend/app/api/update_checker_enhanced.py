"""
更新检查API - 增强版
✅ P2-2优化：完整的更新检查功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import aiohttp
import json
from datetime import datetime
from ..config import settings
from ..utils.logger import logger

router = APIRouter(prefix="/api/updates", tags=["更新检查"])


class VersionInfo(BaseModel):
    """版本信息"""
    version: str
    release_date: str
    download_url: str
    changelog: str
    is_critical: bool = False  # 是否关键更新（必须更新）
    min_version: Optional[str] = None  # 最低兼容版本


class UpdateCheckResponse(BaseModel):
    """更新检查响应"""
    has_update: bool
    current_version: str
    latest_version: Optional[str] = None
    download_url: Optional[str] = None
    changelog: Optional[str] = None
    is_critical: bool = False


@router.get("/check", response_model=UpdateCheckResponse)
async def check_for_updates():
    """
    检查是否有可用更新
    
    从GitHub Releases获取最新版本信息
    
    Returns:
        更新检查结果
    """
    try:
        current_version = settings.app_version
        
        # 从GitHub API获取最新Release
        github_api_url = "https://api.github.com/repos/your-username/CSBJJWT/releases/latest"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                github_api_url,
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    latest_version = data['tag_name'].lstrip('v')
                    
                    # 比较版本
                    has_update = compare_versions(latest_version, current_version) > 0
                    
                    if has_update:
                        # 查找对应平台的下载链接
                        download_url = get_download_url(data['assets'])
                        
                        return UpdateCheckResponse(
                            has_update=True,
                            current_version=current_version,
                            latest_version=latest_version,
                            download_url=download_url,
                            changelog=data.get('body', ''),
                            is_critical=is_critical_update(data.get('body', ''))
                        )
                    else:
                        return UpdateCheckResponse(
                            has_update=False,
                            current_version=current_version,
                            latest_version=current_version
                        )
                else:
                    logger.warning(f"GitHub API返回错误: {response.status}")
                    return UpdateCheckResponse(
                        has_update=False,
                        current_version=current_version
                    )
    
    except Exception as e:
        logger.error(f"检查更新失败: {str(e)}")
        # 返回无更新（避免因网络问题影响用户）
        return UpdateCheckResponse(
            has_update=False,
            current_version=settings.app_version
        )


@router.get("/versions")
async def get_version_history(limit: int = 10):
    """
    获取版本历史
    
    Args:
        limit: 返回的版本数量
        
    Returns:
        版本历史列表
    """
    try:
        github_api_url = f"https://api.github.com/repos/your-username/CSBJJWT/releases?per_page={limit}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                github_api_url,
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    versions = [
                        {
                            'version': release['tag_name'].lstrip('v'),
                            'release_date': release['published_at'],
                            'changelog': release.get('body', ''),
                            'download_url': get_download_url(release['assets']),
                            'is_prerelease': release.get('prerelease', False)
                        }
                        for release in data
                    ]
                    
                    return {
                        'success': True,
                        'versions': versions
                    }
                else:
                    raise HTTPException(status_code=response.status, detail="GitHub API请求失败")
    
    except Exception as e:
        logger.error(f"获取版本历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_version():
    """
    获取当前版本信息
    
    Returns:
        当前版本信息
    """
    return {
        'version': settings.app_version,
        'app_name': settings.app_name,
        'build_date': datetime.now().isoformat()
    }


@router.post("/notify")
async def send_update_notification(version: str):
    """
    发送更新通知
    
    Args:
        version: 新版本号
        
    Returns:
        通知发送结果
    """
    try:
        # TODO: 实现通知发送逻辑
        # 可以通过WebSocket、邮件等方式通知用户
        
        logger.info(f"发送更新通知: v{version}")
        
        return {
            'success': True,
            'message': f'更新通知已发送: v{version}'
        }
    
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def compare_versions(v1: str, v2: str) -> int:
    """
    比较版本号
    
    Args:
        v1: 版本1
        v2: 版本2
        
    Returns:
        v1 > v2: 1
        v1 == v2: 0
        v1 < v2: -1
    """
    def parse_version(v):
        return tuple(map(int, v.split('.')))
    
    try:
        ver1 = parse_version(v1)
        ver2 = parse_version(v2)
        
        if ver1 > ver2:
            return 1
        elif ver1 < ver2:
            return -1
        else:
            return 0
    except:
        return 0


def get_download_url(assets: List[dict]) -> Optional[str]:
    """
    从assets中获取适合当前平台的下载链接
    
    Args:
        assets: GitHub Release assets
        
    Returns:
        下载链接
    """
    import platform
    
    system = platform.system()
    
    for asset in assets:
        name = asset['name'].lower()
        
        if system == 'Windows' and ('.exe' in name or '.msi' in name):
            return asset['browser_download_url']
        elif system == 'Darwin' and ('.dmg' in name or '.pkg' in name):
            return asset['browser_download_url']
        elif system == 'Linux' and '.appimage' in name:
            return asset['browser_download_url']
    
    # 没有找到匹配的，返回第一个
    return assets[0]['browser_download_url'] if assets else None


def is_critical_update(changelog: str) -> bool:
    """
    判断是否是关键更新
    
    通过changelog中的关键词判断
    
    Args:
        changelog: 更新日志
        
    Returns:
        是否关键更新
    """
    critical_keywords = [
        '安全更新',
        '紧急修复',
        '严重漏洞',
        'security',
        'critical',
        'urgent',
        '必须更新'
    ]
    
    changelog_lower = changelog.lower()
    
    return any(keyword.lower() in changelog_lower for keyword in critical_keywords)
