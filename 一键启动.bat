@echo off 
title KOOK 消息转发系统 
echo 正在启动 KOOK 系统... 
echo. 
echo [1/2] 启动后端服务... 
start "KOOK-后端" cmd /k "cd backend && venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload" 
echo [2/2] 等待后端启动... 
timeout /t 10 /nobreak >nul 
echo [3/3] 启动前端服务... 
start "KOOK-前端" cmd /k "cd frontend && npm run dev" 
echo. 
echo ========================================== 
echo 系统启动中... 
echo ========================================== 
echo. 
echo 后端窗口：黑色窗口（标题：KOOK-后端） 
echo 前端窗口：黑色窗口（标题：KOOK-前端） 
echo. 
echo 等待15秒后自动打开浏览器... 
timeout /t 15 /nobreak >nul 
echo 正在打开浏览器... 
start http://localhost:5174 
echo. 
echo 提示：关闭后端或前端窗口将停止对应服务 
pause
