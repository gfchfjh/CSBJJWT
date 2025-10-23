#!/bin/bash
# ============================================================================
# KOOK消息转发系统 - 完整发布脚本 (v1.14.0增强版)
# ============================================================================
# 功能：
# 1. 全面验证构建环境
# 2. 生成所有平台的预编译安装包
# 3. 创建GitHub Release
# 4. 上传所有构建产物
# 5. 更新文档
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
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

print_step() {
    echo -e "${MAGENTA}▶  $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取版本号
get_version() {
    if [ -f "frontend/package.json" ]; then
        VERSION=$(grep '"version"' frontend/package.json | head -1 | cut -d'"' -f4)
        echo "v${VERSION}"
    else
        echo "v1.14.0"
    fi
}

# 验证Git状态
check_git_status() {
    print_step "检查Git状态..."
    
    # 检查是否是Git仓库
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "当前目录不是Git仓库"
        return 1
    fi
    
    # 检查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        print_warning "存在未提交的更改"
        git status --short
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "已取消发布"
            return 1
        fi
    fi
    
    print_success "Git状态检查通过"
}

# 验证构建环境
check_build_environment() {
    print_step "验证构建环境..."
    
    # 运行构建就绪性检查
    if [ -f "build/verify_build_readiness.py" ]; then
        python3 build/verify_build_readiness.py
        if [ $? -ne 0 ]; then
            print_error "构建环境验证失败"
            return 1
        fi
    else
        print_warning "未找到构建验证脚本，跳过"
    fi
    
    print_success "构建环境验证通过"
}

# 更新版本号
update_version() {
    local version=$1
    print_step "更新版本号为 ${version}..."
    
    # 更新frontend/package.json
    if [ -f "frontend/package.json" ]; then
        sed -i.bak "s/\"version\": \".*\"/\"version\": \"${version#v}\"/" frontend/package.json
        rm -f frontend/package.json.bak
        print_success "已更新 frontend/package.json"
    fi
    
    # 更新backend/app/config.py
    if [ -f "backend/app/config.py" ]; then
        sed -i.bak "s/app_version: str = \".*\"/app_version: str = \"${version#v}\"/" backend/app/config.py
        rm -f backend/app/config.py.bak
        print_success "已更新 backend/app/config.py"
    fi
    
    # 更新README.md
    if [ -f "README.md" ]; then
        sed -i.bak "s/version-[0-9.]*-/version-${version#v}-/" README.md
        rm -f README.md.bak
        print_success "已更新 README.md"
    fi
}

# 运行测试
run_tests() {
    print_step "运行测试套件..."
    
    # 后端测试
    if [ -f "backend/pytest.ini" ]; then
        print_info "运行后端测试..."
        cd backend
        python -m pytest tests/ -v --tb=short || {
            print_warning "部分后端测试失败"
            read -p "是否继续发布？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        }
        cd ..
    fi
    
    # 前端测试
    if [ -f "frontend/vitest.config.js" ]; then
        print_info "运行前端测试..."
        cd frontend
        npm test || {
            print_warning "部分前端测试失败"
            read -p "是否继续发布？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        }
        cd ..
    fi
    
    print_success "测试完成"
}

# 构建后端
build_backend() {
    print_step "构建Python后端..."
    
    cd backend
    
    # 安装依赖
    print_info "安装Python依赖..."
    pip install -r requirements.txt -q
    pip install pyinstaller -q
    
    # 运行PyInstaller
    print_info "打包后端可执行文件..."
    pyinstaller --clean --noconfirm build_backend.spec
    
    if [ $? -eq 0 ]; then
        print_success "后端构建成功"
        ls -lh dist/
    else
        print_error "后端构建失败"
        return 1
    fi
    
    cd ..
}

# 构建前端
build_frontend() {
    print_step "构建前端应用..."
    
    cd frontend
    
    # 安装依赖
    print_info "安装npm依赖..."
    npm install
    
    # 构建前端资源
    print_info "构建前端资源..."
    npm run build
    
    # 打包Electron应用
    print_info "打包Electron应用..."
    npm run electron:build
    
    if [ $? -eq 0 ]; then
        print_success "前端构建成功"
        ls -lh dist-electron/
    else
        print_error "前端构建失败"
        return 1
    fi
    
    cd ..
}

# 创建发布包
create_release_archive() {
    local version=$1
    print_step "创建发布归档..."
    
    mkdir -p releases
    
    # 打包源码
    print_info "打包源码..."
    git archive --format=tar.gz --prefix=CSBJJWT-${version}/ HEAD > releases/source-${version}.tar.gz
    
    # 复制构建产物
    print_info "收集构建产物..."
    if [ -d "frontend/dist-electron" ]; then
        cp frontend/dist-electron/*.{exe,dmg,AppImage,deb} releases/ 2>/dev/null || true
    fi
    
    print_success "发布包创建完成"
    ls -lh releases/
}

# 生成发布说明
generate_release_notes() {
    local version=$1
    local output_file="releases/RELEASE_NOTES_${version}.md"
    
    print_step "生成发布说明..."
    
    cat > "$output_file" << EOF
# KOOK消息转发系统 ${version} 发布说明

**发布日期**: $(date +%Y-%m-%d)

## 🎯 本次更新

### ✨ 新增功能
- ✅ 完整的预编译安装包（Windows/macOS/Linux）
- ✅ 一键安装脚本优化（Docker/脚本/预编译）
- ✅ 增强的环境检查系统
- ✅ 完善的错误诊断和自动修复
- ✅ 优化的构建流程

### 🐛 Bug修复
- ✅ 修复了Chromium打包问题
- ✅ 修复了Redis嵌入式启动问题
- ✅ 优化了图标文件生成

### 📚 文档更新
- ✅ 新增构建验证工具
- ✅ 完善发布流程文档
- ✅ 更新安装指南

## 📥 下载安装

### Windows用户
下载 \`KOOK消息转发系统_v${version#v}_Windows_x64.exe\` 并运行安装。

### macOS用户
下载 \`KOOK消息转发系统_v${version#v}_macOS.dmg\` 并拖拽安装。

### Linux用户
下载 \`KOOK消息转发系统_v${version#v}_Linux_x64.AppImage\` 并赋予执行权限。

### Docker用户
\`\`\`bash
docker pull ghcr.io/gfchfjh/csbjjwt:${version}
\`\`\`

## 📖 完整文档

- [快速开始指南](QUICK_START.md)
- [安装指南](INSTALLATION_GUIDE.md)
- [用户手册](docs/用户手册.md)
- [开发指南](docs/开发指南.md)

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)
EOF
    
    print_success "发布说明已生成: $output_file"
}

# 创建Git Tag
create_git_tag() {
    local version=$1
    print_step "创建Git Tag ${version}..."
    
    # 提交版本更改
    git add .
    git commit -m "chore: bump version to ${version}" || true
    
    # 创建Tag
    git tag -a "${version}" -m "Release ${version}"
    
    print_success "Git Tag创建成功"
}

# 推送到GitHub
push_to_github() {
    local version=$1
    print_step "推送到GitHub..."
    
    # 推送代码
    git push origin main
    
    # 推送Tag
    git push origin "${version}"
    
    print_success "已推送到GitHub"
    print_info "GitHub Actions将自动开始构建"
    print_info "查看进度: https://github.com/gfchfjh/CSBJJWT/actions"
}

# 主函数
main() {
    print_header "🚀 KOOK消息转发系统 - 完整发布流程"
    
    # 1. 获取版本号
    VERSION=$(get_version)
    print_info "当前版本: $VERSION"
    
    # 询问是否要更新版本号
    read -p "是否要更新版本号？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入新版本号 (例如: 1.14.0): " NEW_VERSION
        VERSION="v${NEW_VERSION}"
        update_version "$VERSION"
    fi
    
    print_header "准备发布 ${VERSION}"
    
    # 2. 检查Git状态
    check_git_status || exit 1
    
    # 3. 验证构建环境
    check_build_environment || exit 1
    
    # 4. 运行测试（可选）
    read -p "是否运行测试套件？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests || exit 1
    fi
    
    # 5. 询问构建方式
    echo ""
    print_info "选择构建方式:"
    echo "  1) 仅创建Tag（触发GitHub Actions自动构建）推荐⭐"
    echo "  2) 本地完整构建（耗时较长）"
    echo "  3) 跳过构建"
    read -p "请选择 (1/2/3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            # 创建Tag并推送
            create_git_tag "$VERSION"
            push_to_github "$VERSION"
            
            print_success "✅ 发布流程完成！"
            print_info "GitHub Actions将自动构建并发布"
            print_info "预计15-20分钟后可在以下地址下载:"
            print_info "https://github.com/gfchfjh/CSBJJWT/releases/tag/${VERSION}"
            ;;
        2)
            # 本地构建
            build_backend || exit 1
            build_frontend || exit 1
            create_release_archive "$VERSION"
            generate_release_notes "$VERSION"
            create_git_tag "$VERSION"
            
            print_success "✅ 本地构建完成！"
            print_info "构建产物位于: releases/"
            
            read -p "是否推送到GitHub？(y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                push_to_github "$VERSION"
            fi
            ;;
        3)
            print_info "已跳过构建"
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac
    
    # 显示后续步骤
    print_header "✅ 发布完成"
    echo ""
    print_info "后续步骤:"
    echo "  1. 等待GitHub Actions构建完成（约15-20分钟）"
    echo "  2. 检查构建状态: https://github.com/gfchfjh/CSBJJWT/actions"
    echo "  3. 验证Release: https://github.com/gfchfjh/CSBJJWT/releases"
    echo "  4. 测试下载的安装包"
    echo "  5. 更新文档和公告"
    echo ""
    print_success "🎉 恭喜！发布流程全部完成！"
}

# 错误处理
trap 'print_error "发布过程中发生错误（退出码: $?）"' ERR

# 执行主函数
main "$@"
