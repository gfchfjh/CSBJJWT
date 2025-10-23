#!/bin/bash
# 构建监控脚本 - v1.13.3

VERSION="v1.13.3"
REPO="gfchfjh/CSBJJWT"
CHECK_INTERVAL=60  # 每60秒检查一次

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  KOOK消息转发系统 - 构建监控${NC}"
echo -e "${BLUE}  版本: ${VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "开始监控时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo ""

# 检查GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI未安装，使用备用方法监控${NC}"
    echo ""
    echo "📍 请手动访问以下地址查看构建进度："
    echo "   https://github.com/${REPO}/actions"
    echo ""
    echo "📍 构建完成后访问："
    echo "   https://github.com/${REPO}/releases/tag/${VERSION}"
    echo ""
    exit 0
fi

# 获取最新workflow运行
get_latest_run() {
    gh run list \
        --repo "${REPO}" \
        --workflow "Build and Release" \
        --limit 1 \
        --json status,conclusion,displayTitle,startedAt,updatedAt,url \
        2>/dev/null
}

# 监控循环
MONITOR_START=$(date +%s)
LAST_STATUS=""

while true; do
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    ELAPSED=$(($(date +%s) - MONITOR_START))
    ELAPSED_MIN=$((ELAPSED / 60))
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "检查时间: ${CURRENT_TIME} (已监控${ELAPSED_MIN}分钟)"
    echo ""
    
    # 获取workflow状态
    RUN_INFO=$(get_latest_run)
    
    if [ -z "$RUN_INFO" ]; then
        echo -e "${YELLOW}⚠️  无法获取构建信息${NC}"
        echo "请检查网络连接或手动访问："
        echo "https://github.com/${REPO}/actions"
    else
        # 解析JSON
        STATUS=$(echo "$RUN_INFO" | jq -r '.[0].status')
        CONCLUSION=$(echo "$RUN_INFO" | jq -r '.[0].conclusion')
        TITLE=$(echo "$RUN_INFO" | jq -r '.[0].displayTitle')
        STARTED=$(echo "$RUN_INFO" | jq -r '.[0].startedAt')
        URL=$(echo "$RUN_INFO" | jq -r '.[0].url')
        
        echo "构建标题: ${TITLE}"
        echo "构建URL: ${URL}"
        echo ""
        
        # 显示状态
        case "$STATUS" in
            "queued")
                echo -e "${YELLOW}⏳ 状态: 队列中${NC}"
                ;;
            "in_progress")
                echo -e "${BLUE}🔄 状态: 构建中${NC}"
                ;;
            "completed")
                echo ""
                if [ "$CONCLUSION" == "success" ]; then
                    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo -e "${GREEN}✅ 构建成功！${NC}"
                    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo ""
                    echo "🎉 恭喜！v1.13.3已成功构建"
                    echo ""
                    echo "📦 下载安装包："
                    echo "   https://github.com/${REPO}/releases/tag/${VERSION}"
                    echo ""
                    echo "安装包包含："
                    echo "  • KookForwarder-Setup-1.13.3.exe (~450MB)"
                    echo "  • KookForwarder-1.13.3.dmg (~480MB)"
                    echo "  • KookForwarder-1.13.3.AppImage (~420MB)"
                    echo ""
                    echo "总耗时: ${ELAPSED_MIN}分钟"
                    echo ""
                    exit 0
                else
                    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo -e "${RED}❌ 构建失败！${NC}"
                    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo ""
                    echo "失败原因: ${CONCLUSION}"
                    echo ""
                    echo "📍 查看详细日志："
                    echo "   ${URL}"
                    echo ""
                    echo "💡 建议："
                    echo "   1. 查看GitHub Actions日志"
                    echo "   2. 修复问题"
                    echo "   3. 删除tag后重新发布"
                    echo ""
                    exit 1
                fi
                ;;
            *)
                echo -e "${YELLOW}❓ 状态: ${STATUS}${NC}"
                ;;
        esac
        
        # 保存状态用于下次比较
        LAST_STATUS="$STATUS"
    fi
    
    echo ""
    echo -e "${BLUE}下次检查: $(date -d "+${CHECK_INTERVAL} seconds" '+%H:%M:%S' 2>/dev/null || date -v +${CHECK_INTERVAL}S '+%H:%M:%S' 2>/dev/null)${NC}"
    echo ""
    
    # 如果已监控超过30分钟，提醒用户
    if [ $ELAPSED_MIN -gt 30 ]; then
        echo -e "${YELLOW}⚠️  构建时间已超过30分钟${NC}"
        echo "正常构建时间: 15-20分钟"
        echo "建议检查GitHub Actions页面"
        echo ""
    fi
    
    # 等待下次检查
    sleep $CHECK_INTERVAL
done
