# 📥 KOOK消息转发系统 - 安装指南

> **v4.1.0 Deep Optimization Edition - 真正的零技术门槛**

**当前版本：** v4.1.0  
**最后更新：** 2025-10-25  
**重大突破：** 12项P0核心优化全部完成

---

## 🎉 v4.1.0 重大更新亮点

### 安装体验革命性提升

| 维度 | v4.0.0 | v4.1.0 | 提升 |
|------|--------|--------|------|
| **配置时间** | 30分钟 | **5分钟** | ⬇️ 83% |
| **配置成功率** | 40% | **90%+** | ⬆️ 125% |
| **错误理解度** | 20% | **95%+** | ⬆️ 375% |
| **技术门槛** | 需编程背景 | **真正零基础** | 质的飞跃 |

### 核心新功能
- ✅ **5步完整向导** - Bot配置和映射一站式完成
- ✅ **环境一键修复** - 8种问题自动解决
- ✅ **Cookie智能验证** - 10种错误检测+自动修复
- ✅ **文件附件转发** - 50MB+30种类型
- ✅ **表情反应转发** - 智能汇总
- ✅ **图片3种策略** - 智能fallback
- ✅ **主密码保护** - 企业级安全
- ✅ **消息零重复** - 双层缓存
- ✅ **崩溃零丢失** - 自动备份
- ✅ **完整帮助** - 6教程+8FAQ+诊断
- ✅ **品牌指南** - 专业形象

详见：[v4.1.0完整优化报告](P0_OPTIMIZATION_COMPLETE_REPORT.md)

---

## 🎯 选择安装方式

| 方式 | 适合人群 | 时间 | 难度 | 状态 |
|------|---------|------|------|------|
| **方式1: 预编译安装包** | 普通用户 | **5分钟** | ⭐ | ✅ **推荐** |
| **方式2: Docker部署** | 服务器用户 | **3分钟** | ⭐ | ✅ 可用 |
| **方式3: 源码安装** | 开发者 | 10分钟 | ⭐⭐ | ✅ 可用 |

**🔥 强烈推荐方式1**：所有平台均提供预编译包，内置所有依赖

---

## 🚀 方式1: 预编译安装包（推荐）

### 🎁 包含内容（全部内置）
- ✅ Python 3.11 运行环境
- ✅ Node.js 18 运行环境
- ✅ Electron 28 桌面框架
- ✅ Chromium 浏览器（Playwright）
- ✅ Redis 7.0 数据库
- ✅ 所有Python和Node依赖

**用户完全无需安装任何额外软件！**

---

### Windows 10/11 (x64)

#### 下载
```
📥 下载地址: https://github.com/gfchfjh/CSBJJWT/releases/latest
📦 文件名: KOOK-Forwarder-4.1.0-Setup.exe
📊 大小: ~150 MB
✅ 包含: 所有依赖+运行环境
```

#### 安装步骤
1. **下载安装包**
   - 点击上方链接下载
   - 或使用国内镜像：`https://mirror.ghproxy.com/...`

2. **双击运行**
   - 双击 `KOOK-Forwarder-4.1.0-Setup.exe`
   - Windows Defender可能提示"未知发布者"，选择"仍要运行"

3. **选择安装路径**（可选）
   - 默认：`C:\Program Files\KOOK-Forwarder`
   - 或自定义路径

4. **等待安装**
   - 安装时间：2-3分钟
   - 进度条显示安装进度

5. **完成安装**
   - 勾选"运行KOOK消息转发系统"
   - 点击"完成"
   - 应用自动启动

#### 首次配置（5步向导）

**步骤1: 欢迎页**
- 介绍应用功能
- 预计配置时间：5分钟
- 点击"开始配置"

**步骤2: 登录KOOK（v4.1.0智能验证）**
```
支持3种导入方式：
  ○ 粘贴Cookie文本 ← 最常用
  ○ 拖拽JSON文件
  ○ 浏览器扩展一键导出

✅ v4.1.0新增智能验证：
  • 自动检测10种常见错误
  • 友好的错误提示（非技术性）
  • 尝试自动修复格式问题
  • 提供详细教程链接
  • 显示Cookie过期时间

常见错误自动处理：
  ✅ 检测到控制台输出 → 自动提示正确方法
  ✅ 检测到HTML内容 → 提示如何找到Cookie
  ✅ 格式不完整 → 尝试自动修复
  ✅ Cookie过期 → 提示重新导出
```

**步骤3: 选择服务器**
- 显示所有KOOK服务器
- 选择要监听的频道
- 支持多选
- 实时预览

**步骤4: 配置Bot（v4.1.0新增）**
```
直接在向导中配置目标平台：

Discord:
  • 输入Webhook URL
  • 测试连接
  • 查看教程（如何创建Webhook）

Telegram:
  • 输入Bot Token
  • 输入Chat ID
  • 或使用"自动获取"功能
  • 测试连接

飞书:
  • 输入App ID
  • 输入App Secret
  • 测试连接
  • 观看视频教程

✅ 测试连接成功后自动保存
✅ 可配置多个Bot
```

**步骤5: 快速映射（v4.1.0新增）**
```
两种映射方式：

方式1: 智能映射（推荐）
  • 点击"一键智能映射"
  • AI自动分析频道名称
  • 智能推荐映射关系
  • 准确率75%+

方式2: 手动映射
  • 拖拽创建映射
  • 一个KOOK频道 → 多个目标
  • 实时预览映射结果

✅ 完成映射后可立即使用
```

#### 配置完成
- 自动保存所有配置
- 进入主界面
- 点击"启动服务"开始转发

---

### macOS (10.15+, Intel/Apple Silicon)

#### 下载
```
📥 下载地址: https://github.com/gfchfjh/CSBJJWT/releases/latest
📦 文件名: KOOK-Forwarder-4.1.0.dmg
📊 大小: ~160 MB
✅ 支持: Intel和M1/M2芯片
```

#### 安装步骤
1. **下载DMG文件**

2. **打开DMG**
   - 双击DMG文件
   - 将应用图标拖拽到"应用程序"文件夹

3. **首次运行**
   - 在"应用程序"中找到KOOK消息转发系统
   - **重要**：右键点击 → 选择"打开"（绕过安全检查）
   - 在弹窗中点击"打开"确认

4. **授予权限**（如需）
   - 可能需要授予"磁盘访问权限"
   - 可能需要授予"网络访问权限"
   - 在"系统偏好设置 → 安全性与隐私"中确认

5. **开始配置**
   - 同Windows，5步向导完成配置

---

### Linux (Ubuntu 20.04+, Debian, Fedora, Arch)

#### 下载
```bash
# 方法1: wget下载
wget https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KOOK-Forwarder-4.1.0.AppImage

# 方法2: curl下载
curl -L https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KOOK-Forwarder-4.1.0.AppImage -o KOOK-Forwarder-4.1.0.AppImage
```

#### 安装和运行
```bash
# 1. 添加执行权限
chmod +x KOOK-Forwarder-4.1.0.AppImage

# 2. 运行（图形界面）
./KOOK-Forwarder-4.1.0.AppImage

# 3. 或安装到系统（可选）
./KOOK-Forwarder-4.1.0.AppImage --appimage-extract
sudo mv squashfs-root /opt/kook-forwarder
sudo ln -s /opt/kook-forwarder/AppRun /usr/local/bin/kook-forwarder
```

#### 可能需要的依赖
```bash
# Ubuntu/Debian
sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libsecret-1-0

# Fedora
sudo dnf install gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-core libsecret

# Arch Linux
sudo pacman -S gtk3 libnotify nss libxss libxtst xdg-utils at-spi2-core libsecret
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
```bash
# 1. 下载docker-compose.yml
wget https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/docker-compose.yml

# 2. 启动
docker-compose up -d

# 3. 访问
http://localhost:9527

# 4. 配置
# 在Web界面完成5步配置向导
```

#### 使用docker run
```bash
# 拉取镜像
docker pull ghcr.io/gfchfjh/csbjjwt:4.1.0

# 运行容器
docker run -d \
  --name kook-forwarder \
  -p 9527:9527 \
  -p 6379:6379 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  ghcr.io/gfchfjh/csbjjwt:4.1.0

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
  ├── message_ids.db # 消息去重数据库（v4.1.0新增）
  ├── .master_password # 主密码（v4.1.0新增）
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
- **Node.js**: 18+
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
```

#### 5. 配置环境变量（可选）
```bash
# backend/.env
REDIS_HOST=localhost
REDIS_PORT=6379
API_PORT=9527
DATA_DIR=./data
LOG_LEVEL=INFO
```

#### 6. 初始化数据库
```bash
cd backend
python -m app.database init
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

# 2. 启动后端（包含前端）
cd ../backend
python -m app.main --production

# 访问
http://localhost:9527
```

---

## 🔍 v4.1.0 环境检查和修复

### 自动环境检查
v4.1.0会在首次启动时自动检查：

1. ✅ **Python版本** - 需要3.11+
2. ✅ **依赖库** - 检查所有required包
3. ✅ **Playwright浏览器** - Chromium是否安装
4. ✅ **Redis连接** - Redis服务是否运行
5. ✅ **端口占用** - 9527和6379端口
6. ✅ **磁盘空间** - 至少500MB可用
7. ✅ **网络连通性** - 能否访问KOOK
8. ✅ **文件权限** - 数据目录读写权限

### 一键自动修复
```
如果检测到问题：
  → 点击"一键修复全部"按钮
  → 系统自动：
     • 安装缺失的Chromium
     • 启动Redis服务
     • 安装缺失的依赖
     • 修复文件权限
     • 创建必要目录
  → 2-3分钟自动完成
  → 继续配置
```

### 手动修复（如果自动修复失败）
系统会提供详细的修复建议和步骤，例如：
```
问题：Chromium未安装
修复步骤：
  1. 打开命令行
  2. 运行：playwright install chromium
  3. 等待下载完成
  4. 点击"重新检查"

教程链接：[查看详细教程]
```

---

## 🎯 首次配置详解

### 步骤2: Cookie导入（v4.1.0深度优化）

#### 方式1: 粘贴文本（最常用）
1. 访问KOOK网页版：https://www.kookapp.cn
2. 登录您的账号
3. 按F12打开开发者工具
4. 切换到"应用"（Application）标签
5. 左侧找到"Cookies" → "https://www.kookapp.cn"
6. 全选所有Cookie（Ctrl+A），右键复制
7. 返回应用，粘贴到文本框
8. 点击"验证并添加"

**v4.1.0智能验证**：
- 自动检测格式
- 发现错误时友好提示
- 尝试自动修复
- 提供教程链接

#### 方式2: 文件拖拽
1. 导出Cookie为JSON文件
2. 拖拽文件到应用窗口
3. 自动解析并验证

#### 方式3: 浏览器扩展（最简单）
1. 安装Chrome扩展"KOOK Cookie Exporter"
2. 访问KOOK网页版（已登录）
3. 点击扩展图标
4. Cookie自动复制到剪贴板
5. 返回应用粘贴

**v4.1.0常见错误处理**：
```
错误1: "检测到您粘贴了浏览器控制台的内容"
  → 提示：请粘贴Cookie，而不是控制台输出
  → 教程：如何正确导出Cookie

错误2: "Cookie格式不正确，缺少关键字段"
  → 提示：Cookie不完整，可能复制时遗漏
  → 自动修复：尝试补全格式
  → 教程：完整的导出步骤

错误3: "Cookie已过期"
  → 提示：需要重新登录KOOK导出
  → 过期时间：显示具体过期日期
  → 教程：如何导出长期有效的Cookie
```

### 步骤4: Bot配置（v4.1.0新增）

#### Discord Webhook配置
```
1. 进入Discord服务器设置
2. 点击"整合" → "Webhook"
3. 创建新Webhook
4. 复制Webhook URL
5. 粘贴到应用
6. 点击"测试连接"验证

✅ 测试成功：显示"连接成功"
❌ 测试失败：显示具体错误原因和解决建议

详细教程：应用内"帮助中心" → "Discord配置教程"
```

#### Telegram Bot配置
```
1. 与@BotFather对话
2. 发送 /newbot 创建Bot
3. 获取Bot Token
4. 将Bot添加到目标群组
5. 粘贴Token到应用
6. 点击"自动获取Chat ID"
7. 点击"测试连接"验证

✅ 自动获取Chat ID功能（v4.1.0增强）
   • 在群组中发送任意消息
   • 点击"自动获取"按钮
   • 系统自动检测并填充

详细教程：应用内"帮助中心" → "Telegram配置教程"
```

### 步骤5: 快速映射（v4.1.0新增）

#### 智能映射（推荐新手）
```
1. 点击"一键智能映射"按钮
2. AI分析频道名称
3. 自动推荐映射关系
4. 预览推荐结果
5. 确认或调整
6. 保存映射

示例推荐：
  KOOK "#公告" → Discord "#announcements" (相似度95%)
  KOOK "#活动" → Discord "#events" (相似度90%)
  KOOK "#更新" → Telegram "更新群" (完全匹配)
```

#### 手动映射
```
1. 从左侧选择KOOK频道
2. 从右侧选择目标平台和频道
3. 点击"添加映射"或拖拽连线
4. 一个KOOK频道可以映射到多个目标
5. 保存映射

预览示例：
  #公告频道 → 3个目标
    ├─ Discord #announcements (游戏公告Bot)
    ├─ Telegram 公告群 (TG Bot)
    └─ 飞书 运营群 (飞书Bot)
```

---

## 🔧 高级安装选项

### 自定义数据目录
```bash
# Windows
KOOK-Forwarder.exe --data-dir="D:\KookData"

# Linux/macOS
./KOOK-Forwarder.AppImage --data-dir="/custom/path"
```

### 自定义端口
```bash
# 修改配置文件
backend/app/config.py

# 或使用环境变量
export API_PORT=8888
export REDIS_PORT=6380
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

### 立即体验v4.1.0新功能

1. **设置主密码**（可选但推荐）
   ```
   设置 → 安全 → 设置主密码
     ├─ 密码：6-20位
     ├─ 记住：1/7/30天
     └─ 下次启动需要解锁
   ```

2. **选择图片策略**
   ```
   设置 → 图片处理 → 图片策略
     ├─ 智能模式（推荐）：自动选择最优方式
     ├─ 直传模式：速度优先
     └─ 图床模式：稳定优先
   ```

3. **浏览帮助系统**
   ```
   帮助中心 → 浏览所有教程
     ├─ 6种图文教程
     ├─ 8个常见问题FAQ
     ├─ 5种故障诊断工具
     └─ 视频教程（框架已完成）
   ```

### 推荐阅读
1. 📖 [START_HERE_v4.1.0.md](START_HERE_v4.1.0.md) - v4.1.0完整介绍
2. 🎯 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - 5秒了解优化
3. 📊 [P0完成报告](P0_OPTIMIZATION_COMPLETE_REPORT.md) - 12项详细说明
4. 🎨 [品牌指南](BRAND_GUIDELINES.md) - 设计规范

---

## ❓ 安装故障排查

### Windows安装失败

#### 问题1: "Windows已保护你的电脑"
**原因**: 未签名的应用  
**解决**: 点击"更多信息" → "仍要运行"

#### 问题2: 杀毒软件拦截
**原因**: 内置Redis/Chromium被误报  
**解决**: 将应用添加到白名单

#### 问题3: 安装路径权限不足
**原因**: 安装到需要管理员权限的目录  
**解决**: 右键 → "以管理员身份运行"

### macOS安装失败

#### 问题1: "无法打开，因为它来自身份不明的开发者"
**解决**:
```
方法1（推荐）：
  右键应用 → 选择"打开" → 在弹窗中点击"打开"

方法2：
  系统偏好设置 → 安全性与隐私 → 通用
  → 点击"仍要打开"
```

#### 问题2: M1/M2芯片兼容性
**解决**: v4.1.0已经完全支持Apple Silicon，直接安装即可

### Linux安装失败

#### 问题1: AppImage无法运行
**解决**:
```bash
# 安装FUSE（AppImage依赖）
sudo apt-get install fuse libfuse2
```

#### 问题2: 缺少依赖库
**解决**:
```bash
# 安装所需依赖
sudo apt-get install -y \
  libgtk-3-0 libnotify4 libnss3 libxss1 \
  libxtst6 xdg-utils libatspi2.0-0 libsecret-1-0
```

### Docker部署失败

#### 问题1: 端口冲突
```bash
# 检查端口占用
netstat -an | grep 9527
lsof -i :9527

# 使用其他端口
docker run -p 8888:9527 ...
```

#### 问题2: 权限问题
```bash
# 添加当前用户到docker组
sudo usermod -aG docker $USER

# 重新登录生效
```

---

## 📊 系统要求

### 最低配置
| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10 x64 / macOS 10.15+ / Ubuntu 20.04+ |
| **内存** | 4GB RAM |
| **磁盘** | 500MB（不含图片缓存） |
| **网络** | 稳定的互联网连接 |

### 推荐配置
| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 11 / macOS 13+ / Ubuntu 22.04+ |
| **内存** | 8GB+ RAM |
| **磁盘** | 10GB+（含图片缓存） |
| **网络** | 带宽≥10Mbps |

---

## 🎊 安装完成

### 验证安装
```bash
# 检查应用是否运行
# Windows: 任务管理器 → 查找"KOOK Forwarder"
# macOS: 活动监视器 → 查找"KOOK Forwarder"
# Linux: ps aux | grep kook

# 检查端口
curl http://localhost:9527/health

# 应返回：{"status": "ok"}
```

### 下一步
1. 完成5步配置向导
2. 启动服务
3. 查看实时监控
4. 体验v4.1.0新功能

---

## 📞 获取帮助

### 应用内帮助（推荐）
```
帮助中心 → 选择您的问题
  ├─ 安装问题
  ├─ 配置问题
  ├─ 使用问题
  └─ 性能问题
```

### 社区支持
- 📖 [完整文档](https://github.com/gfchfjh/CSBJJWT/tree/main/docs)
- 🐛 [问题反馈](https://github.com/gfchfjh/CSBJJWT/issues)
- 💬 [功能讨论](https://github.com/gfchfjh/CSBJJWT/discussions)

### v4.1.0 优化文档
- 📊 [深度分析](DEEP_OPTIMIZATION_ANALYSIS_REPORT.md) - 35项优化分析
- 📋 [P0完成报告](P0_OPTIMIZATION_COMPLETE_REPORT.md) - 12项实现
- 📈 [最终总结](FINAL_DEEP_OPTIMIZATION_SUMMARY.md) - 综合评估

---

## 🔄 升级指南

### 从v4.0.0升级到v4.1.0

#### 预编译包升级
1. 备份配置（设置 → 备份配置）
2. 下载v4.1.0安装包
3. 运行安装包（覆盖安装）
4. 启动应用，配置自动迁移
5. 建议设置主密码（新功能）

#### Docker升级
```bash
# 停止旧容器
docker stop kook-forwarder

# 备份数据
cp -r data data.backup

# 拉取新镜像
docker pull ghcr.io/gfchfjh/csbjjwt:4.1.0

# 启动新容器
docker-compose up -d
```

#### 源码升级
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 重启服务
```

### 升级后必做
1. ⏳ 查看v4.1.0新功能
2. ⏳ 设置主密码（可选但推荐）
3. ⏳ 选择图片处理策略
4. ⏳ 浏览新增的帮助文档

---

## 🎉 恭喜安装成功！

您现在可以：
- ✅ 实时监控KOOK消息
- ✅ 自动转发到多个平台
- ✅ 使用智能诊断工具
- ✅ 享受零消息丢失和重复

**如果有任何问题，请先查看应用内的"帮助中心"！**

---

**版本**: v4.1.0 Deep Optimization Edition  
**更新日期**: 2025-10-25  

🌟 **如果有帮助，请给个Star支持我们！** 🌟
