@echo off
chcp 65001 >nul
title KOOK 消息转发系统 - 自动安装脚本
color 0A

echo.
echo ================================================================
echo            KOOK 消息转发系统 - 自动安装程序
echo ================================================================
echo.
echo 本脚本将自动完成以下操作：
echo   1. 下载项目源码
echo   2. 安装后端环境
echo   3. 安装前端环境  
echo   4. 创建启动脚本
echo.
echo 预计时间：15-20 分钟
echo.
echo ================================================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 建议以管理员身份运行此脚本
    echo.
    pause
)

:: 检查必要软件
echo [检查环境] 检查必要软件是否已安装...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo 请先安装 Python 3.11+ : https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js！
    echo 请先安装 Node.js 18+ : https://nodejs.org/
    pause
    exit /b 1
)

git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git！
    echo 请先安装 Git : https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [成功] 环境检查通过！
python --version
node --version
git --version
echo.

:: 选择安装目录
echo [配置] 选择安装位置
echo.
echo 1. 安装到桌面（推荐）
echo 2. 安装到当前目录
echo.
set /p choice="请选择 (1 或 2): "

if "%choice%"=="1" (
    set "INSTALL_DIR=%USERPROFILE%\Desktop\CSBJJWT"
) else (
    set "INSTALL_DIR=%CD%\CSBJJWT"
)

echo.
echo 将安装到: %INSTALL_DIR%
echo.
pause

:: 检查目录是否已存在
if exist "%INSTALL_DIR%" (
    echo [警告] 目录已存在！
    echo.
    echo 1. 删除旧版本重新安装
    echo 2. 取消安装
    echo.
    set /p overwrite="请选择 (1 或 2): "
    
    if "!overwrite!"=="1" (
        echo [操作] 正在删除旧版本...
        rd /s /q "%INSTALL_DIR%"
        echo [完成] 旧版本已删除
        echo.
    ) else (
        echo [取消] 安装已取消
        pause
        exit /b 0
    )
)

:: 下载项目
echo.
echo ================================================================
echo [步骤 1/4] 下载项目源码
echo ================================================================
echo.

cd /d "%INSTALL_DIR%\.."
git clone https://github.com/gfchfjh/CSBJJWT.git
if %errorlevel% neq 0 (
    echo [错误] 项目下载失败！
    echo 请检查网络连接或手动下载：
    echo https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
    pause
    exit /b 1
)

cd "%INSTALL_DIR%"
echo [完成] 项目下载完成
echo.

:: 安装后端
echo.
echo ================================================================
echo [步骤 2/4] 安装后端环境
echo ================================================================
echo.

cd backend
echo [2.1] 创建 Python 虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境创建失败！
    pause
    exit /b 1
)

echo [2.2] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2.3] 升级 pip...
python -m pip install --upgrade pip

echo [2.4] 安装 Python 依赖包（这可能需要 5-10 分钟）...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [警告] 使用国内镜像失败，尝试默认源...
    pip install -r requirements.txt
)

echo [2.5] 安装 Playwright 浏览器（这可能需要 2-3 分钟）...
playwright install chromium
if %errorlevel% neq 0 (
    echo [警告] Playwright 安装失败，稍后可手动安装
)

cd ..
echo [完成] 后端环境安装完成
echo.

:: 安装前端
echo.
echo ================================================================
echo [步骤 3/4] 安装前端环境
echo ================================================================
echo.

cd frontend
echo [3.1] 安装 npm 依赖包（这可能需要 3-5 分钟）...
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo [警告] 使用默认源失败，尝试国内镜像...
    call npm install --legacy-peer-deps --registry=https://registry.npmmirror.com
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败！
        pause
        exit /b 1
    )
)

echo [3.2] 编译前端代码（这可能需要 2-3 分钟）...
call npm run build
if %errorlevel% neq 0 (
    echo [警告] 前端编译失败，但不影响使用
)

cd ..
echo [完成] 前端环境安装完成
echo.

:: 创建启动脚本
echo.
echo ================================================================
echo [步骤 4/4] 创建启动脚本
echo ================================================================
echo.

(
echo @echo off
echo title KOOK 消息转发系统
echo chcp 65001 ^>nul
echo.
echo echo ========================================
echo echo KOOK 消息转发系统正在启动...
echo echo ========================================
echo echo.
echo.
echo cd /d "%%~dp0backend"
echo call venv\Scripts\activate.bat
echo.
echo echo [1/2] 正在启动后端服务...
echo echo 后端地址: http://127.0.0.1:9527
echo echo API文档: http://127.0.0.1:9527/docs
echo echo.
echo.
echo start /MIN cmd /k "python -m app.main"
echo.
echo echo [2/2] 等待后端启动（15秒）...
echo timeout /t 15 /nobreak ^>nul
echo.
echo echo ========================================
echo echo 启动完成！正在打开浏览器...
echo echo ========================================
echo echo.
echo.
echo start http://127.0.0.1:9527
echo.
echo echo 提示：
echo echo - 关闭黑色窗口将停止服务
echo echo - 如果浏览器未自动打开，请手动访问: http://127.0.0.1:9527
echo echo.
echo pause
) > "启动KOOK系统.bat"

echo [完成] 启动脚本已创建
echo.

:: 创建停止脚本
(
echo @echo off
echo title 停止 KOOK 系统
echo echo 正在停止 KOOK 消息转发系统...
echo taskkill /F /IM python.exe 2^>nul
echo echo 系统已停止
echo timeout /t 3 /nobreak ^>nul
) > "停止KOOK系统.bat"

echo [完成] 停止脚本已创建
echo.

:: 完成
echo.
echo ================================================================
echo                    安装完成！
echo ================================================================
echo.
echo 安装位置: %INSTALL_DIR%
echo.
echo 下一步操作：
echo   1. 双击 "启动KOOK系统.bat" 启动服务
echo   2. 浏览器会自动打开 http://127.0.0.1:9527
echo   3. 首次使用需要设置管理员密码
echo   4. 按照向导完成配置
echo.
echo 停止服务：
echo   - 双击 "停止KOOK系统.bat"
echo   - 或关闭后端命令行窗口
echo.
echo 重要文件：
echo   启动KOOK系统.bat  - 启动脚本
echo   停止KOOK系统.bat  - 停止脚本
echo.
echo ================================================================
echo.

echo 是否立即启动系统？(Y/N)
set /p start_now="请选择: "

if /i "%start_now%"=="Y" (
    echo.
    echo 正在启动...
    start "" "%INSTALL_DIR%\启动KOOK系统.bat"
) else (
    echo.
    echo 您可以随时双击 "启动KOOK系统.bat" 启动服务
)

echo.
echo 按任意键退出安装程序...
pause >nul
exit /b 0
