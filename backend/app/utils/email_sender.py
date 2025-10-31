"""
邮件告警系统 - P0优化
支持SMTP发送邮件，用于系统异常告警、通知等
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import List, Optional
from datetime import datetime
from ..config import settings
from .logger import logger


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.from_email = None
        self.from_name = "KOOK消息转发系统"
        self.enabled = False
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """从数据库加载邮件配置"""
        try:
            from ..database import db
            
            # 读取系统配置
            configs = {
                'smtp_host': None,
                'smtp_port': None,
                'smtp_username': None,
                'smtp_password': None,
                'from_email': None,
                'from_name': None,
                'email_enabled': None
            }
            
            for key in configs.keys():
                result = db.execute(
                    "SELECT value FROM system_config WHERE key = ?",
                    (key,)
                ).fetchone()
                if result:
                    configs[key] = result['value']
            
            # 设置配置
            self.smtp_host = configs.get('smtp_host')
            self.smtp_port = int(configs.get('smtp_port', 587))
            self.smtp_username = configs.get('smtp_username')
            self.smtp_password = configs.get('smtp_password')
            self.from_email = configs.get('from_email') or self.smtp_username
            self.from_name = configs.get('from_name') or self.from_name
            self.enabled = configs.get('email_enabled') == 'true'
            
            if self.enabled:
                logger.info(f"邮件告警已启用: {self.from_email}")
            else:
                logger.info("邮件告警未启用")
                
        except Exception as e:
            logger.error(f"加载邮件配置失败: {str(e)}")
            self.enabled = False
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        content: str,
        html: bool = True,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_emails: 收件人列表
            subject: 邮件主题
            content: 邮件内容
            html: 是否为HTML格式
            cc_emails: 抄送列表
            bcc_emails: 密送列表
            
        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.warning("邮件告警未启用，跳过发送")
            return False
        
        if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
            logger.error("邮件配置不完整，无法发送")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # 添加内容
            if html:
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_port == 587,
                start_tls=self.smtp_port == 587,
                timeout=30
            )
            
            logger.info(f"邮件发送成功: {subject} -> {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    async def send_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        details: Optional[str] = None,
        level: str = "warning"
    ) -> bool:
        """
        发送告警邮件
        
        Args:
            alert_type: 告警类型（service_down/rate_limit/queue_backlog等）
            title: 告警标题
            message: 告警消息
            details: 详细信息
            level: 严重级别（info/warning/error/critical）
            
        Returns:
            是否发送成功
        """
        # 从配置读取告警接收邮箱
        from ..database import db
        result = db.execute(
            "SELECT value FROM system_config WHERE key = 'alert_emails'"
        ).fetchone()
        
        if not result or not result['value']:
            logger.warning("未配置告警接收邮箱")
            return False
        
        to_emails = result['value'].split(',')
        
        # 构建HTML邮件内容
        level_colors = {
            'info': '#409EFF',
            'warning': '#E6A23C',
            'error': '#F56C6C',
            'critical': '#F56C6C'
        }
        
        level_labels = {
            'info': '信息',
            'warning': '警告',
            'error': '错误',
            'critical': '严重'
        }
        
        color = level_colors.get(level, '#409EFF')
        level_label = level_labels.get(level, '未知')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: {color};
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-top: none;
                }}
                .alert-info {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid {color};
                }}
                .alert-label {{
                    font-weight: bold;
                    color: {color};
                    margin-bottom: 5px;
                }}
                .details {{
                    background: #fff;
                    padding: 10px;
                    margin-top: 10px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    font-family: monospace;
                    font-size: 12px;
                    white-space: pre-wrap;
                }}
                .footer {{
                    background: #f9f9f9;
                    padding: 15px;
                    text-align: center;
                    border: 1px solid #ddd;
                    border-top: none;
                    border-radius: 0 0 5px 5px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ 系统告警</h1>
            </div>
            <div class="content">
                <div class="alert-info">
                    <div class="alert-label">告警级别: {level_label}</div>
                    <div class="alert-label">告警类型: {alert_type}</div>
                    <div class="alert-label">告警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                <h2 style="color: {color};">{title}</h2>
                <p>{message}</p>
                
                {f'<div class="details"><strong>详细信息:</strong><br>{details}</div>' if details else ''}
            </div>
            <div class="footer">
                <p>此邮件由 KOOK消息转发系统 自动发送，请勿回复。</p>
                <p>如需关闭告警邮件，请在系统设置中修改。</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"[{level_label}] {title}"
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            content=html_content,
            html=True
        )
    
    async def send_daily_report(
        self,
        report_data: dict
    ) -> bool:
        """
        发送每日报告邮件
        
        Args:
            report_data: 报告数据
            
        Returns:
            是否发送成功
        """
        # 从配置读取报告接收邮箱
        from ..database import db
        result = db.execute(
            "SELECT value FROM system_config WHERE key = 'report_emails'"
        ).fetchone()
        
        if not result or not result['value']:
            logger.info("未配置报告接收邮箱，跳过发送")
            return False
        
        to_emails = result['value'].split(',')
        
        # 构建报告HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .stats-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    padding: 20px;
                    background: #f9f9f9;
                }}
                .stat-card {{
                    flex: 1;
                    min-width: 200px;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                .footer {{
                    background: #f9f9f9;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 10px 10px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 每日运行报告</h1>
                <p>{datetime.now().strftime('%Y年%m月%d日')}</p>
            </div>
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{report_data.get('total_messages', 0)}</div>
                    <div class="stat-label">转发消息总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report_data.get('success_rate', 0)}%</div>
                    <div class="stat-label">转发成功率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report_data.get('avg_latency', 0)}ms</div>
                    <div class="stat-label">平均延迟</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report_data.get('active_accounts', 0)}</div>
                    <div class="stat-label">活跃账号数</div>
                </div>
            </div>
            <div class="footer">
                <p>此邮件由 KOOK消息转发系统 自动发送</p>
                <p>如需关闭每日报告，请在系统设置中修改</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"KOOK消息转发系统 - 每日报告 ({datetime.now().strftime('%Y-%m-%d')})"
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            content=html_content,
            html=True
        )
    
    async def test_connection(self) -> tuple[bool, str]:
        """
        测试邮件服务器连接
        
        Returns:
            (是否成功, 消息)
        """
        if not self.enabled:
            return False, "邮件告警未启用"
        
        if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
            return False, "邮件配置不完整"
        
        try:
            # 尝试连接SMTP服务器
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                timeout=10
            )
            
            await smtp.connect()
            
            if self.smtp_port == 587:
                await smtp.starttls()
            
            await smtp.login(self.smtp_username, self.smtp_password)
            await smtp.quit()
            
            return True, "邮件服务器连接成功"
            
        except Exception as e:
            return False, f"连接失败: {str(e)}"


# 全局邮件发送器实例
email_sender = EmailSender()
