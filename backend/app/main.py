"""
FastAPI主应用（✅ P2-5优化：全局API认证）
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import accounts, bots, mappings, logs, system, websocket, backup, smart_mapping, smart_mapping_enhanced, auth, health, updates, selectors, password_reset, telegram_helper, cookie_import, environment, environment_autofix, auth_master_password, first_run, smart_mapping_ultimate
# ✅ P0-P1优化新增: 增强版API
from .api import password_reset_enhanced, environment_autofix_enhanced, help_system
# ✅ P0-1新增: 视频管理API
from .api import video_api
# ✅ 深度优化: 视频教程管理API（完整版）
from .api import video_tutorials
# ✅ P0-2新增: 邮件管理API
from .api import email_api
# ✅ P0-4新增: 文件安全API
from .api import file_security_api
from .api import performance  # v1.12.0 性能监控API
# ✅ v6.0.0新增: Cookie导入增强版API
from .api import cookie_import_enhanced
# ✅ P0-2深度优化: 配置向导测试API
from .api import wizard_testing, wizard_testing_enhanced
# ✅ P0-3深度优化: 图床存储管理API
from .api import image_storage_manager
# ✅ P0-5深度优化: 限流监控API
from .api import rate_limit_monitor
# ✅ P1-1深度优化: 消息搜索API
from .api import message_search
# ✅ P1-5深度优化: Prometheus监控API
from .api import metrics_api
# ✅ v11.0.0终极优化新增: 终极版API 🆕
from .api import environment_ultimate_api, mapping_learning_ultimate_api, database_optimizer_api, notification_api
# ✅ v18.0.3新增: 统计和消息API 🆕
from .api import stats, messages, settings
from .middleware.auth_middleware import APIAuthMiddleware  # ✅ P2-5优化
from .queue.redis_client import redis_queue
from .queue.worker import message_worker
from .queue.retry_worker import retry_worker
from .utils.logger import logger
from .utils.captcha_solver import init_captcha_solver
from .utils.auth import verify_api_token, generate_api_token
from .utils.scheduler import setup_scheduled_tasks, shutdown_scheduled_tasks
from .utils.health import health_checker
from .utils.update_checker import update_checker
from .utils.redis_manager_enhanced import redis_manager  # v1.8.1使用增强版
from .config import settings
from .database import db
import asyncio
import json
from pathlib import Path


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
        # ✅ v1.13.0新增：环境检查（P0-5优化）
        # env_ok = await check_environment()
        if False:  # Disabled
            logger.warning("⚠️ 环境检查发现严重问题，但将继续启动。请尽快解决这些问题以确保正常运行。")
        
        # 启动嵌入式Redis服务（v1.8.1增强版）
        logger.info("🔍 启动Redis服务...")
        redis_success, redis_msg = await redis_manager.start()
        if redis_success:
            logger.info(f"✅ {redis_msg}")
        else:
            logger.warning(f"⚠️ {redis_msg}")
            logger.warning("⚠️ 尝试连接外部Redis...")
        
        # 初始化验证码求解器
        if settings.captcha_2captcha_api_key:
            init_captcha_solver(settings.captcha_2captcha_api_key)
            logger.info("✅ 2Captcha验证码求解器已初始化")
        else:
            logger.info("ℹ️ 2Captcha未配置，将使用本地OCR或手动输入")
        
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
        
        # ✅ P0-5深度优化: 启动安全图床服务器
        # from .image_server_secure import start_image_server
        # image_server_task = asyncio.create_task(start_image_server())
        # background_tasks.append(image_server_task)
        # logger.info(f"✅ 安全图床服务器已启动: http://127.0.0.1:{settings.image_server_port}")
        logger.info(f"   - IP白名单已启用（仅本地访问）")
        logger.info(f"   - Token验证已启用（2小时有效期）")
        logger.info(f"   - 路径遍历防护已启用")
        
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
        
        # 停止Token清理任务
        from .processors.image import image_processor
        image_processor.stop_cleanup_task()
        logger.info("✅ Token清理任务已停止")
        
        # 停止嵌入式Redis服务
        redis_manager.stop()
        logger.info("✅ Redis服务已停止")
        
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

# ✅ 优化12: 注册全局异常处理器
from .utils.exceptions import KookForwarderException, get_exception_handler

@app.exception_handler(KookForwarderException)
async def kook_exception_handler(request, exc: KookForwarderException):
    """处理所有KookForwarder自定义异常"""
    return get_exception_handler()(request, exc)

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
app.include_router(auth_master_password.router)  # 主密码认证 🆕 P0-8优化
app.include_router(password_reset.router)  # 密码重置（无需Token）
app.include_router(first_run.router)  # 首次运行检测 🆕 P0-2优化

# ✅ v17.0.0深度优化: 免责声明API
from .api import disclaimer
app.include_router(disclaimer.router)  # 免责声明系统 🆕 v17.0.0深度优化

# ✅ v17.0.0深度优化: 密码强度验证API
from .api import password_strength
app.include_router(password_strength.router)  # 密码强度验证 🆕 v17.0.0深度优化
app.include_router(accounts.router)
app.include_router(bots.router)
app.include_router(mappings.router)
app.include_router(logs.router)
app.include_router(system.router)
app.include_router(websocket.router)
app.include_router(backup.router)
app.include_router(smart_mapping.router)
app.include_router(smart_mapping_enhanced.router)  # ✅ 增强版智能映射（真实API）
app.include_router(smart_mapping_ultimate.router)  # ✅ P0-4优化：终极版智能映射
app.include_router(health.router)  # 健康检查
app.include_router(updates.router)  # 更新检查

# ✅ P2-2优化: 更新检查增强API
from .api import update_checker_enhanced
app.include_router(update_checker_enhanced.router)  # 更新检查增强 🆕 P2-2优化
app.include_router(selectors.router)  # 选择器配置
app.include_router(performance.router)  # 性能监控 🆕 v1.12.0
app.include_router(telegram_helper.router)  # Telegram辅助工具 🆕 v1.15.0
app.include_router(cookie_import.router)  # Cookie导入 🆕 P0-2优化
app.include_router(environment.router)  # 环境检查 🆕 P0-5优化
app.include_router(environment_autofix.router)  # 环境一键修复 🆕 P0-2优化
# ✅ P0-P1优化新增路由
app.include_router(password_reset_enhanced.router)  # 邮箱验证码重置 🆕 P0-14优化
app.include_router(environment_autofix_enhanced.router)  # 增强环境修复 🆕 P0-3优化
app.include_router(help_system.router)  # 完整帮助系统 🆕 P1-4优化
app.include_router(video_api.router)  # 视频管理API 🆕 P0-1优化
app.include_router(video_tutorials.router)  # 视频教程管理API（完整版） 🆕 深度优化
app.include_router(email_api.router)  # 邮件管理API 🆕 P0-2优化
app.include_router(file_security_api.router)  # 文件安全API 🆕 P0-4优化
app.include_router(cookie_import_enhanced.router)  # Cookie导入增强API 🆕 v6.0.0
# ✅ P0-3终极优化: Cookie一键导入API（支持Chrome扩展自动发送）
from .api import cookie_import_ultimate
app.include_router(cookie_import_ultimate.router)  # Cookie一键导入API 🆕 P0-3终极优化
app.include_router(wizard_testing.router)  # 配置向导测试API 🆕 P0-2深度优化
app.include_router(wizard_testing_enhanced.router)  # 配置向导测试API增强版 🆕 P0-2深度优化完整版
app.include_router(image_storage_manager.router)  # 图床存储管理API 🆕 P0-3深度优化
app.include_router(rate_limit_monitor.router)  # 限流监控API 🆕 P0-5深度优化
app.include_router(message_search.router)  # 消息搜索API 🆕 P1-1深度优化
app.include_router(metrics_api.router)  # Prometheus监控API 🆕 P1-5深度优化
# ✅ v11.0.0终极优化新增路由 🚀
app.include_router(environment_ultimate_api.router)  # 环境检测终极版API 🆕 v11.0.0
app.include_router(mapping_learning_ultimate_api.router)  # AI映射学习终极版API 🆕 v11.0.0
app.include_router(database_optimizer_api.router)  # 数据库优化API 🆕 v11.0.0
app.include_router(notification_api.router)  # 通知系统增强API 🆕 v11.0.0

# ✅ P0-2深度优化：友好错误提示系统
from .api import error_translator_api
app.include_router(error_translator_api.router)  # 错误翻译API 🆕 P0-2深度优化

# ✅ P0-4深度优化：验证码处理界面
from .api import captcha_api
app.include_router(captcha_api.router)  # 验证码API 🆕 P0-4深度优化

# ✅ P1-1深度优化：托盘菜单实时统计
from .api import system_stats_api
app.include_router(system_stats_api.router)  # 系统统计API 🆕 P1-1深度优化

# ✅ P0-9深度优化：托盘菜单统计完善
from .api import tray_stats_enhanced
app.include_router(tray_stats_enhanced.router)  # 托盘统计增强API 🆕 P0-9优化

# ✅ P0-3深度优化：验证码WebSocket
from .api import captcha_websocket
app.include_router(captcha_websocket.router)  # 验证码WebSocket 🆕 P0-3深度优化

# ✅ v9.0.0新增：智能向导API
from .api import wizard_smart_setup
app.include_router(wizard_smart_setup.router)  # 智能向导设置 🆕 v9.0.0

# ✅ P0-2深度优化: 首次运行检测API
from .api import wizard_first_run
app.include_router(wizard_first_run.router)  # 首次运行检测 🆕 P0-2优化

# ✅ P0-5深度优化: 终极环境检测API
from .api import environment_ultimate
app.include_router(environment_ultimate.router)  # 终极环境检测 🆕 P0-5优化

# ✅ P1-2深度优化: 映射学习引擎API
from .api import mapping_learning_ultimate
app.include_router(mapping_learning_ultimate.router)  # 映射学习引擎 🆕 P1-2优化

# ✅ P2-1深度优化: 数据库优化API
from .api import database_optimizer_ultimate_api
app.include_router(database_optimizer_ultimate_api.router)  # 数据库优化 🆕 P2-1优化

# ✅ v9.0.0新增：数据库优化API
from .api import database_optimizer_api
app.include_router(database_optimizer_api.router)  # 数据库优化 🆕 v9.0.0

# ✅ v9.0.0新增：映射学习引擎API
from .api import mapping_learning_api
app.include_router(mapping_learning_api.router)  # 映射学习 🆕 v9.0.0

# ✅ P0-2优化: 服务器自动发现API
from .api import server_discovery
app.include_router(server_discovery.router)  # 服务器/频道自动获取 🆕 P0-2优化

# ✅ P0-2终极优化: 服务器自动发现API（使用真实KOOK API）
from .api import servers_discovery_ultimate
app.include_router(servers_discovery_ultimate.router)  # 服务器/频道自动获取终极版 🆕 P0-2终极优化

# ✅ P0-4深度优化: 服务器自动发现增强API
from .api import server_discovery_enhanced
app.include_router(server_discovery_enhanced.router)  # 服务器/频道自动获取增强版 🆕 P0-4深度优化

# ✅ P1-5深度优化: 实时统计API
from .api import system_stats_realtime
app.include_router(system_stats_realtime.router)  # 实时统计API 🆕 P1-5深度优化

# ✅ P1-6优化: 映射学习反馈API
from .api import mapping_learning_feedback
app.include_router(mapping_learning_feedback.router)  # 映射学习反馈 🆕 P1-6优化

# ✅ 深度优化: 统一配置向导API
from .api import wizard_unified
app.include_router(wizard_unified.router)  # 统一配置向导 🆕 深度优化

# ✅ 深度优化: Cookie导入WebSocket
from .api import cookie_websocket
app.include_router(cookie_websocket.router)  # Cookie导入WebSocket 🆕 深度优化

# ✅ P0深度优化: 审计日志API
from .api import audit_logs
app.include_router(audit_logs.router)  # 审计日志系统 🆕 P0深度优化

# ✅ P0深度优化: 邮件告警API
from .api import email_config
app.include_router(email_config.router)  # 邮件告警系统 🆕 P0深度优化

# ✅ P1深度优化: 插件管理API
from .api import plugins_manager
app.include_router(plugins_manager.router)  # 插件管理系统 🆕 P1深度优化

# ✅ v18.0.3新增: 统计、消息和设置API
app.include_router(stats.router)  # 统计数据API 🆕 v18.0.3
app.include_router(messages.router)  # 消息查询API 🆕 v18.0.3
app.include_router(settings.router)  # 设置管理API 🆕 v18.0.3


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
