"""
自定义消息模板系统
✅ P1-4: 灵活的消息格式化
"""
import re
from typing import Dict, Optional, List
from pathlib import Path
import yaml
from ..utils.logger import logger


class MessageTemplate:
    """消息模板"""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self.template_dir = Path('data/templates')
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认模板
        self.default_templates = {
            'default': '{content}',
            'with_author': '**{author}**: {content}',
            'with_time': '[{time}] {content}',
            'full': '[{time}] **{author}** 在 #{channel_name}:\n{content}',
            'quote': '> {content}',
            'card': '📋 **{title}**\n{content}\n---\n来自: {author}',
            'mention': '@{target_user} {content}'
        }
        
        # 加载自定义模板
        self.load_templates()
    
    def load_templates(self):
        """加载模板"""
        try:
            template_file = self.template_dir / 'message_templates.yaml'
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    custom_templates = yaml.safe_load(f) or {}
                
                # 合并自定义模板
                self.templates = {**self.default_templates, **custom_templates}
                
                logger.info(f"消息模板加载完成，共{len(self.templates)}个模板")
            else:
                # 使用默认模板
                self.templates = self.default_templates.copy()
                
                # 保存默认模板
                self.save_templates()
                
        except Exception as e:
            logger.error(f"加载消息模板失败: {str(e)}")
            self.templates = self.default_templates.copy()
    
    def save_templates(self):
        """保存模板"""
        try:
            template_file = self.template_dir / 'message_templates.yaml'
            
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.templates,
                    f,
                    allow_unicode=True,
                    default_flow_style=False
                )
            
            logger.info("消息模板已保存")
            
        except Exception as e:
            logger.error(f"保存消息模板失败: {str(e)}")
    
    def render(
        self,
        template_name: str,
        context: Dict,
        fallback_template: Optional[str] = None
    ) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板名称
            context: 上下文变量
            fallback_template: 后备模板
            
        Returns:
            渲染后的文本
        """
        # 获取模板
        template = self.templates.get(template_name)
        
        if not template:
            if fallback_template:
                template = fallback_template
            else:
                template = self.default_templates['default']
                logger.warning(f"模板不存在，使用默认模板: {template_name}")
        
        try:
            # 渲染模板
            rendered = self._render_template(template, context)
            
            return rendered
            
        except Exception as e:
            logger.error(f"模板渲染失败: {str(e)}")
            return context.get('content', '')
    
    def _render_template(self, template: str, context: Dict) -> str:
        """
        渲染模板（支持变量和条件语句）
        
        语法:
        - {variable}: 变量
        - {variable|default}: 带默认值的变量
        - {{if variable}}...{{endif}}: 条件语句
        - {{for item in list}}...{{endfor}}: 循环语句
        """
        rendered = template
        
        # 1. 处理条件语句
        rendered = self._process_conditions(rendered, context)
        
        # 2. 处理循环语句
        rendered = self._process_loops(rendered, context)
        
        # 3. 替换变量
        rendered = self._replace_variables(rendered, context)
        
        return rendered
    
    def _process_conditions(self, template: str, context: Dict) -> str:
        """处理条件语句"""
        # 匹配 {{if variable}}...{{endif}}
        pattern = r'\{\{if\s+(\w+)\}\}(.*?)\{\{endif\}\}'
        
        def replace_condition(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # 检查变量是否存在且为真
            if context.get(var_name):
                return content
            else:
                return ''
        
        return re.sub(pattern, replace_condition, template, flags=re.DOTALL)
    
    def _process_loops(self, template: str, context: Dict) -> str:
        """处理循环语句"""
        # 匹配 {{for item in list}}...{{endfor}}
        pattern = r'\{\{for\s+(\w+)\s+in\s+(\w+)\}\}(.*?)\{\{endfor\}\}'
        
        def replace_loop(match):
            item_name = match.group(1)
            list_name = match.group(2)
            content = match.group(3)
            
            # 获取列表
            items = context.get(list_name, [])
            
            if not isinstance(items, list):
                return ''
            
            # 循环渲染
            results = []
            for item in items:
                # 创建临时上下文
                temp_context = {**context, item_name: item}
                
                # 渲染内容
                rendered = self._replace_variables(content, temp_context)
                results.append(rendered)
            
            return ''.join(results)
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _replace_variables(self, template: str, context: Dict) -> str:
        """替换变量"""
        # 匹配 {variable} 或 {variable|default}
        pattern = r'\{(\w+)(?:\|([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) or ''
            
            # 获取变量值
            value = context.get(var_name, default_value)
            
            return str(value)
        
        return re.sub(pattern, replace_var, template)
    
    def add_template(self, name: str, template: str):
        """添加模板"""
        self.templates[name] = template
        self.save_templates()
        
        logger.info(f"模板已添加: {name}")
    
    def remove_template(self, name: str):
        """移除模板"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
            
            logger.info(f"模板已移除: {name}")
    
    def get_template(self, name: str) -> Optional[str]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())


# 全局实例
message_template = MessageTemplate()


# 便捷函数
def render_message(template_name: str, context: Dict) -> str:
    """渲染消息"""
    return message_template.render(template_name, context)
