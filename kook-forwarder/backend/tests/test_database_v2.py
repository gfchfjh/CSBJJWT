"""
数据库模块v2测试
版本: v6.0.0
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from app.database_v2 import DatabaseV2


@pytest.fixture
async def test_db(tmp_path):
    """测试数据库fixture"""
    db_path = tmp_path / "test.db"
    db = DatabaseV2(db_path)
    yield db
    
    # 清理
    if db_path.exists():
        db_path.unlink()


class TestDatabaseV2:
    """数据库v2测试类"""
    
    @pytest.mark.asyncio
    async def test_get_message_logs_basic(self, test_db):
        """测试基础日志查询"""
        # 添加测试数据
        test_messages = [
            {
                'kook_message_id': f'msg_{i}',
                'kook_channel_id': 'channel_1',
                'content': f'测试消息{i}',
                'status': 'success',
                'latency_ms': 100
            }
            for i in range(10)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 查询
        logs, total = await test_db.get_message_logs(limit=5, offset=0)
        
        assert total == 10
        assert len(logs) == 5
    
    @pytest.mark.asyncio
    async def test_get_message_logs_pagination(self, test_db):
        """测试分页查询"""
        # 添加测试数据
        test_messages = [
            {
                'kook_message_id': f'msg_{i}',
                'kook_channel_id': 'channel_1',
                'content': f'测试消息{i}',
                'status': 'success'
            }
            for i in range(100)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 第1页
        logs_page1, total = await test_db.get_message_logs(limit=20, offset=0)
        assert len(logs_page1) == 20
        assert total == 100
        
        # 第2页
        logs_page2, _ = await test_db.get_message_logs(limit=20, offset=20)
        assert len(logs_page2) == 20
        
        # 确保不重复
        ids_page1 = {log['kook_message_id'] for log in logs_page1}
        ids_page2 = {log['kook_message_id'] for log in logs_page2}
        assert len(ids_page1 & ids_page2) == 0
    
    @pytest.mark.asyncio
    async def test_get_message_logs_filter_by_status(self, test_db):
        """测试按状态过滤"""
        # 添加不同状态的消息
        test_messages = [
            {'kook_message_id': f'msg_success_{i}', 'kook_channel_id': 'ch1', 'content': 'test', 'status': 'success'}
            for i in range(10)
        ] + [
            {'kook_message_id': f'msg_failed_{i}', 'kook_channel_id': 'ch1', 'content': 'test', 'status': 'failed'}
            for i in range(5)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 查询成功消息
        success_logs, success_total = await test_db.get_message_logs(status='success')
        assert success_total == 10
        
        # 查询失败消息
        failed_logs, failed_total = await test_db.get_message_logs(status='failed')
        assert failed_total == 5
    
    @pytest.mark.asyncio
    async def test_get_message_logs_filter_by_channel(self, test_db):
        """测试按频道过滤"""
        # 添加不同频道的消息
        test_messages = [
            {'kook_message_id': f'msg_ch1_{i}', 'kook_channel_id': 'channel_1', 'content': 'test', 'status': 'success'}
            for i in range(10)
        ] + [
            {'kook_message_id': f'msg_ch2_{i}', 'kook_channel_id': 'channel_2', 'content': 'test', 'status': 'success'}
            for i in range(15)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 查询channel_1
        logs_ch1, total_ch1 = await test_db.get_message_logs(channel_id='channel_1')
        assert total_ch1 == 10
        
        # 查询channel_2
        logs_ch2, total_ch2 = await test_db.get_message_logs(channel_id='channel_2')
        assert total_ch2 == 15
    
    @pytest.mark.asyncio
    async def test_query_performance(self, test_db):
        """测试查询性能（目标<100ms）"""
        import time
        
        # 插入1000条记录
        test_messages = [
            {
                'kook_message_id': f'msg_{i}',
                'kook_channel_id': f'channel_{i % 10}',
                'content': f'测试消息{i}',
                'status': 'success',
                'latency_ms': 100
            }
            for i in range(1000)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 测试查询性能
        start_time = time.time()
        logs, total = await test_db.get_message_logs(limit=100, offset=0)
        query_time = (time.time() - start_time) * 1000
        
        assert total == 1000
        assert len(logs) == 100
        assert query_time < 100  # 应该<100ms
        
        print(f"查询1000条记录耗时: {query_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_batch_insert_performance(self, test_db):
        """测试批量插入性能（目标<200ms/100条）"""
        import time
        
        test_messages = [
            {
                'kook_message_id': f'batch_msg_{i}',
                'kook_channel_id': 'channel_1',
                'content': f'批量消息{i}',
                'status': 'pending'
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        inserted = await test_db.add_message_log_batch(test_messages)
        insert_time = (time.time() - start_time) * 1000
        
        assert inserted == 100
        assert insert_time < 200  # 应该<200ms
        
        print(f"批量插入100条耗时: {insert_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cleanup_old_logs(self, test_db):
        """测试清理旧日志"""
        # 添加旧消息
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        
        conn = await test_db.get_async_connection().__aenter__()
        
        await conn.execute("""
            INSERT INTO message_logs 
            (kook_message_id, kook_channel_id, content, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ('old_msg', 'ch1', 'old', 'success', old_date))
        
        await conn.commit()
        await conn.close()
        
        # 清理7天前的日志
        deleted = await test_db.cleanup_old_logs(days=7)
        
        assert deleted == 1
    
    @pytest.mark.asyncio
    async def test_get_stats_summary(self, test_db):
        """测试统计摘要"""
        # 添加测试数据
        test_messages = [
            {'kook_message_id': f'msg_{i}', 'kook_channel_id': 'ch1', 'content': 'test', 
             'status': 'success', 'latency_ms': 100 + i}
            for i in range(50)
        ] + [
            {'kook_message_id': f'msg_failed_{i}', 'kook_channel_id': 'ch2', 'content': 'test', 
             'status': 'failed', 'latency_ms': 200}
            for i in range(10)
        ]
        
        await test_db.add_message_log_batch(test_messages)
        
        # 获取统计
        stats = await test_db.get_stats_summary(hours=24)
        
        assert stats['total'] == 60
        assert stats['success'] == 50
        assert stats['failed'] == 10
        assert stats['success_rate'] == pytest.approx(83.33, rel=0.1)
        assert stats['avg_latency_ms'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
