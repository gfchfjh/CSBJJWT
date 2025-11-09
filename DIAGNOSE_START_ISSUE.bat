@echo off
chcp 65001 >nul
echo ========================================
echo 启动按钮问题诊断脚本
echo ========================================
echo.

echo [步骤1] 检查后端服务是否运行...
echo.
curl -s http://localhost:9527/api/system/status >nul 2>&1
if errorlevel 1 (
    echo ❌ 后端服务未运行或无响应
    echo.
    echo 请在新CMD窗口执行：
    echo cd C:\Users\tanzu\Desktop\CSBJJWT\backend
    echo ..\venv\Scripts\activate
    echo python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
    echo.
    pause
    exit /b 1
) else (
    echo ✅ 后端服务正常运行
)

echo.
echo [步骤2] 检查前端服务是否运行...
echo.
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo ❌ 前端服务未运行或无响应
    echo.
    echo 请在新CMD窗口执行：
    echo cd C:\Users\tanzu\Desktop\CSBJJWT\frontend
    echo npm run dev
    echo.
    pause
    exit /b 1
) else (
    echo ✅ 前端服务正常运行
)

echo.
echo [步骤3] 测试账号列表API...
echo.
curl -s http://localhost:9527/api/accounts/ > temp_accounts.json
if errorlevel 1 (
    echo ❌ 获取账号列表失败
    pause
    exit /b 1
) else (
    echo ✅ 账号列表API正常
    type temp_accounts.json
    del temp_accounts.json
)

echo.
echo ========================================
echo 诊断完成
echo ========================================
echo.
echo 请按照以下步骤提供信息：
echo.
echo 1. 打开浏览器访问 http://localhost:5173
echo 2. 按F12打开开发者工具
echo 3. 切换到Console标签
echo 4. 点击"启动"按钮
echo 5. 复制Console中的所有输出（包括错误）
echo 6. 同时复制后端CMD窗口中的日志输出
echo.
echo 然后把这两部分信息发给我！
echo.
pause
