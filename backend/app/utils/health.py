"""
健康检查模块
定期检查系统各组件状态
"""
import asyncio
import aiohttp
from typing import Dict, Any, List
from datetime import datetime
from ..config import settings
from .logger import logger


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = getattr(settings, 'health_check_interval', 300)
        self.last_results = {}
        self.listeners = []
    
    async def check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            from ..queue.redis_client import redis_queue
            
            if hasattr(redis_queue, 'redis') and redis_queue.redis:
                await redis_queue.redis.ping()
                return {"status": "healthy", "message": "Redis连接正常"}
            else:
                return {"status": "unhealthy", "message": "Redis未连接"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Redis连接失败: {str(e)}"}
    
    async def check_discord_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """检查Discord Webhook可用性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(webhook_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return {"status": "healthy", "message": "Discord Webhook可用"}
                    else:
                        return {"status": "unhealthy", "message": f"Discord Webhook返回 {response.status}"}
        except asyncio.TimeoutError:
            return {"status": "unhealthy", "message": "Discord Webhook连接超时"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Discord Webhook检查失败: {str(e)}"}
    
    async def check_telegram_bot(self, token: str) -> Dict[str, Any]:
        """检查Telegram Bot可用性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.telegram.org/bot{token}/getMe", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    if data.get("ok"):
                        return {"status": "healthy", "message": f"Telegram Bot可用: @{data['result']['username']}"}
                    else:
                        return {"status": "unhealthy", "message": "Telegram Bot Token无效"}
        except asyncio.TimeoutError:
            return {"status": "unhealthy", "message": "Telegram API连接超时"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Telegram Bot检查失败: {str(e)}"}
    
    async def check_feishu_app(self, app_id: str, app_secret: str) -> Dict[str, Any]:
        """检查飞书应用可用性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", json={"app_id": app_id, "app_secret": app_secret}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    if data.get("code") == 0:
                        return {"status": "healthy", "message": "飞书应用可用"}
                    else:
                        return {"status": "unhealthy", "message": f"飞书应用认证失败: {data.get('msg')}"}
        except asyncio.TimeoutError:
            return {"status": "unhealthy", "message": "飞书API连接超时"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"飞书应用检查失败: {str(e)}"}
    
    async def check_all_bots(self) -> List[Dict[str, Any]]:
        """检查所有Bot配置"""
        from ..database import db
        
        results = []
        bot_configs = db.get_bot_configs()
        
        for bot in bot_configs:
            platform = bot['platform']
            config = bot['config']
            
            if platform == 'discord':
                result = await self.check_discord_webhook(config.get('webhook_url'))
            elif platform == 'telegram':
                result = await self.check_telegram_bot(config.get('token'))
            elif platform == 'feishu':
                result = await self.check_feishu_app(config.get('app_id'), config.get('app_secret'))
            else:
                result = {"status": "unknown", "message": f"未知平台: {platform}"}
            
            results.append({"bot_id": bot['id'], "bot_name": bot['name'], "platform": platform, **result})
        
        return results
    
    async def check_scrapers(self) -> Dict[str, Any]:
        """检查抓取器状态"""
        from ..kook.scraper import scraper_manager
        
        total_scrapers = len(scraper_manager.scrapers)
        active_scrapers = sum(1 for scraper in scraper_manager.scrapers.values() if scraper.is_running)
        
        return {"total": total_scrapers, "active": active_scrapers, "status": "healthy" if active_scrapers > 0 else "warning", "message": f"{active_scrapers}/{total_scrapers} 个抓取器运行中"}
    
    async def check_worker(self) -> Dict[str, Any]:
        """检查Worker状态"""
        from ..queue.worker import message_worker
        
        if message_worker.is_running:
            return {"status": "healthy", "message": "Worker运行中"}
        else:
            return {"status": "unhealthy", "message": "Worker未运行"}
    
    async def check_storage(self) -> Dict[str, Any]:
        """检查存储空间"""
        import shutil
        from pathlib import Path
        
        try:
            data_dir = Path(settings.data_dir)
            stat = shutil.disk_usage(data_dir)
            
            total_gb = stat.total / (1024 ** 3)
            used_gb = stat.used / (1024 ** 3)
            free_gb = stat.free / (1024 ** 3)
            usage_percent = (stat.used / stat.total) * 100
            
            status = "healthy"
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            
            return {"status": status, "total_gb": round(total_gb, 2), "used_gb": round(used_gb, 2), "free_gb": round(free_gb, 2), "usage_percent": round(usage_percent, 1), "message": f"磁盘使用: {round(usage_percent, 1)}%"}
        except Exception as e:
            return {"status": "error", "message": f"存储检查失败: {str(e)}"}
    
    async def check_all(self) -> Dict[str, Any]:
        """执行所有健康检查（调度器接口）"""
        try:
            full_results = await self.perform_health_check()
            checks = {}
            for component, status in full_results["components"].items():
                if component == "bots":
                    all_healthy = all(bot.get("status") == "healthy" for bot in status)
                    checks["bots"] = {"healthy": all_healthy, "message": f"{len(status)} bots checked"}
                else:
                    checks[component] = {"healthy": status.get("status") == "healthy", "message": status.get("message", "")}
            return {"healthy": full_results["overall_status"] == "healthy", "checks": checks}
        except Exception as e:
            logger.error(f"check_all失败: {str(e)}")
            return {"healthy": False, "checks": {"error": {"healthy": False, "message": str(e)}}}
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """执行完整健康检查"""
        logger.info("开始健康检查...")
        
        results = {"timestamp": datetime.now().isoformat(), "overall_status": "healthy", "components": {}}
        
        results["components"]["redis"] = await self.check_redis()
        results["components"]["worker"] = await self.check_worker()
        results["components"]["scrapers"] = await self.check_scrapers()
        results["components"]["bots"] = await self.check_all_bots()
        results["components"]["storage"] = await self.check_storage()
        
        unhealthy_count = 0
        warning_count = 0
        
        for component, status in results["components"].items():
            if component == "bots":
                for bot in status:
                    if bot.get("status") == "unhealthy":
                        unhealthy_count += 1
                    elif bot.get("status") == "warning":
                        warning_count += 1
            else:
                if status.get("status") == "unhealthy":
                    unhealthy_count += 1
                elif status.get("status") in ["warning", "critical"]:
                    warning_count += 1
        
        if unhealthy_count > 0:
            results["overall_status"] = "unhealthy"
        elif warning_count > 0:
            results["overall_status"] = "warning"
        
        self.last_results = results
        await self._notify_listeners(results)
        
        logger.info(f"健康检查完成: {results['overall_status']}")
        
        return results
    
    async def _notify_listeners(self, results: Dict[str, Any]):
        """通知状态变更监听器"""
        for listener in self.listeners:
            try:
                await listener(results)
            except Exception as e:
                logger.error(f"通知监听器失败: {str(e)}")
    
    def add_listener(self, callback):
        """添加状态变更监听器"""
        self.listeners.append(callback)
    
    async def start(self):
        """启动定期健康检查"""
        logger.info(f"启动健康检查服务（间隔: {self.check_interval}秒）")
        self.is_running = True
        
        while self.is_running:
            try:
                await self.perform_health_check()
            except Exception as e:
                logger.error(f"健康检查异常: {str(e)}")
            
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """停止健康检查"""
        logger.info("停止健康检查服务")
        self.is_running = False
    
    def get_last_results(self) -> Dict[str, Any]:
        """获取最后一次检查结果"""
        return self.last_results


health_checker = HealthChecker()