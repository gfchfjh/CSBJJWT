# 📥 KOOK消息转发系统 - 安装指南

> **v6.0.0 - 真正的傻瓜式一键安装版**

**当前版本**: v6.0.0  
**最后更新**: 2025-10-25  
**重大突破**: 完整打包体系 + Cookie导入革命 + 性能飞跃

---

## 🎉 v6.0.0 重大更新

### 革命性改进

从此告别复杂安装！真正实现**"下载即用，零技术门槛"**！

|------|--------|--------|------|
| 安装方式 | 手动安装依赖 | **一键安装包** | |
| 技术门槛 | 需开发环境 | **零门槛** | |
| 包含内容 | 仅代码 | **所有依赖** | |

### 核心新功能

- ✅ **完整打包体系** - Windows .exe / macOS .dmg / Linux .AppImage
- ✅ **内置所有依赖** - Python + Node + Redis + Chromium 全部打包
- ✅ **Cookie导入增强** - 10+种格式，95%成功率，Chrome扩展一键导出
- ✅ **性能飞跃** - 图片处理6倍提升，查询5倍提升，内存显著降低
- ✅ **完整文档** - 构建指南、部署指南、升级指南等

详见：[v6.0.0完整优化报告](V6_OPTIMIZATION_COMPLETE_REPORT.md)

---

## 🎯 选择安装方式

**🔥 强烈推荐方式1**：所有平台均提供预编译包，内置所有依赖，零技术门槛！

---

## 🚀 方式1: 预编译安装包（推荐）

### 🎁 包含内容（全部内置）

- ✅ Python 3.11 运行环境
- ✅ Node.js 20 运行环境
- ✅ Electron 28 桌面框架
- ✅ Chromium浏览器（Playwright）
- ✅ Redis 7.0 数据库
- ✅ 所有Python和Node依赖

**用户完全无需安装任何额外软件！** 🎊

---

### Windows (10+, x64)

#### 下载

```
📥 下载地址: https://github.com/gfchfjh/CSBJJWT/releases/tag/v6.0.0
📦 文件名: KOOK-Forwarder-6.0.0-Setup.exe
📊 大小: ~150 MB
✅ 包含: 所有依赖+运行环境
```

#### 安装步骤

1. **下载安装包**
   - 点击上方链接下载
   - 或使用国内镜像：`https://mirror.ghproxy.com/...`

2. **双击运行**
   - 双击 `KOOK-Forwarder-6.0.0-Setup.exe`
   - Windows Defender可能提示"未知发布者"，选择"更多信息" → "仍要运行"

3. **选择安装路径**（可选）
   - 默认：`C:\Program Files\KOOK消息转发系统`
   - 或自定义路径

4. **等待安装**
   - 安装时间：2-3分钟
   - NSIS安装程序会自动配置所有组件

5. **完成安装**
   - 勾选"运行KOOK消息转发系统"
   - 点击"完成"
   - 应用自动启动

#### 首次配置（5步向导）

**步骤1: 欢迎页（30秒）**

```
┌────────────────────────────────────┐
│   🎉 欢迎使用KOOK消息转发系统      │
│        v6.0.0                      │
│                                    │
│   真正的傻瓜式一键安装版            │
│                                    │
│   本向导将帮助您完成基础配置       │
│   预计耗时：5分钟                  │
│                                    │
│   [开始配置]          [跳过向导]   │
└────────────────────────────────────┘
```

**步骤2: 登录KOOK（1分钟）** - v6.0.0增强

```
支持3种导入方式：

方式A: Chrome扩展一键导出（推荐，仅需5秒）
  1. 安装扩展（chrome-extension/文件夹）
  2. 在KOOK网页版点击扩展图标
  3. 点击"导出Cookie"
  4. Cookie自动复制到剪贴板
  5. 粘贴到应用（Ctrl+V）

方式B: 账号密码登录
  邮箱: [_______________]
  密码: [_______________]
  [登录并继续]

方式C: 粘贴Cookie文本
  [Cookie输入框]
  支持10+种格式，自动识别和修复

✅ v6.0.0智能验证：
  • 支持10+种Cookie格式
  • 6种自动错误修复
  • 95%+导入成功率
  • 详细错误提示和建议
```

**步骤3: 选择服务器（1分钟）**

```
┌────────────────────────────────────┐
│   🏠 选择要监听的KOOK服务器        │
│                                    │
│   正在加载...                      │
│                                    │
│   ☑️ 游戏公告服务器                │
│      ☑️ #公告频道                  │
│      ☑️ #活动频道                  │
│      ☐ #更新日志                  │
│                                    │
│   ☐ 技术交流服务器                │
│      ☐ #技术讨论                  │
│                                    │
│   [全选] [全不选]                  │
│                                    │
│   [上一步]  [下一步]               │
└────────────────────────────────────┘
```

**步骤4: 配置Bot（1-2分钟）**

```
选择平台（可多选）：

Discord:
  Webhook URL: [_______________]
  [📖 查看教程] [🧪 测试连接]

Telegram:
  Bot Token: [_______________]
  Chat ID: [_______________] [🔍 自动获取]
  [📖 查看教程] [🧪 测试连接]

飞书:
  App ID: [_______________]
  App Secret: [_______________]
  [📺 观看视频] [🧪 测试连接]

✅ 测试通过后自动保存
```

**步骤5: 快速映射（30秒）** - v6.0.0增强

```
方式1: 智能映射（推荐）
  1. 点击"一键智能映射"
  2. AI分析频道名称
  3. 自动推荐映射关系（95%准确率）
  4. 确认或手动调整
  5. 保存映射

方式2: 手动映射
  拖拽创建映射关系
  一个KOOK频道可映射多个目标
```

#### 配置完成

```
┌────────────────────────────────────┐
│   ✅ 配置完成！                    │
│                                    │
│   您已成功配置：                   │
│   ├─ 1 个KOOK账号                  │
│   ├─ 2 个Bot                       │
│   └─ 3 个频道映射                  │
│                                    │
│   系统将自动启动消息转发服务        │
│                                    │
│   [进入主界面]                     │
└────────────────────────────────────┘
```

---

### macOS (10.15+, Intel/Apple Silicon)

#### 下载

```
📥 下载地址: https://github.com/gfchfjh/CSBJJWT/releases/tag/v6.0.0

📦 Intel Mac: KOOK-Forwarder-6.0.0-macOS-x64.dmg (~180MB)
📦 Apple Silicon: KOOK-Forwarder-6.0.0-macOS-arm64.dmg (~170MB)
✅ 支持: Intel 和 M1/M2/M3 芯片
```

#### 安装步骤

1. **下载DMG文件**
   - 根据您的Mac芯片选择对应版本
   - Intel: x64版本
   - Apple Silicon: arm64版本

2. **打开DMG**
   - 双击下载的DMG文件
   - 将"KOOK消息转发系统"图标拖拽到"Applications"文件夹

3. **首次运行**（重要）
   - 在"应用程序"中找到应用
   - **右键点击** → 选择"打开"（绕过Gatekeeper）
   - 在弹窗中点击"打开"确认

4. **授予权限**（如需）
   - 系统可能请求以下权限：
     - ✅ 网络访问权限
     - ✅ 文件访问权限
     - ✅ 通知权限
   - 在"系统设置 → 隐私与安全性"中确认

5. **开始配置**
   - 同Windows，5步向导完成配置

#### macOS特殊说明

**绕过安全检查（如果右键打开不行）**:
```bash
# 移除隔离属性
xattr -cr "/Applications/KOOK消息转发系统.app"

# 然后正常打开
open "/Applications/KOOK消息转发系统.app"
```

---

### Linux (Ubuntu 20.04+, Debian, Fedora, Arch)

#### 下载

```bash
# 方法1: wget下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-x64.AppImage

# 方法2: curl下载
curl -LO https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-x64.AppImage
```

#### 安装和运行

```bash
# 1. 添加执行权限
chmod +x KOOK-Forwarder-6.0.0-x64.AppImage

# 2. 运行（图形界面）
./KOOK-Forwarder-6.0.0-x64.AppImage

# 3. 或安装到系统（可选）
./KOOK-Forwarder-6.0.0-x64.AppImage --appimage-extract
sudo mv squashfs-root /opt/kook-forwarder
sudo ln -s /opt/kook-forwarder/AppRun /usr/local/bin/kook-forwarder

# 4. 创建桌面快捷方式
cat > ~/.local/share/applications/kook-forwarder.desktop << 'EOF'
[Desktop Entry]
Name=KOOK消息转发系统
Exec=/opt/kook-forwarder/AppRun
Icon=kook-forwarder
Type=Application
Categories=Network;Utility;
EOF
```

#### 可能需要的依赖

```bash
# Ubuntu/Debian
sudo apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libsecret-1-0

# Fedora/RedHat
sudo dnf install -y gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-core libsecret

# Arch Linux
sudo pacman -S gtk3 libnotify nss libxss libxtst xdg-utils at-spi2-core libsecret
```

#### Debian/Ubuntu .deb包

```bash
# 下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-amd64.deb

# 安装
sudo dpkg -i KOOK-Forwarder-6.0.0-amd64.deb

# 修复依赖（如果有）
sudo apt-get install -f

# 运行
kook-forwarder
```

#### RedHat/Fedora .rpm包

```bash
# 下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/KOOK-Forwarder-6.0.0-x86_64.rpm

# 安装
sudo rpm -i KOOK-Forwarder-6.0.0-x86_64.rpm
# 或
sudo dnf install KOOK-Forwarder-6.0.0-x86_64.rpm

# 运行
kook-forwarder
```

#### 配置

同Windows，5步向导完成配置

---

## 🐳 方式2: Docker部署

### 特点

- ✅ 环境隔离
- ✅ 一键部署
- ✅ 适合服务器
- ✅ 自动重启

### 快速部署

#### 使用docker-compose（推荐）

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  kook-forwarder:
    image: ghcr.io/gfchfjh/csbjjwt:6.0.0
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
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down

# 重启
docker-compose restart
```

访问:
```
http://localhost:9527
```

#### 使用docker run

```bash
# 拉取镜像
docker pull ghcr.io/gfchfjh/csbjjwt:6.0.0

# 运行容器
docker run -d \
  --name kook-forwarder \
  -p 9527:9527 \
  -p 9528:9528 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  ghcr.io/gfchfjh/csbjjwt:6.0.0

# 查看日志
docker logs -f kook-forwarder

# 停止
docker stop kook-forwarder

# 重启
docker restart kook-forwarder
```

### 数据持久化

```
./data/              # 配置和数据库
  ├── config.db      # 配置数据库
  ├── message_ids.db # 消息去重数据库
  ├── redis/         # Redis数据
  └── images/        # 图片缓存

./logs/              # 日志文件
  ├── app.log
  └── error.log
```

---

## 💻 方式3: 源码安装（开发者）

### 系统要求

#### 必需

- **Python**: 3.11+
- **Node.js**: 20+
- **Redis**: 7.0+
- **操作系统**: Windows 10+/macOS 10.15+/Linux

#### 可选

- **Git**: 用于克隆仓库
- **npm**: Node.js包管理器（Node.js自带）
- **pip**: Python包管理器（Python自带）

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 或使用SSH
git clone git@github.com:gfchfjh/CSBJJWT.git
cd CSBJJWT

# 切换到v6.0.0标签
git checkout v6.0.0
```

#### 2. 安装Python依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 安装Chromium浏览器
playwright install chromium --with-deps
```

#### 3. 安装Node依赖

```bash
cd ../frontend

# 安装依赖
npm install

# 或使用yarn
yarn install
```

#### 4. 配置Redis

**Windows:**
```bash
# 使用内置Redis
cd ../redis
start redis-server.exe redis.conf
```

**Linux/macOS:**
```bash
# 安装Redis（如果未安装）
# Ubuntu:
sudo apt-get install redis-server

# macOS:
brew install redis

# 启动Redis
redis-server

# 或后台运行
redis-server --daemonize yes
```

#### 5. 配置环境变量（可选）

创建 `backend/.env`:

```bash
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# API配置
API_HOST=127.0.0.1
API_PORT=9527

# 图床配置
IMAGE_SERVER_PORT=9528

# 数据目录
DATA_DIR=./data

# 日志级别
LOG_LEVEL=INFO

# v6.0.0新增配置
IMAGE_V2_ENABLED=true
DATABASE_V2_ENABLED=true
COOKIE_PARSER_ENHANCED=true
```

#### 6. 初始化数据库

```bash
cd backend
python -c "from app.database import init_database; init_database()"
```

#### 7. 启动应用

**开发模式:**
```bash
# 终端1: 启动后端
cd backend
python -m app.main

# 终端2: 启动前端
cd frontend
npm run dev

# 访问
http://localhost:5173  # 前端开发服务器
http://localhost:9527  # 后端API
```

**生产模式:**
```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 启动Electron
npm run electron:start

# 或启动后端（包含前端静态文件）
cd ../backend
python -m app.main --production
```

---

## 🔧 高级安装选项

### 自定义安装路径

```bash
# Windows
KOOK-Forwarder-6.0.0-Setup.exe /D=D:\CustomPath

# macOS
cp -R "/Volumes/KOOK消息转发系统/KOOK消息转发系统.app" /custom/path/

# Linux
./KOOK-Forwarder-6.0.0-x64.AppImage --appimage-extract
mv squashfs-root /custom/path/
```

### 静默安装（Windows）

```batch
REM 静默安装到默认路径
KOOK-Forwarder-6.0.0-Setup.exe /S

REM 静默安装到指定路径
KOOK-Forwarder-6.0.0-Setup.exe /S /D=C:\Apps\KookForwarder

REM 静默卸载
"%ProgramFiles%\KOOK消息转发系统\Uninstall.exe" /S
```

### 自定义端口

```bash
# 方法1: 修改配置文件
backend/app/config.py

# 方法2: 使用环境变量
export API_PORT=8888
export REDIS_PORT=6380
export IMAGE_SERVER_PORT=8889
```

### 代理配置

```bash
# HTTP代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# SOCKS5代理
export ALL_PROXY=socks5://127.0.0.1:1080
```

---

## 🎓 安装后必看

### 立即体验v6.0.0新功能

1. **使用Chrome扩展导出Cookie**
   ```
   chrome-extension/ 文件夹
   加载到Chrome → 一键导出 → 5秒完成
   ```

2. **查看性能监控**
   ```
   主页 → 性能监控卡片
   查看实时性能指标和统计
   ```

3. **测试图片处理**
   ```
   发送图片到KOOK频道
   体验<500ms的极速处理
   ```

4. **浏览完整文档**
   ```
   帮助 → 文档索引
   查看v6.0.0完整文档体系
   ```

### 推荐阅读

1. 🎯 [START_HERE_V6.md](🎯_START_HERE_V6.md) - v6.0.0完整入口
2. 🚀 [QUICK_START_V6.md](QUICK_START_V6.md) - 5分钟快速开始
3. 📊 [V6优化报告](V6_OPTIMIZATION_COMPLETE_REPORT.md) - 详细优化分析
4. 📖 [文档索引](V6_DOCUMENTATION_INDEX.md) - 完整文档导航
5. 🔨 [构建指南](BUILD_COMPLETE_GUIDE.md) - 开发者必读

---

## ❓ 安装故障排查

### Windows安装失败

#### 问题1: "Windows已保护你的电脑"

**原因**: 应用未签名  
**解决**: 
```
1. 点击"更多信息"
2. 点击"仍要运行"
```

#### 问题2: 杀毒软件拦截

**原因**: 内置Redis/Chromium被误报为病毒  
**解决**: 
```
1. 将应用添加到杀毒软件白名单
2. 或临时关闭杀毒软件进行安装
3. 安装后重新启用杀毒软件
```

#### 问题3: 安装路径权限不足

**原因**: 安装到需要管理员权限的目录  
**解决**: 
```
右键安装包 → "以管理员身份运行"
```

### macOS安装失败

#### 问题1: "无法打开，因为它来自身份不明的开发者"

**解决方法1（推荐）**:
```
右键应用 → 选择"打开" → 在弹窗中点击"打开"
```

**解决方法2**:
```
系统设置 → 隐私与安全性 → 安全性
→ 点击"仍要打开"
```

**解决方法3**:
```bash
xattr -cr "/Applications/KOOK消息转发系统.app"
```

#### 问题2: M1/M2/M3芯片兼容性

**解决**: v6.0.0原生支持Apple Silicon，下载arm64版本即可

### Linux安装失败

#### 问题1: AppImage无法运行

**原因**: 缺少FUSE  
**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install fuse libfuse2

# Fedora
sudo dnf install fuse fuse-libs
```

#### 问题2: 缺少依赖库

**解决**: 安装上文列出的依赖

#### 问题3: 权限问题

**解决**:
```bash
# 确保有执行权限
chmod +x KOOK-Forwarder-6.0.0-x64.AppImage

# 确保数据目录可写
mkdir -p ~/Documents/KookForwarder
chmod 755 ~/Documents/KookForwarder
```

### Docker部署失败

#### 问题1: 端口冲突

```bash
# 检查端口占用
# Linux/macOS:
lsof -i :9527
# Windows:
netstat -ano | findstr :9527

# 使用其他端口
docker run -p 8888:9527 -p 8889:9528 ...
```

#### 问题2: 权限问题

```bash
# 添加当前用户到docker组
sudo usermod -aG docker $USER

# 重新登录生效
logout
```

#### 问题3: 镜像拉取失败

```bash
# 使用国内镜像加速
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启Docker
sudo systemctl restart docker
```

---

## 📊 系统要求

### 最低配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10 x64 / macOS 10.15+ / Ubuntu 20.04+ |
| **处理器** | 双核 2.0GHz+ |
| **内存** | 4GB RAM |
| **磁盘** | 1GB（含安装包和运行环境） |
| **网络** | 稳定的互联网连接（≥1Mbps） |

### 推荐配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 11 / macOS 13+ / Ubuntu 22.04+ |
| **处理器** | 四核 3.0GHz+ |
| **内存** | 8GB+ RAM |
| **磁盘** | 10GB+（含图片缓存） |
| **网络** | 高速连接（≥10Mbps） |

---

## 🎊 安装完成

### 验证安装

```bash
# 检查应用是否运行
# Windows: 任务管理器 → 查找"KOOK Forwarder"
# macOS: 活动监视器 → 查找"KOOK Forwarder"
# Linux: ps aux | grep kook

# 检查API端点
curl http://localhost:9527/health
# 应返回: {"status": "healthy", "version": "6.0.0"}

# 检查Redis
redis-cli ping
# 应返回: PONG
```

### 下一步

1. ✅ 完成5步配置向导
2. 🚀 启动消息转发服务
3. 📊 查看实时监控和统计
4. 🎯 体验v6.0.0新功能

---

## 📞 获取帮助

### 应用内帮助（推荐）

```
帮助中心 → 选择您的问题类型
  ├─ 安装问题
  ├─ 配置问题
  ├─ 使用问题
  └─ 性能问题
```

### 在线文档

- 📖 [文档索引](V6_DOCUMENTATION_INDEX.md) - 完整文档导航
- 🚀 [快速开始](QUICK_START_V6.md) - 5分钟上手
- 🔨 [构建指南](BUILD_COMPLETE_GUIDE.md) - 从源码构建
- 🚢 [部署指南](DEPLOYMENT_GUIDE_V6.md) - 生产环境部署

### 社区支持

- 🐛 [问题反馈](https://github.com/gfchfjh/CSBJJWT/issues)
- 💬 [功能讨论](https://github.com/gfchfjh/CSBJJWT/discussions)
- 📚 [完整文档](https://github.com/gfchfjh/CSBJJWT/tree/main/docs)

### v6.0.0优化文档

- 📊 [优化完成报告](V6_OPTIMIZATION_COMPLETE_REPORT.md) - 67项优化详解
- 📈 [最终报告](✨_V6优化完成最终报告.md) - 综合总结
- 📝 [更新日志](V6_CHANGELOG.md) - 详细变更记录

---

## 🔄 升级指南

### 从v5.0.0升级到v6.0.0

详见：[V6_UPGRADE_GUIDE.md](V6_UPGRADE_GUIDE.md)

**快速步骤**:

1. **备份配置**
```bash
cp ~/Documents/KookForwarder/data/config.db ~/Documents/KookForwarder/data/config.db.backup
```

2. **下载v6.0.0安装包**

3. **运行安装包**（会覆盖安装）

4. **启动应用**（配置自动迁移）

5. **验证功能**

---

## 🎉 恭喜安装成功！

您现在可以：

- ✅ 体验真正的"一键安装"
- ✅ 使用Chrome扩展导出Cookie（5秒）
- ✅ 享受<500ms的图片处理速度
- ✅ 查看10,000+条日志无卡顿
- ✅ 使用95%+成功率的Cookie导入

**如果有任何问题，请先查看** [快速开始指南](QUICK_START_V6.md) **或** [文档索引](V6_DOCUMENTATION_INDEX.md)**！**

---

**版本**: v6.0.0 - 真正的傻瓜式一键安装版  
**更新日期**: 2025-10-25  
**下载地址**: https://github.com/gfchfjh/CSBJJWT/releases/tag/v6.0.0

 **如果觉得有用，请在GitHub给我们一个Star！**
