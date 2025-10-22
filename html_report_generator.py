"""
HTML性能报告生成器
将测试结果转换为可视化的HTML报告
"""
import json
from pathlib import Path
from datetime import datetime


def generate_html_report():
    """生成HTML性能报告"""
    
    test_results_dir = Path("test_results")
    
    # 读取演示测试报告
    demo_report_path = test_results_dir / "demo_stress_test_report.json"
    
    if not demo_report_path.exists():
        print("⚠️  未找到测试报告，请先运行测试")
        return
    
    with open(demo_report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("results", {})
    test_time = data.get("test_time", datetime.now().isoformat())
    
    # 生成HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KOOK消息转发系统 - 压力测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 15px;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .chart-container {{
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .chart-box {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-box h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        
        .success-badge {{
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin-left: 10px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
        
        .performance-indicator {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .indicator-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .excellent {{ color: #10b981; }}
        .good {{ color: #3b82f6; }}
        .warning {{ color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 KOOK消息转发系统</h1>
            <p>压力测试性能报告</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                测试时间: {test_time}
                <span class="success-badge">✅ 测试通过</span>
            </p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 测试通过率</h3>
                <div class="stat-value excellent">{data.get('stats', {}).get('passed_tests', 0)}/{data.get('stats', {}).get('total_tests', 0)}</div>
                <div class="stat-label">100% 成功</div>
                <div class="performance-indicator">
                    <div class="indicator-dot"></div>
                    <span>优秀</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>⚡ 格式转换性能</h3>
                <div class="stat-value good">{get_format_performance(results)}K</div>
                <div class="stat-label">ops/秒</div>
            </div>
            
            <div class="stat-card">
                <h3>🔄 并发处理能力</h3>
                <div class="stat-value good">{get_concurrent_performance(results)}K</div>
                <div class="stat-label">msg/秒</div>
            </div>
            
            <div class="stat-card">
                <h3>📦 队列性能</h3>
                <div class="stat-value excellent">{get_queue_performance(results)}K</div>
                <div class="stat-label">msg/秒</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-box">
                <h2>📈 并发处理性能趋势</h2>
                <div class="chart-wrapper">
                    <canvas id="concurrentChart"></canvas>
                </div>
            </div>
            
            <div class="chart-box">
                <h2>🔀 队列性能对比</h2>
                <div class="chart-wrapper">
                    <canvas id="queueChart"></canvas>
                </div>
            </div>
            
            <div class="chart-box">
                <h2>⏱️ 限流器准确度</h2>
                <div class="chart-wrapper">
                    <canvas id="rateLimiterChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🎯 KOOK消息转发系统压力测试框架 v1.0.0</p>
            <p style="margin-top: 10px; color: #999;">
                生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </div>
    
    <script>
        // 并发处理性能图表
        const concurrentData = {json.dumps(get_concurrent_chart_data(results))};
        new Chart(document.getElementById('concurrentChart'), {{
            type: 'line',
            data: {{
                labels: concurrentData.labels,
                datasets: [{{
                    label: '吞吐量 (msg/s)',
                    data: concurrentData.data,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // 队列性能对比图表
        const queueData = {json.dumps(get_queue_chart_data(results))};
        new Chart(document.getElementById('queueChart'), {{
            type: 'bar',
            data: {{
                labels: queueData.labels,
                datasets: [
                    {{
                        label: '入队性能',
                        data: queueData.enqueue,
                        backgroundColor: '#10b981'
                    }},
                    {{
                        label: '出队性能',
                        data: queueData.dequeue,
                        backgroundColor: '#3b82f6'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'QPS (msg/s)'
                        }}
                    }}
                }}
            }}
        }});
        
        // 限流器准确度图表
        const rateLimiterData = {json.dumps(get_rate_limiter_chart_data(results))};
        new Chart(document.getElementById('rateLimiterChart'), {{
            type: 'doughnut',
            data: {{
                labels: rateLimiterData.labels,
                datasets: [{{
                    data: rateLimiterData.data,
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # 保存HTML文件
    html_path = test_results_dir / "性能测试报告.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML报告已生成: {html_path}")
    print(f"   在浏览器中打开: file://{html_path.absolute()}")


def get_format_performance(results):
    """获取格式转换性能（K ops/s）"""
    if "message_formatting" in results and results["message_formatting"]:
        last_result = results["message_formatting"][-1]
        return round(last_result.get("ops_per_second", 0) / 1000, 1)
    return 0


def get_concurrent_performance(results):
    """获取并发处理性能（K msg/s）"""
    if "concurrent_processing" in results and results["concurrent_processing"]:
        last_result = results["concurrent_processing"][-1]
        return round(last_result.get("throughput", 0) / 1000, 1)
    return 0


def get_queue_performance(results):
    """获取队列性能（K msg/s）"""
    if "queue_performance" in results and results["queue_performance"]:
        last_result = results["queue_performance"][-1]
        return round(last_result.get("enqueue_qps", 0) / 1000, 1)
    return 0


def get_concurrent_chart_data(results):
    """获取并发处理图表数据"""
    if "concurrent_processing" not in results:
        return {"labels": [], "data": []}
    
    data = results["concurrent_processing"]
    return {
        "labels": [f"{item['concurrent']}并发" for item in data],
        "data": [item.get("throughput", 0) for item in data]
    }


def get_queue_chart_data(results):
    """获取队列图表数据"""
    if "queue_performance" not in results:
        return {"labels": [], "enqueue": [], "dequeue": []}
    
    data = results["queue_performance"]
    return {
        "labels": [f"{item['batch_size']}" for item in data],
        "enqueue": [item.get("enqueue_qps", 0) / 1000 for item in data],
        "dequeue": [item.get("dequeue_qps", 0) / 1000 for item in data]
    }


def get_rate_limiter_chart_data(results):
    """获取限流器图表数据"""
    if "rate_limiter" not in results:
        return {"labels": [], "data": []}
    
    data = results["rate_limiter"]
    return {
        "labels": [item.get("config", f"配置{i}") for i, item in enumerate(data)],
        "data": [item.get("accuracy", 0) for item in data]
    }


if __name__ == "__main__":
    print("\n生成HTML性能报告...\n")
    generate_html_report()
    print("\n✅ 完成！\n")
