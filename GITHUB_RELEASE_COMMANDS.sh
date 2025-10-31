#!/bin/bash
# GitHub Release 发布脚本
# KOOK消息转发系统 v18.0.0

set -e

echo "================================================"
echo "KOOK消息转发系统 v18.0.0 - GitHub发布脚本"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 版本信息
VERSION="v18.0.0"
TAG="v18.0.0"
RELEASE_NAME="KOOK消息转发系统 v18.0.0 - 重大更新"

echo -e "${BLUE}步骤1: 检查Git状态${NC}"
echo "--------------------------------------------"
git status
echo ""

echo -e "${BLUE}步骤2: 准备发布文件${NC}"
echo "--------------------------------------------"
cd /workspace/dist

# 检查必需文件
if [ ! -f "KOOK-Forwarder-v18.0.0-Linux.tar.gz" ]; then
    echo -e "${RED}错误: 找不到安装包文件${NC}"
    exit 1
fi

if [ ! -f "KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5" ]; then
    echo -e "${RED}错误: 找不到MD5校验文件${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 所有发布文件准备就绪${NC}"
ls -lh KOOK-Forwarder-v18.0.0-Linux.tar.gz*
echo ""

echo -e "${BLUE}步骤3: 创建Git标签${NC}"
echo "--------------------------------------------"
cd /workspace

# 检查标签是否已存在
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${YELLOW}警告: 标签 $TAG 已存在${NC}"
    echo "是否删除并重新创建? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        git tag -d "$TAG"
        git push origin ":refs/tags/$TAG" 2>/dev/null || true
        echo -e "${GREEN}已删除旧标签${NC}"
    else
        echo -e "${YELLOW}跳过标签创建${NC}"
    fi
fi

# 创建标签
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
    git tag -a "$TAG" -m "Release $VERSION

新增功能:
- 企业微信转发支持
- 钉钉转发支持
- 关键词自动回复插件
- URL预览插件

修复问题:
- 修复所有TODO和未完成功能
- 替换mock数据为真实实现
- 完善系统集成

详细信息请查看 RELEASE_NOTES_v18.0.0.md"

    echo -e "${GREEN}✅ 标签创建成功${NC}"
else
    echo -e "${YELLOW}标签已存在，跳过创建${NC}"
fi
echo ""

echo -e "${BLUE}步骤4: 推送到GitHub${NC}"
echo "--------------------------------------------"
echo "是否推送标签到GitHub? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    git push origin "$TAG"
    echo -e "${GREEN}✅ 标签已推送${NC}"
else
    echo -e "${YELLOW}跳过推送${NC}"
fi
echo ""

echo -e "${BLUE}步骤5: 使用GitHub CLI创建Release${NC}"
echo "--------------------------------------------"

# 检查gh是否安装
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI (gh) 未安装${NC}"
    echo "请按照以下步骤手动创建Release:"
    echo ""
    echo "1. 访问: https://github.com/gfchfjh/CSBJJWT/releases/new"
    echo "2. 选择标签: $TAG"
    echo "3. 发布标题: $RELEASE_NAME"
    echo "4. 上传文件:"
    echo "   - /workspace/dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz"
    echo "   - /workspace/dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5"
    echo "5. 复制发布说明: /workspace/RELEASE_NOTES_v18.0.0.md"
    echo ""
else
    echo "使用GitHub CLI创建Release..."
    echo ""
    
    # 创建Release
    gh release create "$TAG" \
        --title "$RELEASE_NAME" \
        --notes-file /workspace/RELEASE_NOTES_v18.0.0.md \
        /workspace/dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz \
        /workspace/dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5
    
    echo -e "${GREEN}✅ Release创建成功${NC}"
fi
echo ""

echo -e "${BLUE}步骤6: 生成发布统计${NC}"
echo "--------------------------------------------"
cd /workspace

# 统计信息
TOTAL_FILES=$(find dist/KOOK-Forwarder-v18.0.0-Linux -type f | wc -l)
TOTAL_SIZE=$(du -sh dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz | cut -f1)

echo "发布统计:"
echo "  版本: $VERSION"
echo "  文件数: $TOTAL_FILES"
echo "  总大小: $TOTAL_SIZE"
echo "  MD5: $(cat dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5 | cut -d' ' -f1)"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}发布准备完成！${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

echo "下一步操作:"
echo ""
echo "如果使用GitHub CLI:"
echo "  1. 确认gh已登录: gh auth status"
echo "  2. 运行此脚本: bash GITHUB_RELEASE_COMMANDS.sh"
echo ""
echo "如果手动发布:"
echo "  1. 访问: https://github.com/gfchfjh/CSBJJWT/releases/new"
echo "  2. 上传文件: dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz"
echo "  3. 上传MD5: dist/KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5"
echo "  4. 复制发布说明: RELEASE_NOTES_v18.0.0.md"
echo ""
echo "发布链接:"
echo "  https://github.com/gfchfjh/CSBJJWT/releases/tag/$TAG"
echo ""

# 生成发布清单
cat > /workspace/RELEASE_CHECKLIST.md << 'EOF'
# 发布检查清单 - v18.0.0

## ✅ 发布前检查

- [ ] 代码已提交到Git
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] 安装包已构建
- [ ] MD5校验已生成

## ✅ 发布步骤

### 1. 创建Git标签
```bash
git tag -a v18.0.0 -m "Release v18.0.0"
git push origin v18.0.0
```

### 2. 创建GitHub Release
- 访问: https://github.com/gfchfjh/CSBJJWT/releases/new
- 选择标签: v18.0.0
- 发布标题: KOOK消息转发系统 v18.0.0 - 重大更新
- 上传文件:
  - [ ] KOOK-Forwarder-v18.0.0-Linux.tar.gz (150 MB)
  - [ ] KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5
- 发布说明: 复制 RELEASE_NOTES_v18.0.0.md

### 3. 验证Release
- [ ] 文件可下载
- [ ] MD5校验正确
- [ ] 发布说明显示正常
- [ ] 标签链接正确

## ✅ 发布后任务

- [ ] 在README.md更新版本号
- [ ] 在社交媒体发布公告
- [ ] 更新官方文档
- [ ] 通知用户升级

## 📝 发布信息

- **版本**: v18.0.0
- **日期**: 2025-10-31
- **类型**: 重大更新
- **下载链接**: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0

## 🎉 发布完成！

© 2025 KOOK Forwarder Team
EOF

echo -e "${GREEN}✅ 发布检查清单已生成: RELEASE_CHECKLIST.md${NC}"
echo ""
