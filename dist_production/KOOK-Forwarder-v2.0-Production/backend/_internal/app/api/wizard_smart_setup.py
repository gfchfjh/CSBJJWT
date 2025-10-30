"""
智能向导设置API - 快速配置
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from datetime import datetime
from ..database import db
from ..kook.scraper import scraper_manager
from ..processors.smart_mapping_ultimate import smart_mapping_engine
from ..utils.logger import logger
from ..utils.cookie_parser_ultimate import cookie_parser_ultimate

router = APIRouter(prefix="/api/wizard/smart", tags=["智能向导"])


class SmartSetupRequest(BaseModel):
    """智能配置请求"""
    cookie: str  # Cookie字符串
    target_platforms: List[str] = ["discord"]  # 默认只配置Discord
    auto_mapping: bool = True  # 自动智能映射
    skip_testing: bool = False  # 跳过测试步骤


class CookieValidationRequest(BaseModel):
    """Cookie验证请求"""
    cookie: str


@router.post("/validate-cookie")
async def validate_cookie(request: CookieValidationRequest):
    """
    验证Cookie格式和有效性
    
    Returns:
        {
            "valid": True/False,
            "count": 15,  # Cookie数量
            "expires": "2025-12-31",  # 最早过期时间
            "domain": "kookapp.cn",
            "email": "user@example.com",  # 如果能识别
            "warnings": ["某些Cookie即将过期"]
        }
    """
    try:
        # 解析Cookie
        cookies = cookie_parser_ultimate.parse(request.cookie)
        
        if not cookies:
            return {
                "valid": False,
                "message": "无法解析Cookie，请检查格式"
            }
        
        # 验证Cookie
        is_valid = cookie_parser_ultimate.validate(cookies)
        
        if not is_valid:
            return {
                "valid": False,
                "message": "Cookie验证失败，缺少必要字段"
            }
        
        # 提取信息
        domain = None
        earliest_expires = None
        warnings = []
        
        for cookie in cookies:
            # 检查域名
            if cookie.get('domain'):
                domain = cookie['domain'].replace('.', '')
            
            # 检查过期时间
            if cookie.get('expires'):
                try:
                    expires_timestamp = cookie['expires']
                    if isinstance(expires_timestamp, (int, float)):
                        expires_date = datetime.fromtimestamp(expires_timestamp)
                        
                        if earliest_expires is None or expires_date < earliest_expires:
                            earliest_expires = expires_date
                        
                        # 检查是否即将过期（7天内）
                        days_left = (expires_date - datetime.now()).days
                        if 0 < days_left < 7:
                            warnings.append(f"部分Cookie将在{days_left}天后过期")
                except:
                    pass
        
        # 尝试识别邮箱（从Cookie中）
        email = None
        for cookie in cookies:
            if cookie.get('name', '').lower() in ['email', 'user_email', 'username']:
                email = cookie.get('value')
                break
        
        return {
            "valid": True,
            "count": len(cookies),
            "expires": earliest_expires.strftime("%Y-%m-%d") if earliest_expires else None,
            "domain": domain,
            "email": email,
            "warnings": warnings
        }
        
    except ValueError as e:
        return {
            "valid": False,
            "message": f"Cookie格式错误: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Cookie验证异常: {str(e)}")
        return {
            "valid": False,
            "message": f"验证失败: {str(e)}"
        }


@router.post("/quick-setup")
async def quick_setup(request: SmartSetupRequest, background_tasks: BackgroundTasks):
    """
    一键快速配置
    
    流程:
    1. 验证Cookie → 2. 创建账号 → 3. 启动抓取器 
    → 4. 获取服务器/频道 → 5. 智能映射 → 6. 返回配置摘要
    
    预计耗时: 30-60秒
    """
    try:
        logger.info("开始快速配置流程...")
        
        # 阶段1: Cookie验证（3秒）
        logger.info("阶段1: 验证Cookie...")
        cookies = cookie_parser_ultimate.parse(request.cookie)
        
        if not cookie_parser_ultimate.validate(cookies):
            raise HTTPException(400, "Cookie验证失败，请检查格式")
        
        logger.info(f"✅ Cookie验证成功，共{len(cookies)}个Cookie")
        
        # 阶段2: 创建账号（1秒）
        logger.info("阶段2: 创建账号...")
        
        # 生成自动邮箱
        auto_email = f"auto_{int(datetime.now().timestamp())}@kook.com"
        
        account_id = db.add_account(
            email=auto_email,
            cookie=json.dumps(cookies)
        )
        
        logger.info(f"✅ 账号创建成功，ID: {account_id}")
        
        # 阶段3: 启动抓取器（5-10秒）
        logger.info("阶段3: 启动KOOK抓取器...")
        
        await scraper_manager.start_scraper(
            account_id=account_id,
            cookie=json.dumps(cookies)
        )
        
        # 等待连接成功（最多15秒）
        connected = False
        for i in range(15):
            await asyncio.sleep(1)
            account = db.get_account(account_id)
            if account and account['status'] == 'online':
                connected = True
                logger.info(f"✅ 抓取器连接成功（耗时{i+1}秒）")
                break
        
        if not connected:
            raise HTTPException(500, "账号连接超时，请检查Cookie是否有效或网络连接")
        
        # 阶段4: 获取服务器和频道（10-20秒）
        logger.info("阶段4: 获取服务器和频道列表...")
        
        scraper = scraper_manager.scrapers.get(account_id)
        if not scraper:
            raise HTTPException(500, "抓取器未找到")
        
        # 获取服务器
        servers = await scraper.get_servers()
        logger.info(f"✅ 找到 {len(servers)} 个服务器")
        
        # 获取频道（快速模式只处理前5个服务器的文本频道）
        all_channels = []
        for i, server in enumerate(servers[:5]):
            try:
                channels = await scraper.get_channels(server['id'])
                text_channels = [
                    {
                        'server_id': server['id'],
                        'server_name': server['name'],
                        'channel_id': ch['id'],
                        'channel_name': ch['name'],
                        'channel_type': ch.get('type', 'text')
                    }
                    for ch in channels if ch.get('type') == 'text'
                ]
                all_channels.extend(text_channels)
                logger.info(f"  服务器 {i+1}/{min(len(servers), 5)}: {server['name']} - {len(text_channels)}个文本频道")
            except Exception as e:
                logger.warning(f"  获取服务器 {server['name']} 的频道失败: {str(e)}")
                continue
        
        logger.info(f"✅ 共获取 {len(all_channels)} 个文本频道")
        
        # 阶段5: 智能映射（如果启用）
        mappings_created = 0
        
        if request.auto_mapping and 'discord' in request.target_platforms:
            logger.info("阶段5: 创建智能映射...")
            
            # 获取Discord Bot配置
            bot_configs = db.get_bot_configs(platform='discord')
            
            if bot_configs:
                default_bot = bot_configs[0]
                logger.info(f"使用Bot: {default_bot['name']}")
                
                # 为每个频道创建智能映射
                for ch in all_channels[:20]:  # 快速模式最多映射20个频道
                    try:
                        # 智能匹配目标频道名称
                        suggestions = smart_mapping_engine.get_suggestions(
                            ch['channel_name'],
                            'discord'
                        )
                        
                        if suggestions and suggestions[0]['confidence'] > 0.7:
                            # 自动创建高置信度映射
                            db.add_channel_mapping(
                                kook_server_id=ch['server_id'],
                                kook_channel_id=ch['channel_id'],
                                kook_channel_name=ch['channel_name'],
                                target_platform='discord',
                                target_bot_id=default_bot['id'],
                                target_channel_id=suggestions[0]['id']
                            )
                            mappings_created += 1
                            logger.debug(f"  映射: {ch['channel_name']} → {suggestions[0]['name']}")
                    except Exception as e:
                        logger.warning(f"  创建映射失败: {str(e)}")
                        continue
                
                logger.info(f"✅ 创建了 {mappings_created} 个智能映射")
            else:
                logger.warning("未找到Discord Bot配置，跳过自动映射")
        
        # 阶段6: 返回配置摘要
        logger.info("✅ 快速配置完成！")
        
        return {
            "success": True,
            "account_id": account_id,
            "servers_found": len(servers),
            "channels_found": len(all_channels),
            "mappings_created": mappings_created,
            "estimated_setup_time": "45秒",
            "next_step": "配置转发目标平台",
            "servers": servers[:5],  # 返回前5个服务器信息
            "channels": all_channels[:20]  # 返回前20个频道信息
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快速配置失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"配置失败: {str(e)}")


@router.get("/setup-status/{account_id}")
async def get_setup_status(account_id: int):
    """
    获取配置状态（用于前端轮询）
    
    Returns:
        {
            "stage": "connecting",  # connecting/loading_servers/mapping/completed
            "progress": 60,  # 0-100
            "message": "正在获取服务器列表...",
            "details": {...}
        }
    """
    try:
        # 从数据库或缓存获取状态
        account = db.get_account(account_id)
        
        if not account:
            raise HTTPException(404, "账号不存在")
        
        # 简化实现：根据账号状态返回进度
        if account['status'] == 'offline':
            return {
                "stage": "connecting",
                "progress": 30,
                "message": "正在连接KOOK..."
            }
        elif account['status'] == 'online':
            # 检查是否有映射
            mappings = db.get_channel_mappings()
            
            if len(mappings) > 0:
                return {
                    "stage": "completed",
                    "progress": 100,
                    "message": "配置完成",
                    "details": {
                        "mappings": len(mappings)
                    }
                }
            else:
                return {
                    "stage": "mapping",
                    "progress": 70,
                    "message": "正在创建频道映射..."
                }
        else:
            return {
                "stage": "unknown",
                "progress": 0,
                "message": f"未知状态: {account['status']}"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置状态失败: {str(e)}")
        raise HTTPException(500, f"获取状态失败: {str(e)}")
