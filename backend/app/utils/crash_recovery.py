"""
崩溃恢复管理器
功能：程序崩溃时自动保存待发送消息，重启后自动恢复
"""

import pickle
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import settings
from ..utils.logger import logger


class CrashRecoveryManager:
    """崩溃恢复管理器"""
    
    def __init__(self):
        self.recovery_dir = Path(settings.data_dir) / "recovery"
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前会话ID（时间戳）
        self.session_id = int(time.time())
        self.recovery_file = self.recovery_dir / f"session_{self.session_id}.pkl"
        
        # 恢复数据缓存
        self._pending_messages = []
        self._last_save_time = 0
        self._save_interval = 5  # 每5秒保存一次
        
        logger.info(f"崩溃恢复管理器初始化: 会话ID={self.session_id}")
    
    def add_pending_message(self, message: Dict[str, Any]):
        """
        添加待发送消息到恢复队列
        
        Args:
            message: 消息数据
        """
        self._pending_messages.append({
            'message': message,
            'timestamp': time.time(),
            'retry_count': 0,
        })
        
        # 如果距离上次保存超过interval，则保存
        current_time = time.time()
        if current_time - self._last_save_time >= self._save_interval:
            self.save_pending_messages()
    
    def remove_pending_message(self, message_id: str):
        """
        从恢复队列中移除已成功发送的消息
        
        Args:
            message_id: 消息ID
        """
        self._pending_messages = [
            m for m in self._pending_messages
            if m['message'].get('message_id') != message_id
        ]
    
    def save_pending_messages(self):
        """保存待发送消息到文件"""
        if not self._pending_messages:
            return
        
        try:
            data = {
                'version': settings.app_version,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'message_count': len(self._pending_messages),
                'messages': self._pending_messages,
            }
            
            # 使用pickle序列化（支持复杂对象）
            with open(self.recovery_file, 'wb') as f:
                pickle.dump(data, f)
            
            self._last_save_time = time.time()
            
            logger.debug(f"已保存 {len(self._pending_messages)} 条待发送消息到恢复文件")
            
        except Exception as e:
            logger.error(f"保存恢复文件失败: {str(e)}")
    
    def load_pending_messages(self) -> List[Dict[str, Any]]:
        """
        加载未完成的消息（程序启动时调用）
        
        Returns:
            待恢复的消息列表
        """
        try:
            # 查找所有恢复文件（按时间倒序）
            recovery_files = sorted(
                self.recovery_dir.glob("session_*.pkl"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if not recovery_files:
                logger.info("没有待恢复的消息")
                return []
            
            # 加载最新的恢复文件
            latest_file = recovery_files[0]
            
            with open(latest_file, 'rb') as f:
                data = pickle.load(f)
            
            messages = data.get('messages', [])
            
            if messages:
                logger.warning("=" * 60)
                logger.warning("⚠️ 检测到上次程序未正常退出")
                logger.warning(f"   恢复文件时间: {data.get('timestamp')}")
                logger.warning(f"   待恢复消息数: {len(messages)}")
                logger.warning(f"   会话ID: {data.get('session_id')}")
                logger.warning("=" * 60)
                
                # 显示恢复提示（前5条）
                logger.info("待恢复的消息（前5条）：")
                for i, msg_data in enumerate(messages[:5]):
                    msg = msg_data['message']
                    logger.info(f"  {i+1}. {msg.get('channel_id')} - {msg.get('content', '')[:50]}...")
                
                if len(messages) > 5:
                    logger.info(f"  ... 还有 {len(messages) - 5} 条消息")
            
            # 删除已使用的恢复文件
            latest_file.unlink()
            logger.info(f"✅ 已删除恢复文件: {latest_file.name}")
            
            # 清理7天前的旧恢复文件
            self.cleanup_old_recovery_files()
            
            return messages
            
        except Exception as e:
            logger.error(f"加载恢复文件失败: {str(e)}")
            return []
    
    def cleanup_old_recovery_files(self, days: int = 7):
        """
        清理旧的恢复文件
        
        Args:
            days: 保留天数
        """
        try:
            cutoff_time = time.time() - (days * 86400)
            cleaned_count = 0
            
            for file in self.recovery_dir.glob("session_*.pkl"):
                if file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    cleaned_count += 1
                    logger.debug(f"已清理旧恢复文件: {file.name}")
            
            if cleaned_count > 0:
                logger.info(f"✅ 已清理 {cleaned_count} 个过期恢复文件（>{days}天）")
                
        except Exception as e:
            logger.error(f"清理恢复文件失败: {str(e)}")
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """
        获取恢复统计信息
        
        Returns:
            统计信息字典
        """
        try:
            recovery_files = list(self.recovery_dir.glob("session_*.pkl"))
            
            total_messages = 0
            oldest_file = None
            newest_file = None
            
            for file in recovery_files:
                try:
                    with open(file, 'rb') as f:
                        data = pickle.load(f)
                        total_messages += len(data.get('messages', []))
                    
                    mtime = file.stat().st_mtime
                    if oldest_file is None or mtime < oldest_file[1]:
                        oldest_file = (file, mtime)
                    if newest_file is None or mtime > newest_file[1]:
                        newest_file = (file, mtime)
                        
                except:
                    continue
            
            return {
                'total_files': len(recovery_files),
                'total_pending_messages': total_messages,
                'current_session_messages': len(self._pending_messages),
                'oldest_file_time': datetime.fromtimestamp(oldest_file[1]).isoformat() if oldest_file else None,
                'newest_file_time': datetime.fromtimestamp(newest_file[1]).isoformat() if newest_file else None,
            }
            
        except Exception as e:
            logger.error(f"获取恢复统计失败: {str(e)}")
            return {}
    
    def force_save(self):
        """强制保存（在程序即将退出时调用）"""
        if self._pending_messages:
            logger.info(f"💾 程序退出前保存 {len(self._pending_messages)} 条待发送消息...")
            self.save_pending_messages()
            logger.info("✅ 恢复数据已保存")
    
    def clear_recovery_data(self):
        """清空所有恢复数据"""
        try:
            for file in self.recovery_dir.glob("session_*.pkl"):
                file.unlink()
            
            self._pending_messages = []
            logger.info("✅ 已清空所有恢复数据")
            
        except Exception as e:
            logger.error(f"清空恢复数据失败: {str(e)}")


# 全局实例
crash_recovery_manager = CrashRecoveryManager()
