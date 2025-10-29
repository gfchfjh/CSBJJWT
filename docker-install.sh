#!/bin/bash
# KOOK消息转发系统 - Docker一键安装脚本
# ✅ P2-1优化：傻瓜式Docker部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印欢迎信息
print_header "KOOK消息转发系统 - Docker一键安装"
echo ""

# 检查Docker
echo "🔍 检查Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker未安装！"
    echo ""
    echo "请先安装Docker："
    echo "  Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
    echo "  CentOS/RHEL:   sudo yum install docker docker-compose"
    echo "  macOS:         brew install docker docker-compose"
    echo ""
    exit 1
fi
print_success "Docker已安装: $(docker --version)"

# 检查Docker Compose
echo "🔍 检查Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose未安装！"
    echo ""
    echo "请先安装Docker Compose："
    echo "  sudo apt-get install docker-compose"
    echo ""
    exit 1
fi
print_success "Docker Compose已安装: $(docker-compose --version)"

# 检查Docker服务
echo "🔍 检查Docker服务..."
if ! docker info &> /dev/null; then
    print_error "Docker服务未运行！"
    echo ""
    echo "请启动Docker服务："
    echo "  sudo systemctl start docker"
    echo ""
    exit 1
fi
print_success "Docker服务正在运行"

echo ""
print_header "开始部署"
echo ""

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/{config,images,logs,redis}
chmod -R 755 data
print_success "数据目录创建完成"

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose down || true
print_success "旧容器已停止"

# 构建镜像
echo "🔨 构建Docker镜像..."
echo "  （这可能需要几分钟时间，请耐心等待...）"
if docker-compose build --no-cache; then
    print_success "镜像构建成功"
else
    print_error "镜像构建失败"
    exit 1
fi

# 启动容器
echo "🚀 启动容器..."
if docker-compose up -d; then
    print_success "容器启动成功"
else
    print_error "容器启动失败"
    exit 1
fi

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:9527/health &> /dev/null; then
    print_success "服务运行正常"
else
    print_warning "服务可能未就绪，请稍等片刻"
fi

echo ""
print_header "部署完成"
echo ""

echo "访问地址："
echo "  Web界面: http://localhost:9527"
echo "  API文档: http://localhost:9527/docs"
echo ""

echo "常用命令："
echo "  查看日志:   docker-compose logs -f"
echo "  停止服务:   docker-compose stop"
echo "  启动服务:   docker-compose start"
echo "  重启服务:   docker-compose restart"
echo "  卸载服务:   docker-compose down -v"
echo ""

echo "数据目录："
echo "  配置文件:   ./data/config/"
echo "  图片缓存:   ./data/images/"
echo "  日志文件:   ./data/logs/"
echo ""

print_success "安装完成！现在可以访问 http://localhost:9527 开始使用"
