"""
审计日志API - P0优化
提供审计日志查询、统计、导出等功能
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..utils.audit_logger import audit_logger
from ..utils.logger import logger
import csv
import io


router = APIRouter(prefix="/api/audit-logs", tags=["审计日志"])


class AuditLogQuery(BaseModel):
    """审计日志查询参数"""
    limit: int = 100
    offset: int = 0
    user_id: Optional[str] = None
    action: Optional[str] = None
    level: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    success_only: Optional[bool] = None


@router.get("/")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    level: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    success_only: Optional[bool] = None
):
    """
    获取审计日志列表
    
    支持多种筛选条件：
    - limit: 返回数量（1-1000）
    - offset: 偏移量（分页）
    - user_id: 用户ID筛选
    - action: 操作类型筛选
    - level: 严重级别筛选（info/warning/error/critical）
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD）
    - success_only: 仅显示成功/失败的操作
    """
    try:
        logs = audit_logger.get_logs(
            limit=limit,
            offset=offset,
            user_id=user_id,
            action=action,
            level=level,
            start_date=start_date,
            end_date=end_date,
            success_only=success_only
        )
        
        # 获取总数（用于分页）
        total_query = {}
        if user_id:
            total_query['user_id'] = user_id
        if action:
            total_query['action'] = action
        if level:
            total_query['level'] = level
        if start_date:
            total_query['start_date'] = start_date
        if end_date:
            total_query['end_date'] = end_date
        if success_only is not None:
            total_query['success_only'] = success_only
        
        # 简单估算总数
        all_logs = audit_logger.get_logs(limit=10000, **total_query)
        total = len(all_logs)
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
        
    except Exception as e:
        logger.error(f"获取审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_audit_statistics(
    days: int = Query(7, ge=1, le=365, description="统计天数")
):
    """
    获取审计日志统计信息
    
    返回指定天数内的统计数据：
    - 总操作数
    - 成功/失败数
    - 按操作类型统计
    - 按严重级别统计
    - 按用户统计
    """
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        stats = audit_logger.get_statistics(
            start_date=start_date,
            end_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return {
            "success": True,
            "data": {
                **stats,
                "period_days": days,
                "start_date": start_date
            }
        }
        
    except Exception as e:
        logger.error(f"获取审计日志统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions")
async def get_available_actions():
    """
    获取所有可用的操作类型
    
    返回系统支持的所有审计操作类型列表
    """
    return {
        "success": True,
        "data": {
            "actions": [
                {"value": audit_logger.ACTION_LOGIN, "label": "登录"},
                {"value": audit_logger.ACTION_LOGOUT, "label": "登出"},
                {"value": audit_logger.ACTION_ADD_ACCOUNT, "label": "添加账号"},
                {"value": audit_logger.ACTION_DELETE_ACCOUNT, "label": "删除账号"},
                {"value": audit_logger.ACTION_UPDATE_ACCOUNT, "label": "更新账号"},
                {"value": audit_logger.ACTION_ADD_BOT, "label": "添加Bot"},
                {"value": audit_logger.ACTION_DELETE_BOT, "label": "删除Bot"},
                {"value": audit_logger.ACTION_UPDATE_BOT, "label": "更新Bot"},
                {"value": audit_logger.ACTION_ADD_MAPPING, "label": "添加映射"},
                {"value": audit_logger.ACTION_DELETE_MAPPING, "label": "删除映射"},
                {"value": audit_logger.ACTION_UPDATE_MAPPING, "label": "更新映射"},
                {"value": audit_logger.ACTION_START_SERVICE, "label": "启动服务"},
                {"value": audit_logger.ACTION_STOP_SERVICE, "label": "停止服务"},
                {"value": audit_logger.ACTION_RESTART_SERVICE, "label": "重启服务"},
                {"value": audit_logger.ACTION_UPDATE_SETTINGS, "label": "更新设置"},
                {"value": audit_logger.ACTION_EXPORT_CONFIG, "label": "导出配置"},
                {"value": audit_logger.ACTION_IMPORT_CONFIG, "label": "导入配置"},
                {"value": audit_logger.ACTION_BACKUP_DATABASE, "label": "备份数据库"},
                {"value": audit_logger.ACTION_RESTORE_DATABASE, "label": "恢复数据库"},
                {"value": audit_logger.ACTION_CLEAR_LOGS, "label": "清空日志"},
                {"value": audit_logger.ACTION_UPDATE_FILTER, "label": "更新过滤规则"},
                {"value": audit_logger.ACTION_INSTALL_PLUGIN, "label": "安装插件"},
                {"value": audit_logger.ACTION_UNINSTALL_PLUGIN, "label": "卸载插件"},
            ]
        }
    }


@router.get("/levels")
async def get_available_levels():
    """
    获取所有可用的严重级别
    """
    return {
        "success": True,
        "data": {
            "levels": [
                {"value": audit_logger.LEVEL_INFO, "label": "信息", "color": "primary"},
                {"value": audit_logger.LEVEL_WARNING, "label": "警告", "color": "warning"},
                {"value": audit_logger.LEVEL_ERROR, "label": "错误", "color": "danger"},
                {"value": audit_logger.LEVEL_CRITICAL, "label": "严重", "color": "danger"},
            ]
        }
    }


@router.get("/export")
async def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json)$"),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    level: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    导出审计日志
    
    支持格式：
    - csv: CSV文件
    - json: JSON文件
    """
    try:
        # 获取所有匹配的日志（不限制数量）
        logs = audit_logger.get_logs(
            limit=100000,
            offset=0,
            user_id=user_id,
            action=action,
            level=level,
            start_date=start_date,
            end_date=end_date
        )
        
        if format == "csv":
            # 生成CSV
            output = io.StringIO()
            if logs:
                fieldnames = ['id', 'timestamp', 'username', 'action', 'resource_type', 
                             'resource_id', 'ip_address', 'level', 'success', 'error_message']
                writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for log in logs:
                    writer.writerow(log)
            
            content = output.getvalue()
            output.close()
            
            from fastapi.responses import Response
            return Response(
                content=content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        else:  # json
            import json
            from fastapi.responses import Response
            return Response(
                content=json.dumps(logs, ensure_ascii=False, indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
        
    except Exception as e:
        logger.error(f"导出审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clean")
async def clean_old_audit_logs(
    days: int = Query(90, ge=7, le=365, description="保留天数")
):
    """
    清理旧的审计日志
    
    清理指定天数之前的审计日志（最少保留7天）
    """
    try:
        deleted_count = audit_logger.clean_old_logs(days=days)
        
        # 记录清理操作到审计日志
        audit_logger.log(
            action=audit_logger.ACTION_CLEAR_LOGS,
            username="system",
            details={"days": days, "deleted_count": deleted_count},
            level=audit_logger.LEVEL_INFO
        )
        
        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count,
                "message": f"成功清理了 {deleted_count} 条审计日志（{days}天前）"
            }
        }
        
    except Exception as e:
        logger.error(f"清理审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_audit_logs(
    limit: int = Query(10, ge=1, le=100, description="返回数量")
):
    """
    获取最近的审计日志（快速查看）
    """
    try:
        logs = audit_logger.get_logs(limit=limit, offset=0)
        
        return {
            "success": True,
            "data": logs
        }
        
    except Exception as e:
        logger.error(f"获取最近审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
