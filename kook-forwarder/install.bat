@echo off
REM KOOK消息转发系统 - 一键安装脚本（Windows）
REM 自动安装所有依赖和配置环境

setlocal enabledelayedexpansion

:: 设置颜色（Windows 10+）
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

:: 打印函数
echo.
echo %BLUE%╔═══════════════════════════════════════════════╗%NC%
echo %BLUE%║                                               ║%NC%
echo %BLUE%║   KOOK消息转发系统 - 一键安装脚本 v1.0       ║%NC%
echo %BLUE%║                                               ║%NC%
echo %BLUE%╚═══════════════════════════════════════════════╝%NC%
echo.

echo %YELLOW%此脚本将安装以下组件：%NC%
echo   • Python 3.11+ 及依赖
echo   • Node.js 18+ 及npm
echo   • Redis服务器
echo   • Playwright浏览器
echo   • 项目依赖包
echo.

set /p "CONFIRM=是否继续安装？ (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo %YELLOW%安装已取消%NC%
    exit /b 0
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 1/6: 检查Python环境%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 未检测到Python%NC%
    echo.
    echo 请先安装Python 3.11+:
    echo   1. 访问 https://www.python.org/downloads/
    echo   2. 下载Python 3.11或更高版本
    echo   3. 安装时勾选 "Add Python to PATH"
    echo   4. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %GREEN%✅ Python已安装: %PYTHON_VERSION%%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 2/6: 检查Node.js环境%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ 未检测到Node.js%NC%
    echo.
    echo 请先安装Node.js 18+:
    echo   1. 访问 https://nodejs.org/
    echo   2. 下载LTS版本（推荐18.x或20.x）
    echo   3. 安装后重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo %GREEN%✅ Node.js已安装: %NODE_VERSION%%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 3/6: 检查Redis环境%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Redis
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️  Redis未安装%NC%
    echo.
    echo Redis安装选项:
    echo   1. 手动安装: https://github.com/tporadowski/redis/releases
    echo   2. 使用Docker: docker-compose up -d redis
    echo   3. 使用内置Redis（打包版本提供）
    echo.
    echo 继续安装，但启动时需要确保Redis可用
    echo.
) else (
    for /f "tokens=1-3" %%i in ('redis-server --version') do set REDIS_VERSION=%%j
    echo %GREEN%✅ Redis已安装: %REDIS_VERSION%%NC%
)

pause

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 4/6: 获取项目代码%NC%
echo %BLUE%================================================%NC%
echo.

if exist "CSBJJWT" (
    echo %YELLOW%⚠️  项目目录已存在，更新代码...%NC%
    cd CSBJJWT
    git pull
) else (
    echo %BLUE%ℹ️  克隆项目仓库...%NC%
    git clone https://github.com/gfchfjh/CSBJJWT.git
    if errorlevel 1 (
        echo %RED%❌ 项目克隆失败%NC%
        echo.
        echo 请检查：
        echo   1. 网络连接是否正常
        echo   2. Git是否已安装
        echo   3. 手动下载: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
        echo.
        pause
        exit /b 1
    )
    cd CSBJJWT
)

echo %GREEN%✅ 项目代码获取完成%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 5/6: 安装Python依赖%NC%
echo %BLUE%================================================%NC%
echo.

echo %BLUE%ℹ️  创建Python虚拟环境...%NC%
python -m venv venv

echo %BLUE%ℹ️  激活虚拟环境...%NC%
call venv\Scripts\activate.bat

echo %BLUE%ℹ️  升级pip...%NC%
python -m pip install --upgrade pip

echo %BLUE%ℹ️  安装Python依赖包...%NC%
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%❌ Python依赖安装失败%NC%
    pause
    exit /b 1
)

echo %BLUE%ℹ️  安装Playwright浏览器...%NC%
playwright install chromium
if errorlevel 1 (
    echo %YELLOW%⚠️  Playwright浏览器安装失败，首次启动时会自动下载%NC%
)

cd ..
echo %GREEN%✅ Python依赖安装完成%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 6/6: 安装前端依赖%NC%
echo %BLUE%================================================%NC%
echo.

cd frontend
echo %BLUE%ℹ️  安装npm依赖...%NC%
call npm install
if errorlevel 1 (
    echo %RED%❌ 前端依赖安装失败%NC%
    pause
    exit /b 1
)

cd ..
echo %GREEN%✅ 前端依赖安装完成%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%创建启动脚本%NC%
echo %BLUE%================================================%NC%
echo.

:: 创建启动脚本
(
echo @echo off
echo REM KOOK消息转发系统 - 启动脚本
echo.
echo echo 启动KOOK消息转发系统...
echo.
echo REM 激活Python虚拟环境
echo call venv\Scripts\activate.bat
echo.
echo REM 启动后端服务
echo start "KOOK-Backend" cmd /k "cd backend && python -m app.main"
echo.
echo REM 等待后端启动
echo timeout /t 3 /nobreak ^> nul
echo.
echo REM 启动前端服务
echo start "KOOK-Frontend" cmd /k "cd frontend && npm run electron:dev"
echo.
echo echo.
echo echo %GREEN%✅ KOOK消息转发系统已启动%NC%
echo echo.
echo echo 后端服务: http://127.0.0.1:9527
echo echo 前端界面: 将自动打开
echo echo.
echo echo 关闭窗口即可停止服务
echo pause
) > start.bat

echo %GREEN%✅ 启动脚本创建完成%NC%

:: 创建配置文件
if not exist "backend\.env" (
    echo.
    echo %BLUE%================================================%NC%
    echo %BLUE%创建配置文件%NC%
    echo %BLUE%================================================%NC%
    echo.
    
    (
    echo # KOOK消息转发系统配置文件
    echo.
    echo # API服务
    echo API_HOST=127.0.0.1
    echo API_PORT=9527
    echo.
    echo # Redis配置
    echo REDIS_HOST=127.0.0.1
    echo REDIS_PORT=6379
    echo.
    echo # 日志级别
    echo LOG_LEVEL=INFO
    echo.
    echo # 图床配置
    echo IMAGE_MAX_SIZE_GB=10
    echo IMAGE_CLEANUP_DAYS=7
    echo.
    echo # 验证码识别（可选）
    echo # CAPTCHA_2CAPTCHA_API_KEY=your_api_key_here
    ) > backend\.env
    
    echo %GREEN%✅ 配置文件已创建: backend\.env%NC%
) else (
    echo %YELLOW%⚠️  配置文件已存在，跳过%NC%
)

:: 安装完成
echo.
echo.
echo %GREEN%╔═══════════════════════════════════════════════╗%NC%
echo %GREEN%║                                               ║%NC%
echo %GREEN%║          🎉 安装完成！                        ║%NC%
echo %GREEN%║                                               ║%NC%
echo %GREEN%╚═══════════════════════════════════════════════╝%NC%
echo.
echo.
echo %GREEN%下一步操作：%NC%
echo   1. 确保Redis正在运行（或使用Docker）
echo   2. 双击 start.bat 启动服务
echo   3. 首次启动会打开配置向导
echo.
echo %BLUE%查看文档：%NC%
echo   • 用户手册: docs\完整用户手册.md
echo   • 视频教程: docs\视频教程指南.md
echo   • 故障排查: README.md
echo.
echo %YELLOW%提示：%NC%
echo   • 首次启动会打开配置向导
echo   • 需要准备KOOK账号Cookie
echo   • 配置至少一个转发Bot（Discord/Telegram/飞书）
echo.
echo %GREEN%感谢使用KOOK消息转发系统！%NC%
echo.
pause
