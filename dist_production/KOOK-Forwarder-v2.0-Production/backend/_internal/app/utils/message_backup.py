"""
消息备份器
✅ P0-10优化：崩溃恢复机制
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from ..config import settings
from ..utils.logger import logger


class MessageBackup:
    """消息备份器 - 用于崩溃恢复"""
    
    def __init__(self):
        self.backup_dir = Path(settings.data_dir) / "message_backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_file = self.backup_dir / "pending_messages.jsonl"
        
        logger.info("✅ 消息备份器已初始化")
    
    def save_message(self, message: Dict[str, Any]):
        """
        保存待发送消息到磁盘
        
        Args:
            message: 消息数据
        """
        try:
            with open(self.backup_file, 'a', encoding='utf-8') as f:
                json.dump(message, f, ensure_ascii=False)
                f.write('\n')
            logger.debug(f"消息已备份: {message.get('message_id', 'unknown')}")
        except Exception as e:
            logger.error(f"备份消息失败: {str(e)}")
    
    def load_pending_messages(self) -> List[Dict[str, Any]]:
        """
        加载待发送消息
        
        Returns:
            消息列表
        """
        if not self.backup_file.exists():
            return []
        
        messages = []
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            message = json.loads(line)
                            messages.append(message)
                        except json.JSONDecodeError:
                            logger.warning(f"跳过无效的备份行: {line[:50]}")
            
            if messages:
                logger.info(f"从备份加载了 {len(messages)} 条待发送消息")
            
            return messages
        except Exception as e:
            logger.error(f"加载备份消息失败: {str(e)}")
            return []
    
    def remove_message(self, message_id: str):
        """
        从备份中移除已发送的消息
        
        Args:
            message_id: 消息ID
        """
        if not self.backup_file.exists():
            return
        
        try:
            # 读取所有消息
            messages = []
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            msg = json.loads(line)
                            if msg.get('message_id') != message_id:
                                messages.append(msg)
                        except:
                            pass
            
            # 重写文件
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                for msg in messages:
                    json.dump(msg, f, ensure_ascii=False)
                    f.write('\n')
            
            logger.debug(f"消息已从备份移除: {message_id}")
        except Exception as e:
            logger.error(f"移除备份消息失败: {str(e)}")
    
    def remove_messages_batch(self, message_ids: List[str]):
        """
        批量移除消息（性能优化）
        """
        if not self.backup_file.exists() or not message_ids:
            return
        
        try:
            message_ids_set = set(message_ids)
            
            # 读取所有消息
            messages = []
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            msg = json.loads(line)
                            if msg.get('message_id') not in message_ids_set:
                                messages.append(msg)
                        except:
                            pass
            
            # 重写文件
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                for msg in messages:
                    json.dump(msg, f, ensure_ascii=False)
                    f.write('\n')
            
            logger.info(f"批量移除了 {len(message_ids)} 条备份消息")
        except Exception as e:
            logger.error(f"批量移除备份消息失败: {str(e)}")
    
    def clear_backup(self):
        """清空备份（所有消息已发送）"""
        try:
            if self.backup_file.exists():
                self.backup_file.unlink()
                logger.info("✅ 备份已清空（所有消息已发送）")
        except Exception as e:
            logger.error(f"清空备份失败: {str(e)}")
    
    def get_backup_count(self) -> int:
        """获取备份消息数量"""
        if not self.backup_file.exists():
            return 0
        
        try:
            count = 0
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        count += 1
            return count
        except Exception as e:
            logger.error(f"获取备份数量失败: {str(e)}")
            return 0
    
    def get_oldest_message_time(self) -> int:
        """获取最旧消息的时间戳"""
        if not self.backup_file.exists():
            return 0
        
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line:
                    message = json.loads(first_line)
                    return message.get('timestamp', 0)
        except Exception as e:
            logger.error(f"获取最旧消息时间失败: {str(e)}")
        
        return 0


# 创建全局实例
message_backup = MessageBackup()
