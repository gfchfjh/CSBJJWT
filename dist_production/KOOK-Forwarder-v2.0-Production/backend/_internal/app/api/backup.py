"""
配置备份恢复API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import json
import shutil
from datetime import datetime
from pathlib import Path
from ..database import db
from ..config import settings
from ..utils.logger import logger

router = APIRouter(prefix="/api/backup", tags=["配置备份"])

# 备份目录
BACKUP_DIR = Path(settings.data_dir) / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/export")
async def export_config():
    """
    导出配置
    
    Returns:
        配置文件下载
    """
    try:
        # 收集所有配置数据
        config_data = {
            "version": "1.0",
            "export_time": datetime.now().isoformat(),
            "accounts": [],
            "bot_configs": [],
            "channel_mappings": [],
            "filter_rules": [],
            "system_config": {}
        }
        
        # 导出账号（不包含敏感信息）
        accounts = db.get_accounts()
        for account in accounts:
            config_data["accounts"].append({
                "id": account["id"],
                "email": account["email"],
                # 不导出密码和Cookie
                "status": account["status"],
                "created_at": account["created_at"]
            })
        
        # 导出Bot配置
        config_data["bot_configs"] = db.get_bot_configs()
        
        # 导出频道映射
        config_data["channel_mappings"] = db.get_channel_mappings()
        
        # 导出过滤规则
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM filter_rules WHERE enabled = 1")
            config_data["filter_rules"] = [dict(row) for row in cursor.fetchall()]
        
        # 导出系统配置
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_config")
            for row in cursor.fetchall():
                # 不导出验证码等临时配置
                if not row[0].startswith("captcha_"):
                    config_data["system_config"][row[0]] = row[1]
        
        # 生成备份文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"kook_forwarder_backup_{timestamp}.json"
        backup_path = BACKUP_DIR / backup_filename
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置导出成功: {backup_path}")
        
        # 返回文件下载
        return FileResponse(
            backup_path,
            media_type="application/json",
            filename=backup_filename
        )
        
    except Exception as e:
        logger.error(f"导出配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/import")
async def import_config(
    file: UploadFile = File(...),
    mode: str = "merge"  # merge: 合并, replace: 替换
):
    """
    导入配置
    
    Args:
        file: 配置文件
        mode: 导入模式（merge合并，replace替换）
        
    Returns:
        导入结果
    """
    try:
        # 读取上传的文件
        content = await file.read()
        config_data = json.loads(content.decode('utf-8'))
        
        # 验证配置文件格式
        if "version" not in config_data:
            raise ValueError("无效的配置文件格式")
        
        result = {
            "status": "success",
            "imported": {
                "accounts": 0,
                "bot_configs": 0,
                "channel_mappings": 0,
                "filter_rules": 0,
                "system_config": 0
            },
            "errors": []
        }
        
        # 如果是替换模式，先清空现有数据（保留账号的敏感信息）
        if mode == "replace":
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # 不删除accounts，保留登录信息
                cursor.execute("DELETE FROM channel_mappings")
                cursor.execute("DELETE FROM filter_rules")
                # 不删除bot_configs，可能包含Token
                conn.commit()
        
        # 导入Bot配置
        for bot_config in config_data.get("bot_configs", []):
            try:
                # 检查是否已存在
                existing = db.get_bot_configs(bot_config["platform"])
                exists = any(
                    b["name"] == bot_config["name"] for b in existing
                )
                
                if not exists:
                    db.add_bot_config(
                        platform=bot_config["platform"],
                        name=bot_config["name"],
                        config=bot_config["config"]
                    )
                    result["imported"]["bot_configs"] += 1
            except Exception as e:
                result["errors"].append(f"Bot配置导入失败: {str(e)}")
        
        # 导入频道映射
        for mapping in config_data.get("channel_mappings", []):
            try:
                db.add_channel_mapping(
                    kook_server_id=mapping["kook_server_id"],
                    kook_channel_id=mapping["kook_channel_id"],
                    kook_channel_name=mapping["kook_channel_name"],
                    target_platform=mapping["target_platform"],
                    target_bot_id=mapping["target_bot_id"],
                    target_channel_id=mapping["target_channel_id"]
                )
                result["imported"]["channel_mappings"] += 1
            except Exception as e:
                result["errors"].append(f"频道映射导入失败: {str(e)}")
        
        # 导入过滤规则
        for rule in config_data.get("filter_rules", []):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO filter_rules (rule_type, rule_value, scope, enabled)
                        VALUES (?, ?, ?, ?)
                    """, (
                        rule["rule_type"],
                        rule["rule_value"],
                        rule["scope"],
                        rule["enabled"]
                    ))
                    conn.commit()
                result["imported"]["filter_rules"] += 1
            except Exception as e:
                result["errors"].append(f"过滤规则导入失败: {str(e)}")
        
        # 导入系统配置
        for key, value in config_data.get("system_config", {}).items():
            try:
                db.set_system_config(key, value)
                result["imported"]["system_config"] += 1
            except Exception as e:
                result["errors"].append(f"系统配置导入失败: {str(e)}")
        
        logger.info(f"配置导入完成: {result}")
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="配置文件格式错误")
    except Exception as e:
        logger.error(f"导入配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/list")
async def list_backups():
    """
    列出所有备份文件
    
    Returns:
        备份文件列表
    """
    try:
        backups = []
        
        for backup_file in sorted(BACKUP_DIR.glob("*.json"), reverse=True):
            stat = backup_file.stat()
            
            backups.append({
                "filename": backup_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "path": str(backup_file)
            })
        
        return {"backups": backups}
        
    except Exception as e:
        logger.error(f"列出备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"列出备份失败: {str(e)}")


@router.delete("/delete/{filename}")
async def delete_backup(filename: str):
    """
    删除备份文件
    
    Args:
        filename: 备份文件名
    """
    try:
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="备份文件不存在")
        
        # 安全检查：确保文件在备份目录内
        if not str(backup_path.resolve()).startswith(str(BACKUP_DIR.resolve())):
            raise HTTPException(status_code=403, detail="非法的文件路径")
        
        backup_path.unlink()
        
        logger.info(f"删除备份文件: {filename}")
        
        return {"status": "success", "message": "备份已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/auto-backup")
async def create_auto_backup():
    """
    创建自动备份
    
    Returns:
        备份信息
    """
    try:
        # 导出配置（同导出功能）
        response = await export_config()
        
        # 清理旧备份（保留最近10个）
        backups = sorted(BACKUP_DIR.glob("*.json"), key=lambda x: x.stat().st_ctime)
        
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()
                logger.info(f"删除旧备份: {old_backup.name}")
        
        return {
            "status": "success",
            "message": "自动备份创建成功",
            "filename": response.headers.get("content-disposition", "").split("filename=")[-1]
        }
        
    except Exception as e:
        logger.error(f"自动备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"自动备份失败: {str(e)}")


@router.get("/download/{filename}")
async def download_backup(filename: str):
    """
    下载指定的备份文件
    
    Args:
        filename: 备份文件名
    """
    try:
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="备份文件不存在")
        
        # 安全检查
        if not str(backup_path.resolve()).startswith(str(BACKUP_DIR.resolve())):
            raise HTTPException(status_code=403, detail="非法的文件路径")
        
        return FileResponse(
            backup_path,
            media_type="application/json",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
