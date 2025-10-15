@echo off
REM KOOK消息转发系统 - Windows启动脚本
title KOOK消息转发系统

echo.
echo ========================================
echo   KOOK消息转发系统
echo   版本: 1.0.0
echo ========================================
echo.

REM 获取脚本所在目录
set PROJECT_DIR=%~dp0

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境！
    echo 请先安装Python 3.11或更高版本
    pause
    exit /b 1
)

REM 检查Redis
if not exist "%PROJECT_DIR%redis\redis-server.exe" (
    echo [警告] Redis未安装！
    echo 请参考 redis/README.md 下载Redis
    echo.
    choice /C YN /M "是否继续启动（不含Redis）"
    if errorlevel 2 exit /b 0
) else (
    echo [1/4] 启动Redis服务器...
    start "Redis服务器" /MIN cmd /c "%PROJECT_DIR%redis\start_redis.bat"
    timeout /t 2 /nobreak >nul
)

echo [2/4] 启动后端服务...
cd /d "%PROJECT_DIR%backend"
start "后端服务" cmd /k python -m app.main

echo [3/4] 等待后端启动...
timeout /t 3 /nobreak >nul

echo [4/4] 启动前端界面...
cd /d "%PROJECT_DIR%frontend"

REM 检查Node.js
where npm >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js环境！
    echo 请先安装Node.js
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules" (
    echo 首次运行，安装依赖...
    call npm install
)

echo 启动前端...
start "前端界面" cmd /k npm run dev

echo.
echo ========================================
echo ✅ 所有服务已启动！
echo.
echo 📝 访问地址: http://localhost:5173
echo 📊 后端API: http://localhost:9527
echo 🖼️  图床服务: http://localhost:9528
echo.
echo 按任意键打开浏览器...
echo ========================================
pause >nul

start http://localhost:5173

exit /b 0
