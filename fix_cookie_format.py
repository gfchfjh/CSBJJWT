"""
修复Cookie格式问题
直接修改本地backend/app/kook/scraper.py文件
"""

file_path = r'backend\app\kook\scraper.py'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经修复
if 'Cookie格式已修复' in content:
    print('✅ Cookie格式已经修复过了，无需再次修复')
    exit(0)

# 查找需要替换的代码块
old_code = """                logger.info(f"[Scraper-{self.account_id}] Cookie解密成功")
                # 修复sameSite字段
                for cookie in cookie_data:
                    if cookie.get("sameSite") in ["no_restriction", "unspecified"]:
                        cookie["sameSite"] = "None"
                    if cookie.get("sameSite") == "None":
                        cookie["secure"] = True
                logger.info(f"[Scraper-{self.account_id}] Cookie已修复sameSite字段")
                
                # 创建上下文并添加Cookie
                context = browser.new_context()
                context.add_cookies(cookie_data)"""

new_code = """                logger.info(f"[Scraper-{self.account_id}] Cookie解密成功")
                # 修复Cookie格式
                for cookie in cookie_data:
                    # 修复sameSite字段
                    if cookie.get("sameSite") in ["no_restriction", "unspecified"]:
                        cookie["sameSite"] = "None"
                    if cookie.get("sameSite") == "None":
                        cookie["secure"] = True
                    
                    # ✅ 修复：确保Cookie有domain字段（Playwright要求）
                    if "domain" not in cookie or not cookie["domain"]:
                        cookie["domain"] = ".kookapp.cn"
                    
                    # ✅ 修复：确保Cookie有path字段（Playwright要求）
                    if "path" not in cookie or not cookie["path"]:
                        cookie["path"] = "/"
                    
                    # ✅ 修复：移除不支持的字段
                    cookie.pop("sameSite", None) if cookie.get("sameSite") not in ["Strict", "Lax", "None"] else None
                    
                logger.info(f"[Scraper-{self.account_id}] Cookie格式已修复")
                
                # 创建上下文并添加Cookie
                context = browser.new_context()
                context.add_cookies(cookie_data)"""

# 替换代码
if old_code in content:
    content = content.replace(old_code, new_code)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ Cookie格式修复成功！')
    print('✅ 文件已更新: backend/app/kook/scraper.py')
    print('')
    print('接下来：')
    print('1. 重启后端服务（Ctrl+C 然后重新运行 uvicorn）')
    print('2. 刷新浏览器页面')
    print('3. 点击"启动"按钮测试')
else:
    print('❌ 未找到需要替换的代码块')
    print('可能文件已被修改或版本不匹配')
    print('')
    print('请手动检查文件: backend/app/kook/scraper.py')
    print('查找第888行附近的Cookie处理代码')
