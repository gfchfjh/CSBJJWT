"""
图床安全服务器 - 完整安全机制实现
✅ P0-4优化: Token验证 + IP白名单 + 路径遍历防护
"""
import secrets
import time
import asyncio
from pathlib import Path
from typing import Dict, Optional, Set
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from .config import settings
from .utils.logger import logger


class SecureImageServer:
    """安全的图床服务器"""
    
    def __init__(self):
        # Token存储：{token: {'filename': str, 'expire_at': float}}
        self.tokens: Dict[str, Dict] = {}
        
        # IP白名单（只允许本地访问）
        self.whitelist_ips: Set[str] = {
            '127.0.0.1',
            '::1',
            'localhost',
            '0.0.0.0'  # Docker容器内部访问
        }
        
        # 危险路径模式
        self.dangerous_patterns = ['..', '~', '/etc/', '/root/', 'C:\\', 'D:\\']
        
        # 清理任务
        self.cleanup_task = None
        
    def generate_token(self, filename: str, ttl: int = 7200) -> str:
        """
        生成安全Token
        
        Args:
            filename: 文件名（仅文件名，不含路径）
            ttl: 有效期（秒），默认2小时
            
        Returns:
            32字节的随机Token
            
        Raises:
            ValueError: 文件名不合法
        """
        # 1. 验证文件名安全性
        if self._is_dangerous_path(filename):
            raise ValueError(f"非法文件名: {filename}")
        
        # 2. 验证文件存在
        file_path = settings.image_storage_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        # 3. 生成随机Token（256位熵）
        token = secrets.token_urlsafe(32)
        
        # 4. 存储Token信息
        self.tokens[token] = {
            'filename': filename,
            'expire_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        logger.debug(f"生成Token: {token[:10]}... -> {filename} (有效期{ttl}秒)")
        
        return token
    
    def _is_dangerous_path(self, path: str) -> bool:
        """检查路径是否包含危险模式"""
        path_lower = path.lower()
        
        for pattern in self.dangerous_patterns:
            if pattern in path_lower:
                return True
        
        # 检查路径分隔符（防止跨目录访问）
        if '/' in path or '\\' in path:
            return True
        
        return False
    
    async def serve_image(self, request: Request, token: str) -> FileResponse:
        """
        提供图片服务（带完整安全检查）
        
        Args:
            request: FastAPI请求对象
            token: 访问Token
            
        Returns:
            FileResponse对象
            
        Raises:
            HTTPException: 各种安全检查失败
        """
        # 1. IP白名单检查
        client_ip = request.client.host
        
        if client_ip not in self.whitelist_ips:
            logger.warning(f"⚠️ 拒绝非白名单IP访问: {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Forbidden: 仅允许本地访问"
            )
        
        # 2. Token存在性检查
        if token not in self.tokens:
            logger.warning(f"⚠️ 无效Token访问: {token[:10]}... from {client_ip}")
            raise HTTPException(
                status_code=404,
                detail="Token无效或已过期"
            )
        
        token_info = self.tokens[token]
        
        # 3. Token过期检查
        if time.time() > token_info['expire_at']:
            logger.info(f"Token已过期: {token[:10]}...")
            # 删除过期Token
            del self.tokens[token]
            raise HTTPException(
                status_code=410,
                detail="Token已过期"
            )
        
        # 4. 文件名安全检查
        filename = token_info['filename']
        
        if self._is_dangerous_path(filename):
            logger.error(f"🚨 检测到路径遍历攻击: {filename} from {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Forbidden: 路径遍历攻击"
            )
        
        # 5. 路径规范化检查（防止符号链接攻击）
        file_path = settings.image_storage_path / filename
        
        try:
            # 获取真实路径
            real_path = file_path.resolve()
            allowed_path = settings.image_storage_path.resolve()
            
            # 确保文件在允许的目录内
            if not str(real_path).startswith(str(allowed_path)):
                logger.error(f"🚨 检测到目录遍历攻击: {filename} -> {real_path}")
                raise HTTPException(
                    status_code=403,
                    detail="Forbidden: 目录遍历攻击"
                )
        except Exception as e:
            logger.error(f"路径检查失败: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
        
        # 6. 文件存在性检查
        if not file_path.exists():
            logger.warning(f"文件不存在: {filename}")
            raise HTTPException(
                status_code=404,
                detail="文件不存在"
            )
        
        # 7. 记录访问日志（最近100条）
        self._log_access(token, filename, client_ip)
        
        # 8. 返回文件
        logger.info(f"✅ 提供图片: {filename} to {client_ip}")
        
        return FileResponse(
            path=file_path,
            media_type=self._get_media_type(filename),
            headers={
                'Cache-Control': 'public, max-age=3600',  # 缓存1小时
                'X-Content-Type-Options': 'nosniff',      # 防止MIME嗅探
                'X-Frame-Options': 'DENY'                 # 防止点击劫持
            }
        )
    
    def _get_media_type(self, filename: str) -> str:
        """根据文件扩展名返回MIME类型"""
        ext = filename.lower().split('.')[-1]
        
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml'
        }
        
        return mime_types.get(ext, 'application/octet-stream')
    
    def _log_access(self, token: str, filename: str, client_ip: str):
        """记录访问日志（环形缓冲，保留最近100条）"""
        if not hasattr(self, '_access_logs'):
            self._access_logs = []
        
        self._access_logs.append({
            'token': token[:10] + '...',
            'filename': filename,
            'client_ip': client_ip,
            'timestamp': time.time()
        })
        
        # 保留最近100条
        if len(self._access_logs) > 100:
            self._access_logs = self._access_logs[-100:]
    
    def get_access_logs(self, limit: int = 50) -> list:
        """获取访问日志"""
        if not hasattr(self, '_access_logs'):
            return []
        
        return self._access_logs[-limit:]
    
    async def cleanup_expired_tokens(self):
        """清理过期Token（定时任务）"""
        while True:
            try:
                await asyncio.sleep(900)  # 每15分钟清理一次
                
                now = time.time()
                expired_tokens = [
                    token for token, info in self.tokens.items()
                    if now > info['expire_at']
                ]
                
                for token in expired_tokens:
                    del self.tokens[token]
                
                if expired_tokens:
                    logger.info(f"🧹 清理了{len(expired_tokens)}个过期Token")
                
                # 统计信息
                logger.debug(f"Token统计: 总数={len(self.tokens)}, 清理={len(expired_tokens)}")
                
            except Exception as e:
                logger.error(f"清理Token异常: {e}")
    
    def start_cleanup_task(self):
        """启动清理任务"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self.cleanup_expired_tokens())
            logger.info("✅ Token清理任务已启动")
    
    def stop_cleanup_task(self):
        """停止清理任务"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            logger.info("Token清理任务已停止")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        now = time.time()
        
        active_tokens = sum(1 for info in self.tokens.values() if now <= info['expire_at'])
        expired_tokens = len(self.tokens) - active_tokens
        
        return {
            'total_tokens': len(self.tokens),
            'active_tokens': active_tokens,
            'expired_tokens': expired_tokens,
            'whitelist_ips': list(self.whitelist_ips),
            'total_accesses': len(getattr(self, '_access_logs', []))
        }


# 全局实例
secure_image_server = SecureImageServer()


# FastAPI应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    logger.info("🔒 启动安全图床服务器...")
    secure_image_server.start_cleanup_task()
    
    yield
    
    # 关闭时
    logger.info("🔒 关闭安全图床服务器...")
    secure_image_server.stop_cleanup_task()


app = FastAPI(
    title="KOOK图床安全服务器",
    description="带Token验证和IP白名单的安全图床",
    lifespan=lifespan
)


@app.get("/images/{token}/{filename}")
async def serve_image(request: Request, token: str, filename: str):
    """提供图片服务（兼容旧URL格式）"""
    return await secure_image_server.serve_image(request, token)


@app.get("/images/{filename}")
async def serve_image_with_token(request: Request, filename: str, token: str):
    """提供图片服务（Token作为查询参数）"""
    return await secure_image_server.serve_image(request, token)


@app.get("/stats")
async def get_stats():
    """获取统计信息（仅本地访问）"""
    return secure_image_server.get_stats()


@app.get("/logs")
async def get_logs(limit: int = 50):
    """获取访问日志（仅本地访问）"""
    return {
        'logs': secure_image_server.get_access_logs(limit)
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'active_tokens': len(secure_image_server.tokens)
    }


# 启动函数
async def start_secure_image_server():
    """启动安全图床服务器"""
    import uvicorn
    
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",  # 仅本地访问
        port=settings.image_server_port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    logger.info(f"🔒 安全图床服务器启动在: http://127.0.0.1:{settings.image_server_port}")
    
    await server.serve()


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_secure_image_server())
