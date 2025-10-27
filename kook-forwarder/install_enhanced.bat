@echo off
REM KOOK消息转发系统 - Windows增强安装脚本 v2.0
REM 自动下载并安装Python、Node.js、Git等依赖
REM 真正的一键安装体验

setlocal enabledelayedexpansion

:: 设置颜色
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

:: 临时下载目录
set "TEMP_DIR=%TEMP%\kook-forwarder-setup"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════╗%NC%
echo %BLUE%║                                                           ║%NC%
echo %BLUE%║   KOOK消息转发系统 - Windows增强安装脚本 v2.0            ║%NC%
echo %BLUE%║   自动下载并安装所有依赖                                  ║%NC%
echo %BLUE%║                                                           ║%NC%
echo %BLUE%╚═══════════════════════════════════════════════════════════╝%NC%
echo.

echo %YELLOW%此脚本将自动完成：%NC%
echo   ✅ 检测并安装 Python 3.11
echo   ✅ 检测并安装 Node.js 18 LTS
echo   ✅ 检测并安装 Git
echo   ✅ 下载并安装 Redis（可选）
echo   ✅ 克隆项目代码
echo   ✅ 安装所有依赖
echo   ✅ 下载 Chromium 浏览器
echo   ✅ 创建桌面快捷方式
echo.

set /p "CONFIRM=是否继续安装？ (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo %YELLOW%安装已取消%NC%
    exit /b 0
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 1/8: 检查管理员权限%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ 需要管理员权限%NC%
    echo.
    echo %YELLOW%请右键以管理员身份运行此脚本%NC%
    echo.
    pause
    exit /b 1
)

echo %GREEN%✅ 管理员权限检查通过%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 2/8: 检查并安装 Python%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo %GREEN%✅ Python已安装: !PYTHON_VERSION!%NC%
) else (
    echo %YELLOW%⚠️  Python未安装，开始自动安装...%NC%
    echo.
    
    :: 下载Python安装器
    set "PYTHON_INSTALLER=python-3.11.7-amd64.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/!PYTHON_INSTALLER!"
    
    echo %BLUE%ℹ️  下载Python 3.11.7...%NC%
    echo    下载地址: !PYTHON_URL!
    echo    保存位置: %TEMP_DIR%\!PYTHON_INSTALLER!
    echo.
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!PYTHON_URL!' -OutFile '%TEMP_DIR%\!PYTHON_INSTALLER!' -UseBasicParsing}"
    
    if !errorlevel! neq 0 (
        echo %RED%❌ Python下载失败%NC%
        echo.
        echo %YELLOW%请手动下载并安装：%NC%
        echo   1. 访问 https://www.python.org/downloads/
        echo   2. 下载 Python 3.11 或更高版本
        echo   3. 安装时勾选 "Add Python to PATH"
        echo   4. 重新运行此脚本
        echo.
        pause
        exit /b 1
    )
    
    echo %BLUE%ℹ️  安装Python（请稍候，约2-3分钟）...%NC%
    echo    ⚠️  安装过程中请勾选 "Add Python to PATH"
    echo.
    
    :: 静默安装Python
    "%TEMP_DIR%\!PYTHON_INSTALLER!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    if !errorlevel! neq 0 (
        echo %YELLOW%⚠️  静默安装失败，启动图形安装界面...%NC%
        "%TEMP_DIR%\!PYTHON_INSTALLER!"
        echo.
        echo %YELLOW%请完成Python安装后，按任意键继续...%NC%
        pause >nul
    ) else (
        echo %GREEN%✅ Python安装完成%NC%
    )
    
    :: 刷新环境变量
    echo %BLUE%ℹ️  刷新环境变量...%NC%
    call :RefreshEnv
    
    :: 再次检查
    python --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo %RED%❌ Python安装可能未成功，请检查%NC%
        echo.
        echo %YELLOW%故障排查：%NC%
        echo   1. 确认是否勾选了 "Add Python to PATH"
        echo   2. 重启命令提示符
        echo   3. 手动运行: python --version
        echo.
        pause
        exit /b 1
    )
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 3/8: 检查并安装 Node.js%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
    echo %GREEN%✅ Node.js已安装: !NODE_VERSION!%NC%
) else (
    echo %YELLOW%⚠️  Node.js未安装，开始自动安装...%NC%
    echo.
    
    :: 下载Node.js安装器
    set "NODE_INSTALLER=node-v18.19.0-x64.msi"
    set "NODE_URL=https://nodejs.org/dist/v18.19.0/!NODE_INSTALLER!"
    
    echo %BLUE%ℹ️  下载Node.js 18.19.0 LTS...%NC%
    echo    下载地址: !NODE_URL!
    echo    保存位置: %TEMP_DIR%\!NODE_INSTALLER!
    echo.
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!NODE_URL!' -OutFile '%TEMP_DIR%\!NODE_INSTALLER!' -UseBasicParsing}"
    
    if !errorlevel! neq 0 (
        echo %RED%❌ Node.js下载失败%NC%
        echo.
        echo %YELLOW%请手动下载并安装：%NC%
        echo   1. 访问 https://nodejs.org/
        echo   2. 下载 LTS 版本（推荐18.x）
        echo   3. 安装后重新运行此脚本
        echo.
        pause
        exit /b 1
    )
    
    echo %BLUE%ℹ️  安装Node.js（请稍候，约2-3分钟）...%NC%
    echo.
    
    :: 静默安装Node.js
    msiexec /i "%TEMP_DIR%\!NODE_INSTALLER!" /quiet /norestart
    
    if !errorlevel! neq 0 (
        echo %YELLOW%⚠️  静默安装失败，启动图形安装界面...%NC%
        msiexec /i "%TEMP_DIR%\!NODE_INSTALLER!"
        echo.
        echo %YELLOW%请完成Node.js安装后，按任意键继续...%NC%
        pause >nul
    ) else (
        echo %GREEN%✅ Node.js安装完成%NC%
    )
    
    :: 刷新环境变量
    call :RefreshEnv
    
    :: 再次检查
    node --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo %RED%❌ Node.js安装可能未成功，请检查%NC%
        pause
        exit /b 1
    )
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 4/8: 检查并安装 Git%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1-3" %%i in ('git --version') do set GIT_VERSION=%%k
    echo %GREEN%✅ Git已安装: !GIT_VERSION!%NC%
) else (
    echo %YELLOW%⚠️  Git未安装%NC%
    echo.
    echo %YELLOW%Git安装选项：%NC%
    echo   1. 自动下载安装（推荐）
    echo   2. 手动安装
    echo   3. 跳过（需手动下载项目代码）
    echo.
    
    set /p "GIT_CHOICE=请选择 (1/2/3): "
    
    if "!GIT_CHOICE!"=="1" (
        :: 下载Git安装器
        set "GIT_INSTALLER=Git-2.43.0-64-bit.exe"
        set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/!GIT_INSTALLER!"
        
        echo.
        echo %BLUE%ℹ️  下载Git 2.43.0...%NC%
        echo    下载地址: !GIT_URL!
        echo.
        
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!GIT_URL!' -OutFile '%TEMP_DIR%\!GIT_INSTALLER!' -UseBasicParsing}"
        
        if !errorlevel! neq 0 (
            echo %RED%❌ Git下载失败，将跳过Git安装%NC%
        ) else (
            echo %BLUE%ℹ️  安装Git...%NC%
            "%TEMP_DIR%\!GIT_INSTALLER!" /SILENT /NORESTART
            call :RefreshEnv
            echo %GREEN%✅ Git安装完成%NC%
        )
    ) else if "!GIT_CHOICE!"=="2" (
        echo.
        echo %YELLOW%请访问 https://git-scm.com/download/win 下载并安装Git%NC%
        echo 安装完成后，按任意键继续...
        pause >nul
    )
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 5/8: Redis安装（可选）%NC%
echo %BLUE%================================================%NC%
echo.

echo %BLUE%ℹ️  Redis选项：%NC%
echo   1. 下载安装Redis（推荐）
echo   2. 使用内置Redis（打包版本提供）
echo   3. 跳过（稍后使用Docker）
echo.

set /p "REDIS_CHOICE=请选择 (1/2/3，默认2): "
if "!REDIS_CHOICE!"=="" set "REDIS_CHOICE=2"

if "!REDIS_CHOICE!"=="1" (
    echo.
    echo %BLUE%ℹ️  下载Redis for Windows...%NC%
    set "REDIS_ZIP=Redis-x64-5.0.14.1.zip"
    set "REDIS_URL=https://github.com/tporadowski/redis/releases/download/v5.0.14.1/!REDIS_ZIP!"
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!REDIS_URL!' -OutFile '%TEMP_DIR%\!REDIS_ZIP!' -UseBasicParsing}"
    
    if !errorlevel! equ 0 (
        echo %BLUE%ℹ️  解压Redis...%NC%
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\!REDIS_ZIP!' -DestinationPath '%TEMP_DIR%\redis' -Force"
        
        :: 移动到项目redis目录
        if not exist "redis" mkdir redis
        xcopy /E /I /Y "%TEMP_DIR%\redis\*" "redis\"
        
        echo %GREEN%✅ Redis安装完成%NC%
    ) else (
        echo %YELLOW%⚠️  Redis下载失败，将使用内置版本%NC%
    )
) else if "!REDIS_CHOICE!"=="2" (
    echo %GREEN%✅ 将使用内置Redis%NC%
) else (
    echo %YELLOW%⚠️  已跳过Redis安装%NC%
)

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 6/8: 获取项目代码%NC%
echo %BLUE%================================================%NC%
echo.

:: 检查Git是否可用
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Git不可用，无法克隆项目%NC%
    echo.
    echo %YELLOW%请手动下载项目：%NC%
    echo   1. 访问 https://github.com/gfchfjh/CSBJJWT
    echo   2. 点击 "Code" → "Download ZIP"
    echo   3. 解压到当前目录
    echo   4. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

if exist "CSBJJWT" (
    echo %YELLOW%⚠️  项目目录已存在，更新代码...%NC%
    cd CSBJJWT
    git pull
) else (
    echo %BLUE%ℹ️  克隆项目仓库...%NC%
    git clone https://github.com/gfchfjh/CSBJJWT.git
    if !errorlevel! neq 0 (
        echo %RED%❌ 项目克隆失败%NC%
        echo.
        echo %YELLOW%请检查网络连接或手动下载项目%NC%
        pause
        exit /b 1
    )
    cd CSBJJWT
)

echo %GREEN%✅ 项目代码获取完成%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 7/8: 安装项目依赖%NC%
echo %BLUE%================================================%NC%
echo.

:: 创建Python虚拟环境
echo %BLUE%ℹ️  创建Python虚拟环境...%NC%
python -m venv venv

echo %BLUE%ℹ️  激活虚拟环境...%NC%
call venv\Scripts\activate.bat

echo %BLUE%ℹ️  升级pip...%NC%
python -m pip install --upgrade pip

echo %BLUE%ℹ️  安装Python依赖（这可能需要5-10分钟）...%NC%
cd backend
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo %RED%❌ Python依赖安装失败%NC%
    pause
    exit /b 1
)

echo %BLUE%ℹ️  下载Playwright Chromium浏览器...%NC%
playwright install chromium
if !errorlevel! neq 0 (
    echo %YELLOW%⚠️  Playwright浏览器下载失败，首次启动时会自动下载%NC%
)

cd ..

echo %BLUE%ℹ️  安装Node.js依赖（这可能需要3-5分钟）...%NC%
cd frontend
call npm install
if !errorlevel! neq 0 (
    echo %RED%❌ Node.js依赖安装失败%NC%
    pause
    exit /b 1
)

cd ..

echo %GREEN%✅ 所有依赖安装完成%NC%

echo.
echo %BLUE%================================================%NC%
echo %BLUE%步骤 8/8: 创建启动脚本和快捷方式%NC%
echo %BLUE%================================================%NC%
echo.

:: 创建启动脚本（已存在，跳过）
if exist "start.bat" (
    echo %GREEN%✅ 启动脚本已存在%NC%
) else (
    echo %BLUE%ℹ️  创建启动脚本...%NC%
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
    echo echo ✅ KOOK消息转发系统已启动
    echo echo.
    echo echo 后端服务: http://127.0.0.1:9527
    echo echo 前端界面: 将自动打开
    echo echo.
    echo pause
    ) > start.bat
    echo %GREEN%✅ 启动脚本创建完成%NC%
)

:: 创建桌面快捷方式
echo %BLUE%ℹ️  创建桌面快捷方式...%NC%

set "CURRENT_DIR=%CD%"
set "DESKTOP=%USERPROFILE%\Desktop"

:: 使用PowerShell创建快捷方式
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\KOOK消息转发.lnk'); $SC.TargetPath = '%CURRENT_DIR%\start.bat'; $SC.WorkingDirectory = '%CURRENT_DIR%'; $SC.Description = 'KOOK消息转发系统'; $SC.Save()"

if !errorlevel! equ 0 (
    echo %GREEN%✅ 桌面快捷方式创建完成%NC%
) else (
    echo %YELLOW%⚠️  快捷方式创建失败（不影响使用）%NC%
)

:: 创建配置文件
if not exist "backend\.env" (
    echo.
    echo %BLUE%ℹ️  创建默认配置文件...%NC%
    
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
)

:: 清理临时文件
echo.
echo %BLUE%ℹ️  清理临时文件...%NC%
rd /s /q "%TEMP_DIR%" 2>nul

:: 安装完成
echo.
echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════╗%NC%
echo %GREEN%║                                                           ║%NC%
echo %GREEN%║               🎉 安装完成！                               ║%NC%
echo %GREEN%║                                                           ║%NC%
echo %GREEN%╚═══════════════════════════════════════════════════════════╝%NC%
echo.
echo.
echo %GREEN%下一步操作：%NC%
echo   1. 双击桌面的 "KOOK消息转发" 快捷方式
echo      或双击项目目录的 start.bat
echo   2. 首次启动会打开配置向导
echo   3. 按照向导完成账号和Bot配置
echo.
echo %BLUE%快速启动：%NC%
echo   • 桌面快捷方式: 双击 "KOOK消息转发"
echo   • 命令行启动: cd CSBJJWT ^&^& start.bat
echo.
echo %BLUE%查看文档：%NC%
echo   • 快速开始: docs\快速开始指南.md
echo   • 用户手册: docs\用户手册.md
echo   • 视频教程: docs\视频教程\
echo.
echo %YELLOW%提示：%NC%
echo   • 需要准备KOOK账号Cookie
echo   • 至少配置一个Bot（Discord/Telegram/飞书）
echo   • 首次启动会自动打开配置向导
echo.
echo %GREEN%感谢使用KOOK消息转发系统！%NC%
echo.

:: 询问是否立即启动
set /p "START_NOW=是否立即启动系统？ (Y/N): "
if /i "!START_NOW!"=="Y" (
    echo.
    echo %BLUE%ℹ️  正在启动...%NC%
    start.bat
) else (
    echo.
    echo %YELLOW%您可以稍后双击桌面快捷方式或start.bat启动系统%NC%
)

pause
exit /b 0

:: ========== 辅助函数 ==========

:RefreshEnv
:: 刷新环境变量
echo %BLUE%ℹ️  刷新环境变量...%NC%
:: 从注册表读取最新的PATH
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SystemPath=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "UserPath=%%b"
set "PATH=%SystemPath%;%UserPath%"
goto :eof
