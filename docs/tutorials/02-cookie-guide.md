# 📙 如何获取KOOK Cookie（完整指南）

本教程将详细介绍如何获取KOOK Cookie并导入到转发系统中。

---

## 🎯 什么是Cookie？

Cookie是网站存储在您浏览器中的小型数据文件，用于记录登录状态。通过导入Cookie，我们的系统可以模拟您的登录状态，从而获取KOOK消息。

**优点**：
- ✅ 不需要输入密码
- ✅ 更安全（Cookie可以随时删除）
- ✅ 不会触发KOOK的登录验证
- ✅ 支持多账号

---

## 方法一：使用Chrome扩展（最简单）

这是最简单、最推荐的方法，只需3步即可完成！

### 第1步：安装Chrome扩展

1. 打开Chrome浏览器
2. 访问扩展管理页面：在地址栏输入 `chrome://extensions/`
3. 开启右上角的"开发者模式"

   ![开启开发者模式](../screenshots/chrome-dev-mode.png)

4. 点击左上角的"加载已解压的扩展程序"
5. 选择软件安装目录下的 `chrome-extension` 文件夹

   ![加载扩展](../screenshots/chrome-load-extension.png)

6. 安装成功后，您会看到扩展图标出现在浏览器右上角

   ![扩展图标](../screenshots/chrome-extension-icon.png)

### 第2步：登录KOOK网页版

1. 打开新标签页，访问：https://www.kookapp.cn
2. 使用您的账号和密码正常登录

   ![KOOK网页登录](../screenshots/kook-web-login.png)

3. 登录成功后，您会看到KOOK的主界面

   ![KOOK主界面](../screenshots/kook-main-interface.png)

### 第3步：一键导出Cookie

1. 确保KOOK转发系统正在运行
2. 点击浏览器右上角的扩展图标（绿色的KOOK图标）
3. Cookie会自动发送到转发系统
4. 看到通知"✅ Cookie已自动导入！"即成功

   ![Cookie导出成功](../screenshots/cookie-auto-import.png)

**快捷键**：您也可以按 `Ctrl+Shift+K`（Mac: `Cmd+Shift+K`）快速导出Cookie

---

## 方法二：手动复制Cookie（适合高级用户）

如果Chrome扩展方法不可用，您可以手动复制Cookie。

### 第1步：打开开发者工具

1. 在KOOK网页版登录后，按 `F12` 打开开发者工具
2. 切换到"Application"（应用程序）标签
   - 如果是中文版：切换到"应用"标签

   ![开发者工具](../screenshots/devtools-application.png)

### 第2步：查找Cookie

1. 在左侧菜单找到"Storage" → "Cookies"
2. 点击 `https://www.kookapp.cn`
3. 右侧会显示所有Cookie

   ![Cookie列表](../screenshots/devtools-cookies.png)

### 第3步：导出Cookie

**选项A：使用Console导出（推荐）**

1. 切换到"Console"（控制台）标签
2. 复制粘贴以下代码，按回车：

   ```javascript
   // 导出Cookie为JSON格式
   (function() {
     const cookies = document.cookie.split('; ').map(c => {
       const [name, value] = c.split('=');
       return {
         name: name,
         value: value,
         domain: '.kookapp.cn',
         path: '/'
       };
     });
     
     const json = JSON.stringify(cookies, null, 2);
     console.log('Cookie JSON:');
     console.log(json);
     
     // 复制到剪贴板
     const textarea = document.createElement('textarea');
     textarea.value = json;
     document.body.appendChild(textarea);
     textarea.select();
     document.execCommand('copy');
     document.body.removeChild(textarea);
     
     console.log('✅ Cookie已复制到剪贴板！');
   })();
   ```

3. 看到"✅ Cookie已复制到剪贴板！"提示
4. Cookie JSON已自动复制，准备粘贴到软件中

   ![Console导出](../screenshots/console-export.png)

**选项B：手动复制每个Cookie**

1. 在Cookie列表中，逐个复制重要的Cookie：
   - `token`
   - `session`
   - `user_id`
   - `refresh_token`

2. 按照以下格式组织：
   ```json
   [
     {
       "name": "token",
       "value": "xxxxxx",
       "domain": ".kookapp.cn"
     },
     {
       "name": "session",
       "value": "xxxxxx",
       "domain": ".kookapp.cn"
     }
   ]
   ```

### 第4步：导入到软件

1. 打开KOOK转发系统
2. 进入"账号管理"页面
3. 点击"添加账号"
4. 选择"Cookie导入"标签
5. 将复制的Cookie JSON粘贴到文本框
6. 点击"验证并导入"

   ![手动导入Cookie](../screenshots/manual-cookie-import.png)

---

## 方法三：从EditThisCookie扩展导出

如果您已安装EditThisCookie扩展，可以使用它导出Cookie。

### 第1步：安装EditThisCookie

1. 访问Chrome网上应用店
2. 搜索"EditThisCookie"
3. 点击"添加到Chrome"

   ![EditThisCookie安装](../screenshots/editthiscookie-install.png)

### 第2步：导出Cookie

1. 登录KOOK网页版
2. 点击EditThisCookie扩展图标
3. 点击"导出"按钮（Export图标）
4. Cookie会以JSON格式复制到剪贴板

   ![EditThisCookie导出](../screenshots/editthiscookie-export.png)

### 第3步：导入到软件

1. 打开KOOK转发系统
2. 进入"账号管理" → "添加账号"
3. 选择"Cookie导入"标签
4. 粘贴Cookie JSON
5. 点击"验证并导入"

---

## 🔍 Cookie验证

导入Cookie后，系统会自动验证：

### 成功提示

```
✅ Cookie验证成功！
账号已导入到KOOK转发系统
用户名: 您的用户名
用户ID: 123456789
```

![Cookie验证成功](../screenshots/cookie-validation-success.png)

### 失败提示

如果看到以下错误，请检查：

```
❌ Cookie验证失败
原因：Cookie已过期或格式错误
```

**解决方法**：
1. 重新登录KOOK网页版
2. 重新导出Cookie
3. 确保Cookie包含必要的字段（token、session）

![Cookie验证失败](../screenshots/cookie-validation-fail.png)

---

## ⚠️ 安全提示

### Cookie的安全性

- ✅ Cookie存储在本地数据库中，经过加密
- ✅ Cookie只用于连接KOOK，不会发送到其他地方
- ✅ 您可以随时删除Cookie

### 保护您的Cookie

1. **不要分享Cookie给他人**
   - Cookie = 登录凭证，分享Cookie等同于分享密码

2. **定期更换Cookie**
   - 如果怀疑Cookie泄露，立即在KOOK网页版退出登录
   - 重新登录后导出新的Cookie

3. **使用Cookie过期机制**
   - KOOK的Cookie通常会在一段时间后自动过期
   - 系统会提示您重新导入

---

## ❓ 常见问题

### Q1: Cookie导入后显示"已过期"？

**A**: Cookie确实已过期，需要重新导出：
1. 访问KOOK网页版
2. 退出登录
3. 重新登录
4. 导出新的Cookie

### Q2: 扩展显示"无法连接到本地软件"？

**A**: 确保KOOK转发系统正在运行：
1. 检查软件是否启动
2. 检查端口9527是否被其他程序占用
3. 尝试重启软件

### Q3: 可以使用多个KOOK账号吗？

**A**: 可以！系统支持多账号：
1. 对每个账号重复上述步骤
2. 在"账号管理"页面可以看到所有账号
3. 每个账号独立监听各自的服务器

### Q4: Cookie会被发送到互联网吗？

**A**: 不会！Cookie仅用于本地：
1. Cookie存储在您的电脑上
2. 仅用于连接KOOK服务器
3. 不会发送给第三方

---

## 📺 视频教程

点击观看详细的视频教程：

- [📺 Chrome扩展安装和使用（2分钟）](../videos/chrome-extension-tutorial.mp4)
- [📺 手动复制Cookie教程（5分钟）](../videos/manual-cookie-tutorial.mp4)

---

## 🎓 总结

**推荐方法排序**：
1. Chrome扩展自动导出（最简单，推荐）
2. 开发者工具Console导出
3. EditThisCookie扩展
4. 手动复制Cookie

**下一步学习**：
- [📗 如何配置Discord Webhook](02-discord-webhook.md)
- [📕 如何配置Telegram Bot](03-telegram-bot.md)

---

有问题？查看 [常见问题FAQ](../faq.md) 或 [联系支持](../support.md)
