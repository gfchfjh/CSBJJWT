#!/bin/bash
# Windows构建实时监控脚本

echo "================================================"
echo "Windows构建实时监控"
echo "Run ID: 18972513161"
echo "================================================"
echo ""

while true; do
    # 获取状态
    STATUS=$(gh run view 18972513161 --json status --jq '.status' 2>/dev/null)
    CONCLUSION=$(gh run view 18972513161 --json conclusion --jq '.conclusion' 2>/dev/null)
    
    # 清屏并显示状态
    clear
    echo "================================================"
    echo "Windows构建监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "================================================"
    echo ""
    echo "Run ID: 18972513161"
    echo "状态: $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo "结果: $CONCLUSION"
        echo ""
        
        if [ "$CONCLUSION" = "success" ]; then
            echo "✅ 构建成功！"
            echo ""
            echo "查看产物:"
            gh run view 18972513161
            echo ""
            echo "下载命令:"
            echo "gh run download 18972513161"
            break
        else
            echo "❌ 构建失败！"
            echo ""
            echo "查看日志:"
            echo "gh run view 18972513161 --log"
            break
        fi
    fi
    
    echo ""
    echo "查看详情: https://github.com/gfchfjh/CSBJJWT/actions/runs/18972513161"
    echo ""
    echo "实时日志: gh run watch 18972513161"
    echo ""
    echo "30秒后刷新..."
    
    sleep 30
done
