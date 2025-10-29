#!/bin/bash
# KOOK消息转发系统 - Docker入口脚本
# ✅ P2-1优化：完善的启动脚本

set -e

echo "========================================="
echo "KOOK消息转发系统 - Docker版"
echo "========================================="

# 读取版本号
VERSION=$(cat /app/VERSION 2>/dev/null || echo "unknown")
echo "版本: $VERSION"
echo ""

# 初始化数据目录
echo "🔧 初始化数据目录..."
mkdir -p /app/data/{images,logs,redis,config}
chmod -R 755 /app/data
echo "✅ 数据目录初始化完成"

# 检查Redis连接
echo "🔧 检查Redis连接..."
if [ -n "$REDIS_HOST" ]; then
    until redis-cli -h $REDIS_HOST -p ${REDIS_PORT:-6379} ping 2>/dev/null; do
        echo "⏳ 等待Redis启动..."
        sleep 2
    done
    echo "✅ Redis连接成功"
fi

# 初始化数据库
echo "🔧 初始化数据库..."
python3 -c "
from backend.app.database import db
db.init_db()
print('✅ 数据库初始化完成')
" || echo "⚠️ 数据库已存在，跳过初始化"

# 检查Playwright浏览器
echo "🔧 检查Playwright浏览器..."
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH/chromium-"* ]; then
    echo "⏳ 首次运行，正在下载Chromium浏览器..."
    python3 -m playwright install chromium --with-deps
    echo "✅ Chromium安装完成"
else
    echo "✅ Chromium已安装"
fi

# 显示配置信息
echo ""
echo "========================================="
echo "配置信息:"
echo "  API地址: http://0.0.0.0:9527"
echo "  图床地址: http://0.0.0.0:9528"
echo "  Redis: ${REDIS_HOST}:${REDIS_PORT}"
echo "  数据目录: /app/data"
echo "========================================="
echo ""

# 启动应用
echo "🚀 启动应用..."
exec "$@"
