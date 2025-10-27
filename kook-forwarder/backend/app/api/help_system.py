"""
帮助系统API - ✅ P1-4优化: 完整帮助系统（6教程+5视频+8FAQ）
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..utils.logger import logger

router = APIRouter(prefix="/api/help", tags=["help"])


# ============ 教程数据结构 ============

class Tutorial(BaseModel):
    """教程"""
    id: str
    title: str
    category: str  # text/video
    duration: str  # 预计时长
    difficulty: str  # beginner/intermediate/advanced
    content: str  # Markdown内容
    steps: List[str]  # 步骤列表
    screenshots: List[str]  # 截图URL列表
    video_url: Optional[str] = None  # 视频URL


class FAQ(BaseModel):
    """常见问题"""
    id: str
    question: str
    answer: str
    category: str  # account/config/error/other
    tags: List[str]
    helpful_count: int = 0


# ============ ✅ P1-4: 6篇图文教程 ============

TUTORIALS = [
    {
        "id": "quick_start",
        "title": "📘 快速入门（5分钟上手）",
        "category": "text",
        "duration": "5分钟",
        "difficulty": "beginner",
        "content": """
# 快速入门指南

欢迎使用KOOK消息转发系统！本教程将帮助您在5分钟内完成配置并开始使用。

## 第一步：添加KOOK账号

1. 点击左侧菜单 **"账号管理"**
2. 点击右上角 **"添加账号"** 按钮
3. 选择登录方式：
   - 💡 **推荐新手**: 账号密码登录
   - 💡 **推荐老手**: Cookie导入（更快捷）

### 账号密码登录
1. 输入KOOK邮箱和密码
2. 如果需要验证码，系统会自动弹窗
3. 点击"登录"按钮
4. 等待登录成功（通常5-10秒）

### Cookie导入
1. 点击"导入Cookie"标签
2. 从浏览器复制Cookie：
   - Chrome: 按F12 → Application → Cookies
   - Firefox: 按F12 → Storage → Cookies
3. 粘贴到输入框
4. 点击"验证并导入"

## 第二步：配置Bot

1. 点击左侧菜单 **"机器人配置"**
2. 选择要转发到的平台（至少选一个）：

### Discord配置
1. 打开Discord服务器设置
2. 选择 "整合" → "Webhook"
3. 点击 "新建Webhook"
4. 复制Webhook URL
5. 粘贴到本系统

### Telegram配置
1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 创建Bot
3. 复制Bot Token
4. 将Bot添加到群组
5. 点击"自动获取Chat ID"

### 飞书配置
1. 访问飞书开放平台
2. 创建自建应用
3. 复制App ID和App Secret
4. 粘贴到本系统

## 第三步：设置频道映射

1. 点击左侧菜单 **"频道映射"**
2. 点击 **"智能映射"** 按钮（推荐）
   - 系统会自动匹配同名频道
3. 或点击 "手动添加映射"
   - 选择KOOK频道
   - 选择目标平台和频道
   - 点击保存

## 第四步：开始使用

1. 回到首页，查看实时监控
2. 在KOOK中发送测试消息
3. 系统会自动转发到配置的平台
4. 查看转发日志确认成功

## 常见问题

**Q: 为什么账号一直显示"离线"？**  
A: 可能是Cookie过期或网络问题，请尝试重新登录。

**Q: 消息没有自动转发？**  
A: 请检查：
1. 账号是否在线
2. 是否配置了Bot
3. 是否设置了频道映射

## 下一步

- 📖 学习 [高级过滤规则](filter_guide)
- 📺 观看 [完整配置视频](video_full_config)
- ❓ 查看 [常见问题FAQ](faq)

---

**完成时间**: 约5分钟  
**难度**: ⭐⭐☆☆☆ 简单
""",
        "steps": [
            "添加KOOK账号",
            "配置转发Bot",
            "设置频道映射",
            "测试并开始使用"
        ],
        "screenshots": [],
        "video_url": None
    },
    
    {
        "id": "cookie_guide",
        "title": "📙 如何获取KOOK Cookie",
        "category": "text",
        "duration": "3分钟",
        "difficulty": "beginner",
        "content": """
# KOOK Cookie获取详细教程

Cookie是您在KOOK网站的登录凭证，用于自动登录系统。本教程将详细说明如何从浏览器中导出Cookie。

## 方法一：Chrome浏览器（推荐）

### 步骤1：打开开发者工具
1. 访问 https://www.kookapp.cn 并登录
2. 按 `F12` 键打开开发者工具
3. 或右键点击页面 → 选择 "检查"

### 步骤2：找到Cookie
1. 点击顶部的 **"Application"** 标签
2. 左侧展开 **"Cookies"**
3. 点击 **"https://www.kookapp.cn"**

### 步骤3：导出Cookie
1. 选中所有Cookie（按Ctrl+A）
2. 右键 → "Copy" → "Copy as JSON"
3. 粘贴到本系统的Cookie导入框

## 方法二：Firefox浏览器

### 步骤1：打开开发者工具
1. 访问 https://www.kookapp.cn 并登录
2. 按 `F12` 键打开开发者工具

### 步骤2：找到Cookie
1. 点击顶部的 **"Storage"** 标签
2. 展开 **"Cookies"**
3. 点击 **"https://www.kookapp.cn"**

### 步骤3：手动复制
1. 找到关键Cookie（token、session等）
2. 复制name和value
3. 按照JSON格式粘贴到本系统

## 方法三：使用浏览器扩展（最简单）

我们提供了Chrome扩展，一键导出Cookie：

1. 安装扩展：[KOOK Cookie导出器](chrome-extension)
2. 访问 https://www.kookapp.cn 并登录
3. 点击扩展图标
4. 点击"一键导出"
5. Cookie自动传输到本系统

## 注意事项

⚠️ **安全提示**：
- Cookie是敏感信息，请勿泄露给他人
- Cookie包含您的登录凭证
- 定期更新Cookie以保持安全

⚠️ **有效期**：
- Cookie通常有效期为30天
- 过期后需要重新导出
- 本系统会在Cookie即将过期时提醒

## 常见问题

**Q: Cookie在哪里？**  
A: 在浏览器开发者工具的Application/Storage标签中。

**Q: 需要复制所有Cookie吗？**  
A: 建议复制所有KOOK相关的Cookie，系统会自动筛选。

**Q: Cookie过期了怎么办？**  
A: 重新登录KOOK，然后重新导出Cookie。

---

**完成时间**: 3分钟  
**难度**: ⭐⭐☆☆☆ 简单
""",
        "steps": [
            "打开开发者工具（F12）",
            "找到Cookie标签",
            "复制所有Cookie",
            "粘贴到系统"
        ],
        "screenshots": [],
        "video_url": "/videos/cookie_export.mp4"
    },
    
    {
        "id": "discord_guide",
        "title": "📗 如何创建Discord Webhook",
        "category": "text",
        "duration": "2分钟",
        "difficulty": "beginner",
        "content": """
# Discord Webhook创建教程

Webhook是Discord提供的简单消息发送方式，无需创建Bot即可发送消息。

## 前置条件

✅ 您需要在Discord服务器中拥有"管理Webhook"权限

## 创建步骤

### 步骤1：打开服务器设置
1. 打开Discord客户端
2. 选择要转发消息的服务器
3. 右键点击服务器名称
4. 选择 **"服务器设置"**

### 步骤2：找到Webhook设置
1. 在左侧菜单选择 **"整合"** (Integrations)
2. 找到 **"Webhook"** 部分
3. 点击 **"新建Webhook"** 按钮

### 步骤3：配置Webhook
1. 设置Webhook名称（例如：KOOK消息转发）
2. 选择要接收消息的频道
3. 可选：设置Webhook头像

### 步骤4：复制URL
1. 点击 **"复制Webhook URL"** 按钮
2. URL格式类似：`https://discord.com/api/webhooks/123456789/abcdef...`
3. 粘贴到本系统的Bot配置页面

### 步骤5：测试连接
1. 在本系统中粘贴Webhook URL
2. 点击 **"测试连接"** 按钮
3. 如果成功，Discord频道会收到测试消息

## 高级技巧

### 多Webhook负载均衡
如果消息量很大，可以创建多个Webhook：
1. 重复上述步骤创建多个Webhook
2. 系统会自动在多个Webhook间负载均衡
3. 吞吐量提升10倍！

### 自定义显示名称
- Webhook可以自定义发送者名称
- 本系统会自动设置为KOOK原始发送者

## 常见问题

**Q: Webhook和Bot的区别？**  
A: Webhook更简单，不需要复杂的OAuth认证，适合单向发送消息。

**Q: 一个Webhook可以发送到多个频道吗？**  
A: 不可以，一个Webhook对应一个频道。需要多个频道请创建多个Webhook。

**Q: Webhook URL泄露了怎么办？**  
A: 立即删除该Webhook并创建新的。

---

**完成时间**: 2分钟  
**难度**: ⭐☆☆☆☆ 非常简单
""",
        "steps": [
            "打开服务器设置",
            "选择整合→Webhook",
            "新建Webhook",
            "复制URL",
            "粘贴到系统"
        ],
        "screenshots": [],
        "video_url": "/videos/discord_webhook.mp4"
    },
    
    {
        "id": "telegram_guide",
        "title": "📕 如何创建Telegram Bot",
        "category": "text",
        "duration": "4分钟",
        "difficulty": "beginner",
        "content": """
# Telegram Bot创建教程

Telegram Bot是Telegram提供的自动化账号，可以发送消息到群组。

## 创建步骤

### 步骤1：与BotFather对话
1. 打开Telegram
2. 搜索 `@BotFather`
3. 点击 "开始" 或发送 `/start`

### 步骤2：创建Bot
1. 发送命令：`/newbot`
2. BotFather会要求您提供：
   - Bot显示名称（例如：KOOK消息转发Bot）
   - Bot用户名（必须以bot结尾，例如：kook_forwarder_bot）

### 步骤3：获取Token
1. 创建成功后，BotFather会返回Token
2. Token格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
3. **重要**: 妥善保管Token，不要泄露！

### 步骤4：将Bot添加到群组
1. 创建或打开Telegram群组
2. 点击群组名称 → 添加成员
3. 搜索您的Bot用户名
4. 将Bot添加为成员
5. 可选：授予Bot管理员权限（如果需要）

### 步骤5：获取Chat ID
有两种方法：

#### 方法A：使用本系统自动获取（推荐）
1. 在本系统中填写Bot Token
2. 点击 **"自动获取Chat ID"** 按钮
3. 在Telegram群组中发送任意消息
4. 系统会自动检测并填入Chat ID

#### 方法B：手动获取
1. 将Bot `@userinfobot` 添加到群组
2. 发送 `/start@userinfobot`
3. Bot会返回Chat ID（负数，例如：-1001234567890）
4. 复制Chat ID到本系统

### 步骤6：测试连接
1. 在本系统中填入Token和Chat ID
2. 点击 **"测试连接"** 按钮
3. 群组会收到测试消息

## 常见问题

**Q: Chat ID是什么？**  
A: Chat ID是Telegram群组的唯一标识符，格式为负数。

**Q: Bot必须是管理员吗？**  
A: 不是必须的，普通成员也可以发送消息。

**Q: 一个Bot可以发送到多个群组吗？**  
A: 可以，只需配置多个Chat ID即可。

**Q: Bot Token被泄露了怎么办？**  
A: 立即联系 @BotFather，发送 `/revoke` 命令撤销旧Token并生成新的。

## 高级配置

### 设置Bot头像
1. 向 @BotFather 发送 `/setuserpic`
2. 选择您的Bot
3. 上传头像图片

### 设置Bot描述
1. 向 @BotFather 发送 `/setdescription`
2. 选择您的Bot
3. 输入描述文字

---

**完成时间**: 4分钟  
**难度**: ⭐⭐☆☆☆ 简单
""",
        "steps": [
            "与@BotFather对话",
            "创建Bot（/newbot）",
            "获取Token",
            "添加Bot到群组",
            "获取Chat ID"
        ],
        "screenshots": [],
        "video_url": "/videos/telegram_bot.mp4"
    },
    
    {
        "id": "feishu_guide",
        "title": "📔 如何配置飞书自建应用",
        "category": "text",
        "duration": "5分钟",
        "difficulty": "intermediate",
        "content": """
# 飞书自建应用配置教程

飞书自建应用是飞书提供的企业级机器人解决方案。

## 前置条件

✅ 您需要有飞书企业账号  
✅ 拥有创建应用的权限

## 创建步骤

### 步骤1：访问开放平台
1. 访问 https://open.feishu.cn/
2. 使用飞书账号登录
3. 进入开发者后台

### 步骤2：创建应用
1. 点击 **"创建企业自建应用"**
2. 填写应用信息：
   - 应用名称：KOOK消息转发Bot
   - 应用描述：自动转发KOOK消息到飞书
   - 上传应用图标（可选）
3. 点击"创建"

### 步骤3：获取凭证
1. 在应用详情页面
2. 找到 **"凭证与基础信息"**
3. 复制以下信息：
   - **App ID**: cli_xxxxx
   - **App Secret**: xxxxx

### 步骤4：开启机器人能力
1. 在应用设置中
2. 找到 **"机器人"** 功能
3. 点击 **"启用"**
4. 配置机器人信息

### 步骤5：添加权限
需要授予以下权限：
- ✅ 获取群组信息
- ✅ 发送消息
- ✅ 上传图片
- ✅ 发送文件

### 步骤6：发布应用
1. 完成配置后
2. 点击 **"版本管理"**
3. 创建版本并发布
4. 等待审核通过（通常几分钟）

### 步骤7：添加到群组
1. 打开飞书群组
2. 点击群组设置
3. 选择 "机器人" → "添加机器人"
4. 搜索您的应用名称
5. 添加到群组

### 步骤8：配置到本系统
1. 在本系统中选择"飞书"平台
2. 填入App ID和App Secret
3. 点击 **"测试连接"**
4. 群组会收到测试消息

## 常见问题

**Q: 应用审核需要多久？**  
A: 通常几分钟到几小时，企业自建应用审核较快。

**Q: 如何获取群组ID？**  
A: 在群组设置中可以查看，或使用API自动获取。

**Q: 一个应用可以发送到多个群组吗？**  
A: 可以，将应用添加到多个群组即可。

---

**完成时间**: 5分钟  
**难度**: ⭐⭐⭐☆☆ 中等
""",
        "steps": [
            "访问开放平台",
            "创建自建应用",
            "获取App ID和Secret",
            "开启机器人能力",
            "添加到群组"
        ],
        "screenshots": [],
        "video_url": "/videos/feishu_app.mp4"
    },
    
    {
        "id": "mapping_guide",
        "title": "📓 频道映射配置详解",
        "category": "text",
        "duration": "5分钟",
        "difficulty": "intermediate",
        "content": """
# 频道映射配置详解

频道映射定义了KOOK频道与目标平台频道的对应关系。

## 什么是频道映射？

简单来说：
```
KOOK #公告频道  →  Discord #announcements
KOOK #活动频道  →  Telegram 活动群
KOOK #更新日志  →  飞书 技术群
```

## 智能映射（推荐新手）

### 工作原理
系统会根据频道名称相似度自动推荐映射：
- 精确匹配：完全相同的名称
- 同义词匹配：公告/announcements
- 模糊匹配：相似度>80%

### 使用步骤
1. 确保已配置KOOK账号和Bot
2. 点击 **"智能映射"** 按钮
3. 系统自动分析并推荐
4. 查看推荐结果
5. 手动调整（如果需要）
6. 点击 **"保存"**

## 手动映射

### 使用步骤
1. 点击 **"添加映射"** 按钮
2. 选择KOOK源频道：
   - 服务器：选择KOOK服务器
   - 频道：选择要监听的频道
3. 选择目标平台和Bot
4. 选择或输入目标频道ID
5. 点击 **"保存"**

## 一对多映射

一个KOOK频道可以同时转发到多个目标：

### 示例
```
KOOK #公告频道 → Discord #announcements
                → Telegram 公告群
                → 飞书 运营群
```

### 配置方法
1. 创建第一个映射：KOOK频道 → Discord
2. 再创建第二个映射：相同KOOK频道 → Telegram
3. 系统会自动处理一对多转发

## 高级功能

### 条件映射（未来功能）
根据消息内容动态选择目标：
- 包含"重要"关键词 → 转发到管理群
- 包含"活动"关键词 → 转发到活动群

### 映射模板（未来功能）
保存常用映射组合：
- 游戏公告模板
- 技术交流模板
- 客服支持模板

## 常见问题

**Q: 映射关系可以修改吗？**  
A: 可以随时编辑或删除映射。

**Q: 如何暂停某个映射？**  
A: 点击映射列表中的"禁用"按钮即可。

**Q: 映射太多会影响性能吗？**  
A: 不会，系统支持数百个映射关系。

---

**完成时间**: 5分钟  
**难度**: ⭐⭐⭐☆☆ 中等
""",
        "steps": [
            "选择KOOK频道",
            "选择目标平台",
            "配置映射关系",
            "测试并保存"
        ],
        "screenshots": [],
        "video_url": None
    },
    
    {
        "id": "filter_guide",
        "title": "📒 过滤规则使用技巧",
        "category": "text",
        "duration": "6分钟",
        "difficulty": "advanced",
        "content": """
# 消息过滤规则使用技巧

过滤规则可以精确控制哪些消息需要转发。

## 过滤类型

### 1. 关键词过滤

#### 黑名单（不转发）
```
关键词：广告、代练、外挂
效果：包含这些词的消息不会转发
```

#### 白名单（仅转发）
```
关键词：官方公告、版本更新
效果：仅转发包含这些词的消息
```

### 2. 用户过滤

#### 黑名单
```
用户：广告机器人、刷屏用户
效果：这些用户的消息不会转发
```

#### 白名单
```
用户：官方管理员、运营团队
效果：仅转发这些用户的消息
```

### 3. 消息类型过滤

选择要转发的消息类型：
- ☑️ 文本消息
- ☑️ 图片消息
- ☑️ 文件附件
- ☐ 表情反应（可选）
- ☐ 语音消息（可选）

## 高级技巧

### 正则表达式（未来功能）
```
模式：^\\[官方\\].*
效果：仅转发以"[官方]"开头的消息
```

### 时间段过滤（未来功能）
```
时间：仅工作日 9:00-18:00
效果：仅在工作时间转发消息
```

## 组合使用

### 示例1：只转发官方公告
```
用户白名单：官方账号
关键词白名单：公告、通知
→ 只转发官方账号发送的包含"公告"或"通知"的消息
```

### 示例2：过滤广告
```
关键词黑名单：广告、代练、外挂、加群
→ 包含这些词的消息全部不转发
```

## 常见问题

**Q: 黑名单和白名单可以同时使用吗？**  
A: 可以，白名单优先级更高。

**Q: 支持通配符吗？**  
A: 当前版本不支持，未来会添加正则表达式支持。

**Q: 过滤规则会降低转发速度吗？**  
A: 不会，过滤在内存中进行，几乎零延迟。

---

**完成时间**: 6分钟  
**难度**: ⭐⭐⭐⭐☆ 较难
""",
        "steps": [
            "理解过滤类型",
            "配置黑白名单",
            "测试过滤效果",
            "调整优化规则"
        ],
        "screenshots": [],
        "video_url": None
    },
    
    {
        "id": "troubleshooting_guide",
        "title": "📖 常见问题排查指南",
        "category": "text",
        "duration": "10分钟",
        "difficulty": "advanced",
        "content": """
# 常见问题排查指南

本指南帮助您快速定位和解决常见问题。

## 问题1: 账号一直显示"离线"

### 可能原因
1. ❌ Cookie已过期
2. ❌ 网络连接问题
3. ❌ KOOK服务器问题
4. ❌ IP被限制

### 排查步骤
```
第1步：检查Cookie是否过期
→ 查看账号详情
→ 如果显示"Cookie已过期"，请重新登录

第2步：检查网络连接
→ 访问 https://www.kookapp.cn 确认可访问
→ 如果无法访问，检查网络设置

第3步：查看系统日志
→ 点击"日志"页面
→ 搜索该账号的错误信息
→ 根据错误提示操作

第4步：尝试重新登录
→ 点击账号的"重新登录"按钮
→ 或删除账号后重新添加
```

### 解决方案
- ✅ Cookie过期 → 重新导出Cookie
- ✅ 网络问题 → 检查网络/代理设置
- ✅ IP限制 → 更换网络或等待解封

---

## 问题2: 消息转发延迟很大

### 可能原因
1. ❌ 消息队列积压
2. ❌ 目标平台限流
3. ❌ 网络不稳定
4. ❌ 图片处理慢

### 排查步骤
```
第1步：查看队列状态
→ 首页查看"队列中消息"
→ 如果>100条，说明积压

第2步：检查转发日志
→ 查看最近消息的延迟时间
→ 如果>10秒，定位慢的环节

第3步：查看限流状态
→ 日志中搜索"rate limit"
→ 如果被限流，会自动排队
```

### 解决方案
- ✅ 队列积压 → 等待消化，或增加Worker数量
- ✅ 被限流 → 配置多个Webhook（负载均衡）
- ✅ 网络慢 → 检查网络速度
- ✅ 图片慢 → 切换到"仅图床"模式

---

## 问题3: 图片转发失败

### 可能原因
1. ❌ 图片被防盗链
2. ❌ 图片过大
3. ❌ 目标平台限制
4. ❌ 网络问题

### 排查步骤
```
第1步：查看错误日志
→ 搜索图片URL
→ 查看具体错误信息

第2步：检查图片大小
→ 如果>10MB，可能被拒绝
→ 系统会自动压缩

第3步：检查图床状态
→ 设置 → 图片处理
→ 查看当前策略
```

### 解决方案
- ✅ 防盗链 → 系统会自动处理（使用Cookie）
- ✅ 图片过大 → 自动压缩或使用图床
- ✅ 平台限制 → 切换到图床模式

---

## 问题4: 如何卸载软件

### Windows
1. 控制面板 → 程序 → 卸载程序
2. 找到"KOOK消息转发系统"
3. 点击卸载
4. 数据保留在: `C:\\Users\\用户名\\Documents\\KookForwarder`

### macOS
1. 打开"访达" → "应用程序"
2. 找到"KOOK消息转发系统"
3. 拖到废纸篓
4. 数据保留在: `~/Documents/KookForwarder`

### Linux
1. 直接删除 .AppImage 文件
2. 数据保留在: `~/.kook-forwarder`

### 完全删除（包括数据）
1. 卸载应用
2. 手动删除数据目录
3. Windows: `Documents\\KookForwarder`
4. macOS/Linux: `~/.kook-forwarder` 或 `~/Documents/KookForwarder`

---

## 更多帮助

- 📖 查看 [完整FAQ](faq)
- 📺 观看 [视频教程](videos)
- 💬 加入 [用户社区](community)

---

**完成时间**: 10分钟  
**难度**: ⭐⭐⭐☆☆ 中等
""",
        "steps": [
            "识别问题类型",
            "查看系统日志",
            "执行排查步骤",
            "应用解决方案"
        ],
        "screenshots": [],
        "video_url": None
    }
]


# ============ ✅ P1-4: 8个常见问题FAQ ============

FAQS = [
    {
        "id": "faq_offline",
        "question": "为什么KOOK账号一直显示"离线"？",
        "answer": """
### 可能原因

1. **Cookie已过期** (最常见)
   - 解决方案：重新登录KOOK并导出新的Cookie
   - 操作：账号管理 → 选择账号 → 重新登录

2. **网络连接问题**
   - 解决方案：检查网络连接，确认可以访问 www.kookapp.cn
   - 操作：设置 → 环境检查 → 一键诊断网络

3. **IP被KOOK限制**
   - 解决方案：更换网络IP或等待解封
   - 预防：不要频繁登录登出

4. **账号被封禁**
   - 解决方案：联系KOOK客服确认账号状态
   - 注意：使用自动化工具有被封风险

### 快速修复步骤

1. 点击账号的"重新登录"按钮
2. 如果失败，删除账号并重新添加
3. 使用最新的Cookie
4. 确保勾选"记住密码"（自动续期）
""",
        "category": "account",
        "tags": ["账号", "离线", "Cookie", "登录"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_delay",
        "question": "消息转发延迟很大（超过10秒）？",
        "answer": """
### 正常延迟范围

- ✅ **理想**: 0.5-2秒
- ⚠️ **可接受**: 2-5秒
- ❌ **异常**: >10秒

### 可能原因

1. **消息队列积压**
   - 检查方法：首页查看"队列中消息"数量
   - 解决方案：等待队列消化（自动处理）
   - 预防：减少监听的频道数量

2. **目标平台限流**
   - 现象：日志显示"rate limit"或"429"
   - 解决方案：系统会自动排队重试
   - 优化：配置多个Webhook实现负载均衡

3. **网络不稳定**
   - 检查方法：设置 → 环境检查 → 测试网络
   - 解决方案：检查网络连接速度
   - 建议：带宽至少10Mbps

4. **图片处理慢**
   - 现象：有图片的消息延迟更大
   - 解决方案：切换到"仅图床"模式
   - 设置：设置 → 图片处理 → 选择策略

### 优化建议

1. **使用多Webhook负载均衡**
   - Discord: 创建3-5个Webhook
   - 吞吐量提升3-5倍

2. **开启智能图片策略**
   - 设置 → 图片处理 → 智能模式
   - 自动选择最快方式

3. **减少监听频道**
   - 只监听重要频道
   - 减少不必要的映射
""",
        "category": "performance",
        "tags": ["延迟", "慢", "性能", "队列"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_image_fail",
        "question": "图片转发失败？",
        "answer": """
### 诊断步骤

#### 第1步：确认图片来源
- 查看日志中的图片URL
- 尝试在浏览器中直接打开
- 如果浏览器也打不开，说明图片本身有问题

#### 第2步：检查图片大小
- 系统限制：单张图片最大10MB
- 超过限制会自动压缩
- 如果压缩后仍过大，会被跳过

#### 第3步：查看图片策略
- 设置 → 图片处理 → 当前策略
- 推荐：智能模式（自动fallback）

### 解决方案

#### 方案1：使用智能模式（推荐）
```
设置 → 图片处理 → 选择"智能模式"

工作原理：
1. 优先尝试直传原始URL
2. 失败则下载并上传到本地图床
3. 图床失败则暂存本地，等待重试
```

#### 方案2：强制使用图床
```
设置 → 图片处理 → 选择"仅使用图床"

优点：稳定性高
缺点：需要占用本地磁盘
```

#### 方案3：检查防盗链设置
- 系统会自动处理KOOK防盗链
- 无需手动配置
- 如果仍失败，可能是图片服务器问题

### 防盗链说明

KOOK图片通常有防盗链保护，系统会自动：
- ✅ 带上KOOK的Cookie
- ✅ 设置正确的Referer头
- ✅ 使用KOOK的User-Agent

### 常见错误码

- **403 Forbidden**: 防盗链拦截（系统会自动处理）
- **404 Not Found**: 图片已被删除
- **413 Request Entity Too Large**: 图片过大
- **504 Gateway Timeout**: 下载超时
""",
        "category": "error",
        "tags": ["图片", "失败", "防盗链", "下载"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_backup",
        "question": "如何备份和恢复配置？",
        "answer": """
### 自动备份

系统默认每天自动备份配置：
- 备份位置：`数据目录/backups/`
- 保留时间：30天
- 备份内容：账号、Bot配置、映射关系

### 手动备份

1. 点击 设置 → 备份与恢复
2. 点击 **"立即备份配置"**
3. 选择保存位置
4. 系统会生成 `.kook_backup` 文件

### 恢复配置

1. 点击 设置 → 备份与恢复
2. 点击 **"恢复配置"**
3. 选择备份文件
4. 确认恢复

### 备份文件说明

备份文件包含：
- ✅ 账号列表（不含密码）
- ✅ Bot配置（Webhook/Token等）
- ✅ 频道映射关系
- ✅ 过滤规则
- ✅ 系统设置

不包含：
- ❌ 主密码
- ❌ 消息历史记录
- ❌ 图片缓存

### 迁移到新电脑

1. 在旧电脑上备份配置
2. 复制备份文件到新电脑
3. 在新电脑上安装系统
4. 导入备份文件
5. 重新输入主密码（如果启用）
""",
        "category": "config",
        "tags": ["备份", "恢复", "迁移", "导出"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_multi_account",
        "question": "如何添加和管理多个账号？",
        "answer": """
### 添加多个账号

系统支持同时监听多个KOOK账号：

#### 使用场景
- 监听不同服务器（账号在不同服务器中）
- 备用账号（主账号掉线时切换）
- 分流处理（多账号分担负载）

#### 添加步骤
1. 账号管理 → 添加账号
2. 重复添加流程
3. 每个账号独立登录
4. 系统会自动管理多个浏览器实例

### 账号状态管理

每个账号卡片显示：
- 📧 邮箱地址
- 🟢 在线状态（在线/离线）
- 🕐 最后活跃时间
- 📡 监听服务器数量

### 操作按钮
- 🔄 **重新登录**: 刷新Cookie
- ✏️ **编辑**: 修改账号信息
- 🗑️ **删除**: 移除账号

### 性能说明

- 单账号内存占用：~200MB
- 推荐最多：3-5个账号
- 超过5个账号可能影响性能

### 账号切换

系统会自动管理账号：
- 不需要手动切换
- 每个账号独立监听
- 互不干扰

### 数据隔离

- 每个账号的Cookie独立存储
- 不会混淆
- 安全隔离
""",
        "category": "account",
        "tags": ["多账号", "管理", "切换", "添加"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_filter",
        "question": "如何设置消息过滤规则？",
        "answer": """
### 基础配置

1. 点击左侧菜单 **"过滤规则"**
2. 选择应用范围：
   - 全局规则：对所有频道生效
   - 特定频道：仅对某个频道生效

### 关键词过滤

#### 黑名单（不转发包含的词）
```
输入框：广告, 代练, 外挂
效果：包含这些词的消息不会转发
```

#### 白名单（仅转发包含的词）
```
输入框：官方公告, 版本更新, 重要通知
效果：只有包含这些词的消息才会转发
```

### 用户过滤

#### 黑名单用户
1. 点击"添加用户"
2. 输入用户ID或用户名
3. 该用户的所有消息不会转发

#### 白名单用户
1. 点击"添加用户"
2. 输入用户ID或用户名
3. 仅转发该用户的消息

### 消息类型过滤

勾选要转发的类型：
- ☑️ 文本消息
- ☑️ 图片消息
- ☑️ 链接消息
- ☐ 表情反应
- ☑️ 文件附件

### 优先级

1. 用户白名单（最高）
2. 用户黑名单
3. 关键词白名单
4. 关键词黑名单
5. 消息类型过滤

### 示例场景

#### 场景1：只转发官方公告
```
用户白名单：官方运营、管理员
关键词白名单：公告、通知、更新
```

#### 场景2：过滤垃圾信息
```
关键词黑名单：广告、代练、外挂、刷屏
用户黑名单：广告机器人A、刷屏用户B
```
""",
        "category": "config",
        "tags": ["过滤", "规则", "黑名单", "白名单"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_logs",
        "question": "如何查看和分析转发日志？",
        "answer": """
### 查看实时日志

1. 点击左侧菜单 **"实时日志"**
2. 日志会自动刷新（每5秒）
3. 可以暂停自动刷新

### 筛选日志

提供多种筛选条件：
- **状态**: 全部/成功/失败/进行中
- **平台**: 全部/Discord/Telegram/飞书
- **频道**: 选择特定KOOK频道
- **搜索**: 关键词搜索

### 日志详情

点击任意日志条目查看详细信息：
- 📝 原始消息内容
- 📝 转发后消息内容
- ⏱️ 转发耗时分析
- 🔍 错误详情（如果失败）

### 导出日志

1. 点击 **"导出日志"** 按钮
2. 选择时间范围：
   - 最近1小时
   - 最近24小时
   - 最近7天
   - 自定义时间段
3. 选择格式：CSV/JSON/TXT
4. 点击"导出"

### 日志统计

首页实时显示：
- 📊 今日转发总数
- ✅ 成功率
- ⏱️ 平均延迟
- ❌ 失败消息数

### 清空日志

1. 日志页面 → 清空日志
2. 确认操作
3. 仅清除显示，不删除数据库记录

### 日志保留策略

- 默认保留：3天
- 可在设置中调整：1-30天
- 超过保留期的日志会自动删除
""",
        "category": "usage",
        "tags": ["日志", "查看", "导出", "统计"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_security",
        "question": "系统安全性如何？会泄露Cookie吗？",
        "answer": """
### 安全措施

#### 1. 数据加密存储
- ✅ 所有敏感信息（Cookie、Token、密码）使用 **AES-256** 加密
- ✅ 加密密钥基于设备唯一ID生成
- ✅ 换设备需要重新输入

#### 2. 主密码保护
- ✅ 首次启动设置主密码（6-20位）
- ✅ 使用 **bcrypt** 哈希存储（行业标准）
- ✅ 启动时需要输入密码
- ✅ 支持邮箱验证码重置

#### 3. 访问控制
- ✅ API仅监听本地（127.0.0.1）
- ✅ 不接受外网访问
- ✅ 所有API都需要Token认证

#### 4. 日志脱敏
- ✅ 日志中不显示完整Token
- ✅ Cookie仅显示前10个字符
- ✅ 密码完全不记录

### 数据存储位置

```
Windows:
  C:\\Users\\{用户名}\\Documents\\KookForwarder\\data\\

macOS/Linux:
  ~/Documents/KookForwarder/data/
  或 ~/.kook-forwarder/data/
```

### 权限设置

- 配置文件权限：仅当前用户可读
- 数据库文件：仅当前用户可读写
- 自动设置适当的文件权限

### 网络安全

- ✅ 所有HTTPS连接
- ✅ 证书验证
- ✅ 不信任不安全的连接

### 审计日志

系统记录所有操作：
- 登录/登出
- 配置修改
- 敏感操作

### 建议

1. **定期更新Cookie**（30天一次）
2. **设置强密码**（至少8位，含字母数字）
3. **不要分享配置文件**
4. **定期备份配置**

### 免责声明

⚠️ **请注意**：
- 本软件通过浏览器自动化抓取KOOK消息
- 可能违反KOOK服务条款
- 使用有账号被封禁的风险
- 请仅在授权场景下使用
""",
        "category": "security",
        "tags": ["安全", "加密", "Cookie", "隐私"],
        "helpful_count": 0
    },
    
    {
        "id": "faq_performance",
        "question": "如何优化系统性能？",
        "answer": """
### 性能优化建议

#### 1. 减少监听频道
- 只监听必要的频道
- 取消不活跃频道的映射
- 建议：每个账号<20个频道

#### 2. 配置多Webhook（负载均衡）
```
单Webhook吞吐量：60条/分钟
10个Webhook：600条/分钟（提升10倍！）

配置方法：
1. 创建多个Discord Webhook
2. 系统自动轮询使用
3. 大幅提升吞吐量
```

#### 3. 优化图片策略
```
推荐配置：
- 图片策略：智能模式
- 压缩质量：85%
- 最大尺寸：10MB

效果：
- 减少带宽占用
- 加快转发速度
- 节省磁盘空间
```

#### 4. 调整日志保留策略
```
设置 → 日志设置 → 保留时长

建议：
- 开发/调试：7天
- 生产环境：3天
- 低性能设备：1天
```

#### 5. 定期清理数据
```
设置 → 图片处理 → 立即清理旧图片

自动清理：
- 7天前的图片自动删除
- 释放磁盘空间
- 不影响已转发的消息
```

### 性能监控

首页实时显示：
- 📊 CPU占用率
- 💾 内存使用量
- 📈 消息处理速度
- 📉 队列长度

### 系统要求

#### 最低配置
- CPU: 双核处理器
- 内存: 4GB
- 磁盘: 500MB（不含图片缓存）
- 网络: 稳定连接

#### 推荐配置
- CPU: 四核处理器
- 内存: 8GB
- 磁盘: 10GB+
- 网络: 10Mbps+

### 性能问题排查

如果系统运行缓慢：
1. 查看首页性能监控
2. 如果CPU>80%，减少监听频道
3. 如果内存>2GB，重启应用
4. 如果磁盘满，清理旧图片
""",
        "category": "performance",
        "tags": ["性能", "优化", "速度", "负载均衡"],
        "helpful_count": 0
    }
]


# ============ ✅ P1-4: 5个视频教程 ============

VIDEOS = [
    {
        "id": "video_full_config",
        "title": "📺 完整配置演示（10分钟）",
        "duration": "10:00",
        "description": "从安装到使用的完整流程演示",
        "url": "/videos/full_configuration.mp4",
        "thumbnail": "/videos/thumbnails/full_config.jpg",
        "chapters": [
            {"time": "0:00", "title": "简介"},
            {"time": "0:30", "title": "安装应用"},
            {"time": "2:00", "title": "添加KOOK账号"},
            {"time": "4:00", "title": "配置Bot"},
            {"time": "7:00", "title": "设置映射"},
            {"time": "9:00", "title": "测试运行"}
        ]
    },
    {
        "id": "video_cookie",
        "title": "📺 Cookie获取教程（3分钟）",
        "duration": "3:00",
        "description": "详细演示如何从浏览器导出Cookie",
        "url": "/videos/cookie_export.mp4",
        "thumbnail": "/videos/thumbnails/cookie.jpg",
        "chapters": [
            {"time": "0:00", "title": "Chrome浏览器"},
            {"time": "1:30", "title": "Firefox浏览器"},
            {"time": "2:30", "title": "使用扩展"}
        ]
    },
    {
        "id": "video_discord",
        "title": "📺 Discord Webhook配置（2分钟）",
        "duration": "2:00",
        "description": "快速创建Discord Webhook",
        "url": "/videos/discord_webhook.mp4",
        "thumbnail": "/videos/thumbnails/discord.jpg",
        "chapters": [
            {"time": "0:00", "title": "打开设置"},
            {"time": "0:30", "title": "创建Webhook"},
            {"time": "1:30", "title": "复制URL"}
        ]
    },
    {
        "id": "video_telegram",
        "title": "📺 Telegram Bot配置（4分钟）",
        "duration": "4:00",
        "description": "创建Telegram Bot并获取Chat ID",
        "url": "/videos/telegram_bot.mp4",
        "thumbnail": "/videos/thumbnails/telegram.jpg",
        "chapters": [
            {"time": "0:00", "title": "与BotFather对话"},
            {"time": "1:00", "title": "创建Bot"},
            {"time": "2:00", "title": "添加到群组"},
            {"time": "3:00", "title": "获取Chat ID"}
        ]
    },
    {
        "id": "video_feishu",
        "title": "📺 飞书应用配置（5分钟）",
        "duration": "5:00",
        "description": "创建飞书自建应用的完整流程",
        "url": "/videos/feishu_app.mp4",
        "thumbnail": "/videos/thumbnails/feishu.jpg",
        "chapters": [
            {"time": "0:00", "title": "访问开放平台"},
            {"time": "1:00", "title": "创建应用"},
            {"time": "2:30", "title": "配置权限"},
            {"time": "4:00", "title": "添加到群组"}
        ]
    }
]


# ============ API接口 ============

@router.get("/tutorials")
async def get_tutorials():
    """
    获取所有教程列表
    
    Returns:
        教程列表
    """
    return {
        "tutorials": TUTORIALS,
        "total": len(TUTORIALS)
    }


@router.get("/tutorials/{tutorial_id}")
async def get_tutorial(tutorial_id: str):
    """
    获取指定教程详情
    
    Args:
        tutorial_id: 教程ID
        
    Returns:
        教程详情
    """
    tutorial = next((t for t in TUTORIALS if t["id"] == tutorial_id), None)
    
    if not tutorial:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="教程不存在")
    
    return tutorial


@router.get("/faqs")
async def get_faqs(category: Optional[str] = None):
    """
    获取常见问题FAQ
    
    Args:
        category: 分类筛选（可选）
        
    Returns:
        FAQ列表
    """
    faqs = FAQS
    
    if category:
        faqs = [f for f in faqs if f["category"] == category]
    
    return {
        "faqs": faqs,
        "total": len(faqs),
        "categories": ["account", "config", "error", "performance", "security", "usage"]
    }


@router.get("/faqs/{faq_id}")
async def get_faq(faq_id: str):
    """
    获取指定FAQ详情
    
    Args:
        faq_id: FAQ ID
        
    Returns:
        FAQ详情
    """
    faq = next((f for f in FAQS if f["id"] == faq_id), None)
    
    if not faq:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="FAQ不存在")
    
    return faq


@router.get("/videos")
async def get_videos():
    """
    获取所有视频教程
    
    Returns:
        视频列表
    """
    return {
        "videos": VIDEOS,
        "total": len(VIDEOS)
    }


@router.get("/search")
async def search_help(query: str):
    """
    搜索帮助内容
    
    Args:
        query: 搜索关键词
        
    Returns:
        搜索结果
    """
    query_lower = query.lower()
    
    results = {
        "tutorials": [],
        "faqs": [],
        "videos": []
    }
    
    # 搜索教程
    for tutorial in TUTORIALS:
        if (query_lower in tutorial["title"].lower() or
            query_lower in tutorial["content"].lower()):
            results["tutorials"].append(tutorial)
    
    # 搜索FAQ
    for faq in FAQS:
        if (query_lower in faq["question"].lower() or
            query_lower in faq["answer"].lower() or
            any(query_lower in tag.lower() for tag in faq["tags"])):
            results["faqs"].append(faq)
    
    # 搜索视频
    for video in VIDEOS:
        if (query_lower in video["title"].lower() or
            query_lower in video["description"].lower()):
            results["videos"].append(video)
    
    total_results = (
        len(results["tutorials"]) +
        len(results["faqs"]) +
        len(results["videos"])
    )
    
    return {
        **results,
        "query": query,
        "total": total_results
    }
