# KOOK消息转发系统 v18.0.0 - 完整正式版

**发布日期**: 2025-10-31  
**版本状态**: 稳定版 (Stable)  
**更新类型**: 重大更新 (Major Release)

---

## 📦 快速下载

### Windows (111MB)
```
KOOK-Forwarder-v18.0.0-Windows.zip
```
- 包含: NSIS安装器 + Python后端 + 完整文档
- 校验: MD5 + SHA256
- 系统要求: Windows 10 (1809+) / Windows 11

### Linux (274MB)
```
KOOK-Forwarder-v18.0.0-Linux.tar.gz
```
- 包含: AppImage前端 + Python后端 + 完整文档
- 校验: MD5 + SHA256
- 系统要求: Ubuntu 20.04+ / Debian 11+ / CentOS 8+

**下载地址**: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0

---

## 🎉 本次更新亮点

### ✨ 全新功能

#### 1. 🆕 新增平台支持（5平台全覆盖）
- ✅ **企业微信群机器人** - Webhook完整支持
  - 文本、Markdown、图片、文件消息
  - 自动消息分割（2000字符）
  - 速率限制（20次/分钟）
  
- ✅ **钉钉群机器人** - Webhook完整支持
  - 签名验证安全机制
  - @提及功能
  - Markdown格式支持

- ✅ 现已支持：Discord | Telegram | 飞书 | 企业微信 | 钉钉

#### 2. 🔌 智能插件系统
- ✅ **关键词自动回复插件**
  - 精确匹配、包含匹配、正则表达式
  - 10个预定义规则
  - 变量替换（{sender}、{time}等）
  - 自定义规则持久化

- ✅ **URL链接预览插件**
  - 自动提取并预览URL
  - 获取网页元数据（标题、描述、封面图）
  - 智能限制预览数量

#### 3. 🪟 Windows完整正式版
- ✅ **NSIS专业安装器** - 一键安装体验
- ✅ **GitHub Actions自动构建** - CI/CD全自动
- ✅ **便携版支持** - 免安装直接运行
- ✅ **版本号修复** - 正确显示v18.0.0

---

## 🔧 代码质量提升

### 语法错误修复（本次更新）
- ✅ 修复5处Python语法错误
  - `wizard_unified.py` - 添加缺失的with关键字
  - `cookie_import_enhanced.py` - 修复中文引号
  - `environment_autofix.py` - 修复3处中文引号
  - `smart_mapping_api.py` - 删除死代码
  - `help_system.py` - 修复中文引号

### 完整性验证（本次更新）
- ✅ **250个Python文件** - 语法全部正确
- ✅ **16个核心文件** - 完整无缺失
- ✅ **70+个API路由** - 正确注册
- ✅ **5个数据库表** - 结构完整

详见: [CODE_INTEGRITY_REPORT.md](https://github.com/gfchfjh/CSBJJWT/blob/main/CODE_INTEGRITY_REPORT.md)

### 系统完善
- ✅ **所有TODO已修复** - 20+个待完成功能全部实现
- ✅ **Mock数据替换** - 所有模拟数据改为真实数据库查询
- ✅ **系统集成完善** - 启动/停止/状态监控一体化

---

## 📥 安装指南

### Windows安装

#### 方式1: NSIS安装器（推荐）
```powershell
# 1. 下载Windows包
Invoke-WebRequest -Uri "https://github.com/gfchfjh/CSBJJWT/releases/download/v18.0.0/KOOK-Forwarder-v18.0.0-Windows.zip" -OutFile "KOOK-v18.0.0.zip"

# 2. 解压
Expand-Archive -Path "KOOK-v18.0.0.zip" -DestinationPath "KOOK-v18.0.0"

# 3. 运行安装器
cd KOOK-v18.0.0
.\KOOK消息转发系统-Setup-18.0.0.exe
```

#### 方式2: 便携版
直接运行解压后的 `win-unpacked\KOOK消息转发系统.exe`

### Linux安装

```bash
# 1. 下载Linux包
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v18.0.0/KOOK-Forwarder-v18.0.0-Linux.tar.gz

# 2. 校验完整性（推荐）
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v18.0.0/KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5
md5sum -c KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5

# 3. 解压
tar -xzf KOOK-Forwarder-v18.0.0-Linux.tar.gz
cd KOOK-Forwarder-v18.0.0-Linux

# 4. 赋予执行权限
chmod +x frontend/*.AppImage
chmod +x backend/KOOKForwarder/KOOKForwarder

# 5. 启动后端
./backend/KOOKForwarder/KOOKForwarder &

# 6. 启动前端
./frontend/KOOK消息转发系统-18.0.0.AppImage
```

---

## 🔒 文件校验

### Windows包
**文件名**: `KOOK-Forwarder-v18.0.0-Windows.zip`  
**大小**: 111 MB  
**MD5**: 见 `KOOK-Forwarder-v18.0.0-Windows.zip.md5`  
**SHA256**: 见 `KOOK-Forwarder-v18.0.0-Windows.zip.sha256`

### Linux包
**文件名**: `KOOK-Forwarder-v18.0.0-Linux.tar.gz`  
**大小**: 274 MB  
**MD5**: `bc8e2a8a3d0ac238ed3a7aaf0f3d898e`  
**SHA256**: `bd44148ce5029c147f600392a79eb3bc21a530ff91aff5f4c25a4872b5c922e8`

---

## 📋 系统要求

### Windows
- **操作系统**: Windows 10 (版本1809+) 或 Windows 11
- **处理器**: x64架构
- **内存**: 4GB RAM (推荐8GB)
- **存储**: 500MB可用空间
- **网络**: 互联网连接

### Linux
- **发行版**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Fedora 35+ / Arch Linux
- **架构**: x86_64
- **内存**: 4GB RAM (推荐8GB)
- **存储**: 500MB可用空间
- **依赖**: FUSE 2.x (AppImage运行需要)

---

## 🚀 快速开始

### 1. 首次运行
启动后会自动打开配置向导，按照以下步骤操作：

#### 步骤1: 添加KOOK账号
- 方式A: 导入Cookie（推荐）
- 方式B: 扫码登录
- 方式C: 账号密码登录

#### 步骤2: 配置目标Bot
选择转发平台并配置：
- **Discord**: Webhook URL
- **Telegram**: Bot Token + Chat ID
- **飞书**: App ID + App Secret + Chat ID
- **企业微信**: Webhook URL
- **钉钉**: Webhook URL + Secret（可选）

#### 步骤3: 设置频道映射
- 选择KOOK源频道
- 选择目标平台频道
- 配置转发规则（可选）

### 2. 开始使用
完成配置后，系统会自动开始监听和转发消息。

---

## 📚 完整文档

### 用户文档
- [用户手册](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/USER_MANUAL.md)
- [常见问题FAQ](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/FAQ.md)
- [更新日志](https://github.com/gfchfjh/CSBJJWT/blob/main/CHANGELOG.md)

### 配置教程
- [如何获取KOOK Cookie](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/如何获取KOOK_Cookie.md)
- [如何创建Discord Webhook](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/如何创建Discord_Webhook.md)
- [如何创建Telegram Bot](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/如何创建Telegram_Bot.md)
- [如何配置飞书自建应用](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/如何配置飞书自建应用.md)

### 开发文档
- [开发指南](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/开发指南.md)
- [架构设计](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/架构设计.md)
- [API接口文档](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/API接口文档.md)
- [构建发布指南](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/构建发布指南.md)

---

## ✨ 核心特性

### 消息转发
- ✅ **实时转发** - 基于Playwright的WebSocket监听
- ✅ **多平台支持** - Discord、Telegram、飞书、企业微信、钉钉
- ✅ **消息类型** - 文本、图片、文件、语音、视频、KMarkdown
- ✅ **智能映射** - 灵活的频道映射规则
- ✅ **格式转换** - KMarkdown → Markdown自动转换

### 消息处理
- ✅ **图片处理** - 直接上传/本地图床/压缩
- ✅ **文件转发** - 自动下载并转发到目标平台
- ✅ **消息去重** - LRU缓存机制，避免重复转发
- ✅ **消息队列** - Redis异步队列，高并发支持
- ✅ **速率限制** - 防止API滥用，保护账号安全

### 高级功能
- ✅ **插件系统** - 关键词回复、URL预览等可扩展功能
- ✅ **账号管理** - 多账号支持，Cookie自动更新
- ✅ **日志记录** - 完整的转发日志和审计跟踪
- ✅ **数据加密** - AES-256加密敏感信息
- ✅ **备份恢复** - 一键备份和恢复配置

### 用户界面
- ✅ **现代化UI** - Vue 3 + Element Plus
- ✅ **配置向导** - 3步快速配置
- ✅ **实时监控** - 转发状态实时显示
- ✅ **统计图表** - ECharts数据可视化
- ✅ **多语言** - 中文/英文（计划中）

---

## 🔄 从旧版本升级

### 从v16.x/v17.x升级
1. **备份数据**: 先在旧版本中执行"备份配置"
2. **卸载旧版**: 卸载旧版本（Windows）或删除旧文件（Linux）
3. **安装新版**: 按照上述安装指南安装v18.0.0
4. **恢复数据**: 在新版本中执行"恢复配置"

**注意**: v18.0.0数据库结构兼容v16.x和v17.x，无需手动迁移。

---

## ⚠️ 重要说明

### 1. 版本清理
本次发布清理了以下混淆的旧版本：
- ❌ v18.0.0-win (文件名错误)
- ❌ v18.0.0-update (临时标签)

**现在只保留唯一正确的v18.0.0版本**，避免用户混淆。

### 2. 文件命名规范
所有安装包现在使用统一命名格式：
```
KOOK-Forwarder-v18.0.0-{Platform}.{ext}
```

### 3. 代码质量
本次更新修复了5处Python语法错误，通过了250个文件的完整性检查。
所有核心功能完整，可直接用于生产环境。

---

## 🐛 已知问题

### macOS版本
- ⚠️ macOS DMG暂时不可用
- 替代方案: 使用源码安装或Docker部署
- 计划在v18.1.0修复

### 性能优化
- 大量消息转发时可能出现延迟（> 100条/秒）
- 建议配置Redis缓存优化
- 计划在v18.1.0优化

---

## 💬 反馈与支持

### 遇到问题？
1. 查看 [常见问题FAQ](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/FAQ.md)
2. 搜索 [已有Issues](https://github.com/gfchfjh/CSBJJWT/issues)
3. 提交 [新Issue](https://github.com/gfchfjh/CSBJJWT/issues/new)

### 功能建议
欢迎在 [Discussions](https://github.com/gfchfjh/CSBJJWT/discussions) 中分享您的想法！

### 贡献代码
查看 [开发指南](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/开发指南.md) 了解如何贡献。

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

特别感谢：
- Playwright 团队 - 强大的浏览器自动化工具
- FastAPI 团队 - 优秀的Python Web框架
- Vue.js 团队 - 现代化的前端框架
- Element Plus 团队 - 精美的UI组件库

---

## 📜 许可证

MIT License - 详见 [LICENSE](https://github.com/gfchfjh/CSBJJWT/blob/main/LICENSE)

---

## 🔗 相关链接

- **项目主页**: https://github.com/gfchfjh/CSBJJWT
- **在线文档**: https://github.com/gfchfjh/CSBJJWT/tree/main/docs
- **更新日志**: https://github.com/gfchfjh/CSBJJWT/blob/main/CHANGELOG.md
- **Issues**: https://github.com/gfchfjh/CSBJJWT/issues
- **Discussions**: https://github.com/gfchfjh/CSBJJWT/discussions

---

**享受使用 KOOK消息转发系统 v18.0.0！** 🎉

*最后更新: 2025-10-31*
