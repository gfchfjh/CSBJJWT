@echo off
chcp 65001 >nul
echo ========================================
echo KOOK消息转发系统 - 自动修复工具 v1.0
echo ========================================
echo.
echo 本工具将尝试修复"后端服务未找到"的问题
echo.
pause

:: 设置变量
set "INSTALL_DIR=%LOCALAPPDATA%\Programs"
set "APP_NAME=kook-forwarder-frontend"

echo.
echo [步骤1] 正在搜索安装目录...
echo.

:: 搜索可能的安装路径
for /d %%d in ("%INSTALL_DIR%\*") do (
    echo 检查: %%d
    if exist "%%d\KOOK消息转发系统.exe" (
        set "FOUND_DIR=%%d"
        goto :found
    )
    if exist "%%d\resources" (
        set "FOUND_DIR=%%d"
        goto :found
    )
)

:found
if "%FOUND_DIR%"=="" (
    echo.
    echo [错误] 未找到安装目录！
    echo.
    echo 请手动输入完整安装路径（从错误信息中复制）：
    echo 例如: C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend
    echo.
    set /p "FOUND_DIR=输入路径: "
    
    if not exist "%FOUND_DIR%" (
        echo.
        echo [错误] 输入的路径不存在: %FOUND_DIR%
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [成功] 找到安装目录: %FOUND_DIR%
echo.

:: 设置关键路径
set "RESOURCES=%FOUND_DIR%\resources"
if not exist "%RESOURCES%" (
    set "RESOURCES=%FOUND_DIR%"
)

set "BACKEND=%RESOURCES%\backend"

echo [步骤2] 正在搜索后端文件...
echo.

:: 查找所有exe文件
set "FOUND_BACKEND="
set "BACKEND_DIR="

for /r "%BACKEND%" %%f in (*.exe) do (
    set "FILENAME=%%~nxf"
    echo 找到: %%f
    
    if /i "!FILENAME!"=="kook-forwarder-backend.exe" (
        set "FOUND_BACKEND=%%f"
        set "BACKEND_DIR=%%~dpf"
        echo [匹配] 这是后端文件！
    )
    if /i "!FILENAME!"=="KOOKForwarder.exe" (
        set "FOUND_BACKEND=%%f"
        set "BACKEND_DIR=%%~dpf"
        echo [匹配] 这是后端文件！
    )
)

if "%FOUND_BACKEND%"=="" (
    echo.
    echo [错误] 未找到后端可执行文件！
    echo.
    echo ========================================
    echo 可能的原因：
    echo ========================================
    echo 1. 安装包不完整（下载时损坏）
    echo 2. 杀毒软件删除了exe文件
    echo 3. 解压不完整
    echo.
    echo ========================================
    echo 建议解决方案：
    echo ========================================
    echo.
    echo [方案1] 检查Windows Defender
    echo   1. 打开"Windows 安全中心"
    echo   2. 病毒和威胁防护 → 保护历史记录
    echo   3. 查找是否有被隔离的文件
    echo   4. 如果有，点击"还原"
    echo   5. 然后添加排除项（下方有说明）
    echo.
    echo [方案2] 添加排除项并重新安装
    echo   1. 打开"Windows 安全中心"
    echo   2. 病毒和威胁防护 → 管理设置
    echo   3. 排除项 → 添加或删除排除项
    echo   4. 添加文件夹: %FOUND_DIR%
    echo   5. 重新下载并安装程序
    echo.
    echo [方案3] 重新下载完整安装包
    echo   下载地址: https://github.com/gfchfjh/CSBJJWT/releases
    echo   确保下载大小约 112 MB
    echo.
    echo [方案4] 使用便携版
    echo   下载后使用 win-unpacked 文件夹中的程序
    echo.
    pause
    exit /b 1
)

echo.
echo [成功] 找到后端文件: %FOUND_BACKEND%
echo 后端目录: %BACKEND_DIR%
echo.

:: 创建目标目录
echo [步骤3] 正在创建正确的目录结构...
echo.

set "TARGET_DIR=%BACKEND%\KOOKForwarder"

if exist "%TARGET_DIR%" (
    echo 目标目录已存在，正在清理...
    rd /s /q "%TARGET_DIR%" 2>nul
)

mkdir "%TARGET_DIR%" 2>nul

if not exist "%TARGET_DIR%" (
    echo [错误] 无法创建目录: %TARGET_DIR%
    echo 请以管理员身份运行此脚本！
    echo.
    pause
    exit /b 1
)

echo [成功] 创建目录: %TARGET_DIR%
echo.

:: 复制所有文件
echo [步骤4] 正在复制文件...
echo.

echo 从: %BACKEND_DIR%
echo 到: %TARGET_DIR%
echo.

xcopy /Y /E /I "%BACKEND_DIR%*" "%TARGET_DIR%\" >nul 2>&1

if errorlevel 1 (
    echo [警告] 文件复制可能不完整
) else (
    echo [成功] 文件复制完成
)

:: 重命名exe文件
echo.
echo [步骤5] 正在重命名可执行文件...
echo.

if exist "%TARGET_DIR%\kook-forwarder-backend.exe" (
    copy /Y "%TARGET_DIR%\kook-forwarder-backend.exe" "%TARGET_DIR%\KOOKForwarder.exe" >nul 2>&1
    echo [成功] 已创建 KOOKForwarder.exe
)

:: 验证结果
echo.
echo ========================================
echo 修复完成！正在验证...
echo ========================================
echo.

if exist "%TARGET_DIR%\KOOKForwarder.exe" (
    echo [✓] KOOKForwarder.exe 存在
    set "SUCCESS=1"
) else (
    echo [✗] KOOKForwarder.exe 不存在
    set "SUCCESS=0"
)

if exist "%TARGET_DIR%\KOOKForwarder.exe" (
    echo [✓] 后端文件大小: 
    for %%f in ("%TARGET_DIR%\KOOKForwarder.exe") do echo     %%~zf 字节
)

echo.

if "%SUCCESS%"=="1" (
    echo ========================================
    echo 🎉 修复成功！
    echo ========================================
    echo.
    echo 后端文件位置:
    echo %TARGET_DIR%\KOOKForwarder.exe
    echo.
    echo ========================================
    echo 下一步操作：
    echo ========================================
    echo.
    echo 1. 关闭此窗口
    echo 2. 重新启动"KOOK消息转发系统"应用
    echo 3. 如果还有问题，尝试以下操作：
    echo    - 以管理员身份运行应用
    echo    - 检查防火墙是否允许该应用
    echo    - 查看日志文件获取详细错误信息
    echo.
    echo 日志位置:
    echo %APPDATA%\KOOK消息转发系统\logs
    echo.
) else (
    echo ========================================
    echo ❌ 修复失败！
    echo ========================================
    echo.
    echo 请尝试以下方案：
    echo.
    echo [推荐] 重新下载完整安装包
    echo   1. 访问: https://github.com/gfchfjh/CSBJJWT/releases
    echo   2. 下载: KOOK-Forwarder-v18.0.0-Windows.zip (112 MB)
    echo   3. 先添加Windows Defender排除项
    echo   4. 完全解压后安装
    echo.
    echo [备选] 使用便携版
    echo   1. 下载ZIP包
    echo   2. 解压到 C:\KOOK\
    echo   3. 运行 win-unpacked\KOOK消息转发系统.exe
    echo.
    echo [高级] 从源码安装
    echo   1. 安装 Python 3.11+ 和 Node.js 18+
    echo   2. 克隆代码库
    echo   3. 运行 install.bat
    echo.
)

echo ========================================
echo 按任意键退出...
echo ========================================
pause >nul
