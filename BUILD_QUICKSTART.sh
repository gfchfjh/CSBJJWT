#!/bin/bash
# 快速构建脚本 - 一键完成所有准备工作

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║          🚀 KOOK消息转发系统 - 快速构建准备工具                  ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# 1. 生成图标
echo "📦 步骤1/3: 生成图标文件..."
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py

echo ""
echo "✅ 图标生成完成！"
echo ""

# 2. 验证环境
echo "🔍 步骤2/3: 验证构建环境..."
python3 build/verify_build.py

echo ""

# 3. 提示下一步
echo "🎯 步骤3/3: 准备就绪！"
echo ""
echo "现在可以选择："
echo ""
echo "  方式1: 触发GitHub Actions构建（推荐）"
echo "         ./release_package.sh"
echo ""
echo "  方式2: 本地构建"
echo "         ./build_installer.sh"
echo ""
echo "详细文档："
echo "  - PRE_BUILD_CHECKLIST.md - 构建前检查清单"
echo "  - BUILD_EXECUTION_GUIDE.md - 详细构建指南"
echo "  - BUILD_TOOLS_README.md - 工具使用说明"
echo ""
