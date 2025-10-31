#!/bin/bash
# Windows安装包快速构建脚本
# 用于在Windows环境（Git Bash/WSL）中执行

echo "========================================="
echo "  KOOK消息转发系统 v17.0.0"
echo "  Windows安装包构建脚本"
echo "========================================="
echo ""

# 检查环境
if [[ "$OSTYPE" != "win32" && "$OSTYPE" != "msys" ]]; then
    echo "警告: 此脚本设计用于Windows环境"
    echo "当前环境: $OSTYPE"
    echo ""
fi

# 进入前端目录
cd frontend || exit 1

echo "1. 检查Node.js..."
node --version || { echo "错误: Node.js未安装"; exit 1; }
echo ""

echo "2. 安装依赖..."
npm install --legacy-peer-deps
npm install -D sass-embedded --legacy-peer-deps
echo ""

echo "3. 构建前端..."
npm run build
echo ""

echo "4. 构建Windows安装包..."
npx electron-builder --win --x64
echo ""

echo "========================================="
echo "  构建完成！"
echo "========================================="
echo ""
echo "安装包位置: dist-electron/"
ls -lh dist-electron/*.exe 2>/dev/null || echo "未找到exe文件，请检查构建日志"
echo ""
