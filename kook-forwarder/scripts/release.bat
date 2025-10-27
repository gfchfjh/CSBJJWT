@echo off
REM KOOK消息转发系统 - Windows发布脚本
REM 自动化版本发布流程

setlocal enabledelayedexpansion

echo.
echo ==================================================
echo    KOOK消息转发系统 - 自动发布脚本
echo ==================================================
echo.

REM 检查Git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Git未安装，请先安装Git
    exit /b 1
)

REM 检查Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Node.js未安装，请先安装Node.js
    exit /b 1
)

REM 检查Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Python未安装，请先安装Python
    exit /b 1
)

echo [信息] 所有必要工具已安装
echo.

REM 获取当前版本
for /f "tokens=2 delims=:, " %%a in ('findstr /c:"\"version\"" frontend\package.json') do (
    set CURRENT_VERSION=%%a
    set CURRENT_VERSION=!CURRENT_VERSION:"=!
)

echo [信息] 当前版本: v!CURRENT_VERSION!
echo.

REM 询问新版本号
set /p NEW_VERSION="请输入新版本号 (当前: !CURRENT_VERSION!): "

echo [信息] 新版本: v%NEW_VERSION%
echo.

REM 确认发布
set /p CONFIRM="确认发布 v%NEW_VERSION%? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo [警告] 发布已取消
    exit /b 0
)

echo.
echo [信息] 开始发布流程...
echo.

REM 步骤1: 检查Git状态
echo [信息] 步骤1/8: 检查Git状态...
git status -s
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 工作目录有未提交的更改
    set /p CONTINUE="是否继续? (y/n): "
    if /i not "!CONTINUE!"=="y" (
        echo [警告] 发布已取消
        exit /b 0
    )
)
echo [成功] Git状态检查完成
echo.

REM 步骤2: 更新版本号
echo [信息] 步骤2/8: 更新版本号...

REM 更新frontend/package.json
powershell -Command "(Get-Content frontend\package.json) -replace '\"version\": \".*\"', '\"version\": \"%NEW_VERSION%\"' | Set-Content frontend\package.json"

REM 更新backend/app/config.py
powershell -Command "(Get-Content backend\app\config.py) -replace 'app_version = \".*\"', 'app_version = \"%NEW_VERSION%\"' | Set-Content backend\app\config.py"

REM 更新README.md
powershell -Command "(Get-Content README.md) -replace 'version-[\d\.]+', 'version-%NEW_VERSION%' | Set-Content README.md"

echo [成功] 版本号已更新为 v%NEW_VERSION%
echo.

REM 步骤3: 运行测试
echo [信息] 步骤3/8: 运行测试...
if exist "backend\pytest.ini" (
    echo [信息] 运行后端测试...
    cd backend
    python -m pytest --tb=short -v
    cd ..
    echo [成功] 后端测试完成
) else (
    echo [警告] 跳过后端测试
)

if exist "frontend\package.json" (
    echo [信息] 运行前端测试...
    cd frontend
    call npm run test
    cd ..
    echo [成功] 前端测试完成
) else (
    echo [警告] 跳过前端测试
)
echo.

REM 步骤4: 检查CHANGELOG
echo [信息] 步骤4/8: 检查CHANGELOG...
if not exist "CHANGELOG_v%NEW_VERSION%.md" (
    echo [警告] 未找到 CHANGELOG_v%NEW_VERSION%.md，请手动创建
    pause
) else (
    echo [成功] CHANGELOG已存在
)
echo.

REM 步骤5: Git提交
echo [信息] 步骤5/8: 提交更改到Git...
git add -A
git commit -m "chore: 发布 v%NEW_VERSION%"
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 没有需要提交的更改
)
echo [成功] 更改已提交
echo.

REM 步骤6: 创建Git标签
echo [信息] 步骤6/8: 创建Git标签...
git tag -a "v%NEW_VERSION%" -m "Release v%NEW_VERSION%"
echo [成功] Git标签已创建: v%NEW_VERSION%
echo.

REM 步骤7: 推送到远程仓库
echo [信息] 步骤7/8: 推送到远程仓库...
set /p PUSH="是否推送到GitHub? (y/n): "
if /i "%PUSH%"=="y" (
    git push origin main
    git push origin "v%NEW_VERSION%"
    echo [成功] 已推送到GitHub
) else (
    echo [警告] 跳过推送
)
echo.

REM 步骤8: 构建安装包
echo [信息] 步骤8/8: 构建安装包...
set /p BUILD="是否构建安装包? (y/n): "
if /i "%BUILD%"=="y" (
    echo [信息] 开始构建...
    
    if exist "build\build_backend.py" (
        echo [信息] 构建后端...
        python build\build_backend.py
    )
    
    if exist "build\build_all.bat" (
        echo [信息] 构建前端...
        call build\build_all.bat
    )
    
    echo [成功] 构建完成
) else (
    echo [警告] 跳过构建
)
echo.

REM 完成
echo ==================================================
echo    🎉 发布完成！
echo ==================================================
echo.
echo [成功] 版本 v%NEW_VERSION% 已成功发布
echo.
echo 接下来：
echo   1. 访问 GitHub Releases 页面
echo   2. 编辑发布说明
echo   3. 上传构建的安装包
echo.
echo GitHub Releases: https://github.com/gfchfjh/CSBJJWT/releases
echo.
pause
