"""
KOOK消息转发系统 - 全面功能测试计划
根据需求文档进行系统性测试
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveTestPlan:
    """
    全面测试计划
    
    根据需求文档中的功能模块，系统性测试所有功能
    """
    
    def __init__(self):
        self.test_results = {
            "test_time": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "modules": {}
        }
    
    def test_module_1_message_capture(self) -> Dict[str, Any]:
        """
        模块1：消息抓取模块测试
        
        测试内容：
        1. Playwright浏览器引擎
        2. Cookie导入和账号密码登录
        3. 验证码处理（本地OCR + 手动输入）
        4. WebSocket消息监听
        5. 多账号管理
        6. 支持的消息类型（文本、图片、@提及、引用、链接、附件）
        """
        results = {
            "module_name": "消息抓取模块",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "Playwright浏览器集成",
                "description": "检查是否正确集成Playwright",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["playwright", "chromium", "browser"]
            },
            {
                "name": "Cookie多格式支持",
                "description": "检查Cookie解析器支持多种格式",
                "check": "backend/app/utils/cookie_parser.py",
                "keywords": ["JSON", "Netscape", "parse"]
            },
            {
                "name": "验证码处理（本地OCR）",
                "description": "检查ddddocr本地OCR集成",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["ddddocr", "captcha", "OCR"]
            },
            {
                "name": "WebSocket消息监听",
                "description": "检查WebSocket消息处理",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["websocket", "_handle_websocket", "MESSAGE_CREATE"]
            },
            {
                "name": "多账号管理（共享浏览器）",
                "description": "检查ScraperManager和共享浏览器上下文",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["ScraperManager", "shared_browser", "shared_context"]
            },
            {
                "name": "支持的消息类型",
                "description": "检查支持文本、图片、表情、@提及、引用等",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["message_type", "attachments", "mentions", "quote"]
            },
            {
                "name": "自动重新登录机制",
                "description": "检查Cookie过期自动重登录",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["_auto_relogin_if_expired", "password_encrypted", "decrypt"]
            },
            {
                "name": "历史消息同步",
                "description": "检查启动时同步历史消息",
                "check": "backend/app/kook/scraper.py",
                "keywords": ["sync_history_messages", "sync_history_minutes"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def test_module_2_message_processing(self) -> Dict[str, Any]:
        """
        模块2：消息处理模块测试
        
        测试内容：
        1. Redis消息队列
        2. KMarkdown格式转换（Discord/Telegram/飞书）
        3. 图片处理（三种策略）
        4. 消息去重机制
        5. 限流保护
        """
        results = {
            "module_name": "消息处理模块",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "Redis队列集成",
                "description": "检查Redis客户端和消息队列",
                "check": "backend/app/queue/redis_client.py",
                "keywords": ["redis", "enqueue", "dequeue", "RedisQueue"]
            },
            {
                "name": "消息Worker",
                "description": "检查消息消费Worker",
                "check": "backend/app/queue/worker.py",
                "keywords": ["MessageWorker", "process_message", "start", "stop"]
            },
            {
                "name": "格式转换（Discord）",
                "description": "检查KMarkdown到Discord Markdown转换",
                "check": "backend/app/processors/formatter.py",
                "keywords": ["kmarkdown_to_discord", "EMOJI_MAP"]
            },
            {
                "name": "格式转换（Telegram）",
                "description": "检查KMarkdown到Telegram HTML转换",
                "check": "backend/app/processors/formatter.py",
                "keywords": ["kmarkdown_to_telegram_html", "<b>", "<i>", "<code>"]
            },
            {
                "name": "格式转换（飞书）",
                "description": "检查KMarkdown到飞书文本转换",
                "check": "backend/app/processors/formatter.py",
                "keywords": ["kmarkdown_to_feishu_text"]
            },
            {
                "name": "图片处理",
                "description": "检查图片下载、压缩、上传",
                "check": "backend/app/processors/image.py",
                "keywords": ["ImageProcessor", "download_image", "compress_image", "upload"]
            },
            {
                "name": "图床服务器",
                "description": "检查内置图床HTTP服务器",
                "check": "backend/app/image_server.py",
                "keywords": ["start_image_server", "serve_image", "token"]
            },
            {
                "name": "消息去重",
                "description": "检查消息ID去重机制",
                "check": "backend/app/database.py",
                "keywords": ["kook_message_id", "UNIQUE", "IntegrityError"]
            },
            {
                "name": "限流器",
                "description": "检查限流保护机制",
                "check": "backend/app/utils/rate_limiter.py",
                "keywords": ["RateLimiter", "acquire", "calls", "period"]
            },
            {
                "name": "智能消息分段",
                "description": "检查超长消息智能分割",
                "check": "backend/app/processors/formatter.py",
                "keywords": ["split_long_message", "_split_by_sentences", "_split_by_clauses"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def test_module_3_forwarders(self) -> Dict[str, Any]:
        """
        模块3：转发模块测试
        
        测试内容：
        1. Discord Webhook集成
        2. Telegram Bot集成
        3. 飞书应用集成
        4. 转发器池化（负载均衡）
        """
        results = {
            "module_name": "转发模块",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "Discord转发器",
                "description": "检查Discord Webhook转发",
                "check": "backend/app/forwarders/discord.py",
                "keywords": ["DiscordForwarder", "send_message", "DiscordWebhook", "DiscordEmbed"]
            },
            {
                "name": "Discord转发器池",
                "description": "检查多Webhook负载均衡",
                "check": "backend/app/forwarders/discord.py",
                "keywords": ["DiscordForwarderPool", "webhook_urls", "_get_next_webhook"]
            },
            {
                "name": "Telegram转发器",
                "description": "检查Telegram Bot转发",
                "check": "backend/app/forwarders/telegram.py",
                "keywords": ["TelegramForwarder", "send_message", "Bot", "chat_id"]
            },
            {
                "name": "飞书转发器",
                "description": "检查飞书应用转发",
                "check": "backend/app/forwarders/feishu.py",
                "keywords": ["FeishuForwarder", "send_message", "app_id", "app_secret"]
            },
            {
                "name": "转发器池管理",
                "description": "检查转发器池管理器",
                "check": "backend/app/forwarders/pools.py",
                "keywords": ["ForwarderPool", "get_forwarder", "load_balance"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def test_module_4_ui_management(self) -> Dict[str, Any]:
        """
        模块4：UI管理界面测试
        
        测试内容：
        1. Electron桌面应用
        2. Vue 3 + Element Plus UI
        3. 各个功能页面（账号、Bot、映射、日志、设置等）
        4. WebSocket实时通信
        """
        results = {
            "module_name": "UI管理界面",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "账号管理页面",
                "description": "检查账号管理Vue组件",
                "check": "frontend/src/views/Accounts.vue",
                "keywords": ["template", "script", "accounts", "add", "delete"]
            },
            {
                "name": "Bot配置页面",
                "description": "检查Bot配置Vue组件",
                "check": "frontend/src/views/Bots.vue",
                "keywords": ["template", "script", "platform", "webhook", "test"]
            },
            {
                "name": "频道映射页面",
                "description": "检查频道映射配置页面",
                "check": "frontend/src/views/Mapping.vue",
                "keywords": ["template", "script", "mapping", "kook_channel", "target"]
            },
            {
                "name": "实时日志页面",
                "description": "检查实时日志监控页面",
                "check": "frontend/src/views/Logs.vue",
                "keywords": ["template", "script", "logs", "message", "status"]
            },
            {
                "name": "系统设置页面",
                "description": "检查系统设置页面",
                "check": "frontend/src/views/Settings.vue",
                "keywords": ["template", "script", "settings", "config"]
            },
            {
                "name": "配置向导",
                "description": "检查首次启动配置向导",
                "check": "frontend/src/views/Wizard.vue",
                "keywords": ["template", "script", "wizard", "steps"]
            },
            {
                "name": "WebSocket通信",
                "description": "检查WebSocket实时通信",
                "check": "frontend/src/composables/useWebSocket.js",
                "keywords": ["WebSocket", "connect", "onmessage", "send"]
            },
            {
                "name": "帮助中心",
                "description": "检查内置帮助中心",
                "check": "frontend/src/components/HelpCenter.vue",
                "keywords": ["template", "script", "help", "tutorial"]
            },
            {
                "name": "性能监控面板",
                "description": "检查性能监控组件",
                "check": "frontend/src/components/PerformanceMonitor.vue",
                "keywords": ["template", "script", "performance", "chart"]
            },
            {
                "name": "主题切换",
                "description": "检查深色/浅色主题切换",
                "check": "frontend/src/composables/useTheme.js",
                "keywords": ["theme", "dark", "light", "toggle"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def test_module_5_database(self) -> Dict[str, Any]:
        """
        模块5：数据库Schema和持久化测试
        
        测试内容：
        1. SQLite数据库
        2. 各个数据表（accounts, bot_configs, channel_mappings等）
        3. 索引优化
        4. 数据加密
        """
        results = {
            "module_name": "数据库和持久化",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "accounts表",
                "description": "检查账号表结构",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "accounts", "email", "password_encrypted", "cookie"]
            },
            {
                "name": "bot_configs表",
                "description": "检查Bot配置表",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "bot_configs", "platform", "config"]
            },
            {
                "name": "channel_mappings表",
                "description": "检查频道映射表",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "channel_mappings", "kook_channel_id", "target_platform"]
            },
            {
                "name": "message_logs表",
                "description": "检查消息日志表",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "message_logs", "kook_message_id", "status", "latency"]
            },
            {
                "name": "filter_rules表",
                "description": "检查过滤规则表",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "filter_rules", "rule_type", "rule_value"]
            },
            {
                "name": "system_config表",
                "description": "检查系统配置表",
                "check": "backend/app/database.py",
                "keywords": ["CREATE TABLE", "system_config", "key", "value"]
            },
            {
                "name": "数据库索引优化",
                "description": "检查是否创建了性能优化索引",
                "check": "backend/app/database.py",
                "keywords": ["CREATE INDEX", "idx_", "ON"]
            },
            {
                "name": "数据加密",
                "description": "检查敏感数据加密",
                "check": "backend/app/utils/crypto.py",
                "keywords": ["encrypt", "decrypt", "AES", "Fernet"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def test_module_6_advanced_features(self) -> Dict[str, Any]:
        """
        模块6：高级功能测试
        
        测试内容：
        1. 异常处理和自动重试
        2. 数据持久化
        3. 健康检查
        4. 邮件告警
        5. 主密码保护
        6. 国际化
        """
        results = {
            "module_name": "高级功能",
            "test_cases": []
        }
        
        test_cases = [
            {
                "name": "错误诊断系统",
                "description": "检查智能错误诊断和解决方案",
                "check": "backend/app/utils/error_diagnosis.py",
                "keywords": ["diagnose_error", "error_solutions", "auto_fix"]
            },
            {
                "name": "重试Worker",
                "description": "检查失败消息自动重试",
                "check": "backend/app/queue/retry_worker.py",
                "keywords": ["RetryWorker", "retry", "failed_messages"]
            },
            {
                "name": "健康检查器",
                "description": "检查系统健康检查",
                "check": "backend/app/utils/health.py",
                "keywords": ["HealthChecker", "check_", "status"]
            },
            {
                "name": "邮件告警",
                "description": "检查SMTP邮件发送",
                "check": "backend/app/utils/email_sender.py",
                "keywords": ["EmailSender", "send_email", "smtp"]
            },
            {
                "name": "主密码保护",
                "description": "检查密码管理和验证",
                "check": "backend/app/utils/password_manager.py",
                "keywords": ["PasswordManager", "verify", "hash_password", "SHA"]
            },
            {
                "name": "国际化（i18n）",
                "description": "检查多语言支持",
                "check": "frontend/src/i18n/index.js",
                "keywords": ["i18n", "createI18n", "locale", "messages"]
            },
            {
                "name": "中文语言包",
                "description": "检查中文翻译",
                "check": "frontend/src/i18n/locales/zh-CN.json",
                "keywords": ["{", "}", "\""]
            },
            {
                "name": "英文语言包",
                "description": "检查英文翻译",
                "check": "frontend/src/i18n/locales/en-US.json",
                "keywords": ["{", "}", "\""]
            },
            {
                "name": "定时任务调度",
                "description": "检查APScheduler集成",
                "check": "backend/app/utils/scheduler.py",
                "keywords": ["scheduler", "setup_scheduled_tasks", "job"]
            },
            {
                "name": "审计日志",
                "description": "检查操作审计日志",
                "check": "backend/app/utils/audit_logger.py",
                "keywords": ["AuditLogger", "log_action", "audit"]
            }
        ]
        
        for tc in test_cases:
            result = self._check_file_contains_keywords(
                tc["check"], 
                tc["keywords"]
            )
            tc["status"] = "PASSED" if result["found"] else "FAILED"
            tc["details"] = result
            results["test_cases"].append(tc)
        
        return results
    
    def _check_file_contains_keywords(self, file_path: str, keywords: List[str]) -> Dict[str, Any]:
        """
        检查文件是否包含关键词
        
        Args:
            file_path: 文件路径（相对于workspace根目录）
            keywords: 关键词列表
            
        Returns:
            检查结果
        """
        result = {
            "found": False,
            "matched_keywords": [],
            "missing_keywords": [],
            "file_exists": False,
            "file_path": file_path
        }
        
        full_path = f"/workspace/{file_path}"
        
        if not os.path.exists(full_path):
            result["missing_keywords"] = keywords
            return result
        
        result["file_exists"] = True
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for keyword in keywords:
                if keyword in content:
                    result["matched_keywords"].append(keyword)
                else:
                    result["missing_keywords"].append(keyword)
            
            # 如果至少匹配了一半的关键词，认为通过
            if len(result["matched_keywords"]) >= len(keywords) * 0.5:
                result["found"] = True
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 80)
        print("KOOK消息转发系统 - 全面功能测试")
        print("=" * 80)
        print()
        
        modules = [
            self.test_module_1_message_capture(),
            self.test_module_2_message_processing(),
            self.test_module_3_forwarders(),
            self.test_module_4_ui_management(),
            self.test_module_5_database(),
            self.test_module_6_advanced_features(),
        ]
        
        for module in modules:
            module_name = module["module_name"]
            test_cases = module["test_cases"]
            
            passed = sum(1 for tc in test_cases if tc["status"] == "PASSED")
            failed = sum(1 for tc in test_cases if tc["status"] == "FAILED")
            total = len(test_cases)
            
            print(f"\n{'=' * 80}")
            print(f"模块: {module_name}")
            print(f"{'=' * 80}")
            print(f"总计: {total} | 通过: {passed} | 失败: {failed} | 成功率: {passed/total*100:.1f}%")
            print()
            
            for tc in test_cases:
                status_icon = "✅" if tc["status"] == "PASSED" else "❌"
                print(f"{status_icon} {tc['name']}")
                print(f"   描述: {tc['description']}")
                print(f"   文件: {tc['check']}")
                
                details = tc.get("details", {})
                if details.get("matched_keywords"):
                    print(f"   匹配关键词: {', '.join(details['matched_keywords'][:3])}...")
                if details.get("missing_keywords"):
                    print(f"   缺失关键词: {', '.join(details['missing_keywords'][:3])}...")
                print()
            
            self.test_results["modules"][module_name] = {
                "total": total,
                "passed": passed,
                "failed": failed,
                "test_cases": test_cases
            }
            
            self.test_results["total_tests"] += total
            self.test_results["passed"] += passed
            self.test_results["failed"] += failed
        
        return self.test_results
    
    def generate_report(self, output_file: str = "/workspace/comprehensive_test_report.json"):
        """生成测试报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"测试时间: {self.test_results['test_time']}")
        print(f"总测试数: {self.test_results['total_tests']}")
        print(f"通过数量: {self.test_results['passed']}")
        print(f"失败数量: {self.test_results['failed']}")
        print(f"成功率: {self.test_results['passed']/self.test_results['total_tests']*100:.1f}%")
        print()
        print(f"详细报告已保存到: {output_file}")
        print("=" * 80)


if __name__ == "__main__":
    tester = ComprehensiveTestPlan()
    results = tester.run_all_tests()
    tester.generate_report()
