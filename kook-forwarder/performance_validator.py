"""
性能基准验证器
验证测试结果是否达到性能基准要求
"""
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class PerformanceValidator:
    """性能验证器"""
    
    def __init__(self, config_path="stress_test_config.yaml"):
        self.config = self._load_config(config_path)
        self.benchmarks = self.config.get('benchmarks', {})
        self.requirements = self._extract_requirements()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_pass': True,
            'checks': [],
            'grade': 'Unknown',
            'score': 0
        }
    
    def _load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  无法加载配置文件: {e}")
            return {}
    
    def _extract_requirements(self):
        """提取所有性能要求"""
        requirements = {}
        
        # API要求
        if 'api_tests' in self.config:
            requirements['api'] = self.config['api_tests'].get('requirements', {})
        
        # 消息处理要求
        if 'message_processing' in self.config:
            requirements['message_processing'] = self.config['message_processing'].get('requirements', {})
        
        # Redis队列要求
        if 'redis_queue' in self.config:
            requirements['redis_queue'] = self.config['redis_queue'].get('requirements', {})
        
        # 数据库要求
        if 'database' in self.config:
            requirements['database'] = self.config['database'].get('requirements', {})
        
        return requirements
    
    def validate_all_reports(self):
        """验证所有测试报告"""
        print("=" * 70)
        print("性能基准验证")
        print("=" * 70)
        
        test_results_dir = Path("test_results")
        if not test_results_dir.exists():
            print("❌ test_results 目录不存在")
            return False
        
        report_files = list(test_results_dir.glob("*_report.json"))
        
        if not report_files:
            print("❌ 未找到测试报告")
            return False
        
        print(f"\n找到 {len(report_files)} 个测试报告\n")
        
        total_checks = 0
        passed_checks = 0
        
        for report_file in report_files:
            print(f"\n📄 验证: {report_file.name}")
            print("-" * 70)
            
            data = self._load_report(report_file)
            if not data:
                continue
            
            # 根据报告类型进行验证
            if 'comprehensive' in report_file.name:
                checks, passed = self._validate_comprehensive_report(data)
            elif 'demo' in report_file.name:
                checks, passed = self._validate_demo_report(data)
            elif 'module' in report_file.name:
                checks, passed = self._validate_module_report(data)
            else:
                continue
            
            total_checks += checks
            passed_checks += passed
            
            self.results['checks'].extend(self._get_last_checks())
        
        # 计算总体结果
        if total_checks > 0:
            pass_rate = (passed_checks / total_checks) * 100
            self.results['score'] = round(pass_rate, 2)
            self.results['overall_pass'] = pass_rate >= 80
            self.results['grade'] = self._calculate_grade(pass_rate)
        
        # 打印总结
        self._print_summary(total_checks, passed_checks)
        
        # 保存验证结果
        self._save_results()
        
        return self.results['overall_pass']
    
    def _load_report(self, report_path):
        """加载测试报告"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ❌ 加载报告失败: {e}")
            return None
    
    def _validate_comprehensive_report(self, data):
        """验证全面测试报告"""
        checks = 0
        passed = 0
        
        if 'test_results' not in data:
            return checks, passed
        
        test_results = data['test_results']
        
        # 验证API性能
        if 'api_stress' in test_results and 'api' in self.requirements:
            c, p = self._validate_api_performance(test_results['api_stress'])
            checks += c
            passed += p
        
        # 验证格式转换性能
        if 'formatter_stress' in test_results and 'message_processing' in self.requirements:
            c, p = self._validate_formatter_performance(test_results['formatter_stress'])
            checks += c
            passed += p
        
        # 验证Redis队列性能
        if 'redis_queue_stress' in test_results and 'redis_queue' in self.requirements:
            c, p = self._validate_redis_performance(test_results['redis_queue_stress'])
            checks += c
            passed += p
        
        return checks, passed
    
    def _validate_api_performance(self, test_data):
        """验证API性能"""
        checks = 0
        passed = 0
        
        if 'results' not in test_data:
            return checks, passed
        
        results = test_data['results']
        req = self.requirements.get('api', {})
        
        # 查找并发100的结果
        result_100 = None
        for r in results:
            if r.get('concurrent') == 100:
                result_100 = r
                break
        
        if result_100:
            # 检查QPS
            if 'min_qps' in req:
                checks += 1
                actual_qps = result_100.get('qps', 0)
                min_qps = req['min_qps']
                
                if actual_qps >= min_qps:
                    print(f"  ✅ API QPS: {actual_qps:.2f} (>= {min_qps})")
                    passed += 1
                else:
                    print(f"  ❌ API QPS: {actual_qps:.2f} (< {min_qps})")
            
            # 检查平均延迟
            if 'max_avg_latency_ms' in req:
                checks += 1
                actual_latency = result_100.get('avg_time_ms', 0)
                max_latency = req['max_avg_latency_ms']
                
                if actual_latency <= max_latency:
                    print(f"  ✅ 平均延迟: {actual_latency:.2f}ms (<= {max_latency}ms)")
                    passed += 1
                else:
                    print(f"  ❌ 平均延迟: {actual_latency:.2f}ms (> {max_latency}ms)")
            
            # 检查成功率
            if 'min_success_rate' in req:
                checks += 1
                total = result_100.get('total_requests', 0)
                successful = result_100.get('successful', 0)
                
                if total > 0:
                    success_rate = (successful / total) * 100
                    min_rate = req['min_success_rate']
                    
                    if success_rate >= min_rate:
                        print(f"  ✅ 成功率: {success_rate:.2f}% (>= {min_rate}%)")
                        passed += 1
                    else:
                        print(f"  ❌ 成功率: {success_rate:.2f}% (< {min_rate}%)")
        
        return checks, passed
    
    def _validate_formatter_performance(self, test_data):
        """验证格式转换性能"""
        checks = 0
        passed = 0
        
        if 'results' not in test_data:
            return checks, passed
        
        results = test_data['results']
        req = self.requirements.get('message_processing', {})
        
        # 取最后一次测试结果（最大迭代次数）
        last_result = results[-1] if results else None
        
        if last_result:
            # 检查Discord转换性能
            if 'discord_min_ops' in req and 'discord' in last_result:
                checks += 1
                actual_ops = last_result['discord'].get('ops_per_sec', 0)
                min_ops = req['discord_min_ops']
                
                if actual_ops >= min_ops:
                    print(f"  ✅ Discord转换: {actual_ops:.0f} ops/s (>= {min_ops})")
                    passed += 1
                else:
                    print(f"  ❌ Discord转换: {actual_ops:.0f} ops/s (< {min_ops})")
            
            # 检查Telegram转换性能
            if 'telegram_min_ops' in req and 'telegram' in last_result:
                checks += 1
                actual_ops = last_result['telegram'].get('ops_per_sec', 0)
                min_ops = req['telegram_min_ops']
                
                if actual_ops >= min_ops:
                    print(f"  ✅ Telegram转换: {actual_ops:.0f} ops/s (>= {min_ops})")
                    passed += 1
                else:
                    print(f"  ❌ Telegram转换: {actual_ops:.0f} ops/s (< {min_ops})")
        
        return checks, passed
    
    def _validate_redis_performance(self, test_data):
        """验证Redis性能"""
        checks = 0
        passed = 0
        
        if 'results' not in test_data:
            return checks, passed
        
        results = test_data['results']
        req = self.requirements.get('redis_queue', {})
        
        # 查找批量1000的结果
        result_1000 = None
        for r in results:
            if r.get('batch_size') == 1000:
                result_1000 = r
                break
        
        if result_1000:
            # 检查入队性能
            if 'min_enqueue_qps' in req:
                checks += 1
                actual_qps = result_1000.get('enqueue_qps', 0)
                min_qps = req['min_enqueue_qps']
                
                if actual_qps >= min_qps:
                    print(f"  ✅ 入队性能: {actual_qps:.0f} msg/s (>= {min_qps})")
                    passed += 1
                else:
                    print(f"  ❌ 入队性能: {actual_qps:.0f} msg/s (< {min_qps})")
            
            # 检查出队性能
            if 'min_dequeue_qps' in req:
                checks += 1
                actual_qps = result_1000.get('dequeue_qps', 0)
                min_qps = req['min_dequeue_qps']
                
                if actual_qps >= min_qps:
                    print(f"  ✅ 出队性能: {actual_qps:.0f} msg/s (>= {min_qps})")
                    passed += 1
                else:
                    print(f"  ❌ 出队性能: {actual_qps:.0f} msg/s (< {min_qps})")
        
        return checks, passed
    
    def _validate_demo_report(self, data):
        """验证演示测试报告"""
        # 演示测试只做基本验证
        checks = 1
        passed = 0
        
        if 'results' in data and data['results']:
            print("  ✅ 演示测试执行成功")
            passed = 1
        else:
            print("  ❌ 演示测试未找到结果")
        
        return checks, passed
    
    def _validate_module_report(self, data):
        """验证模块测试报告"""
        # 模块测试做基本验证
        checks = len(data) if isinstance(data, dict) else 0
        passed = 0
        
        if isinstance(data, dict):
            for module, results in data.items():
                if results:
                    print(f"  ✅ {module} 模块测试成功")
                    passed += 1
                else:
                    print(f"  ❌ {module} 模块测试失败")
        
        return checks, passed
    
    def _get_last_checks(self):
        """获取最后的检查结果"""
        # 这里可以实现详细的检查记录
        return []
    
    def _calculate_grade(self, pass_rate):
        """计算性能等级"""
        grades = self.benchmarks.get('grades', {})
        
        if pass_rate >= grades.get('excellent', 120):
            return "优秀 ⭐⭐⭐⭐⭐"
        elif pass_rate >= grades.get('good', 100):
            return "良好 ⭐⭐⭐⭐"
        elif pass_rate >= grades.get('acceptable', 80):
            return "及格 ⭐⭐⭐"
        else:
            return "差 ⭐"
    
    def _print_summary(self, total_checks, passed_checks):
        """打印验证总结"""
        print("\n" + "=" * 70)
        print("验证总结")
        print("=" * 70)
        
        if total_checks > 0:
            pass_rate = (passed_checks / total_checks) * 100
            
            print(f"\n总检查项: {total_checks}")
            print(f"通过检查: {passed_checks}")
            print(f"失败检查: {total_checks - passed_checks}")
            print(f"通过率: {pass_rate:.2f}%")
            print(f"性能等级: {self.results['grade']}")
            
            if self.results['overall_pass']:
                print("\n✅ 性能验证通过！")
            else:
                print("\n❌ 性能验证未通过！")
        else:
            print("\n⚠️  未找到可验证的数据")
    
    def _save_results(self):
        """保存验证结果"""
        output_path = Path("test_results/performance_validation.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 验证结果已保存: {output_path}")
        except Exception as e:
            print(f"\n❌ 保存验证结果失败: {e}")


def main():
    """主函数"""
    validator = PerformanceValidator()
    result = validator.validate_all_reports()
    
    # 返回退出码
    import sys
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
