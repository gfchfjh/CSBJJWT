@echo off
chcp 65001 >nul
title KOOK转发系统 - 后端服务
color 0A

echo ========================================
echo   KOOK消息转发系统 - 后端启动脚本
echo   版本: v18.0.4+
echo ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %cd%
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在！
    echo 请先运行 install.bat 安装环境
    pause
    exit /b 1
)

echo [1/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境激活失败！
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活
echo.

echo [2/4] 检查数据目录...
if not exist "%USERPROFILE%\Documents\KookForwarder\data" (
    echo 创建数据目录...
    mkdir "%USERPROFILE%\Documents\KookForwarder\data"
)
echo ✅ 数据目录: %USERPROFILE%\Documents\KookForwarder\data
echo.

echo [3/4] 检查后端代码...
if not exist "backend\app\main.py" (
    echo [错误] 找不到后端代码！
    pause
    exit /b 1
)
echo ✅ 后端代码存在
echo.

echo [4/4] 启动后端服务...
echo ----------------------------------------
echo 服务地址: http://localhost:9527
echo API文档: http://localhost:9527/docs
echo 健康检查: http://localhost:9527/health
echo ----------------------------------------
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload

pause
