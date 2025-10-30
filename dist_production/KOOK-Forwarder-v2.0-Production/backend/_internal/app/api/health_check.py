"""
健康检查API
✅ P0-26: 系统健康状态监控
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import psutil
import time
from datetime import datetime
from ..utils.logger import logger
from ..core.multi_account_manager import multi_account_manager
from ..queue.failed_message_queue import failed_message_queue
from ..utils.message_deduplicator import message_deduplicator

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict:
    """
    系统健康检查
    
    Returns:
        健康状态信息
    """
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': get_uptime(),
            'components': await check_all_components(),
            'resources': get_resource_usage(),
            'accounts': get_accounts_health(),
            'queue': get_queue_health()
        }
        
        # 判断整体状态
        component_statuses = [c['status'] for c in health_status['components'].values()]
        
        if 'critical' in component_statuses:
            health_status['status'] = 'critical'
        elif 'degraded' in component_statuses:
            health_status['status'] = 'degraded'
        
        return health_status
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components")
async def check_all_components() -> Dict:
    """检查所有组件状态"""
    components = {}
    
    # 1. 数据库
    components['database'] = await check_database()
    
    # 2. Redis
    components['redis'] = await check_redis()
    
    # 3. 图片服务器
    components['image_server'] = await check_image_server()
    
    # 4. Playwright
    components['playwright'] = await check_playwright()
    
    # 5. 各平台API
    components['platforms'] = await check_platforms()
    
    return components


async def check_database() -> Dict:
    """检查数据库"""
    try:
        from ..database import get_database
        
        db = get_database()
        cursor = db.execute("SELECT COUNT(*) FROM accounts")
        cursor.fetchone()
        
        return {
            'status': 'healthy',
            'message': '数据库正常',
            'response_time': 0  # TODO: 测量响应时间
        }
        
    except Exception as e:
        logger.error(f"数据库检查失败: {str(e)}")
        return {
            'status': 'critical',
            'message': f'数据库异常: {str(e)}'
        }


async def check_redis() -> Dict:
    """检查Redis"""
    try:
        from ..queue.redis_client import redis_client
        
        # Ping测试
        await redis_client.ping()
        
        # 获取队列长度
        queue_length = await redis_client.llen('message_queue')
        
        return {
            'status': 'healthy',
            'message': 'Redis正常',
            'queue_length': queue_length
        }
        
    except Exception as e:
        logger.error(f"Redis检查失败: {str(e)}")
        return {
            'status': 'critical',
            'message': f'Redis异常: {str(e)}'
        }


async def check_image_server() -> Dict:
    """检查图片服务器"""
    try:
        import aiohttp
        
        url = f"http://127.0.0.1:{settings.image_server_port}/health"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return {
                        'status': 'healthy',
                        'message': '图片服务器正常'
                    }
                else:
                    return {
                        'status': 'degraded',
                        'message': f'图片服务器异常: {response.status}'
                    }
                    
    except Exception as e:
        logger.error(f"图片服务器检查失败: {str(e)}")
        return {
            'status': 'degraded',
            'message': f'图片服务器不可用: {str(e)}'
        }


async def check_playwright() -> Dict:
    """检查Playwright"""
    try:
        # 简单检查：是否可以导入
        from playwright.async_api import async_playwright
        
        return {
            'status': 'healthy',
            'message': 'Playwright正常'
        }
        
    except Exception as e:
        logger.error(f"Playwright检查失败: {str(e)}")
        return {
            'status': 'critical',
            'message': f'Playwright异常: {str(e)}'
        }


async def check_platforms() -> Dict:
    """检查各平台API状态"""
    platforms = {}
    
    # Discord
    platforms['discord'] = await check_discord()
    
    # Telegram
    platforms['telegram'] = await check_telegram()
    
    # 飞书
    platforms['feishu'] = await check_feishu()
    
    return platforms


async def check_discord() -> Dict:
    """检查Discord API"""
    try:
        import aiohttp
        
        # 简单的API可用性检查
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v10', timeout=5) as response:
                if response.status in [200, 401]:  # 401也说明API可用
                    return {'status': 'healthy', 'message': 'Discord API正常'}
                else:
                    return {'status': 'degraded', 'message': f'Discord API异常: {response.status}'}
                    
    except Exception as e:
        return {'status': 'degraded', 'message': f'Discord API不可用: {str(e)}'}


async def check_telegram() -> Dict:
    """检查Telegram API"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.telegram.org', timeout=5) as response:
                if response.status in [200, 404]:  # 404也说明API可用
                    return {'status': 'healthy', 'message': 'Telegram API正常'}
                else:
                    return {'status': 'degraded', 'message': f'Telegram API异常: {response.status}'}
                    
    except Exception as e:
        return {'status': 'degraded', 'message': f'Telegram API不可用: {str(e)}'}


async def check_feishu() -> Dict:
    """检查飞书API"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://open.feishu.cn', timeout=5) as response:
                if response.status == 200:
                    return {'status': 'healthy', 'message': '飞书API正常'}
                else:
                    return {'status': 'degraded', 'message': f'飞书API异常: {response.status}'}
                    
    except Exception as e:
        return {'status': 'degraded', 'message': f'飞书API不可用: {str(e)}'}


def get_resource_usage() -> Dict:
    """获取系统资源使用情况"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            }
        }
    except Exception as e:
        logger.error(f"获取资源使用失败: {str(e)}")
        return {}


def get_accounts_health() -> Dict:
    """获取账号健康状态"""
    try:
        stats = multi_account_manager.get_stats()
        
        status = 'healthy'
        if stats['online'] == 0 and stats['total'] > 0:
            status = 'critical'
        elif stats['online'] < stats['total']:
            status = 'degraded'
        
        return {
            'status': status,
            'total': stats['total'],
            'online': stats['online'],
            'offline': stats['offline']
        }
        
    except Exception as e:
        logger.error(f"获取账号健康状态失败: {str(e)}")
        return {
            'status': 'unknown',
            'error': str(e)
        }


def get_queue_health() -> Dict:
    """获取队列健康状态"""
    try:
        stats = failed_message_queue.get_stats()
        
        status = 'healthy'
        if stats['queue_size'] > 100:
            status = 'degraded'
        if stats['queue_size'] > 500:
            status = 'critical'
        
        return {
            'status': status,
            'queue_size': stats['queue_size'],
            'pending_retry': stats['pending_retry']
        }
        
    except Exception as e:
        logger.error(f"获取队列健康状态失败: {str(e)}")
        return {
            'status': 'unknown',
            'error': str(e)
        }


# 启动时间
_start_time = time.time()

def get_uptime() -> float:
    """获取运行时长（秒）"""
    return time.time() - _start_time


@router.get("/detailed")
async def detailed_health_check() -> Dict:
    """详细健康检查"""
    return {
        'basic': await health_check(),
        'deduplicator': message_deduplicator.get_stats(),
        'failed_queue': failed_message_queue.get_stats(),
        'multi_account': multi_account_manager.get_stats()
    }
