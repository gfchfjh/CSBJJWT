"""
增强的密码复杂度验证器
v17.0.0深度优化：要求8位+大小写+数字+特殊字符
"""
import re
from typing import Tuple, List
from pydantic import BaseModel


class PasswordStrength(BaseModel):
    """密码强度评估"""
    is_valid: bool
    score: int  # 0-100
    level: str  # weak/medium/strong/very_strong
    issues: List[str]
    suggestions: List[str]


class PasswordValidatorEnhanced:
    """增强的密码验证器"""
    
    # 最小长度要求
    MIN_LENGTH = 8
    RECOMMENDED_LENGTH = 12
    
    # 密码复杂度要求
    REQUIRE_LOWERCASE = True
    REQUIRE_UPPERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    
    # 特殊字符列表
    SPECIAL_CHARS = r'!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~'
    
    # 常见弱密码（禁止使用）
    COMMON_WEAK_PASSWORDS = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        '111111', '123456789', 'letmein', 'welcome', 'monkey',
        'admin', 'root', 'user', 'test', 'guest', '1234', '123123',
        'sunshine', 'iloveyou', 'princess', 'dragon', 'master'
    ]
    
    @classmethod
    def validate(cls, password: str, username: str = None) -> PasswordStrength:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            username: 用户名（可选，用于检测密码是否包含用户名）
            
        Returns:
            PasswordStrength对象，包含验证结果和建议
        """
        issues = []
        suggestions = []
        score = 0
        
        # 1. 检查长度
        if len(password) < cls.MIN_LENGTH:
            issues.append(f"密码长度不足{cls.MIN_LENGTH}位")
            suggestions.append(f"请使用至少{cls.MIN_LENGTH}个字符")
        else:
            score += 20
            
        if len(password) >= cls.RECOMMENDED_LENGTH:
            score += 10
        
        # 2. 检查小写字母
        if not re.search(r'[a-z]', password):
            issues.append("缺少小写字母")
            suggestions.append("请至少包含一个小写字母（a-z）")
        else:
            score += 15
        
        # 3. 检查大写字母
        if not re.search(r'[A-Z]', password):
            issues.append("缺少大写字母")
            suggestions.append("请至少包含一个大写字母（A-Z）")
        else:
            score += 15
        
        # 4. 检查数字
        if not re.search(r'\d', password):
            issues.append("缺少数字")
            suggestions.append("请至少包含一个数字（0-9）")
        else:
            score += 15
        
        # 5. 检查特殊字符
        special_pattern = f'[{re.escape(cls.SPECIAL_CHARS)}]'
        if not re.search(special_pattern, password):
            issues.append("缺少特殊字符")
            suggestions.append(f"请至少包含一个特殊字符（如 !@#$%^&*）")
        else:
            score += 15
        
        # 6. 检查是否为常见弱密码
        if password.lower() in cls.COMMON_WEAK_PASSWORDS:
            issues.append("密码过于简单，容易被猜测")
            suggestions.append("请避免使用常见弱密码")
            score = max(0, score - 30)
        
        # 7. 检查是否包含用户名
        if username and username.lower() in password.lower():
            issues.append("密码包含用户名")
            suggestions.append("请不要在密码中包含用户名")
            score = max(0, score - 20)
        
        # 8. 检查连续字符（如 abc, 123）
        if cls._has_sequential_chars(password):
            issues.append("包含连续字符序列")
            suggestions.append("避免使用连续字符（如abc、123）")
            score = max(0, score - 10)
        
        # 9. 检查重复字符（如 aaa, 111）
        if cls._has_repeating_chars(password):
            issues.append("包含重复字符")
            suggestions.append("避免使用重复字符（如aaa、111）")
            score = max(0, score - 10)
        
        # 10. 字符多样性加分
        unique_chars = len(set(password))
        if unique_chars >= len(password) * 0.75:  # 75%以上字符不重复
            score += 10
        
        # 确定强度等级
        if score >= 80:
            level = "very_strong"
        elif score >= 60:
            level = "strong"
        elif score >= 40:
            level = "medium"
        else:
            level = "weak"
        
        # 是否通过验证（必须满足所有基本要求）
        is_valid = (
            len(password) >= cls.MIN_LENGTH and
            re.search(r'[a-z]', password) and
            re.search(r'[A-Z]', password) and
            re.search(r'\d', password) and
            re.search(special_pattern, password) and
            password.lower() not in cls.COMMON_WEAK_PASSWORDS
        )
        
        return PasswordStrength(
            is_valid=is_valid,
            score=min(100, score),
            level=level,
            issues=issues,
            suggestions=suggestions
        )
    
    @staticmethod
    def _has_sequential_chars(password: str, min_length: int = 3) -> bool:
        """
        检测是否包含连续字符序列
        
        Args:
            password: 密码
            min_length: 最小连续长度
            
        Returns:
            是否包含连续字符
        """
        password_lower = password.lower()
        
        # 检查连续字母（abc, xyz）
        for i in range(len(password_lower) - min_length + 1):
            is_sequential = True
            for j in range(min_length - 1):
                if ord(password_lower[i + j + 1]) != ord(password_lower[i + j]) + 1:
                    is_sequential = False
                    break
            if is_sequential:
                return True
        
        # 检查连续数字（123, 789）
        for i in range(len(password) - min_length + 1):
            if password[i:i+min_length].isdigit():
                is_sequential = True
                for j in range(min_length - 1):
                    if int(password[i + j + 1]) != int(password[i + j]) + 1:
                        is_sequential = False
                        break
                if is_sequential:
                    return True
        
        return False
    
    @staticmethod
    def _has_repeating_chars(password: str, min_length: int = 3) -> bool:
        """
        检测是否包含重复字符
        
        Args:
            password: 密码
            min_length: 最小重复长度
            
        Returns:
            是否包含重复字符
        """
        for i in range(len(password) - min_length + 1):
            if len(set(password[i:i+min_length])) == 1:
                return True
        return False
    
    @classmethod
    def generate_suggestion(cls) -> str:
        """
        生成密码建议文本
        
        Returns:
            密码要求说明
        """
        return f"""密码要求：
• 长度：至少{cls.MIN_LENGTH}位字符（建议{cls.RECOMMENDED_LENGTH}位以上）
• 大写字母：至少包含一个大写字母（A-Z）
• 小写字母：至少包含一个小写字母（a-z）
• 数字：至少包含一个数字（0-9）
• 特殊字符：至少包含一个特殊字符（!@#$%^&*等）
• 避免：常见弱密码、用户名、连续字符、重复字符

示例强密码：MyP@ssw0rd2025!、Secure#123Pwd"""
    
    @classmethod
    def quick_validate(cls, password: str) -> Tuple[bool, str]:
        """
        快速验证（只返回是否通过和错误消息）
        
        Args:
            password: 待验证的密码
            
        Returns:
            (是否通过, 错误消息)
        """
        result = cls.validate(password)
        
        if result.is_valid:
            return True, "密码强度符合要求"
        else:
            # 返回第一个问题
            if result.issues:
                return False, result.issues[0]
            else:
                return False, "密码不符合复杂度要求"


# 创建全局实例
password_validator_enhanced = PasswordValidatorEnhanced()


# 导出快捷函数
def validate_password(password: str, username: str = None) -> PasswordStrength:
    """验证密码强度（快捷函数）"""
    return password_validator_enhanced.validate(password, username)


def quick_validate_password(password: str) -> Tuple[bool, str]:
    """快速验证密码（快捷函数）"""
    return password_validator_enhanced.quick_validate(password)
