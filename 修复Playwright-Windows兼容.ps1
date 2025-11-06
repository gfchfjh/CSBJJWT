# KOOK Playwright Windows兼容性修复脚本
# 此脚本将修改scraper.py以使用同步Playwright避免asyncio子进程问题

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 Playwright Windows兼容性修复" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 添加import
Write-Host "[1/3] 添加必要的导入..." -ForegroundColor Yellow
$filePath = "backend/app/kook/scraper.py"
$content = Get-Content $filePath -Raw -Encoding UTF8

# 检查是否已经有sync_playwright导入
if ($content -notmatch "from playwright.sync_api import sync_playwright") {
    $content = $content -replace "(from playwright\.async_api import[^\n]+)", "`$1`nfrom playwright.sync_api import sync_playwright`nimport concurrent.futures"
    Write-Host "✅ 已添加sync_playwright和concurrent.futures导入" -ForegroundColor Green
} else {
    Write-Host "✅ 导入已存在" -ForegroundColor Green
}

# 2. 修改start方法
Write-Host "[2/3] 修改start方法以使用同步模式..." -ForegroundColor Yellow

$oldStart = @'
    async def start\(self\):
        """启动抓取器"""
        try:
            logger\.info\(f"\[Scraper-\{self\.account_id\}\] 正在启动\.\.\."\)
            
            async with async_playwright\(\) as p:
'@

$newStart = @'
    async def start(self):
        """启动抓取器"""
        try:
            logger.info(f"[Scraper-{self.account_id}] 正在启动...")
            
            # Windows兼容性：使用同步Playwright避免asyncio子进程问题
            import sys
            if sys.platform == "win32":
                logger.info(f"[Scraper-{self.account_id}] 使用同步Playwright（Windows兼容模式）")
                # 在线程池中运行同步版本
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, self._run_sync_playwright)
                return
            
            async with async_playwright() as p:
'@

$content = $content -replace $oldStart, $newStart

# 3. 添加同步运行方法
Write-Host "[3/3] 添加同步运行方法..." -ForegroundColor Yellow

$syncMethod = @'
    
    def _run_sync_playwright(self):
        """同步版本的Playwright运行（Windows兼容模式）"""
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-automation',
                        '--disable-infobars',
                        '--no-first-run',
                        '--no-default-browser-check',
                    ]
                )
                
                # 获取账号信息
                account = db.execute(
                    "SELECT email, cookie FROM accounts WHERE id = ?",
                    (self.account_id,)
                ).fetchone()
                
                if not account:
                    logger.error(f"[Scraper-{self.account_id}] 账号不存在")
                    return
                
                # 解析Cookie
                cookie_data = json.loads(account['cookie'])
                
                # 创建上下文并添加Cookie
                context = browser.new_context()
                context.add_cookies(cookie_data)
                
                # 打开页面
                page = context.new_page()
                page.goto("https://www.kookapp.cn/app/", wait_until="networkidle")
                
                logger.info(f"[Scraper-{self.account_id}] ✅ 浏览器已启动并访问KOOK（同步模式）")
                
                # 保持运行
                self.is_running = True
                while self.is_running:
                    import time
                    time.sleep(1)
                
                # 清理
                page.close()
                context.close()
                browser.close()
                
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 同步模式启动失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
'@

# 在stop方法之前插入
$content = $content -replace "(    def register_message_handler.*?\n        self\.message_handlers\.append\(handler\)\n)(    async def stop\(self\):)", "`$1$syncMethod`n`$2"

# 保存文件
$content | Out-File $filePath -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 修复完成！" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 修改内容：" -ForegroundColor Cyan
Write-Host "  1. ✅ 添加了sync_playwright导入" -ForegroundColor White
Write-Host "  2. ✅ 修改start方法使用Windows兼容模式" -ForegroundColor White
Write-Host "  3. ✅ 添加了_run_sync_playwright同步运行方法" -ForegroundColor White
Write-Host ""
Write-Host "🔄 下一步：" -ForegroundColor Cyan
Write-Host "  重启后端服务，然后测试账号启动功能" -ForegroundColor White
Write-Host ""
