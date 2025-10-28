"""
🔍 P0-5优化: 环境检测与自动修复系统（终极版）

功能：
1. 并发检测6项环境（5-10秒完成）
2. Python版本检测（3.11+）
3. Chromium浏览器检测
4. Redis服务检测
5. 网络连接检测（3个测试点）
6. 端口可用性检测（9527/6379/9528）
7. 磁盘空间检测（至少5GB）
8. 自动修复功能

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
import asyncio
import sys
import shutil
import psutil
import platform
from typing import Dict, List, Optional
from pathlib import Path
from ..utils.logger import logger


class EnvironmentChecker:
    """环境检测器（并发优化版）"""
    
    def __init__(self):
        self.python_required = (3, 11)
        self.disk_required_gb = 5
        self.required_ports = [9527, 6379, 9528]
        
        # 网络测试点
        self.network_test_urls = [
            'https://www.kookapp.cn',
            'https://discord.com',
            'https://api.telegram.org'
        ]
    
    async def check_all_concurrent(self) -> Dict[str, any]:
        """
        并发检查所有环境（5-10秒完成）
        
        Returns:
            检查结果字典
        """
        import time
        start_time = time.time()
        
        logger.info("🔍 开始并发环境检测...")
        
        # 并发执行所有检查
        results = await asyncio.gather(
            self.check_python_version(),
            self.check_chromium(),
            self.check_redis(),
            self.check_network(),
            self.check_ports(),
            self.check_disk_space(),
            return_exceptions=True
        )
        
        elapsed = time.time() - start_time
        
        # 整理结果
        check_results = {
            'python': results[0] if not isinstance(results[0], Exception) else self._error_result('Python', results[0]),
            'chromium': results[1] if not isinstance(results[1], Exception) else self._error_result('Chromium', results[1]),
            'redis': results[2] if not isinstance(results[2], Exception) else self._error_result('Redis', results[2]),
            'network': results[3] if not isinstance(results[3], Exception) else self._error_result('Network', results[3]),
            'ports': results[4] if not isinstance(results[4], Exception) else self._error_result('Ports', results[4]),
            'disk': results[5] if not isinstance(results[5], Exception) else self._error_result('Disk', results[5]),
        }
        
        # 计算总体状态
        all_passed = all(
            r['passed'] for r in check_results.values()
            if isinstance(r, dict)
        )
        
        result = {
            'elapsed': round(elapsed, 2),
            'all_passed': all_passed,
            **check_results
        }
        
        logger.info(f"✅ 环境检测完成，耗时{elapsed:.2f}秒，{'全部通过' if all_passed else '存在问题'}")
        
        return result
    
    def _error_result(self, name: str, exception: Exception) -> Dict:
        """生成错误结果"""
        return {
            'name': name,
            'passed': False,
            'message': f'❌ 检测异常: {str(exception)}',
            'fix_available': False
        }
    
    async def check_python_version(self) -> Dict:
        """检查Python版本"""
        version = sys.version_info
        required = self.python_required
        
        passed = version >= required
        
        return {
            'name': 'Python版本',
            'passed': passed,
            'current': f"{version.major}.{version.minor}.{version.micro}",
            'required': f"{required[0]}.{required[1]}+",
            'platform': platform.python_implementation(),
            'fix_available': False,
            'fix_command': None,
            'message': f'✅ Python {version.major}.{version.minor}.{version.micro} 符合要求' if passed
                      else f'❌ Python版本过低（{version.major}.{version.minor}），需要{required[0]}.{required[1]}+',
            'details': {
                'executable': sys.executable,
                'version_full': sys.version
            }
        }
    
    async def check_chromium(self) -> Dict:
        """检查Chromium浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            # 尝试启动Playwright
            p = await async_playwright().start()
            
            try:
                # 检查Chromium可执行文件
                executable_path = p.chromium.executable_path
                
                if not Path(executable_path).exists():
                    raise FileNotFoundError(f"Chromium不存在: {executable_path}")
                
                # 尝试启动浏览器
                browser = await p.chromium.launch(headless=True)
                version = browser.version
                await browser.close()
                
                await p.stop()
                
                return {
                    'name': 'Chromium浏览器',
                    'passed': True,
                    'message': f'✅ Chromium {version} 已安装且可用',
                    'version': version,
                    'executable': str(executable_path),
                    'fix_available': False
                }
            
            finally:
                try:
                    await p.stop()
                except:
                    pass
        
        except ImportError:
            return {
                'name': 'Chromium浏览器',
                'passed': False,
                'message': '❌ Playwright未安装',
                'fix_available': True,
                'fix_command': 'pip install playwright',
                'fix_description': '安装Playwright库'
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # 判断是否是Chromium未安装
            if 'Executable doesn\'t exist' in error_msg or 'not found' in error_msg.lower():
                return {
                    'name': 'Chromium浏览器',
                    'passed': False,
                    'message': '❌ Chromium未安装',
                    'fix_available': True,
                    'fix_command': 'playwright install chromium',
                    'fix_description': '自动下载并安装Chromium浏览器'
                }
            else:
                return {
                    'name': 'Chromium浏览器',
                    'passed': False,
                    'message': f'❌ Chromium检测失败: {error_msg}',
                    'fix_available': True,
                    'fix_command': 'playwright install chromium',
                    'fix_description': '重新安装Chromium浏览器'
                }
    
    async def check_redis(self) -> Dict:
        """检查Redis服务"""
        try:
            import redis.asyncio as aioredis
            
            # 尝试连接Redis
            r = await aioredis.from_url(
                'redis://localhost:6379',
                socket_connect_timeout=3
            )
            
            # 发送PING命令
            response = await r.ping()
            
            # 获取Redis信息
            info = await r.info()
            redis_version = info.get('redis_version', 'unknown')
            
            await r.close()
            
            if response:
                return {
                    'name': 'Redis服务',
                    'passed': True,
                    'message': f'✅ Redis {redis_version} 运行正常',
                    'version': redis_version,
                    'fix_available': False,
                    'details': {
                        'port': 6379,
                        'uptime_seconds': info.get('uptime_in_seconds', 0),
                        'connected_clients': info.get('connected_clients', 0)
                    }
                }
        
        except ImportError:
            return {
                'name': 'Redis服务',
                'passed': False,
                'message': '❌ Redis库未安装',
                'fix_available': True,
                'fix_command': 'pip install redis',
                'fix_description': '安装Redis Python客户端'
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # 判断错误类型
            if 'Connection refused' in error_msg:
                return {
                    'name': 'Redis服务',
                    'passed': False,
                    'message': '❌ Redis未启动',
                    'fix_available': True,
                    'fix_command': 'auto_start_redis',
                    'fix_description': '自动启动嵌入式Redis服务'
                }
            elif 'Timeout' in error_msg:
                return {
                    'name': 'Redis服务',
                    'passed': False,
                    'message': '❌ Redis连接超时',
                    'fix_available': True,
                    'fix_command': 'auto_start_redis',
                    'fix_description': '重新启动Redis服务'
                }
            else:
                return {
                    'name': 'Redis服务',
                    'passed': False,
                    'message': f'❌ Redis连接失败: {error_msg}',
                    'fix_available': True,
                    'fix_command': 'auto_start_redis',
                    'fix_description': '尝试启动Redis服务'
                }
    
    async def check_network(self) -> Dict:
        """检查网络连接（3个测试点）"""
        import aiohttp
        
        results = {}
        
        for url in self.network_test_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        results[url] = {
                            'success': resp.status == 200,
                            'status': resp.status,
                            'time': resp.headers.get('Date', 'unknown')
                        }
            except asyncio.TimeoutError:
                results[url] = {
                    'success': False,
                    'error': 'Timeout'
                }
            except Exception as e:
                results[url] = {
                    'success': False,
                    'error': str(e)
                }
        
        # 计算成功率
        success_count = sum(1 for r in results.values() if r.get('success'))
        total_count = len(results)
        passed = success_count >= 2  # 至少2个可达
        
        return {
            'name': '网络连接',
            'passed': passed,
            'message': f'{"✅" if passed else "⚠️"} 网络{'正常' if passed else '不稳定'} ({success_count}/{total_count}可达)',
            'success_count': success_count,
            'total_count': total_count,
            'fix_available': False,
            'details': results
        }
    
    async def check_ports(self) -> Dict:
        """检查端口可用性"""
        occupied = []
        
        for port in self.required_ports:
            if self._is_port_in_use(port):
                process_info = self._get_process_using_port(port)
                occupied.append({
                    'port': port,
                    'process': process_info
                })
        
        if not occupied:
            return {
                'name': '端口可用性',
                'passed': True,
                'message': f'✅ 所有端口可用 ({", ".join(map(str, self.required_ports))})',
                'ports': self.required_ports,
                'fix_available': False
            }
        else:
            port_list = [str(p['port']) for p in occupied]
            return {
                'name': '端口可用性',
                'passed': False,
                'message': f'❌ 端口被占用: {", ".join(port_list)}',
                'occupied_ports': occupied,
                'fix_available': True,
                'fix_command': 'kill_processes',
                'fix_description': '自动终止占用端口的进程（仅python/node/redis）'
            }
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        
        return False
    
    def _get_process_using_port(self, port: int) -> Optional[Dict]:
        """获取占用端口的进程信息"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'name': process.name(),
                            'exe': process.exe(),
                            'cmdline': ' '.join(process.cmdline())
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {
                            'pid': conn.pid,
                            'name': 'Unknown',
                            'exe': 'Unknown'
                        }
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        
        return None
    
    async def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        try:
            data_dir = Path.home() / "Documents" / "KookForwarder"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取磁盘使用情况
            disk = psutil.disk_usage(str(data_dir))
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            used_percent = disk.percent
            
            required_gb = self.disk_required_gb
            passed = free_gb >= required_gb
            
            return {
                'name': '磁盘空间',
                'passed': passed,
                'message': f'{"✅" if passed else "❌"} 磁盘空间{"充足" if passed else "不足"} ({free_gb:.2f}GB可用/{total_gb:.2f}GB总计)',
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'used_percent': used_percent,
                'required_gb': required_gb,
                'fix_available': False,
                'details': {
                    'data_dir': str(data_dir),
                    'filesystem': disk._asdict() if hasattr(disk, '_asdict') else {}
                }
            }
        
        except Exception as e:
            return {
                'name': '磁盘空间',
                'passed': False,
                'message': f'❌ 磁盘检查失败: {str(e)}',
                'fix_available': False
            }
    
    async def auto_fix(self, check_name: str) -> Dict:
        """
        自动修复问题
        
        Args:
            check_name: 检查项名称（python/chromium/redis/ports）
            
        Returns:
            修复结果
        """
        logger.info(f"🔧 开始自动修复: {check_name}")
        
        if check_name == 'chromium':
            return await self._fix_chromium()
        elif check_name == 'redis':
            return await self._fix_redis()
        elif check_name == 'ports':
            return await self._fix_ports()
        else:
            return {
                'success': False,
                'message': f'不支持自动修复: {check_name}'
            }
    
    async def _fix_chromium(self) -> Dict:
        """自动安装Chromium"""
        try:
            logger.info("📥 正在下载并安装Chromium...")
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'playwright', 'install', 'chromium',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5分钟超时
            )
            
            if process.returncode == 0:
                logger.info("✅ Chromium安装成功")
                return {
                    'success': True,
                    'message': '✅ Chromium安装成功',
                    'output': stdout.decode() if stdout else ''
                }
            else:
                error_msg = stderr.decode() if stderr else 'Unknown error'
                logger.error(f"❌ Chromium安装失败: {error_msg}")
                return {
                    'success': False,
                    'message': f'❌ Chromium安装失败: {error_msg}'
                }
        
        except asyncio.TimeoutError:
            return {
                'success': False,
                'message': '❌ Chromium安装超时（5分钟）'
            }
        except Exception as e:
            logger.error(f"❌ Chromium安装异常: {str(e)}")
            return {
                'success': False,
                'message': f'❌ 安装异常: {str(e)}'
            }
    
    async def _fix_redis(self) -> Dict:
        """自动启动Redis"""
        try:
            from ..utils.redis_manager_enhanced import redis_manager
            
            logger.info("🚀 正在启动Redis服务...")
            
            success, message = await redis_manager.start()
            
            if success:
                logger.info("✅ Redis启动成功")
            else:
                logger.error(f"❌ Redis启动失败: {message}")
            
            return {
                'success': success,
                'message': message
            }
        
        except ImportError:
            return {
                'success': False,
                'message': '❌ Redis管理器未安装'
            }
        except Exception as e:
            logger.error(f"❌ Redis启动异常: {str(e)}")
            return {
                'success': False,
                'message': f'❌ Redis启动失败: {str(e)}'
            }
    
    async def _fix_ports(self) -> Dict:
        """自动清理占用的端口"""
        try:
            check_result = await self.check_ports()
            
            if check_result['passed']:
                return {
                    'success': True,
                    'message': '✅ 端口已可用'
                }
            
            occupied = check_result.get('occupied_ports', [])
            killed = []
            failed = []
            
            for port_info in occupied:
                process_info = port_info['process']
                pid = process_info['pid']
                process_name = process_info['name']
                
                try:
                    # 仅kill特定进程（避免误杀系统进程）
                    safe_names = ['python', 'python.exe', 'node', 'node.exe', 'redis-server', 'redis-server.exe']
                    
                    if any(name.lower() in process_name.lower() for name in safe_names):
                        process = psutil.Process(pid)
                        process.terminate()
                        
                        # 等待进程结束
                        try:
                            process.wait(timeout=5)
                            killed.append(f"{process_name}(PID:{pid},端口:{port_info['port']})")
                            logger.info(f"✅ 已终止进程: {process_name}(PID:{pid})")
                        except psutil.TimeoutExpired:
                            # 强制kill
                            process.kill()
                            killed.append(f"{process_name}(PID:{pid},端口:{port_info['port']},强制)")
                            logger.info(f"✅ 已强制终止进程: {process_name}(PID:{pid})")
                    else:
                        failed.append(f"{process_name}(PID:{pid},端口:{port_info['port']},不安全)")
                        logger.warning(f"⚠️  跳过进程（不安全）: {process_name}(PID:{pid})")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    failed.append(f"{process_name}(PID:{pid},端口:{port_info['port']},{str(e)})")
                    logger.error(f"❌ 终止进程失败: {process_name}(PID:{pid}) - {str(e)}")
            
            if killed:
                message = f'✅ 已终止进程: {", ".join(killed)}'
                if failed:
                    message += f'\n⚠️  跳过进程: {", ".join(failed)}'
                
                return {
                    'success': True,
                    'message': message,
                    'killed': killed,
                    'failed': failed
                }
            else:
                return {
                    'success': False,
                    'message': f'❌ 无法自动终止进程，请手动处理: {", ".join(failed)}',
                    'failed': failed
                }
        
        except Exception as e:
            logger.error(f"❌ 端口清理异常: {str(e)}")
            return {
                'success': False,
                'message': f'❌ 端口清理失败: {str(e)}'
            }
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': sys.version,
            'hostname': platform.node(),
            'processor': platform.processor()
        }


# 创建全局实例
environment_checker = EnvironmentChecker()
