@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title KOOK消息转发系统 - 一键安装构建工具

:: ═══════════════════════════════════════════════════════════════
:: KOOK消息转发系统 - 一键安装构建脚本
:: 版本: 2.0
:: 功能: 自动下载源码、修复问题、构建完整安装包
:: ═══════════════════════════════════════════════════════════════

color 0B
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║      KOOK 消息转发系统 - 一键安装构建工具               ║
echo ║                                                          ║
echo ║      Version 2.0                                         ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0E
    echo ⚠️  警告：建议以管理员身份运行
    echo.
    echo 右键点击此脚本 → 选择"以管理员身份运行"
    echo.
    echo 是否继续？ (Y/N)
    choice /c YN /n /m "请选择: "
    if errorlevel 2 exit /b 1
)

echo ═══════════════════════════════════════════════════════════════
echo  第1步：环境检查
echo ═══════════════════════════════════════════════════════════════
echo.

set "ENV_OK=1"

echo [检查1] Python 3.11+
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [✗] Python 未安装
    echo     请先安装 Python 3.11+: https://www.python.org/downloads/
    set "ENV_OK=0"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [✓] Python %%i
    )
)

echo [检查2] Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [✗] Node.js 未安装
    echo     请先安装 Node.js 18+: https://nodejs.org/
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do (
        echo [✓] Node.js %%i
    )
)

echo [检查3] npm
npm --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [✗] npm 未安装
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do (
        echo [✓] npm %%i
    )
)

echo [检查4] Git
git --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [?] Git 未安装（将使用备用下载方式）
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do (
        echo [✓] Git %%i
    )
)

if "%ENV_OK%"=="0" (
    echo.
    color 0C
    echo ════════════════════════════════════════════════════════════
    echo  ❌ 环境检查失败
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 请安装缺失的软件后重试。
    pause
    exit /b 1
)

echo.
color 0A
echo ✅ 环境检查通过！
echo.
timeout /t 2 >nul

:: 设置工作目录
set "WORK_DIR=%USERPROFILE%\KOOK-Build"
set "SOURCE_DIR=%WORK_DIR%\CSBJJWT"

echo ═══════════════════════════════════════════════════════════════
echo  第2步：准备工作目录
echo ═══════════════════════════════════════════════════════════════
echo.
echo 工作目录: %WORK_DIR%
echo.

if exist "%WORK_DIR%" (
    echo 检测到已存在的工作目录。
    echo.
    echo 选项:
    echo   [1] 删除旧文件，重新开始（推荐）
    echo   [2] 继续使用现有文件
    echo   [3] 退出
    echo.
    choice /c 123 /n /m "请选择 (1-3): "
    
    if errorlevel 3 exit /b 0
    if errorlevel 2 goto :skip_clean
    if errorlevel 1 (
        echo.
        echo 正在清理旧文件...
        rd /s /q "%WORK_DIR%" 2>nul
        timeout /t 1 >nul
    )
)

:skip_clean
if not exist "%WORK_DIR%" (
    echo 创建工作目录...
    mkdir "%WORK_DIR%"
)
cd /d "%WORK_DIR%"
echo [✓] 工作目录准备完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第3步：下载源代码
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "%SOURCE_DIR%" (
    echo [✓] 源代码已存在，跳过下载
) else (
    git --version >nul 2>&1
    if errorlevel 1 (
        echo 未检测到 Git，正在使用备用方式下载...
        echo.
        echo 请手动执行以下操作:
        echo   1. 访问: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
        echo   2. 下载并解压到: %WORK_DIR%
        echo   3. 确保解压后的文件夹名为: CSBJJWT
        echo.
        pause
    ) else (
        echo 正在从 GitHub 克隆源代码...
        echo 仓库: https://github.com/gfchfjh/CSBJJWT.git
        echo.
        git clone https://github.com/gfchfjh/CSBJJWT.git
        if errorlevel 1 (
            color 0C
            echo.
            echo [✗] 克隆失败
            echo.
            echo 可能的原因:
            echo   - 网络连接问题
            echo   - GitHub 访问受限
            echo.
            echo 解决方案:
            echo   1. 检查网络连接
            echo   2. 或手动下载: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
            echo   3. 解压到: %WORK_DIR%\CSBJJWT
            echo.
            pause
            exit /b 1
        )
    )
)

if not exist "%SOURCE_DIR%" (
    color 0C
    echo [✗] 源代码目录不存在
    pause
    exit /b 1
)

cd /d "%SOURCE_DIR%"
echo [✓] 源代码准备完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第4步：应用修复补丁
echo ═══════════════════════════════════════════════════════════════
echo.
echo 正在修复 PyInstaller 配置...

python -c "import os; file='build/pyinstaller.spec'; content=open(file,encoding='utf-8').read(); content=content.replace(\"name='kook-forwarder-backend'\",\"name='KOOKForwarder'\"); open(file,'w',encoding='utf-8').write(content)"

if errorlevel 1 (
    color 0E
    echo [!] 自动修复失败，尝试手动修复...
    
    if exist "build\pyinstaller.spec" (
        echo 请手动编辑 build\pyinstaller.spec
        echo 将所有 name='kook-forwarder-backend' 改为 name='KOOKForwarder'
        pause
    ) else (
        echo [✗] 找不到 pyinstaller.spec 文件
        pause
        exit /b 1
    )
) else (
    echo [✓] PyInstaller 配置已修复
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第5步：安装 Python 依赖
echo ═══════════════════════════════════════════════════════════════
echo.
echo 这可能需要 5-10 分钟...
echo.

cd /d "%SOURCE_DIR%\backend"

if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo [✗] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

if errorlevel 1 (
    color 0C
    echo [✗] 依赖安装失败
    pause
    exit /b 1
)

echo [✓] Python 依赖安装完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第6步：构建后端可执行文件
echo ═══════════════════════════════════════════════════════════════
echo.
echo 这可能需要 5-10 分钟...
echo.

cd /d "%SOURCE_DIR%"

if exist "dist\KOOKForwarder" (
    echo 清理旧的构建文件...
    rd /s /q "dist\KOOKForwarder" 2>nul
)

echo 正在使用 PyInstaller 打包后端...
pyinstaller build\pyinstaller.spec --clean

if errorlevel 1 (
    color 0C
    echo [✗] 后端打包失败
    pause
    exit /b 1
)

if not exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    color 0C
    echo [✗] 后端可执行文件生成失败
    pause
    exit /b 1
)

echo [✓] 后端构建完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第7步：安装前端依赖
echo ═══════════════════════════════════════════════════════════════
echo.
echo 这可能需要 5-10 分钟...
echo.

cd /d "%SOURCE_DIR%\frontend"

if not exist "node_modules" (
    echo 正在安装 Node.js 依赖...
    call npm install
    if errorlevel 1 (
        color 0C
        echo [✗] 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [✓] 前端依赖已存在
)

echo [✓] 前端依赖安装完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第8步：构建 Electron 应用
echo ═══════════════════════════════════════════════════════════════
echo.
echo 这可能需要 5-15 分钟...
echo.

echo 正在构建 Windows 安装包...
call npm run electron:build:win

if errorlevel 1 (
    color 0C
    echo [✗] Electron 打包失败
    pause
    exit /b 1
)

echo [✓] Electron 应用构建完成
echo.

echo ═══════════════════════════════════════════════════════════════
echo  第9步：查找安装包
echo ═══════════════════════════════════════════════════════════════
echo.

cd /d "%SOURCE_DIR%"

:: 查找生成的安装包
set "INSTALLER_FOUND=0"
set "INSTALLER_PATH="

if exist "dist\*.exe" (
    for %%F in (dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

if exist "frontend\dist\*.exe" (
    for %%F in (frontend\dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

if exist "dist_electron\*.exe" (
    for %%F in (dist_electron\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

:found_installer

if "%INSTALLER_FOUND%"=="1" (
    echo [✓] 找到安装包
    echo.
    echo 安装包位置:
    echo %INSTALLER_PATH%
    echo.
    
    :: 复制到桌面
    echo 正在复制安装包到桌面...
    copy "%INSTALLER_PATH%" "%USERPROFILE%\Desktop\" >nul
    if errorlevel 1 (
        echo [!] 无法复制到桌面，但文件在上述路径可用
    ) else (
        echo [✓] 安装包已复制到桌面
    )
) else (
    color 0E
    echo [!] 未找到安装包
    echo     请在以下目录手动查找 .exe 文件:
    echo     - %SOURCE_DIR%\dist
    echo     - %SOURCE_DIR%\frontend\dist
    echo     - %SOURCE_DIR%\dist_electron
)

echo.
echo ═══════════════════════════════════════════════════════════════
color 0A
echo.
echo   ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗
echo   ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝
echo   ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗
echo   ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║
echo   ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║
echo   ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo  🎉 构建完成！
echo.
echo  📦 安装包已准备就绪
echo  📂 位置: %INSTALLER_PATH%
echo  🖥️  桌面上也有一份副本
echo.
echo  下一步：
echo    1. 双击安装包进行安装
echo    2. 按照安装向导完成安装
echo    3. 启动 KOOK 消息转发系统
echo    4. 首次使用请参考用户手册配置
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: 询问是否打开文件位置
echo 是否打开安装包所在文件夹？ (Y/N)
choice /c YN /n /m "请选择: "
if errorlevel 2 goto :end
if errorlevel 1 (
    if "%INSTALLER_FOUND%"=="1" (
        explorer /select,"%INSTALLER_PATH%"
    ) else (
        explorer "%SOURCE_DIR%\dist"
    )
)

:end
echo.
echo 感谢使用！
echo.
pause
exit /b 0
