#!/bin/bash

# KOOK消息转发系统 - 完整压力测试运行脚本

echo "=========================================="
echo "  KOOK消息转发系统 - 完整压力测试"
echo "=========================================="
echo ""
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3已安装${NC}"

# 检查依赖包
echo "检查依赖包..."
python3 -c "import aiohttp, redis, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  部分依赖包未安装，尝试安装...${NC}"
    pip install aiohttp redis pillow
fi

# 检查后端服务
echo "检查后端服务状态..."
curl -s http://127.0.0.1:9527/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    echo "请先启动后端服务: cd backend && python -m app.main"
    echo "继续执行测试（某些测试可能会失败）..."
else
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
fi

# 检查Redis服务
echo "检查Redis服务状态..."
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Redis服务未运行${NC}"
    echo "请先启动Redis服务"
    echo "继续执行测试（某些测试可能会失败）..."
else
    echo -e "${GREEN}✅ Redis服务运行正常${NC}"
fi

echo ""
echo "=========================================="
echo "  开始执行压力测试"
echo "=========================================="
echo ""

# 创建测试结果目录
mkdir -p test_results

# 1. 运行原有的压力测试
echo -e "${GREEN}[1/3] 运行原有压力测试...${NC}"
python3 stress_test.py 2>&1 | tee test_results/stress_test.log
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 原有压力测试完成${NC}"
else
    echo -e "${RED}❌ 原有压力测试失败${NC}"
fi
echo ""

# 2. 运行全面压力测试
echo -e "${GREEN}[2/3] 运行全面压力测试...${NC}"
python3 comprehensive_stress_test.py 2>&1 | tee test_results/comprehensive_stress_test.log
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 全面压力测试完成${NC}"
else
    echo -e "${RED}❌ 全面压力测试失败${NC}"
fi
echo ""

# 3. 运行模块专项测试
echo -e "${GREEN}[3/3] 运行模块专项测试...${NC}"
python3 module_specific_stress_test.py 2>&1 | tee test_results/module_specific_stress_test.log
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 模块专项测试完成${NC}"
else
    echo -e "${RED}❌ 模块专项测试失败${NC}"
fi
echo ""

# 移动报告文件到结果目录
echo "整理测试报告..."
mv stress_test_report.json test_results/ 2>/dev/null
mv 压力测试报告.md test_results/ 2>/dev/null
mv comprehensive_stress_test_report.json test_results/ 2>/dev/null
mv 全面压力测试报告.md test_results/ 2>/dev/null
mv module_stress_test_report.json test_results/ 2>/dev/null

echo ""
echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo ""
echo "测试报告保存在: ./test_results/"
echo ""
echo "生成的报告文件:"
ls -lh test_results/ 2>/dev/null | grep -E '\.(json|md|log)$'
echo ""
echo -e "${GREEN}✅ 所有压力测试执行完毕！${NC}"
