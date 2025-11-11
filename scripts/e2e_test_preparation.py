"""
端到端测试准备检查脚本
检查系统是否具备进行端到端测试的所有条件
"""
import sqlite3
import json
import sys
import socket
from pathlib import Path

DB_PATH = Path.home() / "Documents" / "KookForwarder" / "data" / "config.db"

def check_e2e_requirements():
    """检查端到端测试所需的条件"""
    
    print("=" * 70)
    print("端到端测试准备检查")
    print("=" * 70)
    
    requirements = {
        "数据库": False,
        "KOOK账号": False,
        "有效Cookie": False,
        "Bot配置": False,
        "频道映射": False
    }
    
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return requirements
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. 检查数据库
        print("\n[1/5] 检查数据库...")
        requirements["数据库"] = True
        print("    ✅ 数据库文件存在")
        
        # 2. 检查KOOK账号
        print("\n[2/5] 检查KOOK账号...")
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        
        if account_count > 0:
            requirements["KOOK账号"] = True
            print(f"    ✅ 已配置 {account_count} 个KOOK账号")
            
            # 显示账号详情
            cursor.execute("SELECT id, email, status, cookies FROM accounts")
            accounts = cursor.fetchall()
            
            for i, (acc_id, email, status, cookies) in enumerate(accounts, 1):
                print(f"    [{i}] {email} - 状态: {status}")
                
                if cookies:
                    try:
                        cookie_data = json.loads(cookies)
                        cookie_fields = len(cookie_data)
                        print(f"        ✅ Cookie已配置 ({cookie_fields} 个字段)")
                        
                        # 检查是否包含auth字段
                        if 'auth' in cookie_data or 'authorization' in cookie_data:
                            requirements["有效Cookie"] = True
                            print(f"        ✅ 包含认证字段")
                        else:
                            print(f"        ⚠️  缺少auth认证字段")
                    except:
                        print(f"        ⚠️  Cookie格式可能有问题")
                else:
                    print(f"        ❌ Cookie未配置")
        else:
            print("    ❌ 未配置KOOK账号")
            print("    ℹ️  需要在前端添加KOOK账号")
        
        # 3. 检查Bot配置
        print("\n[3/5] 检查Bot配置...")
        cursor.execute("SELECT COUNT(*) FROM bot_configs WHERE enabled = 1")
        bot_count = cursor.fetchone()[0]
        
        if bot_count > 0:
            requirements["Bot配置"] = True
            print(f"    ✅ 已配置 {bot_count} 个Bot")
            
            # 显示Bot详情
            cursor.execute("""
                SELECT platform, bot_name, webhook_url, enabled 
                FROM bot_configs 
                WHERE enabled = 1
            """)
            bots = cursor.fetchall()
            
            for i, (platform, name, webhook, enabled) in enumerate(bots, 1):
                webhook_preview = webhook[:50] + "..." if len(webhook) > 50 else webhook
                print(f"    [{i}] {platform} - {name}")
                print(f"        Webhook: {webhook_preview}")
        else:
            print("    ❌ 未配置Bot")
            print("    ℹ️  需要在前端配置至少一个Bot (Discord/Telegram/飞书等)")
        
        # 4. 检查频道映射
        print("\n[4/5] 检查频道映射...")
        cursor.execute("SELECT COUNT(*) FROM channel_mappings WHERE enabled = 1")
        mapping_count = cursor.fetchone()[0]
        
        if mapping_count > 0:
            requirements["频道映射"] = True
            print(f"    ✅ 已配置 {mapping_count} 个频道映射")
            
            # 显示映射详情
            cursor.execute("""
                SELECT kook_channel_id, kook_channel_name, bot_id, enabled
                FROM channel_mappings
                WHERE enabled = 1
                LIMIT 5
            """)
            mappings = cursor.fetchall()
            
            for i, (channel_id, channel_name, bot_id, enabled) in enumerate(mappings, 1):
                print(f"    [{i}] KOOK频道: {channel_name} ({channel_id})")
                print(f"        → Bot ID: {bot_id}")
        else:
            print("    ❌ 未配置频道映射")
            print("    ℹ️  需要在前端配置频道映射关系")
        
        # 5. 检查系统服务
        print("\n[5/5] 检查系统服务...")
        
        # 检查后端
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 9527))
            sock.close()
            
            if result == 0:
                print("    ✅ 后端服务运行中 (端口 9527)")
            else:
                print("    ❌ 后端服务未运行")
        except:
            print("    ❌ 无法检查后端服务")
        
        # 检查前端
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 5173))
            sock.close()
            
            if result == 0:
                print("    ✅ 前端服务运行中 (端口 5173)")
            else:
                print("    ⚠️  前端服务未运行")
        except:
            print("    ⚠️  无法检查前端服务")
        
        conn.close()
        
        # 生成测试报告
        print("\n" + "=" * 70)
        print("📊 端到端测试准备状态")
        print("=" * 70)
        
        total = len(requirements)
        completed = sum(requirements.values())
        progress = (completed / total) * 100
        
        for item, status in requirements.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {item}")
        
        print(f"\n📈 完成度: {completed}/{total} ({progress:.0f}%)")
        
        if completed == total:
            print("\n🎉 所有准备工作已完成，可以开始端到端测试！")
            print("\n下一步操作:")
            print("1. 确保KOOK账号已登录（Cookie有效）")
            print("2. 启动账号监听")
            print("3. 在KOOK频道发送测试消息")
            print("4. 检查目标平台是否收到消息")
        else:
            print("\n⚠️  还有工作未完成，请完成以下准备:")
            
            if not requirements["KOOK账号"]:
                print("   ❌ 添加KOOK账号 (前端 → 账号管理)")
            
            if not requirements["有效Cookie"]:
                print("   ❌ 配置有效的Cookie (使用浏览器扩展导出)")
            
            if not requirements["Bot配置"]:
                print("   ❌ 配置目标Bot (前端 → Bot配置)")
                print("      支持: Discord, Telegram, 飞书, 钉钉, 企业微信")
            
            if not requirements["频道映射"]:
                print("   ❌ 配置频道映射 (前端 → 频道映射)")
        
        print("=" * 70)
        
        return requirements
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return requirements

if __name__ == "__main__":
    requirements = check_e2e_requirements()
    all_ready = all(requirements.values())
    sys.exit(0 if all_ready else 1)
