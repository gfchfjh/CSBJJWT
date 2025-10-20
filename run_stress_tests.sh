#!/bin/bash

echo "========================================="
echo " KOOK消息转发系统 - 压力测试执行脚本"
echo "========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查后端服务是否运行
echo ""
echo "检查后端服务..."
if curl -s http://127.0.0.1:9527/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行中"
else
    echo "⚠️  后端服务未运行"
    echo "正在启动后端服务..."
    cd backend
    python3 -m app.main &
    BACKEND_PID=$!
    echo "后端服务PID: $BACKEND_PID"
    cd ..
    
    # 等待服务启动
    echo "等待服务启动..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:9527/health > /dev/null 2>&1; then
            echo "✅ 后端服务已启动"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
fi

# 检查Redis服务
echo ""
echo "检查Redis服务..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis服务运行中"
else
    echo "⚠️  Redis服务未运行，后端会自动启动嵌入式Redis"
fi

echo ""
echo "========================================="
echo " 选择测试类型"
echo "========================================="
echo "1. 基础压力测试 (7个测试, 约3-5分钟)"
echo "2. 全面压力测试 (7个测试, 约15-20分钟)"
echo "3. 两者都运行 (14个测试, 约20-25分钟)"
echo ""
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "运行基础压力测试..."
        python3 stress_test.py
        ;;
    2)
        echo ""
        echo "运行全面压力测试..."
        python3 comprehensive_stress_test.py
        ;;
    3)
        echo ""
        echo "先运行基础压力测试..."
        python3 stress_test.py
        echo ""
        echo "========================================="
        echo ""
        echo "现在运行全面压力测试..."
        python3 comprehensive_stress_test.py
        ;;
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo " 测试完成！"
echo "========================================="
echo ""
echo "测试报告位置："
echo "  • 基础测试: ./压力测试报告.md"
echo "  • 全面测试: ./comprehensive_stress_test_report.md"
echo ""
echo "JSON结果："
echo "  • 基础测试: ./stress_test_report.json"
echo "  • 全面测试: ./comprehensive_stress_test_results.json"
echo ""
