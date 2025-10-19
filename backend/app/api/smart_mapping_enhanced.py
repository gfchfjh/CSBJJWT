"""
增强版智能频道映射API
集成真实平台API，提供更精确的映射建议
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
from ..database import db
from ..utils.logger import logger


router = APIRouter(prefix="/api/smart-mapping-enhanced", tags=["smart-mapping-enhanced"])


class EnhancedSmartMappingRequest(BaseModel):
    account_id: int
    kook_servers: List[Dict[str, Any]]  # KOOK服务器和频道列表
    target_bots: List[Dict[str, Any]]   # 目标平台Bot配置


class MappingSuggestion(BaseModel):
    kook_server_id: str
    kook_server_name: str
    kook_channel_id: str
    kook_channel_name: str
    target_platform: str
    target_bot_id: int
    target_channel_id: str
    target_channel_name: str
    confidence: float  # 匹配置信度 0-1
    reason: str  # 匹配原因


def normalize_name(name: str) -> str:
    """标准化频道名称"""
    name = re.sub(r'^[#*\-\s]+', '', name)
    name = name.lower()
    name = name.replace(' ', '').replace('-', '').replace('_', '')
    return name


def calculate_similarity(name1: str, name2: str) -> float:
    """计算两个名称的相似度"""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if norm1 == norm2:
        return 1.0
    
    if norm1 in norm2 or norm2 in norm1:
        min_len = min(len(norm1), len(norm2))
        max_len = max(len(norm1), len(norm2))
        return min_len / max_len * 0.8
    
    set1 = set(norm1)
    set2 = set(norm2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union * 0.6 if union > 0 else 0.0


def match_channel_name(kook_channel_name: str, target_channel_candidates: List[str]) -> tuple[Optional[str], float]:
    """从候选频道中匹配最佳目标频道"""
    best_match = None
    best_score = 0.0
    
    for candidate in target_channel_candidates:
        score = calculate_similarity(kook_channel_name, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate
    
    if best_score >= 0.5:
        return best_match, best_score
    
    return None, 0.0


@router.post("/suggest-with-real-api", response_model=List[MappingSuggestion])
async def suggest_mappings_with_real_api(request: EnhancedSmartMappingRequest):
    """
    ✅ 使用真实API的智能映射建议
    
    调用Discord/Telegram/飞书的真实API获取频道列表，
    然后进行智能匹配
    
    Args:
        request: 包含KOOK服务器列表和目标Bot配置
        
    Returns:
        映射建议列表
    """
    try:
        from ..utils.platform_api_client import (
            discord_api_client,
            telegram_api_client,
            feishu_api_client
        )
        
        suggestions = []
        
        # ✅ 第一步：获取所有目标平台的真实频道列表
        logger.info("=" * 50)
        logger.info("开始增强版智能映射（使用真实API）")
        logger.info("=" * 50)
        
        target_channels_by_bot = {}  # {bot_id: {platform, channels, config}}
        
        for bot in request.target_bots:
            platform = bot.get('platform')
            bot_id = bot.get('id')
            config = bot.get('config', {})
            bot_name = bot.get('name', f'{platform} Bot')
            
            logger.info(f"\n📡 正在获取 [{platform}] {bot_name} (ID:{bot_id}) 的频道列表...")
            
            channels = []
            
            # ✅ 调用真实API获取频道列表
            try:
                if platform == 'discord':
                    webhook_url = config.get('webhook_url', '')
                    if webhook_url:
                        channels = await discord_api_client.get_channels_from_webhook(webhook_url)
                        if channels:
                            logger.info(f"  ✅ Discord: 成功获取到 {len(channels)} 个频道")
                            for ch in channels:
                                logger.debug(f"     - {ch['name']} (ID: {ch['id']})")
                        else:
                            logger.warning(f"  ⚠️ Discord: 未获取到任何频道")
                    else:
                        logger.warning(f"  ⚠️ Discord: Webhook URL为空")
                
                elif platform == 'telegram':
                    bot_token = config.get('bot_token', '')
                    if bot_token:
                        channels = await telegram_api_client.get_bot_chats(bot_token)
                        if channels:
                            logger.info(f"  ✅ Telegram: 成功获取到 {len(channels)} 个群组")
                            for ch in channels:
                                logger.debug(f"     - {ch['name']} (ID: {ch['id']})")
                        else:
                            logger.warning(f"  ⚠️ Telegram: 未获取到任何群组（Bot可能未被添加到群组）")
                    else:
                        logger.warning(f"  ⚠️ Telegram: Bot Token为空")
                
                elif platform == 'feishu':
                    app_id = config.get('app_id', '')
                    app_secret = config.get('app_secret', '')
                    if app_id and app_secret:
                        channels = await feishu_api_client.get_group_chats(app_id, app_secret)
                        if channels:
                            logger.info(f"  ✅ 飞书: 成功获取到 {len(channels)} 个群组")
                            for ch in channels[:5]:  # 只显示前5个
                                logger.debug(f"     - {ch['name']} (ID: {ch['id']})")
                            if len(channels) > 5:
                                logger.debug(f"     ... 以及其他 {len(channels)-5} 个群组")
                        else:
                            logger.warning(f"  ⚠️ 飞书: 未获取到任何群组")
                    else:
                        logger.warning(f"  ⚠️ 飞书: App ID或Secret为空")
                
            except Exception as api_error:
                logger.error(f"  ❌ 获取 {platform} Bot#{bot_id} 频道失败: {str(api_error)}")
                # 即使失败也继续处理其他Bot
            
            target_channels_by_bot[bot_id] = {
                'platform': platform,
                'bot_name': bot_name,
                'channels': channels,
                'config': config
            }
        
        # ✅ 第二步：遍历所有KOOK频道，进行智能匹配
        logger.info(f"\n🔍 开始智能匹配 KOOK频道...")
        logger.info("=" * 50)
        
        total_kook_channels = sum(len(server.get('channels', [])) for server in request.kook_servers)
        logger.info(f"待匹配的KOOK频道数量: {total_kook_channels}")
        
        match_count = 0
        
        for server in request.kook_servers:
            server_id = server.get('id')
            server_name = server.get('name')
            
            logger.info(f"\n📁 服务器: {server_name}")
            
            for channel in server.get('channels', []):
                kook_channel_name = channel.get('name', '')
                kook_channel_id = channel.get('id', '')
                
                logger.debug(f"  🔸 频道: {kook_channel_name}")
                
                # 对每个目标Bot进行匹配
                for bot_id, bot_data in target_channels_by_bot.items():
                    platform = bot_data['platform']
                    bot_name = bot_data['bot_name']
                    target_channels = bot_data['channels']
                    
                    if not target_channels:
                        continue
                    
                    # ✅ 使用真实的目标频道列表进行匹配
                    target_channel_names = [ch['name'] for ch in target_channels]
                    
                    # 执行匹配
                    best_match, confidence = match_channel_name(
                        kook_channel_name, 
                        target_channel_names
                    )
                    
                    if best_match and confidence >= 0.5:
                        # ✅ 找到匹配的目标频道对象
                        matched_channel = next(
                            (ch for ch in target_channels if ch['name'] == best_match),
                            None
                        )
                        
                        if matched_channel:
                            # 生成匹配原因
                            if confidence >= 0.9:
                                reason = f"完全匹配: '{kook_channel_name}' → '{best_match}'"
                                reason_emoji = "🎯"
                            elif confidence >= 0.7:
                                reason = f"高度相似: '{kook_channel_name}' → '{best_match}'"
                                reason_emoji = "✨"
                            else:
                                reason = f"部分匹配: '{kook_channel_name}' → '{best_match}'"
                                reason_emoji = "🔗"
                            
                            logger.info(f"    {reason_emoji} [{platform}] {bot_name}: {kook_channel_name} → {best_match} (置信度: {confidence:.2f})")
                            
                            suggestions.append(MappingSuggestion(
                                kook_server_id=server_id,
                                kook_server_name=server_name,
                                kook_channel_id=kook_channel_id,
                                kook_channel_name=kook_channel_name,
                                target_platform=platform,
                                target_bot_id=bot_id,
                                target_channel_id=matched_channel['id'],  # ✅ 真实的频道ID
                                target_channel_name=best_match,
                                confidence=confidence,
                                reason=reason
                            ))
                            
                            match_count += 1
        
        logger.info("\n" + "=" * 50)
        logger.info(f"✅ 智能映射完成！")
        logger.info(f"   - 处理了 {total_kook_channels} 个KOOK频道")
        logger.info(f"   - 生成了 {len(suggestions)} 条映射建议")
        logger.info(f"   - 匹配成功率: {match_count}/{total_kook_channels} = {match_count/total_kook_channels*100 if total_kook_channels > 0 else 0:.1f}%")
        logger.info("=" * 50)
        
        # 按置信度排序
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"❌ 增强版智能映射失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"智能映射失败: {str(e)}")


@router.get("/test-platform-api/{platform}")
async def test_platform_api(platform: str, bot_id: int):
    """
    测试目标平台API连接
    
    Args:
        platform: 平台名称 (discord/telegram/feishu)
        bot_id: Bot ID
        
    Returns:
        频道列表
    """
    try:
        from ..utils.platform_api_client import (
            discord_api_client,
            telegram_api_client,
            feishu_api_client
        )
        
        # 从数据库获取Bot配置
        bot = db.get_bot_config(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot配置不存在")
        
        config = bot.get('config', {})
        
        logger.info(f"测试 {platform} API连接...")
        
        if platform == 'discord':
            webhook_url = config.get('webhook_url', '')
            channels = await discord_api_client.get_channels_from_webhook(webhook_url)
            return {
                "platform": "Discord",
                "status": "success" if channels else "no_channels",
                "channels": channels,
                "count": len(channels)
            }
        
        elif platform == 'telegram':
            bot_token = config.get('bot_token', '')
            channels = await telegram_api_client.get_bot_chats(bot_token)
            return {
                "platform": "Telegram",
                "status": "success" if channels else "no_channels",
                "channels": channels,
                "count": len(channels),
                "tip": "如果为0，请确保Bot已被添加到群组并至少收到一条消息"
            }
        
        elif platform == 'feishu':
            app_id = config.get('app_id', '')
            app_secret = config.get('app_secret', '')
            channels = await feishu_api_client.get_group_chats(app_id, app_secret)
            return {
                "platform": "飞书",
                "status": "success" if channels else "no_channels",
                "channels": channels,
                "count": len(channels)
            }
        
        else:
            raise HTTPException(status_code=400, detail="不支持的平台")
            
    except Exception as e:
        logger.error(f"测试平台API失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
