@echo off
REM ====================================================
REM   KOOK消息转发系统 启动脚本 (Windows)
REM   版本: v11.0.0 Enhanced
REM ====================================================

echo ===================================
echo   KOOK消息转发系统 v11.0.0
echo ===================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 📦 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📥 首次运行，正在安装依赖...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查Redis
where redis-server >nul 2>&1
if errorlevel 1 (
    echo 📥 启动嵌入式Redis...
    if exist redis\redis-server.exe (
        start /B redis\redis-server.exe redis\redis.conf
    ) else (
        echo ⚠️  Redis未找到，将尝试连接外部Redis
    )
) else (
    echo 📥 启动Redis服务...
    start /B redis-server redis\redis.conf
)

REM 等待Redis启动
timeout /t 2 /nobreak >nul

REM 启动后端
echo 🚀 启动后端服务...
cd backend
start /B python -m app.main
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🎨 启动前端界面...
cd frontend
if exist dist\index.html (
    REM 生产模式：使用构建后的文件
    if exist node_modules (
        npm run preview
    ) else (
        echo ⚠️  请先运行: cd frontend && npm install
    )
) else (
    REM 开发模式
    if exist node_modules (
        npm run dev
    ) else (
        echo 📥 首次运行，正在安装前端依赖...
        npm install
        if errorlevel 1 (
            echo ❌ 前端依赖安装失败
            pause
            exit /b 1
        )
        npm run dev
    )
)

cd ..

echo.
echo ===================================
echo   ✅ 系统已启动！
echo   📍 访问地址: http://localhost:9527
echo   📍 后端API: http://localhost:9527/docs
echo ===================================
echo.
echo 按 Ctrl+C 停止服务...
pause
