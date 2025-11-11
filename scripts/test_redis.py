"""
Redis连接测试脚本
测试Redis服务连接、读写操作和基本信息
"""
import sys

def test_redis():
    """测试Redis连接"""
    
    print("=" * 60)
    print("Redis连接测试")
    print("=" * 60)
    
    try:
        import redis
    except ImportError:
        print("❌ Redis模块未安装")
        print("ℹ️  运行: pip install redis")
        return False
    
    try:
        # 连接Redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            socket_connect_timeout=5,
            decode_responses=True
        )
        
        # Ping测试
        print("📡 测试连接...")
        response = r.ping()
        print(f"✅ Ping响应: {response}")
        
        # 写入测试
        print("\n📝 测试写入...")
        r.set('test_key', 'test_value', ex=60)
        print("✅ 写入成功")
        
        # 读取测试
        print("\n📖 测试读取...")
        value = r.get('test_key')
        print(f"✅ 读取成功: {value}")
        
        # 删除测试键
        r.delete('test_key')
        
        # 获取Redis信息
        print("\n" + "=" * 60)
        print("📊 Redis服务信息")
        print("-" * 60)
        info = r.info()
        print(f"✅ Redis版本: {info.get('redis_version', 'N/A')}")
        print(f"✅ 运行时间: {info.get('uptime_in_seconds', 0)} 秒")
        print(f"✅ 已连接客户端: {info.get('connected_clients', 0)}")
        print(f"✅ 使用内存: {info.get('used_memory_human', 'N/A')}")
        print(f"✅ 键总数: {r.dbsize()}")
        
        print("\n" + "=" * 60)
        print("✅ Redis连接测试通过！")
        print("=" * 60)
        
        return True
        
    except redis.ConnectionError:
        print("❌ 无法连接到Redis服务")
        print("⚠️  请检查Redis是否正在运行")
        print("ℹ️  系统将使用内置Redis（自动降级）")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_redis()
    sys.exit(0 if success else 1)
