"""
终极环境检测API
✅ P0-5深度优化
"""
from fastapi import APIRouter
from ..utils.environment_checker_ultimate import ultimate_env_checker
from ..utils.logger import logger

router = APIRouter(prefix="/api/environment", tags=["environment"])


@router.get("/check-all")
async def check_all_environment():
    """
    并发检查所有环境（5-10秒完成）
    
    Returns:
        完整的检查结果
    """
    logger.info("📋 收到环境检测请求")
    result = await ultimate_env_checker.check_all_concurrent()
    
    if result["all_passed"]:
        logger.info(f"✅ 环境检测全部通过（耗时{result['duration']}秒）")
    else:
        logger.warning(f"⚠️ 环境检测发现 {len(result['fixable_issues'])} 个问题")
    
    return result


@router.post("/auto-fix")
async def auto_fix_environment():
    """
    一键自动修复所有问题
    
    Returns:
        修复结果
    """
    logger.info("🔧 开始自动修复环境问题")
    result = await ultimate_env_checker.auto_fix_all()
    
    if result["success"]:
        logger.info(f"✅ 自动修复成功: {len(result['fixed'])} 个问题已修复")
    else:
        logger.error(f"❌ 自动修复部分失败: {len(result['failed'])} 个问题无法修复")
    
    return result
