@echo off
chcp 65001 >nul
title KOOK转发系统 - 前端服务
color 0B

echo ========================================
echo   KOOK消息转发系统 - 前端启动脚本
echo   版本: v18.0.4+
echo ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %cd%
echo.

echo [1/3] 检查Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Node.js未安装或不在PATH中！
    echo 请先安装 Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js版本:
node --version
echo.

echo [2/3] 检查前端代码...
if not exist "frontend\package.json" (
    echo [错误] 找不到前端代码！
    pause
    exit /b 1
)
echo ✅ 前端代码存在
echo.

echo [3/3] 启动前端服务...
echo ----------------------------------------
echo 前端地址: http://localhost:5173
echo ----------------------------------------
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

cd frontend
npm run dev

pause
