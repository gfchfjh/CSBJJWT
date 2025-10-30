"""
✅ P1-5新增：完整的设置管理API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import os
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from ..database import db
from ..utils.logger import logger
from ..config import settings as config_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsModel(BaseModel):
    """设置模型"""
    # 服务控制
    autoLaunch: bool = False
    minimizeToTray: bool = True
    startMinimized: bool = False
    
    # 图片处理
    imageStrategy: str = "smart"
    imageStoragePath: str = ""
    imageMaxSizeGB: int = 10
    imageCleanupDays: int = 7
    imageCompressionQuality: int = 85
    imageMaxSizeMB: float = 10.0
    
    # 日志
    logLevel: str = "INFO"
    logRetentionDays: int = 3
    
    # 通知
    notifyOnServiceError: bool = True
    notifyOnAccountOffline: bool = True
    notifyOnMessageFailed: bool = False
    notificationSound: bool = True
    
    # 邮件
    emailAlertEnabled: bool = False
    smtpHost: str = "smtp.gmail.com"
    smtpPort: int = 587
    smtpFromEmail: str = ""
    smtpPassword: str = ""
    smtpToEmail: str = ""
    smtpUseTLS: bool = True
    
    # 安全
    requirePassword: bool = False
    
    # 备份
    autoBackup: bool = True
    autoBackupTime: Optional[str] = None
    backupRetentionCount: int = 10
    backupItems: List[str] = ["accounts", "bots", "mappings", "filters", "settings"]
    
    # 其他
    language: str = "zh-CN"
    theme: str = "light"
    autoCheckUpdate: bool = True
    developerMode: bool = False
    performanceMonitor: bool = False


@router.get("/")
async def get_settings() -> Dict[str, Any]:
    """
    获取所有设置
    """
    try:
        # 从数据库读取设置
        result = db.execute("SELECT * FROM system_config").fetchall()
        
        settings_dict = {}
        for row in result:
            key = row['key']
            value = row['value']
            
            # 尝试解析JSON
            try:
                settings_dict[key] = json.loads(value)
            except:
                settings_dict[key] = value
        
        # 如果没有设置，返回默认值
        if not settings_dict:
            default_settings = SettingsModel()
            settings_dict = default_settings.dict()
        
        # 补充图片存储路径
        if not settings_dict.get('imageStoragePath'):
            settings_dict['imageStoragePath'] = str(config_settings.image_storage_path)
        
        return settings_dict
        
    except Exception as e:
        logger.error(f"获取设置失败: {str(e)}")
        # 返回默认设置
        return SettingsModel().dict()


@router.post("/")
async def save_settings(settings: SettingsModel) -> Dict[str, Any]:
    """
    保存所有设置
    """
    try:
        settings_dict = settings.dict()
        
        # 保存到数据库
        for key, value in settings_dict.items():
            json_value = json.dumps(value) if not isinstance(value, str) else value
            
            db.execute(
                "INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)",
                (key, json_value)
            )
        
        logger.info("✅ 设置已保存")
        
        # 应用某些设置
        if settings.logLevel:
            logger.setLevel(settings.logLevel)
        
        return {"success": True, "message": "设置已保存"}
        
    except Exception as e:
        logger.error(f"保存设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-stats")
async def get_image_stats() -> Dict[str, Any]:
    """
    获取图片存储统计
    """
    try:
        image_path = Path(config_settings.image_storage_path)
        
        if not image_path.exists():
            return {
                "usedSize": "0 MB",
                "usedPercent": 0
            }
        
        # 计算已用空间
        total_size = 0
        file_count = 0
        
        for file in image_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        used_gb = total_size / (1024 ** 3)
        max_gb = config_settings.image_max_size_gb
        used_percent = int((used_gb / max_gb) * 100) if max_gb > 0 else 0
        
        return {
            "usedSize": f"{used_gb:.2f} GB",
            "usedPercent": min(used_percent, 100),
            "fileCount": file_count
        }
        
    except Exception as e:
        logger.error(f"获取图片统计失败: {str(e)}")
        return {"usedSize": "0 MB", "usedPercent": 0}


@router.get("/log-stats")
async def get_log_stats() -> Dict[str, Any]:
    """
    获取日志统计
    """
    try:
        log_path = Path(config_settings.log_dir)
        
        if not log_path.exists():
            return {
                "totalSize": "0 MB",
                "fileCount": 0
            }
        
        total_size = 0
        file_count = 0
        
        for file in log_path.rglob("*.log"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 ** 2)
        
        return {
            "totalSize": f"{size_mb:.2f} MB",
            "fileCount": file_count
        }
        
    except Exception as e:
        logger.error(f"获取日志统计失败: {str(e)}")
        return {"totalSize": "0 MB", "fileCount": 0}


@router.get("/backup-info")
async def get_backup_info() -> Dict[str, Any]:
    """
    获取备份信息
    """
    try:
        backup_path = Path(config_settings.data_dir) / "backups"
        
        if not backup_path.exists():
            return {
                "lastBackupTime": None,
                "lastBackupSize": None,
                "totalBackups": 0
            }
        
        backups = list(backup_path.glob("backup_*.json"))
        
        if not backups:
            return {
                "lastBackupTime": None,
                "lastBackupSize": None,
                "totalBackups": 0
            }
        
        # 最新备份
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
        backup_size = latest_backup.stat().st_size
        
        return {
            "lastBackupTime": backup_time.strftime("%Y-%m-%d %H:%M:%S"),
            "lastBackupSize": f"{backup_size / 1024:.2f} KB",
            "totalBackups": len(backups)
        }
        
    except Exception as e:
        logger.error(f"获取备份信息失败: {str(e)}")
        return {
            "lastBackupTime": None,
            "lastBackupSize": None,
            "totalBackups": 0
        }


@router.post("/cleanup-images")
async def cleanup_old_images(request: Dict[str, int]) -> Dict[str, Any]:
    """
    清理旧图片
    """
    try:
        days = request.get('days', 7)
        image_path = Path(config_settings.image_storage_path)
        
        if not image_path.exists():
            return {"deletedCount": 0, "freedSpace": "0 MB"}
        
        cutoff_time = time.time() - (days * 86400)
        deleted_count = 0
        freed_space = 0
        
        for file in image_path.rglob("*"):
            if file.is_file() and file.stat().st_mtime < cutoff_time:
                file_size = file.stat().st_size
                file.unlink()
                deleted_count += 1
                freed_space += file_size
        
        freed_mb = freed_space / (1024 ** 2)
        
        logger.info(f"✅ 清理了 {deleted_count} 个文件，释放 {freed_mb:.2f} MB")
        
        return {
            "deletedCount": deleted_count,
            "freedSpace": f"{freed_mb:.2f} MB"
        }
        
    except Exception as e:
        logger.error(f"清理图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-logs")
async def clear_all_logs() -> Dict[str, Any]:
    """
    清空所有日志
    """
    try:
        log_path = Path(config_settings.log_dir)
        
        if not log_path.exists():
            return {"message": "日志目录不存在"}
        
        deleted_count = 0
        for file in log_path.rglob("*.log"):
            if file.is_file():
                file.unlink()
                deleted_count += 1
        
        logger.info(f"✅ 清空了 {deleted_count} 个日志文件")
        
        return {
            "success": True,
            "deletedCount": deleted_count
        }
        
    except Exception as e:
        logger.error(f"清空日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email_config(email_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试邮件配置
    """
    try:
        import aiosmtplib
        from email.message import EmailMessage
        
        message = EmailMessage()
        message["From"] = email_config["smtpFromEmail"]
        message["To"] = email_config["smtpToEmail"]
        message["Subject"] = "KOOK转发系统 - 测试邮件"
        message.set_content(
            f"这是一封测试邮件。\n\n"
            f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"如果您收到此邮件，说明邮件配置正确。"
        )
        
        # 发送邮件
        await aiosmtplib.send(
            message,
            hostname=email_config["smtpHost"],
            port=email_config["smtpPort"],
            username=email_config["smtpFromEmail"],
            password=email_config["smtpPassword"],
            use_tls=email_config.get("smtpUseTLS", True)
        )
        
        logger.info("✅ 测试邮件已发送")
        
        return {"success": True, "message": "测试邮件已发送"}
        
    except Exception as e:
        logger.error(f"发送测试邮件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate-key")
async def regenerate_encryption_key() -> Dict[str, Any]:
    """
    重新生成加密密钥
    """
    try:
        from ..utils.crypto import crypto_manager
        
        # 重新生成密钥
        crypto_manager.regenerate_key()
        
        logger.warning("⚠️ 加密密钥已重新生成")
        
        return {
            "success": True,
            "message": "加密密钥已重新生成，请重新输入所有敏感信息"
        }
        
    except Exception as e:
        logger.error(f"重新生成密钥失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-all-data")
async def clear_all_data() -> Dict[str, Any]:
    """
    清空所有数据（危险操作）
    """
    try:
        # 清空所有表
        tables = ['accounts', 'bot_configs', 'channel_mappings', 'filter_rules', 'message_logs', 'failed_messages']
        
        for table in tables:
            db.execute(f"DELETE FROM {table}")
        
        logger.warning("⚠️ 所有数据已清空")
        
        return {
            "success": True,
            "message": "所有数据已清空"
        }
        
    except Exception as e:
        logger.error(f"清空数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_settings() -> Dict[str, Any]:
    """
    重置为默认设置
    """
    try:
        # 删除所有设置
        db.execute("DELETE FROM system_config")
        
        # 保存默认设置
        default_settings = SettingsModel()
        await save_settings(default_settings)
        
        logger.info("✅ 设置已重置为默认值")
        
        return {
            "success": True,
            "message": "设置已重置"
        }
        
    except Exception as e:
        logger.error(f"重置设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
