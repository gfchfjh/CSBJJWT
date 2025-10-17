"""
更新检查器测试
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from app.utils.update_checker import UpdateChecker


class TestUpdateChecker:
    """测试UpdateChecker类"""
    
    @pytest.fixture
    def update_checker(self):
        """创建测试用更新检查器实例"""
        checker = UpdateChecker()
        checker.check_interval = 10  # 设置较短的检查间隔用于测试
        return checker
    
    def test_init(self, update_checker):
        """测试初始化"""
        assert update_checker.current_version is not None
        assert update_checker.is_running is False
        assert update_checker.latest_version_info is None
    
    def test_is_newer_version(self, update_checker):
        """测试版本比较"""
        # 较新版本
        assert update_checker._is_newer_version("1.1.0", "1.0.0") is True
        assert update_checker._is_newer_version("2.0.0", "1.9.9") is True
        
        # 相同版本
        assert update_checker._is_newer_version("1.0.0", "1.0.0") is False
        
        # 较旧版本
        assert update_checker._is_newer_version("1.0.0", "1.1.0") is False
        
        # 带v前缀
        assert update_checker._is_newer_version("v1.1.0", "v1.0.0") is True
    
    def test_should_check_first_time(self, update_checker):
        """测试首次是否应该检查"""
        # 首次检查
        assert update_checker.should_check() is True
    
    def test_should_check_after_interval(self, update_checker):
        """测试间隔后是否应该检查"""
        # 设置最后检查时间为很久以前
        update_checker.last_check_time = datetime.now() - timedelta(hours=25)
        assert update_checker.should_check() is True
        
        # 设置最后检查时间为最近
        update_checker.last_check_time = datetime.now()
        assert update_checker.should_check() is False
    
    @pytest.mark.asyncio
    async def test_check_for_updates_with_newer_version(self, update_checker):
        """测试检查更新（有新版本）"""
        # Mock GitHub API响应
        mock_response_data = {
            "tag_name": "v1.1.0",
            "name": "Version 1.1.0",
            "body": "New features and bug fixes",
            "published_at": "2025-10-17T00:00:00Z",
            "html_url": "https://github.com/test/repo/releases/tag/v1.1.0",
            "assets": [
                {
                    "name": "App_Windows_x64.exe",
                    "browser_download_url": "https://example.com/windows.exe"
                },
                {
                    "name": "App_macOS.dmg",
                    "browser_download_url": "https://example.com/macos.dmg"
                }
            ]
        }
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            # 配置mock响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # 设置当前版本为较旧版本
            update_checker.current_version = "1.0.0"
            
            # 执行检查
            result = await update_checker.check_for_updates()
            
            # 验证结果
            assert result is not None
            assert result["has_update"] is True
            assert result["latest_version"] == "1.1.0"
            assert result["current_version"] == "1.0.0"
            assert "windows" in result["downloads"]
            assert "macos" in result["downloads"]
    
    @pytest.mark.asyncio
    async def test_check_for_updates_already_latest(self, update_checker):
        """测试检查更新（已是最新）"""
        mock_response_data = {
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
            "body": "Current version",
            "published_at": "2025-10-17T00:00:00Z",
            "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
            "assets": []
        }
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            update_checker.current_version = "1.0.0"
            
            result = await update_checker.check_for_updates()
            
            assert result is not None
            assert result["has_update"] is False
            assert result["latest_version"] == "1.0.0"
    
    def test_get_download_url(self, update_checker):
        """测试获取下载链接"""
        # 设置版本信息
        update_checker.latest_version_info = {
            "downloads": {
                "windows": "https://example.com/windows.exe",
                "macos": "https://example.com/macos.dmg",
                "linux": "https://example.com/linux.AppImage"
            }
        }
        
        # 测试获取各平台链接
        assert update_checker.get_download_url("windows") == "https://example.com/windows.exe"
        assert update_checker.get_download_url("macOS") == "https://example.com/macos.dmg"
        assert update_checker.get_download_url("Linux") == "https://example.com/linux.AppImage"
        
        # 测试不存在的平台
        assert update_checker.get_download_url("unknown") is None
    
    def test_format_release_notes(self, update_checker):
        """测试格式化发布说明"""
        # 短文本
        update_checker.latest_version_info = {
            "release_notes": "Short notes"
        }
        notes = update_checker.format_release_notes(max_length=100)
        assert notes == "Short notes"
        
        # 长文本（应截断）
        long_text = "A" * 600
        update_checker.latest_version_info = {
            "release_notes": long_text
        }
        notes = update_checker.format_release_notes(max_length=500)
        assert len(notes) <= 503  # 500 + "..."
        assert notes.endswith("...")
    
    def test_get_status(self, update_checker):
        """测试获取状态"""
        status = update_checker.get_status()
        
        assert isinstance(status, dict)
        assert "enabled" in status
        assert "is_running" in status
        assert "current_version" in status
        assert "check_interval_hours" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
