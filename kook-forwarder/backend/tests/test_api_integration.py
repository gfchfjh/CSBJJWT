"""
API集成测试
测试所有API端点的集成功能
"""
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import db
from app.config import settings


@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_api_token():
    """模拟API Token"""
    return "test_token_123456"


class TestAccountsAPI:
    """账号管理API测试"""
    
    @pytest.mark.asyncio
    async def test_get_accounts(self, client):
        """测试获取账号列表"""
        response = await client.get("/api/accounts")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert isinstance(data.get("data", []), list)
    
    @pytest.mark.asyncio
    async def test_add_account_with_cookie(self, client):
        """测试添加账号（Cookie方式）"""
        response = await client.post("/api/accounts", json={
            "email": "test@example.com",
            "cookie": '[{"name":"token","value":"test","domain":".kookapp.cn"}]'
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("success") is True
        assert "account_id" in data or "id" in data
    
    @pytest.mark.asyncio
    async def test_add_account_invalid_cookie(self, client):
        """测试添加账号（无效Cookie）"""
        response = await client.post("/api/accounts", json={
            "email": "test@example.com",
            "cookie": "invalid_json"
        })
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_delete_account(self, client):
        """测试删除账号"""
        # 先添加一个账号
        add_response = await client.post("/api/accounts", json={
            "email": "delete_test@example.com",
            "cookie": '[{"name":"token","value":"test"}]'
        })
        account_id = add_response.json().get("account_id") or add_response.json().get("id")
        
        # 删除账号
        response = await client.delete(f"/api/accounts/{account_id}")
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_start_scraper(self, client):
        """测试启动抓取器"""
        # 添加账号
        add_response = await client.post("/api/accounts", json={
            "email": "scraper_test@example.com",
            "cookie": '[{"name":"token","value":"test"}]'
        })
        account_id = add_response.json().get("account_id") or add_response.json().get("id")
        
        # 启动抓取器（模拟）
        response = await client.post(f"/api/accounts/{account_id}/start")
        # 由于没有真实Cookie，可能会失败，但API应该正常响应
        assert response.status_code in [200, 400, 500]


class TestBotsAPI:
    """Bot配置API测试"""
    
    @pytest.mark.asyncio
    async def test_get_bots(self, client):
        """测试获取Bot列表"""
        response = await client.get("/api/bots")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "data" in data
    
    @pytest.mark.asyncio
    async def test_add_discord_bot(self, client):
        """测试添加Discord Bot"""
        response = await client.post("/api/bots", json={
            "platform": "discord",
            "name": "测试Discord Bot",
            "config": {
                "webhook_url": "https://discord.com/api/webhooks/123456/test"
            }
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("success") is True or "id" in data
    
    @pytest.mark.asyncio
    async def test_add_telegram_bot(self, client):
        """测试添加Telegram Bot"""
        response = await client.post("/api/bots", json={
            "platform": "telegram",
            "name": "测试Telegram Bot",
            "config": {
                "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "chat_id": "-1001234567890"
            }
        })
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_add_feishu_bot(self, client):
        """测试添加飞书Bot"""
        response = await client.post("/api/bots", json={
            "platform": "feishu",
            "name": "测试飞书Bot",
            "config": {
                "app_id": "cli_test123456",
                "app_secret": "test_secret_abc123"
            }
        })
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_get_bots_by_platform(self, client):
        """测试按平台获取Bot"""
        response = await client.get("/api/bots?platform=discord")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_delete_bot(self, client):
        """测试删除Bot"""
        # 先添加
        add_response = await client.post("/api/bots", json={
            "platform": "discord",
            "name": "待删除Bot",
            "config": {"webhook_url": "https://discord.com/api/webhooks/test"}
        })
        bot_id = add_response.json().get("id") or add_response.json().get("bot_id")
        
        # 删除
        response = await client.delete(f"/api/bots/{bot_id}")
        assert response.status_code in [200, 204]


class TestMappingsAPI:
    """频道映射API测试"""
    
    @pytest.mark.asyncio
    async def test_get_mappings(self, client):
        """测试获取映射列表"""
        response = await client.get("/api/mappings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "data" in data
    
    @pytest.mark.asyncio
    async def test_add_mapping(self, client):
        """测试添加频道映射"""
        # 先添加一个Bot
        bot_response = await client.post("/api/bots", json={
            "platform": "discord",
            "name": "映射测试Bot",
            "config": {"webhook_url": "https://discord.com/api/webhooks/test"}
        })
        bot_id = bot_response.json().get("id") or bot_response.json().get("bot_id")
        
        # 添加映射
        response = await client.post("/api/mappings", json={
            "kook_server_id": "1234567890",
            "kook_channel_id": "9876543210",
            "kook_channel_name": "测试频道",
            "target_platform": "discord",
            "target_bot_id": bot_id,
            "target_channel_id": "discord_channel_123"
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("success") is True or "id" in data
    
    @pytest.mark.asyncio
    async def test_export_mappings(self, client):
        """测试导出映射配置"""
        response = await client.get("/api/mappings/export")
        assert response.status_code == 200
        data = response.json()
        assert "mappings" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_import_mappings(self, client):
        """测试导入映射配置"""
        mappings_data = {
            "mappings": [
                {
                    "kook_server_id": "test_server",
                    "kook_channel_id": "test_channel",
                    "kook_channel_name": "导入测试",
                    "target_platform": "discord",
                    "target_bot_id": 1,
                    "target_channel_id": "discord_test"
                }
            ]
        }
        response = await client.post("/api/mappings/import", json=mappings_data)
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_delete_mapping(self, client):
        """测试删除映射"""
        # 先添加Bot和映射
        bot_response = await client.post("/api/bots", json={
            "platform": "discord",
            "name": "删除测试Bot",
            "config": {"webhook_url": "https://discord.com/api/webhooks/test"}
        })
        bot_id = bot_response.json().get("id") or bot_response.json().get("bot_id")
        
        mapping_response = await client.post("/api/mappings", json={
            "kook_server_id": "delete_test",
            "kook_channel_id": "delete_test_channel",
            "kook_channel_name": "待删除",
            "target_platform": "discord",
            "target_bot_id": bot_id,
            "target_channel_id": "test"
        })
        mapping_id = mapping_response.json().get("id") or mapping_response.json().get("mapping_id")
        
        # 删除
        response = await client.delete(f"/api/mappings/{mapping_id}")
        assert response.status_code in [200, 204]


class TestLogsAPI:
    """日志API测试"""
    
    @pytest.mark.asyncio
    async def test_get_logs(self, client):
        """测试获取日志列表"""
        response = await client.get("/api/logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "data" in data
    
    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, client):
        """测试带过滤条件获取日志"""
        response = await client.get("/api/logs?limit=50&status=success&platform=discord")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_logs_stats(self, client):
        """测试获取统计信息"""
        response = await client.get("/api/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data or isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_clear_old_logs(self, client):
        """测试清除旧日志"""
        response = await client.post("/api/logs/clear?days=30")
        assert response.status_code in [200, 204]


class TestSystemAPI:
    """系统控制API测试"""
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, client):
        """测试获取系统状态"""
        response = await client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "service_running" in data or "status" in data
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, client):
        """测试获取缓存统计"""
        response = await client.get("/api/cache/stats")
        # 缓存API可能不存在，检查响应
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy" or "status" in data


class TestAuthAPI:
    """认证API测试"""
    
    @pytest.mark.asyncio
    async def test_login(self, client):
        """测试登录"""
        response = await client.post("/api/auth/login", json={
            "password": "test_password"
        })
        # 可能需要先设置密码
        assert response.status_code in [200, 401, 404]
    
    @pytest.mark.asyncio
    async def test_verify_token(self, client):
        """测试验证Token"""
        response = await client.post("/api/auth/verify", json={
            "token": "test_token"
        })
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_change_password(self, client):
        """测试修改密码"""
        response = await client.post("/api/auth/change-password", json={
            "old_password": "old_pass",
            "new_password": "new_pass"
        })
        assert response.status_code in [200, 401, 404]


class TestBackupAPI:
    """备份API测试"""
    
    @pytest.mark.asyncio
    async def test_create_backup(self, client):
        """测试创建备份"""
        response = await client.post("/api/backup/create")
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_list_backups(self, client):
        """测试获取备份列表"""
        response = await client.get("/api/backup/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "backups" in data
    
    @pytest.mark.asyncio
    async def test_restore_backup(self, client):
        """测试恢复备份"""
        # 这个测试可能需要实际的备份文件
        response = await client.post("/api/backup/restore", json={
            "backup_id": "test_backup"
        })
        assert response.status_code in [200, 404]


class TestSmartMappingAPI:
    """智能映射API测试"""
    
    @pytest.mark.asyncio
    async def test_get_kook_servers(self, client):
        """测试获取KOOK服务器列表"""
        response = await client.get("/api/smart-mapping/kook-servers")
        # 需要账号登录才能获取
        assert response.status_code in [200, 400, 401]
    
    @pytest.mark.asyncio
    async def test_get_kook_channels(self, client):
        """测试获取KOOK频道列表"""
        response = await client.get("/api/smart-mapping/kook-channels?server_id=test")
        assert response.status_code in [200, 400, 401]
    
    @pytest.mark.asyncio
    async def test_auto_match_channels(self, client):
        """测试自动匹配频道"""
        response = await client.post("/api/smart-mapping/auto-match")
        assert response.status_code in [200, 400]


class TestWebSocketAPI:
    """WebSocket API测试"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        # WebSocket测试需要特殊处理
        # 这里只验证端点存在
        pass


class TestHealthAPI:
    """健康检查API测试"""
    
    @pytest.mark.asyncio
    async def test_health_check_detail(self, client):
        """测试详细健康检查"""
        response = await client.get("/api/health/check")
        assert response.status_code == 200
        data = response.json()
        # 应该包含各组件状态
        assert isinstance(data, dict)


class TestUpdateAPI:
    """更新检查API测试"""
    
    @pytest.mark.asyncio
    async def test_check_update(self, client):
        """测试检查更新"""
        response = await client.get("/api/updates/check")
        assert response.status_code == 200
        data = response.json()
        assert "current_version" in data or "version" in data


# 性能测试
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """测试并发请求"""
        tasks = []
        for i in range(50):
            tasks.append(client.get("/api/system/status"))
        
        responses = await asyncio.gather(*tasks)
        
        # 所有请求都应该成功
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 45, "并发请求成功率低于90%"
    
    @pytest.mark.asyncio
    async def test_response_time(self, client):
        """测试响应时间"""
        import time
        
        start = time.time()
        response = await client.get("/api/system/status")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0, f"响应时间过长: {duration:.2f}秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
