"""
配置管理器
✅ P0-23: 配置导入导出
✅ P0-24: 配置验证和迁移
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from ..utils.logger import logger
from ..database import get_database


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path('data/config')
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = self.config_dir / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def export_config(self, include_sensitive: bool = False) -> Dict:
        """
        导出配置
        
        Args:
            include_sensitive: 是否包含敏感信息（密码、Token等）
            
        Returns:
            配置字典
        """
        db = get_database()
        
        try:
            config = {
                'version': '1.0',
                'export_time': datetime.now().isoformat(),
                'accounts': [],
                'bots': [],
                'mappings': [],
                'filter_rules': [],
                'system_config': {}
            }
            
            # 导出账号
            accounts = db.execute("SELECT * FROM accounts").fetchall()
            for account in accounts:
                account_data = dict(account)
                
                if not include_sensitive:
                    # 移除敏感信息
                    account_data.pop('password_encrypted', None)
                    account_data.pop('cookie', None)
                
                config['accounts'].append(account_data)
            
            # 导出Bot
            bots = db.execute("SELECT * FROM bot_configs").fetchall()
            for bot in bots:
                bot_data = dict(bot)
                
                if not include_sensitive:
                    # 移除敏感信息
                    bot_config = json.loads(bot_data.get('config', '{}'))
                    if 'webhook_url' in bot_config:
                        bot_config['webhook_url'] = '***HIDDEN***'
                    if 'bot_token' in bot_config:
                        bot_config['bot_token'] = '***HIDDEN***'
                    bot_data['config'] = json.dumps(bot_config)
                
                config['bots'].append(bot_data)
            
            # 导出映射
            mappings = db.execute("SELECT * FROM channel_mappings").fetchall()
            config['mappings'] = [dict(m) for m in mappings]
            
            # 导出过滤规则
            rules = db.execute("SELECT * FROM filter_rules").fetchall()
            config['filter_rules'] = [dict(r) for r in rules]
            
            # 导出系统配置
            sys_config = db.execute("SELECT * FROM system_config").fetchall()
            for row in sys_config:
                config['system_config'][row['key']] = row['value']
            
            logger.info(f"配置导出成功，包含{len(config['accounts'])}个账号，{len(config['bots'])}个Bot")
            
            return config
            
        except Exception as e:
            logger.error(f"导出配置失败: {str(e)}")
            raise
    
    async def import_config(
        self,
        config: Dict,
        merge: bool = False,
        skip_existing: bool = True
    ) -> Dict:
        """
        导入配置
        
        Args:
            config: 配置字典
            merge: 是否合并（True）还是替换（False）
            skip_existing: 是否跳过已存在的项
            
        Returns:
            导入结果统计
        """
        db = get_database()
        
        result = {
            'accounts': {'imported': 0, 'skipped': 0, 'failed': 0},
            'bots': {'imported': 0, 'skipped': 0, 'failed': 0},
            'mappings': {'imported': 0, 'skipped': 0, 'failed': 0},
            'filter_rules': {'imported': 0, 'skipped': 0, 'failed': 0}
        }
        
        try:
            # 验证配置版本
            if not self._validate_config(config):
                raise ValueError("配置格式无效")
            
            # 如果不是合并模式，先清空现有配置
            if not merge:
                await self._clear_config(db)
            
            # 导入账号
            for account in config.get('accounts', []):
                try:
                    if skip_existing:
                        existing = db.execute(
                            "SELECT id FROM accounts WHERE email = ?",
                            (account['email'],)
                        ).fetchone()
                        
                        if existing:
                            result['accounts']['skipped'] += 1
                            continue
                    
                    db.execute("""
                        INSERT INTO accounts (email, password_encrypted, cookie, status)
                        VALUES (?, ?, ?, ?)
                    """, (
                        account['email'],
                        account.get('password_encrypted'),
                        account.get('cookie'),
                        account.get('status', 'offline')
                    ))
                    
                    result['accounts']['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"导入账号失败: {str(e)}")
                    result['accounts']['failed'] += 1
            
            # 导入Bot
            for bot in config.get('bots', []):
                try:
                    if skip_existing:
                        existing = db.execute(
                            "SELECT id FROM bot_configs WHERE platform = ? AND name = ?",
                            (bot['platform'], bot['name'])
                        ).fetchone()
                        
                        if existing:
                            result['bots']['skipped'] += 1
                            continue
                    
                    db.execute("""
                        INSERT INTO bot_configs (platform, name, config, status)
                        VALUES (?, ?, ?, ?)
                    """, (
                        bot['platform'],
                        bot['name'],
                        bot['config'],
                        bot.get('status', 'active')
                    ))
                    
                    result['bots']['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"导入Bot失败: {str(e)}")
                    result['bots']['failed'] += 1
            
            # 导入映射
            for mapping in config.get('mappings', []):
                try:
                    db.execute("""
                        INSERT INTO channel_mappings 
                        (kook_server_id, kook_channel_id, kook_channel_name,
                         target_platform, target_bot_id, target_channel_id, enabled)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        mapping['kook_server_id'],
                        mapping['kook_channel_id'],
                        mapping['kook_channel_name'],
                        mapping['target_platform'],
                        mapping['target_bot_id'],
                        mapping['target_channel_id'],
                        mapping.get('enabled', 1)
                    ))
                    
                    result['mappings']['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"导入映射失败: {str(e)}")
                    result['mappings']['failed'] += 1
            
            # 导入过滤规则
            for rule in config.get('filter_rules', []):
                try:
                    db.execute("""
                        INSERT INTO filter_rules (rule_type, rule_value, scope, enabled)
                        VALUES (?, ?, ?, ?)
                    """, (
                        rule['rule_type'],
                        rule['rule_value'],
                        rule.get('scope', 'global'),
                        rule.get('enabled', 1)
                    ))
                    
                    result['filter_rules']['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"导入过滤规则失败: {str(e)}")
                    result['filter_rules']['failed'] += 1
            
            db.commit()
            
            logger.info(f"配置导入完成: {json.dumps(result)}")
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"导入配置失败: {str(e)}")
            raise
    
    def _validate_config(self, config: Dict) -> bool:
        """验证配置格式"""
        required_keys = ['version', 'accounts', 'bots', 'mappings']
        
        for key in required_keys:
            if key not in config:
                logger.error(f"配置缺少必需字段: {key}")
                return False
        
        return True
    
    async def _clear_config(self, db):
        """清空现有配置"""
        try:
            db.execute("DELETE FROM channel_mappings")
            db.execute("DELETE FROM filter_rules")
            # 不删除accounts和bot_configs，避免丢失重要数据
            
            logger.info("现有配置已清空")
            
        except Exception as e:
            logger.error(f"清空配置失败: {str(e)}")
            raise
    
    async def backup_config(self, name: Optional[str] = None) -> Path:
        """
        备份配置
        
        Args:
            name: 备份名称（可选）
            
        Returns:
            备份文件路径
        """
        try:
            # 导出完整配置（包含敏感信息）
            config = await self.export_config(include_sensitive=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = name or f'backup_{timestamp}'
            backup_file = self.backup_dir / f'{backup_name}.json'
            
            # 保存
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置备份成功: {backup_file}")
            
            return backup_file
            
        except Exception as e:
            logger.error(f"备份配置失败: {str(e)}")
            raise
    
    async def restore_config(self, backup_file: Path) -> Dict:
        """
        恢复配置
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            恢复结果
        """
        try:
            # 读取备份
            with open(backup_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 导入配置
            result = await self.import_config(config, merge=False, skip_existing=False)
            
            logger.info(f"配置恢复成功: {backup_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"恢复配置失败: {str(e)}")
            raise
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.json'):
            try:
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.stem,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created_at': stat.st_mtime
                })
            except Exception as e:
                logger.error(f"读取备份文件失败 {backup_file}: {str(e)}")
        
        # 按时间倒序排序
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    async def delete_backup(self, backup_name: str) -> bool:
        """删除备份"""
        try:
            backup_file = self.backup_dir / f'{backup_name}.json'
            
            if not backup_file.exists():
                logger.warning(f"备份文件不存在: {backup_name}")
                return False
            
            backup_file.unlink()
            logger.info(f"备份已删除: {backup_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"删除备份失败: {str(e)}")
            return False
    
    async def export_to_yaml(self, output_path: Path, include_sensitive: bool = False) -> Path:
        """导出为YAML格式"""
        try:
            config = await self.export_config(include_sensitive)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"配置已导出为YAML: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"导出YAML失败: {str(e)}")
            raise
    
    async def import_from_yaml(self, yaml_path: Path, merge: bool = False) -> Dict:
        """从YAML导入配置"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            result = await self.import_config(config, merge)
            
            logger.info(f"从YAML导入成功: {yaml_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"导入YAML失败: {str(e)}")
            raise


# 全局实例
config_manager = ConfigManager()
