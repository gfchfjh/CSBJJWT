"""
错误解决方案系统
提供详细的错误诊断和自动修复建议
"""
from typing import Optional, Dict
import re


# 错误模式和解决方案映射
ERROR_SOLUTIONS = {
    # Redis相关错误
    r"Redis.*connection.*refused": {
        "category": "redis",
        "severity": "critical",
        "title": "Redis连接被拒绝",
        "cause": "Redis服务未启动或端口配置错误",
        "solutions": [
            "1. 检查Redis服务是否正在运行",
            "2. 使用命令启动Redis: redis-server",
            "3. 或使用Docker: docker-compose up -d redis",
            "4. 检查配置文件中的Redis端口是否正确（默认6379）",
            "5. 检查防火墙是否阻止了Redis端口"
        ],
        "auto_fix": "restart_redis"
    },
    
    r"Redis.*timeout": {
        "category": "redis",
        "severity": "warning",
        "title": "Redis连接超时",
        "cause": "Redis响应过慢或网络延迟",
        "solutions": [
            "1. 检查Redis服务器负载",
            "2. 增加连接超时时间配置",
            "3. 检查网络连接质量",
            "4. 考虑清理Redis中的过期数据"
        ]
    },
    
    # KOOK相关错误
    r"Cookie.*expired|Cookie.*invalid": {
        "category": "kook",
        "severity": "critical",
        "title": "KOOK Cookie已过期",
        "cause": "登录凭证失效",
        "solutions": [
            "1. 重新登录KOOK账号",
            "2. 在账号管理页面点击'重新登录'",
            "3. 或者重新导入最新的Cookie",
            "4. 确保账号未在其他地方登出"
        ],
        "auto_fix": "prompt_relogin"
    },
    
    r"KOOK.*websocket.*closed": {
        "category": "kook",
        "severity": "warning",
        "title": "KOOK WebSocket连接断开",
        "cause": "网络波动或KOOK服务器断开连接",
        "solutions": [
            "1. 程序将自动重连（最多5次）",
            "2. 检查网络连接是否稳定",
            "3. 如果反复断开，尝试重启服务",
            "4. 检查是否被KOOK限流"
        ],
        "auto_fix": "auto_reconnect"
    },
    
    r"IP.*banned|Account.*banned": {
        "category": "kook",
        "severity": "critical",
        "title": "账号或IP被封禁",
        "cause": "触发KOOK反爬虫机制或违反服务条款",
        "solutions": [
            "1. 等待一段时间后再试（通常24小时）",
            "2. 更换网络IP（使用VPN或更换网络）",
            "3. 降低消息抓取频率",
            "4. 联系KOOK客服申诉"
        ]
    },
    
    # Discord相关错误
    r"Discord.*webhook.*invalid|Discord.*404": {
        "category": "discord",
        "severity": "error",
        "title": "Discord Webhook无效",
        "cause": "Webhook URL错误或已被删除",
        "solutions": [
            "1. 在机器人配置页检查Webhook URL是否正确",
            "2. 在Discord服务器重新创建Webhook",
            "3. 确保Webhook URL以https://discord.com/api/webhooks/开头",
            "4. 测试连接确认Webhook可用"
        ],
        "auto_fix": "prompt_webhook_fix"
    },
    
    r"Discord.*rate.*limit": {
        "category": "discord",
        "severity": "warning",
        "title": "Discord API限流",
        "cause": "发送消息过于频繁",
        "solutions": [
            "1. 程序会自动排队等待",
            "2. 降低转发的频道映射数量",
            "3. 增加限流配置中的等待时间",
            "4. 等待限流解除（通常几秒到几分钟）"
        ],
        "auto_fix": "auto_rate_limit"
    },
    
    # Telegram相关错误
    r"Telegram.*bot.*token.*invalid": {
        "category": "telegram",
        "severity": "error",
        "title": "Telegram Bot Token无效",
        "cause": "Bot Token错误或已被撤销",
        "solutions": [
            "1. 与@BotFather对话检查Bot状态",
            "2. 重新生成Bot Token",
            "3. 在机器人配置页更新Token",
            "4. 确保Token格式正确（数字:字母数字组合）"
        ],
        "auto_fix": "prompt_token_fix"
    },
    
    r"Telegram.*chat.*not.*found": {
        "category": "telegram",
        "severity": "error",
        "title": "Telegram群组不存在",
        "cause": "Chat ID错误或Bot未加入群组",
        "solutions": [
            "1. 确认Bot已加入目标群组",
            "2. 使用'自动获取Chat ID'功能重新获取",
            "3. 检查Chat ID格式（应为负数）",
            "4. 确保Bot在群组中有发送消息权限"
        ]
    },
    
    # 飞书相关错误
    r"飞书.*access.*token.*invalid": {
        "category": "feishu",
        "severity": "error",
        "title": "飞书访问令牌无效",
        "cause": "App ID或App Secret错误",
        "solutions": [
            "1. 在飞书开放平台检查应用凭证",
            "2. 重新复制App ID和App Secret",
            "3. 确保应用已发布且未被禁用",
            "4. 检查应用权限是否正确配置"
        ]
    },
    
    r"飞书.*图片上传失败": {
        "category": "feishu",
        "severity": "warning",
        "title": "飞书图片上传失败",
        "cause": "图片格式或大小不符合要求",
        "solutions": [
            "1. 程序会自动压缩图片重试",
            "2. 检查图片大小是否超过10MB",
            "3. 确保图片格式为JPG/PNG/GIF",
            "4. 切换图片策略为'智能模式'"
        ],
        "auto_fix": "auto_compress_image"
    },
    
    # 图片处理错误
    r"图片下载失败|Image.*download.*failed": {
        "category": "image",
        "severity": "warning",
        "title": "图片下载失败",
        "cause": "图片URL失效或网络问题",
        "solutions": [
            "1. 检查网络连接是否正常",
            "2. 图片可能已被KOOK删除",
            "3. 检查防盗链配置是否正确",
            "4. 程序会自动重试3次"
        ],
        "auto_fix": "auto_retry_download"
    },
    
    r"图片.*过大|Image.*too.*large": {
        "category": "image",
        "severity": "info",
        "title": "图片文件过大",
        "cause": "图片超过目标平台限制",
        "solutions": [
            "1. 程序会自动压缩图片",
            "2. 可在设置中调整压缩质量",
            "3. 考虑使用图床模式",
            "4. 检查原图大小是否超过50MB"
        ],
        "auto_fix": "auto_compress"
    },
    
    # 网络错误
    r"Connection.*timeout|连接超时": {
        "category": "network",
        "severity": "warning",
        "title": "网络连接超时",
        "cause": "网络不稳定或服务器响应慢",
        "solutions": [
            "1. 检查网络连接是否正常",
            "2. 程序会自动重试",
            "3. 考虑增加超时时间配置",
            "4. 检查代理设置（如果使用）"
        ],
        "auto_fix": "auto_retry"
    },
    
    # 验证码错误
    r"验证码.*识别失败|Captcha.*failed": {
        "category": "captcha",
        "severity": "warning",
        "title": "验证码识别失败",
        "cause": "自动识别失败",
        "solutions": [
            "1. 程序会切换到手动输入模式",
            "2. 配置2Captcha API Key实现自动识别",
            "3. 或在弹窗中手动输入验证码",
            "4. 本地OCR识别成功率约80%"
        ],
        "auto_fix": "prompt_manual_captcha"
    },
    
    # 数据库错误
    r"Database.*locked|数据库.*锁定": {
        "category": "database",
        "severity": "warning",
        "title": "数据库被锁定",
        "cause": "并发访问导致",
        "solutions": [
            "1. 程序会自动重试",
            "2. 通常会在几秒内自动解决",
            "3. 如果持续出现，重启服务",
            "4. 检查是否有多个程序实例运行"
        ],
        "auto_fix": "auto_retry"
    },
    
    # 权限错误
    r"Permission.*denied|权限被拒绝": {
        "category": "permission",
        "severity": "error",
        "title": "权限不足",
        "cause": "文件或目录权限不足",
        "solutions": [
            "1. 检查数据目录权限（~/Documents/KookForwarder）",
            "2. 以管理员权限运行程序",
            "3. 确保Redis数据目录可写",
            "4. 检查日志目录是否可写"
        ]
    },
    
    # 配置错误
    r"Config.*invalid|配置.*无效": {
        "category": "config",
        "severity": "error",
        "title": "配置错误",
        "cause": "配置文件格式错误或缺少必需配置",
        "solutions": [
            "1. 检查配置文件格式是否正确",
            "2. 参考文档补全必需配置",
            "3. 删除配置文件重新生成",
            "4. 查看日志了解具体错误"
        ]
    }
}


class ErrorSolutionProvider:
    """错误解决方案提供器"""
    
    def __init__(self):
        self.solutions = ERROR_SOLUTIONS
    
    def get_solution(self, error_message: str) -> Optional[Dict]:
        """
        根据错误信息获取解决方案
        
        Args:
            error_message: 错误信息
            
        Returns:
            解决方案字典，包含title, cause, solutions等字段
        """
        if not error_message:
            return None
        
        # 遍历所有错误模式
        for pattern, solution in self.solutions.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return solution
        
        # 没有匹配的解决方案，返回通用建议
        return {
            "category": "unknown",
            "severity": "error",
            "title": "未知错误",
            "cause": "系统遇到了未预期的错误",
            "solutions": [
                "1. 查看完整错误日志了解详情",
                "2. 尝试重启服务",
                "3. 检查系统资源（内存、磁盘空间）",
                "4. 在GitHub Issues中搜索类似问题",
                "5. 联系技术支持并提供错误日志"
            ]
        }
    
    def get_quick_solution(self, error_message: str) -> str:
        """
        获取快速解决方案文本
        
        Args:
            error_message: 错误信息
            
        Returns:
            解决方案文本
        """
        solution = self.get_solution(error_message)
        if not solution:
            return "请查看完整错误日志或联系技术支持"
        
        # 返回第一条建议作为快速解决方案
        solutions_list = solution.get("solutions", [])
        if solutions_list:
            return solutions_list[0]
        
        return solution.get("title", "未知错误")
    
    def get_auto_fix_action(self, error_message: str) -> Optional[str]:
        """
        获取自动修复动作
        
        Args:
            error_message: 错误信息
            
        Returns:
            自动修复动作名称，None表示无法自动修复
        """
        solution = self.get_solution(error_message)
        if not solution:
            return None
        
        return solution.get("auto_fix")
    
    def format_solution_html(self, error_message: str) -> str:
        """
        格式化解决方案为HTML（供前端显示）
        
        Args:
            error_message: 错误信息
            
        Returns:
            HTML格式的解决方案
        """
        solution = self.get_solution(error_message)
        if not solution:
            return ""
        
        severity_colors = {
            "critical": "#f56c6c",
            "error": "#e6a23c",
            "warning": "#e6a23c",
            "info": "#409eff"
        }
        
        color = severity_colors.get(solution.get("severity", "error"), "#909399")
        
        html = f"""
        <div class="error-solution" style="padding: 12px; background: #f4f4f5; border-left: 4px solid {color}; border-radius: 4px;">
            <h4 style="margin: 0 0 8px 0; color: {color};">
                {solution.get('title', '错误')}
            </h4>
            <p style="margin: 0 0 8px 0; color: #606266;">
                <strong>原因：</strong>{solution.get('cause', '未知')}
            </p>
            <p style="margin: 0 0 4px 0; color: #606266;">
                <strong>💡 解决方案：</strong>
            </p>
            <ul style="margin: 0; padding-left: 20px; color: #606266;">
        """
        
        for sol in solution.get("solutions", []):
            html += f"<li>{sol}</li>"
        
        html += """
            </ul>
        </div>
        """
        
        return html


# 创建全局实例
error_solution_provider = ErrorSolutionProvider()
