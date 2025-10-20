"""
错误诊断模块（v1.11.0新增）
提供详细的错误诊断和自动修复建议
"""
import re
from typing import Dict, Any, Optional, Callable, List
from .logger import logger


class ErrorDiagnostic:
    """错误诊断器"""
    
    # 错误诊断规则字典
    DIAGNOSIS_RULES = {
        'rate_limit': {
            'keywords': ['rate limit', 'too many requests', '429', 'rate_limited'],
            'patterns': [r'429\s+too\s+many\s+requests', r'rate\s+limit\s+exceeded'],
            'severity': 'warning',
            'solution': '目标平台API限流，请等待或配置多个Webhook/Bot以提升吞吐量',
            'suggestions': [
                '等待限流时间结束（通常1-5分钟）',
                '配置多个Webhook/Bot实现负载均衡',
                '降低消息发送频率',
                '检查是否有过多的频道映射'
            ],
            'auto_fixable': False
        },
        
        'invalid_token': {
            'keywords': ['unauthorized', 'invalid token', '401', 'invalid webhook', 'forbidden', '403'],
            'patterns': [r'401\s+unauthorized', r'403\s+forbidden', r'invalid\s+(token|webhook|bot)'],
            'severity': 'error',
            'solution': 'Bot Token或Webhook URL无效，请重新配置',
            'suggestions': [
                '检查Discord Webhook URL是否正确',
                '检查Telegram Bot Token是否有效',
                '检查飞书App ID和Secret是否正确',
                '确认Bot已被添加到目标群组/频道',
                '重新生成Token或Webhook URL'
            ],
            'auto_fixable': False
        },
        
        'network_timeout': {
            'keywords': ['timeout', 'connection reset', 'connection refused', 'timed out'],
            'patterns': [r'(connection|request)\s+(timeout|timed\s+out)', r'connection\s+reset'],
            'severity': 'warning',
            'solution': '网络连接超时，检查网络状态或配置代理',
            'suggestions': [
                '检查网络连接是否正常',
                '检查目标平台服务是否可用',
                '增加请求超时时间',
                '配置HTTP代理',
                '稍后重试'
            ],
            'auto_fixable': True  # 可以自动重试
        },
        
        'message_too_long': {
            'keywords': ['message too long', 'content too long', 'text too long', '2000', '4096'],
            'patterns': [r'message\s+(is\s+)?too\s+long', r'content\s+exceeds?\s+\d+\s+characters'],
            'severity': 'warning',
            'solution': '消息内容过长，已自动分段或截断',
            'suggestions': [
                'Discord消息限制2000字符',
                'Telegram消息限制4096字符',
                '系统会自动智能分段发送',
                '检查消息内容是否异常过长'
            ],
            'auto_fixable': True  # 可以自动分段
        },
        
        'channel_not_found': {
            'keywords': ['channel not found', 'chat not found', '404', 'unknown channel'],
            'patterns': [r'(channel|chat)\s+not\s+found', r'404\s+not\s+found', r'unknown\s+(channel|chat)'],
            'severity': 'error',
            'solution': '目标频道/群组不存在或Bot无权访问',
            'suggestions': [
                '检查频道映射配置中的目标频道ID是否正确',
                '确认Bot已被添加到目标频道/群组',
                '检查Bot是否有发送消息的权限',
                '重新配置频道映射'
            ],
            'auto_fixable': False
        },
        
        'image_upload_failed': {
            'keywords': ['image upload', 'file upload', 'upload failed', 'image error'],
            'patterns': [r'image\s+upload\s+failed', r'file\s+upload\s+(error|failed)'],
            'severity': 'warning',
            'solution': '图片上传失败，尝试使用本地图床',
            'suggestions': [
                '图片可能过大，系统会自动压缩',
                '使用图床模式作为备用方案',
                '检查图片URL是否有防盗链',
                '检查目标平台的图片大小限制'
            ],
            'auto_fixable': True  # 可以切换到图床模式
        },
        
        'webhook_invalid': {
            'keywords': ['invalid webhook', 'webhook not found', 'invalid url'],
            'patterns': [r'invalid\s+webhook', r'webhook\s+not\s+found'],
            'severity': 'error',
            'solution': 'Webhook URL无效或已被删除',
            'suggestions': [
                '重新创建Discord Webhook',
                '检查Webhook URL是否完整',
                '确认Webhook未被删除或禁用',
                '在Bot配置页重新配置Webhook'
            ],
            'auto_fixable': False
        },
        
        'json_decode_error': {
            'keywords': ['json', 'decode', 'parse error', 'invalid json'],
            'patterns': [r'json\s+(decode|parse)\s+error', r'invalid\s+json'],
            'severity': 'error',
            'solution': 'API响应格式错误，可能是平台API变更',
            'suggestions': [
                '检查目标平台API是否正常',
                '查看详细错误日志',
                '可能需要更新转发器代码',
                '联系开发者反馈问题'
            ],
            'auto_fixable': False
        },
        
        'bot_blocked': {
            'keywords': ['bot blocked', 'bot kicked', 'bot banned', 'bot removed'],
            'patterns': [r'bot\s+(was\s+)?(blocked|kicked|banned|removed)'],
            'severity': 'error',
            'solution': 'Bot被移除或封禁，请重新添加',
            'suggestions': [
                '将Bot重新添加到目标群组',
                '检查Bot是否违反平台规则',
                '确认Bot账号状态正常',
                '联系群组管理员确认'
            ],
            'auto_fixable': False
        },
        
        'permission_denied': {
            'keywords': ['permission denied', 'access denied', 'insufficient permissions'],
            'patterns': [r'(permission|access)\s+denied', r'insufficient\s+permissions'],
            'severity': 'error',
            'solution': 'Bot权限不足，无法发送消息',
            'suggestions': [
                '检查Bot在目标频道的权限',
                '确认Bot有发送消息的权限',
                'Discord: 检查频道权限设置',
                'Telegram: 确认Bot是管理员（如需要）',
                '重新配置Bot权限'
            ],
            'auto_fixable': False
        }
    }
    
    @classmethod
    def diagnose(cls, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        诊断错误并返回详细信息
        
        Args:
            error: 异常对象
            context: 错误上下文（platform, message_type等）
            
        Returns:
            诊断结果字典
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # 默认诊断结果
        result = {
            'error_type': error_type,
            'error_message': str(error),
            'matched_rule': None,
            'severity': 'error',
            'solution': '未知错误，请查看详细日志',
            'suggestions': ['查看系统日志获取更多信息', '稍后重试', '如问题持续，请联系开发者'],
            'auto_fixable': False,
            'context': context or {}
        }
        
        # 遍历诊断规则
        for rule_name, rule in cls.DIAGNOSIS_RULES.items():
            # 检查关键词匹配
            keyword_match = any(keyword in error_str for keyword in rule['keywords'])
            
            # 检查正则模式匹配
            pattern_match = any(re.search(pattern, error_str, re.IGNORECASE) 
                              for pattern in rule.get('patterns', []))
            
            if keyword_match or pattern_match:
                result.update({
                    'matched_rule': rule_name,
                    'severity': rule['severity'],
                    'solution': rule['solution'],
                    'suggestions': rule['suggestions'],
                    'auto_fixable': rule['auto_fixable']
                })
                
                logger.info(f"🔍 错误诊断匹配: {rule_name}")
                break
        
        return result
    
    @classmethod
    def format_diagnosis_message(cls, diagnosis: Dict[str, Any]) -> str:
        """
        格式化诊断信息为易读的文本
        
        Args:
            diagnosis: 诊断结果
            
        Returns:
            格式化的诊断消息
        """
        severity_emoji = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        emoji = severity_emoji.get(diagnosis['severity'], '❓')
        
        message = f"\n{emoji} 错误诊断报告\n"
        message += f"{'='*50}\n"
        message += f"错误类型: {diagnosis['error_type']}\n"
        message += f"错误信息: {diagnosis['error_message']}\n"
        
        if diagnosis['matched_rule']:
            message += f"匹配规则: {diagnosis['matched_rule']}\n"
        
        message += f"\n💡 解决方案:\n{diagnosis['solution']}\n"
        
        if diagnosis['suggestions']:
            message += f"\n📋 建议步骤:\n"
            for i, suggestion in enumerate(diagnosis['suggestions'], 1):
                message += f"  {i}. {suggestion}\n"
        
        if diagnosis['auto_fixable']:
            message += f"\n🔧 系统将尝试自动修复\n"
        
        if diagnosis['context']:
            message += f"\n📊 错误上下文:\n"
            for key, value in diagnosis['context'].items():
                message += f"  - {key}: {value}\n"
        
        message += f"{'='*50}\n"
        
        return message
    
    @classmethod
    def get_auto_fix_strategy(cls, diagnosis: Dict[str, Any]) -> Optional[str]:
        """
        根据诊断结果获取自动修复策略
        
        Args:
            diagnosis: 诊断结果
            
        Returns:
            修复策略名称（retry/switch_strategy/skip等）
        """
        if not diagnosis['auto_fixable']:
            return None
        
        rule_name = diagnosis.get('matched_rule')
        
        # 根据不同的错误类型返回不同的修复策略
        fix_strategies = {
            'network_timeout': 'retry',
            'message_too_long': 'auto_split',
            'image_upload_failed': 'switch_to_imgbed',
            'rate_limit': 'wait_and_retry'
        }
        
        return fix_strategies.get(rule_name)


class DiagnosticLogger:
    """诊断日志记录器"""
    
    def __init__(self):
        self.diagnostics_history = []
        self.max_history = 100
    
    def log_diagnosis(self, diagnosis: Dict[str, Any]):
        """
        记录诊断结果
        
        Args:
            diagnosis: 诊断结果
        """
        # 添加时间戳
        import time
        diagnosis['timestamp'] = time.time()
        
        # 添加到历史记录
        self.diagnostics_history.append(diagnosis)
        
        # 限制历史记录大小
        if len(self.diagnostics_history) > self.max_history:
            self.diagnostics_history.pop(0)
        
        # 记录到日志
        formatted_message = ErrorDiagnostic.format_diagnosis_message(diagnosis)
        logger.error(formatted_message)
    
    def get_recent_diagnostics(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的诊断记录
        
        Args:
            count: 返回数量
            
        Returns:
            诊断记录列表
        """
        return self.diagnostics_history[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取诊断统计信息
        
        Returns:
            统计信息字典
        """
        if not self.diagnostics_history:
            return {
                'total_count': 0,
                'by_severity': {},
                'by_rule': {},
                'auto_fixable_count': 0
            }
        
        stats = {
            'total_count': len(self.diagnostics_history),
            'by_severity': {},
            'by_rule': {},
            'auto_fixable_count': 0
        }
        
        for diag in self.diagnostics_history:
            # 按严重程度统计
            severity = diag.get('severity', 'unknown')
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # 按规则统计
            rule = diag.get('matched_rule', 'unmatched')
            stats['by_rule'][rule] = stats['by_rule'].get(rule, 0) + 1
            
            # 统计可自动修复的数量
            if diag.get('auto_fixable'):
                stats['auto_fixable_count'] += 1
        
        return stats


# 全局诊断日志记录器
diagnostic_logger = DiagnosticLogger()
