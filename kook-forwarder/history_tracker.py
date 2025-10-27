"""
历史数据跟踪器
记录和对比历史测试数据
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class HistoryTracker:
    """历史数据跟踪器"""
    
    def __init__(self, history_dir="test_results/history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.max_records = 100  # 最多保留100条历史记录
    
    def save_current_results(self):
        """保存当前测试结果到历史记录"""
        print("📊 保存测试结果到历史记录...")
        
        test_results_dir = Path("test_results")
        if not test_results_dir.exists():
            print("❌ test_results 目录不存在")
            return
        
        # 创建历史记录条目
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "test_date": datetime.now().strftime("%Y-%m-%d"),
            "test_time": datetime.now().strftime("%H:%M:%S"),
            "reports": {}
        }
        
        # 收集所有测试报告
        report_files = list(test_results_dir.glob("*_report.json"))
        
        for report_file in report_files:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取关键指标
                metrics = self._extract_metrics(data, report_file.stem)
                if metrics:
                    history_entry["reports"][report_file.stem] = metrics
            
            except Exception as e:
                print(f"  ⚠️  读取 {report_file.name} 失败: {e}")
        
        # 保存历史记录
        history_file = self.history_dir / f"history_{timestamp}.json"
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_entry, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 历史记录已保存: {history_file.name}")
            
            # 清理旧记录
            self._cleanup_old_records()
            
            return history_file
        
        except Exception as e:
            print(f"  ❌ 保存历史记录失败: {e}")
            return None
    
    def _extract_metrics(self, data, report_type):
        """提取关键性能指标"""
        metrics = {}
        
        if 'comprehensive' in report_type and 'test_results' in data:
            test_results = data['test_results']
            
            # API指标
            if 'api_stress' in test_results and 'results' in test_results['api_stress']:
                api_results = test_results['api_stress']['results']
                if api_results:
                    # 取并发100的数据
                    for r in api_results:
                        if r.get('concurrent') == 100:
                            metrics['api_qps_100'] = r.get('qps', 0)
                            metrics['api_avg_latency'] = r.get('avg_time_ms', 0)
                            break
            
            # 格式转换指标
            if 'formatter_stress' in test_results and 'results' in test_results['formatter_stress']:
                formatter_results = test_results['formatter_stress']['results']
                if formatter_results:
                    last = formatter_results[-1]
                    if 'discord' in last:
                        metrics['discord_ops'] = last['discord'].get('ops_per_sec', 0)
                    if 'telegram' in last:
                        metrics['telegram_ops'] = last['telegram'].get('ops_per_sec', 0)
            
            # Redis队列指标
            if 'redis_queue_stress' in test_results and 'results' in test_results['redis_queue_stress']:
                queue_results = test_results['redis_queue_stress']['results']
                for r in queue_results:
                    if r.get('batch_size') == 1000:
                        metrics['redis_enqueue_qps'] = r.get('enqueue_qps', 0)
                        metrics['redis_dequeue_qps'] = r.get('dequeue_qps', 0)
                        break
        
        elif 'demo' in report_type and 'results' in data:
            results = data['results']
            
            # 提取演示测试指标
            if 'message_formatting' in results and results['message_formatting']:
                last = results['message_formatting'][-1]
                metrics['format_ops'] = last.get('ops_per_second', 0)
            
            if 'concurrent_processing' in results and results['concurrent_processing']:
                last = results['concurrent_processing'][-1]
                metrics['throughput'] = last.get('throughput', 0)
        
        return metrics
    
    def _cleanup_old_records(self):
        """清理旧的历史记录"""
        history_files = sorted(self.history_dir.glob("history_*.json"))
        
        if len(history_files) > self.max_records:
            # 删除最旧的记录
            for old_file in history_files[:-self.max_records]:
                try:
                    old_file.unlink()
                    print(f"  🗑️  已删除旧记录: {old_file.name}")
                except Exception as e:
                    print(f"  ⚠️  删除 {old_file.name} 失败: {e}")
    
    def load_history(self, limit=10):
        """加载历史记录"""
        history_files = sorted(self.history_dir.glob("history_*.json"), reverse=True)
        
        history_data = []
        
        for history_file in history_files[:limit]:
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history_data.append(data)
            except Exception as e:
                print(f"  ⚠️  加载 {history_file.name} 失败: {e}")
        
        return history_data
    
    def compare_with_baseline(self, baseline_date=None):
        """与基线对比"""
        print("\n📊 性能趋势分析")
        print("=" * 70)
        
        history_data = self.load_history(limit=10)
        
        if len(history_data) < 2:
            print("历史数据不足，无法进行对比")
            return
        
        current = history_data[0]
        previous = history_data[1]
        
        print(f"\n当前测试: {current['test_date']} {current['test_time']}")
        print(f"对比测试: {previous['test_date']} {previous['test_time']}")
        print()
        
        # 对比各项指标
        for report_type in current.get('reports', {}):
            if report_type not in previous.get('reports', {}):
                continue
            
            print(f"\n📋 {report_type}")
            print("-" * 70)
            
            current_metrics = current['reports'][report_type]
            previous_metrics = previous['reports'][report_type]
            
            for metric_name in current_metrics:
                if metric_name not in previous_metrics:
                    continue
                
                current_value = current_metrics[metric_name]
                previous_value = previous_metrics[metric_name]
                
                if previous_value == 0:
                    continue
                
                change_percent = ((current_value - previous_value) / previous_value) * 100
                
                # 判断变化方向
                if abs(change_percent) < 5:
                    icon = "➡️"
                    status = "持平"
                elif change_percent > 0:
                    icon = "📈"
                    status = "提升"
                else:
                    icon = "📉"
                    status = "下降"
                
                print(f"  {icon} {metric_name}: {current_value:.2f} "
                      f"({status} {abs(change_percent):.2f}%)")
        
        # 生成趋势报告
        self._generate_trend_report(history_data)
    
    def _generate_trend_report(self, history_data):
        """生成趋势报告"""
        trend_file = Path("test_results/performance_trend.txt")
        
        try:
            with open(trend_file, 'w', encoding='utf-8') as f:
                f.write("# 性能趋势报告\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"历史记录数: {len(history_data)}\n\n")
                
                # 写入详细数据
                for i, record in enumerate(history_data):
                    f.write(f"\n## 记录 {i+1}: {record['test_date']} {record['test_time']}\n\n")
                    
                    for report_type, metrics in record.get('reports', {}).items():
                        f.write(f"### {report_type}\n")
                        for metric, value in metrics.items():
                            f.write(f"- {metric}: {value:.2f}\n")
                        f.write("\n")
            
            print(f"\n📄 趋势报告已保存: {trend_file}")
        
        except Exception as e:
            print(f"❌ 生成趋势报告失败: {e}")


def main():
    """主函数"""
    tracker = HistoryTracker()
    
    # 保存当前结果
    tracker.save_current_results()
    
    # 对比分析
    tracker.compare_with_baseline()


if __name__ == "__main__":
    main()
