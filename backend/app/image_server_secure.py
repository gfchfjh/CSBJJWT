"""
安全图片服务器 - P1-2优化
提供Token验证、路径防护、本地访问限制的图片服务
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import secrets
import time
from pathlib import Path
from typing import Dict
import re
from .utils.logger import logger
from .config import settings

app = FastAPI(title="Secure Image Server")

# Token存储（生产环境应使用Redis）
image_tokens: Dict[str, dict] = {}

# 图片目录
IMAGE_DIR = Path(settings.image_dir) if hasattr(settings, 'image_dir') else Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# 允许的IP白名单
ALLOWED_IPS = ["127.0.0.1", "localhost", "::1", "0.0.0.0"]

# Token有效期（秒）
TOKEN_EXPIRE_TIME = 7200  # 2小时

# 自动清理间隔（秒）
CLEANUP_INTERVAL = 900  # 15分钟


@app.post("/generate-token")
async def generate_token(filename: str, request: Request):
    """
    生成图片访问Token
    
    Args:
        filename: 文件名
    
    Returns:
        {
            "success": bool,
            "url": str,
            "token": str,
            "expire_at": float
        }
    """
    # 1. 检查访问来源（仅允许本地）
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403,
            detail="仅允许本地访问"
        )
    
    # 2. 验证文件名安全性
    if not is_safe_filename(filename):
        raise HTTPException(status_code=400, detail="非法文件名")
    
    # 3. 检查文件是否存在
    file_path = IMAGE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 4. 生成Token
    token = secrets.token_urlsafe(32)
    
    # 5. 存储Token
    expire_at = time.time() + TOKEN_EXPIRE_TIME
    image_tokens[token] = {
        "filename": filename,
        "created_at": time.time(),
        "expire_at": expire_at,
        "access_count": 0,
        "client_ip": client_ip
    }
    
    # 6. 构建完整URL
    port = settings.image_server_port if hasattr(settings, 'image_server_port') else 8765
    url = f"http://127.0.0.1:{port}/images/{filename}?token={token}"
    
    logger.info(
        f"生成图片Token: {filename}, "
        f"token={token[:10]}..., "
        f"expire_at={expire_at}"
    )
    
    return {
        "success": True,
        "url": url,
        "token": token,
        "expire_at": expire_at,
        "valid_for_seconds": TOKEN_EXPIRE_TIME
    }


@app.get("/images/{filename}")
async def serve_image(filename: str, token: str, request: Request):
    """
    提供图片服务（安全版）
    
    Args:
        filename: 文件名
        token: 访问Token
    
    Returns:
        FileResponse
    """
    # 1. 检查访问来源
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        logger.warning(f"拒绝非本地访问: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail="仅允许本地访问"
        )
    
    # 2. 验证Token
    if token not in image_tokens:
        logger.warning(f"无效Token: {token[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Token无效或已过期"
        )
    
    token_data = image_tokens[token]
    
    # 3. 检查Token是否过期
    if time.time() > token_data["expire_at"]:
        del image_tokens[token]
        logger.warning(f"Token已过期: {token[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Token已过期"
        )
    
    # 4. 验证文件名匹配
    if token_data["filename"] != filename:
        logger.warning(
            f"Token与文件名不匹配: "
            f"expected={token_data['filename']}, got={filename}"
        )
        raise HTTPException(
            status_code=403,
            detail="Token与文件名不匹配"
        )
    
    # 5. 路径遍历防护
    if not is_safe_filename(filename):
        logger.warning(f"检测到非法文件名: {filename}")
        raise HTTPException(
            status_code=400,
            detail="非法文件名"
        )
    
    # 6. 构建安全的文件路径
    file_path = (IMAGE_DIR / filename).resolve()
    
    # 7. 确保文件在允许的目录内
    if not str(file_path).startswith(str(IMAGE_DIR.resolve())):
        logger.warning(f"路径遍历攻击: {file_path}")
        raise HTTPException(
            status_code=403,
            detail="非法路径"
        )
    
    # 8. 检查文件是否存在
    if not file_path.exists():
        logger.warning(f"文件不存在: {file_path}")
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )
    
    # 9. 更新访问计数
    token_data["access_count"] += 1
    token_data["last_access"] = time.time()
    
    # 10. 返回文件
    media_type = get_media_type(filename)
    
    logger.debug(
        f"提供图片: {filename}, "
        f"token={token[:10]}..., "
        f"access_count={token_data['access_count']}"
    )
    
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Token-Access-Count": str(token_data["access_count"]),
            "X-Token-Expire": str(int(token_data["expire_at"]))
        }
    )


def is_safe_filename(filename: str) -> bool:
    """
    检查文件名是否安全
    
    Args:
        filename: 文件名
    
    Returns:
        是否安全
    """
    # 1. 禁止路径遍历
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    
    # 2. 禁止隐藏文件
    if filename.startswith('.'):
        return False
    
    # 3. 只允许字母、数字、-、_、.
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        return False
    
    # 4. 检查扩展名
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return False
    
    # 5. 文件名长度限制
    if len(filename) > 255:
        return False
    
    return True


def get_media_type(filename: str) -> str:
    """
    根据文件扩展名获取MIME类型
    
    Args:
        filename: 文件名
    
    Returns:
        MIME类型
    """
    ext = filename.lower().split('.')[-1]
    
    media_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'bmp': 'image/bmp'
    }
    
    return media_types.get(ext, 'application/octet-stream')


@app.get("/stats")
async def get_stats(request: Request):
    """
    获取统计信息（仅本地访问）
    
    Returns:
        Token统计信息
    """
    # 检查访问来源
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403,
            detail="仅允许本地访问"
        )
    
    current_time = time.time()
    
    stats = {
        "total_tokens": len(image_tokens),
        "active_tokens": sum(
            1 for data in image_tokens.values()
            if current_time <= data["expire_at"]
        ),
        "expired_tokens": sum(
            1 for data in image_tokens.values()
            if current_time > data["expire_at"]
        ),
        "total_accesses": sum(
            data["access_count"] for data in image_tokens.values()
        ),
        "tokens": [
            {
                "filename": data["filename"],
                "created_at": data["created_at"],
                "expire_at": data["expire_at"],
                "expires_in": max(0, int(data["expire_at"] - current_time)),
                "access_count": data["access_count"],
                "expired": current_time > data["expire_at"]
            }
            for data in list(image_tokens.values())[:100]  # 最多返回100个
        ]
    }
    
    return stats


@app.post("/cleanup")
async def cleanup_expired_tokens(request: Request):
    """
    手动清理过期Token（仅本地访问）
    
    Returns:
        清理结果
    """
    # 检查访问来源
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403,
            detail="仅允许本地访问"
        )
    
    current_time = time.time()
    expired_tokens = [
        token for token, data in image_tokens.items()
        if current_time > data["expire_at"]
    ]
    
    for token in expired_tokens:
        del image_tokens[token]
    
    logger.info(f"清理了 {len(expired_tokens)} 个过期Token")
    
    return {
        "success": True,
        "cleaned_count": len(expired_tokens),
        "remaining_count": len(image_tokens)
    }


# 启动时自动清理任务
@app.on_event("startup")
async def startup_cleanup_task():
    """启动自动清理任务"""
    import asyncio
    
    async def cleanup_loop():
        while True:
            await asyncio.sleep(CLEANUP_INTERVAL)
            
            try:
                current_time = time.time()
                expired_tokens = [
                    token for token, data in image_tokens.items()
                    if current_time > data["expire_at"]
                ]
                
                for token in expired_tokens:
                    del image_tokens[token]
                
                if expired_tokens:
                    logger.info(f"自动清理了 {len(expired_tokens)} 个过期Token")
            
            except Exception as e:
                logger.error(f"自动清理失败: {e}")
    
    asyncio.create_task(cleanup_loop())
    logger.info(f"自动清理任务已启动，间隔{CLEANUP_INTERVAL}秒")
