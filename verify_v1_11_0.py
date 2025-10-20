#!/usr/bin/env python3
"""
v1.11.0功能验证脚本
快速验证新增功能是否正常工作
"""
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}不存在: {filepath}")
        return False

def check_code_changes(filepath, search_text, description):
    """检查代码是否包含特定内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}: 已添加")
                return True
            else:
                print(f"❌ {description}: 未找到")
                return False
    except Exception as e:
        print(f"❌ 检查{description}失败: {e}")
        return False

def verify_error_diagnosis():
    """验证错误诊断模块"""
    print("\n" + "="*60)
    print("📋 验证错误诊断模块")
    print("="*60)
    
    try:
        from app.utils.error_diagnosis import ErrorDiagnostic, DiagnosticLogger
        
        # 测试诊断功能
        error = Exception("429 Too Many Requests")
        diagnosis = ErrorDiagnostic.diagnose(error, {'platform': 'discord'})
        
        assert diagnosis['matched_rule'] == 'rate_limit', "规则匹配失败"
        assert diagnosis['severity'] == 'warning', "严重程度错误"
        assert len(diagnosis['suggestions']) > 0, "建议为空"
        
        print("✅ 错误诊断功能正常")
        print(f"   - 匹配规则: {diagnosis['matched_rule']}")
        print(f"   - 严重程度: {diagnosis['severity']}")
        print(f"   - 建议数量: {len(diagnosis['suggestions'])}")
        
        # 测试诊断日志
        logger = DiagnosticLogger()
        logger.log_diagnosis(diagnosis)
        
        assert len(logger.diagnostics_history) == 1, "日志记录失败"
        
        print("✅ 诊断日志记录正常")
        print(f"   - 历史记录数: {len(logger.diagnostics_history)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误诊断模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证错误诊断模块失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_methods():
    """验证数据库新增方法"""
    print("\n" + "="*60)
    print("📋 验证数据库新增方法")
    print("="*60)
    
    try:
        from app.database import Database
        
        # 检查方法是否存在
        db = Database()
        
        assert hasattr(db, 'get_account'), "缺少get_account方法"
        assert hasattr(db, 'update_account_cookie'), "缺少update_account_cookie方法"
        
        print("✅ 数据库方法已添加")
        print("   - get_account() 方法存在")
        print("   - update_account_cookie() 方法存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入数据库模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证数据库方法失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主验证流程"""
    print("="*60)
    print("🚀 KOOK消息转发系统 v1.11.0 功能验证")
    print("="*60)
    
    all_passed = True
    
    # 检查1: 错误诊断模块文件
    print("\n" + "="*60)
    print("📋 检查新增文件")
    print("="*60)
    
    files_to_check = [
        ('backend/app/utils/error_diagnosis.py', '错误诊断模块'),
        ('backend/tests/test_v1_11_0_features.py', 'v1.11.0测试文件'),
        ('v1.11.0更新说明.md', '更新说明文档'),
        ('v1.11.0交付清单.md', '交付清单文档'),
        ('v1.11.0测试指南.md', '测试指南文档'),
        ('代码完善工作总结_v1.11.0.md', '工作总结文档'),
        ('代码完善度分析报告_最终版.md', '分析报告文档'),
        ('v1.11.0快速参考卡.md', '快速参考卡')
    ]
    
    for filepath, desc in files_to_check:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 检查2: 代码变更
    print("\n" + "="*60)
    print("📋 检查代码变更")
    print("="*60)
    
    code_changes = [
        ('backend/app/kook/scraper.py', '_auto_relogin_if_expired', '自动重新登录方法'),
        ('backend/app/kook/scraper.py', '_get_cookies_dict', 'Cookie获取方法'),
        ('backend/app/database.py', 'get_account', '账号查询方法'),
        ('backend/app/database.py', 'update_account_cookie', 'Cookie更新方法'),
        ('backend/app/queue/worker.py', 'ErrorDiagnostic', '错误诊断集成'),
        ('backend/app/queue/worker.py', 'diagnostic_logger', '诊断日志记录'),
        ('frontend/src/views/Mapping.vue', 'showTemplateDialog', '模板对话框'),
        ('frontend/src/views/Mapping.vue', 'applyTemplate', '应用模板方法'),
        ('backend/app/config.py', '1.11.0', '版本号更新'),
        ('frontend/package.json', '1.11.0', '版本号更新')
    ]
    
    for filepath, search_text, desc in code_changes:
        if not check_code_changes(filepath, search_text, desc):
            all_passed = False
    
    # 检查3: 功能验证
    if verify_error_diagnosis():
        print("✅ 错误诊断模块功能正常")
    else:
        all_passed = False
    
    if verify_database_methods():
        print("✅ 数据库新增方法正常")
    else:
        all_passed = False
    
    # 总结
    print("\n" + "="*60)
    print("📊 验证结果汇总")
    print("="*60)
    
    if all_passed:
        print("✅ 所有验证通过！v1.11.0功能正常")
        print("🎉 代码完善工作成功完成！")
        return 0
    else:
        print("❌ 部分验证失败，请检查上述错误")
        return 1

if __name__ == '__main__':
    sys.exit(main())
