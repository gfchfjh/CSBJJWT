"""
消息API - 提供消息查询功能
✅ 新增：最近消息列表
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..database import db
from ..utils.logger import logger

router = APIRouter(prefix="/api/messages", tags=["messages"])


class Message(BaseModel):
    """消息模型"""
    id: int
    content: str
    author: str
    source_channel: str
    target_platform: str
    status: str
    created_at: str
    latency: Optional[float] = None
    error_message: Optional[str] = None


@router.get("/recent", response_model=List[Message])
async def get_recent_messages(limit: int = Query(10, ge=1, le=100)):
    """
    获取最近的消息列表
    
    Args:
        limit: 返回数量限制 (1-100)
        
    Returns:
        最近消息列表
    """
    try:
        # 尝试从数据库获取最近消息
        try:
            rows = db.execute("""
                SELECT 
                    id,
                    content,
                    author_name as author,
                    source_channel_name as source_channel,
                    target_platform,
                    status,
                    created_at,
                    latency,
                    error_message
                FROM messages
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            messages = []
            for row in rows:
                messages.append(Message(
                    id=row['id'],
                    content=row['content'][:100] + ('...' if len(row.get('content', '')) > 100 else ''),
                    author=row.get('author') or 'Unknown',
                    source_channel=row.get('source_channel') or 'Unknown',
                    target_platform=row.get('target_platform') or 'Unknown',
                    status=row.get('status') or 'pending',
                    created_at=row.get('created_at') or '',
                    latency=row.get('latency'),
                    error_message=row.get('error_message')
                ))
            
            return messages
            
        except Exception as e:
            logger.warning(f"messages表不存在或查询失败: {str(e)}")
            # 返回空列表（数据库还没有消息表）
            return []
        
    except Exception as e:
        logger.error(f"获取最近消息失败: {str(e)}")
        return []


@router.get("/{message_id}", response_model=Message)
async def get_message(message_id: int):
    """
    获取单条消息详情
    
    Args:
        message_id: 消息ID
        
    Returns:
        消息详情
    """
    try:
        row = db.execute("""
            SELECT 
                id,
                content,
                author_name as author,
                source_channel_name as source_channel,
                target_platform,
                status,
                created_at,
                latency,
                error_message
            FROM messages
            WHERE id = ?
        """, (message_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        return Message(
            id=row['id'],
            content=row.get('content') or '',
            author=row.get('author') or 'Unknown',
            source_channel=row.get('source_channel') or 'Unknown',
            target_platform=row.get('target_platform') or 'Unknown',
            status=row.get('status') or 'pending',
            created_at=row.get('created_at') or '',
            latency=row.get('latency'),
            error_message=row.get('error_message')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
