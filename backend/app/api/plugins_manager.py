"""
插件管理API - P1优化
支持插件上传、安装、卸载、启用/禁用等功能
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from ..utils.logger import logger
from ..database import db
from ..config import settings


router = APIRouter(prefix="/api/plugins", tags=["插件管理"])


class PluginInfo(BaseModel):
    """插件信息模型"""
    id: str
    name: str
    version: str
    description: str
    author: str
    enabled: bool = False


# 插件目录
PLUGINS_DIR = settings.data_dir / "plugins"
PLUGINS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_plugin_table():
    """确保插件表存在"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugins (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    enabled INTEGER DEFAULT 0,
                    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config TEXT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plugins_enabled 
                ON plugins(enabled)
            """)
    except Exception as e:
        logger.error(f"创建插件表失败: {str(e)}")


_ensure_plugin_table()


@router.get("/")
async def get_plugins():
    """
    获取所有已安装的插件列表
    """
    try:
        result = db.execute("SELECT * FROM plugins ORDER BY installed_at DESC")
        plugins = [dict(row) for row in result.fetchall()]
        
        # 解析配置
        for plugin in plugins:
            if plugin.get('config'):
                try:
                    plugin['config'] = json.loads(plugin['config'])
                except:
                    plugin['config'] = {}
        
        return {
            "success": True,
            "data": plugins
        }
        
    except Exception as e:
        logger.error(f"获取插件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_plugin(file: UploadFile = File(...)):
    """
    上传并安装插件
    
    插件必须是.zip格式，包含plugin.json配置文件
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="插件文件必须是.zip格式")
    
    try:
        # 保存临时文件
        temp_path = PLUGINS_DIR / f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 解压并验证
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            # 检查plugin.json
            if 'plugin.json' not in zip_ref.namelist():
                temp_path.unlink()
                raise HTTPException(status_code=400, detail="插件包缺少plugin.json配置文件")
            
            # 读取配置
            plugin_json = zip_ref.read('plugin.json').decode('utf-8')
            plugin_info = json.loads(plugin_json)
            
            required_fields = ['id', 'name', 'version', 'author']
            for field in required_fields:
                if field not in plugin_info:
                    temp_path.unlink()
                    raise HTTPException(status_code=400, detail=f"插件配置缺少必需字段: {field}")
            
            plugin_id = plugin_info['id']
            
            # 检查是否已安装
            result = db.execute(
                "SELECT * FROM plugins WHERE id = ?",
                (plugin_id,)
            ).fetchone()
            
            if result:
                temp_path.unlink()
                raise HTTPException(status_code=400, detail=f"插件 {plugin_id} 已安装")
            
            # 解压到插件目录
            plugin_dir = PLUGINS_DIR / plugin_id
            plugin_dir.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(plugin_dir)
        
        # 删除临时文件
        temp_path.unlink()
        
        # 保存到数据库
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO plugins (id, name, version, description, author, enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                plugin_info['name'],
                plugin_info['version'],
                plugin_info.get('description', ''),
                plugin_info['author'],
                0  # 默认禁用
            ))
        
        # 记录审计日志
        from ..utils.audit_logger import audit_logger
        audit_logger.log(
            action=audit_logger.ACTION_INSTALL_PLUGIN,
            username="admin",
            resource_type="plugin",
            resource_id=plugin_id,
            details=plugin_info,
            level=audit_logger.LEVEL_INFO
        )
        
        logger.info(f"插件安装成功: {plugin_id} v{plugin_info['version']}")
        
        return {
            "success": True,
            "message": f"插件 {plugin_info['name']} 安装成功",
            "data": plugin_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"插件安装失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"安装失败: {str(e)}")


@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    """
    卸载插件
    """
    try:
        # 检查插件是否存在
        result = db.execute(
            "SELECT * FROM plugins WHERE id = ?",
            (plugin_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="插件不存在")
        
        # 删除插件目录
        plugin_dir = PLUGINS_DIR / plugin_id
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        
        # 从数据库删除
        db.execute("DELETE FROM plugins WHERE id = ?", (plugin_id,))
        
        # 记录审计日志
        from ..utils.audit_logger import audit_logger
        audit_logger.log(
            action=audit_logger.ACTION_UNINSTALL_PLUGIN,
            username="admin",
            resource_type="plugin",
            resource_id=plugin_id,
            level=audit_logger.LEVEL_INFO
        )
        
        logger.info(f"插件已卸载: {plugin_id}")
        
        return {
            "success": True,
            "message": f"插件 {result['name']} 已卸载"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"插件卸载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/toggle")
async def toggle_plugin(plugin_id: str):
    """
    启用/禁用插件
    """
    try:
        result = db.execute(
            "SELECT * FROM plugins WHERE id = ?",
            (plugin_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="插件不存在")
        
        new_enabled = 0 if result['enabled'] else 1
        
        db.execute(
            "UPDATE plugins SET enabled = ? WHERE id = ?",
            (new_enabled, plugin_id)
        )
        
        status = "已启用" if new_enabled else "已禁用"
        logger.info(f"插件 {plugin_id} {status}")
        
        return {
            "success": True,
            "message": f"插件{status}",
            "data": {
                "enabled": bool(new_enabled)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换插件状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}/config")
async def get_plugin_config(plugin_id: str):
    """
    获取插件配置
    """
    try:
        result = db.execute(
            "SELECT config FROM plugins WHERE id = ?",
            (plugin_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="插件不存在")
        
        config = {}
        if result['config']:
            config = json.loads(result['config'])
        
        return {
            "success": True,
            "data": config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取插件配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/config")
async def update_plugin_config(plugin_id: str, config: dict):
    """
    更新插件配置
    """
    try:
        result = db.execute(
            "SELECT * FROM plugins WHERE id = ?",
            (plugin_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="插件不存在")
        
        config_json = json.dumps(config, ensure_ascii=False)
        
        db.execute(
            "UPDATE plugins SET config = ? WHERE id = ?",
            (config_json, plugin_id)
        )
        
        logger.info(f"插件配置已更新: {plugin_id}")
        
        return {
            "success": True,
            "message": "插件配置已更新"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新插件配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market")
async def get_plugin_market():
    """
    获取插件市场列表（模拟数据）
    """
    # TODO: 实际应该从远程服务器获取
    market_plugins = [
        {
            "id": "translator",
            "name": "消息翻译插件",
            "version": "1.0.0",
            "description": "自动将消息翻译为指定语言",
            "author": "KOOK Forwarder Team",
            "downloads": 1234,
            "rating": 4.5,
            "category": "content",
            "tags": ["翻译", "多语言"],
            "icon": "🌐"
        },
        {
            "id": "keyword_reply",
            "name": "关键词自动回复",
            "version": "1.2.0",
            "description": "监听特定关键词并自动回复",
            "author": "Community",
            "downloads": 856,
            "rating": 4.2,
            "category": "automation",
            "tags": ["自动化", "回复"],
            "icon": "💬"
        },
        {
            "id": "sentiment_filter",
            "name": "情感分析过滤",
            "version": "1.1.0",
            "description": "基于情感分析的智能消息过滤",
            "author": "AI Lab",
            "downloads": 523,
            "rating": 4.7,
            "category": "filter",
            "tags": ["AI", "过滤"],
            "icon": "🧠"
        },
        {
            "id": "image_enhancer",
            "name": "图片增强插件",
            "version": "2.0.0",
            "description": "自动优化和压缩图片",
            "author": "Media Team",
            "downloads": 967,
            "rating": 4.6,
            "category": "media",
            "tags": ["图片", "优化"],
            "icon": "🖼️"
        }
    ]
    
    return {
        "success": True,
        "data": market_plugins
    }
