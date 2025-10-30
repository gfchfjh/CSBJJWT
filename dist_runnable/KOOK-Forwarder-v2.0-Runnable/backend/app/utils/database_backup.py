"""
数据库备份还原工具
✅ P0-25: 自动备份和一键还原
"""
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from ..utils.logger import logger
from ..config import settings


class DatabaseBackup:
    """数据库备份工具"""
    
    def __init__(self):
        self.db_path = settings.database_path
        self.backup_dir = Path('data/backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.max_backups = getattr(settings, 'max_backups', 30)
        self.auto_backup_enabled = getattr(settings, 'auto_backup_enabled', True)
        self.auto_backup_interval = getattr(settings, 'auto_backup_interval_hours', 24)
    
    async def create_backup(self, name: Optional[str] = None) -> Path:
        """
        创建数据库备份
        
        Args:
            name: 备份名称（可选）
            
        Returns:
            备份文件路径
        """
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = name or f'db_backup_{timestamp}'
            backup_file = self.backup_dir / f'{backup_name}.db'
            
            # 使用SQLite在线备份
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_file)
            
            # 执行备份
            with backup_conn:
                source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # 压缩备份（可选）
            compressed_file = await self._compress_backup(backup_file)
            
            logger.info(f"数据库备份成功: {compressed_file or backup_file}")
            
            # 清理旧备份
            await self._cleanup_old_backups()
            
            return compressed_file or backup_file
            
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            raise
    
    async def restore_backup(self, backup_file: Path) -> bool:
        """
        还原数据库备份
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            是否成功还原
        """
        try:
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_file}")
            
            # 解压备份（如果是压缩的）
            if backup_file.suffix == '.gz':
                backup_file = await self._decompress_backup(backup_file)
            
            # 创建当前数据库的备份
            current_backup = await self.create_backup('before_restore')
            logger.info(f"当前数据库已备份至: {current_backup}")
            
            # 关闭所有数据库连接
            # 这里需要通知应用层关闭连接
            
            # 替换数据库文件
            shutil.copy2(backup_file, self.db_path)
            
            logger.info(f"数据库还原成功: {backup_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"还原备份失败: {str(e)}")
            return False
    
    async def _compress_backup(self, backup_file: Path) -> Optional[Path]:
        """压缩备份文件"""
        try:
            import gzip
            
            compressed_file = backup_file.with_suffix('.db.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            backup_file.unlink()
            
            logger.info(f"备份已压缩: {compressed_file}")
            
            return compressed_file
            
        except Exception as e:
            logger.error(f"压缩备份失败: {str(e)}")
            return None
    
    async def _decompress_backup(self, compressed_file: Path) -> Path:
        """解压备份文件"""
        try:
            import gzip
            
            decompressed_file = compressed_file.with_suffix('')
            
            with gzip.open(compressed_file, 'rb') as f_in:
                with open(decompressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"备份已解压: {decompressed_file}")
            
            return decompressed_file
            
        except Exception as e:
            logger.error(f"解压备份失败: {str(e)}")
            raise
    
    async def _cleanup_old_backups(self):
        """清理旧备份"""
        try:
            # 获取所有备份
            backups = list(self.backup_dir.glob('db_backup_*.db*'))
            
            # 按修改时间排序
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 删除超出数量的备份
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    backup.unlink()
                    logger.info(f"已删除旧备份: {backup.name}")
            
        except Exception as e:
            logger.error(f"清理旧备份失败: {str(e)}")
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        
        for backup_file in self.backup_dir.glob('db_backup_*.db*'):
            try:
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.stem,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'size_mb': stat.st_size / 1024 / 1024,
                    'created_at': stat.st_mtime,
                    'compressed': backup_file.suffix == '.gz'
                })
            except Exception as e:
                logger.error(f"读取备份文件失败 {backup_file}: {str(e)}")
        
        # 按时间倒序
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    async def verify_backup(self, backup_file: Path) -> Tuple[bool, Optional[str]]:
        """
        验证备份文件完整性
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            if not backup_file.exists():
                return False, "文件不存在"
            
            # 解压（如果需要）
            if backup_file.suffix == '.gz':
                backup_file = await self._decompress_backup(backup_file)
            
            # 尝试打开数据库
            conn = sqlite3.connect(backup_file)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            required_tables = ['accounts', 'bot_configs', 'channel_mappings']
            existing_tables = [t[0] for t in tables]
            
            for table in required_tables:
                if table not in existing_tables:
                    conn.close()
                    return False, f"缺少必需的表: {table}"
            
            conn.close()
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_backup_stats(self) -> Dict:
        """获取备份统计信息"""
        backups = self.list_backups()
        
        total_size = sum(b['size'] for b in backups)
        
        return {
            'total_backups': len(backups),
            'total_size_mb': total_size / 1024 / 1024,
            'oldest_backup': backups[-1]['created_at'] if backups else None,
            'newest_backup': backups[0]['created_at'] if backups else None
        }


# 全局实例
database_backup = DatabaseBackup()
