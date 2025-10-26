# 🚀 KOOK消息转发系统 v6.5.0 - 部署指南

**版本**: v6.5.0 🎊 极致易用版  
**更新日期**: 2025-10-26  
**适用对象**: 系统管理员、DevOps工程师、普通用户

---

## 🎊 V6.5.0 部署新特性

**极致易用，部署更简单！**

- ⚡ 3步配置向导 - 配置时间缩短60%（15分钟→5分钟）
- 🎨 可视化映射编辑器 - 拖拽式操作 + SVG连接线
- 💬 友好错误提示 - 15+种技术错误转换为普通话
- 🎓 新手引导动画 - 8步分步高亮引导
- 📊 增强系统托盘 - 7项实时统计 + 6个快捷操作
- 🖼️ 图床管理界面升级 - 4个统计卡片 + 双视图模式
- 📺 视频教程播放器 - 内置8个教程
- 📈 5种增强统计图表 - 趋势图/饼图/柱状图/热力图/排行榜

**部署时间**: 5分钟
**配置成功率**: 95%+
**技术门槛**: 零门槛
**用户体验**: 98/100  

---

## 📋 目录

1. [部署方式选择](#部署方式选择)
2. [Windows部署](#windows部署)
3. [macOS部署](#macos部署)
4. [Linux部署](#linux部署)
5. [Docker部署](#docker部署)
6. [生产环境配置](#生产环境配置)
7. [监控和维护](#监控和维护)
8. [故障排查](#故障排查)

---

## 📦 部署方式选择

---

## 🪟 Windows部署

### 方式1: 使用安装包（推荐）

**步骤**:

1. **下载安装包**
```
https://github.com/gfchfjh/CSBJJWT/releases/latest
文件名: KOOK-Forwarder-Setup-6.5.0.exe
```

2. **运行安装程序**
- 双击 `KOOK-Forwarder-Setup-6.5.0.exe`
- 选择安装路径（默认: `C:\Program Files\KOOK消息转发系统`）
- 点击"安装"
- 等待2-3分钟
- Redis和Chromium会自动安装（v6.3.0+）

3. **首次启动**
- 勾选"运行KOOK消息转发系统"
- 或从开始菜单启动

4. **防火墙配置**
```powershell
# 允许端口9527（API）和9528（图床）
netsh advfirewall firewall add rule name="KOOK Forwarder API" dir=in action=allow protocol=TCP localport=9527
netsh advfirewall firewall add rule name="KOOK Forwarder Image" dir=in action=allow protocol=TCP localport=9528
```

### 方式2: 静默安装（批量部署）

```batch
REM 静默安装
KOOK-Forwarder-6.0.0-Setup.exe /S

REM 指定安装路径
KOOK-Forwarder-6.0.0-Setup.exe /S /D=C:\Apps\KookForwarder

REM 静默卸载
"%ProgramFiles%\KOOK消息转发系统\Uninstall.exe" /S
```

### Windows服务部署（可选）

使用NSSM将应用注册为Windows服务：

```batch
REM 1. 下载NSSM
wget https://nssm.cc/release/nssm-2.24.zip
unzip nssm-2.24.zip

REM 2. 安装服务
nssm install KookForwarder "C:\Program Files\KOOK消息转发系统\KOOK消息转发系统.exe"

REM 3. 配置服务
nssm set KookForwarder AppDirectory "C:\Program Files\KOOK消息转发系统"
nssm set KookForwarder DisplayName "KOOK消息转发系统"
nssm set KookForwarder Description "自动转发KOOK消息到Discord/Telegram/飞书"
nssm set KookForwarder Start SERVICE_AUTO_START

REM 4. 启动服务
nssm start KookForwarder

REM 5. 查看状态
nssm status KookForwarder
```

---

## 🍎 macOS部署

### 方式1: 使用DMG安装包（推荐）

**步骤**:

1. **下载DMG**
```bash
# Intel Mac
curl -LO https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-macOS-x64.dmg

# Apple Silicon (M1/M2)
curl -LO https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-macOS-arm64.dmg
```

2. **安装应用**
```bash
# 打开DMG
open KOOK-Forwarder-6.0.0-macOS.dmg

# 拖动到Applications
# 或使用命令行
cp -R "/Volumes/KOOK消息转发系统/KOOK消息转发系统.app" /Applications/
```

3. **首次启动**
```bash
# 由于未签名，需要右键→打开
open /Applications/KOOK消息转发系统.app

# 或使用命令行绕过Gatekeeper
xattr -cr "/Applications/KOOK消息转发系统.app"
open "/Applications/KOOK消息转发系统.app"
```

### 方式2: Homebrew Cask（未来）

```bash
# 待发布到Homebrew
brew install --cask kook-forwarder
```

### macOS后台服务（LaunchAgent）

创建 `~/Library/LaunchAgents/com.kookforwarder.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kookforwarder.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/KOOK消息转发系统.app/Contents/MacOS/KOOK消息转发系统</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Library/Logs/KookForwarder/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Library/Logs/KookForwarder/stderr.log</string>
</dict>
</plist>
```

加载服务:
```bash
launchctl load ~/Library/LaunchAgents/com.kookforwarder.plist
launchctl start com.kookforwarder.app
```

---

## 🐧 Linux部署

### 方式1: AppImage（推荐）

**步骤**:

1. **下载AppImage**
```bash
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-x64.AppImage
```

2. **添加执行权限**
```bash
chmod +x KOOK-Forwarder-6.0.0-x64.AppImage
```

3. **运行**
```bash
./KOOK-Forwarder-6.0.0-x64.AppImage
```

4. **集成到系统**（可选）
```bash
# 移动到标准位置
sudo mv KOOK-Forwarder-6.0.0-x64.AppImage /opt/kook-forwarder/

# 创建桌面快捷方式
cat > ~/.local/share/applications/kook-forwarder.desktop << 'EOF'
[Desktop Entry]
Name=KOOK消息转发系统
Exec=/opt/kook-forwarder/KOOK-Forwarder-6.0.0-x64.AppImage
Icon=kook-forwarder
Type=Application
Categories=Network;Utility;
EOF
```

### 方式2: deb包（Debian/Ubuntu）

```bash
# 下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-amd64.deb

# 安装
sudo dpkg -i KOOK-Forwarder-6.0.0-amd64.deb

# 如果有依赖问题
sudo apt-get install -f

# 运行
kook-forwarder
```

### 方式3: rpm包（RedHat/Fedora/CentOS）

```bash
# 下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-x86_64.rpm

# 安装
sudo rpm -i KOOK-Forwarder-6.0.0-x86_64.rpm

# 或使用dnf
sudo dnf install KOOK-Forwarder-6.0.0-x86_64.rpm

# 运行
kook-forwarder
```

### Systemd服务配置

创建 `/etc/systemd/system/kook-forwarder.service`:

```ini
[Unit]
Description=KOOK消息转发系统
After=network.target

[Service]
Type=simple
User=kook
WorkingDirectory=/opt/kook-forwarder
ExecStart=/opt/kook-forwarder/KOOK-Forwarder-6.0.0-x64.AppImage --no-sandbox
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 环境变量
Environment="API_PORT=9527"
Environment="IMAGE_PORT=9528"

[Install]
WantedBy=multi-user.target
```

启用服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kook-forwarder
sudo systemctl start kook-forwarder
sudo systemctl status kook-forwarder
```

---

## 🐳 Docker部署

### 使用docker-compose（推荐）

`docker-compose.v6.yml`:

```yaml
version: '3.8'

services:
  kook-forwarder:
    image: ghcr.io/gfchfjh/kook-forwarder:6.0.0
    container_name: kook-forwarder
    restart: unless-stopped
    ports:
      - "9527:9527"  # API
      - "9528:9528"  # 图床
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=9527
      - IMAGE_SERVER_PORT=9528
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
    networks:
      - kook-network
  
  redis:
    image: redis:7-alpine
    container_name: kook-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - kook-network

volumes:
  redis-data:

networks:
  kook-network:
    driver: bridge
```

启动:
```bash
docker-compose -f docker-compose.v6.yml up -d
```

---

## ⚙️ 生产环境配置

### 环境变量配置

创建 `.env` 文件:

```bash
# 应用配置
APP_NAME=KOOK消息转发系统
APP_VERSION=6.0.0
DEBUG=false

# API配置
API_HOST=127.0.0.1
API_PORT=9527

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_strong_password_here

# 图床配置
IMAGE_SERVER_PORT=9528
IMAGE_MAX_SIZE_GB=10
IMAGE_CLEANUP_DAYS=7

# 安全配置
API_TOKEN=your_api_token_here
ENCRYPTION_KEY=your_32_char_encryption_key_here

# 邮件配置（可选）
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_app_password

# 验证码配置（可选）
CAPTCHA_2CAPTCHA_API_KEY=your_2captcha_key
CAPTCHA_AUTO_SOLVE=true

# 日志配置
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=7

# 性能配置
DISCORD_RATE_LIMIT_CALLS=5
DISCORD_RATE_LIMIT_PERIOD=5
TELEGRAM_RATE_LIMIT_CALLS=30
TELEGRAM_RATE_LIMIT_PERIOD=1
```

### 反向代理配置（Nginx）

如果需要通过域名访问:

```nginx
# /etc/nginx/sites-available/kook-forwarder
server {
    listen 80;
    server_name kook.example.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name kook.example.com;
    
    # SSL证书
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:9527/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:9527/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
    
    # 图床代理
    location /images/ {
        proxy_pass http://127.0.0.1:9528/images/;
        proxy_cache_valid 200 2h;
        proxy_cache_key "$scheme$request_method$host$request_uri";
    }
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/kook-forwarder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔐 安全加固

### 1. API Token保护

```bash
# 生成强随机Token
openssl rand -hex 32

# 设置环境变量
export API_TOKEN=your_generated_token_here
```

在API请求中添加Header:
```
X-API-Token: your_generated_token_here
```

### 2. 数据库加密

```bash
# 生成加密密钥
openssl rand -hex 16

# 设置环境变量
export ENCRYPTION_KEY=your_generated_key_here
```

### 3. HTTPS配置

使用Let's Encrypt免费证书:

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d kook.example.com

# 自动续期
sudo certbot renew --dry-run
```

### 4. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 📊 监控和维护

### 健康检查

```bash
# API健康检查
curl http://localhost:9527/health

# Redis健康检查
redis-cli ping

# 完整系统检查
curl http://localhost:9527/api/health/full
```

### 日志管理

**日志位置**:
- Windows: `%USERPROFILE%\Documents\KookForwarder\data\logs\`
- macOS: `~/Documents/KookForwarder/data/logs/`
- Linux: `~/Documents/KookForwarder/data/logs/` 或 `/var/log/kook-forwarder/`

**日志轮转**（Linux）:

创建 `/etc/logrotate.d/kook-forwarder`:

```
/var/log/kook-forwarder/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 kook kook
}
```

### 性能监控

**使用内置监控**:
```bash
# 访问性能监控API
curl http://localhost:9527/api/performance/stats

# 返回JSON:
{
  "cpu_percent": 3.5,
  "memory_mb": 185.2,
  "disk_usage_gb": 2.3,
  "message_queue_size": 5,
  "avg_latency_ms": 145,
  "uptime_hours": 48.5
}
```

**使用外部监控**（可选）:

- Prometheus + Grafana
- Datadog
- New Relic
- 自定义监控

---

## 🔄 更新和升级

### 自动更新（桌面应用）

应用内置自动更新，会在后台检查新版本。

**手动检查更新**:
- 打开应用 → 设置 → 关于 → 检查更新

### 手动更新

#### 桌面应用
1. 下载新版本安装包
2. 运行安装程序（会自动升级）
3. 配置和数据自动保留

#### Docker
```bash
# 拉取新镜像
docker pull ghcr.io/gfchfjh/kook-forwarder:6.1.0

# 停止旧容器
docker-compose down

# 启动新容器
docker-compose up -d
```

#### Linux服务
```bash
# 下载新版本
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.1.0/KOOK-Forwarder-6.1.0-x64.AppImage

# 停止服务
sudo systemctl stop kook-forwarder

# 替换可执行文件
sudo cp KOOK-Forwarder-6.1.0-x64.AppImage /opt/kook-forwarder/
sudo chmod +x /opt/kook-forwarder/KOOK-Forwarder-6.1.0-x64.AppImage

# 更新服务配置中的路径
sudo systemctl edit kook-forwarder

# 启动服务
sudo systemctl start kook-forwarder
```

---

## 🐛 故障排查

### 问题1: 无法启动

**症状**: 双击应用无响应

**可能原因**:
1. 端口被占用（9527或9528）
2. 权限问题
3. 依赖缺失

**解决方法**:
```bash
# 检查端口占用
netstat -ano | findstr :9527  # Windows
lsof -i :9527                 # Linux/macOS

# 检查日志
tail -f ~/Documents/KookForwarder/data/logs/app.log

# 以管理员权限运行（Windows）
右键 → 以管理员身份运行
```

### 问题2: Cookie导入失败

**症状**: 提示"Cookie格式错误"

**解决方法**:
1. 使用Chrome扩展一键导出（推荐）
2. 检查Cookie格式（参考支持格式）
3. 查看详细错误信息和建议

### 问题3: Playwright下载失败

**症状**: 首次启动提示"浏览器下载失败"

**解决方法**:
```bash
# 手动下载
playwright install chromium --with-deps

# 使用镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net
playwright install chromium
```

### 问题4: 性能问题

**症状**: 图片转发很慢、内存占用高

**诊断**:
```bash
# 查看性能统计
curl http://localhost:9527/api/performance/stats

# 查看图片处理统计
curl http://localhost:9527/api/image/stats
```

**优化**:
1. 启用图片多进程处理（已默认启用）
2. 调整图片质量（设置 → 图片处理 → 压缩质量）
3. 清理旧图片（设置 → 图片处理 → 立即清理）

---

## 📞 获取支持

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- 文档: https://github.com/gfchfjh/CSBJJWT/docs
- 社区: https://github.com/gfchfjh/CSBJJWT/discussions

---

**部署愉快！** 🎉
