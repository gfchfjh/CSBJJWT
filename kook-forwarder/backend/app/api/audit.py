"""
审计日志API路由
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from ..utils.audit_logger import audit_logger
from ..utils.logger import logger

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    event_type: Optional[str] = Query(None, description="事件类型过滤"),
    severity: Optional[str] = Query(None, description="严重程度过滤"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> Dict[str, Any]:
    """
    获取审计日志
    
    Args:
        event_type: 事件类型（LOGIN/LOGOUT/CONFIG_CHANGE等）
        severity: 严重程度（INFO/WARNING/ERROR/CRITICAL）
        limit: 返回数量
        offset: 偏移量
        
    Returns:
        审计日志列表
    """
    try:
        # 获取审计日志
        all_audits = audit_logger.get_recent_audits(
            event_type=event_type,
            limit=limit + offset
        )
        
        # 按严重程度过滤
        if severity:
            all_audits = [
                a for a in all_audits 
                if a.get('data', {}).get('severity') == severity
            ]
        
        # 应用偏移和限制
        audits = all_audits[offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "logs": audits,
                "total": len(all_audits),
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"获取审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90, description="统计天数")
) -> Dict[str, Any]:
    """
    获取审计日志统计信息
    
    Args:
        days: 统计最近N天
        
    Returns:
        统计信息
    """
    try:
        # 获取最近的审计日志
        audits = audit_logger.get_recent_audits(limit=10000)
        
        # 按事件类型统计
        type_stats = {}
        severity_stats = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }
        
        # 按日期统计
        date_stats = {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for audit in audits:
            # 解析时间戳
            try:
                timestamp = datetime.fromisoformat(audit['timestamp'])
                if timestamp < cutoff_date:
                    continue
            except:
                continue
            
            # 事件类型统计
            event_type = audit.get('event_type', 'UNKNOWN')
            type_stats[event_type] = type_stats.get(event_type, 0) + 1
            
            # 严重程度统计
            severity = audit.get('data', {}).get('severity', 'INFO')
            if severity in severity_stats:
                severity_stats[severity] += 1
            
            # 日期统计
            date_key = timestamp.strftime('%Y-%m-%d')
            if date_key not in date_stats:
                date_stats[date_key] = {
                    'total': 0,
                    'by_type': {},
                    'by_severity': {k: 0 for k in severity_stats.keys()}
                }
            
            date_stats[date_key]['total'] += 1
            date_stats[date_key]['by_type'][event_type] = \
                date_stats[date_key]['by_type'].get(event_type, 0) + 1
            date_stats[date_key]['by_severity'][severity] += 1
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_events": sum(type_stats.values()),
                "by_type": type_stats,
                "by_severity": severity_stats,
                "by_date": date_stats
            }
        }
        
    except Exception as e:
        logger.error(f"获取审计统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security-events")
async def get_security_events(
    severity: Optional[str] = Query(None, description="严重程度"),
    limit: int = Query(50, ge=1, le=500)
) -> Dict[str, Any]:
    """
    获取安全事件
    
    Args:
        severity: 严重程度过滤
        limit: 返回数量
        
    Returns:
        安全事件列表
    """
    try:
        # 获取安全事件类型的审计日志
        security_audits = audit_logger.get_recent_audits(
            event_type="SECURITY_EVENT",
            limit=limit * 2  # 多获取一些用于过滤
        )
        
        # 按严重程度过滤
        if severity:
            security_audits = [
                a for a in security_audits
                if a.get('data', {}).get('severity') == severity
            ]
        
        # 限制数量
        security_audits = security_audits[:limit]
        
        # 统计严重事件数
        critical_count = sum(
            1 for a in security_audits
            if a.get('data', {}).get('severity') == 'CRITICAL'
        )
        
        return {
            "success": True,
            "data": {
                "events": security_audits,
                "total": len(security_audits),
                "critical_count": critical_count
            }
        }
        
    except Exception as e:
        logger.error(f"获取安全事件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_audit_logs(
    event_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    format: str = Query("json", description="导出格式（json/csv）")
) -> Dict[str, Any]:
    """
    导出审计日志
    
    Args:
        event_type: 事件类型过滤
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        format: 导出格式
        
    Returns:
        导出的数据
    """
    try:
        # 获取审计日志
        audits = audit_logger.get_recent_audits(
            event_type=event_type,
            limit=10000
        )
        
        # 按日期过滤
        if start_date or end_date:
            filtered_audits = []
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            for audit in audits:
                try:
                    timestamp = datetime.fromisoformat(audit['timestamp'])
                    
                    if start_dt and timestamp < start_dt:
                        continue
                    if end_dt and timestamp > end_dt:
                        continue
                    
                    filtered_audits.append(audit)
                except:
                    continue
            
            audits = filtered_audits
        
        if format == "csv":
            # CSV格式导出
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(['timestamp', 'event_type', 'severity', 'details'])
            
            # 写入数据
            for audit in audits:
                writer.writerow([
                    audit.get('timestamp', ''),
                    audit.get('event_type', ''),
                    audit.get('data', {}).get('severity', ''),
                    str(audit.get('data', {}))
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "format": "csv",
                "content": csv_content,
                "count": len(audits)
            }
        else:
            # JSON格式导出（默认）
            return {
                "success": True,
                "format": "json",
                "data": audits,
                "count": len(audits)
            }
        
    except Exception as e:
        logger.error(f"导出审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="保留天数")
) -> Dict[str, Any]:
    """
    清理旧审计日志
    
    Args:
        days: 保留最近N天的日志
        
    Returns:
        清理结果
    """
    try:
        import os
        from pathlib import Path
        
        audit_dir = audit_logger.audit_log_dir
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_files = []
        for file_path in audit_dir.glob("audit_*.log"):
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if mtime < cutoff_date:
                # 删除旧文件
                file_path.unlink()
                deleted_files.append(file_path.name)
                logger.info(f"删除旧审计日志: {file_path.name}")
        
        return {
            "success": True,
            "message": f"清理完成，删除了{len(deleted_files)}个文件",
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        logger.error(f"清理审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
