#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOOK消息转发系统 v18.0.2 - 功能测试脚本
测试所有核心功能是否正常工作
"""

import requests
import json
import time
from datetime import datetime

# 配置
BACKEND_URL = "http://127.0.0.1:9527"
FRONTEND_URL = "http://localhost:5173"

# 测试结果
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}

def print_header(text):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name, status, details=""):
    """打印测试结果"""
    results["total"] += 1
    if status == "PASS":
        results["passed"] += 1
        symbol = "✅"
    elif status == "FAIL":
        results["failed"] += 1
        symbol = "❌"
        results["errors"].append(f"{name}: {details}")
    else:
        results["skipped"] += 1
        symbol = "⏭️"
    
    print(f"{symbol} [{status}] {name}")
    if details:
        print(f"   └─ {details}")

def test_backend_health():
    """测试后端健康检查"""
    print_header("🔍 后端服务测试")
    
    try:
        # 1. 基础健康检查
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_test("后端健康检查", "PASS", f"状态: {response.json().get('status')}")
        else:
            print_test("后端健康检查", "FAIL", f"状态码: {response.status_code}")
    except Exception as e:
        print_test("后端健康检查", "FAIL", str(e))
    
    # 2. API 根路径
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        data = response.json()
        if "app" in data and "version" in data:
            print_test("API 根路径", "PASS", f"版本: {data.get('version')}")
        else:
            print_test("API 根路径", "FAIL", "响应格式不正确")
    except Exception as e:
        print_test("API 根路径", "FAIL", str(e))
    
    # 3. API 文档
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_test("API 文档页面", "PASS", "Swagger UI 可访问")
        else:
            print_test("API 文档页面", "FAIL", f"状态码: {response.status_code}")
    except Exception as e:
        print_test("API 文档页面", "FAIL", str(e))
    
    # 4. Redoc 文档
    try:
        response = requests.get(f"{BACKEND_URL}/redoc", timeout=5)
        if response.status_code == 200:
            print_test("Redoc 文档页面", "PASS", "ReDoc 可访问")
        else:
            print_test("Redoc 文档页面", "FAIL", f"状态码: {response.status_code}")
    except Exception as e:
        print_test("Redoc 文档页面", "FAIL", str(e))

def test_backend_apis():
    """测试后端主要 API 端点"""
    print_header("🔌 后端 API 端点测试")
    
    api_endpoints = [
        ("/api/system/status", "GET", "系统状态"),
        ("/auth/status", "GET", "认证状态"),
        ("/api/disclaimer/status", "GET", "免责声明状态"),
        ("/api/first-run/check", "GET", "首次运行检查"),
        ("/api/accounts/", "GET", "账号列表"),
        ("/api/bots/", "GET", "Bot 列表"),
        ("/api/mappings/", "GET", "映射列表"),
        ("/api/logs/", "GET", "日志列表"),
        ("/api/health/status", "GET", "健康状态"),
        ("/api/updates/status", "GET", "更新状态"),
    ]
    
    for endpoint, method, name in api_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=5)
            
            if response.status_code in [200, 201]:
                print_test(f"{name} API", "PASS", f"{endpoint}")
            elif response.status_code == 404:
                print_test(f"{name} API", "FAIL", f"404 Not Found - {endpoint}")
            else:
                print_test(f"{name} API", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            print_test(f"{name} API", "FAIL", f"连接失败: {str(e)}")

def test_frontend():
    """测试前端服务"""
    print_header("🎨 前端服务测试")
    
    try:
        # 1. 前端根路径
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_test("前端根路径", "PASS", f"{FRONTEND_URL}")
        else:
            print_test("前端根路径", "FAIL", f"状态码: {response.status_code}")
    except Exception as e:
        print_test("前端根路径", "FAIL", str(e))
    
    # 2. 前端主页
    try:
        response = requests.get(f"{FRONTEND_URL}/home", timeout=5)
        if response.status_code == 200:
            print_test("前端主页", "PASS", f"{FRONTEND_URL}/home")
        else:
            print_test("前端主页", "FAIL", f"状态码: {response.status_code}")
    except Exception as e:
        print_test("前端主页", "FAIL", str(e))

def test_dependencies():
    """测试依赖是否正确安装"""
    print_header("📦 依赖检查")
    
    import subprocess
    
    # Python 依赖
    python_packages = [
        "fastapi",
        "uvicorn",
        "playwright",
        "redis",
        "loguru",
        "discord-webhook",
        "telegram",
        "psutil",
        "prometheus_client"
    ]
    
    for package in python_packages:
        try:
            result = subprocess.run(
                ["pip", "show", package],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 提取版本号
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        print_test(f"Python包: {package}", "PASS", f"v{version}")
                        break
            else:
                print_test(f"Python包: {package}", "FAIL", "未安装")
        except Exception as e:
            print_test(f"Python包: {package}", "FAIL", str(e))

def test_database():
    """测试数据库连接"""
    print_header("💾 数据库测试")
    
    import os
    
    # 检查数据库文件
    db_path = os.path.expanduser("~/Documents/KookForwarder/data/kook_forwarder.db")
    
    if os.path.exists(db_path):
        print_test("SQLite 数据库", "PASS", f"文件存在: {db_path}")
    else:
        print_test("SQLite 数据库", "SKIP", "数据库文件不存在（首次运行正常）")

def test_redis():
    """测试 Redis 连接"""
    print_header("🔴 Redis 测试")
    
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, socket_connect_timeout=2)
        r.ping()
        print_test("Redis 连接", "PASS", "连接成功")
        
        # 测试基本操作
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        if value == b'test_value':
            print_test("Redis 读写", "PASS", "读写正常")
        r.delete('test_key')
    except Exception as e:
        print_test("Redis 连接", "SKIP", "Redis 未运行或连接失败（不影响核心功能）")

def test_cors():
    """测试 CORS 配置"""
    print_header("🌐 CORS 跨域测试")
    
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET'
        }
        response = requests.options(f"{BACKEND_URL}/api/system/status", headers=headers, timeout=5)
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print_test("CORS 配置", "PASS", f"允许来源: {cors_header}")
        else:
            print_test("CORS 配置", "FAIL", "缺少 CORS 头")
    except Exception as e:
        print_test("CORS 配置", "FAIL", str(e))

def print_summary():
    """打印测试总结"""
    print_header("📊 测试总结")
    
    print(f"\n总测试数: {results['total']}")
    print(f"✅ 通过: {results['passed']}")
    print(f"❌ 失败: {results['failed']}")
    print(f"⏭️  跳过: {results['skipped']}")
    
    if results['failed'] > 0:
        print(f"\n❌ 失败的测试:")
        for error in results['errors']:
            print(f"   - {error}")
    
    # 计算成功率
    if results['total'] > 0:
        success_rate = (results['passed'] / results['total']) * 100
        print(f"\n成功率: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 系统状态: 优秀！所有核心功能正常！")
        elif success_rate >= 70:
            print("\n✅ 系统状态: 良好，核心功能可用")
        elif success_rate >= 50:
            print("\n⚠️  系统状态: 一般，部分功能需要修复")
        else:
            print("\n❌ 系统状态: 需要修复多个问题")
    
    print("\n" + "=" * 60)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

def main():
    """主测试流程"""
    print("\n" + "🧪" * 30)
    print("  KOOK消息转发系统 v18.0.2 - 功能测试")
    print("  开始时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🧪" * 30)
    
    # 执行测试
    test_backend_health()
    test_backend_apis()
    test_frontend()
    test_dependencies()
    test_database()
    test_redis()
    test_cors()
    
    # 打印总结
    print_summary()

if __name__ == "__main__":
    main()
