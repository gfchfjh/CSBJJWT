@echo off
chcp 65001 >nul
title 终极重启前端（清除所有缓存）

echo ================================================
echo     🔥 终极重启前端（清除所有缓存）
echo ================================================
echo.

cd /d "%~dp0frontend"

echo 【1/5】停止所有 Node.js 进程...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo ✅ 已停止

echo.
echo 【2/5】删除 Vite 缓存...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo ✅ Vite 缓存已删除
) else (
    echo ℹ️ 无 Vite 缓存
)

echo.
echo 【3/5】删除构建产物...
if exist "dist" (
    rmdir /s /q "dist"
    echo ✅ dist 目录已删除
) else (
    echo ℹ️ 无 dist 目录
)

echo.
echo 【4/5】清除 NPM 缓存...
call npm cache clean --force 2>nul
echo ✅ NPM 缓存已清除

echo.
echo 【5/5】启动前端开发服务器...
echo.
echo ================================================
echo   🚀 正在启动，请稍候...
echo ================================================
echo.

call npm run dev

pause
