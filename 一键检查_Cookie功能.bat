@echo off
chcp 65001 >nul
title KOOK转发系统 - Cookie功能检查
color 0D

echo ========================================
echo   KOOK消息转发系统 - Cookie功能检查
echo   版本: v18.0.4+
echo ========================================
echo.

cd /d "%~dp0"

echo [检查开始] %date% %time%
echo.

REM 检查Cookie更新API
echo [检查1/3] 查找Cookie更新API...
findstr /i /c:"async def update_cookie" backend\app\api\accounts.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Cookie更新API存在
    echo.
    echo [API详情]
    findstr /i /n /c:"def update_cookie" /c:"def check_cookie_status" backend\app\api\accounts.py
) else (
    echo ❌ Cookie更新API不存在
)
echo.

REM 检查数据库Cookie更新方法
echo [检查2/3] 查找数据库Cookie更新方法...
findstr /i /c:"update_account_cookie" backend\app\database.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 数据库更新方法存在
) else (
    echo ⚠️  数据库更新方法可能在其他位置
)
echo.

REM 检查前端Cookie更新功能
echo [检查3/3] 查找前端Cookie更新功能...
findstr /i /c:"updateCookie" frontend\src\views\Accounts.vue >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 前端更新功能存在
    echo.
    echo [功能详情]
    findstr /i /n /c:"updateCookie" frontend\src\views\Accounts.vue | findstr /v /c:"v-if" /c:"v-show"
) else (
    echo ❌ 前端更新功能不存在
)
echo.

echo ========================================
echo   检查完成！
echo ========================================
echo.

echo [功能说明]
echo 1. Cookie更新API: PUT /api/accounts/{account_id}/cookie
echo 2. Cookie状态API: GET /api/accounts/{account_id}/cookie-status
echo 3. 前端更新按钮: 账号管理页面的"更新Cookie"按钮
echo.

echo [使用方法]
echo 1. 启动后端和前端服务
echo 2. 进入"账号管理"页面
echo 3. 点击账号右侧的"更新Cookie"按钮（黄色）
echo 4. 粘贴新的Cookie
echo 5. 点击"更新"
echo.

echo [Git提交记录]
git log --oneline --all --grep="cookie" -5
echo.

echo [详细文档] 请查看 CMD_操作指南_完整版.md 第五阶段
echo.
pause
