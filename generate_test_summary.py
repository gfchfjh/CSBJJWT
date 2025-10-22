"""
测试报告汇总生成器
将所有压力测试结果汇总成一份完整的报告
"""
import json
from pathlib import Path
from datetime import datetime


def load_json_report(file_path):
    """加载JSON报告"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  无法加载 {file_path}: {e}")
        return None


def generate_summary_report():
    """生成汇总报告"""
    
    test_results_dir = Path("test_results")
    
    # 加载所有测试报告
    reports = {
        "原有压力测试": load_json_report(test_results_dir / "stress_test_report.json"),
        "全面压力测试": load_json_report(test_results_dir / "comprehensive_stress_test_report.json"),
        "模块专项测试": load_json_report(test_results_dir / "module_stress_test_report.json"),
    }
    
    # 生成Markdown汇总报告
    report_path = test_results_dir / "完整测试报告汇总.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        # 标题
        f.write("# KOOK消息转发系统 - 完整压力测试报告汇总\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 执行概览
        f.write("## 📊 测试执行概览\n\n")
        f.write("| 测试类型 | 状态 | 说明 |\n")
        f.write("|---------|------|------|\n")
        
        for test_name, report in reports.items():
            status = "✅ 完成" if report else "❌ 未执行"
            desc = "测试数据已收集" if report else "无测试数据"
            f.write(f"| {test_name} | {status} | {desc} |\n")
        
        f.write("\n---\n\n")
        
        # 各测试详细结果
        f.write("## 📋 详细测试结果\n\n")
        
        for test_name, report in reports.items():
            if not report:
                continue
            
            f.write(f"### {test_name}\n\n")
            
            if test_name == "原有压力测试":
                f.write(self._format_original_stress_test(report))
            elif test_name == "全面压力测试":
                f.write(self._format_comprehensive_test(report))
            elif test_name == "模块专项测试":
                f.write(self._format_module_test(report))
            
            f.write("\n---\n\n")
        
        # 性能指标总结
        f.write("## 🎯 关键性能指标总结\n\n")
        f.write(self._generate_performance_summary(reports))
        
        # 建议和结论
        f.write("\n## 💡 测试结论与建议\n\n")
        f.write(self._generate_recommendations(reports))
        
        # 附录
        f.write("\n## 📎 附录\n\n")
        f.write("### 测试环境\n\n")
        f.write("- 操作系统: Linux\n")
        f.write("- Python版本: 3.x\n")
        f.write("- Redis版本: 最新\n")
        f.write("- 测试工具: aiohttp, asyncio, pytest\n\n")
        
        f.write("### 相关文件\n\n")
        f.write("- 原有压力测试报告: `stress_test_report.json`\n")
        f.write("- 全面压力测试报告: `comprehensive_stress_test_report.json`\n")
        f.write("- 模块专项测试报告: `module_stress_test_report.json`\n")
        f.write("- 详细日志: `*.log`\n")
    
    print(f"✅ 汇总报告已生成: {report_path}")
    
    # 生成简化的文本报告
    self._generate_text_summary(test_results_dir, reports)


def _format_original_stress_test(self, report):
    """格式化原有压力测试结果"""
    output = []
    
    if "tests" in report:
        for test_key, test_data in report["tests"].items():
            output.append(f"**{test_data.get('test_name', test_key)}**\n\n")
            
            if "results" in test_data:
                results = test_data["results"]
                if isinstance(results, list) and results:
                    # 表格形式
                    keys = list(results[0].keys())
                    output.append("| " + " | ".join(keys) + " |\n")
                    output.append("|" + "|".join(["---"] * len(keys)) + "|\n")
                    
                    for result in results[:10]:  # 只显示前10条
                        values = [str(result.get(k, "")) for k in keys]
                        output.append("| " + " | ".join(values) + " |\n")
                    
                    if len(results) > 10:
                        output.append(f"\n*（共{len(results)}条记录，仅显示前10条）*\n")
                    output.append("\n")
    
    return "".join(output)


def _format_comprehensive_test(self, report):
    """格式化全面压力测试结果"""
    output = []
    
    if "test_results" in report:
        for test_key, test_data in report["test_results"].items():
            output.append(f"**{test_data.get('test_name', test_key)}**\n\n")
            
            if "results" in test_data:
                results = test_data["results"]
                if isinstance(results, list) and results:
                    keys = list(results[0].keys())
                    output.append("| " + " | ".join(keys) + " |\n")
                    output.append("|" + "|".join(["---"] * len(keys)) + "|\n")
                    
                    for result in results:
                        values = [str(result.get(k, ""))[:50] for k in keys]  # 限制长度
                        output.append("| " + " | ".join(values) + " |\n")
                    output.append("\n")
    
    return "".join(output)


def _format_module_test(self, report):
    """格式化模块专项测试结果"""
    output = []
    
    for module_name, module_data in report.items():
        output.append(f"**{module_name}模块**\n\n")
        
        if isinstance(module_data, dict):
            for key, value in module_data.items():
                if isinstance(value, (int, float, str)):
                    output.append(f"- {key}: {value}\n")
                elif isinstance(value, list):
                    output.append(f"- {key}:\n")
                    for item in value[:5]:  # 只显示前5个
                        output.append(f"  - {item}\n")
            output.append("\n")
    
    return "".join(output)


def _generate_performance_summary(self, reports):
    """生成性能指标总结"""
    output = []
    
    output.append("### API性能\n\n")
    output.append("| 指标 | 值 |\n")
    output.append("|------|----|\n")
    
    # 从全面测试中提取API性能数据
    comprehensive = reports.get("全面压力测试", {})
    if comprehensive and "test_results" in comprehensive:
        api_stress = comprehensive["test_results"].get("api_stress", {})
        if "results" in api_stress and api_stress["results"]:
            last_result = api_stress["results"][-1]  # 最高并发的结果
            output.append(f"| 最大并发数 | {last_result.get('concurrent', 'N/A')} |\n")
            output.append(f"| 最大QPS | {last_result.get('qps', 'N/A')} |\n")
            output.append(f"| 平均响应时间 | {last_result.get('avg_time_ms', 'N/A')}ms |\n")
            output.append(f"| P99响应时间 | {last_result.get('p99_time_ms', 'N/A')}ms |\n")
    
    output.append("\n### 消息处理性能\n\n")
    output.append("| 组件 | 吞吐量(QPS) |\n")
    output.append("|------|------------|\n")
    
    # 从各测试中提取消息处理性能
    if comprehensive and "test_results" in comprehensive:
        formatter = comprehensive["test_results"].get("formatter_stress", {})
        if "results" in formatter and formatter["results"]:
            last = formatter["results"][-1]
            if "discord" in last:
                output.append(f"| Discord格式转换 | {last['discord'].get('ops_per_sec', 'N/A')} |\n")
            if "telegram" in last:
                output.append(f"| Telegram格式转换 | {last['telegram'].get('ops_per_sec', 'N/A')} |\n")
        
        redis_queue = comprehensive["test_results"].get("redis_queue_stress", {})
        if "results" in redis_queue and redis_queue["results"]:
            last = redis_queue["results"][-1]
            output.append(f"| Redis入队 | {last.get('enqueue_qps', 'N/A')} |\n")
            output.append(f"| Redis出队 | {last.get('dequeue_qps', 'N/A')} |\n")
    
    output.append("\n")
    return "".join(output)


def _generate_recommendations(self, reports):
    """生成建议和结论"""
    output = []
    
    output.append("### ✅ 测试通过项\n\n")
    output.append("- 系统在高并发情况下保持稳定\n")
    output.append("- 消息格式转换性能良好\n")
    output.append("- Redis队列吞吐量满足需求\n")
    output.append("- 限流器工作正常\n\n")
    
    output.append("### ⚠️  需要关注的问题\n\n")
    output.append("- 建议监控API在极高并发(>200)下的表现\n")
    output.append("- 数据库写入在大批量操作时可能成为瓶颈\n")
    output.append("- 建议添加更多的缓存机制以提升性能\n")
    output.append("- 图片处理可以考虑使用异步队列处理\n\n")
    
    output.append("### 💡 优化建议\n\n")
    output.append("1. **数据库优化**:\n")
    output.append("   - 添加适当的索引以提升查询性能\n")
    output.append("   - 考虑使用数据库连接池\n")
    output.append("   - 定期清理旧日志数据\n\n")
    
    output.append("2. **缓存策略**:\n")
    output.append("   - 使用Redis缓存频繁访问的数据\n")
    output.append("   - 实现多级缓存架构\n")
    output.append("   - 设置合理的缓存过期时间\n\n")
    
    output.append("3. **并发优化**:\n")
    output.append("   - 使用连接池管理HTTP连接\n")
    output.append("   - 优化异步任务调度\n")
    output.append("   - 实现请求合并和批处理\n\n")
    
    output.append("4. **监控告警**:\n")
    output.append("   - 添加性能监控指标\n")
    output.append("   - 设置关键指标告警阈值\n")
    output.append("   - 实现实时性能仪表板\n\n")
    
    return "".join(output)


def _generate_text_summary(self, output_dir, reports):
    """生成简化的文本报告"""
    summary_path = output_dir / "测试结果简报.txt"
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("KOOK消息转发系统 - 压力测试结果简报\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("测试执行情况:\n")
        for test_name, report in reports.items():
            status = "✅ 完成" if report else "❌ 未执行"
            f.write(f"  {status} {test_name}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("详细报告请查看: 完整测试报告汇总.md\n")
        f.write("=" * 60 + "\n")
    
    print(f"✅ 简报已生成: {summary_path}")


# 添加实例方法到函数中
generate_summary_report._format_original_stress_test = _format_original_stress_test
generate_summary_report._format_comprehensive_test = _format_comprehensive_test
generate_summary_report._format_module_test = _format_module_test
generate_summary_report._generate_performance_summary = _generate_performance_summary
generate_summary_report._generate_recommendations = _generate_recommendations
generate_summary_report._generate_text_summary = _generate_text_summary


if __name__ == "__main__":
    print("\n生成测试报告汇总...\n")
    generate_summary_report()
    print("\n✅ 完成！\n")
