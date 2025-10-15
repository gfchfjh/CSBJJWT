#!/bin/bash
# Linux/macOS启动Redis脚本

echo "正在启动Redis服务器..."

# 获取脚本所在目录
REDIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查Redis可执行文件是否存在
if [ ! -f "$REDIS_DIR/redis-server" ]; then
    echo "错误: redis-server 未找到！"
    echo "请确保Redis已正确安装到此目录"
    exit 1
fi

# 添加执行权限
chmod +x "$REDIS_DIR/redis-server"

# 启动Redis
cd "$REDIS_DIR"
./redis-server redis.conf
