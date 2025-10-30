#!/bin/bash
echo "========================================"
echo "KOOK消息转发系统 v2.0 - 安装脚本"
echo "========================================"
echo ""

echo "[1/3] 安装Python依赖..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: Python依赖安装失败"
    exit 1
fi
echo ""

echo "[2/3] 安装Playwright浏览器..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "警告: Playwright浏览器安装失败，某些功能可能不可用"
fi
echo ""

echo "[3/3] 安装前端依赖..."
cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo "错误: 前端依赖安装失败"
    exit 1
fi
echo ""

echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "启动方式:"
echo "  后端: ./start_backend.sh"
echo "  前端: ./start_frontend.sh"
echo ""
