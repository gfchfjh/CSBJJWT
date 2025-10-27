#!/bin/bash
# 创建GitHub Release的辅助脚本
# 使用方法: ./scripts/create-release.sh v1.13.2

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERSION=$1

if [ -z "$VERSION" ]; then
    echo -e "${RED}错误: 请指定版本号${NC}"
    echo "用法: ./scripts/create-release.sh v1.13.2"
    exit 1
fi

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}创建Release: $VERSION${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查gh命令
if ! command -v gh &> /dev/null; then
    echo -e "${RED}错误: 未安装GitHub CLI (gh)${NC}"
    echo "请安装: https://cli.github.com/"
    exit 1
fi

# 检查是否登录
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}请先登录GitHub CLI${NC}"
    gh auth login
fi

# 确认当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}当前分支: $CURRENT_BRANCH${NC}"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}警告: 您不在main分支${NC}"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}警告: 有未提交的更改${NC}"
    git status -s
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建tag
echo -e "${BLUE}创建Git tag: $VERSION${NC}"
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo -e "${YELLOW}警告: tag $VERSION 已存在${NC}"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$VERSION"
        git push origin :"$VERSION"
    else
        exit 1
    fi
fi

git tag -a "$VERSION" -m "Release $VERSION"
echo -e "${GREEN}✅ Tag创建完成${NC}"

# 推送tag
echo -e "${BLUE}推送tag到GitHub...${NC}"
git push origin "$VERSION"
echo -e "${GREEN}✅ Tag推送完成${NC}"

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✅ Release创建流程已启动${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo "GitHub Actions将自动："
echo "  1. 构建Windows/macOS/Linux安装包"
echo "  2. 构建Docker镜像"
echo "  3. 创建GitHub Release"
echo "  4. 上传所有安装包"
echo ""
echo "查看进度:"
echo "  https://github.com/gfchfjh/CSBJJWT/actions"
echo ""
echo "预计完成时间: 15-20分钟"
echo ""
