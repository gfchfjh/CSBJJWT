"""
邮件发送模块
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from ..utils.logger import logger
from ..database import db
import json


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.enabled = False
        self.smtp_server = None
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.from_email = None
        self.to_emails = []
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """从数据库加载邮件配置"""
        try:
            email_config = db.get_system_config('email_config')
            if email_config:
                config = json.loads(email_config)
                self.enabled = config.get('enabled', False)
                self.smtp_server = config.get('smtp_server')
                self.smtp_port = config.get('smtp_port', 587)
                self.smtp_user = config.get('smtp_user')
                self.smtp_password = config.get('smtp_password')
                self.from_email = config.get('from_email')
                self.to_emails = config.get('to_emails', [])
                
                if self.enabled:
                    logger.info("邮件告警已启用")
        except Exception as e:
            logger.error(f"加载邮件配置失败: {str(e)}")
    
    async def send_email(
        self,
        subject: str,
        body: str,
        to_emails: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件内容
            to_emails: 收件人列表（可选，默认使用配置的收件人）
            html: 是否为HTML格式
            
        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.debug("邮件告警未启用，跳过发送")
            return False
        
        if not self.smtp_server or not self.smtp_user or not self.smtp_password:
            logger.error("邮件配置不完整，无法发送")
            return False
        
        recipients = to_emails or self.to_emails
        if not recipients:
            logger.error("未指定收件人")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email or self.smtp_user
            msg['To'] = ', '.join(recipients)
            
            # 添加邮件内容
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送
            async with aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=False  # 使用STARTTLS
            ) as smtp:
                # 使用STARTTLS加密
                await smtp.starttls()
                
                # 登录
                await smtp.login(self.smtp_user, self.smtp_password)
                
                # 发送邮件
                await smtp.send_message(msg)
            
            logger.info(f"邮件发送成功: {subject} -> {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    async def send_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        details: Optional[dict] = None
    ) -> bool:
        """
        发送告警邮件
        
        Args:
            alert_type: 告警类型（error/warning/info）
            title: 告警标题
            message: 告警消息
            details: 详细信息（可选）
            
        Returns:
            是否发送成功
        """
        # 构建HTML邮件内容
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px 5px 0 0; }}
                .alert-error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
                .alert-warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
                .alert-info {{ background: #d1ecf1; border-left: 4px solid #17a2b8; }}
                .content {{ padding: 20px; background: white; }}
                .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                h2 {{ margin: 0; color: #333; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 3px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header alert-{alert_type}">
                    <h2>⚠️ {title}</h2>
                </div>
                <div class="content">
                    <p>{message}</p>
                    {f'<div class="details"><h3>详细信息：</h3><pre>{json.dumps(details, indent=2, ensure_ascii=False)}</pre></div>' if details else ''}
                </div>
                <div class="footer">
                    <p>来自 KOOK消息转发系统</p>
                    <p>发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件
        subject = f"[KOOK转发系统] {title}"
        return await self.send_email(subject, html_body, html=True)
    
    async def send_service_error_alert(self, error_message: str, traceback: Optional[str] = None):
        """发送服务异常告警"""
        return await self.send_alert(
            alert_type='error',
            title='服务异常告警',
            message=f'KOOK消息转发系统检测到服务异常：{error_message}',
            details={'error': error_message, 'traceback': traceback} if traceback else None
        )
    
    async def send_account_offline_alert(self, account_email: str, reason: str = None):
        """发送账号掉线告警"""
        return await self.send_alert(
            alert_type='warning',
            title='账号掉线告警',
            message=f'KOOK账号 {account_email} 已离线',
            details={'account': account_email, 'reason': reason} if reason else None
        )
    
    async def send_message_failed_alert(self, failed_count: int, channel_name: str = None):
        """发送消息转发失败告警"""
        return await self.send_alert(
            alert_type='warning',
            title='消息转发失败告警',
            message=f'检测到 {failed_count} 条消息转发失败' + (f'，频道：{channel_name}' if channel_name else ''),
            details={'failed_count': failed_count, 'channel': channel_name}
        )
    
    async def test_connection(self) -> tuple[bool, str]:
        """
        测试SMTP连接
        
        Returns:
            (是否成功, 消息)
        """
        if not self.smtp_server or not self.smtp_user or not self.smtp_password:
            return False, "邮件配置不完整"
        
        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=False
            ) as smtp:
                await smtp.starttls()
                await smtp.login(self.smtp_user, self.smtp_password)
            
            return True, "SMTP连接测试成功"
            
        except Exception as e:
            return False, f"SMTP连接测试失败: {str(e)}"


# 创建全局邮件发送器实例
email_sender = EmailSender()
