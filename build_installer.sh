#!/bin/bash
# ============================================================================
# KOOK消息转发系统 - 一键构建脚本 (Linux/macOS)
# v1.13.0 新增 (P0-4优化)
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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
    echo "========================================"
    echo -e "${BLUE}$1${NC}"
    echo "========================================"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主函数
main() {
    print_header "🚀 KOOK消息转发系统 - 一键构建安装包"
    
    # 1. 环境检查
    print_header "1️⃣  检查构建环境"
    
    print_info "检查Python..."
    if ! command_exists python3; then
        print_error "未安装Python3，请先安装Python 3.11+"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python版本: $PYTHON_VERSION"
    
    print_info "检查Node.js..."
    if ! command_exists node; then
        print_error "未安装Node.js，请先安装Node.js 18+"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js版本: $NODE_VERSION"
    
    print_info "检查npm..."
    if ! command_exists npm; then
        print_error "未安装npm"
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm版本: $NPM_VERSION"
    
    # 2. 安装依赖
    print_header "2️⃣  安装依赖"
    
    print_info "安装Python依赖..."
    pip3 install -r backend/requirements.txt
    pip3 install pyinstaller
    print_success "Python依赖安装完成"
    
    print_info "安装Playwright浏览器..."
    playwright install chromium
    print_success "Playwright浏览器安装完成"
    
    print_info "安装前端依赖..."
    cd frontend
    npm install
    cd ..
    print_success "前端依赖安装完成"
    
    # 3. 准备Redis（跳过，使用系统Redis或后续打包）
    print_header "3️⃣  准备Redis"
    print_warning "Redis准备：将使用系统Redis或嵌入式Redis"
    print_info "如需打包Redis，请运行: python build/prepare_redis.py"
    
    # 4. 构建后端
    print_header "4️⃣  构建Python后端"
    print_info "开始打包后端..."
    if [ -f "build/build_backend.py" ]; then
        python3 build/build_backend.py
        print_success "后端构建完成"
    else
        print_warning "build/build_backend.py不存在，跳过后端构建"
        print_info "如需打包后端，请完善build/build_backend.py"
    fi
    
    # 5. 构建前端
    print_header "5️⃣  构建前端资源"
    print_info "开始构建前端..."
    cd frontend
    npm run build
    cd ..
    print_success "前端构建完成"
    
    # 6. 整合Electron应用
    print_header "6️⃣  整合Electron应用"
    print_info "整合后端可执行文件到Electron..."
    
    # 创建backend目录
    mkdir -p frontend/electron/backend
    
    # 如果后端可执行文件存在，复制它
    if [ -f "backend/dist/KookForwarder" ]; then
        cp backend/dist/KookForwarder frontend/electron/backend/
        print_success "后端可执行文件已复制"
    elif [ -f "dist/KookForwarder" ]; then
        cp dist/KookForwarder frontend/electron/backend/
        print_success "后端可执行文件已复制"
    else
        print_warning "后端可执行文件不存在，跳过复制"
        print_info "Electron应用将使用Python源码模式运行"
    fi
    
    # 7. 生成安装包
    print_header "7️⃣  生成安装包"
    print_info "开始打包Electron应用..."
    
    cd frontend
    
    # 根据平台选择构建目标
    OS=$(uname -s)
    case "$OS" in
        Linux*)
            print_info "检测到Linux系统，构建AppImage..."
            npm run electron:build:linux
            ;;
        Darwin*)
            print_info "检测到macOS系统，构建DMG..."
            npm run electron:build:mac
            ;;
        *)
            print_warning "未知系统: $OS，尝试构建所有平台..."
            npm run electron:build
            ;;
    esac
    
    cd ..
    print_success "安装包生成完成"
    
    # 8. 显示输出
    print_header "🎉 构建完成！"
    echo ""
    print_info "安装包位置:"
    
    if [ -d "frontend/dist-electron" ]; then
        ls -lh frontend/dist-electron/*.{dmg,AppImage,exe} 2>/dev/null || print_warning "未找到安装包文件"
    else
        print_warning "dist-electron目录不存在"
    fi
    
    echo ""
    print_info "下一步操作:"
    echo "  1. 测试安装包: 运行生成的安装文件"
    echo "  2. 查看日志: 检查构建日志获取详细信息"
    echo "  3. 发布: 将安装包上传到GitHub Releases"
    echo ""
    
    print_success "构建流程全部完成！🎊"
}

# 错误处理
trap 'print_error "构建过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"
