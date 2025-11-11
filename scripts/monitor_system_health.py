"""
系统健康监控脚本
持续监控系统状态、资源使用和服务健康
"""
import time
import sys
from datetime import datetime

def monitor_health(duration_minutes=5, interval_seconds=30):
    """监控系统健康状况"""
    
    print("=" * 70)
    print(f"系统健康监控 - 持续 {duration_minutes} 分钟")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控间隔: {interval_seconds} 秒")
    print("=" * 70)
    
    iterations = (duration_minutes * 60) // interval_seconds
    
    for i in range(iterations):
        print(f"\n📊 检查 [{i+1}/{iterations}] - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 70)
        
        # 1. 检查后端服务
        try:
            import requests
            response = requests.get('http://localhost:9527/health', timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务: 正常")
                data = response.json()
                if 'status' in data:
                    print(f"   状态: {data['status']}")
            else:
                print(f"⚠️  后端服务: HTTP {response.status_code}")
        except ImportError:
            print("⚠️  requests模块未安装，跳过后端健康检查")
        except Exception as e:
            print(f"❌ 后端服务: 无法连接 ({e})")
        
        # 2. 检查系统资源
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"📈 系统资源:")
            print(f"   CPU: {cpu_percent:.1f}%")
            print(f"   内存: {memory.percent:.1f}% ({memory.used // 1024 // 1024} MB / {memory.total // 1024 // 1024} MB)")
            print(f"   磁盘: {disk.percent:.1f}% ({disk.free // 1024 // 1024 // 1024} GB 可用)")
        except ImportError:
            print("⚠️  psutil模块未安装，跳过系统资源检查")
        except Exception as e:
            print(f"⚠️  无法获取系统资源信息: {e}")
        
        # 3. 检查进程
        try:
            import psutil
            python_processes = []
            node_processes = []
            redis_processes = []
            
            for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
                try:
                    name = proc.info['name'].lower()
                    if 'python' in name:
                        python_processes.append(proc)
                    elif 'node' in name:
                        node_processes.append(proc)
                    elif 'redis' in name:
                        redis_processes.append(proc)
                except:
                    pass
            
            print(f"🔧 相关进程:")
            print(f"   Python: {len(python_processes)} 个")
            print(f"   Node.js: {len(node_processes)} 个")
            print(f"   Redis: {len(redis_processes)} 个")
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  无法获取进程信息: {e}")
        
        # 4. 检查数据目录
        try:
            from pathlib import Path
            data_dir = Path.home() / "Documents" / "KookForwarder" / "data"
            if data_dir.exists():
                db_path = data_dir / "config.db"
                if db_path.exists():
                    db_size = db_path.stat().st_size / 1024
                    print(f"💾 数据库大小: {db_size:.2f} KB")
        except Exception as e:
            print(f"⚠️  无法检查数据目录: {e}")
        
        # 等待下一次检查
        if i < iterations - 1:
            time.sleep(interval_seconds)
    
    print("\n" + "=" * 70)
    print(f"监控完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        # 默认监控5分钟，每30秒检查一次
        monitor_health(duration_minutes=5, interval_seconds=30)
    except KeyboardInterrupt:
        print("\n\n⚠️  监控已手动停止")
        sys.exit(0)
