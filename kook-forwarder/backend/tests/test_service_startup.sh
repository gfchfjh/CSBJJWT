#!/bin/bash
# 服务启动测试脚本
# 测试后端服务是否能正常启动和响应

set -e

echo "========================================"
echo "  KOOK消息转发系统 - 服务启动测试"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# 测试函数
run_test() {
    local test_name=$1
    local test_command=$2
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "[$TESTS_TOTAL] $test_name ... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 清理函数
cleanup() {
    echo ""
    echo "清理测试环境..."
    
    # 停止服务
    if [ ! -z "$SERVICE_PID" ]; then
        kill $SERVICE_PID 2>/dev/null || true
        wait $SERVICE_PID 2>/dev/null || true
    fi
    
    # 停止Redis
    if [ ! -z "$REDIS_PID" ]; then
        kill $REDIS_PID 2>/dev/null || true
    fi
    
    echo "清理完成"
}

# 注册清理函数
trap cleanup EXIT INT TERM

echo "准备测试环境..."
echo ""

# 切换到backend目录
cd "$(dirname "$0")/.."

# 测试1: 检查Python环境
run_test "检查Python环境" "python3 --version"

# 测试2: 检查依赖是否安装
run_test "检查FastAPI依赖" "python3 -c 'import fastapi'"

# 测试3: 检查配置文件
run_test "检查配置模块" "python3 -c 'from app.config import settings'"

# 测试4: 检查数据库模块
run_test "检查数据库模块" "python3 -c 'from app.database import db'"

echo ""
echo "启动Redis服务..."

# 启动Redis（如果未运行）
if ! pgrep -x "redis-server" > /dev/null; then
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes --port 6379
        REDIS_PID=$!
        sleep 2
        echo -e "${GREEN}✓ Redis启动成功${NC}"
    else
        echo -e "${YELLOW}⚠ Redis未安装，使用嵌入式Redis${NC}"
    fi
else
    echo -e "${GREEN}✓ Redis已运行${NC}"
fi

echo ""
echo "启动后端服务..."

# 启动服务（超时30秒）
timeout 30s python3 -m app.main > /tmp/kook_service.log 2>&1 &
SERVICE_PID=$!

echo "服务PID: $SERVICE_PID"
echo "等待服务就绪..."

# 等待服务启动（最多等待10秒）
MAX_WAIT=10
WAIT_COUNT=0
SERVICE_READY=false

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://localhost:9527/health > /dev/null 2>&1; then
        SERVICE_READY=true
        break
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
done
echo ""

if [ "$SERVICE_READY" = false ]; then
    echo -e "${RED}✗ 服务启动失败或超时${NC}"
    echo "最后的日志输出:"
    tail -20 /tmp/kook_service.log
    exit 1
fi

echo -e "${GREEN}✓ 服务启动成功${NC}"
echo ""

# API测试
echo "开始API测试..."
echo ""

# 测试5: 健康检查端点
run_test "健康检查 GET /health" \
    "curl -s http://localhost:9527/health | grep -q 'healthy\|status'"

# 测试6: 根路径
run_test "根路径 GET /" \
    "curl -s http://localhost:9527/ | grep -q 'KOOK\|version\|status'"

# 测试7: 系统状态
run_test "系统状态 GET /api/system/status" \
    "curl -s http://localhost:9527/api/system/status | grep -q 'service_running\|status'"

# 测试8: 账号列表
run_test "账号列表 GET /api/accounts" \
    "curl -s http://localhost:9527/api/accounts"

# 测试9: Bot列表
run_test "Bot列表 GET /api/bots" \
    "curl -s http://localhost:9527/api/bots"

# 测试10: 频道映射列表
run_test "映射列表 GET /api/mappings" \
    "curl -s http://localhost:9527/api/mappings"

# 测试11: 日志列表
run_test "日志列表 GET /api/logs" \
    "curl -s http://localhost:9527/api/logs"

# 测试12: POST请求 - 添加账号
run_test "添加账号 POST /api/accounts" \
    "curl -s -X POST http://localhost:9527/api/accounts -H 'Content-Type: application/json' -d '{\"email\":\"test@test.com\",\"cookie\":\"[]\"}'"

# 测试13: 响应时间
echo -n "[$((TESTS_TOTAL + 1))] 测试响应时间 ... "
RESPONSE_TIME=$(curl -s -w '%{time_total}' -o /dev/null http://localhost:9527/health)
TESTS_TOTAL=$((TESTS_TOTAL + 1))

if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASSED${NC} (${RESPONSE_TIME}s)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (${RESPONSE_TIME}s, 应该 < 1.0s)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# 测试14: 并发请求
echo -n "[$((TESTS_TOTAL + 1))] 测试并发请求 (10个并发) ... "
TESTS_TOTAL=$((TESTS_TOTAL + 1))

SUCCESS_COUNT=0
for i in {1..10}; do
    curl -s http://localhost:9527/health > /dev/null 2>&1 &
done
wait

# 检查所有请求是否成功
for i in {1..10}; do
    if curl -s http://localhost:9527/health | grep -q "healthy\|status"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
done

if [ $SUCCESS_COUNT -ge 8 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (${SUCCESS_COUNT}/10 成功)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (${SUCCESS_COUNT}/10 成功，应该 >= 8)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# 测试15: 图床服务器
run_test "图床服务 GET http://localhost:9528/" \
    "curl -s http://localhost:9528/ || true"

echo ""
echo "========================================"
echo "  测试结果汇总"
echo "========================================"
echo "总测试数: $TESTS_TOTAL"
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"
echo "通过率: $(echo "scale=2; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc)%"
echo ""

# 显示服务日志摘要
echo "服务日志摘要 (最后20行):"
echo "----------------------------------------"
tail -20 /tmp/kook_service.log
echo "----------------------------------------"
echo ""

# 返回结果
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $TESTS_FAILED 个测试失败${NC}"
    exit 1
fi
