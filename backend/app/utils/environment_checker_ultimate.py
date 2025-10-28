"""
终极环境检查器
✅ P0-5深度优化: 6项并发检测 + 自动修复
"""
import asyncio
import aiohttp
import shutil
import socket
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from ..utils.logger import logger
from ..config import settings


class UltimateEnvironmentChecker:
    """终极环境检查器"""
    
    async def check_all_concurrent(self) -> Dict:
        """
        并发执行所有检查（5-10秒内完成）
        
        Returns:
            完整的检查结果
        """
        start_time = asyncio.get_event_loop().time()
        
        logger.info("🔍 开始并发环境检测...")
        
        # 🔥 并发执行所有检查
        results = await asyncio.gather(
            self._check_python(),
            self._check_chromium(),
            self._check_redis(),
            self._check_network(),
            self._check_ports(),
            self._check_disk_space(),
            return_exceptions=True
        )
        
        python_ok, chromium_ok, redis_ok, network_ok, ports_ok, disk_ok = results
        
        duration = asyncio.get_event_loop().time() - start_time
        
        # 收集可修复的问题
        fixable_issues = []
        
        if not chromium_ok.get("installed", False):
            fixable_issues.append({
                "issue": "Chromium未安装",
                "fix_command": "playwright install chromium --with-deps",
                "severity": "critical"
            })
        
        if not redis_ok.get("running", False):
            fixable_issues.append({
                "issue": "Redis未运行",
                "fix_command": "启动内置Redis服务",
                "severity": "critical"
            })
        
        if not ports_ok.get("all_available", False):
            occupied_ports = [
                port for port, info in ports_ok.get("results", {}).items()
                if not info.get("available", True)
            ]
            if occupied_ports:
                fixable_issues.append({
                    "issue": f"端口被占用: {occupied_ports}",
                    "fix_command": "kill_process_by_port",
                    "severity": "warning"
                })
        
        # 判断是否全部通过
        all_passed = all([
            python_ok.get("version_ok", False),
            chromium_ok.get("installed", False),
            redis_ok.get("running", False),
            network_ok.get("all_reachable", False),
            ports_ok.get("all_available", False),
            disk_ok.get("sufficient", False)
        ])
        
        logger.info(f"✅ 环境检测完成（耗时{duration:.2f}秒）")
        
        return {
            "all_passed": all_passed,
            "duration": round(duration, 2),
            "results": {
                "python": python_ok,
                "chromium": chromium_ok,
                "redis": redis_ok,
                "network": network_ok,
                "ports": ports_ok,
                "disk_space": disk_ok
            },
            "fixable_issues": fixable_issues,
            "summary": {
                "total_checks": 6,
                "passed_checks": sum([
                    python_ok.get("version_ok", False),
                    chromium_ok.get("installed", False),
                    redis_ok.get("running", False),
                    network_ok.get("all_reachable", False),
                    ports_ok.get("all_available", False),
                    disk_ok.get("sufficient", False)
                ]),
                "critical_issues": len([i for i in fixable_issues if i.get("severity") == "critical"])
            }
        }
    
    async def _check_python(self) -> Dict:
        """检查Python版本（需要3.11+）"""
        try:
            version = sys.version_info
            version_ok = version.major == 3 and version.minor >= 11
            
            return {
                "version": f"{version.major}.{version.minor}.{version.micro}",
                "version_ok": version_ok,
                "required": "3.11+",
                "status": "✅ 正常" if version_ok else "❌ 版本过低"
            }
        except Exception as e:
            return {"error": str(e), "status": "❌ 检测失败"}
    
    async def _check_chromium(self) -> Dict:
        """检查Chromium浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser_path = p.chromium.executable_path
                installed = Path(browser_path).exists() if browser_path else False
                
                return {
                    "installed": installed,
                    "path": str(browser_path) if installed else None,
                    "status": "✅ 已安装" if installed else "❌ 未安装"
                }
        except Exception as e:
            return {"installed": False, "error": str(e), "status": "❌ 检测失败"}
    
    async def _check_redis(self) -> Dict:
        """检查Redis服务"""
        try:
            from ..queue.redis_client import redis_queue
            
            await redis_queue.connect()
            running = redis_queue.is_connected()
            
            return {
                "running": running,
                "host": settings.redis_host,
                "port": settings.redis_port,
                "status": "✅ 运行中" if running else "❌ 未运行"
            }
        except Exception as e:
            return {"running": False, "error": str(e), "status": "❌ 连接失败"}
    
    async def _check_network(self) -> Dict:
        """检查网络连接（3个测试点）"""
        test_urls = [
            "https://www.kookapp.cn",
            "https://discord.com/api/v10",
            "https://api.telegram.org"
        ]
        
        results = {}
        
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for url in test_urls:
                try:
                    async with session.get(url) as resp:
                        results[url] = resp.status in [200, 301, 302]
                except:
                    results[url] = False
        
        all_reachable = all(results.values())
        reachable_count = sum(results.values())
        
        return {
            "all_reachable": all_reachable,
            "results": results,
            "status": f"✅ {reachable_count}/3 可达" if all_reachable else f"⚠️ {reachable_count}/3 可达"
        }
    
    async def _check_ports(self) -> Dict:
        """检查端口可用性（9527/6379/9528）"""
        ports_to_check = [
            (settings.api_port, "API服务"),
            (settings.redis_port, "Redis"),
            (settings.image_server_port, "图床服务")
        ]
        
        results = {}
        
        for port, name in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            try:
                sock.bind(('127.0.0.1', port))
                sock.close()
                results[port] = {"available": True, "name": name}
            except:
                results[port] = {"available": False, "name": name}
        
        all_available = all(r["available"] for r in results.values())
        
        return {
            "all_available": all_available,
            "results": results,
            "status": "✅ 全部可用" if all_available else "⚠️ 部分端口被占用"
        }
    
    async def _check_disk_space(self) -> Dict:
        """检查磁盘空间（至少5GB）"""
        try:
            stat = shutil.disk_usage(settings.data_dir)
            
            free_gb = stat.free / (1024 ** 3)
            sufficient = free_gb >= 5.0
            
            return {
                "sufficient": sufficient,
                "free_gb": round(free_gb, 2),
                "total_gb": round(stat.total / (1024 ** 3), 2),
                "used_percent": round((stat.used / stat.total) * 100, 2),
                "status": f"✅ 剩余 {free_gb:.1f}GB" if sufficient else f"⚠️ 仅剩 {free_gb:.1f}GB"
            }
        except Exception as e:
            return {"sufficient": False, "error": str(e), "status": "❌ 检测失败"}
    
    async def auto_fix_all(self) -> Dict:
        """
        自动修复所有可修复的问题
        
        Returns:
            修复结果
        """
        fixed = []
        failed = []
        
        logger.info("🔧 开始自动修复...")
        
        check_result = await self.check_all_concurrent()
        
        for issue in check_result.get("fixable_issues", []):
            try:
                if "Chromium" in issue["issue"]:
                    logger.info("📥 安装Chromium浏览器...")
                    import subprocess
                    result = subprocess.run(
                        ["playwright", "install", "chromium", "--with-deps"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        fixed.append(issue["issue"])
                        logger.info("✅ Chromium安装成功")
                    else:
                        failed.append({"issue": issue["issue"], "reason": result.stderr})
                        logger.error(f"❌ Chromium安装失败: {result.stderr}")
                
                elif "Redis" in issue["issue"]:
                    logger.info("🚀 启动Redis服务...")
                    from ..utils.redis_manager_enhanced import redis_manager
                    success, msg = await redis_manager.start()
                    if success:
                        fixed.append(issue["issue"])
                        logger.info("✅ Redis启动成功")
                    else:
                        failed.append({"issue": issue["issue"], "reason": msg})
                        logger.error(f"❌ Redis启动失败: {msg}")
            
            except Exception as e:
                failed.append({"issue": issue["issue"], "reason": str(e)})
                logger.error(f"❌ 修复失败: {issue['issue']} - {e}")
        
        logger.info(f"🎉 修复完成: 成功{len(fixed)}个, 失败{len(failed)}个")
        
        return {
            "fixed": fixed,
            "failed": failed,
            "success": len(failed) == 0
        }


# 创建全局实例
ultimate_env_checker = UltimateEnvironmentChecker()
