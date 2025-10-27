#!/bin/bash
#
# KOOK消息转发系统 - 后端构建脚本
# 版本: v6.0.0
# 支持平台: Windows, macOS, Linux
#
# 使用方法:
#   ./build_backend.sh [选项]
#
# 选项:
#   --pack-playwright   打包Playwright浏览器（增加300MB）
#   --clean            清理之前的构建
#   --test             构建后运行测试
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PACK_PLAYWRIGHT=false
CLEAN_BUILD=false
RUN_TESTS=false

# 解析参数
for arg in "$@"; do
    case $arg in
        --pack-playwright)
            PACK_PLAYWRIGHT=true
            ;;
        --clean)
            CLEAN_BUILD=true
            ;;
        --test)
            RUN_TESTS=true
            ;;
        *)
            echo -e "${RED}未知参数: $arg${NC}"
            exit 1
            ;;
    esac
done

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 打印标题
print_header() {
    echo ""
    echo "================================================================"
    echo -e "${GREEN}$1${NC}"
    echo "================================================================"
    echo ""
}

# 检测平台
detect_platform() {
    case "$(uname -s)" in
        Linux*)     PLATFORM=linux;;
        Darwin*)    PLATFORM=mac;;
        CYGWIN*|MINGW*|MSYS*) PLATFORM=windows;;
        *)          PLATFORM=unknown;;
    esac
    log_info "检测到平台: $PLATFORM"
}

# 检查依赖
check_dependencies() {
    log_step "检查构建依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装！"
        log_info "请安装Python 3.11+: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查PyInstaller
    if ! python3 -c "import PyInstaller" &> /dev/null 2>&1; then
        log_warn "PyInstaller 未安装，正在安装..."
        pip3 install pyinstaller
    fi
    
    PYINSTALLER_VERSION=$(pyinstaller --version 2>/dev/null || echo "未知")
    log_info "PyInstaller版本: $PYINSTALLER_VERSION"
    
    # 检查项目依赖
    if [ -f "backend/requirements.txt" ]; then
        log_info "检查项目依赖..."
        pip3 install -r backend/requirements.txt --quiet
    fi
    
    # 检查UPX（可选）
    if command -v upx &> /dev/null; then
        UPX_VERSION=$(upx --version 2>/dev/null | head -1 || echo "未知")
        log_info "UPX版本: $UPX_VERSION（将用于压缩）"
    else
        log_warn "UPX 未安装（可选），跳过压缩优化"
        log_info "安装UPX可减小30-50%体积: https://upx.github.io/"
    fi
    
    log_info "✅ 依赖检查完成"
}

# 准备Redis可执行文件
prepare_redis() {
    log_step "准备Redis可执行文件..."
    
    REDIS_DIR="redis"
    mkdir -p "$REDIS_DIR"
    
    case "$PLATFORM" in
        linux)
            if [ ! -f "$REDIS_DIR/redis-server-linux" ]; then
                log_info "下载Redis for Linux..."
                
                # 检查是否有wget或curl
                if command -v wget &> /dev/null; then
                    wget -O /tmp/redis.tar.gz https://download.redis.io/releases/redis-7.0.15.tar.gz
                elif command -v curl &> /dev/null; then
                    curl -L -o /tmp/redis.tar.gz https://download.redis.io/releases/redis-7.0.15.tar.gz
                else
                    log_error "需要wget或curl来下载Redis"
                    exit 1
                fi
                
                tar -xzf /tmp/redis.tar.gz -C /tmp
                cd /tmp/redis-7.0.15
                make -j$(nproc)
                cp src/redis-server "$REDIS_DIR/redis-server-linux"
                cd - > /dev/null
                rm -rf /tmp/redis.tar.gz /tmp/redis-7.0.15
                log_info "✅ Redis for Linux 构建完成"
            else
                log_info "✅ Redis for Linux 已存在"
            fi
            ;;
        mac)
            if [ ! -f "$REDIS_DIR/redis-server-mac" ]; then
                log_info "安装Redis for macOS..."
                if command -v brew &> /dev/null; then
                    brew install redis
                    cp $(which redis-server) "$REDIS_DIR/redis-server-mac"
                    log_info "✅ Redis for macOS 安装完成"
                else
                    log_error "macOS需要Homebrew来安装Redis"
                    log_info "安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                    exit 1
                fi
            else
                log_info "✅ Redis for macOS 已存在"
            fi
            ;;
        windows)
            if [ ! -f "$REDIS_DIR/redis-server.exe" ]; then
                log_info "下载Redis for Windows..."
                curl -L -o /tmp/redis.zip https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip
                unzip -q /tmp/redis.zip -d /tmp/redis
                cp /tmp/redis/redis-server.exe "$REDIS_DIR/"
                rm -rf /tmp/redis.zip /tmp/redis
                log_info "✅ Redis for Windows 下载完成"
            else
                log_info "✅ Redis for Windows 已存在"
            fi
            ;;
    esac
    
    # 创建redis.conf（如果不存在）
    if [ ! -f "$REDIS_DIR/redis.conf" ]; then
        log_info "创建Redis配置文件..."
        cat > "$REDIS_DIR/redis.conf" << 'EOF'
# Redis配置文件（KOOK消息转发系统）
port 6379
bind 127.0.0.1
protected-mode yes
daemonize no

# 持久化
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
dbfilename dump.rdb

# AOF持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# 日志
loglevel notice
EOF
        log_info "✅ Redis配置文件创建完成"
    fi
}

# 清理之前的构建
clean_build() {
    if [ "$CLEAN_BUILD" = true ]; then
        log_step "清理之前的构建..."
        
        cd backend
        
        if [ -d "build" ]; then
            rm -rf build
            log_info "已删除: build/"
        fi
        
        if [ -d "dist" ]; then
            rm -rf dist
            log_info "已删除: dist/"
        fi
        
        if [ -f "*.spec" ]; then
            rm -f *.spec
            log_info "已删除: *.spec"
        fi
        
        cd ..
        
        log_info "✅ 清理完成"
    fi
}

# 执行PyInstaller打包
build_backend() {
    log_step "开始打包后端..."
    
    cd backend
    
    # 设置环境变量
    if [ "$PACK_PLAYWRIGHT" = true ]; then
        export PACK_PLAYWRIGHT=true
        log_warn "将打包Playwright浏览器（约300MB），请耐心等待..."
    else
        export PACK_PLAYWRIGHT=false
        log_info "Playwright浏览器将在首次启动时下载（需要网络）"
    fi
    
    # 执行打包
    log_info "执行PyInstaller..."
    pyinstaller --clean build_backend_enhanced.spec
    
    # 检查结果
    if [ "$PLATFORM" = "windows" ]; then
        EXEC_FILE="dist/KookForwarder-Backend.exe"
    else
        EXEC_FILE="dist/KookForwarder-Backend"
    fi
    
    if [ -f "$EXEC_FILE" ]; then
        # 计算文件大小
        if [ "$PLATFORM" = "mac" ]; then
            SIZE=$(du -h "$EXEC_FILE" | cut -f1)
        else
            SIZE=$(du -h "$EXEC_FILE" | cut -f1)
        fi
        
        log_info "✅ 后端打包成功！"
        log_info "文件路径: backend/$EXEC_FILE"
        log_info "文件大小: $SIZE"
        
        # 添加执行权限（Linux/macOS）
        if [ "$PLATFORM" != "windows" ]; then
            chmod +x "$EXEC_FILE"
            log_info "✅ 已添加执行权限"
        fi
    else
        log_error "打包失败！"
        cd ..
        exit 1
    fi
    
    cd ..
}

# 测试后端
test_backend() {
    if [ "$RUN_TESTS" = true ]; then
        log_step "测试打包后的后端..."
        
        cd backend/dist
        
        # 启动后端
        if [ "$PLATFORM" = "windows" ]; then
            ./KookForwarder-Backend.exe &
        else
            ./KookForwarder-Backend &
        fi
        
        BACKEND_PID=$!
        log_info "后端进程PID: $BACKEND_PID"
        
        # 等待启动
        log_info "等待后端启动..."
        sleep 5
        
        # 测试健康检查
        log_info "测试健康检查端点..."
        if command -v curl &> /dev/null; then
            if curl -f http://localhost:9527/health > /dev/null 2>&1; then
                log_info "✅ 后端测试通过！"
            else
                log_error "❌ 后端健康检查失败！"
                kill $BACKEND_PID
                cd ../..
                exit 1
            fi
        else
            log_warn "curl未安装，跳过健康检查测试"
        fi
        
        # 停止后端
        log_info "停止后端进程..."
        kill $BACKEND_PID
        wait $BACKEND_PID 2>/dev/null || true
        
        cd ../..
    fi
}

# 生成构建报告
generate_report() {
    log_step "生成构建报告..."
    
    REPORT_FILE="build_report.txt"
    
    cat > "$REPORT_FILE" << EOF
================================================================
KOOK消息转发系统 - 后端构建报告
================================================================

构建时间: $(date)
构建平台: $PLATFORM
Python版本: $(python3 --version)
PyInstaller版本: $(pyinstaller --version 2>/dev/null || echo "未知")

================================================================
构建配置
================================================================

打包Playwright: $PACK_PLAYWRIGHT
清理构建: $CLEAN_BUILD
运行测试: $RUN_TESTS

================================================================
输出文件
================================================================

EOF

    if [ "$PLATFORM" = "windows" ]; then
        echo "可执行文件: backend/dist/KookForwarder-Backend.exe" >> "$REPORT_FILE"
        if [ -f "backend/dist/KookForwarder-Backend.exe" ]; then
            ls -lh backend/dist/KookForwarder-Backend.exe >> "$REPORT_FILE"
        fi
    else
        echo "可执行文件: backend/dist/KookForwarder-Backend" >> "$REPORT_FILE"
        if [ -f "backend/dist/KookForwarder-Backend" ]; then
            ls -lh backend/dist/KookForwarder-Backend >> "$REPORT_FILE"
        fi
    fi
    
    cat >> "$REPORT_FILE" << EOF

================================================================
下一步
================================================================

1. 测试可执行文件:
   cd backend/dist
   ./KookForwarder-Backend

2. 构建前端:
   cd frontend
   npm run build

3. 打包完整安装包:
   ./build_complete_installer.sh

================================================================
EOF
    
    log_info "✅ 构建报告已生成: $REPORT_FILE"
}

# 主函数
main() {
    print_header "KOOK消息转发系统 - 后端构建脚本"
    
    log_info "开始时间: $(date)"
    
    detect_platform
    check_dependencies
    prepare_redis
    clean_build
    build_backend
    test_backend
    generate_report
    
    print_header "✅ 所有构建任务完成！"
    
    log_info "输出目录: backend/dist/"
    log_info "构建报告: build_report.txt"
    log_info ""
    log_info "下一步:"
    log_info "  1. 测试后端: cd backend/dist && ./KookForwarder-Backend"
    log_info "  2. 构建前端: cd frontend && npm run build"
    log_info "  3. 打包安装包: ./build_complete_installer.sh"
    
    log_info ""
    log_info "结束时间: $(date)"
}

# 运行主函数
main "$@"
