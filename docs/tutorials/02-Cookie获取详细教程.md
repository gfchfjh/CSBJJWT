# 📘 Cookie 获取详细教程

> 三种方法，总有一种适合您

---

## 🌟 方法一：Chrome扩展（最简单）

### 适用人群
- ✅ 所有人（最推荐）
- ✅ 不想折腾的用户

### 耗时：5秒

### 详细步骤

#### 第1步：安装扩展（仅首次需要）

1. **下载扩展**
   - 在KOOK转发系统中点击「下载Chrome扩展」
   - 或从GitHub下载：[扩展下载地址](https://github.com/gfchfjh/CSBJJWT/releases)

2. **解压文件**
   - 解压下载的 `kook-cookie-exporter.zip`
   - 记住解压位置

3. **安装到浏览器**
   - 打开Chrome，访问 `chrome://extensions/`
   - 开启右上角的「开发者模式」开关
   - 点击「加载已解压的扩展程序」
   - 选择刚才解压的文件夹
   - 完成！扩展图标会出现在工具栏

![安装步骤](../images/extension-install.png)

#### 第2步：导出Cookie

1. **打开KOOK网站**
   - 访问 https://www.kookapp.cn
   - 登录您的账号

2. **点击扩展图标**
   - 点击浏览器工具栏的扩展图标
   - 或点击拼图图标，找到「KOOK Cookie导出工具」

3. **导出**
   - 点击「导出Cookie到剪贴板」按钮
   - 等待提示「✅ Cookie已复制！」

![导出步骤](../images/extension-export.png)

4. **粘贴到转发系统**
   - 回到KOOK转发系统
   - 在登录页面选择「Cookie导入」
   - 按 `Ctrl+V` 粘贴
   - 点击「验证并登录」

✅ **完成！**

---

## 📋 方法二：手动复制Cookie（通用）

### 适用人群
- ✅ 无法安装扩展的用户
- ✅ 需要精确控制的用户

### 耗时：2-3分钟

### 详细步骤

#### 第1步：打开KOOK网站

1. 使用Chrome或Edge浏览器
2. 访问 https://www.kookapp.cn
3. 登录您的账号

#### 第2步：打开开发者工具

**方法A：键盘快捷键**
- Windows/Linux: `F12` 或 `Ctrl+Shift+I`
- macOS: `Cmd+Option+I`

**方法B：右键菜单**
- 页面空白处右键
- 选择「检查」或「审查元素」

![开发者工具](../images/devtools.png)

#### 第3步：查看Cookie

1. 在开发者工具顶部，点击「Application」标签
   - 如果看不到，点击 `>>` 按钮找到

2. 左侧展开「Cookies」
3. 选择「https://www.kookapp.cn」

![Cookie位置](../images/cookie-location.png)

#### 第4步：复制Cookie

**完整复制（推荐）**：

1. 选中所有Cookie行（点击第一个，Shift+点击最后一个）
2. 右键 → 「Copy」 → 「Copy all as JSON」
3. 粘贴到转发系统

**单个复制**：

如果浏览器不支持批量复制，请复制以下关键Cookie：
- `token`
- `session_id`
- `user_id`

格式：
```json
[
  {
    "name": "token",
    "value": "你的token值",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true
  }
]
```

---

## 🔐 方法三：账号密码登录

### 适用人群
- ✅ 不想处理Cookie的用户
- ✅ 首次使用的用户

### 耗时：1-2分钟（如需验证码则更久）

### 详细步骤

1. 在转发系统登录页选择「账号密码登录」
2. 输入KOOK邮箱
3. 输入密码
4. 点击「登录」

⚠️ **注意**：
- 首次登录可能需要验证码
- 验证码会弹窗提示您手动输入
- 登录成功后会自动保存Cookie

---

## 🔍 Cookie 格式说明

### 支持的格式（10+种）

#### 1. JSON数组格式（推荐）✅
```json
[
  {"name": "token", "value": "xxx", "domain": ".kookapp.cn"},
  {"name": "session_id", "value": "yyy", "domain": ".kookapp.cn"}
]
```

#### 2. JSON对象格式✅
```json
{
  "token": "xxx",
  "session_id": "yyy"
}
```

#### 3. Netscape格式✅
```
# Netscape HTTP Cookie File
.kookapp.cn	TRUE	/	TRUE	1735000000	token	xxx
.kookapp.cn	TRUE	/	TRUE	1735000000	session_id	yyy
```

#### 4. 键值对格式✅
```
token=xxx; session_id=yyy; domain=.kookapp.cn
```

#### 5. HTTP Header格式✅
```
Cookie: token=xxx; session_id=yyy
```

### 自动格式识别

转发系统会自动识别以上所有格式，无需手动转换！

---

## ⚠️ 常见错误

### 错误1：「Cookie格式不正确」

**原因**：复制的内容不完整或格式错误

**解决**：
1. 重新复制，确保复制完整
2. 检查是否是纯文本（不要从Word等复制）
3. 尝试使用Chrome扩展方式

---

### 错误2：「Cookie已过期」

**原因**：Cookie有效期已过

**解决**：
1. 重新登录KOOK网页版
2. 重新导出Cookie
3. 立即使用

💡 **提示**：Cookie通常有效期为30天

---

### 错误3：「验证失败」

**原因**：
- Cookie不完整
- 账号已在其他设备登录
- KOOK服务器问题

**解决**：
1. 确保复制了所有必要的Cookie
2. 尝试退出其他设备的登录
3. 等待片刻后重试

---

## 🔒 安全提示

### Cookie的重要性

⚠️ **Cookie等同于账号密码！**

- 拥有Cookie = 可以操作您的账号
- 请勿泄露给他人
- 请勿在公共场合展示

### 保护您的Cookie

1. ✅ 仅在信任的设备上使用
2. ✅ 定期更改KOOK密码（会使旧Cookie失效）
3. ✅ 发现异常登录立即修改密码
4. ❌ 不要通过聊天软件发送Cookie
5. ❌ 不要截图包含Cookie的页面

---

## 📞 需要帮助？

### 遇到问题？

1. 查看 [常见问题FAQ](../FAQ.md)
2. 观看 [视频教程](../../video-tutorials/)
3. 提交 [GitHub Issue](https://github.com/gfchfjh/CSBJJWT/issues)

### 成功了！

恭喜您掌握了Cookie获取方法！

👉 下一步：[配置Discord Bot](03-Discord配置教程.md)

---

**文档版本**: v10.0.0  
**最后更新**: 2025-10-26  
**预计阅读时间**: 5分钟
