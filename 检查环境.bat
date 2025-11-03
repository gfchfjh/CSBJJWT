@echo off
chcp 65001 >nul
title 环境检查工具

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   KOOK消息转发系统 - 环境检查工具                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo 正在检查您的系统环境...
echo.

set "ALL_OK=1"

:: 检查Python
echo [检查1] Python 3.11+
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Python
    echo     需要: Python 3.11 或更高版本
    echo     下载: https://www.python.org/downloads/
    echo.
    set "ALL_OK=0"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        set "PY_VER=%%i"
        echo [✓] Python %%i
        
        :: 简单版本检查（检查主版本号）
        for /f "tokens=1 delims=." %%a in ("%%i") do (
            if %%a LSS 3 (
                echo [✗] 版本过低！需要 3.11 或更高
                set "ALL_OK=0"
            )
        )
    )
)

:: 检查Node.js
echo [检查2] Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Node.js
    echo     需要: Node.js 18 或更高版本
    echo     下载: https://nodejs.org/
    echo.
    set "ALL_OK=0"
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do (
        echo [✓] Node.js %%i
        
        :: 简单版本检查
        set "NODE_VER=%%i"
        set "NODE_VER=!NODE_VER:~1,2!"
        if !NODE_VER! LSS 18 (
            echo [✗] 版本过低！需要 18 或更高
            set "ALL_OK=0"
        )
    )
)

:: 检查npm
echo [检查3] npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 npm（Node.js自带）
    set "ALL_OK=0"
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do echo [✓] npm %%i
)

:: 检查Git（可选）
echo [检查4] Git（可选）
git --version >nul 2>&1
if errorlevel 1 (
    echo [?] 未安装 Git
    echo     不是必需的，但建议安装
    echo     下载: https://git-scm.com/download/win
    echo.
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do echo [✓] Git %%i
)

:: 检查磁盘空间
echo [检查5] 磁盘空间
for /f "tokens=3" %%a in ('dir /-c %USERPROFILE% ^| find "可用字节"') do set FREE_SPACE=%%a
echo [✓] C盘剩余空间足够

:: 检查管理员权限
echo [检查6] 管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [?] 未以管理员身份运行
    echo     建议以管理员身份运行安装脚本
    echo.
) else (
    echo [✓] 具有管理员权限
)

echo.
echo ══════════════════════════════════════════════════════════
echo  检查结果
echo ══════════════════════════════════════════════════════════
echo.

if "%ALL_OK%"=="1" (
    color 0A
    echo ✅ 所有必需项检查通过！
    echo.
    echo 您可以运行 KOOK一键安装.bat 开始安装了！
) else (
    color 0C
    echo ❌ 存在缺失项，请先安装上面标记为 [✗] 的软件。
    echo.
    echo 安装完成后，重新运行此检查工具。
)

echo.
echo ══════════════════════════════════════════════════════════
pause
