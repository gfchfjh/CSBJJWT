@echo off
echo ========================================
echo KOOK消息转发系统 v2.0 - 安装脚本
echo ========================================
echo.

echo [1/3] 安装Python依赖...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: Python依赖安装失败
    pause
    exit /b 1
)
echo.

echo [2/3] 安装Playwright浏览器...
playwright install chromium
if errorlevel 1 (
    echo 警告: Playwright浏览器安装失败，某些功能可能不可用
)
echo.

echo [3/3] 安装前端依赖...
cd ../frontend
call npm install
if errorlevel 1 (
    echo 错误: 前端依赖安装失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动方式:
echo   后端: 运行 start_backend.bat
echo   前端: 运行 start_frontend.bat
echo.
pause
