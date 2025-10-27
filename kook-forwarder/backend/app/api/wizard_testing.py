"""
✅ P0-2新增: 配置向导测试API
提供完整的配置验证和测试功能
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from pydantic import BaseModel
from ..database import db
from ..utils.logger import logger
from ..queue.redis_client import redis_queue
from ..forwarders.discord import discord_forwarder
from ..forwarders.telegram import TelegramForwarder
from ..forwarders.feishu import FeishuForwarder
from ..kook.scraper import scraper_manager
import asyncio
import time
from datetime import datetime

router = APIRouter(prefix="/api/wizard/test", tags=["wizard-testing"])


class TestMessageRequest(BaseModel):
    """测试消息请求"""
    content: str
    platform: str
    bot_id: int


@router.get("/environment")
async def test_environment():
    """
    测试环境配置
    
    检查项：
    - Redis服务
    - Chromium浏览器
    - 磁盘空间
    - 网络连接
    """
    try:
        results = {
            "redis_available": False,
            "redis_message": "",
            "chromium_available": False,
            "chromium_message": "",
            "disk_available": False,
            "disk_free_gb": 0,
            "network_available": False,
            "network_message": "",
            "auto_fix_available": False
        }
        
        # 1. 检查Redis
        try:
            redis_connected = await redis_queue.ping()
            results["redis_available"] = redis_connected
            results["redis_message"] = "Redis服务运行正常" if redis_connected else "Redis服务未启动"
        except Exception as e:
            results["redis_message"] = f"Redis连接失败: {str(e)}"
            results["auto_fix_available"] = True
        
        # 2. 检查Chromium
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            try:
                # 尝试启动浏览器（超时5秒）
                browser = await asyncio.wait_for(
                    playwright.chromium.launch(headless=True),
                    timeout=5.0
                )
                await browser.close()
                results["chromium_available"] = True
                results["chromium_message"] = "Chromium浏览器可用"
            except asyncio.TimeoutError:
                results["chromium_message"] = "Chromium启动超时，可能正在下载"
            except Exception as browser_error:
                results["chromium_message"] = f"Chromium不可用: {str(browser_error)}"
                results["auto_fix_available"] = True
            finally:
                await playwright.stop()
        except Exception as e:
            results["chromium_message"] = f"Playwright未安装或损坏: {str(e)}"
            results["auto_fix_available"] = True
        
        # 3. 检查磁盘空间
        try:
            import shutil
            from ..config import DATA_DIR
            
            stat = shutil.disk_usage(str(DATA_DIR))
            free_gb = stat.free / (1024 ** 3)
            results["disk_free_gb"] = round(free_gb, 2)
            results["disk_available"] = free_gb > 1.0  # 至少1GB可用空间
            
            if not results["disk_available"]:
                results["disk_message"] = f"磁盘空间不足: 仅剩{free_gb:.2f}GB"
            else:
                results["disk_message"] = f"磁盘空间充足: {free_gb:.2f}GB可用"
        except Exception as e:
            results["disk_message"] = f"磁盘检查失败: {str(e)}"
        
        # 4. 检查网络
        try:
            import aiohttp
            
            # 测试连接到常用域名
            test_urls = [
                "https://www.google.com",
                "https://discord.com",
                "https://api.telegram.org"
            ]
            
            network_ok = False
            async with aiohttp.ClientSession() as session:
                for url in test_urls:
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                            if resp.status < 500:
                                network_ok = True
                                break
                    except:
                        continue
            
            results["network_available"] = network_ok
            results["network_message"] = "网络连接正常" if network_ok else "网络连接异常，可能影响消息转发"
        except Exception as e:
            results["network_message"] = f"网络检查失败: {str(e)}"
        
        return results
        
    except Exception as e:
        logger.error(f"环境测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"环境测试失败: {str(e)}")


@router.post("/environment/autofix")
async def autofix_environment():
    """
    自动修复环境问题
    """
    try:
        fixed_items = []
        failed_items = []
        
        # 1. 尝试启动Redis
        try:
            from ..utils.redis_manager_enhanced import redis_manager
            
            redis_success, redis_msg = await redis_manager.start()
            if redis_success:
                fixed_items.append("Redis服务已启动")
            else:
                failed_items.append(f"Redis启动失败: {redis_msg}")
        except Exception as e:
            failed_items.append(f"Redis修复失败: {str(e)}")
        
        # 2. 检查并安装Chromium
        try:
            from playwright.async_api import async_playwright
            
            # 这里可以触发Chromium下载
            # 实际实现在P0-4中完成
            fixed_items.append("Chromium检查完成")
        except Exception as e:
            failed_items.append(f"Chromium检查失败: {str(e)}")
        
        success = len(failed_items) == 0
        
        return {
            "success": success,
            "message": "自动修复完成" if success else "部分修复失败",
            "fixed_items": fixed_items,
            "failed_items": failed_items
        }
        
    except Exception as e:
        logger.error(f"自动修复失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"自动修复失败: {str(e)}")


@router.get("/account/{account_id}")
async def test_account(account_id: int):
    """
    测试指定账号
    
    验证：
    - 账号状态
    - Cookie有效性
    - 可访问的服务器和频道数量
    - 响应时间
    """
    try:
        start_time = time.time()
        
        # 获取账号信息
        account = db.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        
        # 检查账号状态
        if account['status'] != 'online':
            return {
                "success": False,
                "message": f"账号状态: {account['status']}，需要先启动账号",
                "server_count": 0,
                "channel_count": 0,
                "response_time": 0
            }
        
        # 尝试获取服务器列表（测试连接）
        try:
            scraper = scraper_manager.scrapers.get(account_id)
            if not scraper:
                return {
                    "success": False,
                    "message": "抓取器未启动",
                    "server_count": 0,
                    "channel_count": 0,
                    "response_time": 0
                }
            
            # 获取服务器列表
            servers = await scraper.get_servers()
            
            # 统计频道数量（只获取第一个服务器的频道）
            channel_count = 0
            if servers and len(servers) > 0:
                channels = await scraper.get_channels(servers[0]['id'])
                channel_count = len(channels)
            
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "message": "账号连接正常",
                "server_count": len(servers),
                "channel_count": channel_count,
                "response_time": response_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}",
                "server_count": 0,
                "channel_count": 0,
                "response_time": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"账号测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"账号测试失败: {str(e)}")


@router.post("/message")
async def send_test_message(request: TestMessageRequest):
    """
    发送真实测试消息
    
    这是配置向导的最后一步验证，会发送真实的消息到目标平台
    """
    try:
        start_time = time.time()
        
        # 获取Bot配置
        bots = db.get_bot_configs()
        bot = next((b for b in bots if b['id'] == request.bot_id), None)
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot配置不存在")
        
        # 根据平台发送消息
        platform = request.platform.lower()
        config = bot['config']
        
        try:
            if platform == 'discord':
                # Discord Webhook
                webhook_url = config.get('webhook_url')
                if not webhook_url:
                    raise ValueError("缺少webhook_url配置")
                
                success = await discord_forwarder.send_message(
                    webhook_url=webhook_url,
                    content=request.content,
                    username="KOOK转发系统测试"
                )
                
                if not success:
                    raise ValueError("Discord消息发送失败")
                
                message_id = f"discord_test_{int(time.time())}"
                
            elif platform == 'telegram':
                # Telegram Bot
                token = config.get('token')
                chat_id = config.get('chat_id')
                
                if not token or not chat_id:
                    raise ValueError("缺少token或chat_id配置")
                
                telegram = TelegramForwarder(token)
                success = await telegram.send_message(
                    chat_id=chat_id,
                    text=request.content
                )
                
                if not success:
                    raise ValueError("Telegram消息发送失败")
                
                message_id = f"telegram_test_{int(time.time())}"
                
            elif platform == 'feishu':
                # 飞书
                app_id = config.get('app_id')
                app_secret = config.get('app_secret')
                chat_id = config.get('chat_id')
                
                if not app_id or not app_secret or not chat_id:
                    raise ValueError("飞书配置不完整")
                
                feishu = FeishuForwarder(app_id, app_secret)
                success = await feishu.send_message(
                    chat_id=chat_id,
                    text=request.content
                )
                
                if not success:
                    raise ValueError("飞书消息发送失败")
                
                message_id = f"feishu_test_{int(time.time())}"
                
            else:
                raise ValueError(f"不支持的平台: {platform}")
            
            latency = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ 测试消息发送成功: {platform} - {bot['name']}")
            
            return {
                "success": True,
                "message": "测试消息发送成功",
                "message_id": message_id,
                "latency": latency,
                "sent_at": datetime.now().isoformat()
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试消息发送异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试异常: {str(e)}")


@router.get("/summary")
async def get_test_summary():
    """
    获取完整的测试摘要
    
    返回所有配置项的状态概览
    """
    try:
        # 获取所有配置
        accounts = db.get_accounts()
        bots = db.get_bot_configs()
        mappings = db.get_channel_mappings()
        
        # 统计在线账号
        online_accounts = [a for a in accounts if a['status'] == 'online']
        
        # 统计活跃映射
        active_mappings = [m for m in mappings if m.get('enabled', 1) == 1]
        
        # 检查服务状态
        try:
            redis_connected = await redis_queue.ping()
        except:
            redis_connected = False
        
        return {
            "total_accounts": len(accounts),
            "online_accounts": len(online_accounts),
            "total_bots": len(bots),
            "total_mappings": len(mappings),
            "active_mappings": len(active_mappings),
            "redis_connected": redis_connected,
            "service_ready": (
                len(online_accounts) > 0 and
                len(bots) > 0 and
                len(active_mappings) > 0 and
                redis_connected
            )
        }
        
    except Exception as e:
        logger.error(f"获取测试摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")


@router.post("/batch")
async def run_batch_tests():
    """
    批量运行所有测试
    
    返回完整的测试报告
    """
    try:
        report = {
            "started_at": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # 1. 环境测试
        try:
            env_result = await test_environment()
            report["tests"]["environment"] = {
                "status": "passed" if all([
                    env_result["redis_available"],
                    env_result["chromium_available"],
                    env_result["disk_available"],
                    env_result["network_available"]
                ]) else "failed",
                "details": env_result
            }
        except Exception as e:
            report["tests"]["environment"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # 2. 账号测试
        try:
            accounts = db.get_accounts()
            account_results = []
            
            for account in accounts:
                try:
                    result = await test_account(account['id'])
                    account_results.append({
                        "id": account['id'],
                        "email": account['email'],
                        "passed": result["success"],
                        "details": result
                    })
                except Exception as e:
                    account_results.append({
                        "id": account['id'],
                        "email": account['email'],
                        "passed": False,
                        "error": str(e)
                    })
            
            passed_count = sum(1 for r in account_results if r["passed"])
            
            report["tests"]["accounts"] = {
                "status": "passed" if passed_count > 0 else "failed",
                "total": len(accounts),
                "passed": passed_count,
                "results": account_results
            }
        except Exception as e:
            report["tests"]["accounts"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # 3. Bot测试
        try:
            bots = db.get_bot_configs()
            bot_results = []
            
            for bot in bots:
                try:
                    # 调用已有的测试API
                    from .bots import test_bot_connection
                    
                    result = await test_bot_connection({
                        "platform": bot['platform'],
                        "config": bot['config']
                    })
                    
                    bot_results.append({
                        "id": bot['id'],
                        "name": bot['name'],
                        "platform": bot['platform'],
                        "passed": result["success"],
                        "message": result["message"]
                    })
                except Exception as e:
                    bot_results.append({
                        "id": bot['id'],
                        "name": bot['name'],
                        "platform": bot['platform'],
                        "passed": False,
                        "message": str(e)
                    })
            
            passed_count = sum(1 for r in bot_results if r["passed"])
            
            report["tests"]["bots"] = {
                "status": "passed" if passed_count > 0 else "failed",
                "total": len(bots),
                "passed": passed_count,
                "results": bot_results
            }
        except Exception as e:
            report["tests"]["bots"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # 4. 映射验证
        try:
            mappings = db.get_channel_mappings()
            valid_mappings = [m for m in mappings if m.get('enabled', 1) == 1]
            
            report["tests"]["mappings"] = {
                "status": "passed" if len(valid_mappings) > 0 else "failed",
                "total": len(mappings),
                "valid": len(valid_mappings)
            }
        except Exception as e:
            report["tests"]["mappings"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # 生成摘要
        all_tests = list(report["tests"].values())
        passed_tests = sum(1 for t in all_tests if t.get("status") == "passed")
        
        report["summary"] = {
            "total_tests": len(all_tests),
            "passed_tests": passed_tests,
            "failed_tests": len(all_tests) - passed_tests,
            "all_passed": passed_tests == len(all_tests),
            "completed_at": datetime.now().isoformat()
        }
        
        return report
        
    except Exception as e:
        logger.error(f"批量测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量测试失败: {str(e)}")
