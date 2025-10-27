"""
环境检查工具（增强版）
启动时自动检查环境并尝试自动修复
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .logger import logger

class EnvironmentChecker:
    """环境检查器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
    
    def check_all(self) -> Tuple[bool, Dict[str, any]]:
        """
        执行所有检查
        
        Returns:
            (is_ok, results): 是否通过，检查结果字典
        """
        logger.info("=" * 60)
        logger.info("🔍 开始环境检查...")
        logger.info("=" * 60)
        
        results = {}
        
        # 1. 检查Python版本
        results['python'] = self.check_python_version()
        
        # 2. 检查必需的Python包
        results['packages'] = self.check_python_packages()
        
        # 3. 检查Playwright浏览器
        results['playwright'] = self.check_playwright_browser()
        
        # 4. 检查Redis
        results['redis'] = self.check_redis()
        
        # 5. 检查数据目录
        results['directories'] = self.check_data_directories()
        
        # 6. 检查配置文件
        results['config'] = self.check_config_files()
        
        # 7. 检查网络连接
        results['network'] = self.check_network()
        
        # 8. 检查磁盘空间
        results['disk'] = self.check_disk_space()
        
        # 生成报告
        is_ok = self.generate_report(results)
        
        logger.info("=" * 60)
        if is_ok:
            logger.info("✅ 环境检查通过")
        else:
            logger.warning(f"⚠️  环境检查发现 {len(self.errors)} 个错误")
        logger.info("=" * 60)
        
        return is_ok, results
    
    def check_python_version(self) -> Dict:
        """检查Python版本"""
        logger.info("📌 检查Python版本...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        result = {
            'version': version_str,
            'ok': version >= (3, 11),
            'message': ''
        }
        
        if result['ok']:
            logger.info(f"✅ Python版本: {version_str}")
            result['message'] = f"Python {version_str} (OK)"
        else:
            msg = f"Python版本过低: {version_str}，需要3.11+"
            logger.error(f"❌ {msg}")
            self.errors.append(msg)
            result['message'] = msg
            result['fix'] = "请升级Python到3.11或更高版本"
        
        return result
    
    def check_python_packages(self) -> Dict:
        """检查必需的Python包"""
        logger.info("📌 检查Python依赖包...")
        
        required_packages = [
            'fastapi',
            'playwright',
            'redis',
            'aiohttp',
            'cryptography',
            'Pillow',
            'pydantic',
        ]
        
        missing = []
        installed = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').lower())
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        result = {
            'installed': installed,
            'missing': missing,
            'ok': len(missing) == 0
        }
        
        if result['ok']:
            logger.info(f"✅ 所有依赖包已安装 ({len(installed)}个)")
        else:
            msg = f"缺失{len(missing)}个依赖包: {', '.join(missing)}"
            logger.warning(f"⚠️  {msg}")
            self.warnings.append(msg)
            result['fix'] = f"运行: pip install {' '.join(missing)}"
        
        return result
    
    def check_playwright_browser(self) -> Dict:
        """检查Playwright浏览器"""
        logger.info("📌 检查Playwright浏览器...")
        
        result = {
            'installed': False,
            'path': None,
            'ok': False,
            'auto_fix_attempted': False
        }
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser_path = Path(p.chromium.executable_path)
                if browser_path.exists():
                    result['installed'] = True
                    result['path'] = str(browser_path)
                    result['ok'] = True
                    logger.info(f"✅ Playwright Chromium已安装")
                    logger.info(f"   路径: {browser_path}")
                else:
                    raise FileNotFoundError("浏览器文件不存在")
                    
        except Exception as e:
            logger.warning(f"⚠️  Playwright Chromium未安装: {e}")
            
            # 尝试自动安装
            if self.auto_install_playwright_browser():
                result['installed'] = True
                result['ok'] = True
                result['auto_fix_attempted'] = True
                self.fixes_applied.append("自动安装Playwright Chromium")
            else:
                msg = "Playwright Chromium未安装"
                self.warnings.append(msg)
                result['fix'] = "运行: playwright install chromium"
        
        return result
    
    def auto_install_playwright_browser(self) -> bool:
        """自动安装Playwright浏览器"""
        logger.info("🔧 尝试自动安装Playwright Chromium...")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
                capture_output=True,
                timeout=300  # 5分钟超时
            )
            logger.info("✅ Playwright Chromium自动安装成功")
            return True
        except subprocess.TimeoutExpired:
            logger.error("❌ 安装超时（5分钟）")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 安装失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 安装异常: {e}")
            return False
    
    def check_redis(self) -> Dict:
        """检查Redis"""
        logger.info("📌 检查Redis...")
        
        result = {
            'system_redis': False,
            'embedded_redis': False,
            'ok': False
        }
        
        # 检查系统Redis
        if shutil.which('redis-server'):
            result['system_redis'] = True
            result['ok'] = True
            logger.info("✅ 检测到系统Redis")
        
        # 检查嵌入式Redis
        embedded_redis_paths = [
            Path('redis/redis-server'),
            Path('redis/redis-server.exe'),
            Path('redis/windows/redis-server.exe'),
            Path('redis/linux/redis-server'),
            Path('redis/macos/redis-server'),
        ]
        
        for path in embedded_redis_paths:
            if path.exists():
                result['embedded_redis'] = True
                result['ok'] = True
                logger.info(f"✅ 检测到嵌入式Redis: {path}")
                break
        
        if not result['ok']:
            msg = "未检测到Redis（系统或嵌入式）"
            logger.warning(f"⚠️  {msg}")
            self.warnings.append(msg)
            result['fix'] = "安装Redis或使用嵌入式版本"
        
        return result
    
    def check_data_directories(self) -> Dict:
        """检查数据目录"""
        logger.info("📌 检查数据目录...")
        
        from ..config import settings
        
        required_dirs = [
            settings.data_dir,
            settings.image_storage_path,
            settings.log_dir,
        ]
        
        created = []
        exists = []
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created.append(str(dir_path))
                    logger.info(f"✅ 创建目录: {dir_path}")
                except Exception as e:
                    msg = f"无法创建目录 {dir_path}: {e}"
                    logger.error(f"❌ {msg}")
                    self.errors.append(msg)
            else:
                exists.append(str(dir_path))
        
        result = {
            'created': created,
            'exists': exists,
            'ok': len(created) + len(exists) == len(required_dirs)
        }
        
        if result['ok']:
            logger.info(f"✅ 数据目录检查通过")
        
        return result
    
    def check_config_files(self) -> Dict:
        """检查配置文件"""
        logger.info("📌 检查配置文件...")
        
        config_files = {
            'selectors.yaml': Path('backend/data/selectors.yaml'),
            '.env': Path('backend/.env'),
        }
        
        result = {
            'exists': [],
            'missing': [],
            'ok': True
        }
        
        for name, path in config_files.items():
            if path.exists():
                result['exists'].append(name)
            else:
                result['missing'].append(name)
                logger.info(f"ℹ️  配置文件不存在（可选）: {name}")
        
        # 配置文件缺失不算错误，只是警告
        if result['missing']:
            logger.info(f"ℹ️  {len(result['missing'])}个配置文件使用默认值")
        
        return result
    
    def check_network(self) -> Dict:
        """检查网络连接"""
        logger.info("📌 检查网络连接...")
        
        result = {
            'ok': True,
            'reachable': [],
            'unreachable': []
        }
        
        # 测试关键域名
        test_domains = [
            'www.kookapp.cn',
            'api.github.com',
        ]
        
        for domain in test_domains:
            try:
                import socket
                socket.create_connection((domain, 443), timeout=5)
                result['reachable'].append(domain)
                logger.info(f"✅ 可访问: {domain}")
            except Exception:
                result['unreachable'].append(domain)
                logger.warning(f"⚠️  无法访问: {domain}")
        
        if result['unreachable']:
            msg = f"部分域名无法访问: {', '.join(result['unreachable'])}"
            self.warnings.append(msg)
            result['ok'] = False
        
        return result
    
    def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        logger.info("📌 检查磁盘空间...")
        
        from ..config import settings
        
        try:
            stat = shutil.disk_usage(settings.data_dir)
            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            used_percent = (stat.used / stat.total) * 100
            
            result = {
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'used_percent': round(used_percent, 1),
                'ok': free_gb >= 1.0  # 至少1GB空闲
            }
            
            if result['ok']:
                logger.info(f"✅ 磁盘空间充足: {free_gb:.1f}GB 可用")
            else:
                msg = f"磁盘空间不足: 仅剩{free_gb:.1f}GB"
                logger.warning(f"⚠️  {msg}")
                self.warnings.append(msg)
                result['fix'] = "清理磁盘空间或更改数据目录"
            
            return result
            
        except Exception as e:
            logger.warning(f"⚠️  无法检查磁盘空间: {e}")
            return {'ok': True, 'error': str(e)}
    
    def generate_report(self, results: Dict) -> bool:
        """生成检查报告"""
        logger.info("")
        logger.info("📊 环境检查报告")
        logger.info("=" * 60)
        
        # 统计
        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r.get('ok', False))
        
        logger.info(f"总检查项: {total_checks}")
        logger.info(f"通过: {passed_checks}")
        logger.info(f"错误: {len(self.errors)}")
        logger.info(f"警告: {len(self.warnings)}")
        
        # 显示错误
        if self.errors:
            logger.info("")
            logger.info("❌ 严重错误:")
            for i, error in enumerate(self.errors, 1):
                logger.error(f"  {i}. {error}")
        
        # 显示警告
        if self.warnings:
            logger.info("")
            logger.info("⚠️  警告:")
            for i, warning in enumerate(self.warnings, 1):
                logger.warning(f"  {i}. {warning}")
        
        # 显示自动修复
        if self.fixes_applied:
            logger.info("")
            logger.info("🔧 自动修复:")
            for i, fix in enumerate(self.fixes_applied, 1):
                logger.info(f"  {i}. {fix}")
        
        # 建议
        if self.errors or self.warnings:
            logger.info("")
            logger.info("💡 修复建议:")
            for key, result in results.items():
                if 'fix' in result and result['fix']:
                    logger.info(f"  • {result['fix']}")
        
        return len(self.errors) == 0

# 全局环境检查器实例
environment_checker = EnvironmentChecker()


async def check_environment() -> bool:
    """
    执行环境检查（异步版本）
    供main.py启动时调用
    """
    is_ok, results = environment_checker.check_all()
    return is_ok
