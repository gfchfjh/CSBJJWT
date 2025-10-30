"""
环境检测与自动修复 - P0-5优化
完整检测系统运行环境，并提供自动修复功能
"""
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from .logger import logger


class EnvironmentChecker:
    """环境检测器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
        
    def check_all(self) -> Dict:
        """
        执行完整的环境检测
        
        Returns:
            检测结果字典
        """
        logger.info("=" * 60)
        logger.info("🔍 开始环境检测...")
        logger.info("=" * 60)
        
        results = {
            'system': self.check_system(),
            'python': self.check_python(),
            'node': self.check_node(),
            'dependencies': self.check_dependencies(),
            'directories': self.check_directories(),
            'ports': self.check_ports(),
            'permissions': self.check_permissions(),
            'redis': self.check_redis(),
            'playwright': self.check_playwright(),
        }
        
        # 统计
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        logger.info("=" * 60)
        if total_issues == 0 and total_warnings == 0:
            logger.info("✅ 环境检测完成：一切正常！")
        else:
            if total_issues > 0:
                logger.warning(f"⚠️  发现 {total_issues} 个严重问题")
            if total_warnings > 0:
                logger.info(f"ℹ️  发现 {total_warnings} 个警告")
        logger.info("=" * 60)
        
        results['summary'] = {
            'issues': self.issues,
            'warnings': self.warnings,
            'info': self.info,
            'total_issues': total_issues,
            'total_warnings': total_warnings,
            'status': 'error' if total_issues > 0 else ('warning' if total_warnings > 0 else 'ok')
        }
        
        return results
    
    def check_system(self) -> Dict:
        """检测系统信息"""
        logger.info("📋 检测系统信息...")
        
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
        }
        
        logger.info(f"  操作系统: {system_info['platform']} {system_info['platform_release']}")
        logger.info(f"  架构: {system_info['architecture']}")
        logger.info(f"  Python版本: {sys.version.split()[0]}")
        
        # 检查操作系统
        if system_info['platform'] not in ['Linux', 'Darwin', 'Windows']:
            self.issues.append({
                'type': 'system',
                'level': 'error',
                'message': f"不支持的操作系统: {system_info['platform']}",
                'solution': '请在Linux、macOS或Windows上运行'
            })
        
        return system_info
    
    def check_python(self) -> Dict:
        """检测Python版本"""
        logger.info("🐍 检测Python环境...")
        
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        python_info = {
            'version': version_str,
            'version_tuple': (version_info.major, version_info.minor, version_info.micro),
            'executable': sys.executable,
        }
        
        logger.info(f"  Python版本: {version_str}")
        logger.info(f"  可执行文件: {sys.executable}")
        
        # 检查版本（要求3.8+）
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            self.issues.append({
                'type': 'python',
                'level': 'error',
                'message': f"Python版本过低: {version_str}（要求3.8+）",
                'solution': '请升级到Python 3.8或更高版本',
                'auto_fixable': False
            })
        elif version_info.major == 3 and version_info.minor < 10:
            self.warnings.append({
                'type': 'python',
                'level': 'warning',
                'message': f"Python版本较低: {version_str}（推荐3.10+）",
                'solution': '建议升级到Python 3.10或更高版本以获得更好的性能'
            })
        
        return python_info
    
    def check_node(self) -> Dict:
        """检测Node.js环境"""
        logger.info("📦 检测Node.js环境...")
        
        node_info = {
            'installed': False,
            'version': None,
            'npm_version': None,
        }
        
        # 检查Node.js
        node_path = shutil.which('node')
        if not node_path:
            self.warnings.append({
                'type': 'node',
                'level': 'warning',
                'message': '未安装Node.js',
                'solution': '如果需要使用前端功能，请安装Node.js 16+',
                'auto_fixable': False
            })
            logger.warning("  ⚠️  未安装Node.js")
            return node_info
        
        node_info['installed'] = True
        node_info['path'] = node_path
        
        # 检查版本
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                node_info['version'] = result.stdout.strip()
                logger.info(f"  Node.js版本: {node_info['version']}")
        except Exception as e:
            logger.warning(f"  ⚠️  无法获取Node.js版本: {e}")
        
        # 检查npm
        npm_path = shutil.which('npm')
        if npm_path:
            try:
                result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    node_info['npm_version'] = result.stdout.strip()
                    logger.info(f"  npm版本: {node_info['npm_version']}")
            except Exception as e:
                logger.warning(f"  ⚠️  无法获取npm版本: {e}")
        
        return node_info
    
    def check_dependencies(self) -> Dict:
        """检测Python依赖"""
        logger.info("📚 检测Python依赖...")
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'aiohttp',
            'playwright',
            'redis',
            'sqlalchemy',
            'pydantic',
            'cryptography',
            'pillow',
        ]
        
        installed_packages = {}
        missing_packages = []
        
        for package in required_packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
                logger.info(f"  ✅ {package}: {version}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"  ❌ {package}: 未安装")
        
        if missing_packages:
            self.issues.append({
                'type': 'dependencies',
                'level': 'error',
                'message': f"缺少必需的Python包: {', '.join(missing_packages)}",
                'solution': f"运行: pip install {' '.join(missing_packages)}",
                'auto_fixable': True,
                'fix_command': f"pip install {' '.join(missing_packages)}"
            })
        
        return {
            'installed': installed_packages,
            'missing': missing_packages,
        }
    
    def check_directories(self) -> Dict:
        """检测必需的目录"""
        logger.info("📁 检测目录结构...")
        
        required_dirs = [
            'data',
            'data/images',
            'data/attachments',
            'logs',
            'cache',
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for dir_path in required_dirs:
            full_path = Path(dir_path)
            if full_path.exists():
                existing_dirs.append(dir_path)
                logger.info(f"  ✅ {dir_path}")
            else:
                missing_dirs.append(dir_path)
                logger.warning(f"  ❌ {dir_path}: 不存在")
        
        if missing_dirs:
            self.warnings.append({
                'type': 'directories',
                'level': 'warning',
                'message': f"缺少目录: {', '.join(missing_dirs)}",
                'solution': '系统将自动创建这些目录',
                'auto_fixable': True,
                'fix_action': lambda: self.create_missing_directories(missing_dirs)
            })
        
        return {
            'existing': existing_dirs,
            'missing': missing_dirs,
        }
    
    def check_ports(self) -> Dict:
        """检测端口占用"""
        logger.info("🔌 检测端口占用...")
        
        required_ports = [
            (9527, 'FastAPI后端'),
            (6379, 'Redis'),
            (8765, '图床服务器'),
        ]
        
        port_status = {}
        
        for port, description in required_ports:
            is_available = self.is_port_available(port)
            port_status[port] = {
                'description': description,
                'available': is_available
            }
            
            if is_available:
                logger.info(f"  ✅ 端口 {port} ({description}): 可用")
            else:
                logger.warning(f"  ⚠️  端口 {port} ({description}): 已被占用")
                self.warnings.append({
                    'type': 'port',
                    'level': 'warning',
                    'message': f"端口 {port} ({description}) 已被占用",
                    'solution': f"请关闭占用端口 {port} 的程序，或修改配置使用其他端口"
                })
        
        return port_status
    
    def check_permissions(self) -> Dict:
        """检测文件权限"""
        logger.info("🔐 检测文件权限...")
        
        permission_checks = []
        
        # 检查当前目录写权限
        current_dir = Path.cwd()
        can_write = os.access(current_dir, os.W_OK)
        permission_checks.append({
            'path': str(current_dir),
            'writable': can_write
        })
        
        if can_write:
            logger.info(f"  ✅ 当前目录可写: {current_dir}")
        else:
            logger.error(f"  ❌ 当前目录不可写: {current_dir}")
            self.issues.append({
                'type': 'permissions',
                'level': 'error',
                'message': f"当前目录不可写: {current_dir}",
                'solution': '请确保有足够的文件权限',
                'auto_fixable': False
            })
        
        return {
            'checks': permission_checks,
            'current_dir_writable': can_write
        }
    
    def check_redis(self) -> Dict:
        """检测Redis连接"""
        logger.info("🗄️  检测Redis连接...")
        
        redis_info = {
            'available': False,
            'version': None,
        }
        
        try:
            import redis
            
            # 尝试连接Redis
            client = redis.Redis(host='localhost', port=6379, socket_connect_timeout=3)
            client.ping()
            
            redis_info['available'] = True
            
            # 获取版本
            info = client.info()
            redis_info['version'] = info.get('redis_version', 'unknown')
            
            logger.info(f"  ✅ Redis连接成功: v{redis_info['version']}")
            
        except Exception as e:
            logger.warning(f"  ⚠️  Redis连接失败: {e}")
            self.warnings.append({
                'type': 'redis',
                'level': 'warning',
                'message': f"Redis连接失败: {str(e)}",
                'solution': '请确保Redis正在运行（端口6379），或运行内嵌Redis',
                'auto_fixable': False
            })
        
        return redis_info
    
    def check_playwright(self) -> Dict:
        """检测Playwright浏览器"""
        logger.info("🌐 检测Playwright浏览器...")
        
        playwright_info = {
            'installed': False,
            'browsers': {},
        }
        
        try:
            from playwright.sync_api import sync_playwright
            
            playwright_info['installed'] = True
            logger.info("  ✅ Playwright已安装")
            
            # 检查浏览器是否已安装
            try:
                with sync_playwright() as p:
                    # 尝试启动chromium
                    try:
                        browser = p.chromium.launch(headless=True)
                        browser.close()
                        playwright_info['browsers']['chromium'] = True
                        logger.info("  ✅ Chromium浏览器已安装")
                    except Exception as e:
                        playwright_info['browsers']['chromium'] = False
                        logger.warning(f"  ⚠️  Chromium浏览器未安装: {e}")
                        self.warnings.append({
                            'type': 'playwright',
                            'level': 'warning',
                            'message': 'Playwright浏览器未安装',
                            'solution': '运行: playwright install chromium',
                            'auto_fixable': True,
                            'fix_command': 'playwright install chromium'
                        })
            except Exception as e:
                logger.warning(f"  ⚠️  无法检测Playwright浏览器: {e}")
                
        except ImportError:
            logger.warning("  ❌ Playwright未安装")
            self.issues.append({
                'type': 'playwright',
                'level': 'error',
                'message': 'Playwright未安装',
                'solution': '运行: pip install playwright && playwright install chromium',
                'auto_fixable': True,
                'fix_command': 'pip install playwright && playwright install chromium'
            })
        
        return playwright_info
    
    @staticmethod
    def is_port_available(port: int) -> bool:
        """检查端口是否可用"""
        import socket
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return True
            except OSError:
                return False
    
    def create_missing_directories(self, dirs: List[str]) -> bool:
        """创建缺失的目录"""
        try:
            for dir_path in dirs:
                full_path = Path(dir_path)
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  ✅ 已创建目录: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"  ❌ 创建目录失败: {e}")
            return False
    
    def auto_fix(self) -> Dict:
        """自动修复所有可修复的问题"""
        logger.info("=" * 60)
        logger.info("🔧 开始自动修复...")
        logger.info("=" * 60)
        
        fixed = []
        failed = []
        
        # 修复缺失的目录
        for warning in self.warnings:
            if warning['type'] == 'directories' and warning.get('auto_fixable'):
                if 'fix_action' in warning:
                    try:
                        success = warning['fix_action']()
                        if success:
                            fixed.append(warning)
                            logger.info(f"  ✅ 已修复: {warning['message']}")
                        else:
                            failed.append(warning)
                            logger.error(f"  ❌ 修复失败: {warning['message']}")
                    except Exception as e:
                        failed.append(warning)
                        logger.error(f"  ❌ 修复异常: {warning['message']}, {e}")
        
        # 执行命令修复
        for item in self.issues + self.warnings:
            if item.get('auto_fixable') and 'fix_command' in item:
                logger.info(f"  🔧 执行: {item['fix_command']}")
                logger.warning("    ⚠️  自动安装依赖已禁用，请手动运行上述命令")
                # 注意：不自动执行命令，避免安全问题
                # 用户应该手动运行建议的命令
        
        logger.info("=" * 60)
        logger.info(f"✅ 自动修复完成: 成功 {len(fixed)} 个, 失败 {len(failed)} 个")
        logger.info("=" * 60)
        
        return {
            'fixed': fixed,
            'failed': failed
        }
    
    def get_fix_suggestions(self) -> List[str]:
        """获取所有修复建议"""
        suggestions = []
        
        for item in self.issues + self.warnings:
            if 'fix_command' in item:
                suggestions.append(item['fix_command'])
        
        return suggestions


# 全局实例
env_checker = EnvironmentChecker()


def check_environment() -> Dict:
    """执行环境检测"""
    return env_checker.check_all()


def auto_fix_environment() -> Dict:
    """自动修复环境问题"""
    return env_checker.auto_fix()


if __name__ == "__main__":
    # 测试
    result = check_environment()
    
    print("\n" + "=" * 60)
    print("检测结果汇总")
    print("=" * 60)
    
    summary = result['summary']
    print(f"状态: {summary['status']}")
    print(f"问题: {summary['total_issues']} 个")
    print(f"警告: {summary['total_warnings']} 个")
    
    if summary['total_issues'] > 0 or summary['total_warnings'] > 0:
        print("\n修复建议:")
        suggestions = env_checker.get_fix_suggestions()
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        print("\n尝试自动修复...")
        auto_fix_environment()
