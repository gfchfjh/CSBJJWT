@echo off
REM Windows启动Redis脚本

echo 正在启动Redis服务器...

REM 获取脚本所在目录
set REDIS_DIR=%~dp0

REM 检查Redis可执行文件是否存在
if not exist "%REDIS_DIR%redis-server.exe" (
    echo 错误: redis-server.exe 未找到！
    echo 请确保Redis已正确安装到此目录
    pause
    exit /b 1
)

REM 启动Redis
cd /d "%REDIS_DIR%"
redis-server.exe redis.conf

pause
