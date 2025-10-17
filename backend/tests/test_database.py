"""
数据库操作测试
"""
import pytest
import tempfile
import os
from pathlib import Path
from backend.app.database import Database


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    # 创建临时文件
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # 创建数据库实例
    db = Database(Path(path))
    
    yield db
    
    # 清理
    if os.path.exists(path):
        os.unlink(path)


class TestDatabase:
    """数据库测试类"""
    
    def test_init_database(self, temp_db):
        """测试数据库初始化"""
        # 数据库文件应该存在
        assert temp_db.db_path.exists()
        
        # 获取所有表名
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        
        # 验证所有表都已创建
        expected_tables = [
            'accounts',
            'bot_configs',
            'channel_mappings',
            'filter_rules',
            'message_logs',
            'failed_messages',
            'system_config'
        ]
        
        for table in expected_tables:
            assert table in tables, f"表 {table} 未创建"
    
    def test_add_account(self, temp_db):
        """测试添加账号"""
        # 添加账号
        account_id = temp_db.add_account(
            email="test@example.com",
            password_encrypted="encrypted_password",
            cookie='[{"name": "test", "value": "test"}]'
        )
        
        # 验证ID
        assert account_id > 0
        
        # 获取账号
        accounts = temp_db.get_accounts()
        assert len(accounts) == 1
        assert accounts[0]['email'] == "test@example.com"
    
    def test_update_account_status(self, temp_db):
        """测试更新账号状态"""
        # 添加账号
        account_id = temp_db.add_account(email="test@example.com")
        
        # 更新状态
        temp_db.update_account_status(account_id, 'online')
        
        # 验证
        accounts = temp_db.get_accounts()
        assert accounts[0]['status'] == 'online'
        assert accounts[0]['last_active'] is not None
    
    def test_delete_account(self, temp_db):
        """测试删除账号"""
        # 添加账号
        account_id = temp_db.add_account(email="test@example.com")
        
        # 删除账号
        temp_db.delete_account(account_id)
        
        # 验证
        accounts = temp_db.get_accounts()
        assert len(accounts) == 0
    
    def test_add_bot_config(self, temp_db):
        """测试添加Bot配置"""
        # 添加Bot
        bot_id = temp_db.add_bot_config(
            platform='discord',
            name='测试Bot',
            config={'webhook_url': 'https://discord.com/api/webhooks/123'}
        )
        
        assert bot_id > 0
        
        # 获取Bot
        bots = temp_db.get_bot_configs()
        assert len(bots) == 1
        assert bots[0]['platform'] == 'discord'
        assert bots[0]['name'] == '测试Bot'
        assert bots[0]['config']['webhook_url'] == 'https://discord.com/api/webhooks/123'
    
    def test_get_bot_configs_by_platform(self, temp_db):
        """测试按平台获取Bot配置"""
        # 添加多个Bot
        temp_db.add_bot_config('discord', 'Discord Bot', {})
        temp_db.add_bot_config('telegram', 'Telegram Bot', {})
        temp_db.add_bot_config('discord', 'Discord Bot 2', {})
        
        # 获取Discord Bot
        discord_bots = temp_db.get_bot_configs('discord')
        assert len(discord_bots) == 2
        
        # 获取Telegram Bot
        telegram_bots = temp_db.get_bot_configs('telegram')
        assert len(telegram_bots) == 1
    
    def test_add_channel_mapping(self, temp_db):
        """测试添加频道映射"""
        # 先添加Bot
        bot_id = temp_db.add_bot_config('discord', '测试Bot', {})
        
        # 添加映射
        mapping_id = temp_db.add_channel_mapping(
            kook_server_id='123',
            kook_channel_id='456',
            kook_channel_name='公告',
            target_platform='discord',
            target_bot_id=bot_id,
            target_channel_id='789'
        )
        
        assert mapping_id > 0
        
        # 获取映射
        mappings = temp_db.get_channel_mappings()
        assert len(mappings) == 1
        assert mappings[0]['kook_channel_name'] == '公告'
    
    def test_get_channel_mappings_by_channel(self, temp_db):
        """测试按频道获取映射"""
        bot_id = temp_db.add_bot_config('discord', '测试Bot', {})
        
        # 添加多个映射
        temp_db.add_channel_mapping('123', '456', '公告', 'discord', bot_id, '789')
        temp_db.add_channel_mapping('123', '789', '活动', 'discord', bot_id, '101')
        
        # 获取特定频道的映射
        mappings = temp_db.get_channel_mappings('456')
        assert len(mappings) == 1
        assert mappings[0]['kook_channel_id'] == '456'
    
    def test_add_message_log(self, temp_db):
        """测试添加消息日志"""
        # 添加日志
        log_id = temp_db.add_message_log(
            kook_message_id='msg_123',
            kook_channel_id='ch_456',
            content='测试消息',
            message_type='text',
            sender_name='测试用户',
            target_platform='discord',
            target_channel='target_ch',
            status='success',
            latency_ms=100
        )
        
        assert log_id > 0
        
        # 获取日志
        logs = temp_db.get_message_logs()
        assert len(logs) == 1
        assert logs[0]['content'] == '测试消息'
        assert logs[0]['status'] == 'success'
    
    def test_message_log_unique_constraint(self, temp_db):
        """测试消息ID唯一约束"""
        # 添加第一条日志
        log_id1 = temp_db.add_message_log(
            kook_message_id='msg_unique',
            kook_channel_id='ch_456',
            content='消息1',
            message_type='text',
            sender_name='用户1',
            target_platform='discord',
            target_channel='target_ch',
            status='success'
        )
        
        # 尝试添加相同message_id的日志（应该返回已存在的ID）
        log_id2 = temp_db.add_message_log(
            kook_message_id='msg_unique',
            kook_channel_id='ch_789',
            content='消息2',
            message_type='text',
            sender_name='用户2',
            target_platform='telegram',
            target_channel='target_ch2',
            status='failed'
        )
        
        # 应该返回相同的ID
        assert log_id1 == log_id2
        
        # 数据库中只有一条记录
        logs = temp_db.get_message_logs()
        assert len(logs) == 1
    
    def test_system_config(self, temp_db):
        """测试系统配置"""
        # 设置配置
        temp_db.set_config('test_key', 'test_value')
        
        # 获取配置
        value = temp_db.get_config('test_key')
        assert value == 'test_value'
        
        # 更新配置
        temp_db.set_config('test_key', 'new_value')
        value = temp_db.get_config('test_key')
        assert value == 'new_value'
        
        # 删除配置
        temp_db.delete_config('test_key')
        value = temp_db.get_config('test_key')
        assert value is None
    
    def test_context_manager(self, temp_db):
        """测试数据库上下文管理器"""
        # 正常操作应该自动提交
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO system_config (key, value) VALUES (?, ?)", ('k1', 'v1'))
        
        # 验证数据已提交
        value = temp_db.get_config('k1')
        assert value == 'v1'
    
    def test_transaction_rollback(self, temp_db):
        """测试事务回滚"""
        try:
            with temp_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO system_config (key, value) VALUES (?, ?)", ('k2', 'v2'))
                # 抛出异常触发回滚
                raise Exception("测试回滚")
        except Exception:
            pass
        
        # 验证数据未提交
        value = temp_db.get_config('k2')
        assert value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
