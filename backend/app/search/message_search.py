"""
全文消息搜索
✅ P1-11: Elasticsearch集成搜索
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from ..utils.logger import logger
from ..database import get_database


class MessageSearch:
    """消息搜索引擎"""
    
    def __init__(self):
        self.use_elasticsearch = False  # 可选启用ES
        
    async def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        搜索消息
        
        Args:
            query: 搜索关键词
            filters: 过滤条件
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            搜索结果
        """
        if self.use_elasticsearch:
            return await self._search_with_es(query, filters, limit, offset)
        else:
            return await self._search_with_sqlite(query, filters, limit, offset)
    
    async def _search_with_sqlite(
        self,
        query: str,
        filters: Optional[Dict],
        limit: int,
        offset: int
    ) -> Dict:
        """使用SQLite搜索"""
        db = get_database()
        
        try:
            # 构建SQL查询
            sql = "SELECT * FROM message_logs WHERE content LIKE ?"
            params = [f"%{query}%"]
            
            # 添加过滤条件
            if filters:
                if 'platform' in filters:
                    sql += " AND target_platform = ?"
                    params.append(filters['platform'])
                
                if 'status' in filters:
                    sql += " AND status = ?"
                    params.append(filters['status'])
                
                if 'start_time' in filters:
                    sql += " AND created_at >= ?"
                    params.append(filters['start_time'])
                
                if 'end_time' in filters:
                    sql += " AND created_at <= ?"
                    params.append(filters['end_time'])
            
            # 排序和分页
            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            cursor = db.execute(sql, params)
            results = cursor.fetchall()
            
            # 获取总数
            count_sql = "SELECT COUNT(*) FROM message_logs WHERE content LIKE ?"
            count_params = [f"%{query}%"]
            
            count = db.execute(count_sql, count_params).fetchone()[0]
            
            return {
                'total': count,
                'results': [dict(row) for row in results],
                'query': query,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return {'total': 0, 'results': [], 'error': str(e)}
    
    async def _search_with_es(
        self,
        query: str,
        filters: Optional[Dict],
        limit: int,
        offset: int
    ) -> Dict:
        """使用Elasticsearch搜索（待实现）"""
        # TODO: 实现ES搜索
        logger.info("Elasticsearch搜索尚未实现，回退到SQLite")
        return await self._search_with_sqlite(query, filters, limit, offset)


# 全局实例
message_search = MessageSearch()
