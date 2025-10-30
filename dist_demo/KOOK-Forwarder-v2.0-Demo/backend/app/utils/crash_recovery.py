"""
✅ P0-5深度优化: 崩溃恢复系统
自动保存未发送消息，程序重启后自动恢复
"""
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from .logger import logger
from ..config import DATA_DIR


class CrashRecoveryManager:
    """崩溃恢复管理器"""
    
    def __init__(self):
        self.recovery_dir = DATA_DIR / "recovery"
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        
        # 未发送消息文件
        self.pending_file = self.recovery_dir / "pending_messages.json"
        
        # 失败消息文件
        self.failed_file = self.recovery_dir / "failed_messages.json"
        
        # 锁文件
        self.lock_file = self.recovery_dir / "recovery.lock"
        
    async def save_pending_message(self, message: Dict[str, Any]):
        """
        保存待发送消息
        
        Args:
            message: 消息数据
        """
        try:
            # 读取现有消息
            pending_messages = await self._load_pending_messages()
            
            # 添加新消息
            message['saved_at'] = datetime.now().isoformat()
            message['status'] = 'pending'
            pending_messages.append(message)
            
            # 保存
            await self._save_pending_messages(pending_messages)
            
            logger.debug(f"✅ 保存待发送消息: {message.get('kook_message_id')}")
            
        except Exception as e:
            logger.error(f"保存待发送消息失败: {e}")
    
    async def save_failed_message(self, message: Dict[str, Any], error: str):
        """
        保存失败消息
        
        Args:
            message: 消息数据
            error: 错误信息
        """
        try:
            # 读取现有失败消息
            failed_messages = await self._load_failed_messages()
            
            # 添加新消息
            message['failed_at'] = datetime.now().isoformat()
            message['error'] = error
            message['retry_count'] = message.get('retry_count', 0) + 1
            failed_messages.append(message)
            
            # 保存
            await self._save_failed_messages(failed_messages)
            
            logger.warning(f"⚠️ 保存失败消息: {message.get('kook_message_id')}")
            
        except Exception as e:
            logger.error(f"保存失败消息失败: {e}")
    
    async def recover_pending_messages(self) -> List[Dict[str, Any]]:
        """
        恢复待发送消息
        
        Returns:
            待发送消息列表
        """
        try:
            messages = await self._load_pending_messages()
            
            if messages:
                logger.info(f"🔄 发现 {len(messages)} 条待发送消息，准备恢复")
            
            return messages
            
        except Exception as e:
            logger.error(f"恢复待发送消息失败: {e}")
            return []
    
    async def recover_failed_messages(self) -> List[Dict[str, Any]]:
        """
        恢复失败消息
        
        Returns:
            失败消息列表
        """
        try:
            messages = await self._load_failed_messages()
            
            # 只恢复重试次数<5的消息
            recoverable = [m for m in messages if m.get('retry_count', 0) < 5]
            
            if recoverable:
                logger.info(f"🔄 发现 {len(recoverable)} 条可恢复的失败消息")
            
            return recoverable
            
        except Exception as e:
            logger.error(f"恢复失败消息失败: {e}")
            return []
    
    async def clear_pending_message(self, message_id: str):
        """清除已发送的待发送消息"""
        try:
            messages = await self._load_pending_messages()
            messages = [m for m in messages if m.get('kook_message_id') != message_id]
            await self._save_pending_messages(messages)
            logger.debug(f"✅ 清除待发送消息: {message_id}")
        except Exception as e:
            logger.error(f"清除待发送消息失败: {e}")
    
    async def clear_all_pending(self):
        """清除所有待发送消息"""
        try:
            await self._save_pending_messages([])
            logger.info("✅ 清除所有待发送消息")
        except Exception as e:
            logger.error(f"清除失败: {e}")
    
    async def _load_pending_messages(self) -> List[Dict[str, Any]]:
        """加载待发送消息"""
        if not self.pending_file.exists():
            return []
        
        try:
            with open(self.pending_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    async def _save_pending_messages(self, messages: List[Dict[str, Any]]):
        """保存待发送消息"""
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    async def _load_failed_messages(self) -> List[Dict[str, Any]]:
        """加载失败消息"""
        if not self.failed_file.exists():
            return []
        
        try:
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    async def _save_failed_messages(self, messages: List[Dict[str, Any]]):
        """保存失败消息"""
        with open(self.failed_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def get_recovery_stats(self) -> Dict[str, int]:
        """
        获取恢复统计
        
        Returns:
            统计信息
        """
        try:
            pending = len(self._load_pending_messages_sync())
            failed = len(self._load_failed_messages_sync())
            
            return {
                "pending_count": pending,
                "failed_count": failed,
                "total_count": pending + failed
            }
        except:
            return {
                "pending_count": 0,
                "failed_count": 0,
                "total_count": 0
            }
    
    def _load_pending_messages_sync(self) -> List[Dict[str, Any]]:
        """同步加载待发送消息"""
        if not self.pending_file.exists():
            return []
        
        try:
            with open(self.pending_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _load_failed_messages_sync(self) -> List[Dict[str, Any]]:
        """同步加载失败消息"""
        if not self.failed_file.exists():
            return []
        
        try:
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []


# 全局单例
crash_recovery = CrashRecoveryManager()
