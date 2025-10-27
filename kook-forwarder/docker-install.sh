#!/bin/bash
# KOOK消息转发系统 - Docker一键安装脚本
# 适用于Linux/macOS，自动安装Docker并部署应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_header() {
    echo ""
    echo -e "${BLUE}========================================"
    echo -e "$1"
    echo -e "========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header "KOOK消息转发系统 - Docker一键安装"

echo -e "${GREEN}这个脚本将帮助您：${NC}"
echo "  ✅ 安装Docker和Docker Compose（如果需要）"
echo "  ✅ 创建配置文件"
echo "  ✅ 拉取最新镜像"
echo "  ✅ 启动所有服务"
echo "  ✅ 设置自动重启"
echo ""

read -p "是否继续？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "安装已取消"
    exit 0
fi

# 步骤1: 检查并安装Docker
print_header "步骤 1/5: 检查Docker环境"

if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_success "Docker已安装: $DOCKER_VERSION"
else
    print_warning "Docker未安装，开始自动安装..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "检测到Linux系统"
        
        # 使用Docker官方安装脚本
        print_info "下载Docker安装脚本..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        
        print_info "执行安装脚本..."
        sudo sh get-docker.sh
        
        # 添加当前用户到docker组
        print_info "配置Docker权限..."
        sudo usermod -aG docker $USER
        
        # 启动Docker服务
        sudo systemctl start docker
        sudo systemctl enable docker
        
        print_success "Docker安装完成"
        print_warning "请注销并重新登录以应用用户组更改"
        print_warning "或运行: newgrp docker"
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_error "请手动安装Docker Desktop for Mac"
        print_info "访问: https://www.docker.com/products/docker-desktop"
        exit 1
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
fi

# 步骤2: 检查Docker Compose
print_header "步骤 2/5: 检查Docker Compose"

if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    print_success "Docker Compose已安装"
else
    print_warning "Docker Compose未安装，开始自动安装..."
    
    # 下载Docker Compose
    print_info "下载Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose安装完成"
fi

# 步骤3: 下载项目
print_header "步骤 3/5: 获取项目代码"

if [ -d "CSBJJWT" ]; then
    print_warning "项目目录已存在，更新代码..."
    cd CSBJJWT
    git pull
else
    print_info "克隆项目仓库..."
    git clone https://github.com/gfchfjh/CSBJJWT.git
    cd CSBJJWT
fi

print_success "项目代码获取完成"

# 步骤4: 创建配置文件
print_header "步骤 4/5: 创建配置文件"

# 创建数据目录
mkdir -p data/logs data/images data/redis

# 创建.env文件（如果不存在）
if [ ! -f "backend/.env" ]; then
    print_info "创建默认配置文件..."
    cat > backend/.env << 'EOF'
# KOOK消息转发系统配置文件

# API服务
API_HOST=0.0.0.0
API_PORT=9527

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379

# 日志级别
LOG_LEVEL=INFO

# 图床配置
IMAGE_MAX_SIZE_GB=10
IMAGE_CLEANUP_DAYS=7

# 验证码识别（可选）
# CAPTCHA_2CAPTCHA_API_KEY=your_api_key_here

EOF
    print_success "配置文件已创建"
else
    print_warning "配置文件已存在，跳过"
fi

# 步骤5: 启动服务
print_header "步骤 5/5: 启动服务"

print_info "拉取/构建Docker镜像（首次运行需要几分钟）..."
docker-compose -f docker-compose.standalone.yml build

print_info "启动服务..."
docker-compose -f docker-compose.standalone.yml up -d

# 等待服务启动
print_info "等待服务启动..."
sleep 10

# 检查服务状态
print_info "检查服务状态..."
docker-compose -f docker-compose.standalone.yml ps

# 健康检查
print_info "执行健康检查..."
for i in {1..10}; do
    if curl -sf http://localhost:9527/health > /dev/null 2>&1; then
        print_success "服务启动成功！"
        break
    fi
    
    if [ $i -eq 10 ]; then
        print_error "服务启动超时，请检查日志"
        echo ""
        echo "查看日志："
        echo "  docker-compose -f docker-compose.standalone.yml logs -f"
        exit 1
    fi
    
    echo -n "."
    sleep 2
done

# 安装完成
print_header "🎉 安装完成！"

echo ""
echo -e "${GREEN}服务访问地址：${NC}"
echo "  • API服务: http://localhost:9527"
echo "  • 图床服务: http://localhost:9528"
echo "  • 健康检查: http://localhost:9527/health"
echo ""
echo -e "${BLUE}常用命令：${NC}"
echo "  • 查看日志: docker-compose -f docker-compose.standalone.yml logs -f"
echo "  • 停止服务: docker-compose -f docker-compose.standalone.yml stop"
echo "  • 启动服务: docker-compose -f docker-compose.standalone.yml start"
echo "  • 重启服务: docker-compose -f docker-compose.standalone.yml restart"
echo "  • 删除服务: docker-compose -f docker-compose.standalone.yml down"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "  1. 访问 http://localhost:9527 查看API状态"
echo "  2. 配置KOOK账号和转发Bot"
echo "  3. 查看文档：docs/快速开始指南.md"
echo ""
echo -e "${GREEN}享受自动化的消息转发！${NC}"
echo ""
