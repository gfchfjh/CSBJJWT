#!/bin/bash
# ============================================================================
# KOOK消息转发系统 - 快速执行命令脚本
# 
# 用途：在本地快速执行完整的发布流程
# 使用：bash 快速执行命令.sh
# ============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
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

# 显示标题
clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}║   KOOK消息转发系统 - 快速执行脚本                ║${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

print_info "本脚本将引导您完成发布流程"
echo ""

# 第一步：检查当前状态
print_step "1️⃣  检查当前状态"

CURRENT_BRANCH=$(git branch --show-current)
print_info "当前分支: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" == "main" ]] || [[ "$CURRENT_BRANCH" == "master" ]]; then
    print_success "已在主分支上"
    MAIN_BRANCH=$CURRENT_BRANCH
else
    print_warning "当前不在主分支上"
    
    # 检测主分支名称
    if git rev-parse --verify main >/dev/null 2>&1; then
        MAIN_BRANCH="main"
    elif git rev-parse --verify master >/dev/null 2>&1; then
        MAIN_BRANCH="master"
    else
        print_error "无法找到主分支（main或master）"
        exit 1
    fi
    
    print_info "检测到主分支: $MAIN_BRANCH"
    echo ""
    read -p "是否切换到 $MAIN_BRANCH 分支？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "切换到 $MAIN_BRANCH 分支..."
        git checkout $MAIN_BRANCH
        git pull origin $MAIN_BRANCH
        print_success "已切换到 $MAIN_BRANCH 分支"
    else
        print_warning "取消操作"
        exit 0
    fi
fi

# 第二步：检查是否有Cursor分支需要合并
print_step "2️⃣  检查待合并的更改"

CURSOR_BRANCHES=$(git branch --list 'cursor/*' | head -1 | xargs)

if [ -n "$CURSOR_BRANCHES" ]; then
    print_info "发现Cursor分支: $CURSOR_BRANCHES"
    
    # 显示差异
    echo ""
    print_info "与当前分支的差异："
    git diff $MAIN_BRANCH $CURSOR_BRANCHES --stat
    
    echo ""
    read -p "是否合并Cursor分支的更改？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "合并Cursor分支..."
        git merge $CURSOR_BRANCHES --no-ff -m "feat: Merge release automation and build guides from Cursor

- Add release_package.sh for one-click release
- Add comprehensive build documentation
- Add GitHub Actions automation
- Ready for package build"
        
        if [ $? -eq 0 ]; then
            print_success "合并成功"
            
            echo ""
            read -p "是否推送到远程？(Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                git push origin $MAIN_BRANCH
                print_success "已推送到远程"
            fi
        else
            print_error "合并失败，请手动解决冲突"
            exit 1
        fi
    fi
else
    print_info "没有待合并的Cursor分支"
fi

# 第三步：检查发布脚本
print_step "3️⃣  检查发布脚本"

if [ -f "release_package.sh" ]; then
    print_success "发布脚本已存在"
    
    # 确保可执行
    chmod +x release_package.sh
    
    # 检查语法
    bash -n release_package.sh
    if [ $? -eq 0 ]; then
        print_success "脚本语法检查通过"
    else
        print_error "脚本语法错误"
        exit 1
    fi
else
    print_error "发布脚本不存在"
    print_info "请确保 release_package.sh 文件在项目根目录"
    exit 1
fi

# 第四步：准备执行
print_step "4️⃣  准备执行发布"

echo ""
print_warning "即将执行发布脚本，这将："
echo "  1. 创建新的Git Tag"
echo "  2. 推送到GitHub"
echo "  3. 触发GitHub Actions构建"
echo "  4. 生成Windows/macOS/Linux安装包"
echo "  5. 创建GitHub Release"
echo ""
print_warning "预计耗时：15-20分钟"
echo ""

read -p "确认执行发布脚本？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "已取消发布"
    echo ""
    print_info "如需手动执行，运行："
    echo "  ./release_package.sh"
    exit 0
fi

# 第五步：执行发布脚本
print_step "5️⃣  执行发布脚本"

print_info "启动发布脚本..."
echo ""

# 执行发布脚本
./release_package.sh

# 检查执行结果
if [ $? -eq 0 ]; then
    print_header "✅ 发布流程已完成"
    
    echo ""
    print_success "下一步操作："
    echo "  1. 访问 GitHub Actions 查看构建进度"
    echo "     https://github.com/gfchfjh/CSBJJWT/actions"
    echo ""
    echo "  2. 等待约15-20分钟后，访问Release页面下载安装包"
    echo "     https://github.com/gfchfjh/CSBJJWT/releases"
    echo ""
    echo "  3. 下载并测试各平台的安装包"
    echo ""
    echo "  4. 更新README.md中的下载链接"
    echo ""
    print_info "详细说明请查看: 本地构建执行指南.md"
    echo ""
else
    print_error "发布脚本执行失败"
    echo ""
    print_info "请检查错误信息，或查看文档："
    echo "  - BUILD_RELEASE_GUIDE.md"
    echo "  - 本地构建执行指南.md"
    exit 1
fi
