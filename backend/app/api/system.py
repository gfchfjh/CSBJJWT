"""
系统管理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..queue.redis_client import redis_queue
from ..queue.worker import message_worker
from ..kook.scraper import scraper_manager
from ..processors.filter import message_filter
from ..config import settings
import asyncio


router = APIRouter(prefix="/api/system", tags=["system"])


class SystemStatus(BaseModel):
    service_running: bool
    redis_connected: bool
    queue_size: int
    active_scrapers: int


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    try:
        queue_size = await redis_queue.get_queue_size()
        redis_connected = True
    except:
        queue_size = 0
        redis_connected = False
    
    return {
        "service_running": message_worker.is_running,
        "redis_connected": redis_connected,
        "queue_size": queue_size,
        "active_scrapers": len(scraper_manager.scrapers)
    }


@router.post("/start")
async def start_service():
    """启动服务"""
    if not message_worker.is_running:
        asyncio.create_task(message_worker.start())
    
    return {"message": "服务已启动"}


@router.post("/stop")
async def stop_service():
    """停止服务"""
    await message_worker.stop()
    await scraper_manager.stop_all()
    
    return {"message": "服务已停止"}


@router.get("/config")
async def get_config():
    """获取配置信息"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "api_port": settings.api_port,
        "image_storage_path": str(settings.image_storage_path),
        "log_level": settings.log_level
    }


@router.get("/filter-rules")
async def get_filter_rules():
    """获取过滤规则"""
    rules = message_filter.get_rules()
    return rules


class FilterRules(BaseModel):
    scope: str = "global"
    channel_id: Optional[str] = None
    keyword_blacklist: List[str] = []
    keyword_whitelist: List[str] = []
    keyword_filter_enabled: bool = False
    user_blacklist: List[Dict[str, str]] = []
    user_whitelist: List[Dict[str, str]] = []
    user_filter_enabled: bool = False
    message_types: List[str] = ["text", "image", "file", "link"]
    only_mention_all: bool = False


@router.post("/filter-rules")
async def save_filter_rules(rules: FilterRules):
    """保存过滤规则"""
    try:
        success = message_filter.save_rules(rules.dict())
        if success:
            return {"message": "过滤规则保存成功"}
        else:
            raise HTTPException(status_code=500, detail="保存失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    from ..database import db
    from datetime import datetime, timedelta
    
    # 获取今日消息统计
    logs = db.get_message_logs(limit=1000)
    
    today = datetime.now().date()
    today_logs = [log for log in logs if datetime.fromisoformat(log['created_at']).date() == today]
    
    total = len(today_logs)
    success = len([log for log in today_logs if log['status'] == 'success'])
    failed = len([log for log in today_logs if log['status'] == 'failed'])
    
    # 计算平均延迟
    latencies = [log['latency_ms'] for log in today_logs if log.get('latency_ms')]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    # 计算成功率
    success_rate = (success / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "success_rate": round(success_rate, 1),
        "avg_latency": round(avg_latency, 0)
    }


@router.post("/restart")
async def restart_service():
    """重启服务"""
    await message_worker.stop()
    await asyncio.sleep(1)
    asyncio.create_task(message_worker.start())
    
    return {"message": "服务正在重启"}


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        from datetime import datetime
        
        # 检查Redis连接
        redis_ok = await redis_queue.ping() if hasattr(redis_queue, 'ping') else True
        
        # 检查Worker状态
        worker_ok = message_worker.is_running
        
        # 检查抓取器状态
        scrapers_count = len(scraper_manager.scrapers)
        
        status = "healthy" if (redis_ok and worker_ok) else "unhealthy"
        
        return {
            "status": status,
            "redis": "connected" if redis_ok else "disconnected",
            "worker": "running" if worker_ok else "stopped",
            "scrapers": scrapers_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


class EmailConfig(BaseModel):
    """邮件配置"""
    enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    to_emails: List[str] = []


@router.get("/email-config")
async def get_email_config():
    """获取邮件配置"""
    from ..database import db
    import json
    
    email_config = db.get_system_config('email_config')
    if email_config:
        config = json.loads(email_config)
        # 隐藏密码
        if config.get('smtp_password'):
            config['smtp_password'] = '******'
        return config
    else:
        return EmailConfig().dict()


@router.post("/email-config")
async def save_email_config(config: EmailConfig):
    """保存邮件配置"""
    from ..database import db
    from ..utils.email_sender import email_sender
    import json
    
    try:
        # 如果密码是******，则保持原密码不变
        if config.smtp_password == '******':
            old_config = db.get_system_config('email_config')
            if old_config:
                old_data = json.loads(old_config)
                config.smtp_password = old_data.get('smtp_password')
        
        # 保存配置
        db.set_system_config('email_config', json.dumps(config.dict(), ensure_ascii=False))
        
        # 重新加载配置
        email_sender.load_config()
        
        return {"success": True, "message": "邮件配置保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email-test")
async def test_email():
    """测试邮件发送"""
    from ..utils.email_sender import email_sender
    
    # 先重新加载配置
    email_sender.load_config()
    
    # 测试连接
    success, message = await email_sender.test_connection()
    
    if success:
        # 发送测试邮件
        await email_sender.send_alert(
            alert_type='info',
            title='邮件测试',
            message='这是一封测试邮件，如果您收到此邮件，说明邮件配置正确。'
        )
        return {"success": True, "message": "测试邮件已发送"}
    else:
        return {"success": False, "message": message}
