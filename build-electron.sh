#!/bin/bash
# KOOK消息转发系统 - Electron应用构建脚本 (Linux/macOS)
# 用法: ./build-electron.sh [win|mac|linux]

set -e

echo "========================================================"
echo "KOOK消息转发系统 - Electron应用构建"
echo "========================================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

# 运行构建脚本
python3 scripts/build_electron_app.py "$@"

echo ""
echo "[成功] Electron应用构建完成！"
echo ""
echo "构建产物位于: frontend/dist-electron/"
echo ""
