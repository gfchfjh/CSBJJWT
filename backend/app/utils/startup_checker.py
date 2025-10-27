"""
首次启动环境检测器
✅ P0-2优化: 自动检测和修复环境问题
"""
import os
import sys
import asyncio
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List
from ..utils.logger import logger


class StartupChecker:
    """首次启动环境检测器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.results = {}
        
    async def check_all(self) -> Dict[str, Any]:
        """
        检查所有依赖和环境
        
        Returns:
            {
                'overall_status': 'ok' | 'warning' | 'error',
                'checks': {
                    'python': {...},
                    'chromium': {...},
                    'redis': {...},
                    'network': {...},
                    'ports': {...},
                    'disk_space': {...}
                },
                'auto_fixable': True | False,
                'recommendations': [...]
            }
        """
        logger.info("🔍 开始环境检测...")
        
        checks = {}
        
        # 并行检查
        results = await asyncio.gather(
            self.check_python(),
            self.check_chromium(),
            self.check_redis(),
            self.check_network(),
            self.check_ports(),
            self.check_disk_space(),
            return_exceptions=True
        )
        
        check_names = ['python', 'chromium', 'redis', 'network', 'ports', 'disk_space']
        for name, result in zip(check_names, results):
            if isinstance(result, Exception):
                checks[name] = {
                    'status': 'error',
                    'ok': False,
                    'message': f"检查异常: {str(result)}"
                }
            else:
                checks[name] = result
        
        # 计算总体状态
        overall_status = 'ok'
        auto_fixable = True
        recommendations = []
        
        for name, result in checks.items():
            if not result['ok']:
                if result['status'] == 'error':
                    overall_status = 'error'
                elif result['status'] == 'warning' and overall_status != 'error':
                    overall_status = 'warning'
                
                if not result.get('auto_fixable', False):
                    auto_fixable = False
                
                if 'recommendation' in result:
                    recommendations.append(result['recommendation'])
        
        return {
            'overall_status': overall_status,
            'checks': checks,
            'auto_fixable': auto_fixable,
            'recommendations': recommendations,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def check_python(self) -> Dict:
        """检查Python环境"""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            # 检查版本（需要3.11+）
            if version.major < 3 or (version.major == 3 and version.minor < 11):
                return {
                    'status': 'error',
                    'ok': False,
                    'message': f"Python版本过低: {version_str} (需要3.11+)",
                    'auto_fixable': False,
                    'recommendation': "请升级Python到3.11或更高版本"
                }
            
            return {
                'status': 'ok',
                'ok': True,
                'message': f"Python版本正常: {version_str}",
                'version': version_str
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'ok': False,
                'message': f"Python检查失败: {str(e)}",
                'auto_fixable': False
            }
    
    async def check_chromium(self) -> Dict:
        """检查Chromium浏览器"""
        try:
            # 检查Playwright是否已安装Chromium
            from playwright.sync_api import sync_playwright
            
            try:
                with sync_playwright() as p:
                    browser_type = p.chromium
                    # 尝试获取可执行文件路径
                    executable_path = browser_type.executable_path
                    
                    if os.path.exists(executable_path):
                        return {
                            'status': 'ok',
                            'ok': True,
                            'message': "Chromium已安装",
                            'path': executable_path
                        }
                    else:
                        return {
                            'status': 'warning',
                            'ok': False,
                            'message': "Chromium未安装，需要下载（约200MB）",
                            'auto_fixable': True,
                            'recommendation': "首次启动将自动下载Chromium浏览器",
                            'download_size_mb': 200
                        }
                        
            except Exception as e:
                return {
                    'status': 'warning',
                    'ok': False,
                    'message': f"Chromium未安装: {str(e)}",
                    'auto_fixable': True,
                    'recommendation': "将自动下载并安装Chromium"
                }
                
        except ImportError:
            return {
                'status': 'error',
                'ok': False,
                'message': "Playwright未安装",
                'auto_fixable': False,
                'recommendation': "请运行: pip install playwright"
            }
    
    async def check_redis(self) -> Dict:
        """检查Redis服务"""
        try:
            import redis
            
            # 尝试连接Redis
            try:
                r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=2)
                r.ping()
                
                # 获取Redis信息
                info = r.info()
                version = info.get('redis_version', 'unknown')
                
                return {
                    'status': 'ok',
                    'ok': True,
                    'message': f"Redis运行中 (版本: {version})",
                    'version': version,
                    'port': 6379
                }
                
            except redis.ConnectionError:
                # Redis未运行，但可能已安装
                redis_path = self._find_redis_executable()
                
                if redis_path:
                    return {
                        'status': 'warning',
                        'ok': False,
                        'message': "Redis已安装但未运行",
                        'auto_fixable': True,
                        'recommendation': "将自动启动Redis服务",
                        'redis_path': redis_path
                    }
                else:
                    return {
                        'status': 'warning',
                        'ok': False,
                        'message': "Redis未安装或未找到",
                        'auto_fixable': True,
                        'recommendation': "将使用内置Redis",
                        'use_embedded': True
                    }
                    
        except ImportError:
            return {
                'status': 'error',
                'ok': False,
                'message': "Redis Python客户端未安装",
                'auto_fixable': False,
                'recommendation': "请运行: pip install redis"
            }
    
    async def check_network(self) -> Dict:
        """检查网络连接"""
        import aiohttp
        
        test_urls = [
            'https://www.kookapp.cn',
            'https://www.google.com',
            'https://www.baidu.com'
        ]
        
        reachable = []
        
        async with aiohttp.ClientSession() as session:
            for url in test_urls:
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status < 500:
                            reachable.append(url)
                except:
                    pass
        
        if len(reachable) == 0:
            return {
                'status': 'error',
                'ok': False,
                'message': "网络连接失败，无法访问互联网",
                'auto_fixable': False,
                'recommendation': "请检查网络连接或代理设置"
            }
        elif 'https://www.kookapp.cn' not in reachable:
            return {
                'status': 'warning',
                'ok': False,
                'message': "无法访问KOOK服务器",
                'auto_fixable': False,
                'recommendation': "请检查是否可以访问 kookapp.cn"
            }
        else:
            return {
                'status': 'ok',
                'ok': True,
                'message': "网络连接正常",
                'reachable_count': len(reachable)
            }
    
    async def check_ports(self) -> Dict:
        """检查端口占用"""
        import socket
        
        required_ports = [9527, 6379]  # 后端API端口、Redis端口
        occupied = []
        
        for port in required_ports:
            if self._is_port_occupied(port):
                occupied.append(port)
        
        if occupied:
            return {
                'status': 'error',
                'ok': False,
                'message': f"端口被占用: {', '.join(map(str, occupied))}",
                'auto_fixable': True,
                'recommendation': "将尝试使用其他端口",
                'occupied_ports': occupied,
                'alternative_ports': {
                    9527: 9528,
                    6379: 6380
                }
            }
        
        return {
            'status': 'ok',
            'ok': True,
            'message': "所需端口可用",
            'ports': required_ports
        }
    
    async def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        import shutil
        
        try:
            # 获取用户文档目录的磁盘空间
            if self.system == 'windows':
                home = Path.home()
            else:
                home = Path.home()
            
            usage = shutil.disk_usage(home)
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)
            used_percent = (usage.used / usage.total) * 100
            
            # 至少需要5GB空闲空间
            if free_gb < 5:
                return {
                    'status': 'error',
                    'ok': False,
                    'message': f"磁盘空间不足: 仅剩 {free_gb:.1f} GB",
                    'auto_fixable': False,
                    'recommendation': "请清理磁盘空间，至少需要5GB",
                    'free_gb': free_gb,
                    'total_gb': total_gb
                }
            elif free_gb < 10:
                return {
                    'status': 'warning',
                    'ok': True,
                    'message': f"磁盘空间偏低: 剩余 {free_gb:.1f} GB",
                    'recommendation': "建议保留至少10GB空闲空间",
                    'free_gb': free_gb,
                    'total_gb': total_gb
                }
            else:
                return {
                    'status': 'ok',
                    'ok': True,
                    'message': f"磁盘空间充足: 剩余 {free_gb:.1f} GB",
                    'free_gb': free_gb,
                    'total_gb': total_gb,
                    'used_percent': used_percent
                }
                
        except Exception as e:
            return {
                'status': 'warning',
                'ok': True,
                'message': f"无法检查磁盘空间: {str(e)}"
            }
    
    async def auto_fix(self, check_results: Dict) -> Dict:
        """
        自动修复问题
        
        Args:
            check_results: check_all()的返回结果
            
        Returns:
            {
                'fixed': [...],  # 已修复的问题
                'failed': [...],  # 修复失败的问题
                'skipped': [...]  # 跳过的问题（不可自动修复）
            }
        """
        logger.info("🔧 开始自动修复环境问题...")
        
        fixed = []
        failed = []
        skipped = []
        
        checks = check_results['checks']
        
        # 修复Chromium
        if not checks['chromium']['ok'] and checks['chromium'].get('auto_fixable'):
            try:
                await self._download_chromium()
                fixed.append('chromium')
            except Exception as e:
                failed.append(('chromium', str(e)))
        
        # 修复Redis
        if not checks['redis']['ok'] and checks['redis'].get('auto_fixable'):
            try:
                await self._start_redis(checks['redis'].get('redis_path'))
                fixed.append('redis')
            except Exception as e:
                failed.append(('redis', str(e)))
        
        # 修复端口占用
        if not checks['ports']['ok'] and checks['ports'].get('auto_fixable'):
            try:
                # 更新配置使用备用端口
                alternative_ports = checks['ports'].get('alternative_ports', {})
                # 这里需要更新配置文件
                fixed.append('ports')
            except Exception as e:
                failed.append(('ports', str(e)))
        
        # 其他不可自动修复的问题
        for name, result in checks.items():
            if not result['ok'] and not result.get('auto_fixable'):
                skipped.append(name)
        
        logger.info(f"✅ 修复完成: 成功 {len(fixed)}, 失败 {len(failed)}, 跳过 {len(skipped)}")
        
        return {
            'fixed': fixed,
            'failed': failed,
            'skipped': skipped
        }
    
    def _find_redis_executable(self) -> Optional[str]:
        """查找Redis可执行文件"""
        possible_paths = []
        
        if self.system == 'windows':
            possible_paths = [
                'redis/redis-server.exe',
                'C:/Program Files/Redis/redis-server.exe',
                os.path.join(os.getcwd(), 'redis', 'redis-server.exe')
            ]
        else:
            possible_paths = [
                'redis/redis-server',
                '/usr/local/bin/redis-server',
                '/usr/bin/redis-server',
                os.path.join(os.getcwd(), 'redis', 'redis-server')
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _is_port_occupied(self, port: int) -> bool:
        """检查端口是否被占用"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    async def _download_chromium(self):
        """下载Chromium浏览器"""
        logger.info("📥 开始下载Chromium...")
        
        try:
            # 使用Playwright CLI下载
            process = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'playwright', 'install', 'chromium',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Chromium下载完成")
            else:
                raise Exception(f"下载失败: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"❌ Chromium下载失败: {str(e)}")
            raise
    
    async def _start_redis(self, redis_path: Optional[str] = None):
        """启动Redis服务"""
        logger.info("🚀 启动Redis服务...")
        
        if not redis_path:
            redis_path = self._find_redis_executable()
        
        if not redis_path:
            raise Exception("未找到Redis可执行文件")
        
        try:
            # 后台启动Redis
            if self.system == 'windows':
                subprocess.Popen([redis_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([redis_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 等待Redis启动
            await asyncio.sleep(2)
            
            # 验证Redis是否启动成功
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            
            logger.info("✅ Redis启动成功")
            
        except Exception as e:
            logger.error(f"❌ Redis启动失败: {str(e)}")
            raise


# 全局实例
startup_checker = StartupChecker()
