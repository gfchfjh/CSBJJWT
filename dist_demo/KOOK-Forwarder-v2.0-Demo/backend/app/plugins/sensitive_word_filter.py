"""
敏感词过滤插件
✅ P1-3: 敏感词自动替换和过滤
"""
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
from .plugin_system import PluginBase, PluginInfo, PluginHook, plugin_manager
from ..utils.logger import logger


class SensitiveWordFilter(PluginBase):
    """敏感词过滤插件"""
    
    def __init__(self):
        super().__init__()
        
        # 敏感词库
        self.sensitive_words: Set[str] = set()
        self.sensitive_patterns: List[re.Pattern] = []
        
        # 替换策略
        self.replace_char = '*'
        self.replace_mode = 'mask'  # mask/remove/custom
        
        # 词库文件
        self.words_file = Path('data/sensitive_words.txt')
        
        # 统计
        self.stats = {
            'total_checked': 0,
            'words_found': 0,
            'messages_filtered': 0
        }
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            id='sensitive_word_filter',
            name='敏感词过滤',
            version='1.0.0',
            author='KOOK Forwarder Team',
            description='自动检测和替换消息中的敏感词'
        )
    
    async def on_load(self):
        """插件加载"""
        # 加载敏感词库
        await self.load_words()
        
        # 注册钩子
        plugin_manager.register_hook(
            PluginHook.AFTER_MESSAGE_PROCESS,
            self.filter_message
        )
        
        logger.info(f"敏感词过滤插件已加载，词库大小: {len(self.sensitive_words)}")
    
    async def load_words(self):
        """加载敏感词库"""
        try:
            if not self.words_file.exists():
                # 创建默认词库
                self.words_file.parent.mkdir(parents=True, exist_ok=True)
                self.words_file.write_text(
                    '# 敏感词列表（每行一个）\n'
                    '广告\n'
                    '代练\n'
                    '外挂\n',
                    encoding='utf-8'
                )
            
            # 读取词库
            with open(self.words_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 支持正则表达式（以 / 开头和结尾）
                    if line.startswith('/') and line.endswith('/'):
                        pattern = line[1:-1]
                        self.sensitive_patterns.append(re.compile(pattern))
                    else:
                        self.sensitive_words.add(line)
            
            logger.info(
                f"敏感词库加载完成: {len(self.sensitive_words)}个词，"
                f"{len(self.sensitive_patterns)}个正则"
            )
            
        except Exception as e:
            logger.error(f"加载敏感词库失败: {str(e)}")
    
    async def filter_message(self, message: Dict) -> Dict:
        """
        过滤消息中的敏感词
        
        Args:
            message: 消息对象
            
        Returns:
            过滤后的消息对象
        """
        content = message.get('content', '')
        
        if not content:
            return message
        
        self.stats['total_checked'] += 1
        
        # 检查和替换敏感词
        filtered_content, found_words = self._filter_text(content)
        
        if found_words:
            message['content'] = filtered_content
            message['filtered_words'] = found_words
            
            self.stats['words_found'] += len(found_words)
            self.stats['messages_filtered'] += 1
            
            logger.info(f"消息已过滤，发现{len(found_words)}个敏感词: {found_words}")
        
        return message
    
    def _filter_text(self, text: str) -> Tuple[str, List[str]]:
        """
        过滤文本中的敏感词
        
        Args:
            text: 原文本
            
        Returns:
            (过滤后的文本, 发现的敏感词列表)
        """
        filtered_text = text
        found_words = []
        
        # 1. 检查敏感词
        for word in self.sensitive_words:
            if word in filtered_text:
                found_words.append(word)
                
                # 替换敏感词
                if self.replace_mode == 'mask':
                    # 用*替换
                    replacement = self.replace_char * len(word)
                elif self.replace_mode == 'remove':
                    # 直接删除
                    replacement = ''
                else:
                    # 自定义替换
                    replacement = '[已过滤]'
                
                filtered_text = filtered_text.replace(word, replacement)
        
        # 2. 检查正则表达式
        for pattern in self.sensitive_patterns:
            matches = pattern.findall(filtered_text)
            
            if matches:
                found_words.extend(matches)
                
                # 替换匹配项
                if self.replace_mode == 'mask':
                    filtered_text = pattern.sub(
                        lambda m: self.replace_char * len(m.group()),
                        filtered_text
                    )
                elif self.replace_mode == 'remove':
                    filtered_text = pattern.sub('', filtered_text)
                else:
                    filtered_text = pattern.sub('[已过滤]', filtered_text)
        
        return filtered_text, found_words
    
    async def add_word(self, word: str):
        """添加敏感词"""
        self.sensitive_words.add(word)
        
        # 追加到文件
        try:
            with open(self.words_file, 'a', encoding='utf-8') as f:
                f.write(f'\n{word}')
            
            logger.info(f"敏感词已添加: {word}")
            
        except Exception as e:
            logger.error(f"添加敏感词失败: {str(e)}")
    
    async def remove_word(self, word: str):
        """移除敏感词"""
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            
            # 重写文件
            try:
                words = list(self.sensitive_words)
                with open(self.words_file, 'w', encoding='utf-8') as f:
                    f.write('# 敏感词列表（每行一个）\n')
                    for w in words:
                        f.write(f'{w}\n')
                
                logger.info(f"敏感词已移除: {word}")
                
            except Exception as e:
                logger.error(f"移除敏感词失败: {str(e)}")
    
    def get_word_count(self) -> int:
        """获取词库大小"""
        return len(self.sensitive_words) + len(self.sensitive_patterns)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'word_count': self.get_word_count()
        }


# 自动注册插件
sensitive_word_filter = SensitiveWordFilter()
