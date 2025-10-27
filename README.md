# 🚀 KOOK消息转发系统

<div align="center">

![Version](https://img.shields.io/badge/version-6.8.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4-green.svg)
![Electron](https://img.shields.io/badge/electron-28.0-purple.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**企业级桌面应用 · 真正一键安装 · 傻瓜式操作 · 零代码门槛**

[🎬 快速开始](docs/tutorials/01-快速入门指南.md) | [📖 完整文档](V6.8.0_DOCUMENTATION_INDEX.md) | [🐛 问题反馈](https://github.com/gfchfjh/CSBJJWT/issues) | [💬 讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)

</div>

---

## ✨ v6.8.0 - 傻瓜式完美版

🎊 **巅峰之作！** 12项P0级深度优化全部完成，真正实现"一键安装、3步配置、零门槛"的产品目标！

> 📖 **完整发布说明**: [V6.8.0_RELEASE_NOTES.md](./V6.8.0_RELEASE_NOTES.md)  
> 📋 **变更日志**: [V6_CHANGELOG.md](./V6_CHANGELOG.md)

---

## 🚀 v6.8.0 十二大核心优化

### 🎯 1. 真正的一键安装包
- ✅ **Windows安装包** - .exe安装程序，双击即用
- ✅ **macOS安装包** - .dmg镜像文件，拖拽安装
- ✅ **Linux安装包** - .AppImage便携版，无需安装
- ✅ **自动集成依赖** - Redis + Chromium + Python运行时全部内置
- ✅ **零技术门槛** - 无需任何配置，下载即用
- ✅ **SHA256校验** - 自动生成安装包校验和

### 🎯 2. 极简3步配置向导
- ✅ **步骤1: 欢迎页** - 免责声明 + 阅读进度 + 双重确认
- ✅ **步骤2: KOOK登录** - Cookie拖拽导入 + 自动验证
- ✅ **步骤3: 选择服务器** - 自动加载服务器/频道列表
- ✅ **完成页引导** - 明确下一步操作

### 🍪 3. Cookie拖拽导入增强
- ✅ **300px超大拖拽区** - 脉冲动画 + 渐变边框 + 悬停效果
- ✅ **3种导入方式** - 拖拽文件 / 粘贴文本 / 选择文件
- ✅ **3种格式自动识别** - JSON / Netscape / Header String
- ✅ **实时预览表格** - 显示Cookie名称/值/域名/过期时间
- ✅ **智能验证** - 检查必需字段
- ✅ **帮助链接** - 一键查看获取Cookie详细教程

### ⚡ 4. 验证码WebSocket实时推送
- ✅ **WebSocket双向通信** - 实时双向通信，替代数据库轮询
- ✅ **美观输入对话框** - 大图预览 + 120秒倒计时 + 进度条
- ✅ **动态提示** - 倒计时少于30秒时显示警告动画
- ✅ **刷新支持** - 看不清可一键刷新验证码
- ✅ **自动聚焦** - 对话框打开自动聚焦输入框

### 🎨 5. 可视化映射编辑器增强
- ✅ **三栏拖拽布局** - KOOK频道（左）← SVG画布（中）→ 目标Bot（右）
- ✅ **拖拽创建映射** - 从左侧频道拖到右侧Bot卡片
- ✅ **SVG贝塞尔曲线** - 平滑三次曲线 + 渐变色 + 箭头标记
- ✅ **60+智能映射规则** - 中英文翻译 + Levenshtein距离 + 置信度分级
- ✅ **映射预览面板** - 底部实时显示所有映射关系
- ✅ **一对多支持** - 虚线表示一个频道映射到多个Bot

### 📺 6. 应用内视频教程播放器
- ✅ **内置8个教程** - 快速入门 / Cookie / Discord / Telegram / 飞书 / 映射 / 过滤 / 排查
- ✅ **HTML5播放器** - 播放/暂停/进度条/音量/全屏
- ✅ **速度调节** - 0.5x ~ 2.0x，6档播放速度
- ✅ **章节导航** - 快速跳转到指定章节
- ✅ **观看记录** - 自动记录观看进度和次数
- ✅ **相关推荐** - 根据当前视频推荐相关教程

### 🔐 7. 主密码保护完善
- ✅ **美观解锁界面** - 渐变背景 + 浮动动画球体
- ✅ **记住我（30天）** - 勾选后30天内自动登录
- ✅ **忘记密码流程** - 邮箱验证码 → 重置密码 + 强度指示器
- ✅ **设备Token管理** - 安全的设备识别和Token存储
- ✅ **密码强度检测** - 实时显示密码强度（弱/中/强）
- ✅ **自动聚焦** - 打开页面自动聚焦密码输入框

### 💬 8. 错误提示友好化
- ✅ **30种错误翻译** - 技术错误转换为通俗易懂的描述
- ✅ **明确解决方案** - 分步骤说明如何解决问题
- ✅ **一键自动修复** - Chromium安装 / Redis启动等自动修复
- ✅ **技术详情可折叠** - 开发者可查看原始错误堆栈
- ✅ **复制错误信息** - 一键复制完整错误报告用于提Issue

### 🖼️ 9. 图床管理界面增强
- ✅ **4个彩色统计卡片** - 总空间 / 已用 / 可用 / 图片数，渐变配色
- ✅ **动态进度条** - 根据使用率变色
- ✅ **双视图模式** - 网格视图（缩略图）/ 列表视图（详细信息）
- ✅ **Lightbox预览** - 点击放大 + 显示完整信息
- ✅ **智能清理选项** - 按天数清理 / 清空全部 / 删除选中
- ✅ **搜索和排序** - 按文件名搜索，按时间/大小排序

### 📊 10. 托盘菜单统计完善
- ✅ **4种动态图标** - 在线 / 连接中 / 错误 / 离线
- ✅ **7项实时统计** - 今日消息 / 平均延迟 / 队列大小 / 活跃账号 / 活跃Bot / 运行时长
- ✅ **5秒自动刷新** - 后台定时器自动拉取最新统计数据
- ✅ **6个快捷操作** - 显示窗口 / 启动 / 停止 / 重启 / 打开日志 / 退出

### 📚 11. 图文教程完善
- ✅ **新增教程06** - 《频道映射详解教程》- 智能映射 / 可视化编辑 / 映射规则
- ✅ **新增教程07** - 《过滤规则使用技巧》- 关键词 / 用户 / 类型过滤 + 案例
- ✅ **统一模板** - 标准化结构
- ✅ **截图标注** - 所有教程新增清晰截图和标注说明
- ✅ **阅读时间** - 每篇教程标注预计阅读时间

### 🧠 12. 智能默认配置
- ✅ **系统资源检测** - CPU核心数 / RAM大小 / 磁盘空间自动检测
- ✅ **性能分级** - 高性能 / 中等性能 / 低性能三档分类
- ✅ **自动推荐配置** - 图片处理 / 并发数 / 速率限制 / 日志级别
- ✅ **首次运行应用** - 第一次启动时自动应用智能默认配置
- ✅ **配置摘要** - 启动时输出应用的配置摘要到日志
- ✅ **用户无感知** - 完全自动化，用户无需任何操作

---

## 📋 功能特性

### 核心功能

#### 🖥️ 桌面应用
- **Electron主进程** - 完整的生命周期管理
- **系统托盘** - 实时状态更新，快捷操作
- **自动启动** - 开机自启，无需手动
- **进程管理** - 自动启停后端服务
- **单实例锁** - 防止多开冲突
- **IPC通信** - 安全的主进程↔渲染进程通信

#### 📨 消息抓取
- 🌐 **Playwright驱动** - 稳定可靠的浏览器自动化
- 🔐 **多种登录方式** - 账号密码 / Cookie导入 / Chrome扩展
- 🔄 **自动重连** - 断线自动恢复
- 📡 **实时监听** - WebSocket实时接收消息
- 🎭 **多账号支持** - 同时监听多个KOOK账号

#### 🔄 消息处理
- 🎨 **智能队列** - Redis消息队列，支持持久化
- 🎨 **格式转换** - KMarkdown自动转换为目标平台格式
- 🖼️ **图片处理** - 三种策略（智能/直传/图床）
- 📎 **附件支持** - 自动下载转发
- 🔒 **文件安全** - 危险类型检测，白名单机制
- 🗑️ **消息去重** - 基于消息ID，防止重复转发
- ⚡ **异步处理** - 不阻塞，高性能

#### 🎯 多平台转发
- 💬 **Discord** - Webhook方式，支持Embed卡片
- ✈️ **Telegram** - Bot API，支持HTML/Markdown格式
- 🏢 **飞书** - 自建应用，支持消息卡片

#### 🎨 图形化界面
- 🖥️ **Electron桌面应用** - 跨平台支持（Windows/macOS/Linux）
- 🎨 **Vue 3 + Element Plus** - 现代化UI设计
- 🌍 **多语言** - 中文/英文切换
- 🌓 **主题支持** - 浅色/深色/自动跟随系统
- 📊 **实时监控** - 转发状态、统计信息、日志查看
- 🚀 **虚拟滚动** - 大量日志流畅显示

### 高级功能

#### 🧠 智能映射
- 🎯 **智能算法** - Levenshtein距离 + 中英翻译映射
- 🎯 **置信度分级** - 高/中/低三级置信度
- 🔀 **一对多转发** - 一个KOOK频道转发到多个目标
- 🔧 **灵活配置** - 支持频道级别的映射规则

#### 🔍 过滤规则
- 🔍 **关键词过滤** - 黑名单/白名单支持
- 👤 **用户过滤** - 指定用户消息转发
- 📦 **类型过滤** - 选择转发的消息类型
- 🎛️ **组合规则** - 多条件组合过滤

#### ⚙️ 系统增强
- 🔐 **主密码保护** - bcrypt加密，可选启用
- 📧 **邮件告警** - SMTP支持，异常通知
- 💾 **配置备份** - 自动/手动备份，一键恢复
- 📊 **性能监控** - CPU、内存实时监控
- 🗂️ **日志管理** - 分级日志，自动清理
- 🔒 **数据加密** - AES-256加密敏感信息

---

## 🎬 快速开始

### 方式一：一键安装包（推荐）

1. **下载安装包**
   - Windows: `KOOK-Forwarder-Setup-6.8.0.exe`
   - macOS: `KOOK-Forwarder-6.8.0.dmg`
   - Linux: `KOOK-Forwarder-6.8.0.AppImage`

2. **双击安装，完全自动化**
   - ✅ 自动安装Redis（内置，无需配置）
   - ✅ 自动安装Chromium（内置，带进度条）
   - ✅ 智能默认配置（根据系统自动优化）
   - ✅ 3步配置向导

3. **立即使用**
   - 所有依赖已内置
   - 无需任何编程知识
   - 完全傻瓜式操作

📖 **详细教程**: [快速入门指南](docs/tutorials/01-快速入门指南.md)

### 方式二：Docker部署

```bash
# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 启动服务
docker-compose up -d

# 3. 访问Web界面
# 浏览器打开: http://localhost:8080
```

📖 **详细教程**: [Docker部署指南](DEPLOYMENT_GUIDE_V6.md)

### 方式三：源码运行（开发者）

```bash
# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 启动后端
cd backend
pip install -r requirements.txt
python -m app.main

# 3. 启动前端（新终端）
cd frontend
npm install
npm run dev

# 4. 访问 http://localhost:5173
```

### 方式四：构建安装包（进阶）

```bash
# 使用极致版一键安装包构建系统
python build/build_installer_ultimate.py --clean

# 生成的安装包位于
dist/KOOK-Forwarder-Setup-6.8.0.exe      # Windows
dist/KOOK-Forwarder-6.8.0.dmg            # macOS
dist/KOOK-Forwarder-6.8.0.AppImage       # Linux
dist/checksums.json                      # SHA256校验和
```

📖 **详细教程**: [开发指南](docs/开发指南.md) | [构建指南](BUILD_INSTALLER_GUIDE.md)

---

## 📖 完整文档

### 🎓 新手教程

| 文档 | 说明 |
|-----|------|
| [快速入门指南](docs/tutorials/01-快速入门指南.md) | 快速上手系统 |
| [Cookie获取教程](docs/tutorials/02-Cookie获取详细教程.md) | 3种方法获取Cookie |
| [Discord配置教程](docs/tutorials/03-Discord配置教程.md) | 创建Webhook配置 |
| [Telegram配置教程](docs/tutorials/04-Telegram配置教程.md) | 创建Bot配置 |
| [飞书配置教程](docs/tutorials/05-飞书配置教程.md) | 自建应用配置 |
| [频道映射教程](docs/tutorials/06-频道映射详解教程.md) | 智能映射和可视化编辑 |
| [过滤规则教程](docs/tutorials/07-过滤规则使用技巧.md) | 过滤规则配置技巧 |
| [常见问题FAQ](docs/tutorials/FAQ-常见问题.md) | 常见问题详解 |

### 📚 进阶文档

| 文档 | 说明 |
|-----|------|
| [用户手册](docs/用户手册.md) | 完整功能说明 |
| [API接口文档](docs/API接口文档.md) | 所有API端点 |
| [开发指南](docs/开发指南.md) | 二次开发指南 |
| [架构设计](docs/架构设计.md) | 技术架构详解 |
| [部署指南](DEPLOYMENT_GUIDE_V6.md) | 生产环境部署 |
| [构建指南](BUILD_INSTALLER_GUIDE.md) | 从源码构建安装包 |

### 📊 版本文档

| 文档 | 说明 |
|-----|------|
| [V6.8.0发布说明](V6.8.0_RELEASE_NOTES.md) | v6.8.0详细发布说明 |
| [V6 Changelog](V6_CHANGELOG.md) | V6系列完整更新日志 |

---

## 🏗️ 技术架构

### 前端技术栈

```
Electron 28.0         # 桌面应用框架
Vue 3.4               # 渐进式JavaScript框架
Element Plus 2.5      # Vue 3组件库
Pinia 2.1             # 状态管理
Vue Router 4.2        # 路由管理
Vue I18n 9.9          # 国际化
ECharts 5.4           # 数据可视化
Vite 5.0              # 构建工具
```

### 后端技术栈

```
FastAPI 0.109         # 现代Python Web框架
Uvicorn 0.27          # ASGI服务器
Playwright 1.40       # 浏览器自动化
aiosqlite 0.19        # 异步SQLite
aioredis 2.0          # 异步Redis客户端
aiohttp 3.9           # 异步HTTP客户端
cryptography 41.0     # 加密库
Pillow 10.1           # 图片处理
PyInstaller 6.3       # Python打包工具
```

### 数据存储

```
SQLite 3              # 主数据库（异步版本）
Redis 7.2             # 消息队列 + 缓存
```

### 部署方案

```
Docker + Compose      # 容器化部署
GitHub Actions        # 自动化CI/CD
Electron Builder      # 桌面应用打包
PyInstaller           # Python打包
```

---

## 🔒 安全说明

### ⚠️ 重要声明

**本软件仅供学习和研究使用，使用本软件可能违反KOOK服务条款。**

- ❌ 请勿用于商业用途
- ❌ 请勿用于非法目的
- ❌ 请勿滥用或恶意使用
- ✅ 仅在已授权的场景使用
- ✅ 自行承担使用风险

### 🔐 安全特性

- ✅ **密码加密** - bcrypt哈希，不可逆
- ✅ **Token加密** - AES-256加密存储
- ✅ **本地存储** - 所有数据本地保存，不上传云端
- ✅ **权限隔离** - 配置文件权限限制
- ✅ **安全审计** - SQL注入防护、日志脱敏

---

## 🗺️ 路线图

### ✅ v6.8.0 已完成（2025-10-27）

- ✅ 真正的一键安装包系统
- ✅ 极简3步配置向导
- ✅ Cookie拖拽导入增强
- ✅ 验证码WebSocket实时推送
- ✅ 可视化映射编辑器增强
- ✅ 应用内视频教程播放器
- ✅ 主密码保护完善
- ✅ 错误提示友好化
- ✅ 图床管理界面增强
- ✅ 托盘菜单统计完善
- ✅ 图文教程完善
- ✅ 智能默认配置

### 🔜 未来计划

#### v7.0.0（计划中）
- ⏳ 插件系统（社区插件市场）
- ⏳ Web远程控制（多设备同步）
- ⏳ AI增强（消息摘要、智能分类）
- ⏳ 更多平台（QQ、企业微信、Slack）

---

## 🤝 贡献

欢迎贡献！我们接受以下形式的贡献：

- 🐛 **Bug报告** - [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues/new?template=bug_report.md)
- ✨ **功能建议** - [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues/new?template=feature_request.md)
- 📝 **文档改进** - 提交PR
- 🌍 **翻译** - 完善多语言支持
- 💻 **代码贡献** - 提交PR

### 贡献流程

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

**许可摘要**：
- ✅ 商业使用
- ✅ 修改
- ✅ 分发
- ✅ 私人使用
- ⚠️ 责任限制
- ⚠️ 无保证

---

## 🙏 致谢

### 核心技术

- [Electron](https://www.electronjs.org/) - 跨平台桌面应用框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [Playwright](https://playwright.dev/) - 浏览器自动化工具
- [aiosqlite](https://aiosqlite.omnilib.dev/) - 异步SQLite库

### 社区

感谢所有贡献者、使用者和提供反馈的朋友！

---

## 📞 支持与反馈

### 获取帮助

- 📖 **文档** - 查看 [完整文档](V6.8.0_DOCUMENTATION_INDEX.md)
- ❓ **FAQ** - 查看 [常见问题](docs/tutorials/FAQ-常见问题.md)
- 🐛 **Issues** - [GitHub Issues](https://github.com/gfchfjh/CSBJJWT/issues)
- 💬 **讨论** - [GitHub Discussions](https://github.com/gfchfjh/CSBJJWT/discussions)

### 联系方式

- **GitHub**: https://github.com/gfchfjh/CSBJJWT
- **Issues**: https://github.com/gfchfjh/CSBJJWT/issues
- **Discussions**: https://github.com/gfchfjh/CSBJJWT/discussions

---

## 📊 项目统计

- **代码行数**: ~50,000行
- **提交次数**: 125+
- **文档字数**: ~75,000字
- **API端点**: 68+
- **UI页面**: 24个
- **Vue组件**: 72+
- **测试覆盖**: 75+
- **Star数**: 如果觉得有用，请给项目点个Star！

---

<div align="center">

**⭐ 如果觉得有用，请给项目点个Star ⭐**

**📢 欢迎分享给更多需要的朋友 📢**

**Made with ❤️ by KOOK消息转发系统团队**

</div>

---

**版本**: v6.8.0 (傻瓜式完美版)  
**最后更新**: 2025-10-27  
**许可证**: MIT License  
**里程碑**: 实现真正的"一键安装、3步配置、零门槛"目标
