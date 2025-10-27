"""
性能测试图表生成器
生成各种性能分析图表
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

try:
    import matplotlib
    matplotlib.use('Agg')  # 非GUI后端
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib未安装，将生成简化版图表")


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, output_dir="charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if MATPLOTLIB_AVAILABLE:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
    
    def load_test_results(self, report_path):
        """加载测试结果"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"无法加载测试结果: {e}")
            return None
    
    def generate_all_charts(self, report_paths):
        """生成所有图表"""
        print("🎨 开始生成性能图表...")
        
        charts_generated = []
        
        for report_path in report_paths:
            if not Path(report_path).exists():
                continue
            
            data = self.load_test_results(report_path)
            if not data:
                continue
            
            report_name = Path(report_path).stem
            
            # 根据不同的报告生成不同的图表
            if 'comprehensive' in report_name.lower():
                charts_generated.extend(self._generate_comprehensive_charts(data))
            elif 'demo' in report_name.lower():
                charts_generated.extend(self._generate_demo_charts(data))
            elif 'module' in report_name.lower():
                charts_generated.extend(self._generate_module_charts(data))
        
        # 生成汇总图表
        charts_generated.extend(self._generate_summary_charts())
        
        print(f"✅ 已生成 {len(charts_generated)} 个图表")
        for chart in charts_generated:
            print(f"   📊 {chart}")
        
        return charts_generated
    
    def _generate_comprehensive_charts(self, data):
        """生成全面测试的图表"""
        charts = []
        
        if not MATPLOTLIB_AVAILABLE:
            return self._generate_text_charts(data, "comprehensive")
        
        try:
            # API并发测试图表
            if 'test_results' in data and 'api_stress' in data['test_results']:
                chart_path = self._plot_api_concurrent_test(
                    data['test_results']['api_stress']
                )
                if chart_path:
                    charts.append(chart_path)
            
            # Redis队列性能图表
            if 'test_results' in data and 'redis_queue_stress' in data['test_results']:
                chart_path = self._plot_redis_queue_test(
                    data['test_results']['redis_queue_stress']
                )
                if chart_path:
                    charts.append(chart_path)
            
            # 格式转换性能图表
            if 'test_results' in data and 'formatter_stress' in data['test_results']:
                chart_path = self._plot_formatter_test(
                    data['test_results']['formatter_stress']
                )
                if chart_path:
                    charts.append(chart_path)
        
        except Exception as e:
            print(f"生成图表时出错: {e}")
        
        return charts
    
    def _plot_api_concurrent_test(self, test_data):
        """绘制API并发测试图表"""
        if 'results' not in test_data:
            return None
        
        results = test_data['results']
        
        concurrent_levels = [r['concurrent'] for r in results]
        qps_values = [r['qps'] for r in results]
        avg_times = [r['avg_time_ms'] for r in results]
        p99_times = [r.get('p99_time_ms', 0) for r in results]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # QPS图表
        ax1.plot(concurrent_levels, qps_values, 'o-', linewidth=2, markersize=8)
        ax1.set_xlabel('并发数', fontsize=12)
        ax1.set_ylabel('QPS (请求/秒)', fontsize=12)
        ax1.set_title('API并发性能 - QPS', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 响应时间图表
        ax2.plot(concurrent_levels, avg_times, 'o-', label='平均响应时间', linewidth=2)
        ax2.plot(concurrent_levels, p99_times, 's-', label='P99响应时间', linewidth=2)
        ax2.set_xlabel('并发数', fontsize=12)
        ax2.set_ylabel('响应时间 (ms)', fontsize=12)
        ax2.set_title('API并发性能 - 响应时间', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = self.output_dir / 'api_concurrent_performance.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_redis_queue_test(self, test_data):
        """绘制Redis队列性能图表"""
        if 'results' not in test_data:
            return None
        
        results = test_data['results']
        
        batch_sizes = [r['batch_size'] for r in results]
        enqueue_qps = [r['enqueue_qps'] for r in results]
        dequeue_qps = [r['dequeue_qps'] for r in results]
        batch_qps = [r.get('batch_qps', 0) for r in results]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(batch_sizes))
        width = 0.25
        
        ax.bar([i - width for i in x], enqueue_qps, width, label='入队QPS', alpha=0.8)
        ax.bar(x, dequeue_qps, width, label='出队QPS', alpha=0.8)
        if any(batch_qps):
            ax.bar([i + width for i in x], batch_qps, width, label='批量QPS', alpha=0.8)
        
        ax.set_xlabel('批量大小', fontsize=12)
        ax.set_ylabel('QPS (消息/秒)', fontsize=12)
        ax.set_title('Redis队列性能测试', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(batch_sizes)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self.output_dir / 'redis_queue_performance.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_formatter_test(self, test_data):
        """绘制格式转换性能图表"""
        if 'results' not in test_data:
            return None
        
        results = test_data['results']
        
        iterations = [r['iterations'] for r in results]
        
        # 提取不同平台的性能数据
        discord_ops = [r.get('discord', {}).get('ops_per_sec', 0) for r in results]
        telegram_ops = [r.get('telegram', {}).get('ops_per_sec', 0) for r in results]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if any(discord_ops):
            ax.plot(iterations, discord_ops, 'o-', label='Discord', linewidth=2, markersize=8)
        if any(telegram_ops):
            ax.plot(iterations, telegram_ops, 's-', label='Telegram', linewidth=2, markersize=8)
        
        ax.set_xlabel('迭代次数', fontsize=12)
        ax.set_ylabel('性能 (ops/秒)', fontsize=12)
        ax.set_title('消息格式转换性能', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        
        plt.tight_layout()
        
        output_path = self.output_dir / 'formatter_performance.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _generate_demo_charts(self, data):
        """生成演示测试的图表"""
        charts = []
        
        if not MATPLOTLIB_AVAILABLE:
            return self._generate_text_charts(data, "demo")
        
        try:
            # 创建综合性能对比图
            chart_path = self._plot_demo_summary(data)
            if chart_path:
                charts.append(chart_path)
        except Exception as e:
            print(f"生成演示图表时出错: {e}")
        
        return charts
    
    def _plot_demo_summary(self, data):
        """绘制演示测试汇总图"""
        if 'results' not in data:
            return None
        
        results = data['results']
        
        # 提取各项测试的性能数据
        test_names = []
        performance_values = []
        
        for key, value in results.items():
            if isinstance(value, list) and value:
                # 取最后一项数据
                last_result = value[-1]
                
                if key == 'message_formatting':
                    test_names.append('消息格式转换')
                    performance_values.append(last_result.get('ops_per_second', 0) / 1000)  # 转换为K ops/s
                
                elif key == 'concurrent_processing':
                    test_names.append('并发处理')
                    performance_values.append(last_result.get('throughput', 0))
                
                elif key == 'queue_performance':
                    test_names.append('队列性能')
                    performance_values.append(last_result.get('enqueue_qps', 0) / 1000)
        
        if not test_names:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(test_names, performance_values, color=['#3498db', '#2ecc71', '#e74c3c'])
        
        ax.set_xlabel('性能指标', fontsize=12)
        ax.set_title('演示测试性能汇总', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 在柱状图上添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{width:.0f}',
                   ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        
        output_path = self.output_dir / 'demo_performance_summary.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _generate_module_charts(self, data):
        """生成模块测试的图表"""
        # 简化实现，生成文本格式图表
        return self._generate_text_charts(data, "module")
    
    def _generate_text_charts(self, data, chart_type):
        """生成文本格式的图表（当matplotlib不可用时）"""
        charts = []
        
        output_path = self.output_dir / f'{chart_type}_text_chart.txt'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {chart_type.upper()} 测试结果图表\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 递归打印数据结构
            self._write_text_data(f, data, 0)
        
        charts.append(str(output_path))
        return charts
    
    def _write_text_data(self, f, data, indent=0):
        """递归写入文本数据"""
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    f.write(f"{prefix}{key}:\n")
                    self._write_text_data(f, value, indent + 1)
                else:
                    f.write(f"{prefix}{key}: {value}\n")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                f.write(f"{prefix}[{i}]:\n")
                self._write_text_data(f, item, indent + 1)
    
    def _generate_summary_charts(self):
        """生成汇总图表"""
        # 这里可以添加跨测试的汇总图表
        return []


def main():
    """主函数"""
    print("=" * 60)
    print("性能测试图表生成器")
    print("=" * 60)
    
    # 查找所有测试报告
    test_results_dir = Path("test_results")
    if not test_results_dir.exists():
        print("❌ test_results 目录不存在")
        return
    
    report_files = list(test_results_dir.glob("*_report.json"))
    
    if not report_files:
        print("❌ 未找到测试报告文件")
        return
    
    print(f"\n找到 {len(report_files)} 个测试报告:")
    for report in report_files:
        print(f"  - {report.name}")
    
    # 生成图表
    generator = ChartGenerator()
    charts = generator.generate_all_charts(report_files)
    
    if charts:
        print(f"\n✅ 图表已保存到 charts/ 目录")
    else:
        print(f"\n⚠️  未生成任何图表")


if __name__ == "__main__":
    main()
