#!/bin/bash
# ============================================================================
# KOOK消息转发系统 - 一键发布预编译安装包脚本
# 
# 功能：自动创建Git Tag并触发GitHub Actions构建
# 用途：生成 Windows/macOS/Linux 三平台安装包
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo ""
}

# 显示标题
clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}║   KOOK消息转发系统 - 一键发布预编译安装包        ║${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# 检查Git仓库
print_step "1️⃣  检查Git仓库状态"
if [ ! -d ".git" ]; then
    print_error "当前目录不是Git仓库"
    exit 1
fi
print_success "Git仓库检查通过"

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    print_warning "检测到未提交的更改："
    git status -s
    echo ""
    read -p "是否继续？未提交的更改不会包含在发布中。(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "发布已取消"
        exit 0
    fi
fi

# 获取当前版本
print_step "2️⃣  获取版本信息"
CURRENT_VERSION=$(grep '"version"' frontend/package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')
print_info "当前版本: v${CURRENT_VERSION}"

# 提示输入新版本号
echo ""
print_warning "请输入新版本号（格式：1.13.3），留空使用当前版本 v${CURRENT_VERSION}:"
read -p "新版本号: " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
    print_info "使用当前版本: v${NEW_VERSION}"
else
    print_info "新版本: v${NEW_VERSION}"
    
    # 确认是否更新版本号
    read -p "是否更新 package.json 中的版本号？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "更新 frontend/package.json 版本号..."
        sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" frontend/package.json
        rm frontend/package.json.bak 2>/dev/null || true
        print_success "版本号已更新"
        
        # 提交版本号更改
        git add frontend/package.json
        git commit -m "chore: bump version to v${NEW_VERSION}" || print_warning "没有需要提交的更改"
    fi
fi

VERSION_TAG="v${NEW_VERSION}"

# 检查Tag是否已存在
print_step "3️⃣  检查版本标签"
if git rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
    print_warning "标签 $VERSION_TAG 已存在"
    read -p "是否删除旧标签并创建新标签？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$VERSION_TAG"
        git push origin :refs/tags/"$VERSION_TAG" 2>/dev/null || print_warning "远程标签不存在或已删除"
        print_success "旧标签已删除"
    else
        print_error "发布已取消"
        exit 1
    fi
fi

# 显示发布清单
print_header "📋 发布前检查清单"
echo ""
echo "版本信息："
echo "  版本号: ${VERSION_TAG}"
echo "  当前分支: $(git branch --show-current)"
echo "  最后提交: $(git log -1 --pretty=format:'%h - %s (%an, %ar)')"
echo ""
echo "构建内容："
echo "  ✅ Windows 安装包 (.exe, ~450MB)"
echo "  ✅ macOS 安装包 (.dmg, ~480MB)"
echo "  ✅ Linux 安装包 (.AppImage, ~420MB)"
echo "  ✅ Docker 镜像 (ghcr.io/gfchfjh/csbjjwt:${NEW_VERSION})"
echo ""
echo "构建方式："
echo "  GitHub Actions 自动构建（需要15-20分钟）"
echo ""
echo "发布位置："
echo "  https://github.com/gfchfjh/CSBJJWT/releases/tag/${VERSION_TAG}"
echo ""

read -p "确认创建发布？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "发布已取消"
    exit 0
fi

# 创建并推送Tag
print_step "4️⃣  创建Git Tag"
git tag -a "$VERSION_TAG" -m "Release ${VERSION_TAG}

🎉 KOOK消息转发系统 ${VERSION_TAG}

## 📦 安装包
- Windows: KookForwarder-Setup-${NEW_VERSION}.exe
- macOS: KookForwarder-${NEW_VERSION}.dmg
- Linux: KookForwarder-${NEW_VERSION}.AppImage

## 🐳 Docker镜像
\`\`\`bash
docker pull ghcr.io/gfchfjh/csbjjwt:${NEW_VERSION}
\`\`\`

## 📚 文档
- 快速开始: https://github.com/gfchfjh/CSBJJWT/blob/main/QUICK_START.md
- 完整文档: https://github.com/gfchfjh/CSBJJWT/blob/main/README.md

---
自动生成的发布说明
"
print_success "Tag ${VERSION_TAG} 已创建"

# 推送到远程
print_step "5️⃣  推送到GitHub"
print_info "推送代码到远程仓库..."
git push origin $(git branch --show-current)

print_info "推送标签到远程仓库..."
git push origin "$VERSION_TAG"
print_success "推送完成"

# 显示构建状态
print_header "🚀 构建已触发"
echo ""
print_success "Git Tag ${VERSION_TAG} 已成功推送到GitHub！"
echo ""
echo -e "${CYAN}GitHub Actions 将自动执行以下任务：${NC}"
echo "  1️⃣  构建 Python 后端（3个平台）"
echo "  2️⃣  构建 Electron 应用（Windows/macOS/Linux）"
echo "  3️⃣  构建 Docker 镜像"
echo "  4️⃣  创建 GitHub Release"
echo "  5️⃣  上传所有安装包"
echo ""
echo -e "${YELLOW}⏱️  预计完成时间: 15-20 分钟${NC}"
echo ""
echo -e "${CYAN}📍 查看构建进度：${NC}"
echo "  https://github.com/gfchfjh/CSBJJWT/actions"
echo ""
echo -e "${CYAN}📦 发布页面（构建完成后可见）：${NC}"
echo "  https://github.com/gfchfjh/CSBJJWT/releases/tag/${VERSION_TAG}"
echo ""

# 询问是否在浏览器中打开
read -p "是否在浏览器中打开GitHub Actions页面？(Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    ACTIONS_URL="https://github.com/gfchfjh/CSBJJWT/actions"
    
    # 根据操作系统打开浏览器
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$ACTIONS_URL"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$ACTIONS_URL" 2>/dev/null || print_info "请手动打开: $ACTIONS_URL"
    else
        print_info "请手动打开: $ACTIONS_URL"
    fi
fi

# 显示后续步骤
print_header "✅ 发布流程已启动"
echo ""
echo -e "${GREEN}后续步骤：${NC}"
echo ""
echo "  1️⃣  监控构建进度"
echo "     访问: https://github.com/gfchfjh/CSBJJWT/actions"
echo "     等待所有构建任务完成（约15-20分钟）"
echo ""
echo "  2️⃣  验证发布"
echo "     访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/${VERSION_TAG}"
echo "     确认所有安装包已上传"
echo ""
echo "  3️⃣  测试安装包"
echo "     下载对应平台的安装包"
echo "     在本地测试安装和运行"
echo ""
echo "  4️⃣  更新文档"
echo "     更新 README.md 中的下载链接"
echo "     更新 CHANGELOG.md 添加版本历史"
echo ""
echo "  5️⃣  推广发布"
echo "     在社交媒体/论坛发布新版本信息"
echo "     通知用户升级"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 发布流程完成！请耐心等待GitHub Actions构建。${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""
