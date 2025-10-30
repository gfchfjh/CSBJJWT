"""
智能频道映射API - 统一版
使用IntelligentChannelMatcher进行智能推荐
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..utils.channel_matcher import channel_matcher
from ..utils.logger import logger
from ..database import db

router = APIRouter(prefix="/api/smart-mapping", tags=["智能映射"])


class RecommendRequest(BaseModel):
    """推荐请求"""
    kook_channels: Optional[List[Dict]] = None  # 如果不提供，则自动获取
    target_channels: Optional[List[Dict]] = None  # 如果不提供，则从已配置的Bot获取
    min_confidence: float = 0.5  # 最小置信度阈值


class RecommendResponse(BaseModel):
    """推荐响应"""
    success: bool
    recommendations: List[Dict]
    stats: Dict[str, Any]


class TestMatchRequest(BaseModel):
    """测试匹配请求"""
    source: str
    target: str


class TestMatchResponse(BaseModel):
    """测试匹配响应"""
    success: bool
    scores: Dict[str, float]
    final_score: float
    recommended: bool


@router.post("/recommend", response_model=RecommendResponse)
async def get_smart_recommendations(request: RecommendRequest):
    """
    智能推荐频道映射
    
    根据KOOK频道名称，自动推荐最匹配的目标平台频道
    """
    try:
        # 1. 获取KOOK频道列表
        if request.kook_channels:
            kook_channels = request.kook_channels
        else:
            kook_channels = await _fetch_kook_channels()
        
        if not kook_channels:
            return RecommendResponse(
                success=False,
                recommendations=[],
                stats={'error': '未找到KOOK频道'}
            )
        
        # 2. 获取目标频道列表
        if request.target_channels:
            target_channels = request.target_channels
        else:
            target_channels = await _fetch_target_channels()
        
        if not target_channels:
            return RecommendResponse(
                success=False,
                recommendations=[],
                stats={'error': '未配置任何Bot'}
            )
        
        # 3. 执行智能推荐
        recommendations = channel_matcher.batch_recommend(
            kook_channels=kook_channels,
            target_channels=target_channels,
            min_confidence=request.min_confidence
        )
        
        # 4. 统计信息
        stats = {
            'kook_channels_count': len(kook_channels),
            'target_channels_count': len(target_channels),
            'recommendations_count': len(recommendations),
            'total_mappings': sum(len(r['recommended_targets']) for r in recommendations),
            'coverage_rate': len(recommendations) / len(kook_channels) if kook_channels else 0
        }
        
        logger.info(f"智能推荐完成: {stats}")
        
        return RecommendResponse(
            success=True,
            recommendations=recommendations,
            stats=stats
        )
    
    except Exception as e:
        logger.error(f"智能推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-match", response_model=TestMatchResponse)
async def test_channel_match(request: TestMatchRequest):
    """
    测试两个频道的匹配度
    
    用于调试和验证匹配算法
    """
    try:
        # 计算各项分数
        exact_score = channel_matcher.exact_match(request.source, request.target)
        similarity_score = channel_matcher.calculate_similarity(request.source, request.target)
        keyword_score = channel_matcher.keyword_match(request.source, request.target)
        
        # 综合评分
        final_score = (
            exact_score * 0.5 +
            similarity_score * 0.3 +
            keyword_score * 0.2
        )
        
        return TestMatchResponse(
            success=True,
            scores={
                'exact_match': exact_score,
                'similarity': similarity_score,
                'keyword': keyword_score
            },
            final_score=final_score,
            recommended=final_score >= 0.5
        )
    
    except Exception as e:
        logger.error(f"测试匹配失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translation-dict")
async def get_translation_dictionary():
    """
    获取中英文翻译词典
    
    返回系统支持的所有中英文映射规则
    """
    return {
        'success': True,
        'chinese_to_english': channel_matcher.TRANSLATION_MAP,
        'english_to_chinese': channel_matcher.REVERSE_TRANSLATION_MAP,
        'total_rules': len(channel_matcher.TRANSLATION_MAP)
    }


@router.post("/apply-recommendations")
async def apply_recommended_mappings(recommendations: List[Dict]):
    """
    应用推荐的映射关系
    
    将推荐结果保存到数据库
    """
    try:
        applied_count = 0
        
        for rec in recommendations:
            kook_channel_id = rec['kook_channel_id']
            kook_server_id = rec.get('kook_server_id')
            kook_channel_name = rec['kook_channel_name']
            
            for target in rec['recommended_targets']:
                # 插入映射关系
                db.execute("""
                    INSERT INTO channel_mappings 
                    (kook_server_id, kook_channel_id, kook_channel_name, 
                     target_platform, target_bot_id, target_channel_id, enabled)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (
                    kook_server_id,
                    kook_channel_id,
                    kook_channel_name,
                    target['platform'],
                    target['channel_id'],  # TODO: 需要找到对应的bot_id
                    target['channel_id']
                ))
                
                applied_count += 1
        
        db.commit()
        
        logger.info(f"应用智能推荐: {applied_count}个映射关系已保存")
        
        return {
            'success': True,
            'applied_count': applied_count
        }
    
    except Exception as e:
        logger.error(f"应用推荐失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 辅助函数 ==========

async def _fetch_kook_channels() -> List[Dict]:
    """
    获取所有KOOK频道
    
    从服务器发现API获取
    """
    try:
        # 查询已发现的服务器和频道
        # TODO: 实现服务器发现API的调用
        
        # 临时：从数据库获取已映射的频道
        channels = []
        rows = db.execute("""
            SELECT DISTINCT kook_server_id, kook_channel_id, kook_channel_name
            FROM channel_mappings
        """).fetchall()
        
        for row in rows:
            channels.append({
                'server_id': row['kook_server_id'],
                'id': row['kook_channel_id'],
                'name': row['kook_channel_name']
            })
        
        return channels
    
    except Exception as e:
        logger.error(f"获取KOOK频道失败: {e}")
        return []


async def _fetch_target_channels() -> List[Dict]:
    """
    获取所有目标平台的频道/Bot
    
    从已配置的Bot中提取
    """
    try:
        channels = []
        
        # 获取所有已配置的Bot
        bots = db.get_bot_configs()
        
        for bot in bots:
            platform = bot['platform']
            config = bot['config']
            
            if platform == 'discord':
                # Discord Webhook
                channels.append({
                    'id': str(bot['id']),
                    'name': bot['name'],
                    'platform': 'discord'
                })
            
            elif platform == 'telegram':
                # Telegram Bot
                channels.append({
                    'id': str(bot['id']),
                    'name': bot['name'],
                    'platform': 'telegram'
                })
            
            elif platform == 'feishu':
                # 飞书应用
                channels.append({
                    'id': str(bot['id']),
                    'name': bot['name'],
                    'platform': 'feishu'
                })
        
        return channels
    
    except Exception as e:
        logger.error(f"获取目标频道失败: {e}")
        return []
