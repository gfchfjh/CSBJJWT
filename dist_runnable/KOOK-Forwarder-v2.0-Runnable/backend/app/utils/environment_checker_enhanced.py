"""
环境检查器（增强版）
P0-19: Playwright 浏览器检查
P0-20: 端口占用检查
P0-21: 网络连通性测试
P0-22: 一键修复功能
"""
import os
import sys
import asyncio
import socket
import subprocess
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple, Any
from playwright.async_api import async_playwright
from ..utils.logger import logger


class EnvironmentChecker:
    """环境检查器（增强版）"""
    
    def __init__(self):
        self.checks = []
        self.fixes = []
        
    async def check_all(self) -> Dict[str, Any]:
        """执行所有检查"""
        results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'fixable': []
        }
        
        # 定义检查项
        checks = [
            ('Python 版本', self.check_python_version),
            ('依赖库', self.check_dependencies),
            ('Playwright 浏览器', self.check_playwright_browser),
            ('Redis 连接', self.check_redis_connection),
            ('端口占用', self.check_ports),
            ('磁盘空间', self.check_disk_space),
            ('网络连通性', self.check_network_connectivity),
            ('写入权限', self.check_write_permissions),
        ]
        
        for name, check_func in checks:
            try:
                logger.info(f"检查: {name}")
                success, message, fixable = await check_func()
                
                result = {
                    'name': name,
                    'message': message,
                    'fixable': fixable
                }
                
                if success:
                    results['passed'].append(result)
                    logger.info(f"✅ {name}: {message}")
                else:
                    results['failed'].append(result)
                    logger.error(f"❌ {name}: {message}")
                    
                    if fixable:
                        results['fixable'].append(result)
                        logger.warning(f"🔧 可自动修复: {name}")
                        
            except Exception as e:
                logger.error(f"❌ {name} 检查异常: {str(e)}")
                results['failed'].append({
                    'name': name,
                    'message': f"检查异常: {str(e)}",
                    'fixable': False
                })
        
        # 生成摘要
        results['summary'] = {
            'total': len(checks),
            'passed': len(results['passed']),
            'failed': len(results['failed']),
            'fixable': len(results['fixable'])
        }
        
        return results
    
    async def check_python_version(self) -> Tuple[bool, str, bool]:
        """检查 Python 版本"""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            # 要求 Python 3.9+
            if version.major >= 3 and version.minor >= 9:
                return True, f"Python {version_str}", False
            else:
                return False, f"Python {version_str}（需要 3.9+）", False
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def check_dependencies(self) -> Tuple[bool, str, bool]:
        """检查依赖库"""
        try:
            required_packages = [
                'fastapi',
                'uvicorn',
                'playwright',
                'redis',
                'aiohttp',
                'cryptography',
                'Pillow',
                'orjson',
            ]
            
            missing = []
            for package in required_packages:
                try:
                    __import__(package.replace('-', '_'))
                except ImportError:
                    missing.append(package)
            
            if not missing:
                return True, f"所有依赖库已安装（共 {len(required_packages)} 个）", False
            else:
                return False, f"缺少依赖库: {', '.join(missing)}", True
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def check_playwright_browser(self) -> Tuple[bool, str, bool]:
        """检查 Playwright 浏览器"""
        try:
            # 检查浏览器路径
            playwright_dir = Path.home() / ".cache/ms-playwright"
            
            if sys.platform == "win32":
                pattern = "chromium-*/chrome-win/chrome.exe"
            elif sys.platform == "darwin":
                pattern = "chromium-*/chrome-mac/Chromium.app"
            else:
                pattern = "chromium-*/chrome-linux/chrome"
            
            matches = list(playwright_dir.glob(pattern))
            
            if not matches:
                return False, "Chromium 浏览器未安装", True
            
            # 验证浏览器可用性
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    await browser.close()
                
                return True, f"Chromium 浏览器可用（路径: {matches[0].parent}）", False
                
            except Exception as e:
                return False, f"Chromium 浏览器无法启动: {str(e)}", True
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", True
    
    async def check_redis_connection(self) -> Tuple[bool, str, bool]:
        """检查 Redis 连接"""
        try:
            import redis.asyncio as aioredis
            
            redis_client = aioredis.from_url(
                "redis://127.0.0.1:6379/0",
                encoding="utf-8",
                decode_responses=True
            )
            
            try:
                await redis_client.ping()
                await redis_client.close()
                return True, "Redis 连接正常", False
            except Exception as e:
                return False, f"Redis 连接失败: {str(e)}", True
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def check_ports(self) -> Tuple[bool, str, bool]:
        """检查端口占用"""
        try:
            ports_to_check = [
                (9527, "后端 API"),
                (6379, "Redis"),
                (9528, "图床服务"),
            ]
            
            occupied = []
            
            for port, name in ports_to_check:
                if self._is_port_in_use(port):
                    occupied.append(f"{name}({port})")
            
            if not occupied:
                return True, "所有端口可用", False
            else:
                return False, f"端口被占用: {', '.join(occupied)}", True
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except:
            return False
    
    async def check_disk_space(self) -> Tuple[bool, str, bool]:
        """检查磁盘空间"""
        try:
            import shutil
            
            # 检查数据目录空间
            data_dir = Path.home() / "Documents/KookForwarder/data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            stat = shutil.disk_usage(data_dir)
            free_gb = stat.free / (1024 ** 3)
            
            # 要求至少 1GB 可用空间
            if free_gb >= 1.0:
                return True, f"磁盘空间充足（{free_gb:.2f} GB 可用）", False
            else:
                return False, f"磁盘空间不足（仅 {free_gb:.2f} GB 可用，建议至少 1GB）", False
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def check_network_connectivity(self) -> Tuple[bool, str, bool]:
        """检查网络连通性"""
        try:
            urls_to_test = [
                ('https://www.kookapp.cn', 'KOOK 官网'),
                ('https://discord.com', 'Discord'),
                ('https://api.telegram.org', 'Telegram'),
            ]
            
            failed = []
            
            async with aiohttp.ClientSession() as session:
                for url, name in urls_to_test:
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                            if resp.status >= 400:
                                failed.append(f"{name}(HTTP {resp.status})")
                    except asyncio.TimeoutError:
                        failed.append(f"{name}(超时)")
                    except Exception as e:
                        failed.append(f"{name}({str(e)})")
            
            if not failed:
                return True, "网络连接正常", False
            else:
                return False, f"无法访问: {', '.join(failed)}", False
                
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def check_write_permissions(self) -> Tuple[bool, str, bool]:
        """检查写入权限"""
        try:
            test_dirs = [
                Path.home() / "Documents/KookForwarder",
                Path.home() / "Documents/KookForwarder/data",
                Path.home() / "Documents/KookForwarder/data/images",
                Path.home() / "Documents/KookForwarder/data/redis",
                Path.home() / "Documents/KookForwarder/data/logs",
            ]
            
            for dir_path in test_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # 尝试写入测试文件
                test_file = dir_path / ".write_test"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                except Exception as e:
                    return False, f"无法写入 {dir_path}: {str(e)}", False
            
            return True, "所有目录可写", False
            
        except Exception as e:
            return False, f"检查失败: {str(e)}", False
    
    async def auto_fix(self, issue_name: str) -> Tuple[bool, str]:
        """自动修复问题"""
        logger.info(f"🔧 尝试自动修复: {issue_name}")
        
        if issue_name == "依赖库":
            return await self._fix_dependencies()
        elif issue_name == "Playwright 浏览器":
            return await self._fix_playwright_browser()
        elif issue_name == "Redis 连接":
            return await self._fix_redis_connection()
        elif issue_name == "端口占用":
            return await self._fix_ports()
        else:
            return False, f"未知问题: {issue_name}"
    
    async def _fix_dependencies(self) -> Tuple[bool, str]:
        """修复依赖库"""
        try:
            logger.info("📦 安装缺失的依赖库...")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, "依赖库安装成功"
            else:
                return False, f"依赖库安装失败: {result.stderr}"
                
        except Exception as e:
            return False, f"修复失败: {str(e)}"
    
    async def _fix_playwright_browser(self) -> Tuple[bool, str]:
        """修复 Playwright 浏览器"""
        try:
            logger.info("🌐 安装 Chromium 浏览器...")
            
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return True, "Chromium 浏览器安装成功"
            else:
                return False, f"Chromium 安装失败: {result.stderr}"
                
        except Exception as e:
            return False, f"修复失败: {str(e)}"
    
    async def _fix_redis_connection(self) -> Tuple[bool, str]:
        """修复 Redis 连接"""
        try:
            logger.info("📦 启动嵌入式 Redis...")
            
            from ..utils.redis_manager_enhanced import redis_manager
            
            success, message = await redis_manager.start()
            return success, message
            
        except Exception as e:
            return False, f"修复失败: {str(e)}"
    
    async def _fix_ports(self) -> Tuple[bool, str]:
        """修复端口占用（尝试使用其他端口）"""
        try:
            logger.info("🔧 尝试释放被占用的端口或使用备用端口...")
            
            # 这里可以实现：
            # 1. 检测占用端口的进程并询问是否关闭
            # 2. 使用备用端口（9527 -> 9537 -> 9547）
            # 3. 更新配置文件
            
            return False, "端口占用问题需要手动处理（请关闭占用端口的程序）"
            
        except Exception as e:
            return False, f"修复失败: {str(e)}"


# 全局实例
environment_checker = EnvironmentChecker()
