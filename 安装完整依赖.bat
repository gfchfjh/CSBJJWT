@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo     安装所有后端依赖（完整版）
echo ========================================
echo.

call venv\Scripts\activate

echo 【1/3】安装核心框架...
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-multipart -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 【2/3】安装数据库和异步库...
pip install aiohttp aiofiles aiosqlite redis aioredis sqlalchemy -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 【3/3】安装第三方集成和工具...
pip install discord-webhook python-telegram-bot loguru apscheduler requests beautifulsoup4 ddddocr python-jose[cryptography] passlib[bcrypt] httpx qrcode pillow playwright cryptography bcrypt python-dotenv orjson aiosmtplib email-validator -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo     ✅ 所有依赖安装完成！
echo ========================================
echo.

pause
