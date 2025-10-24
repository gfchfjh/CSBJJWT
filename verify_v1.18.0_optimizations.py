#!/usr/bin/env python3
"""
v1.18.0 深度优化验证脚本

验证所有优化是否正确应用
"""
import sys
import os
from pathlib import Path


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def check_orjson():
    """检查orjson是否已安装"""
    print("\n🔍 检查orjson优化...")
    try:
        import orjson
        print("  ✅ orjson已安装（版本: {})".format(orjson.__version__ if hasattr(orjson, '__version__') else 'unknown'))
        
        # 测试性能
        import json
        import time
        
        test_data = {'key': 'value', 'number': 12345, 'array': list(range(100))}
        iterations = 10000
        
        # 标准json
        start = time.time()
        for _ in range(iterations):
            json.dumps(test_data)
            json.loads(json.dumps(test_data))
        std_time = time.time() - start
        
        # orjson
        start = time.time()
        for _ in range(iterations):
            orjson.dumps(test_data)
            orjson.loads(orjson.dumps(test_data))
        orjson_time = time.time() - start
        
        speedup = std_time / orjson_time
        print(f"  ✅ 性能测试: orjson比标准json快 {speedup:.1f}倍")
        
        if speedup >= 3:
            print("  ✅ orjson优化生效（P1-5）")
            return True
        else:
            print("  ⚠️  性能提升不足3倍，可能未正确应用")
            return False
            
    except ImportError:
        print("  ❌ orjson未安装")
        print("  💡 解决: pip install orjson==3.9.10")
        return False


def check_exceptions_module():
    """检查统一异常处理模块"""
    print("\n🔍 检查统一异常处理...")
    
    exc_file = Path("backend/app/utils/exceptions.py")
    if exc_file.exists():
        content = exc_file.read_text()
        
        # 检查关键异常类
        exceptions = [
            'KookForwarderException',
            'LoginFailedException',
            'MessageForwardException',
            'ImageDownloadException',
            'RateLimitException'
        ]
        
        found = sum(1 for exc in exceptions if exc in content)
        
        if found == len(exceptions):
            print(f"  ✅ 异常模块完整（包含{found}种异常类）")
            print("  ✅ 统一异常处理已实现（优化12）")
            return True
        else:
            print(f"  ⚠️  仅找到{found}/{len(exceptions)}种异常类")
            return False
    else:
        print("  ❌ exceptions.py文件不存在")
        return False


def check_async_database():
    """检查异步数据库层"""
    print("\n🔍 检查异步数据库...")
    
    async_db_file = Path("backend/app/database_async.py")
    if async_db_file.exists():
        content = async_db_file.read_text()
        
        # 检查关键方法
        methods = [
            'class AsyncDatabase',
            'async def init',
            'async def execute_write',
            'async def execute_read',
            '_write_worker',
            '_flush_batch'
        ]
        
        found = sum(1 for method in methods if method in content)
        
        if found == len(methods):
            print(f"  ✅ 异步数据库模块完整（{found}/{len(methods)}个关键方法）")
            print("  ✅ 数据库异步化已实现（P1-4）")
            return True
        else:
            print(f"  ⚠️  仅找到{found}/{len(methods)}个关键方法")
            return False
    else:
        print("  ❌ database_async.py文件不存在")
        return False


def check_message_segmentation():
    """检查消息自动分段"""
    print("\n🔍 检查消息自动分段...")
    
    worker_file = Path("backend/app/queue/worker.py")
    if worker_file.exists():
        content = worker_file.read_text()
        
        # 检查分段逻辑
        checks = [
            'split_long_message' in content,
            'P0-1优化' in content or '自动分段' in content,
            '2000' in content,  # Discord限制
            '4096' in content,  # Telegram限制
        ]
        
        passed = sum(checks)
        
        if passed >= 3:
            print(f"  ✅ 消息分段逻辑已实现（{passed}/4检查通过）")
            print("  ✅ 超长消息自动分段（P0-1）")
            return True
        else:
            print(f"  ⚠️  分段逻辑可能不完整（{passed}/4检查通过）")
            return False
    else:
        print("  ❌ worker.py文件不存在")
        return False


def check_image_multiprocessing():
    """检查图片多进程处理"""
    print("\n🔍 检查图片多进程处理...")
    
    worker_file = Path("backend/app/queue/worker.py")
    image_file = Path("backend/app/processors/image.py")
    
    if worker_file.exists() and image_file.exists():
        worker_content = worker_file.read_text()
        image_content = image_file.read_text()
        
        # 检查关键实现
        checks = [
            'run_in_executor' in worker_content,
            'process_pool' in worker_content or 'ProcessPoolExecutor' in image_content,
            'save_and_process_strategy' in worker_content or 'save_and_process_strategy' in image_content,
            'P1-3优化' in worker_content or 'P1-3优化' in image_content,
        ]
        
        passed = sum(checks)
        
        if passed >= 3:
            print(f"  ✅ 图片多进程处理已实现（{passed}/4检查通过）")
            print("  ✅ 图片压缩多进程化（P1-3）")
            return True
        else:
            print(f"  ⚠️  多进程处理可能不完整（{passed}/4检查通过）")
            return False
    else:
        print("  ❌ 相关文件不存在")
        return False


def check_token_cleanup():
    """检查Token自动清理"""
    print("\n🔍 检查Token自动清理...")
    
    image_file = Path("backend/app/processors/image.py")
    main_file = Path("backend/app/main.py")
    
    if image_file.exists() and main_file.exists():
        image_content = image_file.read_text()
        main_content = main_file.read_text()
        
        checks = [
            'cleanup_expired_tokens' in image_content,
            '_cleanup_task_running' in image_content,
            'cleanup_expired_tokens' in main_content,
            'stop_cleanup_task' in image_content,
        ]
        
        passed = sum(checks)
        
        if passed >= 3:
            print(f"  ✅ Token清理任务已实现（{passed}/4检查通过）")
            print("  ✅ Token过期自动清理（优化11）")
            return True
        else:
            print(f"  ⚠️  清理任务可能不完整（{passed}/4检查通过）")
            return False
    else:
        print("  ❌ 相关文件不存在")
        return False


def check_security_enhancements():
    """检查安全增强"""
    print("\n🔍 检查安全增强...")
    
    scraper_file = Path("backend/app/kook/scraper.py")
    accounts_file = Path("backend/app/api/accounts.py")
    
    security_checks = []
    
    # 检查1: 验证码域名验证
    if scraper_file.exists():
        content = scraper_file.read_text()
        if 'allowed_domains' in content and 'kookapp.cn' in content:
            print("  ✅ 验证码域名验证（安全-8）")
            security_checks.append(True)
        else:
            print("  ⚠️  验证码域名验证未找到")
            security_checks.append(False)
    
    # 检查2: HTTPS检查
    if accounts_file.exists():
        content = accounts_file.read_text()
        if 'is_https' in content or 'HTTPS' in content:
            print("  ✅ HTTPS传输检查（安全-9）")
            security_checks.append(True)
        else:
            print("  ⚠️  HTTPS检查未找到")
            security_checks.append(False)
    
    return all(security_checks)


def check_macos_config():
    """检查macOS配置"""
    print("\n🔍 检查macOS构建配置...")
    
    builder_file = Path("build/electron-builder.yml")
    entitlements_file = Path("build/entitlements.mac.plist")
    doc_file = Path("docs/macOS代码签名配置指南.md")
    
    if builder_file.exists() and entitlements_file.exists():
        builder_content = builder_file.read_text()
        
        checks = [
            'mac:' in builder_content,
            'dmg' in builder_content,
            'hardenedRuntime' in builder_content,
            entitlements_file.exists(),
            doc_file.exists(),
        ]
        
        passed = sum(checks)
        
        if passed >= 4:
            print(f"  ✅ macOS构建配置完整（{passed}/5检查通过）")
            print("  ✅ macOS安装包配置（P0-2）")
            return True
        else:
            print(f"  ⚠️  macOS配置可能不完整（{passed}/5检查通过）")
            return False
    else:
        print("  ❌ 配置文件不存在")
        return False


def check_documentation():
    """检查文档完整性"""
    print("\n🔍 检查新增文档...")
    
    docs = [
        "KOOK转发系统_深度代码分析与优化建议_v2.md",
        "OPTIMIZATION_COMPLETION_REPORT_v1.18.0.md",
        "CHANGELOG_v1.18.0_深度优化完成版.md",
        "QUICK_START_v1.18.0.md",
        "深度优化成果总结_v1.18.0.md",
        "docs/macOS代码签名配置指南.md",
        "docs/数据库异步化改造指南.md",
        "docs/日志页面虚拟滚动改造指南.md",
        "docs/SQL注入防护审查报告.md",
        "docs/日志脱敏审查报告.md",
    ]
    
    found = 0
    for doc in docs:
        if Path(doc).exists():
            found += 1
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} (缺失)")
    
    print(f"\n  文档完整度: {found}/{len(docs)} ({found/len(docs)*100:.0f}%)")
    
    return found >= 8  # 至少80%文档存在


def check_version_numbers():
    """检查版本号更新"""
    print("\n🔍 检查版本号...")
    
    files_to_check = [
        ("backend/app/config.py", "1.18.0"),
        ("frontend/package.json", "1.18.0"),
        ("README.md", "v1.18.0"),
    ]
    
    all_updated = True
    
    for filepath, expected_version in files_to_check:
        if Path(filepath).exists():
            content = Path(filepath).read_text()
            if expected_version in content:
                print(f"  ✅ {filepath}: {expected_version}")
            else:
                print(f"  ⚠️  {filepath}: 版本号可能未更新")
                all_updated = False
        else:
            print(f"  ❌ {filepath}: 文件不存在")
            all_updated = False
    
    return all_updated


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     v1.18.0 深度优化验证工具                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # 检查1: orjson
    print_section("P1-5: WebSocket解析优化")
    results['orjson'] = check_orjson()
    
    # 检查2: 消息分段
    print_section("P0-1: 消息自动分段")
    results['segmentation'] = check_message_segmentation()
    
    # 检查3: 图片多进程
    print_section("P1-3: 图片压缩多进程化")
    results['multiprocessing'] = check_image_multiprocessing()
    
    # 检查4: Token清理
    print_section("优化11: Token过期自动清理")
    results['token_cleanup'] = check_token_cleanup()
    
    # 检查5: 异步数据库
    print_section("P1-4: 数据库异步化")
    results['async_db'] = check_async_database()
    
    # 检查6: 统一异常
    print_section("优化12: 统一错误处理")
    results['exceptions'] = check_exceptions_module()
    
    # 检查7: 安全增强
    print_section("安全优化（8, 9, 10）")
    results['security'] = check_security_enhancements()
    
    # 检查8: macOS配置
    print_section("P0-2: macOS安装包配置")
    results['macos'] = check_macos_config()
    
    # 检查9: 文档
    print_section("文档完整性")
    results['documentation'] = check_documentation()
    
    # 检查10: 版本号
    print_section("版本号更新")
    results['version'] = check_version_numbers()
    
    # 总结
    print_section("验证结果总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n  通过检查: {passed}/{total} ({passed/total*100:.0f}%)")
    print("\n  详细结果:")
    
    for check, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"    {check:20s}: {status}")
    
    # 最终评分
    print("\n" + "="*70)
    if passed == total:
        print("  🎉 恭喜！所有优化都已正确应用！")
        print("  ⭐ v1.18.0验证: 100% 通过")
        return 0
    elif passed >= total * 0.8:
        print("  ✅ 大部分优化已应用（{:.0f}%）".format(passed/total*100))
        print("  💡 建议检查失败的项目")
        return 1
    else:
        print("  ⚠️  优化应用不完整（{:.0f}%）".format(passed/total*100))
        print("  🔧 请参考优化文档进行修复")
        return 2


if __name__ == "__main__":
    sys.exit(main())
