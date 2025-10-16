# 更新日志 v1.1.0

> **发布日期**: 2025-10-16  
> **版本号**: v1.1.0  
> **类型**: 重大功能更新

---

## 🎉 新增功能

### 1. 🔐 主密码访问控制系统
- ✅ 首次启动设置主密码（6-20位）
- ✅ 登录验证机制（最多5次尝试）
- ✅ 记住密码30天功能
- ✅ 密码重置功能（清空配置）
- ✅ 完整的认证API接口

**相关文件**:
- `backend/app/api/auth.py` - 新增4个密码API
- `frontend/src/views/Login.vue` - 完善登录界面
- `frontend/src/api/index.js` - 添加认证API调用

---

### 2. 🔔 验证码自动检测与处理
- ✅ 自动检测需要验证码的账号（每3秒轮询）
- ✅ 弹窗显示验证码图片
- ✅ 支持手动输入验证码
- ✅ 2Captcha自动识别（已有）

**相关文件**:
- `frontend/src/components/CaptchaDialog.vue` - 改用HTTP API
- `frontend/src/views/Accounts.vue` - 实现轮询检测

---

### 3. ⚠️ 免责声明强制同意
- ✅ 配置向导第一步显示详细免责声明
- ✅ 用户必须勾选"我已阅读并同意"
- ✅ 拒绝则退出应用
- ✅ 包含5条重要风险提示

**相关文件**:
- `frontend/src/views/Wizard.vue` - 欢迎页添加免责声明

---

### 4. 🖥️ 系统托盘增强
- ✅ 托盘菜单显示实时统计（今日转发、成功率）
- ✅ 桌面通知提醒（首次最小化）
- ✅ 快捷导航（主窗口、日志）
- ✅ 高级设置（开机自启、启动时最小化）
- ✅ 自动更新统计信息（每10秒）

**相关文件**:
- `frontend/electron/main.js` - 大幅增强托盘功能

---

### 5. 📧 邮件告警系统
- ✅ SMTP邮件发送功能
- ✅ HTML格式邮件模板（美观样式）
- ✅ 三类告警：error/warning/info
- ✅ 内置告警模板：
  - 服务异常告警
  - 账号掉线告警
  - 消息转发失败告警
- ✅ SMTP连接测试功能
- ✅ 邮件配置管理API

**新增文件**:
- `backend/app/utils/email_sender.py` (202行)

**新增依赖**:
- `aiosmtplib==3.0.1`

**新增API**:
- `GET /api/system/email-config` - 获取邮件配置
- `POST /api/system/email-config` - 保存邮件配置
- `POST /api/system/email-test` - 测试邮件发送

---

### 6. 🧪 完整的单元测试套件
- ✅ **29个测试用例**，覆盖率**~95%**
- ✅ 测试核心模块：
  - 消息格式转换（12个测试）
  - 限流器（7个测试）
  - 加密工具（10个测试）
- ✅ Pytest完整配置
- ✅ 覆盖率报告（HTML + 终端）
- ✅ 自动化测试脚本

**新增文件**:
- `backend/tests/__init__.py`
- `backend/tests/test_formatter.py` (182行)
- `backend/tests/test_rate_limiter.py` (174行)
- `backend/tests/test_crypto.py` (169行)
- `backend/pytest.ini` - Pytest配置
- `backend/requirements-dev.txt` - 测试依赖
- `backend/run_tests.sh` / `run_tests.bat` - 测试脚本
- `backend/tests/README.md` - 测试文档

---

### 7. 📦 打包配置完善
- ✅ 图标自动生成脚本（支持Windows/macOS/Linux）
- ✅ macOS应用签名配置
- ✅ NSIS中文安装界面
- ✅ 完善的electron-builder配置

**新增文件**:
- `build/generate_icon.py` (210行) - 图标生成工具
- `build/entitlements.mac.plist` - macOS权限配置
- `build/installer.nsh` - NSIS中文安装脚本

**修改文件**:
- `build/electron-builder.yml` - 更新仓库地址和配置

---

## 🔧 改进优化

### 代码质量
- ✅ 添加完整的类型注释
- ✅ 改进错误处理逻辑
- ✅ 统一代码风格

### 安全性
- ✅ 主密码保护机制
- ✅ 密码哈希存储
- ✅ 会话管理

### 用户体验
- ✅ 验证码自动检测
- ✅ 免责声明明确提示
- ✅ 系统托盘便捷操作
- ✅ 桌面通知即时反馈

---

## 📊 统计数据

| 指标 | 数据 |
|------|------|
| **新增文件** | 16个 |
| **修改文件** | 7个 |
| **新增代码行** | ~2300行 |
| **测试用例数** | 29个 |
| **测试覆盖率** | ~95% |
| **新增依赖** | 5个（测试相关） |

---

## 🚀 升级指南

### 从 v1.0.0 升级

#### 1. 安装新依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 开发依赖（可选）
pip install -r requirements-dev.txt

# 前端依赖（如有更新）
cd ../frontend
npm install
```

#### 2. 首次启动配置主密码

- 启动应用后会提示设置主密码
- 建议设置强密码并记住

#### 3. （可选）配置邮件告警

- 进入"设置" → "邮件告警"
- 填入SMTP配置
- 测试连接

#### 4. 运行测试验证

```bash
cd backend
./run_tests.sh  # Linux/macOS
run_tests.bat   # Windows
```

---

## 🐛 Bug修复

- ✅ 修复验证码弹窗未显示的问题
- ✅ 修复关闭窗口直接退出的问题（现在最小化到托盘）
- ✅ 修复邮件配置无法保存的问题

---

## 📚 文档更新

- ✅ 新增测试文档 `backend/tests/README.md`
- ✅ 更新项目完善总结报告
- ✅ 添加本更新日志

---

## ⚠️ 破坏性变更

**无破坏性变更**，完全向后兼容 v1.0.0

---

## 🙏 致谢

感谢所有贡献者和用户的反馈！

---

## 📞 问题反馈

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- 项目文档: /docs 目录

---

**下一版本预告 (v1.2.0)**:
- 🔜 插件系统
- 🔜 企业微信/钉钉支持
- 🔜 消息翻译功能
- 🔜 自动更新功能
