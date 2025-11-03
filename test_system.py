#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOOK消息转发系统 v18.0.2 - 功能测试脚本
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:9527"
FRONTEND_URL = "http://localhost:5173"

results = {"total": 0, "passed": 0, "failed": 0, "errors": []}

def print_test(name, status, details=""):
    results["total"] += 1
    if status == "PASS":
        results["passed"] += 1
        print(f"✅ [{status}] {name}")
    else:
        results["failed"] += 1
        results["errors"].append(f"{name}: {details}")
        print(f"❌ [{status}] {name}")
    if details:
        print(f"   └─ {details}")

print("\n" + "="*60)
print("  🧪 KOOK消息转发系统 v18.0.2 - 功能测试")
print("  时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("="*60)

# 1. 后端健康检查
print("\n【后端服务测试】")
try:
    r = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    if r.status_code == 200:
        print_test("后端健康检查", "PASS", f"状态: {r.json().get('status')}")
    else:
        print_test("后端健康检查", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("后端健康检查", "FAIL", str(e))

# 2. API 根路径
try:
    r = requests.get(f"{BACKEND_URL}/", timeout=5)
    data = r.json()
    if "app" in data:
        print_test("API 根路径", "PASS", f"版本: {data.get('version')}")
    else:
        print_test("API 根路径", "FAIL", "响应错误")
except Exception as e:
    print_test("API 根路径", "FAIL", str(e))

# 3. 系统状态 API
try:
    r = requests.get(f"{BACKEND_URL}/api/system/status", timeout=5)
    if r.status_code == 200:
        print_test("系统状态 API", "PASS", "/api/system/status")
    else:
        print_test("系统状态 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("系统状态 API", "FAIL", str(e))

# 4. 认证状态
try:
    r = requests.get(f"{BACKEND_URL}/auth/status", timeout=5)
    if r.status_code == 200:
        print_test("认证状态 API", "PASS", "/auth/status")
    else:
        print_test("认证状态 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("认证状态 API", "FAIL", str(e))

# 5. 账号 API
try:
    r = requests.get(f"{BACKEND_URL}/api/accounts/", timeout=5)
    if r.status_code == 200:
        print_test("账号管理 API", "PASS", f"账号数: {len(r.json())}")
    else:
        print_test("账号管理 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("账号管理 API", "FAIL", str(e))

# 6. Bot API
try:
    r = requests.get(f"{BACKEND_URL}/api/bots/", timeout=5)
    if r.status_code == 200:
        print_test("Bot配置 API", "PASS", f"Bot数: {len(r.json())}")
    else:
        print_test("Bot配置 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("Bot配置 API", "FAIL", str(e))

# 7. 映射 API
try:
    r = requests.get(f"{BACKEND_URL}/api/mappings/", timeout=5)
    if r.status_code == 200:
        print_test("频道映射 API", "PASS", "可访问")
    else:
        print_test("频道映射 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("频道映射 API", "FAIL", str(e))

# 8. 日志 API
try:
    r = requests.get(f"{BACKEND_URL}/api/logs/?limit=10", timeout=5)
    if r.status_code == 200:
        print_test("日志查询 API", "PASS", "可访问")
    else:
        print_test("日志查询 API", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("日志查询 API", "FAIL", str(e))

# 9. 前端服务
print("\n【前端服务测试】")
try:
    r = requests.get(FRONTEND_URL, timeout=5)
    if r.status_code == 200:
        print_test("前端服务", "PASS", FRONTEND_URL)
    else:
        print_test("前端服务", "FAIL", f"状态码: {r.status_code}")
except Exception as e:
    print_test("前端服务", "FAIL", str(e))

# 10. Redis
print("\n【Redis 服务测试】")
try:
    import redis
    r = redis.Redis(host='127.0.0.1', port=6379, socket_connect_timeout=2)
    r.ping()
    print_test("Redis 连接", "PASS", "连接成功")
except Exception as e:
    print_test("Redis 连接", "SKIP", "未运行（不影响核心功能）")

# 总结
print("\n" + "="*60)
print("  📊 测试总结")
print("="*60)
print(f"\n总测试数: {results['total']}")
print(f"✅ 通过: {results['passed']}")
print(f"❌ 失败: {results['failed']}")

if results['total'] > 0:
    rate = (results['passed'] / results['total']) * 100
    print(f"\n成功率: {rate:.1f}%")
    
    if rate >= 90:
        print("\n🎉 系统状态: 优秀！所有核心功能正常！")
    elif rate >= 70:
        print("\n✅ 系统状态: 良好，核心功能可用")
    else:
        print("\n⚠️  系统状态: 部分功能需要修复")

if results['failed'] > 0:
    print(f"\n❌ 失败的测试:")
    for error in results['errors']:
        print(f"   - {error}")

print("\n" + "="*60)
print("测试完成时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("="*60 + "\n")