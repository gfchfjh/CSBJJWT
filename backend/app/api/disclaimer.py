"""
免责声明API
记录用户是否已同意免责声明
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..database import db
from ..utils.logger import logger

router = APIRouter(prefix="/api/disclaimer", tags=["免责声明"])


class DisclaimerAcceptance(BaseModel):
    """免责声明同意记录"""
    accepted_at: str
    version: str


class DisclaimerStatus(BaseModel):
    """免责声明状态"""
    has_accepted: bool
    accepted_at: Optional[str] = None
    version: Optional[str] = None
    needs_accept: bool


@router.get("/status", response_model=DisclaimerStatus)
async def get_disclaimer_status():
    """
    获取免责声明状态
    
    Returns:
        免责声明状态（是否已同意）
    """
    try:
        # 从系统配置中读取
        accepted = db.get_config("disclaimer_accepted")
        accepted_at = db.get_config("disclaimer_accepted_at")
        version = db.get_config("disclaimer_version")
        
        has_accepted = accepted == "true"
        needs_accept = not has_accepted
        
        logger.info(f"免责声明状态查询: has_accepted={has_accepted}")
        
        return DisclaimerStatus(
            has_accepted=has_accepted,
            accepted_at=accepted_at,
            version=version,
            needs_accept=needs_accept
        )
        
    except Exception as e:
        logger.error(f"获取免责声明状态失败: {e}")
        # 出错时默认需要同意
        return DisclaimerStatus(
            has_accepted=False,
            accepted_at=None,
            version=None,
            needs_accept=True
        )


@router.post("/accept")
async def accept_disclaimer(acceptance: DisclaimerAcceptance):
    """
    记录用户同意免责声明
    
    Args:
        acceptance: 同意记录（时间和版本）
        
    Returns:
        成功信息
    """
    try:
        # 记录到系统配置
        db.set_config("disclaimer_accepted", "true")
        db.set_config("disclaimer_accepted_at", acceptance.accepted_at)
        db.set_config("disclaimer_version", acceptance.version)
        
        # 记录到审计日志
        logger.info(
            f"用户同意免责声明: version={acceptance.version}, "
            f"time={acceptance.accepted_at}"
        )
        
        # 如果有审计日志系统，记录此操作
        try:
            from ..utils.audit_logger import audit_logger
            audit_logger.log(
                action="disclaimer_accepted",
                resource_type="system",
                resource_id="disclaimer",
                details={
                    "version": acceptance.version,
                    "accepted_at": acceptance.accepted_at
                },
                result="success"
            )
        except ImportError:
            pass  # 审计日志系统可选
        
        return {
            "success": True,
            "message": "免责声明同意记录成功",
            "accepted_at": acceptance.accepted_at
        }
        
    except Exception as e:
        logger.error(f"记录免责声明同意失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"记录失败: {str(e)}"
        )


@router.post("/reset")
async def reset_disclaimer():
    """
    重置免责声明状态（用于测试或重新显示）
    
    ⚠️ 注意：此接口应当受到权限保护，仅供管理员使用
    
    Returns:
        成功信息
    """
    try:
        # 清除配置
        db.set_config("disclaimer_accepted", "false")
        db.set_config("disclaimer_accepted_at", "")
        db.set_config("disclaimer_version", "")
        
        logger.warning("免责声明状态已重置")
        
        return {
            "success": True,
            "message": "免责声明状态已重置"
        }
        
    except Exception as e:
        logger.error(f"重置免责声明状态失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"重置失败: {str(e)}"
        )


@router.get("/content")
async def get_disclaimer_content():
    """
    获取免责声明内容（用于显示或导出）
    
    Returns:
        免责声明文本内容
    """
    content = """
# KOOK消息转发系统 - 免责声明

## 1. 浏览器自动化抓取风险

本软件通过浏览器自动化技术（Playwright）抓取KOOK消息，可能违反KOOK平台服务条款。

- KOOK官方未授权任何第三方工具进行消息抓取
- 使用本软件可能导致您的KOOK账号被警告、限制或永久封禁
- 建议仅在测试环境或已获得平台明确授权的情况下使用

## 2. 账号安全与隐私风险

使用本软件需要提供KOOK账号凭证（密码或Cookie），存在以下风险：

- 虽然软件采用AES-256加密存储，但无法100%保证凭证安全
- 本地数据库文件如被他人获取，可能导致账号信息泄露
- 建议使用独立的测试账号，避免使用主要账号
- 定期更换密码，启用KOOK的两步验证功能

## 3. 版权与内容责任

转发的消息内容可能涉及版权、隐私及其他法律问题：

- 请确保您有权转发相关消息内容
- 未经授权转发他人原创内容可能侵犯著作权
- 转发涉密、敏感、违法信息需自行承担法律责任
- 请遵守目标平台（Discord/Telegram/飞书）的服务条款

## 4. 法律责任与免责条款

使用本软件即表示您理解并同意：

- 本软件仅供学习、研究和技术交流使用
- 开发者不对因使用本软件造成的任何损失承担责任，包括但不限于：
  - 账号被封禁、限制或损失
  - 数据丢失、泄露或被篡改
  - 因违反法律法规导致的法律纠纷
  - 因软件缺陷导致的任何直接或间接损失
- 使用者需自行承担所有使用风险和法律责任
- 如因使用本软件涉及法律诉讼，使用者需自行应对，开发者不承担任何责任

## 5. 建议的合规使用场景

为降低风险，我们建议仅在以下场景使用：

- ✅ 自有社区/服务器：您是KOOK服务器的所有者或管理员
- ✅ 已获授权：已获得服务器所有者和相关用户的明确授权
- ✅ 测试环境：使用测试账号在私有环境中测试
- ✅ 个人备份：仅用于备份自己发送的消息
- ❌ 请勿用于：商业用途、批量营销、爬取他人隐私信息

---

版本: 1.0.0
生效日期: 2025-10-31
"""
    
    return {
        "success": True,
        "content": content,
        "version": "1.0.0",
        "effective_date": "2025-10-31"
    }
