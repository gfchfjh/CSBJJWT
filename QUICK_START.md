# 🚀 5分钟快速开始

**KOOK消息转发系统 v3.0**

---

## 🎯 快速选择安装方式

根据您的使用场景选择合适的安装方式：

| 场景 | 推荐方式 | 预计时间 | 难度 |
|------|----------|----------|------|
| 🪟 Windows桌面用户 | [预编译安装包](#方式1-预编译安装包推荐) | 2分钟 | ⭐ 超简单 |
| 🐧 Linux服务器 | [Docker一键部署](#方式2-docker一键部署) | 3分钟 | ⭐ 超简单 |
| 🍎 macOS用户 | [预编译安装包](#方式1-预编译安装包推荐) | 2分钟 | ⭐ 超简单 |
| 👨‍💻 开发者 | [源码安装](#方式3-源码安装开发者) | 5-10分钟 | ⭐⭐ 简单 |

---

## 方式1: 预编译安装包（⭐推荐）

### Windows

1. **下载安装包**
   ```
   https://github.com/gfchfjh/CSBJJWT/releases/latest
   下载: KOOK.Setup.3.0.0.exe (~100 MB)
   ```

2. **安装**
   - 双击运行 `KOOK.Setup.3.0.0.exe`
   - 按照向导完成安装
   - 安装完成后自动启动

3. **首次配置**
   - 设置主密码（用于保护敏感数据）
   - 添加KOOK账号
   - 配置目标平台（Discord/Telegram/飞书）
   - 创建频道映射

✅ **完成！** 系统将自动开始转发消息

### Linux

1. **下载AppImage**
   ```bash
   # 下载
   wget https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KOOK.-3.0.0.AppImage
   
   # 添加执行权限
   chmod +x KOOK.-3.0.0.AppImage
   
   # 运行
   ./KOOK.-3.0.0.AppImage
   ```

2. **首次配置**（同Windows）

### macOS

1. **下载DMG**
   ```
   https://github.com/gfchfjh/CSBJJWT/releases/latest
   下载: KOOK.-3.0.0.dmg (~150 MB)
   ```

2. **安装**
   - 双击打开DMG文件
   - 将应用拖到Applications文件夹
   - 从Launchpad启动

3. **首次配置**（同Windows）

---

## 方式2: Docker一键部署

### 适用场景
- Linux/macOS服务器
- 需要7×24小时运行
- 需要容器化部署

### 一键安装

```bash
# 一行命令完成安装
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/docker-install.sh | bash
```

这将自动：
- 安装Docker（如果未安装）
- 拉取最新镜像
- 创建容器并启动
- 配置自动重启
- 持久化数据

### 访问

安装完成后，浏览器访问：
```
http://localhost:9527
```

### 管理命令

```bash
# 查看日志
docker logs -f kook-forwarder

# 停止
docker stop kook-forwarder

# 启动
docker start kook-forwarder

# 重启
docker restart kook-forwarder

# 更新到最新版
docker pull ghcr.io/gfchfjh/csbjjwt:latest
docker stop kook-forwarder
docker rm kook-forwarder
docker run -d --name kook-forwarder \
  -p 9527:9527 \
  -v kook-data:/app/data \
  --restart unless-stopped \
  ghcr.io/gfchfjh/csbjjwt:latest
```

---

## 方式3: 源码安装（开发者）

### 前置要求
- Python 3.11+
- Node.js 18+
- Git

### 快速安装

```bash
# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 一键安装并启动
./install.sh  # Linux/macOS
# 或
install.bat   # Windows

# 3. 启动
./start.sh    # Linux/macOS
# 或
start.bat     # Windows
```

### 手动安装（详细）

```bash
# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 启动后端
cd ../backend
python -m app.main

# 5. 启动前端（新终端）
cd ../frontend
npm run dev
```

### 访问

- 前端: http://localhost:5173
- 后端API: http://localhost:9527

---

## 📝 首次配置指南

### 1. 设置主密码

首次启动时，需要设置主密码用于保护敏感数据：

- 密码长度至少8位
- 建议包含大小写字母、数字、特殊字符
- 妥善保管，忘记密码无法找回

### 2. 添加KOOK账号

#### 方法1: 浏览器扩展（推荐）

1. 安装Chrome扩展（项目内提供）
2. 登录KOOK网页版
3. 点击扩展图标
4. 一键导入Cookie

#### 方法2: 手动导入

1. 登录KOOK网页版（https://www.kookapp.cn）
2. 按F12打开开发者工具
3. 切换到Application标签
4. 找到Cookies → kookapp.cn
5. 复制Cookie值
6. 在系统中导入

### 3. 配置目标平台

#### Discord

1. 创建Webhook：
   - 打开Discord频道设置
   - 整合 → Webhook → 新建Webhook
   - 复制Webhook URL

2. 在系统中添加：
   - 平台：Discord
   - 名称：自定义
   - Webhook URL：粘贴刚才复制的URL

#### Telegram

1. 创建Bot：
   - 私信 @BotFather
   - 发送 `/newbot`
   - 按提示创建Bot
   - 获取Bot Token

2. 获取Chat ID：
   - 添加Bot到群组/频道
   - 发送一条消息
   - 访问：`https://api.telegram.org/bot<token>/getUpdates`
   - 查找chat.id

3. 在系统中添加：
   - 平台：Telegram
   - Bot Token：粘贴Token
   - Chat ID：填写Chat ID

#### 飞书

1. 创建Webhook：
   - 打开飞书群设置
   - 群机器人 → 添加机器人
   - 选择自定义机器人
   - 复制Webhook URL

2. 在系统中添加：
   - 平台：飞书
   - Webhook URL：粘贴URL

### 4. 创建频道映射

1. 选择KOOK服务器和频道
2. 选择目标平台和Bot
3. 点击"创建映射"

✅ **完成！** 现在KOOK消息将自动转发到目标平台

---

## 🔍 常见问题

### Q: 忘记主密码怎么办？

A: 主密码无法找回，需要重新初始化系统：
```bash
# 删除数据库（会清空所有配置）
rm ~/Documents/KookForwarder/data/config.db
```

### Q: Cookie失效怎么办？

A: 重新导入Cookie即可：
1. 登录KOOK网页版
2. 使用浏览器扩展或手动方式重新导入

### Q: 消息转发失败？

A: 检查以下几点：
1. 账号Cookie是否有效
2. 目标平台配置是否正确
3. Webhook/Bot Token是否有效
4. 查看日志了解详细错误

### Q: 如何更新到最新版？

A: 
- **预编译包**: 下载最新安装包重新安装
- **Docker**: `docker pull ghcr.io/gfchfjh/csbjjwt:latest`
- **源码**: `git pull && ./install.sh`

---

## 📚 更多文档

- [完整安装指南](INSTALLATION_GUIDE.md)
- [优化实施指南](OPTIMIZATION_IMPLEMENTATION_GUIDE.md)
- [更新日志](CHANGELOG_v3.0_DEEP_OPTIMIZATION.md)
- [完整文档](docs/)

---

## 🆘 获取帮助

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- 文档中心: https://github.com/gfchfjh/CSBJJWT/tree/main/docs
- 示例视频: 项目内置帮助中心

---

<div align="center">

**KOOK消息转发系统 v3.0**

高性能跨平台消息转发工具

**5分钟完成配置，立即开始使用！**

[立即下载](https://github.com/gfchfjh/CSBJJWT/releases/latest) | [查看文档](README.md)

</div>
