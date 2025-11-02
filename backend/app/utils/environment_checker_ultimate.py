"""
环境检测与一键修复 - 终极版
✅ P0-4优化: 全面检测 + 自动修复 + 进度反馈
"""
import sys
import os
import platform
import subprocess
import socket
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator
from ..config import settings
from ..utils.logger import logger


class EnvironmentChecker:
    """
    环境检测器
    
    功能：
    1. Python环境检测
    2. 依赖包检测
    3. 端口占用检测
    4. Chromium检测与下载
    5. Redis检测
    6. 目录权限检测
    7. 自动修复
    8. 实时进度反馈
    """
    
    def __init__(self):
        self.issues = []  # 问题列表
        self.warnings = []  # 警告列表
        self.fixes_applied = []  # 已应用的修复
        
    async def check_all(self) -> Dict:
        """
        执行全面检查
        
        Returns:
            检查结果字典
        """
        logger.info("🔍 开始环境检测...")
        
        results = {
            'python': await self.check_python(),
            'dependencies': await self.check_dependencies(),
            'ports': await self.check_ports(),
            'chromium': await self.check_chromium(),
            'redis': await self.check_redis(),
            'directories': await self.check_directories(),
            'permissions': await self.check_permissions(),
            'nodejs': await self.check_nodejs()
        }
        
        # 统计
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        success = total_issues == 0
        
        logger.info(f"{'✅' if success else '⚠️'} 环境检测完成：{total_issues}个问题，{total_warnings}个警告")
        
        return {
            'success': success,
            'issues': self.issues,
            'warnings': self.warnings,
            'results': results,
            'total_issues': total_issues,
            'total_warnings': total_warnings
        }
    
    async def check_python(self) -> Dict:
        """检查Python环境"""
        logger.info("检查Python环境...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        result = {
            'version': version_str,
            'major': version.major,
            'minor': version.minor,
            'micro': version.micro,
            'executable': sys.executable,
            'platform': platform.system(),
            'architecture': platform.machine()
        }
        
        # 检查版本要求（3.8+）
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.issues.append({
                'type': 'critical',
                'category': 'python',
                'message': f'Python版本过低（{version_str}），需要3.8+',
                'fixable': False,
                'fix_command': 'https://www.python.org/downloads/'
            })
            result['status'] = 'error'
        else:
            logger.info(f"✅ Python版本: {version_str}")
            result['status'] = 'ok'
        
        return result
    
    async def check_dependencies(self) -> Dict:
        """检查Python依赖包"""
        logger.info("检查Python依赖...")
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'aiohttp',
            'playwright',
            'redis',
            'aiosqlite',
            'cryptography',
            'Pillow'
        ]
        
        missing = []
        installed = []
        
        for package in required_packages:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)
                self.issues.append({
                    'type': 'error',
                    'category': 'dependency',
                    'message': f'缺少依赖包: {package}',
                    'fixable': True,
                    'fix_command': f'pip install {package}'
                })
        
        result = {
            'total': len(required_packages),
            'installed': len(installed),
            'missing': len(missing),
            'missing_packages': missing,
            'installed_packages': installed,
            'status': 'ok' if not missing else 'error'
        }
        
        if missing:
            logger.warning(f"⚠️ 缺少{len(missing)}个依赖包: {', '.join(missing)}")
        else:
            logger.info(f"✅ 所有依赖包已安装")
        
        return result
    
    async def check_ports(self) -> Dict:
        """检查端口占用"""
        logger.info("检查端口占用...")
        
        required_ports = [
            (9527, 'API服务'),
            (6379, 'Redis'),
            (9528, '图床服务')
        ]
        
        occupied = []
        available = []
        
        for port, name in required_ports:
            if self._is_port_in_use(port):
                occupied.append({'port': port, 'name': name})
                self.warnings.append({
                    'type': 'warning',
                    'category': 'port',
                    'message': f'端口{port}（{name}）已被占用',
                    'fixable': True,
                    'fix_command': f'自动更换端口'
                })
            else:
                available.append({'port': port, 'name': name})
        
        result = {
            'total': len(required_ports),
            'available': len(available),
            'occupied': len(occupied),
            'occupied_ports': occupied,
            'available_ports': available,
            'status': 'ok' if not occupied else 'warning'
        }
        
        if occupied:
            logger.warning(f"⚠️ {len(occupied)}个端口被占用")
        else:
            logger.info(f"✅ 所有端口可用")
        
        return result
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    async def check_chromium(self) -> Dict:
        """检查Chromium浏览器"""
        logger.info("检查Chromium浏览器...")
        
        result = {
            'installed': False,
            'version': None,
            'path': None,
            'status': 'checking'
        }
        
        try:
            # 检查playwright是否安装
            import playwright
            from playwright.sync_api import sync_playwright
            
            # 尝试获取浏览器路径
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                    
                    result['installed'] = True
                    result['status'] = 'ok'
                    logger.info("✅ Chromium已安装")
                    
                except Exception as e:
                    result['installed'] = False
                    result['status'] = 'error'
                    result['error'] = str(e)
                    
                    self.issues.append({
                        'type': 'error',
                        'category': 'chromium',
                        'message': 'Chromium未安装或损坏',
                        'fixable': True,
                        'fix_command': 'playwright install chromium'
                    })
                    
                    logger.warning("⚠️ Chromium未安装")
        
        except ImportError:
            result['installed'] = False
            result['status'] = 'error'
            self.issues.append({
                'type': 'error',
                'category': 'chromium',
                'message': 'Playwright未安装',
                'fixable': True,
                'fix_command': 'pip install playwright && playwright install chromium'
            })
        
        return result
    
    async def check_redis(self) -> Dict:
        """检查Redis连接"""
        logger.info("检查Redis连接...")
        
        result = {
            'connected': False,
            'host': settings.redis_host,
            'port': settings.redis_port,
            'status': 'checking'
        }
        
        try:
            import redis
            
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                socket_timeout=2
            )
            
            # 测试ping
            client.ping()
            
            result['connected'] = True
            result['status'] = 'ok'
            logger.info("✅ Redis连接正常")
            
        except Exception as e:
            result['connected'] = False
            result['status'] = 'warning'
            result['error'] = str(e)
            
            self.warnings.append({
                'type': 'warning',
                'category': 'redis',
                'message': 'Redis未连接（将使用内嵌版本）',
                'fixable': True,
                'fix_command': '自动启动内嵌Redis'
            })
            
            logger.warning("⚠️ Redis未连接")
        
        return result
    
    async def check_directories(self) -> Dict:
        """检查目录结构"""
        logger.info("检查目录结构...")
        
        required_dirs = [
            settings.data_dir,
            settings.image_storage_path,
            settings.log_dir,
            settings.data_dir / 'redis'
        ]
        
        missing = []
        existing = []
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing.append(str(dir_path))
                
                # 尝试创建
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied.append(f"创建目录: {dir_path}")
                    existing.append(str(dir_path))
                    logger.info(f"✅ 创建目录: {dir_path}")
                except Exception as e:
                    self.issues.append({
                        'type': 'error',
                        'category': 'directory',
                        'message': f'无法创建目录: {dir_path}',
                        'fixable': False,
                        'fix_command': f'mkdir -p {dir_path}'
                    })
            else:
                existing.append(str(dir_path))
        
        result = {
            'total': len(required_dirs),
            'existing': len(existing),
            'missing': len(missing) - len(self.fixes_applied),
            'created': len(self.fixes_applied),
            'status': 'ok' if not missing else 'error'
        }
        
        logger.info(f"✅ 目录检查完成")
        
        return result
    
    async def check_permissions(self) -> Dict:
        """检查文件权限"""
        logger.info("检查文件权限...")
        
        result = {
            'writable': False,
            'readable': False,
            'status': 'checking'
        }
        
        test_file = settings.data_dir / '.permission_test'
        
        try:
            # 测试写入
            test_file.write_text('test')
            result['writable'] = True
            
            # 测试读取
            content = test_file.read_text()
            result['readable'] = content == 'test'
            
            # 清理
            test_file.unlink()
            
            result['status'] = 'ok'
            logger.info("✅ 文件权限正常")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
            self.issues.append({
                'type': 'critical',
                'category': 'permission',
                'message': f'数据目录不可写: {settings.data_dir}',
                'fixable': False,
                'fix_command': f'chmod 755 {settings.data_dir}'
            })
            
            logger.error(f"❌ 文件权限错误: {e}")
        
        return result
    
    async def check_nodejs(self) -> Dict:
        """检查Node.js环境（可选）"""
        logger.info("检查Node.js环境...")
        
        result = {
            'installed': False,
            'version': None,
            'npm_version': None,
            'status': 'optional'
        }
        
        try:
            # 检查node
            node_result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if node_result.returncode == 0:
                result['installed'] = True
                result['version'] = node_result.stdout.strip()
                
                # 检查npm
                npm_result = subprocess.run(
                    ['npm', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if npm_result.returncode == 0:
                    result['npm_version'] = npm_result.stdout.strip()
                
                result['status'] = 'ok'
                logger.info(f"✅ Node.js已安装: {result['version']}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            result['status'] = 'optional'
            self.warnings.append({
                'type': 'info',
                'category': 'nodejs',
                'message': 'Node.js未安装（可选，仅开发需要）',
                'fixable': False,
                'fix_command': 'https://nodejs.org/'
            })
            logger.info("ℹ️ Node.js未安装（可选）")
        
        return result
    
    async def auto_fix(self) -> AsyncGenerator[Dict, None]:
        """
        自动修复问题（带进度反馈）
        
        Yields:
            进度字典 {'step': str, 'progress': int, 'message': str}
        """
        total_fixable = sum(1 for issue in self.issues if issue.get('fixable', False))
        
        if total_fixable == 0:
            yield {
                'step': 'complete',
                'progress': 100,
                'message': '没有可自动修复的问题'
            }
            return
        
        logger.info(f"🔧 开始自动修复（共{total_fixable}个问题）...")
        
        current = 0
        
        for issue in self.issues:
            if not issue.get('fixable', False):
                continue
            
            current += 1
            progress = int((current / total_fixable) * 100)
            
            yield {
                'step': issue['category'],
                'progress': progress,
                'message': f"修复: {issue['message']}"
            }
            
            # 执行修复
            success = await self._apply_fix(issue)
            
            if success:
                self.fixes_applied.append(issue['message'])
                yield {
                    'step': issue['category'],
                    'progress': progress,
                    'message': f"✅ 已修复: {issue['message']}"
                }
            else:
                yield {
                    'step': issue['category'],
                    'progress': progress,
                    'message': f"❌ 修复失败: {issue['message']}"
                }
            
            await asyncio.sleep(0.1)  # 小延迟，便于UI更新
        
        yield {
            'step': 'complete',
            'progress': 100,
            'message': f'自动修复完成！成功{len(self.fixes_applied)}个'
        }
    
    async def _apply_fix(self, issue: Dict) -> bool:
        """
        应用单个修复
        
        Args:
            issue: 问题字典
            
        Returns:
            是否成功
        """
        category = issue['category']
        fix_command = issue.get('fix_command', '')
        
        try:
            if category == 'dependency':
                # 安装依赖
                package = issue['message'].split(': ')[1]
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    timeout=300
                )
                return result.returncode == 0
            
            elif category == 'chromium':
                # 安装Chromium
                if 'Playwright未安装' in issue['message']:
                    # 先安装playwright
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', 'playwright'],
                        capture_output=True,
                        timeout=300
                    )
                
                # 安装chromium
                result = subprocess.run(
                    ['playwright', 'install', 'chromium'],
                    capture_output=True,
                    timeout=600
                )
                return result.returncode == 0
            
            elif category == 'port':
                # 端口冲突 - 自动更换端口（这里只是记录，实际由配置管理）
                return True
            
            elif category == 'redis':
                # Redis - 启动内嵌版本（由系统自动处理）
                return True
            
            else:
                return False
        
        except Exception as e:
            logger.error(f"修复失败: {e}")
            return False


# 全局实例
environment_checker = EnvironmentChecker()


# API辅助函数
async def check_environment_with_progress():
    """
    执行环境检测并返回进度
    
    用于WebSocket实时反馈
    """
    checker = EnvironmentChecker()
    
    # 执行检测
    results = await checker.check_all()
    
    # 如果有问题，尝试自动修复
    if results['total_issues'] > 0:
        async for progress in checker.auto_fix():
            yield progress
    
    # 重新检测
    final_results = await checker.check_all()
    
    yield {
        'step': 'final',
        'progress': 100,
        'message': '环境检测完成',
        'results': final_results
    }


# Global instance
ultimate_env_checker = EnvironmentChecker()
