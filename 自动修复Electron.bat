@echo off
chcp 65001 >nul
title KOOK Electron 自动修复工具
color 0B

echo.
echo ================================================================
echo            KOOK Electron 启动问题 - 自动修复工具
echo ================================================================
echo.
echo 本工具将自动执行以下修复：
echo   1. 创建最小化启动脚本
echo   2. 优化后端配置（禁用非核心功能）
echo   3. 调整 Electron 配置（增加超时时间）
echo   4. 优化健康检查逻辑
echo   5. 重新构建后端和前端
echo.
echo 预计时间：30-60 分钟
echo.
echo ================================================================
echo.

pause

:: 检查项目目录
if not exist "backend" (
    echo [错误] 当前目录不是 KOOK 项目根目录！
    echo 请在项目根目录（CSBJJWT文件夹）中运行此脚本
    pause
    exit /b 1
)

:: 创建备份目录
echo.
echo [准备] 创建备份...
if not exist "backup" mkdir backup
copy /Y "backend\app\main.py" "backup\main.py.bak" >nul 2>&1
copy /Y "frontend\electron\main.js" "backup\main.js.bak" >nul 2>&1
copy /Y "build\pyinstaller.spec" "backup\pyinstaller.spec.bak" >nul 2>&1
echo [完成] 备份已创建到 backup\ 目录
echo.

:: ================================================================
:: 第一部分：创建最小化启动脚本
:: ================================================================
echo.
echo ================================================================
echo [步骤 1/6] 创建最小化启动脚本
echo ================================================================
echo.

(
echo import sys
echo import os
echo.
echo # 设置路径
echo sys.path.insert^(0, os.path.dirname^(__file__^)^)
echo os.chdir^(os.path.dirname^(__file__^)^)
echo.
echo # 最小化导入
echo from app.main import app
echo import uvicorn
echo.
echo if __name__ == "__main__":
echo     # 最简启动配置
echo     uvicorn.run^(
echo         app,
echo         host="127.0.0.1",
echo         port=8000,
echo         log_level="error",
echo         access_log=False,
echo     ^)
) > backend\run_minimal.py

echo [完成] 已创建 backend\run_minimal.py
echo.

:: ================================================================
:: 第二部分：优化 main.py
:: ================================================================
echo.
echo ================================================================
echo [步骤 2/6] 优化后端 main.py
echo ================================================================
echo.

:: 创建 Python 修复脚本
(
echo import re
echo import os
echo.
echo # 读取 main.py
echo filepath = 'backend/app/main.py'
echo with open^(filepath, 'r', encoding='utf-8'^) as f:
echo     content = f.read^(^)
echo.
echo # 注释掉环境检查
echo content = re.sub^(
echo     r'^(\s*^)^(check_environment\(\)^)',
echo     r'\1# \2  # 已禁用以加快启动',
echo     content,
echo     flags=re.MULTILINE
echo ^)
echo.
echo # 注释掉图床服务器启动
echo if 'start_image_server' in content:
echo     content = re.sub^(
echo         r'^(\s*^)^(.*start_image_server.*^)',
echo         r'\1# \2  # 已禁用',
echo         content,
echo         flags=re.MULTILINE
echo     ^)
echo.
echo # 保存
echo with open^(filepath, 'w', encoding='utf-8'^) as f:
echo     f.write^(content^)
echo.
echo print^("main.py 优化完成"^)
) > fix_main.py

python fix_main.py
if %errorlevel% equ 0 (
    echo [完成] main.py 已优化
) else (
    echo [警告] main.py 优化可能失败，但继续执行
)
del fix_main.py
echo.

:: ================================================================
:: 第三部分：修改 PyInstaller 配置
:: ================================================================
echo.
echo ================================================================
echo [步骤 3/6] 修改 PyInstaller 配置
echo ================================================================
echo.

:: 使用 PowerShell 修改
powershell -Command "(Get-Content build\pyinstaller.spec) -replace \"'../backend/run.py'\", \"'../backend/run_minimal.py'\" | Set-Content build\pyinstaller.spec"

if %errorlevel% equ 0 (
    echo [完成] pyinstaller.spec 已更新
) else (
    echo [警告] 自动修改失败，需要手动修改
    echo 请将 build\pyinstaller.spec 中的
    echo   '../backend/run.py'
    echo 改为
    echo   '../backend/run_minimal.py'
)
echo.

:: ================================================================
:: 第四部分：优化 Electron 配置
:: ================================================================
echo.
echo ================================================================
echo [步骤 4/6] 优化 Electron 配置
echo ================================================================
echo.

:: 创建 Python 修复脚本
(
echo import re
echo.
echo # 读取 main.js
echo filepath = 'frontend/electron/main.js'
echo with open^(filepath, 'r', encoding='utf-8'^) as f:
echo     content = f.read^(^)
echo.
echo # 查找并替换超时配置
echo modifications = [
echo     ^(r'const\s+BACKEND_STARTUP_TIMEOUT\s*=\s*\d+', 'const BACKEND_STARTUP_TIMEOUT = 120000'^),
echo     ^(r'const\s+MAX_HEALTH_CHECK_RETRIES\s*=\s*\d+', 'const MAX_HEALTH_CHECK_RETRIES = 10'^),
echo     ^(r'const\s+HEALTH_CHECK_INTERVAL\s*=\s*\d+', 'const HEALTH_CHECK_INTERVAL = 5000'^),
echo ]
echo.
echo for pattern, replacement in modifications:
echo     if re.search^(pattern, content^):
echo         content = re.sub^(pattern, replacement, content^)
echo     else:
echo         # 如果找不到，在文件开头添加
echo         if 'BACKEND_STARTUP_TIMEOUT' not in content:
echo             insert_pos = content.find^('const { app,'^)
echo             if insert_pos != -1:
echo                 insert_pos = content.find^('\n', insert_pos^) + 1
echo                 config = '\n// 修复后的启动配置\nconst BACKEND_STARTUP_TIMEOUT = 120000;\nconst MAX_HEALTH_CHECK_RETRIES = 10;\nconst HEALTH_CHECK_INTERVAL = 5000;\n\n'
echo                 content = content[:insert_pos] + config + content[insert_pos:]
echo.
echo # 保存
echo with open^(filepath, 'w', encoding='utf-8'^) as f:
echo     f.write^(content^)
echo.
echo print^("main.js 优化完成"^)
) > fix_electron.py

python fix_electron.py
if %errorlevel% equ 0 (
    echo [完成] Electron main.js 已优化
) else (
    echo [警告] 自动修改可能失败
)
del fix_electron.py
echo.

:: ================================================================
:: 第五部分：重新构建后端
:: ================================================================
echo.
echo ================================================================
echo [步骤 5/6] 重新构建后端（约 3-5 分钟）
echo ================================================================
echo.

:: 激活虚拟环境
cd backend
call venv\Scripts\activate.bat
cd ..

:: 运行 PyInstaller
echo [构建] 正在打包后端...
pyinstaller build\pyinstaller.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo [完成] 后端打包成功
    echo.
    
    :: 验证文件
    if exist "dist\KOOKForwarder\KOOKForwarder.exe" (
        echo [验证] ✅ 后端可执行文件已生成
        dir dist\KOOKForwarder\KOOKForwarder.exe | findstr "KOOKForwarder.exe"
    ) else (
        echo [错误] ❌ 后端可执行文件未生成
    )
) else (
    echo [错误] 后端打包失败！
    echo 请查看上面的错误信息
    pause
    exit /b 1
)
echo.

:: 测试后端
echo [测试] 测试后端独立启动（10秒测试）
cd dist\KOOKForwarder
start /MIN cmd /c "KOOKForwarder.exe"
timeout /t 10 /nobreak >nul

:: 检查端口
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo [测试] ✅ 后端启动成功，端口 8000 正在监听
    taskkill /F /IM KOOKForwarder.exe >nul 2>&1
) else (
    echo [警告] ⚠️ 后端可能未正常启动
    taskkill /F /IM KOOKForwarder.exe >nul 2>&1
)
cd ..\..
echo.

:: ================================================================
:: 第六部分：重新构建 Electron
:: ================================================================
echo.
echo ================================================================
echo [步骤 6/6] 重新构建 Electron（约 5-10 分钟）
echo ================================================================
echo.

cd frontend
echo [构建] 正在构建 Electron 应用...
call npm run electron:build:win

if %errorlevel% equ 0 (
    echo [完成] Electron 构建成功
    echo.
    
    :: 显示安装包位置
    if exist "dist-electron\*.exe" (
        echo [成功] ✅ 安装包已生成：
        dir dist-electron\*.exe
        echo.
        echo 安装包位置：
        cd
        echo \frontend\dist-electron\
    ) else (
        echo [警告] 未找到安装包文件
    )
) else (
    echo [错误] Electron 构建失败
    echo 请查看上面的错误信息
)
cd ..
echo.

:: ================================================================
:: 完成
:: ================================================================
echo.
echo ================================================================
echo                    修复完成！
echo ================================================================
echo.
echo 下一步操作：
echo.
echo 1. 卸载旧版本（如果已安装）
echo    控制面板 ^> 程序和功能 ^> KOOK消息转发系统 ^> 卸载
echo.
echo 2. 安装新版本
echo    运行: frontend\dist-electron\KOOK消息转发系统 Setup 18.0.x.exe
echo.
echo 3. 启动测试
echo    双击桌面图标或开始菜单中的"KOOK消息转发系统"
echo.
echo 4. 观察启动过程
echo    - 应该不再出现 "fetch failed" 错误
echo    - 能看到登录页面
echo    - 可以正常使用
echo.
echo ================================================================
echo.
echo 如果还是失败：
echo   1. 查看 Electron修复完整方案.md 的调试部分
echo   2. 使用 debug_start.bat 调试启动
echo   3. 或使用 Web 版本（启动KOOK系统.bat）
echo.
echo 备份文件位置：
echo   backup\main.py.bak
echo   backup\main.js.bak
echo   backup\pyinstaller.spec.bak
echo.
echo ================================================================
echo.

echo 是否立即安装新版本？(Y/N)
set /p install_now="请选择: "

if /i "%install_now%"=="Y" (
    echo.
    echo 正在打开安装包目录...
    explorer frontend\dist-electron
    echo.
    echo 请双击 .exe 文件进行安装
) else (
    echo.
    echo 您可以稍后手动安装
    echo 安装包位置: frontend\dist-electron\
)

echo.
echo 按任意键退出...
pause >nul
exit /b 0
