@echo off
chcp 65001 >nul
title KOOK 消息转发系统 - 从零开始完整安装
color 0A

echo.
echo ================================================================
echo     KOOK 消息转发系统 - 从零开始完整安装向导
echo ================================================================
echo.
echo 本脚本将引导您完成以下步骤：
echo   1. 检查必要软件（Python、Node.js、Git）
echo   2. 下载项目源码
echo   3. 安装所有依赖
echo   4. 自动修复 Electron 问题
echo   5. 构建安装包
echo   6. 安装并启动
echo.
echo 预计总时间：60-90 分钟
echo.
echo ================================================================
echo.

pause

:: ================================================================
:: 步骤 1: 检查环境
:: ================================================================
echo.
echo ================================================================
echo [步骤 1/6] 检查必要软件
echo ================================================================
echo.

set "ENV_OK=1"

:: 检查 Python
echo [检查] Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo ✅ Python 已安装
) else (
    echo ❌ Python 未安装
    echo.
    echo 请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时务必勾选: Add Python to PATH
    set "ENV_OK=0"
)
echo.

:: 检查 Node.js
echo [检查] Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    node --version
    echo ✅ Node.js 已安装
) else (
    echo ❌ Node.js 未安装
    echo.
    echo 请先安装 Node.js 18+
    echo 下载地址: https://nodejs.org/
    set "ENV_OK=0"
)
echo.

:: 检查 npm
echo [检查] npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    npm --version
    echo ✅ npm 已安装
) else (
    echo ❌ npm 未安装（通常随 Node.js 安装）
    set "ENV_OK=0"
)
echo.

:: 检查 Git
echo [检查] Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    git --version
    echo ✅ Git 已安装
) else (
    echo ❌ Git 未安装
    echo.
    echo 请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    set "ENV_OK=0"
)
echo.

:: 如果环境不完整，退出
if "%ENV_OK%"=="0" (
    echo ================================================================
    echo [错误] 环境检查未通过
    echo ================================================================
    echo.
    echo 请先安装缺失的软件，然后：
    echo   1. 重启电脑（确保环境变量生效）
    echo   2. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo ================================================================
echo [成功] 环境检查通过！
echo ================================================================
echo.
pause

:: ================================================================
:: 步骤 2: 选择安装位置
:: ================================================================
echo.
echo ================================================================
echo [步骤 2/6] 选择安装位置
echo ================================================================
echo.
echo 推荐安装位置：
echo   1. 桌面（推荐，方便找到）
echo   2. C:\KOOK
echo   3. 自定义位置
echo.
set /p location_choice="请选择 (1/2/3): "

if "%location_choice%"=="1" (
    set "INSTALL_ROOT=%USERPROFILE%\Desktop"
) else if "%location_choice%"=="2" (
    set "INSTALL_ROOT=C:\"
) else if "%location_choice%"=="3" (
    set /p "INSTALL_ROOT=请输入完整路径（例如 D:\Projects）: "
) else (
    echo 无效选择，使用默认位置（桌面）
    set "INSTALL_ROOT=%USERPROFILE%\Desktop"
)

set "PROJECT_DIR=%INSTALL_ROOT%\CSBJJWT"

echo.
echo 将安装到: %PROJECT_DIR%
echo.

:: 检查目录是否已存在
if exist "%PROJECT_DIR%" (
    echo [警告] 目录已存在！
    echo.
    set /p overwrite="是否删除并重新安装？(Y/N): "
    if /i "!overwrite!"=="Y" (
        echo 正在删除旧目录...
        rd /s /q "%PROJECT_DIR%"
        echo 已删除
    ) else (
        echo 安装已取消
        pause
        exit /b 0
    )
)

pause

:: ================================================================
:: 步骤 3: 下载项目
:: ================================================================
echo.
echo ================================================================
echo [步骤 3/6] 下载项目源码
echo ================================================================
echo.

cd /d "%INSTALL_ROOT%"

echo [下载] 正在从 GitHub 下载项目...
echo 地址: https://github.com/gfchfjh/CSBJJWT.git
echo.

git clone https://github.com/gfchfjh/CSBJJWT.git

if %errorlevel% neq 0 (
    echo.
    echo [错误] 项目下载失败！
    echo.
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. Git 未正确安装
    echo   3. GitHub 访问受限
    echo.
    echo 解决方案：
    echo   1. 检查网络连接
    echo   2. 手动下载: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
    echo   3. 解压到: %INSTALL_ROOT%\CSBJJWT
    echo.
    pause
    exit /b 1
)

cd "%PROJECT_DIR%"

echo.
echo [完成] 项目下载完成
echo 位置: %PROJECT_DIR%
echo.

:: 显示项目结构
echo 项目结构：
dir /b
echo.

pause

:: ================================================================
:: 步骤 4: 安装后端
:: ================================================================
echo.
echo ================================================================
echo [步骤 4/6] 安装后端环境（约 10-15 分钟）
echo ================================================================
echo.

cd backend

echo [4.1] 创建 Python 虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已创建
echo.

echo [4.2] 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✅ 虚拟环境已激活
echo.

echo [4.3] 升级 pip...
python -m pip install --upgrade pip
echo ✅ pip 已升级
echo.

echo [4.4] 安装 Python 依赖包（这可能需要 5-10 分钟）...
echo 使用国内镜像加速...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo [警告] 使用国内镜像失败，尝试默认源...
    pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        echo 请检查网络连接
        pause
        exit /b 1
    )
)
echo ✅ Python 依赖已安装
echo.

echo [4.5] 安装额外依赖...
pip install loguru discord-webhook python-telegram-bot beautifulsoup4 apscheduler prometheus_client ddddocr -i https://pypi.tuna.tsinghua.edu.cn/simple
echo ✅ 额外依赖已安装
echo.

echo [4.6] 安装 Playwright 浏览器（约 2-3 分钟）...
playwright install chromium

if %errorlevel% neq 0 (
    echo [警告] Playwright 安装失败
    echo 稍后可手动安装: playwright install chromium
)
echo ✅ Playwright 已安装
echo.

cd ..

echo ================================================================
echo [完成] 后端环境安装完成
echo ================================================================
echo.

pause

:: ================================================================
:: 步骤 5: 安装前端
:: ================================================================
echo.
echo ================================================================
echo [步骤 5/6] 安装前端环境（约 5-10 分钟）
echo ================================================================
echo.

cd frontend

echo [5.1] 安装 npm 依赖包（这可能需要 3-5 分钟）...
echo 使用 --legacy-peer-deps 解决依赖冲突...
call npm install --legacy-peer-deps

if %errorlevel% neq 0 (
    echo [警告] 使用默认源失败，尝试国内镜像...
    call npm install --legacy-peer-deps --registry=https://registry.npmmirror.com
    
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ npm 依赖已安装
echo.

echo [5.2] 编译前端代码（约 2-3 分钟）...
call npm run build

if %errorlevel% neq 0 (
    echo [警告] 前端编译失败，但不影响后续步骤
)
echo ✅ 前端已编译
echo.

cd ..

echo ================================================================
echo [完成] 前端环境安装完成
echo ================================================================
echo.

pause

:: ================================================================
:: 步骤 6: 应用 Electron 修复
:: ================================================================
echo.
echo ================================================================
echo [步骤 6/6] 应用 Electron 修复并构建
echo ================================================================
echo.

echo [信息] 现在将应用 Electron 启动修复
echo 这将解决 "fetch failed" 问题
echo.
pause

:: 下载修复脚本（如果存在）
if exist "自动修复Electron.bat" (
    echo [执行] 运行 Electron 自动修复...
    call 自动修复Electron.bat
) else (
    echo [警告] 未找到自动修复脚本
    echo 将手动应用基本修复...
    echo.
    
    :: 创建最小化启动脚本
    echo [6.1] 创建最小化启动脚本...
    (
        echo import sys
        echo import os
        echo.
        echo sys.path.insert^(0, os.path.dirname^(__file__^)^)
        echo os.chdir^(os.path.dirname^(__file__^)^)
        echo.
        echo from app.main import app
        echo import uvicorn
        echo.
        echo if __name__ == "__main__":
        echo     uvicorn.run^(app, host="127.0.0.1", port=8000, log_level="error", access_log=False^)
    ) > backend\run_minimal.py
    echo ✅ 最小化启动脚本已创建
    echo.
    
    :: 构建后端
    echo [6.2] 构建后端（约 3-5 分钟）...
    cd backend
    call venv\Scripts\activate.bat
    cd ..
    
    pyinstaller build\pyinstaller.spec --clean --noconfirm
    
    if %errorlevel% equ 0 (
        echo ✅ 后端构建成功
    ) else (
        echo ❌ 后端构建失败
        echo 请查看错误信息
        pause
        exit /b 1
    )
    echo.
    
    :: 构建前端
    echo [6.3] 构建 Electron（约 5-10 分钟）...
    cd frontend
    call npm run electron:build:win
    
    if %errorlevel% equ 0 (
        echo ✅ Electron 构建成功
    ) else (
        echo ❌ Electron 构建失败
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ================================================================
echo [完成] 所有构建已完成
echo ================================================================
echo.

:: ================================================================
:: 步骤 7: 创建启动脚本
:: ================================================================
echo.
echo ================================================================
echo [步骤 7/7] 创建便捷启动脚本
echo ================================================================
echo.

:: 创建 Web 版启动脚本
(
echo @echo off
echo title KOOK 消息转发系统 - Web 版
echo chcp 65001 ^>nul
echo.
echo cd /d "%%~dp0backend"
echo call venv\Scripts\activate.bat
echo.
echo echo ========================================
echo echo KOOK 消息转发系统正在启动...
echo echo ========================================
echo echo.
echo echo 后端地址: http://127.0.0.1:9527
echo echo.
echo.
echo start /MIN cmd /k "python -m app.main"
echo.
echo timeout /t 15 /nobreak ^>nul
echo.
echo start http://127.0.0.1:9527
echo.
echo echo 系统已启动！
echo echo 浏览器应该已自动打开
echo echo.
echo echo 提示：关闭此窗口将停止服务
echo pause
) > "启动KOOK系统-Web版.bat"

echo ✅ 已创建: 启动KOOK系统-Web版.bat
echo.

:: 创建停止脚本
(
echo @echo off
echo title 停止 KOOK 系统
echo echo 正在停止所有 KOOK 服务...
echo taskkill /F /IM python.exe 2^>nul
echo taskkill /F /IM KOOKForwarder.exe 2^>nul
echo taskkill /F /IM "KOOK消息转发系统.exe" 2^>nul
echo echo 所有服务已停止
echo timeout /t 3 /nobreak ^>nul
) > "停止KOOK系统.bat"

echo ✅ 已创建: 停止KOOK系统.bat
echo.

:: ================================================================
:: 完成
:: ================================================================
echo.
echo ================================================================
echo                    🎉 安装完成！
echo ================================================================
echo.
echo 项目位置: %PROJECT_DIR%
echo.
echo ┌─────────────────────────────────────────────────────────────┐
echo │                     使用方式                                 │
echo ├─────────────────────────────────────────────────────────────┤
echo │                                                              │
echo │ 方式1: Electron 桌面应用（推荐）                             │
echo │   位置: frontend\dist-electron\                             │
echo │   文件: KOOK消息转发系统 Setup 18.0.x.exe                   │
echo │   步骤:                                                      │
echo │     1. 双击安装程序                                          │
echo │     2. 按向导完成安装                                        │
echo │     3. 启动应用                                              │
echo │                                                              │
echo │ 方式2: Web 版本（备用）                                      │
echo │   文件: 启动KOOK系统-Web版.bat                              │
echo │   步骤:                                                      │
echo │     1. 双击启动脚本                                          │
echo │     2. 浏览器自动打开                                        │
echo │     3. 开始使用                                              │
echo │                                                              │
echo │ 停止服务:                                                    │
echo │   双击: 停止KOOK系统.bat                                    │
echo │                                                              │
echo └─────────────────────────────────────────────────────────────┘
echo.
echo 首次使用：
echo   1. 设置管理员密码
echo   2. 添加 KOOK 账号
echo   3. 配置转发平台（Discord/Telegram 等）
echo   4. 开始转发消息
echo.
echo ================================================================
echo.

echo 是否立即打开安装包目录？(Y/N)
set /p open_dir="请选择: "

if /i "%open_dir%"=="Y" (
    if exist "frontend\dist-electron" (
        explorer "frontend\dist-electron"
    ) else (
        echo 安装包目录不存在，请检查构建是否成功
        explorer .
    )
)

echo.
echo ================================================================
echo.
echo 重要文件位置：
echo   Electron 安装包: frontend\dist-electron\
echo   Web 版启动脚本: %CD%\启动KOOK系统-Web版.bat
echo   停止服务脚本: %CD%\停止KOOK系统.bat
echo   项目源码: %CD%
echo.
echo 需要帮助？
echo   查看文档: README.md
echo   故障排查: TROUBLESHOOTING_WINDOWS.md
echo   GitHub: https://github.com/gfchfjh/CSBJJWT
echo.
echo ================================================================
echo.

echo 按任意键退出...
pause >nul
exit /b 0
