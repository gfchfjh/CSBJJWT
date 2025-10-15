@echo off
REM 完整打包脚本 - Windows

setlocal enabledelayedexpansion

echo ======================================
echo KOOK消息转发系统 - 完整打包工具
echo ======================================
echo.

REM 项目根目录
cd /d %~dp0\..

REM 1. 打包后端
echo 📦 步骤1/3: 打包Python后端...
echo.
python build\build_backend.py
if errorlevel 1 (
    echo ❌ 后端打包失败
    exit /b 1
)
echo.

REM 2. 打包前端
echo 📦 步骤2/3: 打包Electron前端...
echo.
cd frontend
call npm install
call npm run build
call npm run electron:build
if errorlevel 1 (
    echo ❌ 前端打包失败
    exit /b 1
)
cd ..
echo.

REM 3. 整合打包
echo 📦 步骤3/3: 整合最终安装包...
echo.

REM 复制后端到前端dist目录
if not exist "frontend\dist\backend" mkdir "frontend\dist\backend"
xcopy /E /I /Y "dist\backend\*" "frontend\dist\backend\"

REM 如果有Redis，也复制进去
if exist "redis" (
    if not exist "frontend\dist\redis" mkdir "frontend\dist\redis"
    xcopy /E /I /Y "redis\*" "frontend\dist\redis\"
)

echo.
echo ======================================
echo 🎉 打包完成！
echo ======================================
echo 安装包位置：
echo   - Windows: frontend\dist\*.exe
echo ======================================

endlocal
