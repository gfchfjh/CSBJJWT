"""
密码强度验证API
v17.0.0深度优化：实时密码强度检测
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..utils.password_validator_enhanced import validate_password, password_validator_enhanced
from ..utils.logger import logger

router = APIRouter(prefix="/api/password-strength", tags=["密码强度"])


class PasswordCheckRequest(BaseModel):
    """密码检测请求"""
    password: str
    username: Optional[str] = None


@router.post("/check")
async def check_password_strength(request: PasswordCheckRequest):
    """
    检测密码强度
    
    Args:
        request: 包含密码和可选用户名的请求
        
    Returns:
        密码强度评估结果
    """
    try:
        # 验证密码强度
        result = validate_password(request.password, request.username)
        
        logger.info(
            f"密码强度检测: valid={result.is_valid}, "
            f"level={result.level}, score={result.score}"
        )
        
        return {
            "success": True,
            "is_valid": result.is_valid,
            "score": result.score,
            "level": result.level,
            "level_text": get_level_text(result.level),
            "issues": result.issues,
            "suggestions": result.suggestions
        }
        
    except Exception as e:
        logger.error(f"检测密码强度失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/requirements")
async def get_password_requirements():
    """
    获取密码要求说明
    
    Returns:
        密码要求文本和规则
    """
    return {
        "success": True,
        "requirements": {
            "min_length": password_validator_enhanced.MIN_LENGTH,
            "recommended_length": password_validator_enhanced.RECOMMENDED_LENGTH,
            "require_lowercase": password_validator_enhanced.REQUIRE_LOWERCASE,
            "require_uppercase": password_validator_enhanced.REQUIRE_UPPERCASE,
            "require_digits": password_validator_enhanced.REQUIRE_DIGITS,
            "require_special": password_validator_enhanced.REQUIRE_SPECIAL,
            "special_chars": password_validator_enhanced.SPECIAL_CHARS,
        },
        "description": password_validator_enhanced.generate_suggestion(),
        "example_passwords": [
            "MyP@ssw0rd2025!",
            "Secure#123Pwd",
            "Complex&Pass99",
            "Strong!2024Key"
        ]
    }


def get_level_text(level: str) -> str:
    """获取密码强度等级文本"""
    level_map = {
        "weak": "弱",
        "medium": "中等",
        "strong": "强",
        "very_strong": "非常强"
    }
    return level_map.get(level, "未知")
