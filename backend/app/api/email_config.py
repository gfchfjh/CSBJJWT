"""
邮件配置API - P0优化
提供邮件服务器配置、测试、告警设置等功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from ..utils.email_sender import email_sender
from ..utils.logger import logger
from ..database import db


router = APIRouter(prefix="/api/email-config", tags=["邮件配置"])


class EmailConfig(BaseModel):
    """邮件配置模型"""
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = "KOOK消息转发系统"
    enabled: bool = True


class AlertEmailsConfig(BaseModel):
    """告警邮箱配置"""
    alert_emails: List[EmailStr]
    report_emails: Optional[List[EmailStr]] = None


class TestEmailRequest(BaseModel):
    """测试邮件请求"""
    to_email: EmailStr
    subject: Optional[str] = "测试邮件"
    content: Optional[str] = "这是一封测试邮件，如果您收到此邮件，说明邮件配置正确。"


@router.get("/")
async def get_email_config():
    """
    获取当前邮件配置
    """
    try:
        # 读取配置
        configs = {}
        config_keys = [
            'smtp_host', 'smtp_port', 'smtp_username', 
            'from_email', 'from_name', 'email_enabled',
            'alert_emails', 'report_emails'
        ]
        
        for key in config_keys:
            result = db.execute(
                "SELECT value FROM system_config WHERE key = ?",
                (key,)
            ).fetchone()
            if result:
                configs[key] = result['value']
        
        # 密码不返回
        configs['smtp_password'] = '******' if configs.get('smtp_username') else None
        
        # 转换类型
        if configs.get('smtp_port'):
            configs['smtp_port'] = int(configs['smtp_port'])
        configs['enabled'] = configs.get('email_enabled') == 'true'
        
        # 解析邮箱列表
        if configs.get('alert_emails'):
            configs['alert_emails'] = configs['alert_emails'].split(',')
        if configs.get('report_emails'):
            configs['report_emails'] = configs['report_emails'].split(',')
        
        return {
            "success": True,
            "data": configs
        }
        
    except Exception as e:
        logger.error(f"获取邮件配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def update_email_config(config: EmailConfig):
    """
    更新邮件配置
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 更新或插入配置
            config_items = {
                'smtp_host': config.smtp_host,
                'smtp_port': str(config.smtp_port),
                'smtp_username': config.smtp_username,
                'smtp_password': config.smtp_password,
                'from_email': config.from_email or config.smtp_username,
                'from_name': config.from_name,
                'email_enabled': 'true' if config.enabled else 'false'
            }
            
            for key, value in config_items.items():
                cursor.execute("""
                    INSERT INTO system_config (key, value) 
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (key, value))
        
        # 重新加载配置
        email_sender._load_config()
        
        # 记录审计日志
        from ..utils.audit_logger import audit_logger
        audit_logger.log(
            action=audit_logger.ACTION_UPDATE_SETTINGS,
            username="admin",
            resource_type="email_config",
            details={"smtp_host": config.smtp_host, "enabled": config.enabled},
            level=audit_logger.LEVEL_INFO
        )
        
        return {
            "success": True,
            "message": "邮件配置已更新"
        }
        
    except Exception as e:
        logger.error(f"更新邮件配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert-emails")
async def update_alert_emails(config: AlertEmailsConfig):
    """
    更新告警邮箱配置
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 保存告警邮箱
            alert_emails_str = ','.join(config.alert_emails)
            cursor.execute("""
                INSERT INTO system_config (key, value) 
                VALUES ('alert_emails', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (alert_emails_str,))
            
            # 保存报告邮箱
            if config.report_emails:
                report_emails_str = ','.join(config.report_emails)
                cursor.execute("""
                    INSERT INTO system_config (key, value) 
                    VALUES ('report_emails', ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (report_emails_str,))
        
        return {
            "success": True,
            "message": "告警邮箱已更新"
        }
        
    except Exception as e:
        logger.error(f"更新告警邮箱失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection")
async def test_email_connection():
    """
    测试邮件服务器连接
    """
    try:
        # 重新加载配置
        email_sender._load_config()
        
        success, message = await email_sender.test_connection()
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"测试邮件连接失败: {str(e)}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


@router.post("/test-send")
async def test_send_email(request: TestEmailRequest):
    """
    发送测试邮件
    """
    try:
        # 重新加载配置
        email_sender._load_config()
        
        success = await email_sender.send_email(
            to_emails=[request.to_email],
            subject=request.subject,
            content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #409EFF;">测试邮件</h2>
                <p>{request.content}</p>
                <hr style="margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    此邮件由 KOOK消息转发系统 发送<br>
                    发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """,
            html=True
        )
        
        if success:
            return {
                "success": True,
                "message": f"测试邮件已发送到 {request.to_email}"
            }
        else:
            return {
                "success": False,
                "message": "发送失败，请检查配置"
            }
        
    except Exception as e:
        logger.error(f"发送测试邮件失败: {str(e)}")
        return {
            "success": False,
            "message": f"发送失败: {str(e)}"
        }


@router.post("/send-alert")
async def send_alert_email(
    alert_type: str,
    title: str,
    message: str,
    details: Optional[str] = None,
    level: str = "warning"
):
    """
    发送告警邮件（供系统内部调用）
    """
    try:
        success = await email_sender.send_alert(
            alert_type=alert_type,
            title=title,
            message=message,
            details=details,
            level=level
        )
        
        return {
            "success": success,
            "message": "告警邮件已发送" if success else "发送失败"
        }
        
    except Exception as e:
        logger.error(f"发送告警邮件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_email_templates():
    """
    获取邮件模板列表
    """
    templates = [
        {
            "id": "alert",
            "name": "告警邮件",
            "description": "系统异常告警通知",
            "preview": "包含告警级别、类型、时间和详细信息"
        },
        {
            "id": "daily_report",
            "name": "每日报告",
            "description": "每日运行统计报告",
            "preview": "包含转发消息数、成功率、平均延迟等统计"
        },
        {
            "id": "test",
            "name": "测试邮件",
            "description": "用于测试邮件配置",
            "preview": "简单的测试邮件模板"
        }
    ]
    
    return {
        "success": True,
        "data": templates
    }
