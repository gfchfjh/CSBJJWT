@echo off
chcp 65001 >nul
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 KOOK消息转发系统 v2.0 - Production Edition
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo 1️⃣  启动后端服务...
start "KOOK Forwarder Backend" /MIN cmd /c "%~dp0backend\KOOKForwarder.exe"

echo ✅ 后端服务已启动
timeout /t 3 /nobreak >nul

echo.
echo 2️⃣  打开Web界面...
start "" "%~dp0web\index.html"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🎉 启动完成！
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📱 访问方式:
echo   Web界面: 已自动打开
echo   API文档: http://localhost:9527/docs
echo   后端API: http://localhost:9527
echo.
echo 💡 提示:
echo   - 后端运行在端口 9527
echo   - 关闭此窗口不会停止后端服务
echo   - 双击 stop.bat 停止服务
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
