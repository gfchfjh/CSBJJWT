"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import accounts, bots, mappings, logs, system
from .queue.redis_client import redis_queue
from .queue.worker import message_worker
from .utils.logger import logger
from .config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info("=" * 50)
    
    # 存储后台任务
    background_tasks = []
    
    try:
        # 连接Redis
        await redis_queue.connect()
        logger.info("✅ Redis连接成功")
        
        # 启动Worker
        worker_task = asyncio.create_task(message_worker.start())
        background_tasks.append(worker_task)
        logger.info("✅ 消息处理Worker已启动")
        
        # 启动图床服务器
        from .image_server import start_image_server
        image_server_task = asyncio.create_task(start_image_server())
        background_tasks.append(image_server_task)
        logger.info(f"✅ 图床服务器已启动: http://127.0.0.1:{settings.image_server_port}")
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")
    
    yield
    
    # 关闭时
    logger.info("正在关闭服务...")
    
    try:
        # 停止Worker
        await message_worker.stop()
        logger.info("✅ 消息处理Worker已停止")
        
        # 取消所有后台任务
        for task in background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info("✅ 后台任务已停止")
        
        # 断开Redis
        await redis_queue.disconnect()
        logger.info("✅ Redis连接已关闭")
        
    except Exception as e:
        logger.error(f"❌ 关闭失败: {str(e)}")
    
    logger.info("服务已完全关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="KOOK消息转发系统后端API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(accounts.router)
app.include_router(bots.router)
app.include_router(mappings.router)
app.include_router(logs.router)
app.include_router(system.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
