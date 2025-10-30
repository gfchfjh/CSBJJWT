"""
邮件通知器
✅ P0-27: 邮件告警通知
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from ..utils.logger import logger
from ..config import settings


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self):
        self.enabled = getattr(settings, 'email_alert_enabled', False)
        self.smtp_host = getattr(settings, 'smtp_host', '')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.from_email = getattr(settings, 'email_from', '')
        self.to_emails = getattr(settings, 'email_to', [])
        
        # 告警级别
        self.alert_levels = {
            'info': '信息',
            'warning': '警告',
            'error': '错误',
            'critical': '严重'
        }
        
        # 统计
        self.stats = {
            'total_sent': 0,
            'success': 0,
            'failed': 0
        }
    
    async def send_alert(
        self,
        title: str,
        message: str,
        level: str = 'info',
        details: Optional[Dict] = None
    ) -> bool:
        """
        发送告警邮件
        
        Args:
            title: 标题
            message: 消息内容
            level: 告警级别（info/warning/error/critical）
            details: 详细信息
            
        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.debug("邮件通知未启用")
            return False
        
        if not self._validate_config():
            logger.error("邮件配置无效")
            return False
        
        self.stats['total_sent'] += 1
        
        try:
            # 构建邮件
            msg = self._build_email(title, message, level, details)
            
            # 发送
            await self._send_email(msg)
            
            self.stats['success'] += 1
            logger.info(f"告警邮件发送成功: {title}")
            
            return True
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"发送告警邮件失败: {str(e)}")
            return False
    
    def _validate_config(self) -> bool:
        """验证配置"""
        required = [
            self.smtp_host,
            self.smtp_user,
            self.smtp_password,
            self.from_email
        ]
        
        if not all(required):
            return False
        
        if not self.to_emails:
            return False
        
        return True
    
    def _build_email(
        self,
        title: str,
        message: str,
        level: str,
        details: Optional[Dict]
    ) -> MIMEMultipart:
        """构建邮件"""
        # 创建邮件
        msg = MIMEMultipart('alternative')
        
        # 设置头部
        level_text = self.alert_levels.get(level, '信息')
        msg['Subject'] = f"[{level_text}] {title}"
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)
        
        # 构建HTML内容
        html = self._build_html_content(title, message, level, details)
        
        # 构建纯文本内容
        text = self._build_text_content(title, message, level, details)
        
        # 添加内容
        part1 = MIMEText(text, 'plain', 'utf-8')
        part2 = MIMEText(html, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    def _build_html_content(
        self,
        title: str,
        message: str,
        level: str,
        details: Optional[Dict]
    ) -> str:
        """构建HTML邮件内容"""
        # 级别颜色
        level_colors = {
            'info': '#409EFF',
            'warning': '#E6A23C',
            'error': '#F56C6C',
            'critical': '#C71585'
        }
        
        color = level_colors.get(level, '#409EFF')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: {color};
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f5f7fa;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                }}
                .details {{
                    background: white;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
                .footer {{
                    text-align: center;
                    color: #909399;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 {title}</h2>
                    <p>告警级别: {self.alert_levels.get(level, '信息')}</p>
                </div>
                
                <div class="content">
                    <p><strong>消息内容:</strong></p>
                    <p>{message}</p>
                    
                    {self._build_details_html(details) if details else ''}
                    
                    <p style="margin-top: 20px;">
                        <strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
                
                <div class="footer">
                    <p>此邮件由KOOK消息转发系统自动发送</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_details_html(self, details: Dict) -> str:
        """构建详细信息HTML"""
        html = '<div class="details"><h3>详细信息</h3><ul>'
        
        for key, value in details.items():
            html += f'<li><strong>{key}:</strong> {value}</li>'
        
        html += '</ul></div>'
        
        return html
    
    def _build_text_content(
        self,
        title: str,
        message: str,
        level: str,
        details: Optional[Dict]
    ) -> str:
        """构建纯文本邮件内容"""
        text = f"""
【{self.alert_levels.get(level, '信息')}】{title}

{message}

{'详细信息:' if details else ''}
{self._build_details_text(details) if details else ''}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
此邮件由KOOK消息转发系统自动发送
        """
        
        return text.strip()
    
    def _build_details_text(self, details: Dict) -> str:
        """构建详细信息文本"""
        lines = []
        for key, value in details.items():
            lines.append(f"- {key}: {value}")
        return '\n'.join(lines)
    
    async def _send_email(self, msg: MIMEMultipart):
        """发送邮件"""
        try:
            # 连接SMTP服务器
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
        except Exception as e:
            logger.error(f"SMTP发送失败: {str(e)}")
            raise
    
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """测试邮件配置"""
        try:
            await self.send_alert(
                title='测试邮件',
                message='这是一封测试邮件，用于验证邮件配置是否正确。',
                level='info'
            )
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats


# 全局实例
email_notifier = EmailNotifier()


# 便捷方法
async def send_info_alert(title: str, message: str, details: Optional[Dict] = None):
    """发送信息级别告警"""
    await email_notifier.send_alert(title, message, 'info', details)


async def send_warning_alert(title: str, message: str, details: Optional[Dict] = None):
    """发送警告级别告警"""
    await email_notifier.send_alert(title, message, 'warning', details)


async def send_error_alert(title: str, message: str, details: Optional[Dict] = None):
    """发送错误级别告警"""
    await email_notifier.send_alert(title, message, 'error', details)


async def send_critical_alert(title: str, message: str, details: Optional[Dict] = None):
    """发送严重级别告警"""
    await email_notifier.send_alert(title, message, 'critical', details)
