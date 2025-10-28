#!/usr/bin/env python3
"""
快速测试脚本 - 测试新增的P0级优化功能
"""
import asyncio
import aiohttp
import json

API_BASE = "http://localhost:9527"

async def test_cookie_auto_import():
    """测试Cookie自动导入功能"""
    print("\n" + "="*60)
    print("测试1: Cookie自动导入API")
    print("="*60)
    
    # 模拟Chrome扩展发送Cookie
    test_cookies = [
        {
            "name": "token",
            "value": "test_token_123",
            "domain": ".kookapp.cn",
            "path": "/",
            "secure": True,
            "httpOnly": True
        },
        {
            "name": "user_id",
            "value": "123456",
            "domain": ".kookapp.cn",
            "path": "/"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        try:
            # 发送Cookie
            print("📤 发送Cookie到 /api/cookie-import/auto...")
            async with session.post(
                f"{API_BASE}/api/cookie-import/auto",
                json={
                    "cookies": test_cookies,
                    "source": "test-script",
                    "extension_version": "3.0.0",
                    "timestamp": 1234567890
                }
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("✅ Cookie发送成功:")
                    print(f"   - 消息: {result.get('message')}")
                    print(f"   - Cookie数量: {result.get('cookie_count')}")
                else:
                    print(f"❌ 失败: HTTP {resp.status}")
                    print(await resp.text())
            
            # 测试轮询
            print("\n📥 测试轮询获取Cookie...")
            async with session.get(f"{API_BASE}/api/cookie-import/poll") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('has_new'):
                        print("✅ 成功获取到新Cookie:")
                        print(f"   - Cookie ID: {result.get('cookie_id')}")
                        print(f"   - 来源: {result.get('source')}")
                        print(f"   - 数量: {len(result.get('cookies', []))}")
                    else:
                        print("ℹ️  没有新的Cookie")
                else:
                    print(f"❌ 失败: HTTP {resp.status}")
                    
        except aiohttp.ClientConnectorError:
            print("❌ 无法连接到后端服务")
            print("   请确保后端已启动: python backend/app/main.py")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


async def test_server_discovery():
    """测试服务器自动发现功能"""
    print("\n" + "="*60)
    print("测试2: 服务器自动发现API")
    print("="*60)
    
    # 注意：这需要有一个已登录的账号
    account_id = 1  # 假设账号ID为1
    
    async with aiohttp.ClientSession() as session:
        try:
            # 尝试从缓存获取
            print(f"📦 从缓存获取账号 {account_id} 的服务器...")
            async with session.get(
                f"{API_BASE}/api/server-discovery/cached/{account_id}"
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('success'):
                        servers = result.get('servers', [])
                        print(f"✅ 成功获取 {len(servers)} 个服务器")
                        for server in servers[:3]:  # 只显示前3个
                            channels_count = len(server.get('channels', []))
                            print(f"   - {server.get('name')}: {channels_count} 个频道")
                    else:
                        print("ℹ️  缓存中没有数据")
                else:
                    print(f"⚠️  API响应: HTTP {resp.status}")
                    
        except aiohttp.ClientConnectorError:
            print("❌ 无法连接到后端服务")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


async def test_image_server_security():
    """测试图床安全机制"""
    print("\n" + "="*60)
    print("测试3: 图床安全机制")
    print("="*60)
    
    # 注意：这需要图床服务器运行在8765端口
    image_server = "http://localhost:8765"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 测试1: 无Token访问（应该失败）
            print("🔒 测试无Token访问（预期失败）...")
            async with session.get(f"{image_server}/images/test.jpg") as resp:
                if resp.status == 403:
                    print("✅ 正确拦截：无Token访问被禁止")
                else:
                    print(f"⚠️  意外状态: HTTP {resp.status}")
            
            # 测试2: 路径遍历攻击（应该失败）
            print("\n🔒 测试路径遍历攻击（预期失败）...")
            async with session.get(
                f"{image_server}/images/..%2F..%2Fetc%2Fpasswd?token=test"
            ) as resp:
                if resp.status in [400, 403]:
                    print("✅ 正确拦截：路径遍历攻击被阻止")
                else:
                    print(f"⚠️  意外状态: HTTP {resp.status}")
                    
        except aiohttp.ClientConnectorError:
            print("ℹ️  图床服务器未启动（这是正常的）")
            print("   图床会在处理图片时自动启动")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


async def main():
    """主测试函数"""
    print("\n" + "🎯"*30)
    print("KOOK消息转发系统 - 新功能测试")
    print("🎯"*30)
    print("\n这将测试以下新增功能:")
    print("1. Cookie自动导入API")
    print("2. 服务器自动发现API")
    print("3. 图床安全机制")
    print("\n⚠️  请确保后端服务已启动！")
    print("   启动命令: cd backend && python -m app.main")
    
    input("\n按Enter键开始测试...")
    
    # 运行测试
    await test_cookie_auto_import()
    await test_server_discovery()
    await test_image_server_security()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
    print("\n详细优化报告请查看: OPTIMIZATION_REPORT.md")
    print("任务状态请查看: TODO_STATUS.md")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
