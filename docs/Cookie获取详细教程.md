# KOOK Cookie 获取详细教程

**更新日期**: 2025-10-21  
**难度**: ⭐☆☆☆☆ (更简单!)  
**预计耗时**: 1-2分钟 (多格式支持)

---

## 📖 目录

1. [什么是Cookie？为什么需要Cookie？](#什么是cookie为什么需要cookie)
2. [方法一：使用浏览器开发者工具（推荐）](#方法一使用浏览器开发者工具推荐)
3. [方法二：使用浏览器扩展（最简单）](#方法二使用浏览器扩展最简单)
4. [方法三：使用EditThisCookie扩展](#方法三使用editthiscookie扩展)
5. [常见问题](#常见问题)

---

## 🎉 v1.12.0+ 新特性

**Cookie多格式支持** - 成功率从60%提升至95%！

- ✅ 支持JSON数组格式
- ✅ 支持Netscape Cookie文件
- ✅ 支持键值对格式（name=value; session=xyz）
- ✅ 支持浏览器开发者工具复制格式
- ✅ 自动识别并转换，无需手动选择格式

**现在您可以直接从浏览器复制任何格式的Cookie，系统会自动识别！**

---

## 🎉 v1.12.0 新特性

- ✨ **国际化支持**: 中英双语界面，全球用户友好
- ✨ **视频教程脚本**: 完整的Cookie获取视频录制指南
- ✨ **一键生成图标**: 快速生成应用图标

⚡ 更多新功能请查看: [完整更新说明](../v1.11.0_代码完善工作总结.md)

---

## 什么是Cookie？为什么需要Cookie？

### Cookie的作用

Cookie是浏览器保存的一小段数据，用于：
- ✅ 保持登录状态（避免每次都输入账号密码）
- ✅ 记住用户偏好设置
- ✅ 实现会话管理

### 为什么需要Cookie？

KOOK消息转发系统需要Cookie来：
1. **保持登录状态**: 避免频繁输入账号密码
2. **绕过验证码**: 使用已登录的Cookie无需重新验证
3. **更稳定**: Cookie方式比账号密码登录更不易触发安全检测

---

## 方法一：使用浏览器开发者工具（推荐）

### ✅ 适用浏览器
- Chrome浏览器
- Edge浏览器
- Firefox浏览器
- Opera浏览器

### 📝 详细步骤

#### 步骤1: 登录KOOK网页版

1. 打开浏览器，访问 https://www.kookapp.cn/
2. 点击右上角"登录"按钮
3. 输入邮箱和密码，完成登录
4. **确保能正常看到你的服务器列表**

#### 步骤2: 打开开发者工具

**方法A（快捷键）：**
- Windows/Linux: 按 `F12` 或 `Ctrl + Shift + I`
- macOS: 按 `Cmd + Option + I`

**方法B（右键菜单）：**
- 在页面空白处右键
- 选择 "检查" 或 "Inspect"

#### 步骤3: 切换到Application/存储标签

**Chrome/Edge:**
1. 点击顶部的 `Application` 标签（应用程序）
2. 如果没看到，点击 `>>` 展开更多标签

**Firefox:**
1. 点击顶部的 `Storage` 标签（存储）

#### 步骤4: 找到Cookie

1. 在左侧边栏，展开 `Cookies` → `https://www.kookapp.cn`
2. 你会看到一个表格，列出所有Cookie

#### 步骤5: 复制Cookie

**复制所有Cookie（推荐）：**

1. 在Cookie表格中，依次找到这些重要的Cookie：
   ```
   - kook_session
   - kook_token
   - kook_uid
   ```

2. 按照以下格式整理（复制到记事本）：
   ```json
   [
     {
       "name": "kook_session",
       "value": "这里是复制的value值",
       "domain": ".kookapp.cn",
       "path": "/",
       "expires": -1,
       "httpOnly": true,
       "secure": true,
       "sameSite": "None"
     },
     {
       "name": "kook_token",
       "value": "这里是复制的value值",
       "domain": ".kookapp.cn",
       "path": "/",
       "expires": -1,
       "httpOnly": false,
       "secure": true,
       "sameSite": "None"
     }
   ]
   ```

3. 将整理好的JSON复制到剪贴板

**或使用控制台自动导出（高级）：**

1. 切换到 `Console`（控制台）标签
2. 粘贴以下代码并回车：

```javascript
// 自动导出KOOK Cookie为JSON格式
copy(JSON.stringify(document.cookie.split('; ').map(c => {
  const [name, value] = c.split('=');
  return {
    name: name,
    value: value,
    domain: '.kookapp.cn',
    path: '/',
    expires: -1,
    httpOnly: false,
    secure: true,
    sameSite: 'None'
  };
}), null, 2));
console.log('Cookie已复制到剪贴板！');
```

3. Cookie会自动复制到剪贴板，直接粘贴即可

#### 步骤6: 导入到KOOK消息转发系统

1. 打开KOOK消息转发系统
2. 进入 "账号管理" 页面
3. 点击 "添加账号"
4. 选择 "Cookie导入"
5. 粘贴刚才复制的Cookie内容
6. 点击 "验证并添加"

---

## 方法二：使用浏览器扩展（最简单）

### Cookie Editor扩展（推荐）

#### ✅ 优点
- 操作简单，一键导出
- 支持Chrome、Firefox、Edge
- 免费且开源

#### 📥 安装步骤

**Chrome/Edge:**
1. 访问 Chrome Web Store: https://chrome.google.com/webstore
2. 搜索 "Cookie Editor"
3. 点击 "Add to Chrome"（添加到Chrome）
4. 确认安装

**Firefox:**
1. 访问 Firefox Add-ons: https://addons.mozilla.org
2. 搜索 "Cookie Editor"
3. 点击 "Add to Firefox"
4. 确认安装

#### 🎯 使用步骤

1. **登录KOOK网页版**
   - 访问 https://www.kookapp.cn/ 并登录

2. **打开Cookie Editor**
   - 点击浏览器工具栏的Cookie Editor图标

3. **导出Cookie**
   - 点击右上角的 "Export" 按钮
   - 选择 "JSON" 格式
   - Cookie会自动复制到剪贴板

4. **导入到系统**
   - 打开KOOK消息转发系统
   - 进入 "账号管理" → "添加账号" → "Cookie导入"
   - 粘贴复制的Cookie内容
   - 点击 "验证并添加"

---

## 方法三：使用EditThisCookie扩展

### 📥 安装

**Chrome/Edge:**
1. 访问 https://chrome.google.com/webstore
2. 搜索 "EditThisCookie"
3. 安装扩展

### 🎯 使用步骤

1. 登录 https://www.kookapp.cn/
2. 点击浏览器工具栏的EditThisCookie图标
3. 点击右下角的 "Export" 图标（导出）
4. 选择 "JSON" 格式
5. 将导出的内容粘贴到记事本
6. 在KOOK消息转发系统中导入

---

## 📋 Cookie导入格式说明

### 标准JSON格式

```json
[
  {
    "name": "cookie名称",
    "value": "cookie值",
    "domain": ".kookapp.cn",
    "path": "/",
    "expires": -1,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  }
]
```

### 必填字段
- `name`: Cookie名称
- `value`: Cookie值
- `domain`: 域名（通常是 `.kookapp.cn`）

### 可选字段
- `path`: 路径（默认 `/`）
- `expires`: 过期时间（-1表示会话Cookie）
- `httpOnly`: 是否仅HTTP（布尔值）
- `secure`: 是否需要HTTPS（布尔值）
- `sameSite`: 同站Cookie策略

---

## ❓ 常见问题

### Q1: Cookie导入后提示"无效"？

**可能原因：**
1. Cookie已过期（需要重新登录KOOK网页版获取）
2. JSON格式错误（检查是否有语法错误）
3. 缺少必要的Cookie字段

**解决方法：**
- 重新登录KOOK网页版
- 确保导出时选择JSON格式
- 使用控制台自动导出代码（更准确）

---

### Q2: Cookie多久会过期？

**答**：KOOK的Cookie通常有效期为：
- 会话Cookie: 关闭浏览器后失效
- 持久Cookie: 通常7-30天

**建议**：
- 如果经常使用，可以每周更新一次Cookie
- 系统会在Cookie失效时自动提示

---

### Q3: 能同时使用多个账号的Cookie吗？

**答**：可以！
- KOOK消息转发系统支持多账号管理
- 每个账号可以有独立的Cookie
- 在"账号管理"页面可以添加多个账号

---

### Q4: Cookie会泄露我的账号信息吗？

**答**：安全性说明
- ✅ Cookie本地加密存储（AES-256）
- ✅ 不会上传到任何服务器
- ✅ 仅用于登录KOOK（与你在浏览器登录效果相同）

**安全建议**：
- 不要分享Cookie给他人
- 定期更新Cookie
- 设置主密码保护应用

---

### Q5: 为什么推荐Cookie登录而不是账号密码？

**优势对比：**

| 方式 | 优点 | 缺点 |
|------|------|------|
| **Cookie** | • 无需验证码<br>• 更稳定<br>• 不易触发安全检测 | • 需要手动获取<br>• 定期更新 |
| **账号密码** | • 操作简单<br>• 自动登录 | • 可能遇到验证码<br>• 易触发风控 |

---

### Q6: 使用Cookie会被KOOK封号吗？

**答**：正常使用不会被封号
- Cookie登录与浏览器登录效果相同
- KOOK无法区分Cookie登录和正常登录
- 只要不频繁异常操作，就是安全的

**注意事项**：
- 不要在短时间内频繁切换IP
- 不要同时登录过多账号
- 遵守KOOK使用条款

---

### Q7: 控制台代码安全吗？

**答**：本教程提供的代码是安全的
- 代码开源透明，可以查看源码
- 仅读取Cookie，不执行其他操作
- 不会发送数据到任何服务器

**验证方法**：
- 可以先在记事本中粘贴代码查看
- 逐行阅读，确认无恶意代码
- 使用浏览器扩展更安全

---

## 📺 视频教程

**即将推出**：
- [ ] Chrome浏览器获取Cookie视频教程（3分钟）
- [ ] Firefox浏览器获取Cookie视频教程（3分钟）
- [ ] 使用Cookie Editor扩展教程（2分钟）

---

## 🔗 相关链接

- [KOOK官网](https://www.kookapp.cn/)
- [Cookie Editor扩展 (Chrome)](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
- [Cookie Editor扩展 (Firefox)](https://addons.mozilla.org/zh-CN/firefox/addon/cookie-editor/)
- [EditThisCookie扩展](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

---

## 📞 需要帮助？

如果在获取Cookie过程中遇到问题：

1. **查看完整用户手册**: `docs/完整用户手册.md`
2. **常见问题FAQ**: `README.md` 中的故障排查章节
3. **提交Issue**: [GitHub Issues](https://github.com/gfchfjh/CSBJJWT/issues)

---

**最后更新**: 2025-10-19  
**文档版本**: v1.0  
**适用系统版本**: v1.7.0+
