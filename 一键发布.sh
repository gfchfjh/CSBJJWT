#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 KOOK消息转发系统 v16.0.0 - 正式发布脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 确保在项目目录
cd /workspace

echo "📋 检查当前状态..."
git status

echo ""
read -p "❓ 确认要发布v16.0.0正式版吗？ (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 取消发布"
    exit 0
fi

echo ""
echo "📦 添加所有更改..."
git add .

echo ""
echo "💾 提交更改..."
git commit -m "release: v16.0.0 正式版

✨ 新特性
- 全新3步配置向导
- 完美UI界面优化
- 详细图文教程文档
- 图片处理策略优化

📦 构建
- GitHub Actions自动构建配置
- 支持Windows/macOS/Linux全平台

📚 文档
- 4篇详细图文教程
- 完整Release Notes
- 跨平台构建指南

🔧 优化
- 性能优化
- 构建脚本增强
"

echo ""
echo "📤 推送代码到远程仓库..."
git push origin cursor/check-if-code-can-be-written-c611

echo ""
echo "🏷️  创建版本tag..."
git tag -a v16.0.0 -m "KOOK消息转发系统 v16.0.0 正式版

深度优化完整版本，包含所有平台安装包。

主要更新：
✅ 全新3步配置向导
✅ 完美UI界面
✅ 4篇详细教程
✅ 图片策略优化
✅ 性能提升

安装包由GitHub Actions自动构建。
"

echo ""
echo "🚀 推送tag，触发GitHub Actions自动构建..."
git push origin v16.0.0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 发布流程已启动！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 监控构建进度:"
echo "   https://github.com/gfchfjh/CSBJJWT/actions"
echo ""
echo "📦 查看Release（10-15分钟后）:"
echo "   https://github.com/gfchfjh/CSBJJWT/releases/tag/v16.0.0"
echo ""
echo "⏱️  预计等待时间: 10-15分钟"
echo ""
echo "🎉 感谢使用KOOK消息转发系统！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
