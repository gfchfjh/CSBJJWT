#!/bin/bash
# ====================================================
#   KOOK消息转发系统 启动脚本 (Linux/macOS)
#   版本: v11.0.0 Enhanced
# ====================================================

set -e

echo "==================================="
echo "  KOOK消息转发系统 v11.0.0"
echo "==================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未检测到Python3，请先安装Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python版本: $(python3 --version)${NC}"

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📥 首次运行，正在安装依赖..."
    pip3 install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装失败${NC}"
        exit 1
    fi
fi

# 创建必要目录
mkdir -p data/images data/logs data/cache

# 启动Redis
echo "📥 启动Redis..."
if command -v redis-server &> /dev/null; then
    redis-server redis/redis.conf --daemonize yes
    REDIS_STARTED=1
elif [ -f "redis/redis-server" ]; then
    ./redis/redis-server redis/redis.conf --daemonize yes
    REDIS_STARTED=1
else
    echo -e "${YELLOW}⚠️  Redis未找到，将尝试连接外部Redis${NC}"
    REDIS_STARTED=0
fi

# 等待Redis启动
if [ $REDIS_STARTED -eq 1 ]; then
    sleep 2
    echo -e "${GREEN}✅ Redis已启动${NC}"
fi

# 启动后端
echo "🚀 启动后端服务..."
cd backend
python3 -m app.main &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3
echo -e "${GREEN}✅ 后端已启动 (PID: $BACKEND_PID)${NC}"

# 启动前端
echo "🎨 启动前端界面..."
cd frontend

if [ -d "dist" ]; then
    # 生产模式：使用构建后的文件
    if [ -d "node_modules" ]; then
        npm run preview &
        FRONTEND_PID=$!
    else
        echo -e "${YELLOW}⚠️  请先运行: cd frontend && npm install${NC}"
        kill $BACKEND_PID
        exit 1
    fi
else
    # 开发模式
    if [ -d "node_modules" ]; then
        npm run dev &
        FRONTEND_PID=$!
    else
        echo "📥 首次运行，正在安装前端依赖..."
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 前端依赖安装失败${NC}"
            kill $BACKEND_PID
            exit 1
        fi
        npm run dev &
        FRONTEND_PID=$!
    fi
fi

cd ..

echo ""
echo "==================================="
echo -e "${GREEN}  ✅ 系统已启动！${NC}"
echo "  📍 访问地址: http://localhost:9527"
echo "  📍 后端API: http://localhost:9527/docs"
echo "==================================="
echo ""
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo ""
echo "按 Ctrl+C 停止服务..."

# 等待中断信号
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 保持脚本运行
wait
