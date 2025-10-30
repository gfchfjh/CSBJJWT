#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 KOOK消息转发系统 v2.0 - Production Edition"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📁 工作目录: $DIR"
echo ""

# 启动后端
echo "1️⃣  启动后端服务..."
cd "$DIR/backend"
./KOOKForwarder &
BACKEND_PID=$!

echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""

# 等待后端启动
echo "⏳ 等待后端就绪..."
sleep 3

# 检查后端是否运行
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 后端运行正常"
else
    echo "❌ 后端启动失败"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 启动完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 访问方式:"
echo "  Web界面: file://$DIR/web/index.html"
echo "  API文档: http://localhost:9527/docs"
echo "  后端API: http://localhost:9527"
echo ""
echo "💡 提示:"
echo "  - 双击打开 web/index.html 访问界面"
echo "  - 后端运行在端口 9527"
echo "  - 按 Ctrl+C 停止服务"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 等待用户中断
trap "echo ''; echo '停止服务...'; kill $BACKEND_PID; echo '✅ 服务已停止'; exit 0" INT
wait $BACKEND_PID
