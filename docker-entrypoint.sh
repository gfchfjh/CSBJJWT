#!/bin/bash
set -e

echo "==================================="
echo "KOOK消息转发系统 - Docker启动"
echo "==================================="

# 启动Redis（后台）
echo "启动Redis服务..."
redis-server --daemonize yes --port ${REDIS_PORT:-6379}

# 等待Redis启动
echo "等待Redis就绪..."
for i in {1..30}; do
    if redis-cli -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; then
        echo "✅ Redis已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Redis启动超时"
        exit 1
    fi
    sleep 1
done

# 初始化数据库（如果需要）
echo "初始化数据库..."
cd backend
python -c "from app.database import db; print('✅ 数据库初始化完成')"

# 执行传入的命令
echo "启动应用..."
exec "$@"
