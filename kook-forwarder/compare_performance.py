"""
性能对比工具
对比两次测试结果，分析性能变化
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def load_report(file_path):
    """加载测试报告"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法加载 {file_path}: {e}")
        return None


def compare_reports(baseline_path, current_path):
    """对比两个测试报告"""
    
    print("\n" + "=" * 80)
    print("  性能对比分析")
    print("=" * 80)
    print()
    
    # 加载报告
    baseline = load_report(baseline_path)
    current = load_report(current_path)
    
    if not baseline or not current:
        print("❌ 无法加载测试报告")
        return
    
    print(f"基线测试: {baseline_path}")
    print(f"当前测试: {current_path}")
    print()
    
    baseline_results = baseline.get("results", {})
    current_results = current.get("results", {})
    
    # 对比各项性能
    print("=" * 80)
    print("  性能指标对比")
    print("=" * 80)
    print()
    
    # 1. 并发处理性能
    if "concurrent_processing" in baseline_results and "concurrent_processing" in current_results:
        print("📊 并发处理性能:")
        compare_concurrent_processing(
            baseline_results["concurrent_processing"],
            current_results["concurrent_processing"]
        )
        print()
    
    # 2. 队列性能
    if "queue_performance" in baseline_results and "queue_performance" in current_results:
        print("📦 队列性能:")
        compare_queue_performance(
            baseline_results["queue_performance"],
            current_results["queue_performance"]
        )
        print()
    
    # 3. 格式转换性能
    if "message_formatting" in baseline_results and "message_formatting" in current_results:
        print("🔄 格式转换性能:")
        compare_formatting_performance(
            baseline_results["message_formatting"],
            current_results["message_formatting"]
        )
        print()
    
    # 4. 限流器性能
    if "rate_limiter" in baseline_results and "rate_limiter" in current_results:
        print("⏱️  限流器准确度:")
        compare_rate_limiter(
            baseline_results["rate_limiter"],
            current_results["rate_limiter"]
        )
        print()
    
    # 总结
    print("=" * 80)
    print("  总结")
    print("=" * 80)
    print()
    
    generate_summary(baseline_results, current_results)


def compare_concurrent_processing(baseline, current):
    """对比并发处理性能"""
    
    print("  并发级别 | 基线吞吐量 | 当前吞吐量 | 变化 | 状态")
    print("  " + "-" * 70)
    
    for i, (base_item, curr_item) in enumerate(zip(baseline, current)):
        if base_item['concurrent'] != curr_item['concurrent']:
            continue
        
        concurrent = base_item['concurrent']
        base_throughput = base_item.get('throughput', 0)
        curr_throughput = curr_item.get('throughput', 0)
        
        change = ((curr_throughput - base_throughput) / base_throughput * 100) if base_throughput > 0 else 0
        status = get_performance_status(change)
        
        print(f"  {concurrent:^10} | {base_throughput:^12.2f} | {curr_throughput:^12.2f} | "
              f"{change:^6.1f}% | {status}")


def compare_queue_performance(baseline, current):
    """对比队列性能"""
    
    print("  批量大小 | 指标 | 基线QPS | 当前QPS | 变化 | 状态")
    print("  " + "-" * 75)
    
    for base_item, curr_item in zip(baseline, current):
        if base_item['batch_size'] != curr_item['batch_size']:
            continue
        
        batch_size = base_item['batch_size']
        
        # 入队性能
        base_enqueue = base_item.get('enqueue_qps', 0)
        curr_enqueue = curr_item.get('enqueue_qps', 0)
        change_enqueue = ((curr_enqueue - base_enqueue) / base_enqueue * 100) if base_enqueue > 0 else 0
        status_enqueue = get_performance_status(change_enqueue)
        
        print(f"  {batch_size:^9} | 入队 | {base_enqueue:^10.2f} | {curr_enqueue:^10.2f} | "
              f"{change_enqueue:^6.1f}% | {status_enqueue}")
        
        # 出队性能
        base_dequeue = base_item.get('dequeue_qps', 0)
        curr_dequeue = curr_item.get('dequeue_qps', 0)
        change_dequeue = ((curr_dequeue - base_dequeue) / base_dequeue * 100) if base_dequeue > 0 else 0
        status_dequeue = get_performance_status(change_dequeue)
        
        print(f"  {batch_size:^9} | 出队 | {base_dequeue:^10.2f} | {curr_dequeue:^10.2f} | "
              f"{change_dequeue:^6.1f}% | {status_dequeue}")


def compare_formatting_performance(baseline, current):
    """对比格式转换性能"""
    
    print("  迭代次数 | 基线ops/s | 当前ops/s | 变化 | 状态")
    print("  " + "-" * 65)
    
    for base_item, curr_item in zip(baseline, current):
        if base_item['iterations'] != curr_item['iterations']:
            continue
        
        iterations = base_item['iterations']
        base_ops = base_item.get('ops_per_second', 0)
        curr_ops = curr_item.get('ops_per_second', 0)
        
        change = ((curr_ops - base_ops) / base_ops * 100) if base_ops > 0 else 0
        status = get_performance_status(change)
        
        print(f"  {iterations:^10} | {base_ops:^11.2f} | {curr_ops:^11.2f} | "
              f"{change:^6.1f}% | {status}")


def compare_rate_limiter(baseline, current):
    """对比限流器性能"""
    
    print("  配置 | 基线准确度 | 当前准确度 | 变化 | 状态")
    print("  " + "-" * 65)
    
    for base_item, curr_item in zip(baseline, current):
        config = base_item.get('config', '未知')
        base_accuracy = base_item.get('accuracy', 0)
        curr_accuracy = curr_item.get('accuracy', 0)
        
        change = curr_accuracy - base_accuracy
        status = "✅" if abs(change) < 1 else "⚠️"
        
        print(f"  {config[:20]:^20} | {base_accuracy:^11.2f}% | {curr_accuracy:^11.2f}% | "
              f"{change:^6.2f}% | {status}")


def get_performance_status(change_percent):
    """获取性能变化状态"""
    if change_percent > 10:
        return "🚀 优化"
    elif change_percent > 0:
        return "✅ 提升"
    elif change_percent > -5:
        return "➡️  持平"
    elif change_percent > -10:
        return "⚠️  下降"
    else:
        return "❌ 退化"


def generate_summary(baseline, current):
    """生成总结"""
    
    improvements = 0
    regressions = 0
    stable = 0
    
    # 统计各项指标的变化
    metrics = []
    
    # 并发处理
    if "concurrent_processing" in baseline and "concurrent_processing" in current:
        for base, curr in zip(baseline["concurrent_processing"], current["concurrent_processing"]):
            if base['concurrent'] == curr['concurrent']:
                change = ((curr['throughput'] - base['throughput']) / base['throughput'] * 100)
                metrics.append(("并发处理", change))
    
    # 队列性能
    if "queue_performance" in baseline and "queue_performance" in current:
        for base, curr in zip(baseline["queue_performance"], current["queue_performance"]):
            if base['batch_size'] == curr['batch_size']:
                change = ((curr['enqueue_qps'] - base['enqueue_qps']) / base['enqueue_qps'] * 100)
                metrics.append(("队列入队", change))
    
    # 分类统计
    for name, change in metrics:
        if change > 5:
            improvements += 1
        elif change < -5:
            regressions += 1
        else:
            stable += 1
    
    total = len(metrics)
    
    print(f"总测试指标: {total}")
    print(f"  🚀 性能提升: {improvements} ({improvements/total*100:.1f}%)" if total > 0 else "  N/A")
    print(f"  ➡️  性能持平: {stable} ({stable/total*100:.1f}%)" if total > 0 else "  N/A")
    print(f"  ❌ 性能退化: {regressions} ({regressions/total*100:.1f}%)" if total > 0 else "  N/A")
    
    print()
    
    if regressions > 0:
        print("⚠️  警告: 发现性能退化，请检查代码变更")
    elif improvements > total * 0.3:
        print("🎉 恭喜: 性能有明显提升！")
    else:
        print("✅ 性能保持稳定")


def main():
    """主函数"""
    
    if len(sys.argv) < 3:
        print("用法: python compare_performance.py <基线报告> <当前报告>")
        print()
        print("示例:")
        print("  python compare_performance.py \\")
        print("    test_results/demo_stress_test_report.json \\")
        print("    test_results/demo_stress_test_report.json")
        print()
        
        # 尝试自动查找报告
        test_results_dir = Path("test_results")
        if test_results_dir.exists():
            reports = list(test_results_dir.glob("*_report.json"))
            if len(reports) >= 2:
                print("找到的测试报告:")
                for i, report in enumerate(reports[:5]):
                    print(f"  {i+1}. {report}")
                print()
                print("提示: 使用最新的两个报告进行对比")
            elif len(reports) == 1:
                print(f"找到1个测试报告: {reports[0]}")
                print("提示: 需要至少2个报告才能进行对比")
        
        return
    
    baseline_path = Path(sys.argv[1])
    current_path = Path(sys.argv[2])
    
    if not baseline_path.exists():
        print(f"❌ 基线报告不存在: {baseline_path}")
        return
    
    if not current_path.exists():
        print(f"❌ 当前报告不存在: {current_path}")
        return
    
    compare_reports(baseline_path, current_path)
    
    print()


if __name__ == "__main__":
    main()
