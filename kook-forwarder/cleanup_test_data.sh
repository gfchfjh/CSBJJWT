#!/bin/bash

# 测试数据清理脚本

echo "=========================================="
echo "  测试数据清理工具"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 默认保留天数
KEEP_DAYS=${1:-7}

echo "清理策略: 保留最近 ${KEEP_DAYS} 天的数据"
echo ""

# 检查test_results目录
if [ ! -d "test_results" ]; then
    echo "⚠️  test_results目录不存在"
    exit 0
fi

cd test_results

# 统计当前文件
TOTAL_FILES=$(find . -type f | wc -l)
TOTAL_SIZE=$(du -sh . | cut -f1)

echo "当前状态:"
echo "  文件数量: ${TOTAL_FILES}"
echo "  占用空间: ${TOTAL_SIZE}"
echo ""

# 查找旧文件
echo "查找 ${KEEP_DAYS} 天前的文件..."
OLD_JSON=$(find . -name "*.json" -mtime +${KEEP_DAYS} | wc -l)
OLD_MD=$(find . -name "*.md" -mtime +${KEEP_DAYS} | wc -l)
OLD_LOG=$(find . -name "*.log" -mtime +${KEEP_DAYS} | wc -l)
OLD_HTML=$(find . -name "*.html" -mtime +${KEEP_DAYS} | wc -l)

echo "  JSON报告: ${OLD_JSON} 个"
echo "  Markdown报告: ${OLD_MD} 个"
echo "  日志文件: ${OLD_LOG} 个"
echo "  HTML报告: ${OLD_HTML} 个"
echo ""

TOTAL_OLD=$((OLD_JSON + OLD_MD + OLD_LOG + OLD_HTML))

if [ ${TOTAL_OLD} -eq 0 ]; then
    echo -e "${GREEN}✅ 没有需要清理的旧文件${NC}"
    exit 0
fi

# 确认清理
echo "即将删除 ${TOTAL_OLD} 个旧文件"
read -p "确认清理? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消清理"
    exit 0
fi

# 执行清理
echo ""
echo "开始清理..."

# 清理JSON文件
if [ ${OLD_JSON} -gt 0 ]; then
    find . -name "*.json" -mtime +${KEEP_DAYS} -delete
    echo -e "${GREEN}✅ 已清理 ${OLD_JSON} 个JSON报告${NC}"
fi

# 清理Markdown文件
if [ ${OLD_MD} -gt 0 ]; then
    find . -name "*.md" -mtime +${KEEP_DAYS} -delete
    echo -e "${GREEN}✅ 已清理 ${OLD_MD} 个Markdown报告${NC}"
fi

# 清理日志文件
if [ ${OLD_LOG} -gt 0 ]; then
    find . -name "*.log" -mtime +${KEEP_DAYS} -delete
    echo -e "${GREEN}✅ 已清理 ${OLD_LOG} 个日志文件${NC}"
fi

# 清理HTML文件
if [ ${OLD_HTML} -gt 0 ]; then
    find . -name "*.html" -mtime +${KEEP_DAYS} -delete
    echo -e "${GREEN}✅ 已清理 ${OLD_HTML} 个HTML报告${NC}"
fi

# 显示清理后的状态
echo ""
echo "清理完成！"
NEW_FILES=$(find . -type f | wc -l)
NEW_SIZE=$(du -sh . | cut -f1)

echo ""
echo "清理后状态:"
echo "  文件数量: ${NEW_FILES} (减少 $((TOTAL_FILES - NEW_FILES)))"
echo "  占用空间: ${NEW_SIZE}"
echo ""

echo -e "${GREEN}✅ 清理完成！${NC}"
