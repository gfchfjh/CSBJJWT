"""
选择器管理器测试
"""
import pytest
import json
from pathlib import Path
from app.utils.selector_manager import SelectorManager


class TestSelectorManager:
    """测试SelectorManager类"""
    
    @pytest.fixture
    def temp_config_path(self, tmp_path):
        """创建临时配置文件路径"""
        return tmp_path / "test_selectors.yaml"
    
    @pytest.fixture
    def selector_manager(self, temp_config_path):
        """创建测试用选择器管理器实例"""
        return SelectorManager(config_path=temp_config_path)
    
    def test_load_default_config(self, selector_manager):
        """测试加载默认配置"""
        assert selector_manager.config is not None
        assert "version" in selector_manager.config
        assert "server_container" in selector_manager.config
        assert "channel_item" in selector_manager.config
    
    def test_get_selectors(self, selector_manager):
        """测试获取选择器列表"""
        selectors = selector_manager.get_selectors("server_container")
        
        assert isinstance(selectors, list)
        assert len(selectors) > 0
    
    def test_get_selector_dict(self, selector_manager):
        """测试获取选择器字典"""
        login_selectors = selector_manager.get_selector_dict("login")
        
        assert isinstance(login_selectors, dict)
        assert "email_input" in login_selectors
        assert "password_input" in login_selectors
    
    def test_save_and_reload(self, selector_manager):
        """测试保存和重新加载配置"""
        # 保存配置
        success = selector_manager.save_to_file()
        assert success is True
        assert selector_manager.config_path.exists()
        
        # 重新加载
        success = selector_manager.reload()
        assert success is True
    
    def test_update_selector(self, selector_manager):
        """测试更新选择器"""
        new_selectors = [".test-selector", "#test-id"]
        success = selector_manager.update_selector("test_category", new_selectors)
        
        assert success is True
        assert selector_manager.config["test_category"] == new_selectors
    
    def test_add_selector(self, selector_manager):
        """测试添加选择器"""
        original_count = len(selector_manager.get_selectors("server_container"))
        
        success = selector_manager.add_selector(
            "server_container",
            ".new-test-selector",
            position=0
        )
        
        assert success is True
        new_count = len(selector_manager.get_selectors("server_container"))
        assert new_count == original_count + 1
        
        # 验证插入位置
        selectors = selector_manager.get_selectors("server_container")
        assert selectors[0] == ".new-test-selector"
    
    def test_add_duplicate_selector(self, selector_manager):
        """测试添加重复选择器"""
        selector = ".duplicate-selector"
        
        # 第一次添加
        success = selector_manager.add_selector("test_category", selector)
        assert success is True
        
        # 第二次添加（应该失败）
        success = selector_manager.add_selector("test_category", selector)
        assert success is False
    
    def test_remove_selector(self, selector_manager):
        """测试删除选择器"""
        # 先添加一个选择器
        selector = ".removable-selector"
        selector_manager.add_selector("test_category", selector)
        
        # 删除它
        success = selector_manager.remove_selector("test_category", selector)
        assert success is True
        
        # 验证已删除
        selectors = selector_manager.get_selectors("test_category")
        assert selector not in selectors
    
    def test_export_config(self, selector_manager):
        """测试导出配置"""
        config_str = selector_manager.export_config()
        
        assert isinstance(config_str, str)
        
        # 验证是有效的JSON
        config_dict = json.loads(config_str)
        assert "version" in config_dict
    
    def test_import_config(self, selector_manager):
        """测试导入配置"""
        # 创建测试配置
        test_config = {
            "test_import": ["selector1", "selector2"]
        }
        config_str = json.dumps(test_config)
        
        # 导入配置
        success = selector_manager.import_config(config_str, format="json")
        assert success is True
        
        # 验证导入
        assert "test_import" in selector_manager.config
        assert selector_manager.config["test_import"] == ["selector1", "selector2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
