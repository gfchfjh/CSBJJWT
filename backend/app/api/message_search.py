"""
✅ P1-1深度优化：消息搜索API

功能：
- 全文搜索消息内容
- 高级筛选（时间范围、平台、状态等）
- 分页支持
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from ..database import db
from ..utils.logger import logger

router = APIRouter(prefix="/api/message-search", tags=["message-search"])


class SearchFilter(BaseModel):
    """搜索过滤器"""
    keyword: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    sender: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


@router.post("/search")
async def search_messages(
    filters: SearchFilter,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """
    搜索消息
    
    Args:
        filters: 搜索过滤器
        page: 页码
        page_size: 每页数量
    
    Returns:
        搜索结果
    """
    try:
        # 构建SQL查询
        sql_conditions = []
        sql_params = []
        
        # 关键词搜索（全文）
        if filters.keyword:
            sql_conditions.append(
                "(content LIKE ? OR sender_name LIKE ? OR kook_channel_id LIKE ?)"
            )
            keyword_pattern = f"%{filters.keyword}%"
            sql_params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        # 平台筛选
        if filters.platform:
            sql_conditions.append("target_platform = ?")
            sql_params.append(filters.platform)
        
        # 状态筛选
        if filters.status:
            sql_conditions.append("status = ?")
            sql_params.append(filters.status)
        
        # 发送者筛选
        if filters.sender:
            sql_conditions.append("sender_name LIKE ?")
            sql_params.append(f"%{filters.sender}%")
        
        # 时间范围
        if filters.date_from:
            sql_conditions.append("created_at >= ?")
            sql_params.append(filters.date_from)
        
        if filters.date_to:
            sql_conditions.append("created_at <= ?")
            sql_params.append(filters.date_to)
        
        # 组装WHERE子句
        where_clause = " AND ".join(sql_conditions) if sql_conditions else "1=1"
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as count FROM message_logs WHERE {where_clause}"
        total_count = db.execute(count_sql, sql_params).fetchone()['count']
        
        # 查询结果
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT * FROM message_logs 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        sql_params.extend([page_size, offset])
        
        results = db.execute(query_sql, sql_params).fetchall()
        
        # 转换为字典列表
        messages = [dict(row) for row in results]
        
        return {
            'messages': messages,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"搜索消息失败: {str(e)}")
        return {
            'messages': [],
            'total': 0,
            'page': page,
            'page_size': page_size,
            'total_pages': 0,
            'error': str(e)
        }


@router.get("/suggestions")
async def get_search_suggestions(keyword: str):
    """
    获取搜索建议
    
    Args:
        keyword: 关键词
    
    Returns:
        建议列表
    """
    try:
        # 搜索最近的发送者
        sender_sql = """
            SELECT DISTINCT sender_name
            FROM message_logs
            WHERE sender_name LIKE ?
            ORDER BY created_at DESC
            LIMIT 10
        """
        senders = db.execute(sender_sql, (f"%{keyword}%",)).fetchall()
        
        # 搜索最近的频道
        channel_sql = """
            SELECT DISTINCT kook_channel_id
            FROM message_logs
            WHERE kook_channel_id LIKE ?
            ORDER BY created_at DESC
            LIMIT 10
        """
        channels = db.execute(channel_sql, (f"%{keyword}%",)).fetchall()
        
        return {
            'senders': [row['sender_name'] for row in senders],
            'channels': [row['kook_channel_id'] for row in channels]
        }
        
    except Exception as e:
        logger.error(f"获取搜索建议失败: {str(e)}")
        return {
            'senders': [],
            'channels': []
        }
