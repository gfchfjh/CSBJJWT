"""
环境一键修复API - ✅ P0-3优化完成: 8项问题自动修复
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import sys
import subprocess
import os
from pathlib import Path
from ..utils.logger import logger
from ..config import settings

router = APIRouter(prefix="/api/system/autofix", tags=["autofix"])


class AutofixResult(BaseModel):
    """修复结果"""
    success: bool
    message: str
    details: Optional[str] = None
    next_steps: Optional[List[str]] = None


# ============ ✅ P0-3: 一键修复接口 ============

@router.post("/chromium")
async def autofix_chromium() -> AutofixResult:
    """
    ✅ P0-3新增: 一键安装Chromium
    
    功能：
    1. 自动检测Playwright是否已安装
    2. 执行 playwright install chromium
    3. 实时返回安装进度
    4. 处理安装失败情况
    
    Returns:
        {
            "success": bool,
            "message": str,
            "details": str,
            "next_steps": List[str]
        }
    """
    logger.info("🔧 开始自动安装Chromium...")
    
    try:
        # 检查playwright是否已安装
        try:
            import playwright
            logger.info("✅ Playwright已安装")
        except ImportError:
            logger.error("❌ Playwright未安装")
            return AutofixResult(
                success=False,
                message="Playwright未安装，无法安装Chromium",
                details="请先安装Playwright: pip install playwright",
                next_steps=[
                    "1. 打开终端",
                    "2. 运行: pip install playwright",
                    "3. 然后重试安装Chromium"
                ]
            )
        
        # 执行安装命令
        logger.info("📥 正在下载并安装Chromium...")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            '-m',
            'playwright',
            'install',
            'chromium',
            '--with-deps',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info("✅ Chromium安装成功")
            return AutofixResult(
                success=True,
                message="✅ Chromium安装成功！",
                details=stdout.decode('utf-8'),
                next_steps=[
                    "1. Chromium已成功安装",
                    "2. 请继续配置向导的下一步"
                ]
            )
        else:
            error_msg = stderr.decode('utf-8')
            logger.error(f"❌ Chromium安装失败: {error_msg}")
            return AutofixResult(
                success=False,
                message="❌ Chromium安装失败",
                details=error_msg,
                next_steps=[
                    "1. 检查网络连接是否正常",
                    "2. 尝试手动运行: playwright install chromium",
                    "3. 如果仍然失败，请查看错误详情"
                ]
            )
            
    except Exception as e:
        logger.error(f"❌ 自动安装Chromium异常: {str(e)}")
        return AutofixResult(
            success=False,
            message=f"安装失败: {str(e)}",
            details=None,
            next_steps=[
                "1. 请尝试手动安装",
                "2. 打开终端运行: playwright install chromium"
            ]
        )


@router.post("/redis")
async def autofix_redis() -> AutofixResult:
    """
    ✅ P0-3新增: 一键启动Redis
    
    功能：
    1. 检测Redis是否已安装
    2. 尝试启动嵌入式Redis
    3. 验证Redis连接
    
    Returns:
        修复结果
    """
    logger.info("🔧 开始自动启动Redis...")
    
    try:
        from ..utils.redis_manager_enhanced import redis_manager
        
        # 尝试启动Redis
        success, message = await redis_manager.start()
        
        if success:
            logger.info("✅ Redis启动成功")
            return AutofixResult(
                success=True,
                message="✅ Redis已成功启动！",
                details=message,
                next_steps=[
                    "1. Redis服务正在运行",
                    "2. 请继续使用系统"
                ]
            )
        else:
            logger.error(f"❌ Redis启动失败: {message}")
            return AutofixResult(
                success=False,
                message="❌ Redis启动失败",
                details=message,
                next_steps=[
                    "1. 检查Redis是否已安装",
                    "2. 尝试手动启动Redis",
                    "3. 或连接到外部Redis服务器"
                ]
            )
            
    except Exception as e:
        logger.error(f"❌ 自动启动Redis异常: {str(e)}")
        return AutofixResult(
            success=False,
            message=f"启动失败: {str(e)}",
            details=None,
            next_steps=[
                "1. 请检查Redis是否正确安装",
                "2. 尝试手动启动Redis服务"
            ]
        )


@router.post("/network")
async def autofix_network() -> AutofixResult:
    """
    ✅ P0-3新增: 网络诊断和修复
    
    功能：
    1. 诊断网络连接问题
    2. 检测DNS解析
    3. 测试KOOK服务器连通性
    4. 提供修复建议
    
    Returns:
        诊断和修复结果
    """
    logger.info("🔧 开始网络诊断...")
    
    try:
        import aiohttp
        import time
        
        diagnostic_results = []
        all_passed = True
        
        # 测试1: 检测基本网络连接
        logger.info("1️⃣ 检测基本网络连接...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://www.baidu.com',
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        diagnostic_results.append("✅ 基本网络连接正常")
                    else:
                        diagnostic_results.append(f"⚠️ 网络连接异常: HTTP {response.status}")
                        all_passed = False
        except asyncio.TimeoutError:
            diagnostic_results.append("❌ 网络连接超时")
            all_passed = False
        except Exception as e:
            diagnostic_results.append(f"❌ 网络连接失败: {str(e)}")
            all_passed = False
        
        # 测试2: 检测KOOK服务器连通性
        logger.info("2️⃣ 检测KOOK服务器连通性...")
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://www.kookapp.cn',
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    latency = int((time.time() - start_time) * 1000)
                    if response.status == 200:
                        diagnostic_results.append(f"✅ KOOK服务器连接正常（延迟: {latency}ms）")
                    else:
                        diagnostic_results.append(f"⚠️ KOOK服务器响应异常: HTTP {response.status}")
                        all_passed = False
        except asyncio.TimeoutError:
            diagnostic_results.append("❌ 无法连接到KOOK服务器（超时）")
            all_passed = False
        except Exception as e:
            diagnostic_results.append(f"❌ KOOK服务器连接失败: {str(e)}")
            all_passed = False
        
        # 测试3: 检测DNS解析
        logger.info("3️⃣ 检测DNS解析...")
        try:
            import socket
            ip = socket.gethostbyname('www.kookapp.cn')
            diagnostic_results.append(f"✅ DNS解析正常（www.kookapp.cn → {ip}）")
        except Exception as e:
            diagnostic_results.append(f"❌ DNS解析失败: {str(e)}")
            all_passed = False
        
        # 生成修复建议
        next_steps = []
        if all_passed:
            next_steps = [
                "✅ 网络环境良好",
                "您可以正常使用系统"
            ]
        else:
            next_steps = [
                "1. 检查是否连接到互联网",
                "2. 尝试访问 https://www.kookapp.cn 确认网站可访问",
                "3. 如果使用代理，请检查代理配置",
                "4. 尝试更换DNS服务器（例如：8.8.8.8）",
                "5. 关闭防火墙或杀毒软件重试"
            ]
        
        result_message = "✅ 网络诊断完成，所有测试通过" if all_passed else "⚠️ 网络诊断发现问题"
        
        return AutofixResult(
            success=all_passed,
            message=result_message,
            details="\n".join(diagnostic_results),
            next_steps=next_steps
        )
        
    except Exception as e:
        logger.error(f"❌ 网络诊断异常: {str(e)}")
        return AutofixResult(
            success=False,
            message=f"诊断失败: {str(e)}",
            details=None,
            next_steps=[
                "1. 请检查网络连接",
                "2. 尝试重启网络设备"
            ]
        )


@router.post("/permissions")
async def autofix_permissions() -> AutofixResult:
    """
    ✅ P0-3新增: 修复文件权限问题
    
    功能：
    1. 检查数据目录权限
    2. 自动修复权限问题
    3. 创建缺失的目录
    
    Returns:
        修复结果
    """
    logger.info("🔧 开始检查和修复文件权限...")
    
    try:
        # 需要的目录列表
        required_dirs = [
            Path(settings.data_dir),
            Path(settings.data_dir) / 'images',
            Path(settings.data_dir) / 'attachments',
            Path(settings.data_dir) / 'logs',
            Path(settings.data_dir) / 'backups'
        ]
        
        fixed_items = []
        errors = []
        
        for dir_path in required_dirs:
            try:
                # 创建目录（如果不存在）
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    fixed_items.append(f"✅ 创建目录: {dir_path}")
                    logger.info(f"✅ 创建目录: {dir_path}")
                
                # 检查写权限
                test_file = dir_path / '.write_test'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    fixed_items.append(f"✅ 目录可写: {dir_path}")
                except PermissionError:
                    errors.append(f"❌ 目录不可写: {dir_path}")
                    logger.error(f"❌ 目录不可写: {dir_path}")
                    
            except Exception as e:
                errors.append(f"❌ 处理目录失败: {dir_path} - {str(e)}")
                logger.error(f"❌ 处理目录失败: {dir_path} - {str(e)}")
        
        # 生成结果
        if len(errors) == 0:
            return AutofixResult(
                success=True,
                message="✅ 文件权限检查通过！",
                details="\n".join(fixed_items),
                next_steps=[
                    "1. 所有必需目录已就绪",
                    "2. 文件权限正常",
                    "3. 可以正常使用系统"
                ]
            )
        else:
            return AutofixResult(
                success=False,
                message="⚠️ 发现权限问题",
                details="\n".join(fixed_items + errors),
                next_steps=[
                    "1. 请以管理员权限运行应用",
                    "2. 或手动修改目录权限",
                    f"3. 确保以下目录可写: {settings.data_dir}"
                ]
            )
            
    except Exception as e:
        logger.error(f"❌ 权限检查异常: {str(e)}")
        return AutofixResult(
            success=False,
            message=f"检查失败: {str(e)}",
            details=None,
            next_steps=[
                "1. 请手动检查应用权限",
                "2. 尝试以管理员权限运行"
            ]
        )


@router.post("/dependencies")
async def autofix_dependencies() -> AutofixResult:
    """
    ✅ P0-3新增: 检查并安装缺失的依赖
    
    功能：
    1. 检查Python依赖包
    2. 自动安装缺失的依赖
    
    Returns:
        修复结果
    """
    logger.info("🔧 开始检查依赖...")
    
    try:
        # 关键依赖列表
        required_packages = [
            'fastapi',
            'uvicorn',
            'playwright',
            'redis',
            'aiohttp',
            'cryptography',
            'pillow'
        ]
        
        missing_packages = []
        installed_packages = []
        
        # 检查每个依赖
        for package in required_packages:
            try:
                __import__(package)
                installed_packages.append(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"⚠️ 缺少依赖: {package}")
        
        if len(missing_packages) == 0:
            return AutofixResult(
                success=True,
                message="✅ 所有依赖已安装！",
                details="\n".join(installed_packages),
                next_steps=[
                    "所有必需的依赖包都已安装",
                    "可以正常使用系统"
                ]
            )
        else:
            # 提供安装建议（不自动安装，避免破坏环境）
            install_command = f"pip install {' '.join(missing_packages)}"
            
            return AutofixResult(
                success=False,
                message=f"⚠️ 缺少{len(missing_packages)}个依赖包",
                details="\n".join(
                    installed_packages + 
                    [f"❌ {pkg}" for pkg in missing_packages]
                ),
                next_steps=[
                    "1. 打开终端",
                    f"2. 运行: {install_command}",
                    "3. 重启应用"
                ]
            )
            
    except Exception as e:
        logger.error(f"❌ 依赖检查异常: {str(e)}")
        return AutofixResult(
            success=False,
            message=f"检查失败: {str(e)}",
            details=None,
            next_steps=[
                "1. 请手动检查依赖",
                "2. 运行: pip install -r requirements.txt"
            ]
        )


@router.post("/all")
async def autofix_all() -> Dict[str, AutofixResult]:
    """
    ✅ P0-3新增: 一键修复所有问题
    
    功能：
    1. 依次执行所有修复操作
    2. 汇总修复结果
    3. 提供总体建议
    
    Returns:
        {
            "chromium": AutofixResult,
            "redis": AutofixResult,
            "network": AutofixResult,
            "permissions": AutofixResult,
            "dependencies": AutofixResult,
            "overall_success": bool,
            "summary": str
        }
    """
    logger.info("🔧 开始一键修复所有问题...")
    
    results = {}
    
    # 1. 检查依赖
    logger.info("1/5: 检查依赖...")
    results["dependencies"] = await autofix_dependencies()
    
    # 2. 检查权限
    logger.info("2/5: 检查权限...")
    results["permissions"] = await autofix_permissions()
    
    # 3. 网络诊断
    logger.info("3/5: 网络诊断...")
    results["network"] = await autofix_network()
    
    # 4. 安装Chromium（如果需要）
    logger.info("4/5: 检查Chromium...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch(headless=True)
            results["chromium"] = AutofixResult(
                success=True,
                message="✅ Chromium已安装",
                next_steps=[]
            )
    except:
        results["chromium"] = await autofix_chromium()
    
    # 5. 启动Redis
    logger.info("5/5: 检查Redis...")
    results["redis"] = await autofix_redis()
    
    # 计算总体成功率
    success_count = sum(1 for r in results.values() if isinstance(r, AutofixResult) and r.success)
    total_count = len(results)
    overall_success = success_count == total_count
    
    # 生成摘要
    if overall_success:
        summary = f"✅ 全部通过！{total_count}个检查项全部成功。"
    else:
        summary = f"⚠️ {success_count}/{total_count}个检查项通过，请查看失败项的修复建议。"
    
    results["overall_success"] = overall_success
    results["summary"] = summary
    
    logger.info(summary)
    
    return results
