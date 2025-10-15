#!/bin/bash
# KOOK消息转发系统 - Linux/macOS启动脚本

echo ""
echo "========================================"
echo "  KOOK消息转发系统"
echo "  版本: 1.0.0"
echo "========================================"
echo ""

# 获取脚本所在目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python环境！"
    echo "请先安装Python 3.11或更高版本"
    exit 1
fi

# 检查Redis
if [ ! -f "$PROJECT_DIR/redis/redis-server" ]; then
    echo "[警告] Redis未安装！"
    echo "请参考 redis/README.md 下载Redis"
    echo ""
    read -p "是否继续启动（不含Redis）？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "[1/4] 启动Redis服务器..."
    cd "$PROJECT_DIR/redis"
    ./start_redis.sh &
    REDIS_PID=$!
    sleep 2
fi

echo "[2/4] 启动后端服务..."
cd "$PROJECT_DIR/backend"
python3 -m app.main &
BACKEND_PID=$!

echo "[3/4] 等待后端启动..."
sleep 3

echo "[4/4] 启动前端界面..."
cd "$PROJECT_DIR/frontend"

# 检查Node.js
if ! command -v npm &> /dev/null; then
    echo "[错误] 未找到Node.js环境！"
    echo "请先安装Node.js"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "首次运行，安装依赖..."
    npm install
fi

echo "启动前端..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "✅ 所有服务已启动！"
echo ""
echo "📝 访问地址: http://localhost:5173"
echo "📊 后端API: http://localhost:9527"
echo "🖼️  图床服务: http://localhost:9528"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "========================================"
echo ""

# 捕获Ctrl+C信号
trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo "正在停止所有服务..."
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$REDIS_PID" ]; then
        kill $REDIS_PID 2>/dev/null
    fi
    
    echo "✅ 所有服务已停止"
    exit 0
}

# 保持脚本运行
wait
