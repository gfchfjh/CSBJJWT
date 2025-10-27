# 🚀 KOOK消息转发系统

<div align="center">

![Version](https://img.shields.io/badge/version-7.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4-green.svg)
![Electron](https://img.shields.io/badge/electron-28.0-purple.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**企业级桌面应用 · 真正一键安装 · 傻瓜式操作 · 零代码门槛**

[🎬 快速开始](docs/tutorials/01-快速入门指南.md) | [📖 完整文档](V6.8.0_DOCUMENTATION_INDEX.md) | [🐛 问题反馈](https://github.com/gfchfjh/CSBJJWT/issues) | [💬 讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)

</div>

---

## ✨ v7.0.0 - 易用版完美实现 🎉

🎊 **史诗级更新！** 15项深度优化全部完成（100%），真正实现"一键安装、3步配置、零门槛"的完美产品！

> 📖 **完整优化报告**: [【最终】KOOK深度优化完成总结.md](./【最终】KOOK深度优化完成总结.md)  
> 📖 **快速开始**: [【开始这里】深度优化成果总览.md](./【开始这里】深度优化成果总览.md)  
> 📖 **集成指南**: [集成部署指南.md](./集成部署指南.md)  
> 📋 **变更日志**: [V6_CHANGELOG.md](./V6_CHANGELOG.md)

---

## 🚀 v7.0.0 十五大深度优化

### 易用性革命

- ✅ **配置流程**: 从10+步骤简化到3步向导
- ✅ **Cookie导入**: 支持3种格式+实时预览
- ✅ **智能映射**: 60+规则自动匹配
- ✅ **图片可靠性**: 智能三级回退策略
- ✅ **消息类型**: 完整支持（表情/引用/链接/附件）
- ✅ **安全防护**: Token+设备+审计+强度检测

---

## 🎯 P0级优化（必须实现）- 8项 ✅

### 🎯 P0-1: KOOK消息监听增强 ✅
**文件**: `backend/app/kook/message_parser.py` (580行)

- ✅ **表情反应解析** - 完整解析和聚合显示
- ✅ **回复引用解析** - 支持嵌套引用
- ✅ **链接预览解析** - Open Graph标签自动提取
- ✅ **文件附件解析** - 50MB大小限制
- ✅ **@提及解析** - 用户/角色/全体成员
- ✅ **指数退避重连** - 30s→60s→120s→240s→300s
- ✅ **WebSocket通知** - 实时推送连接状态
- ✅ **邮件告警** - 服务异常邮件通知

### 🎯 P0-2: 首次配置向导完善 ✅  
**文件**: `wizard/Step0Welcome.vue` + `Step3Complete.vue` + `CookieImportDragDropUltra.vue`

- ✅ **欢迎页** - 免责声明 + 实时阅读进度追踪 + 双重确认
- ✅ **Cookie导入** - 300px超大拖拽区 + 3种格式（JSON/Netscape/Header）
- ✅ **预览表格** - 分页10条/页 + 智能验证
- ✅ **完成页** - 配置摘要 + 分步引导 + 粒子动画

### 🎯 P0-3: 消息格式转换完善 ✅
**文件**: `backend/app/processors/formatter.py` (+250行)

- ✅ **回复引用格式化** - Discord (> 引用块) / Telegram (<blockquote>) / 飞书 (【引用】)
- ✅ **链接预览卡片** - Discord Embed / Telegram HTML / 飞书交互卡片
- ✅ **表情反应聚合** - ❤️ 用户A、用户B (2) | 👍 用户C (1)
- ✅ **@提及增强** - 支持user/role/all/here

### 🎯 P0-4: 图片智能处理策略 ✅
**文件**: `backend/app/processors/image_strategy_ultimate.py` (350行)

- ✅ **智能三级策略** - 优先直传→失败图床→保存本地重试
- ✅ **HMAC-SHA256签名** - Token 2小时自动过期
- ✅ **自动清理** - 7天前旧图 + 空间超限自动删除
- ✅ **存储统计** - 图片数/空间使用/使用率

### 🎯 P0-5: 图床管理界面完善 ✅
**文件**: `frontend/src/views/ImageStorageUltraComplete.vue` (650行)

- ✅ **4个彩色统计卡片** - 渐变背景，悬停效果
- ✅ **双视图模式** - 网格视图（缩略图）/ 列表视图（详情）
- ✅ **Lightbox大图预览** - 点击放大 + 完整信息
- ✅ **搜索排序** - 按文件名/时间/大小
- ✅ **智能清理** - 按天数/清空全部
- ✅ **批量删除** - 多选删除

### 🎯 P0-6: 频道映射编辑器增强 ✅
**文件**: `frontend/src/components/MappingVisualEditorUltimate.vue` (600行)

- ✅ **三栏拖拽布局** - KOOK频道（左）← SVG画布（中）→ 目标Bot（右）
- ✅ **SVG贝塞尔曲线** - 三次曲线 + 渐变色 + 箭头标记
- ✅ **60+智能映射规则** - 中英文双向 + Levenshtein距离
- ✅ **置信度评分** - 高/中/低三级分类
- ✅ **一对多显示** - 虚线表示
- ✅ **映射预览表格** - 底部实时显示

### 🎯 P0-7: 过滤规则界面优化 ✅
**文件**: `frontend/src/views/FilterEnhanced.vue` (550行)

- ✅ **关键词Tag输入器** - 可视化添加/删除
- ✅ **黑名单/白名单** - 关键词+用户双重过滤
- ✅ **实时规则测试** - 5级检测（类型/黑名单/白名单/用户）
- ✅ **用户选择器** - 搜索+表格选择
- ✅ **消息类型复选框** - 文本/图片/链接/文件/反应/@全体

### 🎯 P0-8: 实时监控页增强 ✅
**文件**: `frontend/src/views/LogsEnhanced.vue` (500行)

- ✅ **消息搜索** - 内容全文搜索
- ✅ **多条件筛选** - 状态/平台/日期范围
- ✅ **失败重试** - 手动重试 + 批量重试所有失败
- ✅ **日志导出** - CSV/JSON两种格式
- ✅ **统计卡片** - 总数/成功率/平均延迟
- ✅ **WebSocket实时更新** - 新消息自动推送

---

## 🎯 P1级优化（重要优化）- 4项 ✅

### 🎯 P1-1: 系统设置页完善 ✅
**文件**: `frontend/src/views/SettingsUltimate.vue` (650行)

- ✅ **基础设置** - 服务控制 + 开机自启 + 最小化托盘
- ✅ **图片处理** - 策略选择UI + 存储路径管理 + 自动清理
- ✅ **邮件告警** - SMTP配置 + 测试邮件 + 告警规则
- ✅ **备份恢复** - 手动/自动备份 + 文件列表 + 一键恢复
- ✅ **高级设置** - 日志级别 + 通知 + 语言/主题 + 自动更新

### 🎯 P1-2: 多账号管理增强 ✅
**文件**: `frontend/src/views/AccountsEnhanced.vue` (450行)

- ✅ **状态卡片** - 在线/离线脉冲动画
- ✅ **4个统计指标** - 服务器数/频道数/最后活跃/今日消息
- ✅ **相对时间** - "5分钟前"/"2小时前"
- ✅ **离线提示** - 显示掉线原因
- ✅ **重新登录** - 一键重连

### 🎯 P1-3: 托盘菜单完善 ✅
**文件**: `frontend/electron/tray-enhanced.js` (300行)

- ✅ **4种动态图标** - online/connecting/error/offline
- ✅ **7项实时统计** - 今日消息/延迟/队列/账号/Bot/运行时长
- ✅ **5秒自动刷新** - 定时器自动更新
- ✅ **6个快捷操作** - 启动/停止/重启/日志/配置/退出

### 🎯 P1-4: 文档帮助系统 ✅
**文件**: `frontend/src/views/HelpCenterUltimate.vue` (550行)

- ✅ **HTML5视频播放器** - 播放控制 + 多档速度调节
- ✅ **章节导航** - 快速跳转
- ✅ **9个图文教程** - 快速入门到高级排查
- ✅ **30+FAQ** - 常见问题详解
- ✅ **相关推荐** - 智能推荐

---

## 🎯 P2级优化（增强优化）- 3项 ✅

### 🎯 P2-1: 打包部署流程优化 ✅
**文件**: `build/build_installer_complete.py` (350行)

- ✅ **Redis自动下载** - Windows/Linux/macOS，带进度条
- ✅ **Chromium自动安装** - playwright install，实时输出
- ✅ **SHA256校验和** - 自动生成checksums.json
- ✅ **跨平台构建** - .exe / .dmg / .AppImage

### 🎯 P2-2: 性能监控UI ✅
**文件**: `frontend/src/views/PerformanceMonitorUltimate.vue` (400行)

- ✅ **系统资源卡片** - CPU/内存/磁盘/网络
- ✅ **ECharts实时图表** - CPU/内存趋势 + 消息速率
- ✅ **性能瓶颈分析** - 分级（严重/警告/提示）
- ✅ **慢操作分析** - 耗时>1秒的操作

### 🎯 P2-3: 安全性增强 ✅
**文件**: `frontend/src/views/SecurityEnhanced.vue` (550行)

- ✅ **密码强度检测** - 实时5级评分系统
- ✅ **设备Token管理** - 信任设备列表 + 可撤销
- ✅ **审计日志** - 完整操作追踪（IP/设备/时间）
- ✅ **数据加密** - AES-256加密 + 密钥重新生成

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

### ✅ v7.0.0 已完成（2025-10-27）

**P0级优化（8项）**:
- ✅ KOOK消息监听增强 - 表情/引用/链接/附件全支持
- ✅ 首次配置向导完善 - 3步向导完美体验
- ✅ 消息格式转换完善 - 3平台完整格式化
- ✅ 图片智能处理策略 - 智能三级回退
- ✅ 图床管理界面完善 - 双视图+Lightbox
- ✅ 频道映射编辑器增强 - SVG+60规则
- ✅ 过滤规则界面优化 - Tag输入+实时测试
- ✅ 实时监控页增强 - 搜索+导出+重试

**P1级优化（4项）**:
- ✅ 系统设置页完善 - 5个标签页完整功能
- ✅ 多账号管理增强 - 状态卡片+统计指标
- ✅ 托盘菜单完善 - 动态图标+实时统计
- ✅ 文档帮助系统 - 视频播放器+30+FAQ

**P2级优化（3项）**:
- ✅ 打包部署流程优化 - 自动下载+校验和
- ✅ 性能监控UI - ECharts图表+瓶颈分析
- ✅ 安全性增强 - 密码强度+设备管理+审计

**成果数据**:
- 新增19个代码文件（~11,500行）
- 新增10个技术文档（~4,000行）
- 易用性大幅提升，配置流程简化，功能全面增强
- 完成度：15/15任务（100%）

### 🔜 未来计划

#### v7.1.0（规划中）
- ⏳ 插件系统（社区插件市场）
- ⏳ Web远程控制（多设备同步）
- ⏳ AI增强（消息摘要、智能分类）
- ⏳ 更多平台（QQ、企业微信、Slack）
- ⏳ 性能优化（虚拟滚动、懒加载）
- ⏳ 移动端APP（React Native）

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

### v7.0.0 更新后

- **代码行数**: ~61,500行（+11,500行）
- **提交次数**: 130+
- **文档字数**: ~79,000字（+4,000字）
- **API端点**: 75+（+7个新端点）
- **UI页面**: 32个（+8个新页面）
- **Vue组件**: 85+（+13个新组件）
- **测试覆盖**: 75%+
- **Star数**: 如果觉得有用，请给项目点个Star！

### 本次优化贡献

- ✅ 新增代码文件：19个
- ✅ 新增技术文档：10个
- ✅ 修改核心文件：3个
- ✅ 优化任务完成：15/15（100%）

---

<div align="center">

**如果觉得有用，请给项目点个Star**

**📢 欢迎分享给更多需要的朋友 📢**

**Made with ❤️ by KOOK消息转发系统团队**

</div>

---

**版本**: v7.0.0 (易用版完美实现)  
**最后更新**: 2025-10-27  
**许可证**: MIT License  
**里程碑**: 15项深度优化100%完成，实现完美"一键安装、3步配置、零门槛"产品
 License  
**里程碑**: 15项深度优化100%完成，实现完美"一键安装、3步配置、零门槛"产品
��品
