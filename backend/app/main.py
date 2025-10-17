"""
FastAPI主应用
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import accounts, bots, mappings, logs, system, websocket, backup, smart_mapping, auth, health, updates, selectors
from .queue.redis_client import redis_queue
from .queue.worker import message_worker
from .queue.retry_worker import retry_worker
from .utils.logger import logger
from .utils.captcha_solver import init_captcha_solver
from .utils.auth import verify_api_token, generate_api_token
from .utils.scheduler import setup_scheduled_tasks, shutdown_scheduled_tasks
from .utils.health import health_checker
from .utils.update_checker import update_checker
from .config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info("=" * 50)
    
    # 检查API Token配置
    if settings.api_token:
        logger.info(f"✅ API认证已启用（Token: {settings.api_token[:10]}...）")
    else:
        logger.warning("⚠️  API认证未启用（建议设置API_TOKEN环境变量）")
        logger.warning("⚠️  生成Token建议：export API_TOKEN=" + generate_api_token())
    
    # 存储后台任务
    background_tasks = []
    
    try:
        # 初始化验证码求解器
        if settings.captcha_2captcha_api_key:
            init_captcha_solver(settings.captcha_2captcha_api_key)
            logger.info("✅ 2Captcha验证码求解器已初始化")
        else:
            logger.info("ℹ️ 2Captcha未配置，验证码需手动输入")
        
        # 连接Redis
        await redis_queue.connect()
        logger.info("✅ Redis连接成功")
        
        # 启动Worker
        worker_task = asyncio.create_task(message_worker.start())
        background_tasks.append(worker_task)
        logger.info("✅ 消息处理Worker已启动")
        
        # 启动重试Worker
        retry_task = asyncio.create_task(retry_worker.start())
        background_tasks.append(retry_task)
        logger.info("✅ 失败消息重试Worker已启动")
        
        # 启动图床服务器
        from .image_server import start_image_server
        image_server_task = asyncio.create_task(start_image_server())
        background_tasks.append(image_server_task)
        logger.info(f"✅ 图床服务器已启动: http://127.0.0.1:{settings.image_server_port}")
        
        # 启动定时任务调度器
        setup_scheduled_tasks()
        logger.info("✅ 定时任务调度器已启动")
        
        # 启动健康检查器
        if settings.health_check_enabled:
            health_check_task = asyncio.create_task(health_checker.start())
            background_tasks.append(health_check_task)
            logger.info("✅ 健康检查器已启动")
        
        # 启动更新检查器
        if settings.auto_update_enabled:
            update_check_task = asyncio.create_task(update_checker.start())
            background_tasks.append(update_check_task)
            logger.info("✅ 更新检查器已启动")
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")
    
    yield
    
    # 关闭时
    logger.info("正在关闭服务...")
    
    try:
        # 停止定时任务
        shutdown_scheduled_tasks()
        logger.info("✅ 定时任务已停止")
        
        # 停止健康检查器
        await health_checker.stop()
        logger.info("✅ 健康检查器已停止")
        
        # 停止更新检查器
        await update_checker.stop()
        logger.info("✅ 更新检查器已停止")
        
        # 停止Worker
        await message_worker.stop()
        logger.info("✅ 消息处理Worker已停止")
        
        # 停止重试Worker
        await retry_worker.stop()
        logger.info("✅ 重试Worker已停止")
        
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
    # 开发环境允许本地访问，生产环境应限制具体域名
    allow_origins=[
        "http://localhost:5173",  # Vite开发服务器
        "http://localhost:3000",  # 备用端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Token"],  # 明确允许Token头
)

# 注册路由
app.include_router(auth.router)  # 认证相关（无需Token）
app.include_router(accounts.router)
app.include_router(bots.router)
app.include_router(mappings.router)
app.include_router(logs.router)
app.include_router(system.router)
app.include_router(websocket.router)
app.include_router(backup.router)
app.include_router(smart_mapping.router)
app.include_router(health.router)  # 健康检查
app.include_router(updates.router)  # 更新检查
app.include_router(selectors.router)  # 选择器配置


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
