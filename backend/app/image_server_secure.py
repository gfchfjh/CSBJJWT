"""
🔒 P0-4优化: 安全的图床服务器（Token验证机制）

功能：
1. 32字节URL安全Token
2. 2小时有效期
3. Token与文件名绑定验证
4. 每15分钟自动清理过期Token
5. 防止路径遍历攻击
6. 安全HTTP响应头
7. 仅允许本地访问
8. 自动清理旧图片（7天前）

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
import secrets
import time
import asyncio
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from .utils.logger import logger
from .config import settings, IMAGE_DIR
import uuid


class SecureImageServer:
    """安全的图床服务器"""
    
    def __init__(self):
        # Token存储 {token: {filename, expires_at, created_at}}
        self.tokens: Dict[str, dict] = {}
        
        # Token有效期（2小时）
        self.token_lifetime = 7200
        
        # 清理任务
        self.cleanup_task = None
        self.image_cleanup_task = None
        
        # 启动清理任务
        self.start_cleanup_tasks()
        
        logger.info("✅ 安全图床服务器已初始化")
    
    def generate_token(self, filename: str) -> str:
        """
        生成安全Token
        
        Args:
            filename: 图片文件名
            
        Returns:
            32字节URL安全Token
        """
        token = secrets.token_urlsafe(32)
        
        self.tokens[token] = {
            'filename': filename,
            'expires_at': time.time() + self.token_lifetime,
            'created_at': time.time()
        }
        
        logger.debug(f"生成Token: {token[:10]}... for {filename}")
        
        return token
    
    def validate_token(self, token: str, filename: str) -> bool:
        """
        验证Token
        
        Args:
            token: Token字符串
            filename: 请求的文件名
            
        Returns:
            是否有效
        """
        # Token不存在
        if token not in self.tokens:
            logger.warning(f"Token不存在: {token[:10]}...")
            return False
        
        token_data = self.tokens[token]
        
        # 检查是否过期
        if time.time() > token_data['expires_at']:
            logger.warning(f"Token已过期: {token[:10]}...")
            del self.tokens[token]
            return False
        
        # 检查文件名是否匹配
        if token_data['filename'] != filename:
            logger.warning(f"文件名不匹配: {filename} != {token_data['filename']}")
            return False
        
        return True
    
    def revoke_token(self, token: str):
        """撤销Token"""
        if token in self.tokens:
            del self.tokens[token]
            logger.debug(f"Token已撤销: {token[:10]}...")
    
    async def serve_image(
        self, 
        filename: str, 
        token: str, 
        request: Request
    ) -> FileResponse:
        """
        提供图片服务（带安全检查）
        
        Args:
            filename: 文件名
            token: Token
            request: 请求对象
            
        Returns:
            FileResponse
            
        Raises:
            HTTPException: 验证失败
        """
        # 1. 仅允许本地访问
        client_host = request.client.host
        if client_host not in ['127.0.0.1', 'localhost', '::1', '0.0.0.0']:
            logger.error(f"非本地访问被拒绝: {client_host}")
            raise HTTPException(403, "仅允许本地访问")
        
        # 2. 验证Token
        if not self.validate_token(token, filename):
            raise HTTPException(403, "Token无效或已过期")
        
        # 3. 防止路径遍历
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            logger.error(f"检测到路径遍历攻击: {filename}")
            raise HTTPException(400, "非法文件名")
        
        # 4. 检查文件是否存在
        file_path = IMAGE_DIR / filename
        
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            raise HTTPException(404, "文件不存在")
        
        if not file_path.is_file():
            logger.error(f"不是文件: {file_path}")
            raise HTTPException(400, "非法路径")
        
        # 5. 检查文件是否在IMAGE_DIR内（二次防御）
        try:
            file_path.resolve().relative_to(IMAGE_DIR.resolve())
        except ValueError:
            logger.error(f"文件路径不在IMAGE_DIR内: {file_path}")
            raise HTTPException(403, "非法访问")
        
        # 6. 设置安全响应头
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Cache-Control': 'private, max-age=7200',
            'Content-Security-Policy': "default-src 'none'",
            'X-Token-Expires-At': str(int(self.tokens[token]['expires_at']))
        }
        
        logger.debug(f"提供图片: {filename}")
        
        return FileResponse(file_path, headers=headers)
    
    async def upload_image(self, file: UploadFile) -> Dict[str, str]:
        """
        上传图片并返回带Token的URL
        
        Args:
            file: 上传的文件
            
        Returns:
            {'url': 完整URL, 'filename': 文件名, 'token': Token, 'expires_in': 过期时间}
        """
        # 生成唯一文件名
        ext = Path(file.filename).suffix if file.filename else '.jpg'
        filename = f"{uuid.uuid4()}{ext}"
        file_path = IMAGE_DIR / filename
        
        # 保存文件
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"图片已上传: {filename} ({len(content)} bytes)")
        
        # 生成Token
        token = self.generate_token(filename)
        
        # 返回带Token的URL
        url = f"http://localhost:{settings.image_server_port}/images/{filename}?token={token}"
        
        return {
            'url': url,
            'filename': filename,
            'token': token,
            'expires_in': self.token_lifetime,
            'size': len(content)
        }
    
    def start_cleanup_tasks(self):
        """启动清理任务"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_tokens())
            logger.info("✅ Token清理任务已启动")
        
        if self.image_cleanup_task is None:
            self.image_cleanup_task = asyncio.create_task(self._cleanup_old_images())
            logger.info("✅ 图片清理任务已启动")
    
    def stop_cleanup_tasks(self):
        """停止清理任务"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None
            logger.info("✅ Token清理任务已停止")
        
        if self.image_cleanup_task:
            self.image_cleanup_task.cancel()
            self.image_cleanup_task = None
            logger.info("✅ 图片清理任务已停止")
    
    async def _cleanup_expired_tokens(self):
        """每15分钟清理过期Token"""
        while True:
            try:
                await asyncio.sleep(900)  # 15分钟
                
                current_time = time.time()
                expired = [
                    token for token, data in self.tokens.items()
                    if current_time > data['expires_at']
                ]
                
                for token in expired:
                    del self.tokens[token]
                
                if expired:
                    logger.info(f"清理了{len(expired)}个过期Token")
                
                # 定期打印统计
                logger.debug(f"当前Token数量: {len(self.tokens)}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Token清理任务异常: {str(e)}")
    
    async def _cleanup_old_images(self):
        """每天清理旧图片"""
        while True:
            try:
                await asyncio.sleep(86400)  # 24小时
                
                # 删除7天前的图片
                cutoff_time = time.time() - (settings.image_cleanup_days * 86400)
                deleted_count = 0
                deleted_size = 0
                
                for image_file in IMAGE_DIR.glob('*'):
                    if image_file.is_file():
                        # 检查修改时间
                        if image_file.stat().st_mtime < cutoff_time:
                            file_size = image_file.stat().st_size
                            image_file.unlink()
                            deleted_count += 1
                            deleted_size += file_size
                
                if deleted_count > 0:
                    logger.info(
                        f"清理了{deleted_count}张旧图片 "
                        f"({deleted_size / (1024**2):.2f} MB)"
                    )
                
                # 检查磁盘空间
                await self._check_disk_space()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"图片清理任务异常: {str(e)}")
    
    async def _check_disk_space(self):
        """检查磁盘空间并清理"""
        try:
            # 计算IMAGE_DIR占用空间
            total_size = sum(
                f.stat().st_size for f in IMAGE_DIR.glob('**/*')
                if f.is_file()
            ) / (1024**3)  # GB
            
            max_size = settings.image_max_size_gb
            
            if total_size > max_size:
                logger.warning(
                    f"图片占用空间超限: {total_size:.2f}GB > {max_size}GB"
                )
                
                # 按时间排序，删除最旧的图片
                files = sorted(
                    IMAGE_DIR.glob('*'),
                    key=lambda f: f.stat().st_mtime if f.is_file() else 0
                )
                
                # 删除最旧的20%
                to_delete = int(len(files) * 0.2)
                deleted_count = 0
                deleted_size = 0
                
                for f in files[:to_delete]:
                    if f.is_file():
                        file_size = f.stat().st_size
                        f.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                
                logger.info(
                    f"清理了{deleted_count}张旧图片以释放空间 "
                    f"({deleted_size / (1024**2):.2f} MB)"
                )
        
        except Exception as e:
            logger.error(f"磁盘空间检查异常: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        # 计算过期的Token数量
        current_time = time.time()
        expired_count = sum(
            1 for data in self.tokens.values()
            if current_time > data['expires_at']
        )
        
        # 计算图片总数和大小
        image_count = len(list(IMAGE_DIR.glob('*')))
        total_size = sum(
            f.stat().st_size for f in IMAGE_DIR.glob('*')
            if f.is_file()
        ) / (1024**2)  # MB
        
        return {
            'total_tokens': len(self.tokens),
            'expired_tokens': expired_count,
            'active_tokens': len(self.tokens) - expired_count,
            'total_images': image_count,
            'total_size_mb': round(total_size, 2),
            'max_size_gb': settings.image_max_size_gb,
            'cleanup_days': settings.image_cleanup_days
        }


# 创建全局实例
secure_image_server = SecureImageServer()


# FastAPI应用
app = FastAPI(title="安全图床服务器", version="11.0.0")


@app.get("/images/{filename}")
async def serve_image(filename: str, token: str, request: Request):
    """
    提供图片服务（需要Token）
    
    Args:
        filename: 图片文件名
        token: 访问Token
        
    Returns:
        图片文件
    """
    return await secure_image_server.serve_image(filename, token, request)


@app.post("/api/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片并返回带Token的URL
    
    Args:
        file: 图片文件
        
    Returns:
        {'url': 完整URL, 'token': Token, 'expires_in': 过期时间}
    """
    return await secure_image_server.upload_image(file)


@app.get("/api/images/stats")
async def get_stats():
    """获取图床统计信息"""
    return secure_image_server.get_stats()


@app.post("/api/images/token/revoke")
async def revoke_token(token: str):
    """撤销Token"""
    secure_image_server.revoke_token(token)
    return {"success": True}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


async def start_server():
    """启动服务器"""
    import uvicorn
    
    logger.info(f"启动安全图床服务器: http://127.0.0.1:{settings.image_server_port}")
    
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=settings.image_server_port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()
