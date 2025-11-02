"""
环境检查一键修复API
✅ P0-2优化：提供可执行的修复动作
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import subprocess
import asyncio
import sys
import os
from pathlib import Path
from ..utils.logger import logger
from ..utils.redis_manager import redis_manager
from ..config import settings

router = APIRouter(prefix="/api/environment", tags=["environment"])


class AutoFixRequest(BaseModel):
    fix_items: List[str]  # 需要修复的项目列表


class AutoFixResponse(BaseModel):
    results: List[Dict[str, Any]]
    success_count: int
    failed_count: int


@router.post("/auto-fix", response_model=AutoFixResponse)
async def auto_fix_environment(request: AutoFixRequest):
    """
    一键修复环境问题
    
    支持修复的项目：
    - chromium: 自动安装Chromium浏览器
    - redis: 自动启动Redis服务
    - python_deps: 自动安装Python依赖
    - permissions: 修复文件权限问题
    - data_dirs: 创建必要的数据目录
    """
    logger.info(f"开始一键修复，修复项: {request.fix_items}")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for item in request.fix_items:
        try:
            if item == "chromium":
                result = await fix_chromium()
            elif item == "redis":
                result = await fix_redis()
            elif item == "python_deps":
                result = await fix_python_deps()
            elif item == "permissions":
                result = await fix_permissions()
            elif item == "data_dirs":
                result = await fix_data_dirs()
            elif item == "disk_space":
                result = await fix_disk_space()
            elif item == "network":
                result = await fix_network()
            elif item == "ports":
                result = await fix_ports()
            else:
                result = {
                    "item": item,
                    "status": "skipped",
                    "message": f"未知的修复项: {item}"
                }
            
            results.append(result)
            
            if result["status"] == "fixed" or result["status"] == "success":
                success_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"修复 {item} 失败: {str(e)}")
            results.append({
                "item": item,
                "status": "failed",
                "message": f"修复失败: {str(e)}",
                "error": str(e)
            })
            failed_count += 1
    
    logger.info(f"一键修复完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    
    return AutoFixResponse(
        results=results,
        success_count=success_count,
        failed_count=failed_count
    )


async def fix_chromium() -> Dict[str, Any]:
    """
    自动安装Chromium浏览器
    """
    logger.info("开始安装Chromium...")
    
    try:
        # 检查playwright是否已安装
        try:
            import playwright
        except ImportError:
            logger.error("playwright未安装")
            return {
                "item": "chromium",
                "status": "failed",
                "message": "playwright未安装，请先安装: pip install playwright"
            }
        
        # 执行playwright install chromium
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "playwright", "install", "chromium",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        if process.returncode == 0:
            logger.info("✅ Chromium安装成功")
            return {
                "item": "chromium",
                "status": "fixed",
                "message": "Chromium已成功安装",
                "details": stdout.decode().strip()
            }
        else:
            error_msg = stderr.decode().strip()
            logger.error(f"❌ Chromium安装失败: {error_msg}")
            return {
                "item": "chromium",
                "status": "failed",
                "message": f"安装失败: {error_msg}"
            }
            
    except asyncio.TimeoutError:
        logger.error("Chromium安装超时")
        return {
            "item": "chromium",
            "status": "failed",
            "message": "安装超时（5分钟），请检查网络连接"
        }
    except Exception as e:
        logger.error(f"Chromium安装异常: {str(e)}")
        return {
            "item": "chromium",
            "status": "failed",
            "message": f"安装异常: {str(e)}"
        }


async def fix_redis() -> Dict[str, Any]:
    """
    自动启动Redis服务
    """
    logger.info("开始启动Redis服务...")
    
    try:
        # 使用redis_manager启动
        success, message = await redis_manager.start()
        
        if success:
            logger.info("✅ Redis启动成功")
            return {
                "item": "redis",
                "status": "fixed",
                "message": "Redis服务已成功启动",
                "details": message
            }
        else:
            logger.warning(f"⚠️ Redis启动失败: {message}")
            return {
                "item": "redis",
                "status": "failed",
                "message": f"启动失败: {message}",
                "suggestion": "请检查Redis配置或手动安装Redis"
            }
            
    except Exception as e:
        logger.error(f"Redis启动异常: {str(e)}")
        return {
            "item": "redis",
            "status": "failed",
            "message": f"启动异常: {str(e)}"
        }


async def fix_python_deps() -> Dict[str, Any]:
    """
    自动安装Python依赖
    """
    logger.info("开始安装Python依赖...")
    
    try:
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        
        if not requirements_file.exists():
            return {
                "item": "python_deps",
                "status": "skipped",
                "message": "requirements.txt文件不存在"
            }
        
        # 执行pip install
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        if process.returncode == 0:
            logger.info("✅ Python依赖安装成功")
            return {
                "item": "python_deps",
                "status": "fixed",
                "message": "Python依赖已成功安装"
            }
        else:
            error_msg = stderr.decode().strip()
            logger.error(f"❌ Python依赖安装失败: {error_msg}")
            return {
                "item": "python_deps",
                "status": "failed",
                "message": f"安装失败: {error_msg}"
            }
            
    except asyncio.TimeoutError:
        return {
            "item": "python_deps",
            "status": "failed",
            "message": "安装超时（5分钟）"
        }
    except Exception as e:
        return {
            "item": "python_deps",
            "status": "failed",
            "message": f"安装异常: {str(e)}"
        }


async def fix_permissions() -> Dict[str, Any]:
    """
    修复文件权限问题
    """
    logger.info("开始修复文件权限...")
    
    try:
        data_dir = Path(settings.data_dir)
        
        # 确保数据目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 修复权限（仅Unix系统）
        if os.name != 'nt':  # 非Windows
            try:
                import stat
                # 设置目录权限为755
                os.chmod(data_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                
                # 递归修复子目录权限
                for root, dirs, files in os.walk(data_dir):
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        os.chmod(dir_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                    for f in files:
                        file_path = os.path.join(root, f)
                        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                
                logger.info("✅ 文件权限修复成功")
                return {
                    "item": "permissions",
                    "status": "fixed",
                    "message": "文件权限已修复"
                }
            except PermissionError:
                return {
                    "item": "permissions",
                    "status": "failed",
                    "message": "权限不足，请使用sudo运行"
                }
        else:
            # Windows系统
            return {
                "item": "permissions",
                "status": "success",
                "message": "Windows系统无需修复权限"
            }
            
    except Exception as e:
        logger.error(f"权限修复异常: {str(e)}")
        return {
            "item": "permissions",
            "status": "failed",
            "message": f"修复异常: {str(e)}"
        }


async def fix_data_dirs() -> Dict[str, Any]:
    """
    创建必要的数据目录
    """
    logger.info("开始创建数据目录...")
    
    try:
        # 需要创建的目录列表
        required_dirs = [
            Path(settings.data_dir),
            Path(settings.data_dir) / "images",
            Path(settings.data_dir) / "logs",
            Path(settings.data_dir) / "redis",
            Path(settings.data_dir) / "backup",
            Path(settings.data_dir) / "message_backup",
        ]
        
        created_dirs = []
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(dir_path))
                logger.info(f"创建目录: {dir_path}")
        
        if created_dirs:
            logger.info(f"✅ 创建了 {len(created_dirs)} 个目录")
            return {
                "item": "data_dirs",
                "status": "fixed",
                "message": f"已创建 {len(created_dirs)} 个必要目录",
                "details": created_dirs
            }
        else:
            return {
                "item": "data_dirs",
                "status": "success",
                "message": "所有必要目录已存在"
            }
            
    except Exception as e:
        logger.error(f"目录创建异常: {str(e)}")
        return {
            "item": "data_dirs",
            "status": "failed",
            "message": f"创建失败: {str(e)}"
        }


async def fix_disk_space() -> Dict[str, Any]:
    """
    检查并清理磁盘空间（不能自动修复，只提供建议）
    """
    return {
        "item": "disk_space",
        "status": "manual",
        "message": "磁盘空间不足，请手动清理",
        "suggestions": [
            "删除不需要的文件",
            "清理旧日志（设置 → 日志设置 → 清空日志）",
            "清理旧图片（设置 → 图片处理 → 立即清理旧图片）",
            "扩展磁盘空间"
        ]
    }


async def fix_network() -> Dict[str, Any]:
    """
    检查网络连接（不能自动修复，只提供建议）
    """
    return {
        "item": "network",
        "status": "manual",
        "message": "网络连接问题，请检查网络设置",
        "suggestions": [
            "检查网络连接是否正常",
            "确认防火墙未阻止应用",
            "尝试使用代理",
            "检查DNS设置"
        ]
    }


async def fix_ports() -> Dict[str, Any]:
    """
    检查端口占用（不能自动修复，只提供建议）
    """
    return {
        "item": "ports",
        "status": "manual",
        "message": "端口被占用，请手动处理",
        "suggestions": [
            f"关闭占用端口{settings.api_port}的程序",
            "或在配置中修改API_PORT",
            "重启应用"
        ]
    }


@router.get("/fix-suggestions/{check_item}")
async def get_fix_suggestions(check_item: str) -> Dict[str, Any]:
    """
    获取特定检查项的修复建议
    """
    suggestions = {
        "chromium": {
            "auto_fixable": True,
            "steps": [
                "点击下方\"一键修复\"按钮",
                "等待Chromium自动下载安装（约5分钟）",
                "安装完成后刷新页面"
            ],
            "manual_steps": [
                "或手动执行: playwright install chromium",
                "确保网络连接正常",
                "如果下载失败，可能需要配置代理"
            ]
        },
        "redis": {
            "auto_fixable": True,
            "steps": [
                "点击下方\"一键修复\"按钮",
                "系统将自动启动内置Redis服务",
                "如果启动失败，请查看日志"
            ],
            "manual_steps": [
                "或手动安装Redis: https://redis.io/download",
                "Windows用户可使用: https://github.com/microsoftarchive/redis/releases",
                "启动Redis服务"
            ]
        },
        "python_deps": {
            "auto_fixable": True,
            "steps": [
                "点击下方\"一键修复\"按钮",
                "系统将自动安装所有Python依赖",
                "安装完成后重启应用"
            ]
        },
        "permissions": {
            "auto_fixable": True,
            "steps": [
                "点击下方\"一键修复\"按钮",
                "系统将自动修复文件权限"
            ],
            "manual_steps": [
                "Linux/macOS用户可能需要使用sudo运行"
            ]
        },
        "data_dirs": {
            "auto_fixable": True,
            "steps": [
                "点击下方\"一键修复\"按钮",
                "系统将自动创建所有必要目录"
            ]
        },
        "disk_space": {
            "auto_fixable": False,
            "manual_steps": [
                "删除不需要的文件",
                "进入设置 → 日志设置 → 清空所有日志",
                "进入设置 → 图片处理 → 立即清理旧图片",
                "扩展磁盘空间（添加新硬盘或扩容）"
            ]
        },
        "network": {
            "auto_fixable": False,
            "manual_steps": [
                "检查网络连接",
                "确认防火墙设置",
                "如在国内，某些服务可能需要代理",
                "尝试切换DNS服务器"
            ]
        },
        "ports": {
            "auto_fixable": False,
            "manual_steps": [
                f"关闭占用端口{settings.api_port}的其他程序",
                "或修改配置文件中的API_PORT",
                "重启应用"
            ]
        }
    }
    
    return suggestions.get(check_item, {
        "auto_fixable": False,
        "manual_steps": ["未知的检查项，请联系技术支持"]
    })
