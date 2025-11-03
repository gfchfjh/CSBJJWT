@echo off
chcp 65001 >nul
echo ========================================
echo     彻底重启前端（清除缓存）
echo ========================================
echo.

cd /d "%~dp0frontend"

echo 【1/3】停止现有进程...
taskkill /F /IM node.exe 2>nul

echo 【2/3】清除 Vite 缓存...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo ✅ Vite 缓存已清除
) else (
    echo ℹ️ 没有找到缓存
)

echo 【3/3】启动前端...
echo.
echo ================================
echo    即将启动，请稍候...
echo ================================
echo.

npm run dev

pause
