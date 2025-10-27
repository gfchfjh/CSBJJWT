#!/bin/bash
# KOOK消息转发系统 - 一键安装脚本（Linux/macOS）
# 自动安装所有依赖和配置环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    print_info "检测到操作系统: $OS ($DISTRO)"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 安装系统依赖
install_system_dependencies() {
    print_header "步骤 1/6: 安装系统依赖"
    
    if [ "$OS" == "linux" ]; then
        print_info "更新包管理器..."
        if [ "$DISTRO" == "ubuntu" ] || [ "$DISTRO" == "debian" ]; then
            sudo apt-get update
            print_info "安装基础依赖..."
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                git \
                curl \
                wget \
                build-essential \
                libssl-dev \
                libffi-dev
        elif [ "$DISTRO" == "centos" ] || [ "$DISTRO" == "rhel" ]; then
            sudo yum update -y
            sudo yum install -y \
                python3 \
                python3-pip \
                git \
                curl \
                wget \
                gcc \
                openssl-devel \
                libffi-devel
        elif [ "$DISTRO" == "arch" ]; then
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                git \
                curl \
                wget \
                base-devel
        fi
    elif [ "$OS" == "macos" ]; then
        if ! command_exists brew; then
            print_info "安装Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        print_info "安装基础依赖..."
        brew install python@3.11 git curl wget
    fi
    
    print_success "系统依赖安装完成"
}

# 安装Redis
install_redis() {
    print_header "步骤 2/6: 安装Redis"
    
    if command_exists redis-server; then
        print_warning "Redis已安装，跳过"
        return
    fi
    
    if [ "$OS" == "linux" ]; then
        if [ "$DISTRO" == "ubuntu" ] || [ "$DISTRO" == "debian" ]; then
            sudo apt-get install -y redis-server
            sudo systemctl enable redis-server
            sudo systemctl start redis-server
        elif [ "$DISTRO" == "centos" ] || [ "$DISTRO" == "rhel" ]; then
            sudo yum install -y redis
            sudo systemctl enable redis
            sudo systemctl start redis
        elif [ "$DISTRO" == "arch" ]; then
            sudo pacman -S --noconfirm redis
            sudo systemctl enable redis
            sudo systemctl start redis
        fi
    elif [ "$OS" == "macos" ]; then
        brew install redis
        brew services start redis
    fi
    
    print_success "Redis安装完成"
}

# 安装Node.js和npm
install_nodejs() {
    print_header "步骤 3/6: 安装Node.js"
    
    if command_exists node && command_exists npm; then
        NODE_VERSION=$(node -v)
        print_warning "Node.js已安装: $NODE_VERSION，跳过"
        return
    fi
    
    if [ "$OS" == "linux" ]; then
        print_info "安装Node.js 18.x..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        if [ "$DISTRO" == "ubuntu" ] || [ "$DISTRO" == "debian" ]; then
            sudo apt-get install -y nodejs
        elif [ "$DISTRO" == "centos" ] || [ "$DISTRO" == "rhel" ]; then
            sudo yum install -y nodejs
        fi
    elif [ "$OS" == "macos" ]; then
        brew install node@18
    fi
    
    print_success "Node.js安装完成"
}

# 克隆项目
clone_project() {
    print_header "步骤 4/6: 获取项目代码"
    
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
}

# 安装Python依赖
install_python_dependencies() {
    print_header "步骤 5/6: 安装Python依赖"
    
    print_info "创建Python虚拟环境..."
    python3 -m venv venv
    
    print_info "激活虚拟环境..."
    source venv/bin/activate
    
    print_info "升级pip..."
    pip install --upgrade pip
    
    print_info "安装Python依赖包..."
    cd backend
    pip install -r requirements.txt
    
    print_info "安装Playwright浏览器..."
    playwright install chromium
    playwright install-deps chromium
    
    cd ..
    
    print_success "Python依赖安装完成"
}

# 安装前端依赖
install_frontend_dependencies() {
    print_header "步骤 6/6: 安装前端依赖"
    
    cd frontend
    
    print_info "安装npm依赖..."
    npm install
    
    cd ..
    
    print_success "前端依赖安装完成"
}

# 创建启动脚本
create_start_script() {
    print_header "创建启动脚本"
    
    cat > start.sh << 'EOF'
#!/bin/bash
# KOOK消息转发系统 - 启动脚本

# 激活Python虚拟环境
source venv/bin/activate

# 启动后端服务
cd backend
python -m app.main &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端服务
cd frontend
npm run electron:dev &
FRONTEND_PID=$!
cd ..

echo "✅ KOOK消息转发系统已启动"
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户终止
wait
EOF

    chmod +x start.sh
    
    print_success "启动脚本创建完成"
}

# 创建配置文件
create_config() {
    print_header "创建配置文件"
    
    if [ ! -f backend/.env ]; then
        cat > backend/.env << 'EOF'
# KOOK消息转发系统配置文件

# API服务
API_HOST=127.0.0.1
API_PORT=9527

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 日志级别
LOG_LEVEL=INFO

# 图床配置
IMAGE_MAX_SIZE_GB=10
IMAGE_CLEANUP_DAYS=7

# 验证码识别（可选）
# CAPTCHA_2CAPTCHA_API_KEY=your_api_key_here

EOF
        print_success "配置文件已创建: backend/.env"
    else
        print_warning "配置文件已存在，跳过"
    fi
}

# 主函数
main() {
    clear
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                               ║${NC}"
    echo -e "${GREEN}║   KOOK消息转发系统 - 一键安装脚本 v1.0       ║${NC}"
    echo -e "${GREEN}║                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    
    print_warning "此脚本将安装以下组件："
    echo "  • Python 3.11+ 及依赖"
    echo "  • Node.js 18+ 及npm"
    echo "  • Redis服务器"
    echo "  • Playwright浏览器"
    echo "  • 项目依赖包"
    echo ""
    
    read -p "是否继续安装？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "安装已取消"
        exit 0
    fi
    
    # 检测操作系统
    detect_os
    
    # 执行安装步骤
    install_system_dependencies
    install_redis
    install_nodejs
    clone_project
    install_python_dependencies
    install_frontend_dependencies
    create_start_script
    create_config
    
    # 安装完成
    print_header "🎉 安装完成！"
    
    echo ""
    echo -e "${GREEN}下一步操作：${NC}"
    echo "  1. 进入项目目录: cd CSBJJWT"
    echo "  2. 启动服务: ./start.sh"
    echo "  3. 或使用Docker: docker-compose up -d"
    echo ""
    echo -e "${BLUE}查看文档：${NC}"
    echo "  • 用户手册: docs/完整用户手册.md"
    echo "  • 视频教程: docs/视频教程指南.md"
    echo "  • 故障排查: README.md#故障排查"
    echo ""
    echo -e "${YELLOW}提示：${NC}"
    echo "  • 首次启动会打开配置向导"
    echo "  • 需要准备KOOK账号Cookie"
    echo "  • 配置至少一个转发Bot（Discord/Telegram/飞书）"
    echo ""
    print_success "感谢使用KOOK消息转发系统！"
}

# 运行主函数
main
