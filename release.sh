#!/bin/bash
# ============================================================================
# KOOK消息转发系统 - 一键发布脚本
# 自动化发布流程，创建GitHub Release
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "========================================"
    echo -e "${BLUE}$1${NC}"
    echo "========================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    print_error "不在git仓库目录中！"
    exit 1
fi

# 获取版本号
if [ -z "$1" ]; then
    print_error "请提供版本号，例如: ./release.sh v1.13.0"
    exit 1
fi

VERSION=$1

# 确保版本号以v开头
if [[ ! $VERSION =~ ^v ]]; then
    VERSION="v$VERSION"
fi

print_header "🚀 KOOK消息转发系统 - 发布 $VERSION"

# 1. 检查工作区状态
print_header "1️⃣  检查工作区状态"
if [ -n "$(git status --porcelain)" ]; then
    print_info "工作区有未提交的更改"
    read -p "是否提交所有更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "chore: prepare for $VERSION release"
        print_success "已提交所有更改"
    else
        print_error "请先提交所有更改"
        exit 1
    fi
else
    print_success "工作区干净"
fi

# 2. 检查是否在main分支
print_header "2️⃣  检查分支"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    print_error "当前分支: $CURRENT_BRANCH"
    print_error "请切换到main/master分支！"
    exit 1
fi
print_success "当前分支: $CURRENT_BRANCH"

# 3. 拉取最新代码
print_header "3️⃣  同步远程代码"
print_info "拉取最新代码..."
git pull origin $CURRENT_BRANCH
print_success "代码已同步"

# 4. 检查版本号是否已存在
print_header "4️⃣  检查版本号"
if git tag | grep -q "^$VERSION$"; then
    print_error "版本号 $VERSION 已存在！"
    read -p "是否删除现有Tag并重新创建？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d $VERSION
        git push origin :refs/tags/$VERSION
        print_success "已删除旧Tag"
    else
        exit 1
    fi
fi

# 5. 运行测试（如果有）
print_header "5️⃣  运行测试"
if [ -f "backend/pytest.ini" ]; then
    print_info "跳过测试（需要安装依赖）"
    # cd backend && python3 -m pytest tests/ -v || true
    # cd ..
else
    print_info "未找到测试配置，跳过"
fi

# 6. 更新版本号
print_header "6️⃣  更新版本号"
VERSION_NUM=${VERSION#v}
print_info "版本号: $VERSION_NUM"

# 更新frontend/package.json
if [ -f "frontend/package.json" ]; then
    sed -i.bak "s/\"version\": \".*\"/\"version\": \"$VERSION_NUM\"/" frontend/package.json
    rm -f frontend/package.json.bak
    print_success "已更新 frontend/package.json"
fi

# 提交版本号更改
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "chore: bump version to $VERSION"
    print_success "已提交版本号更改"
fi

# 7. 创建Tag
print_header "7️⃣  创建Git Tag"
git tag -a $VERSION -m "Release $VERSION - S+级易用优化版"
print_success "已创建Tag: $VERSION"

# 8. 推送到远程
print_header "8️⃣  推送到GitHub"
print_info "推送代码..."
git push origin $CURRENT_BRANCH
print_success "代码已推送"

print_info "推送Tag..."
git push origin $VERSION
print_success "Tag已推送"

# 9. 触发GitHub Actions
print_header "9️⃣  GitHub Actions"
print_success "已触发自动构建！"
echo ""
print_info "📊 查看构建进度:"
echo "   https://github.com/gfchfjh/CSBJJWT/actions"
echo ""
print_info "⏱️  预计时间: 30-60分钟"
echo ""
print_info "📦 构建完成后，访问:"
echo "   https://github.com/gfchfjh/CSBJJWT/releases/tag/$VERSION"

# 10. 完成
print_header "🎉 发布流程已启动！"
echo ""
echo -e "${GREEN}接下来：${NC}"
echo "  1. 等待GitHub Actions构建完成（30-60分钟）"
echo "  2. 检查构建结果: https://github.com/gfchfjh/CSBJJWT/actions"
echo "  3. 构建成功后，安装包会自动上传到Releases"
echo "  4. 编辑Release页面，添加更新说明"
echo "  5. 发布！"
echo ""
echo -e "${BLUE}Release页面:${NC}"
echo "  https://github.com/gfchfjh/CSBJJWT/releases/tag/$VERSION"
echo ""
echo -e "${GREEN}✅ 发布脚本执行完成！${NC}"
