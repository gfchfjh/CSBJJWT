"""
环境检查API（终极版）
====================
功能：
1. 8项全面环境检查
2. 一键自动修复
3. 详细诊断报告
4. 实时检查进度

作者：KOOK Forwarder Team
日期：2025-10-25
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import subprocess
import sys
import platform
import shutil
import socket
from pathlib import Path

router = APIRouter(prefix="/api/environment", tags=["environment"])

class CheckItem(BaseModel):
    """检查项"""
    name: str
    passed: bool
    message: str
    fixable: bool = False
    fix_command: Optional[str] = None


class EnvironmentReport(BaseModel):
    """环境检查报告"""
    passed: bool
    checks: List[CheckItem]
    warnings: List[str]
    errors: List[str]


class EnvironmentCheckerUltimate:
    """环境检查器（终极版）"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version.split()[0]
        
    async def check_all(self) -> EnvironmentReport:
        """执行所有检查"""
        checks = []
        warnings = []
        errors = []
        
        # 并行执行所有检查
        check_tasks = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_playwright(),
            self.check_redis(),
            self.check_ports(),
            self.check_disk_space(),
            self.check_network(),
            self.check_permissions()
        ]
        
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(f"检查异常: {str(result)}")
                checks.append(CheckItem(
                    name="检查异常",
                    passed=False,
                    message=str(result),
                    fixable=False
                ))
            else:
                checks.append(result)
                if not result.passed:
                    errors.append(f"{result.name}: {result.message}")
                    
        passed = all(check.passed for check in checks)
        
        return EnvironmentReport(
            passed=passed,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    async def check_python_version(self) -> CheckItem:
        """检查Python版本"""
        required_version = (3, 9, 0)
        current_version = sys.version_info[:3]
        
        passed = current_version >= required_version
        
        message = f"当前版本: {'.'.join(map(str, current_version))}, " \
                 f"要求: >= {'.'.join(map(str, required_version))}"
        
        return CheckItem(
            name="Python版本",
            passed=passed,
            message=message,
            fixable=False
        )
    
    async def check_dependencies(self) -> CheckItem:
        """检查依赖库"""
        required_packages = [
            'fastapi',
            'uvicorn',
            'playwright',
            'aioredis',
            'pydantic',
            'aiohttp',
        ]
        
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        passed = len(missing) == 0
        
        if passed:
            message = f"所有依赖已安装 ({len(required_packages)}个)"
        else:
            message = f"缺少依赖: {', '.join(missing)}"
        
        return CheckItem(
            name="依赖库",
            passed=passed,
            message=message,
            fixable=True,
            fix_command=f"pip install {' '.join(missing)}" if missing else None
        )
    
    async def check_playwright(self) -> CheckItem:
        """检查Playwright浏览器"""
        try:
            # 检查playwright命令是否可用
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "--version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return CheckItem(
                    name="Playwright",
                    passed=False,
                    message="Playwright未安装",
                    fixable=True,
                    fix_command="pip install playwright"
                )
            
            # 检查Chromium是否已安装
            # 简化检查：尝试列出浏览器
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium", "--dry-run"],
                capture_output=True,
                timeout=10
            )
            
            # 如果需要安装（输出包含"downloading"），则未安装
            if b"downloading" in result.stdout.lower() or b"installing" in result.stdout.lower():
                return CheckItem(
                    name="Playwright浏览器",
                    passed=False,
                    message="Chromium浏览器未安装",
                    fixable=True,
                    fix_command="playwright install chromium"
                )
            
            return CheckItem(
                name="Playwright浏览器",
                passed=True,
                message="Chromium已安装",
                fixable=False
            )
            
        except Exception as e:
            return CheckItem(
                name="Playwright浏览器",
                passed=False,
                message=f"检查失败: {str(e)}",
                fixable=True,
                fix_command="playwright install chromium"
            )
    
    async def check_redis(self) -> CheckItem:
        """检查Redis连接"""
        try:
            import aioredis
            
            # 尝试连接Redis
            redis = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                minsize=1,
                maxsize=1,
                timeout=2
            )
            
            # 执行PING
            await redis.ping()
            
            # 关闭连接
            redis.close()
            await redis.wait_closed()
            
            return CheckItem(
                name="Redis服务",
                passed=True,
                message="Redis连接正常",
                fixable=False
            )
            
        except Exception as e:
            return CheckItem(
                name="Redis服务",
                passed=False,
                message=f"Redis连接失败: {str(e)}",
                fixable=True,
                fix_command="启动Redis服务或使用嵌入式Redis"
            )
    
    async def check_ports(self) -> CheckItem:
        """检查端口占用"""
        required_ports = [
            (9527, "API服务"),
            (6379, "Redis"),
            (9528, "图床服务")
        ]
        
        occupied = []
        
        for port, name in required_ports:
            if not self._is_port_available(port):
                occupied.append(f"{name}({port})")
        
        passed = len(occupied) == 0
        
        if passed:
            message = "所有必需端口可用"
        else:
            message = f"以下端口已被占用: {', '.join(occupied)}"
        
        return CheckItem(
            name="端口占用",
            passed=passed,
            message=message,
            fixable=False  # 需要手动处理
        )
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result != 0
        except:
            return True
    
    async def check_disk_space(self) -> CheckItem:
        """检查磁盘空间"""
        try:
            total, used, free = shutil.disk_usage("/")
            
            # 至少需要1GB可用空间
            required_gb = 1
            free_gb = free / (1024 ** 3)
            
            passed = free_gb >= required_gb
            
            message = f"可用空间: {free_gb:.2f} GB, 要求: >= {required_gb} GB"
            
            return CheckItem(
                name="磁盘空间",
                passed=passed,
                message=message,
                fixable=False
            )
            
        except Exception as e:
            return CheckItem(
                name="磁盘空间",
                passed=False,
                message=f"检查失败: {str(e)}",
                fixable=False
            )
    
    async def check_network(self) -> CheckItem:
        """检查网络连通性"""
        test_urls = [
            ("www.kookapp.cn", 443, "KOOK"),
            ("discord.com", 443, "Discord"),
            ("api.telegram.org", 443, "Telegram")
        ]
        
        failed = []
        
        for host, port, name in test_urls:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result != 0:
                    failed.append(name)
            except:
                failed.append(name)
        
        passed = len(failed) == 0
        
        if passed:
            message = "所有目标服务器可达"
        else:
            message = f"以下服务器无法连接: {', '.join(failed)}"
        
        return CheckItem(
            name="网络连通性",
            passed=passed,
            message=message,
            fixable=False
        )
    
    async def check_permissions(self) -> CheckItem:
        """检查文件写入权限"""
        test_dirs = [
            Path("./data"),
            Path("./data/redis"),
            Path("./data/images"),
            Path("./data/logs")
        ]
        
        failed = []
        
        for dir_path in test_dirs:
            try:
                # 确保目录存在
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # 尝试写入测试文件
                test_file = dir_path / ".write_test"
                test_file.write_text("test")
                test_file.unlink()
                
            except Exception as e:
                failed.append(f"{dir_path}: {str(e)}")
        
        passed = len(failed) == 0
        
        if passed:
            message = "所有目录可写"
        else:
            message = f"以下目录无写入权限: {', '.join(failed)}"
        
        return CheckItem(
            name="文件写入权限",
            passed=passed,
            message=message,
            fixable=False
        )


# 全局检查器实例
checker = EnvironmentCheckerUltimate()


@router.get("/check", response_model=EnvironmentReport)
async def check_environment():
    """执行完整环境检查"""
    return await checker.check_all()


@router.post("/fix/{issue_name}")
async def fix_issue(issue_name: str):
    """自动修复指定问题"""
    fix_commands = {
        "依赖库": "pip install -r requirements.txt",
        "Playwright浏览器": "playwright install chromium"
    }
    
    if issue_name not in fix_commands:
        raise HTTPException(
            status_code=400,
            detail=f"问题'{issue_name}'无法自动修复"
        )
    
    command = fix_commands[issue_name]
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"'{issue_name}'修复成功",
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "message": f"'{issue_name}'修复失败",
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="修复超时（5分钟）"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"修复异常: {str(e)}"
        )
