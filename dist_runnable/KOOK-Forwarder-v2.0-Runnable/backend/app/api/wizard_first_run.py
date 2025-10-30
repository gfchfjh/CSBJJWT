"""
首次运行检测API
用于自动启动3步配置向导
"""
from fastapi import APIRouter, HTTPException
from ..database import db
from ..config import settings
from ..utils.logger import logger
from pathlib import Path

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


@router.get("/check-first-run")
async def check_first_run():
    """
    检查是否首次运行
    
    判断依据：
    1. 没有任何账号
    2. 没有任何Bot配置
    3. 首次运行标记文件不存在
    
    Returns:
        {
            "is_first_run": bool,
            "wizard_completed": bool,
            "config_status": {...}
        }
    """
    # 检查首次运行标记
    wizard_marker = settings.data_dir / ".wizard_completed"
    wizard_completed = wizard_marker.exists()
    
    # 检查账号数量
    try:
        accounts = db.get_all_accounts()
        accounts_count = len(accounts) if accounts else 0
    except:
        accounts_count = 0
    
    # 检查Bot数量
    try:
        bots = db.get_all_bots()
        bots_count = len(bots) if bots else 0
    except:
        bots_count = 0
    
    # 检查映射数量
    try:
        mappings = db.get_all_mappings()
        mappings_count = len(mappings) if mappings else 0
    except:
        mappings_count = 0
    
    # 判断是否首次运行
    is_first_run = (
        not wizard_completed and
        accounts_count == 0 and
        bots_count == 0 and
        mappings_count == 0
    )
    
    logger.info(f"首次运行检测: is_first_run={is_first_run}, wizard_completed={wizard_completed}")
    
    return {
        "is_first_run": is_first_run,
        "wizard_completed": wizard_completed,
        "config_status": {
            "accounts_count": accounts_count,
            "bots_count": bots_count,
            "mappings_count": mappings_count
        }
    }


@router.get("/check-config-completeness")
async def check_config_completeness():
    """
    检查配置完整性
    
    Returns:
        {
            "complete": bool,
            "completeness": int (0-100),
            "missing_items": [...],
            "recommendations": [...]
        }
    """
    missing = []
    recommendations = []
    
    # 检查1: 账号
    try:
        accounts = db.get_all_accounts()
        if not accounts or len(accounts) == 0:
            missing.append({
                "category": "账号",
                "item": "KOOK账号",
                "description": "至少需要添加一个KOOK账号",
                "severity": "critical",
                "action_url": "/accounts"
            })
            recommendations.append({
                "title": "添加KOOK账号",
                "description": "您需要至少添加一个KOOK账号才能监听消息",
                "action": "点击前往账号管理页面",
                "url": "/accounts"
            })
        else:
            # 检查账号在线状态
            online_accounts = [a for a in accounts if a.get('status') == 'online']
            if len(online_accounts) == 0:
                recommendations.append({
                    "title": "账号未在线",
                    "description": f"您有 {len(accounts)} 个账号，但都处于离线状态",
                    "action": "检查账号连接",
                    "url": "/accounts"
                })
    except Exception as e:
        logger.error(f"检查账号失败: {e}")
        missing.append({
            "category": "账号",
            "item": "KOOK账号",
            "description": "检查失败，请添加账号",
            "severity": "critical",
            "action_url": "/accounts"
        })
    
    # 检查2: Bot配置
    try:
        bots = db.get_all_bots()
        if not bots or len(bots) == 0:
            missing.append({
                "category": "Bot",
                "item": "转发Bot",
                "description": "至少需要配置一个Discord/Telegram/飞书Bot",
                "severity": "critical",
                "action_url": "/bots"
            })
            recommendations.append({
                "title": "配置转发Bot",
                "description": "添加Discord Webhook或Telegram Bot，用于接收转发的消息",
                "action": "点击前往Bot配置",
                "url": "/bots"
            })
        else:
            # 检查Bot状态
            active_bots = [b for b in bots if b.get('enabled', True)]
            if len(active_bots) == 0:
                recommendations.append({
                    "title": "没有启用的Bot",
                    "description": f"您有 {len(bots)} 个Bot，但都处于禁用状态",
                    "action": "启用至少一个Bot",
                    "url": "/bots"
                })
    except Exception as e:
        logger.error(f"检查Bot失败: {e}")
        missing.append({
            "category": "Bot",
            "item": "转发Bot",
            "description": "检查失败，请配置Bot",
            "severity": "critical",
            "action_url": "/bots"
        })
    
    # 检查3: 频道映射
    try:
        mappings = db.get_all_mappings()
        if not mappings or len(mappings) == 0:
            missing.append({
                "category": "映射",
                "item": "频道映射",
                "description": "至少需要创建一个频道映射关系",
                "severity": "critical",
                "action_url": "/mapping"
            })
            recommendations.append({
                "title": "设置频道映射",
                "description": "配置KOOK频道与目标平台频道的映射关系",
                "action": "点击前往映射配置",
                "url": "/mapping"
            })
        else:
            # 检查映射启用状态
            enabled_mappings = [m for m in mappings if m.get('enabled', True)]
            if len(enabled_mappings) == 0:
                recommendations.append({
                    "title": "没有启用的映射",
                    "description": f"您有 {len(mappings)} 个映射，但都处于禁用状态",
                    "action": "启用至少一个映射",
                    "url": "/mapping"
                })
    except Exception as e:
        logger.error(f"检查映射失败: {e}")
        missing.append({
            "category": "映射",
            "item": "频道映射",
            "description": "检查失败，请配置映射",
            "severity": "critical",
            "action_url": "/mapping"
        })
    
    # 计算完整性百分比
    total_checks = 3
    completed_checks = total_checks - len(missing)
    completeness = int((completed_checks / total_checks) * 100)
    
    # 是否完整
    complete = len(missing) == 0
    
    logger.info(f"配置完整性: {completeness}%, complete={complete}")
    
    return {
        "complete": complete,
        "completeness": completeness,
        "missing_items": missing,
        "recommendations": recommendations,
        "summary": {
            "total_checks": total_checks,
            "completed_checks": completed_checks,
            "critical_issues": len([m for m in missing if m.get("severity") == "critical"])
        }
    }


@router.post("/mark-completed")
async def mark_wizard_completed():
    """
    标记向导已完成
    
    创建标记文件，防止下次启动时再次显示向导
    """
    wizard_marker = settings.data_dir / ".wizard_completed"
    
    try:
        wizard_marker.touch()
        logger.info("✅ 向导已标记为完成")
        
        return {
            "success": True,
            "message": "向导已完成标记",
            "marker_path": str(wizard_marker)
        }
    except Exception as e:
        logger.error(f"标记向导完成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-wizard")
async def reset_wizard():
    """
    重置向导状态
    
    删除标记文件，下次启动时重新显示向导（用于测试或重新配置）
    """
    wizard_marker = settings.data_dir / ".wizard_completed"
    
    try:
        if wizard_marker.exists():
            wizard_marker.unlink()
            logger.info("✅ 向导状态已重置")
        
        return {
            "success": True,
            "message": "向导状态已重置，下次启动将重新显示向导"
        }
    except Exception as e:
        logger.error(f"重置向导状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-wizard-progress")
async def get_wizard_progress():
    """
    获取向导进度
    
    用于在向导中显示当前完成情况
    """
    # 获取配置状态
    config_status = await check_config_completeness()
    
    # 计算各步骤完成情况
    steps = [
        {
            "step": 1,
            "name": "登录KOOK",
            "completed": config_status["config_status"]["accounts_count"] > 0,
            "description": f"已添加 {config_status['config_status']['accounts_count']} 个账号"
        },
        {
            "step": 2,
            "name": "配置Bot",
            "completed": config_status["config_status"]["bots_count"] > 0,
            "description": f"已配置 {config_status['config_status']['bots_count']} 个Bot"
        },
        {
            "step": 3,
            "name": "设置映射",
            "completed": config_status["config_status"]["mappings_count"] > 0,
            "description": f"已创建 {config_status['config_status']['mappings_count']} 个映射"
        }
    ]
    
    # 计算总进度
    completed_steps = len([s for s in steps if s["completed"]])
    total_progress = int((completed_steps / len(steps)) * 100)
    
    return {
        "steps": steps,
        "completed_steps": completed_steps,
        "total_steps": len(steps),
        "progress": total_progress,
        "next_step": None if completed_steps == len(steps) else steps[completed_steps]["name"]
    }
