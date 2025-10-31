# Chrome扩展Cookie导出完整指南

**版本**: v3.1.0  
**更新时间**: 2025-10-31  
**适用于**: KOOK消息转发系统 v18.0.0+

---

## 📖 目录

1. [功能介绍](#功能介绍)
2. [安装方法](#安装方法)
3. [使用教程](#使用教程)
4. [三种导出方式](#三种导出方式)
5. [常见问题](#常见问题)
6. [故障排查](#故障排查)

---

## 功能介绍

KOOK Cookie导出助手是一个Chrome扩展程序，可以帮助您快速、安全地导出KOOK网站的Cookie，并自动导入到本地转发系统。

### ✨ 核心功能

- **🚀 一键自动导入** - 检测到本地系统在线时，自动发送Cookie
- **📋 智能剪贴板** - 系统离线时自动复制到剪贴板
- **💾 文件下载** - 导出为JSON文件，永久保存
- **📊 实时状态** - 显示Cookie数量和系统连接状态
- **📜 导出历史** - 记录最近10次导出操作
- **⌨️ 快捷键** - `Ctrl+Shift+K`（Mac: `Cmd+Shift+K`）快速导出

### 为什么需要这个扩展？

1. **简化操作** - 无需手动查找和复制Cookie
2. **准确性高** - 自动提取所有必要的Cookie字段
3. **安全可靠** - Cookie不经过任何第三方服务器
4. **多种方式** - 根据情况选择最合适的导出方式

---

## 安装方法

### 方法一：开发者模式安装（推荐）

#### 步骤1：下载扩展文件

从项目仓库下载或复制`chrome-extension`文件夹到本地：

```
KOOK-Forwarder/
└── chrome-extension/
    ├── manifest.json
    ├── popup-complete.html
    ├── popup-complete.js
    ├── background-optimized.js
    └── icons/
        ├── icon-16.png
        ├── icon-48.png
        └── icon-128.png
```

#### 步骤2：打开Chrome扩展页面

1. 打开Chrome浏览器
2. 在地址栏输入：`chrome://extensions/`
3. 按回车进入扩展管理页面

![Chrome扩展页面](https://via.placeholder.com/800x400/667eea/ffffff?text=Chrome+Extensions)

#### 步骤3：启用开发者模式

1. 在页面右上角找到"开发者模式"开关
2. 点击开启开发者模式

![开发者模式](https://via.placeholder.com/400x200/764ba2/ffffff?text=Developer+Mode+ON)

#### 步骤4：加载扩展

1. 点击左上角的"加载已解压的扩展程序"按钮
2. 在文件选择对话框中，选择`chrome-extension`文件夹
3. 点击"选择文件夹"

![加载扩展](https://via.placeholder.com/600x300/52c41a/ffffff?text=Load+Unpacked)

#### 步骤5：验证安装

1. 扩展列表中应该出现"KOOK Cookie自动导入助手"
2. 确保扩展处于**启用**状态（蓝色开关）
3. Chrome工具栏右上角应该出现扩展图标 🍪

![安装成功](https://via.placeholder.com/400x200/1890ff/ffffff?text=Installation+Success)

### 方法二：打包安装（可选）

#### 步骤1：打包扩展

1. 在`chrome://extensions/`页面
2. 点击"打包扩展程序"
3. 选择`chrome-extension`文件夹
4. 点击"打包扩展程序"
5. 会生成`.crx`文件和`.pem`文件

#### 步骤2：安装打包文件

1. 将`.crx`文件拖拽到Chrome窗口
2. 点击"添加扩展程序"确认安装

> **注意**: 非Chrome Web Store安装的扩展，Chrome可能会显示警告，这是正常现象。

---

## 使用教程

### 第一次使用

#### 1. 登录KOOK网站

1. 打开Chrome浏览器
2. 访问 [https://www.kookapp.cn](https://www.kookapp.cn)
3. 使用您的账号登录KOOK

> **提示**: 必须先登录KOOK，扩展才能检测到Cookie

#### 2. 启动本地转发系统（可选）

如果您希望使用"一键自动导入"功能，需要先启动本地系统：

- **Windows**: 双击 `start.bat`
- **Mac/Linux**: 运行 `./start.sh`
- 确保系统运行在 `http://localhost:9527`

#### 3. 打开扩展弹窗

点击Chrome工具栏右上角的扩展图标 🍪，或使用快捷键 `Ctrl+Shift+K`（Mac: `Cmd+Shift+K`）

![扩展弹窗](https://via.placeholder.com/400x500/667eea/ffffff?text=Extension+Popup)

#### 4. 查看状态

扩展会自动检测：
- ✅ 是否在KOOK网站
- ✅ 是否已登录（Cookie数量）
- ✅ 本地系统是否在线

![状态显示](https://via.placeholder.com/400x150/f8f9fa/333333?text=Status+Online)

---

## 三种导出方式

### 方式一：一键自动导入 🚀（推荐）

**适用场景**: 本地系统在线时

**步骤**:
1. 确保本地系统运行在 `http://localhost:9527`
2. 点击"一键导出并自动导入"按钮
3. 扩展会自动：
   - 提取所有Cookie
   - 发送到本地系统
   - 自动导入到系统数据库
4. 收到"✅ Cookie已自动导入到系统！"提示

**优点**:
- ✅ 全自动，无需任何手动操作
- ✅ 最快速，3秒内完成
- ✅ 最准确，避免人为错误

**注意事项**:
- 本地系统必须运行
- 需要允许浏览器访问 `localhost:9527`

---

### 方式二：复制到剪贴板 📋

**适用场景**: 本地系统离线或希望手动粘贴

**步骤**:
1. 点击"复制到剪贴板"按钮
2. Cookie数据已复制为JSON格式
3. 在本地系统中：
   - 进入"账号管理"页面
   - 点击"添加账号"
   - 选择"Cookie导入"
   - 粘贴（`Ctrl+V`）到文本框
   - 点击"验证并添加"

**优点**:
- ✅ 不依赖本地系统在线
- ✅ 可以预览Cookie内容
- ✅ 灵活性高

**注意事项**:
- 需要手动操作粘贴
- 剪贴板内容可能被其他程序覆盖

---

### 方式三：下载为JSON文件 💾

**适用场景**: 需要永久保存或批量处理

**步骤**:
1. 点击"下载为JSON文件"按钮
2. 选择保存位置和文件名
3. 文件格式示例：
```json
{
  "domain": ".kookapp.cn",
  "exported_at": "2025-10-31T10:30:00.000Z",
  "cookies": [
    {
      "name": "token",
      "value": "xxxxx",
      "domain": ".kookapp.cn",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "expirationDate": 1730000000
    },
    ...
  ]
}
```
4. 在本地系统中：
   - 进入"账号管理"页面
   - 点击"添加账号"
   - 选择"Cookie导入"
   - 点击"上传JSON文件"
   - 选择刚才下载的文件

**优点**:
- ✅ 永久保存，不会丢失
- ✅ 可以多次使用
- ✅ 方便备份和分享（注意安全）

**注意事项**:
- 文件包含敏感信息，妥善保管
- 不要上传到公开平台

---

## 常见问题

### Q1: 扩展显示"未在KOOK网站"？

**原因**: 当前标签页不是KOOK网站

**解决**:
1. 确保访问 `www.kookapp.cn`
2. 不要在其他网站使用扩展
3. 刷新KOOK页面后重试

---

### Q2: 显示"未检测到Cookie"？

**原因**: 可能未登录或Cookie已过期

**解决**:
1. 退出KOOK账号
2. 重新登录（记住我）
3. 刷新扩展弹窗
4. 如果仍然失败，清除浏览器缓存后重试

---

### Q3: 自动导入失败，显示"本地系统离线"？

**原因**: 本地转发系统未启动或端口不对

**解决**:
1. 检查本地系统是否运行：
   - 打开 `http://localhost:9527` 查看是否能访问
2. 检查端口是否被占用
3. 尝试重启本地系统
4. 如果无法解决，使用"复制到剪贴板"方式

---

### Q4: 点击扩展图标没有反应？

**原因**: 扩展未正确加载或权限不足

**解决**:
1. 访问 `chrome://extensions/`
2. 找到扩展，点击"刷新"按钮
3. 如果仍然无效，移除扩展后重新安装
4. 确保授予了所有必要权限

---

### Q5: 导入后账号显示"离线"？

**原因**: Cookie可能已过期或不完整

**解决**:
1. 重新登录KOOK网站
2. 重新导出Cookie
3. 检查KOOK账号是否被限制
4. 尝试使用账号密码登录方式

---

## 故障排查

### 步骤1：检查扩展状态

1. 访问 `chrome://extensions/`
2. 确认扩展已启用
3. 查看是否有错误提示

### 步骤2：检查网络权限

1. 点击扩展详情
2. 确保"网站访问权限"包含：
   - `https://*.kookapp.cn/*`
   - `http://localhost:9527/*`

### 步骤3：查看控制台日志

1. 右键点击扩展图标
2. 选择"检查弹出窗口"
3. 查看Console标签页的错误信息

### 步骤4：重置扩展

1. 在扩展管理页面
2. 点击扩展卡片上的"移除"
3. 重新安装扩展
4. 重新访问KOOK网站并登录

### 步骤5：检查本地系统

1. 打开 `http://localhost:9527/docs`
2. 查看API文档是否能访问
3. 测试 `/api/health` 端点
4. 查看系统日志了解详细错误

---

## 安全提示

### ⚠️ 重要安全建议

1. **不要分享Cookie文件**
   - Cookie包含您的登录凭证
   - 泄露后他人可以登录您的账号

2. **定期更换密码**
   - 建议每月更换一次KOOK密码
   - 更换后需要重新导出Cookie

3. **及时删除导出文件**
   - 使用完JSON文件后立即删除
   - 不要保存在云盘或公共电脑

4. **使用测试账号**
   - 建议使用专门的测试账号
   - 避免使用主账号进行转发

5. **监控账号活动**
   - 定期检查KOOK账号的登录历史
   - 发现异常立即修改密码

---

## 技术支持

### 问题反馈

如果遇到问题，可以通过以下方式获取帮助：

1. **GitHub Issues**: [提交问题](https://github.com/gfchfjh/CSBJJWT/issues)
2. **查看文档**: `docs/` 目录下的其他教程
3. **查看日志**: Chrome控制台和系统日志

### 相关文档

- [KOOK Cookie获取教程](./如何获取KOOK_Cookie.md)
- [账号管理指南](../USER_MANUAL.md#账号管理)
- [常见问题FAQ](./FAQ-常见问题.md)

---

## 更新日志

### v3.1.0 (2025-10-31)

- ✅ 全新UI设计，更加美观
- ✅ 新增三种导出方式
- ✅ 添加导出历史记录
- ✅ 优化状态检测逻辑
- ✅ 改进错误提示信息
- ✅ 支持快捷键导出

### v3.0.0 (2025-10-25)

- ✅ 支持Manifest V3
- ✅ 自动检测系统在线状态
- ✅ Cookie完整性验证
- ✅ 优化性能和稳定性

---

## 附录：JSON文件格式说明

导出的JSON文件结构：

```json
{
  "domain": ".kookapp.cn",          // Cookie所属域名
  "exported_at": "2025-10-31T10:30:00.000Z",  // 导出时间
  "cookies": [                      // Cookie数组
    {
      "name": "token",              // Cookie名称
      "value": "xxxxxx",            // Cookie值
      "domain": ".kookapp.cn",      // 域名
      "path": "/",                  // 路径
      "secure": true,               // 是否仅HTTPS
      "httpOnly": true,             // 是否HttpOnly
      "expirationDate": 1730000000  // 过期时间（Unix时间戳）
    }
  ]
}
```

### Cookie字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | ✅ | Cookie名称 |
| value | string | ✅ | Cookie值（敏感信息） |
| domain | string | ✅ | 所属域名 |
| path | string | ✅ | 有效路径 |
| secure | boolean | ❌ | 是否仅HTTPS传输 |
| httpOnly | boolean | ❌ | 是否禁止JS访问 |
| expirationDate | number | ❌ | 过期时间戳 |

---

**祝您使用愉快！** 🎉
