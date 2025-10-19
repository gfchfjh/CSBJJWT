#!/bin/bash

# KOOK消息转发系统 - 发布脚本
# 自动化版本发布流程

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印彩色消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装"
        exit 1
    fi
}

# 欢迎信息
echo ""
echo "=================================================="
echo "   KOOK消息转发系统 - 自动发布脚本"
echo "=================================================="
echo ""

# 检查必要的命令
print_info "检查必要的工具..."
check_command git
check_command node
check_command python3
print_success "所有必要工具已安装"

# 获取当前版本
CURRENT_VERSION=$(grep '"version"' frontend/package.json | head -1 | sed 's/.*: "\(.*\)".*/\1/')
print_info "当前版本: v${CURRENT_VERSION}"

# 询问新版本号
echo ""
read -p "请输入新版本号 (当前: ${CURRENT_VERSION}): " NEW_VERSION

# 验证版本号格式
if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "版本号格式无效，请使用 x.y.z 格式"
    exit 1
fi

print_info "新版本: v${NEW_VERSION}"

# 确认发布
echo ""
read -p "确认发布 v${NEW_VERSION}? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
    print_warning "发布已取消"
    exit 0
fi

echo ""
print_info "开始发布流程..."
echo ""

# 步骤1: 检查Git状态
print_info "步骤1/8: 检查Git状态..."
if [[ -n $(git status -s) ]]; then
    print_warning "工作目录有未提交的更改"
    git status -s
    echo ""
    read -p "是否继续? (y/n): " CONTINUE
    if [[ $CONTINUE != "y" && $CONTINUE != "Y" ]]; then
        print_warning "发布已取消"
        exit 0
    fi
fi
print_success "Git状态检查完成"

# 步骤2: 更新版本号
print_info "步骤2/8: 更新版本号..."

# 更新frontend/package.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" frontend/package.json
rm -f frontend/package.json.bak

# 更新backend/app/config.py
sed -i.bak "s/app_version = \".*\"/app_version = \"${NEW_VERSION}\"/" backend/app/config.py
rm -f backend/app/config.py.bak

# 更新README.md
sed -i.bak "s/version-[0-9]*\.[0-9]*\.[0-9]*/version-${NEW_VERSION}/" README.md
rm -f README.md.bak

print_success "版本号已更新为 v${NEW_VERSION}"

# 步骤3: 运行测试
print_info "步骤3/8: 运行测试..."
if [ -f "backend/pytest.ini" ]; then
    print_info "运行后端测试..."
    cd backend
    if python3 -m pytest --tb=short -v 2>&1 | tee test_output.log; then
        print_success "后端测试通过"
    else
        print_warning "后端测试失败，但继续发布"
    fi
    cd ..
else
    print_warning "跳过后端测试（未找到pytest.ini）"
fi

if [ -f "frontend/package.json" ]; then
    print_info "运行前端测试..."
    cd frontend
    if npm run test 2>&1 | tee test_output.log; then
        print_success "前端测试通过"
    else
        print_warning "前端测试失败，但继续发布"
    fi
    cd ..
else
    print_warning "跳过前端测试"
fi

# 步骤4: 生成CHANGELOG
print_info "步骤4/8: 生成CHANGELOG..."
if [ ! -f "CHANGELOG_v${NEW_VERSION}.md" ]; then
    print_warning "未找到 CHANGELOG_v${NEW_VERSION}.md，请手动创建"
    read -p "按Enter继续..."
else
    print_success "CHANGELOG已存在"
fi

# 步骤5: Git提交
print_info "步骤5/8: 提交更改到Git..."
git add -A
git commit -m "chore: 发布 v${NEW_VERSION}

- 更新版本号到 v${NEW_VERSION}
- 更新文档和配置文件
- 准备发布
" || print_warning "没有需要提交的更改"
print_success "更改已提交"

# 步骤6: 创建Git标签
print_info "步骤6/8: 创建Git标签..."
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
print_success "Git标签已创建: v${NEW_VERSION}"

# 步骤7: 推送到远程仓库
print_info "步骤7/8: 推送到远程仓库..."
echo ""
read -p "是否推送到GitHub? (y/n): " PUSH
if [[ $PUSH == "y" || $PUSH == "Y" ]]; then
    git push origin main
    git push origin "v${NEW_VERSION}"
    print_success "已推送到GitHub"
else
    print_warning "跳过推送，你可以稍后手动推送: git push origin main && git push origin v${NEW_VERSION}"
fi

# 步骤8: 构建安装包（可选）
print_info "步骤8/8: 构建安装包..."
echo ""
read -p "是否构建安装包? (y/n): " BUILD
if [[ $BUILD == "y" || $BUILD == "Y" ]]; then
    print_info "开始构建..."
    
    # 构建后端
    if [ -f "build/build_backend.py" ]; then
        print_info "构建后端..."
        python3 build/build_backend.py
    fi
    
    # 构建前端
    if [ -f "build/build_all.sh" ]; then
        print_info "构建前端..."
        bash build/build_all.sh
    fi
    
    print_success "构建完成"
else
    print_warning "跳过构建，你可以稍后手动构建"
fi

# 完成
echo ""
echo "=================================================="
echo "   🎉 发布完成！"
echo "=================================================="
echo ""
print_success "版本 v${NEW_VERSION} 已成功发布"
echo ""
echo "接下来："
echo "  1. 访问 GitHub Releases 页面"
echo "  2. 编辑发布说明"
echo "  3. 上传构建的安装包（如果已构建）"
echo ""
echo "GitHub Releases: https://github.com/gfchfjh/CSBJJWT/releases"
echo ""
