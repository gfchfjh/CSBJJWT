"""
🔔 P2-2优化: 通知系统增强（终极版）

功能：
1. 分类通知（成功/警告/错误/信息）
2. 静默时段设置（默认22:00-8:00）
3. 通知历史记录（保留100条）
4. 通知统计信息
5. 通知点击跳转功能

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
from typing import Optional, Dict, List
from datetime import datetime, time as dt_time
from collections import deque
from ..utils.logger import logger
from ..database import db


class NotificationManager:
    """通知管理器（增强版）"""
    
    def __init__(self):
        # 通知历史（内存中保留最近100条）
        self.history = deque(maxlen=100)
        
        # 通知设置
        self.settings = {
            'enable_success': False,  # 成功通知（默认关闭，太频繁）
            'enable_warning': True,   # 警告通知
            'enable_error': True,     # 错误通知
            'enable_info': True,      # 信息通知
            'quiet_start': dt_time(22, 0),  # 静默开始时间
            'quiet_end': dt_time(8, 0),     # 静默结束时间
            'enable_quiet_time': True       # 启用静默时段
        }
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'warning': 0,
            'error': 0,
            'info': 0,
            'suppressed': 0  # 因静默时段被抑制的通知数
        }
        
        logger.info("✅ 通知管理器已初始化")
    
    def send(
        self, 
        notification_type: str, 
        title: str, 
        body: str,
        action: Optional[str] = None
    ) -> bool:
        """
        发送通知
        
        Args:
            notification_type: 通知类型（success/warning/error/info）
            title: 标题
            body: 内容
            action: 点击操作（可选）
            
        Returns:
            是否发送成功
        """
        # 检查是否启用该类型通知
        if not self._is_enabled(notification_type):
            logger.debug(f"通知类型{notification_type}已禁用，跳过")
            return False
        
        # 检查是否在静默时段
        if self._is_quiet_time():
            logger.debug(f"当前在静默时段，通知已抑制: {title}")
            self.stats['suppressed'] += 1
            
            # 仍然记录到历史
            self._add_to_history(notification_type, title, body, action, suppressed=True)
            
            return False
        
        # 记录到历史
        self._add_to_history(notification_type, title, body, action)
        
        # 更新统计
        self.stats['total'] += 1
        self.stats[notification_type] = self.stats.get(notification_type, 0) + 1
        
        # 实际发送通知（由Electron主进程处理）
        logger.info(f"📢 发送通知[{notification_type}]: {title}")
        
        return True
    
    def _is_enabled(self, notification_type: str) -> bool:
        """检查通知类型是否启用"""
        key = f'enable_{notification_type}'
        return self.settings.get(key, True)
    
    def _is_quiet_time(self) -> bool:
        """检查是否在静默时段"""
        if not self.settings['enable_quiet_time']:
            return False
        
        now = datetime.now().time()
        quiet_start = self.settings['quiet_start']
        quiet_end = self.settings['quiet_end']
        
        # 处理跨午夜的情况（如22:00-8:00）
        if quiet_start > quiet_end:
            # 跨午夜：22:00-23:59 或 0:00-8:00
            return now >= quiet_start or now < quiet_end
        else:
            # 不跨午夜：例如 8:00-18:00
            return quiet_start <= now < quiet_end
    
    def _add_to_history(
        self, 
        notification_type: str,
        title: str,
        body: str,
        action: Optional[str] = None,
        suppressed: bool = False
    ):
        """添加到历史记录"""
        notification = {
            'id': len(self.history) + 1,
            'type': notification_type,
            'title': title,
            'body': body,
            'action': action,
            'suppressed': suppressed,
            'clicked': False,
            'created_at': datetime.now().isoformat()
        }
        
        self.history.append(notification)
        
        # 同时保存到数据库
        try:
            db.save_notification_history(notification)
        except Exception as e:
            logger.warning(f"保存通知历史失败: {str(e)}")
    
    def get_history(
        self, 
        limit: int = 100,
        notification_type: Optional[str] = None
    ) -> List[Dict]:
        """
        获取通知历史
        
        Args:
            limit: 返回数量限制
            notification_type: 过滤类型（可选）
            
        Returns:
            通知历史列表
        """
        history_list = list(self.history)
        
        # 过滤类型
        if notification_type:
            history_list = [
                n for n in history_list 
                if n['type'] == notification_type
            ]
        
        # 限制数量
        return history_list[-limit:]
    
    def clear_history(self):
        """清空历史记录"""
        self.history.clear()
        
        try:
            db.clear_notification_history()
            logger.info("✅ 通知历史已清空")
        except Exception as e:
            logger.error(f"清空通知历史失败: {str(e)}")
    
    def mark_as_clicked(self, notification_id: int):
        """标记通知为已点击"""
        for notification in self.history:
            if notification['id'] == notification_id:
                notification['clicked'] = True
                break
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'history_count': len(self.history),
            'quiet_time_enabled': self.settings['enable_quiet_time'],
            'quiet_start': self.settings['quiet_start'].strftime('%H:%M'),
            'quiet_end': self.settings['quiet_end'].strftime('%H:%M')
        }
    
    def update_settings(self, new_settings: Dict):
        """更新设置"""
        for key, value in new_settings.items():
            if key in self.settings:
                # 处理时间类型
                if key in ['quiet_start', 'quiet_end'] and isinstance(value, str):
                    hour, minute = map(int, value.split(':'))
                    self.settings[key] = dt_time(hour, minute)
                else:
                    self.settings[key] = value
        
        logger.info("✅ 通知设置已更新")
    
    def get_settings(self) -> Dict:
        """获取当前设置"""
        return {
            **self.settings,
            'quiet_start': self.settings['quiet_start'].strftime('%H:%M'),
            'quiet_end': self.settings['quiet_end'].strftime('%H:%M')
        }


# 创建全局实例
notification_manager = NotificationManager()
