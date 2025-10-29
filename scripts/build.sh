#!/bin/bash
# KOOK消息转发系统 - 一键打包脚本（Linux/macOS）
# ✅ P1-1优化：简化版打包脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "${BLUE}[步骤] $1${NC}"
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
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 读取版本号
VERSION=$(cat VERSION 2>/dev/null || echo "1.0.0")

# 打印欢迎信息
print_header "KOOK消息转发系统 v$VERSION - 一键打包"

echo "当前系统: $(uname -s) $(uname -m)"
echo "Python版本: $(python3 --version)"
echo "Node版本: $(node --version 2>/dev/null || echo '未安装')"
echo ""

# 检查必要工具
check_tools() {
    print_step "检查必要工具..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js未安装，将跳过前端打包"
        SKIP_FRONTEND=true
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        print_warning "npm未安装，将跳过前端打包"
        SKIP_FRONTEND=true
    fi
    
    print_success "工具检查完成"
}

# 安装Python依赖
install_python_deps() {
    print_step "安装Python依赖..."
    
    cd backend
    python3 -m pip install -r requirements.txt
    python3 -m pip install pyinstaller
    cd ..
    
    print_success "Python依赖安装完成"
}

# 下载Chromium
download_chromium() {
    print_step "下载Chromium浏览器..."
    
    python3 -m playwright install chromium --with-deps || {
        print_warning "Chromium下载失败，继续..."
    }
    
    print_success "Chromium准备完成"
}

# 打包后端
build_backend() {
    print_step "打包Python后端..."
    
    python3 -m PyInstaller build/pyinstaller.spec --clean --noconfirm || {
        print_error "后端打包失败"
        return 1
    }
    
    print_success "后端打包成功"
}

# 打包前端
build_frontend() {
    if [ "$SKIP_FRONTEND" = true ]; then
        print_warning "跳过前端打包"
        return 0
    fi
    
    print_step "打包Electron前端..."
    
    cd frontend
    
    # 安装依赖
    print_step "安装npm依赖..."
    npm install || {
        print_error "npm依赖安装失败"
        cd ..
        return 1
    }
    
    # 构建Vue应用
    print_step "构建Vue应用..."
    npm run build || {
        print_error "Vue构建失败"
        cd ..
        return 1
    }
    
    # 打包Electron
    print_step "打包Electron应用..."
    
    # 根据平台选择打包命令
    case "$(uname -s)" in
        Darwin*)
            npm run electron:build:mac || {
                print_error "Electron打包失败"
                cd ..
                return 1
            }
            ;;
        Linux*)
            npm run electron:build:linux || {
                print_error "Electron打包失败"
                cd ..
                return 1
            }
            ;;
        *)
            print_error "不支持的平台: $(uname -s)"
            cd ..
            return 1
            ;;
    esac
    
    cd ..
    
    print_success "前端打包成功"
}

# 复制文件到dist目录
collect_files() {
    print_step "收集打包文件..."
    
    # 创建dist目录
    mkdir -p dist
    
    # 复制前端打包结果
    if [ -d "frontend/dist-electron" ]; then
        cp -r frontend/dist-electron/* dist/ 2>/dev/null || true
    fi
    
    # 列出生成的文件
    print_success "打包文件已收集到 dist/ 目录"
    echo ""
    echo "生成的文件："
    ls -lh dist/ | tail -n +2 | awk '{printf "  📦 %s (%s)\n", $9, $5}'
}

# 清理构建文件
clean_build() {
    print_step "清理旧的构建文件..."
    
    rm -rf dist
    rm -rf build
    rm -rf frontend/dist
    rm -rf frontend/dist-electron
    rm -rf backend/dist
    rm -rf backend/build
    
    print_success "清理完成"
}

# 主流程
main() {
    # 解析参数
    SKIP_FRONTEND=false
    
    for arg in "$@"; do
        case $arg in
            --clean)
                clean_build
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                ;;
            --help)
                echo "使用方法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --clean           清理旧的构建文件"
                echo "  --skip-frontend   跳过前端打包"
                echo "  --help            显示此帮助信息"
                exit 0
                ;;
        esac
    done
    
    # 执行打包流程
    check_tools
    
    print_header "第1步：安装依赖"
    install_python_deps
    
    print_header "第2步：准备Chromium"
    download_chromium
    
    print_header "第3步：打包后端"
    build_backend || exit 1
    
    print_header "第4步：打包前端"
    build_frontend || exit 1
    
    print_header "第5步：收集文件"
    collect_files
    
    print_header "打包完成"
    print_success "所有组件打包成功！"
    echo ""
    echo "安装包位置: ./dist/"
    echo ""
    echo "下一步："
    echo "  1. 测试安装包"
    echo "  2. 签名安装包（如需发布）"
    echo "  3. 上传到发布平台"
}

# 运行主流程
main "$@"
