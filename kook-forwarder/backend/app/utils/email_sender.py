"""
邮件发送器 - ✅ P0-2优化：完整的SMTP邮件系统
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from ..utils.logger import logger
from ..config import settings
import asyncio


class EmailSender:
    """邮件发送器 - 支持验证码、通知等"""
    
    def __init__(self):
        self.enabled = settings.smtp_enabled if hasattr(settings, 'smtp_enabled') else False
        
        if self.enabled:
            logger.info("✅ 邮件发送器已启用")
        else:
            logger.info("ℹ️ 邮件发送器未启用（SMTP未配置）")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            html: 是否为HTML格式
            
        Returns:
            {
                "success": bool,
                "message": str,
                "error": str (optional)
            }
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "邮件功能未启用",
                "error": "smtp_not_configured"
            }
        
        try:
            # 构建邮件
            message = MIMEMultipart()
            message["From"] = settings.smtp_from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # 添加正文
            mime_type = "html" if html else "plain"
            message.attach(MIMEText(body, mime_type, "utf-8"))
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                use_tls=settings.smtp_use_tls if hasattr(settings, 'smtp_use_tls') else True,
                timeout=30
            )
            
            logger.info(f"✅ 邮件发送成功: {to_email}")
            
            return {
                "success": True,
                "message": "邮件发送成功"
            }
            
        except asyncio.TimeoutError:
            logger.error(f"❌ 邮件发送超时: {to_email}")
            return {
                "success": False,
                "message": "邮件发送超时",
                "error": "smtp_timeout"
            }
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {to_email}, 错误: {e}")
            return {
                "success": False,
                "message": f"邮件发送失败: {str(e)}",
                "error": "smtp_error"
            }
    
    async def send_verification_code(
        self,
        to_email: str,
        code: str,
        purpose: str = "密码重置"
    ) -> Dict[str, Any]:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 验证码
            purpose: 用途（密码重置/账号验证等）
            
        Returns:
            发送结果
        """
        subject = f"KOOK消息转发系统 - {purpose}验证码"
        
        # HTML格式邮件
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #409EFF;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #409EFF;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #409EFF;
                    letter-spacing: 5px;
                }}
                .info {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin-top: 20px;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀 KOOK消息转发系统</div>
                    <p>{purpose}验证</p>
                </div>
                
                <p>您好！</p>
                
                <p>您正在进行<strong>{purpose}</strong>操作，您的验证码是：</p>
                
                <div class="code-box">
                    <div class="code">{code}</div>
                </div>
                
                <div class="info">
                    <p>✅ 验证码有效期：<strong>10分钟</strong></p>
                    <p>📧 请在10分钟内输入验证码完成验证</p>
                </div>
                
                <div class="warning">
                    <p><strong>⚠️ 安全提示：</strong></p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>如果这不是您的操作，请忽略此邮件</li>
                        <li>请勿将验证码透露给任何人</li>
                        <li>我们的客服不会索要您的验证码</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2025 KOOK消息转发系统</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本格式（备用）
        text_body = f"""
您好！

您正在进行{purpose}操作，您的验证码是：

{code}

验证码有效期：10分钟
请在10分钟内输入验证码完成验证。

⚠️ 安全提示：
- 如果这不是您的操作，请忽略此邮件
- 请勿将验证码透露给任何人
- 我们的客服不会索要您的验证码

---
此邮件由系统自动发送，请勿回复
© 2025 KOOK消息转发系统
        """
        
        # 优先发送HTML邮件，失败则发送纯文本
        result = await self.send_email(to_email, subject, html_body, html=True)
        
        if not result["success"]:
            # HTML发送失败，尝试纯文本
            result = await self.send_email(to_email, subject, text_body, html=False)
        
        return result
    
    async def send_notification(
        self,
        to_email: str,
        title: str,
        content: str,
        notification_type: str = "info"
    ) -> Dict[str, Any]:
        """
        发送通知邮件
        
        Args:
            to_email: 收件人邮箱
            title: 通知标题
            content: 通知内容
            notification_type: 通知类型（info/warning/error/success）
            
        Returns:
            发送结果
        """
        type_config = {
            "info": {"icon": "ℹ️", "color": "#409EFF"},
            "warning": {"icon": "⚠️", "color": "#E6A23C"},
            "error": {"icon": "❌", "color": "#F56C6C"},
            "success": {"icon": "✅", "color": "#67C23A"}
        }
        
        config = type_config.get(notification_type, type_config["info"])
        
        subject = f"KOOK消息转发系统 - {title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .notification {{
                    background: white;
                    border-left: 4px solid {config['color']};
                    padding: 20px;
                    border-radius: 4px;
                }}
                .title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: {config['color']};
                    margin-bottom: 15px;
                }}
                .content {{
                    white-space: pre-wrap;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="notification">
                    <div class="title">{config['icon']} {title}</div>
                    <div class="content">{content}</div>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2025 KOOK消息转发系统</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body, html=True)
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        测试SMTP连接
        
        Returns:
            {
                "success": bool,
                "message": str,
                "smtp_configured": bool,
                "connection_ok": bool
            }
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "SMTP未配置",
                "smtp_configured": False,
                "connection_ok": False
            }
        
        try:
            # 尝试连接SMTP服务器
            async with aiosmtplib.SMTP(
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                timeout=10
            ) as smtp:
                await smtp.connect()
                
                if settings.smtp_use_tls if hasattr(settings, 'smtp_use_tls') else True:
                    await smtp.starttls()
                
                await smtp.login(settings.smtp_username, settings.smtp_password)
                
                logger.info("✅ SMTP连接测试成功")
                
                return {
                    "success": True,
                    "message": "SMTP连接测试成功",
                    "smtp_configured": True,
                    "connection_ok": True
                }
        except Exception as e:
            logger.error(f"❌ SMTP连接测试失败: {e}")
            return {
                "success": False,
                "message": f"SMTP连接失败: {str(e)}",
                "smtp_configured": True,
                "connection_ok": False
            }


# 全局邮件发送器实例
email_sender = EmailSender()
