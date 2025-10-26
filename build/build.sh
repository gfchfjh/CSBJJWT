#!/bin/bash
# KOOK消息转发系统 - Linux/macOS 构建脚本

set -e

echo "=================================="
echo "KOOK消息转发系统 - 构建脚本"
echo "=================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到node"
    exit 1
fi

# 运行统一构建脚本
python3 build/build_unified.py "$@"

echo ""
echo "✅ 构建完成！"
echo "📦 安装包位置: dist/v6.3.0/"
