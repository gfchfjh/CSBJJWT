@echo off
chcp 65001 >nul
echo 停止KOOK消息转发系统...
taskkill /F /IM KOOKForwarder.exe 2>nul
if %errorlevel%==0 (
    echo ✅ 服务已停止
) else (
    echo ℹ️  服务未运行
)
pause
