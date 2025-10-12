#!/bin/bash
# 完整打包脚本 - Linux/macOS

set -e  # 遇到错误立即退出

echo "======================================"
echo "KOOK消息转发系统 - 完整打包工具"
echo "======================================"
echo ""

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. 打包后端
echo "📦 步骤1/3: 打包Python后端..."
echo ""
python3 build/build_backend.py
if [ $? -ne 0 ]; then
    echo "❌ 后端打包失败"
    exit 1
fi
echo ""

# 2. 打包前端
echo "📦 步骤2/3: 打包Electron前端..."
echo ""
cd frontend
npm install
npm run build
npm run electron:build
if [ $? -ne 0 ]; then
    echo "❌ 前端打包失败"
    exit 1
fi
cd ..
echo ""

# 3. 整合打包
echo "📦 步骤3/3: 整合最终安装包..."
echo ""

# 复制后端到前端dist目录（Electron会打包进去）
mkdir -p frontend/dist/backend
cp -r dist/backend/* frontend/dist/backend/

# 如果有Redis，也复制进去
if [ -d "redis" ]; then
    mkdir -p frontend/dist/redis
    cp -r redis/* frontend/dist/redis/
fi

echo ""
echo "======================================"
echo "🎉 打包完成！"
echo "======================================"
echo "安装包位置："
echo "  - Windows: frontend/dist/*.exe"
echo "  - macOS:   frontend/dist/*.dmg"
echo "  - Linux:   frontend/dist/*.AppImage"
echo "======================================"
