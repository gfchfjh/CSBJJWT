/**
 * 内置教程数据
 * 包含图文教程、视频链接、使用提示
 */

export const tutorials = {
  // ========== 快速入门教程 ==========
  quickstart: {
    id: 'quickstart',
    title: '快速入门指南',
    description: '10分钟完成从安装到使用的全流程',
    estimatedTime: '10分钟',
    difficulty: '简单',
    category: 'getting-started',
    icon: '🎬',
    steps: [
      {
        id: 1,
        title: '下载并安装',
        content: '从GitHub Releases下载适合您操作系统的安装包',
        image: '/images/tutorials/quickstart-install.png',
        tips: [
          'Windows用户下载 .exe 文件',
          'macOS用户下载 .dmg 文件',
          'Linux用户下载 .AppImage 文件'
        ],
        warnings: [
          '首次运行可能需要管理员权限',
          'Windows Defender可能会提示安全警告，请选择"仍要运行"'
        ],
        video: null,
        estimatedTime: '2分钟'
      },
      {
        id: 2,
        title: '首次启动配置',
        content: '双击启动程序，系统会自动打开配置向导',
        image: '/images/tutorials/quickstart-wizard.png',
        tips: [
          '配置向导只需要3步即可完成',
          '所有配置都可以稍后修改',
          '建议先准备好KOOK账号Cookie'
        ],
        warnings: null,
        video: null,
        estimatedTime: '5分钟'
      },
      {
        id: 3,
        title: '启动服务',
        content: '完成配置后，点击"启动服务"按钮开始转发',
        image: '/images/tutorials/quickstart-start.png',
        tips: [
          '首次启动可能需要等待几秒钟',
          '可以在主界面查看实时转发统计',
          '建议先测试少量频道的转发效果'
        ],
        warnings: [
          '请保持网络连接稳定',
          '不要同时运行多个程序实例'
        ],
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 4,
        title: '查看转发日志',
        content: '在日志页面查看消息转发情况',
        image: '/images/tutorials/quickstart-logs.png',
        tips: [
          '绿色表示转发成功',
          '红色表示转发失败（会自动重试）',
          '可以搜索和过滤日志'
        ],
        warnings: null,
        video: null,
        estimatedTime: '2分钟'
      }
    ],
    faq: [
      {
        question: '安装包很大（150MB+），正常吗？',
        answer: '是的，安装包包含了Python运行环境、Chromium浏览器、Redis数据库等所有依赖，因此体积较大。这样做的好处是无需额外安装任何软件。'
      },
      {
        question: '可以在服务器上运行吗？',
        answer: '可以。推荐使用Docker部署方式，或者使用源码安装方式。独立安装包主要面向Windows/macOS桌面用户。'
      }
    ]
  },

  // ========== Cookie获取教程 ==========
  cookieGuide: {
    id: 'cookie',
    title: 'Cookie获取详细教程',
    description: '3种方法获取KOOK Cookie',
    estimatedTime: '3分钟',
    difficulty: '简单',
    category: 'configuration',
    icon: '🍪',
    steps: [
      {
        id: 1,
        title: '方式1：Chrome扩展（推荐）',
        content: '使用官方提供的Chrome扩展，一键导出Cookie',
        image: '/images/tutorials/cookie-extension.png',
        tips: [
          '最简单快捷的方式',
          '支持自动导入到系统',
          '无需手动复制粘贴'
        ],
        warnings: [
          '需要先安装Chrome扩展',
          '确保已登录KOOK网页版'
        ],
        video: 'https://example.com/cookie-extension-tutorial.mp4',
        estimatedTime: '1分钟',
        detailedSteps: [
          '1. 安装"KOOK Cookie导出器"Chrome扩展',
          '2. 访问 www.kookapp.cn 并登录',
          '3. 点击浏览器右上角的扩展图标',
          '4. 点击"一键导出Cookie"按钮',
          '5. 如果系统正在运行，Cookie会自动导入',
          '6. 如果系统未运行，Cookie会复制到剪贴板'
        ]
      },
      {
        id: 2,
        title: '方式2：浏览器开发者工具',
        content: '通过浏览器自带的开发者工具手动提取Cookie',
        image: '/images/tutorials/cookie-devtools.png',
        tips: [
          '适合有一定技术基础的用户',
          '不需要安装扩展',
          '任何浏览器都可以使用'
        ],
        warnings: [
          '步骤相对复杂',
          '需要仔细复制每个字段'
        ],
        video: null,
        estimatedTime: '3分钟',
        detailedSteps: [
          '1. 登录 www.kookapp.cn',
          '2. 按F12打开开发者工具',
          '3. 切换到"Application"（应用程序）标签页',
          '4. 左侧菜单选择"Cookies" → "https://www.kookapp.cn"',
          '5. 找到并复制以下Cookie：',
          '   - token',
          '   - session',
          '   - user_id',
          '6. 在系统中选择"手动粘贴Cookie"并填入'
        ]
      },
      {
        id: 3,
        title: '方式3：导出工具脚本',
        content: '使用JavaScript脚本在浏览器控制台导出',
        image: '/images/tutorials/cookie-script.png',
        tips: [
          '快速便捷',
          '自动生成JSON格式',
          '适合批量导出'
        ],
        warnings: [
          '需要基本的浏览器使用知识'
        ],
        video: null,
        estimatedTime: '2分钟',
        code: `
// 在KOOK网页版打开控制台（F12），粘贴以下代码并回车

const cookies = document.cookie.split(';').map(c => {
  const [name, value] = c.trim().split('=');
  return { name, value, domain: '.kookapp.cn' };
});

console.log('Cookie导出成功！请复制以下内容：');
console.log(JSON.stringify(cookies, null, 2));

// 自动复制到剪贴板
copy(JSON.stringify(cookies, null, 2));
alert('Cookie已复制到剪贴板！');
        `,
        detailedSteps: [
          '1. 登录 www.kookapp.cn',
          '2. 按F12打开控制台',
          '3. 切换到"Console"（控制台）标签',
          '4. 复制左侧代码框中的脚本',
          '5. 粘贴到控制台并按Enter',
          '6. Cookie会自动复制到剪贴板',
          '7. 在系统中粘贴导入'
        ]
      },
      {
        id: 4,
        title: '验证Cookie有效性',
        content: '导入后验证Cookie是否正确',
        image: '/images/tutorials/cookie-verify.png',
        tips: [
          '成功导入后账号状态应显示"在线"',
          '如果显示"离线"，说明Cookie无效或已过期',
          'Cookie有效期通常为30天'
        ],
        warnings: [
          '定期检查账号状态',
          'Cookie过期后需要重新获取'
        ],
        video: null,
        estimatedTime: '1分钟'
      }
    ],
    faq: [
      {
        question: 'Cookie多久会过期？',
        answer: 'KOOK的Cookie通常有效期为30天。过期后需要重新获取。系统会自动检测Cookie过期并提示您重新登录。'
      },
      {
        question: 'Cookie安全吗？会被泄露吗？',
        answer: 'Cookie仅存储在您的本地电脑上，使用AES-256加密存储。系统不会上传Cookie到任何服务器。但请注意不要将Cookie分享给他人。'
      },
      {
        question: '可以同时使用多个KOOK账号吗？',
        answer: '可以。系统支持添加多个账号，每个账号独立监听和转发。建议不要超过3个账号，以免占用过多系统资源。'
      }
    ]
  },

  // ========== Discord配置教程 ==========
  discordGuide: {
    id: 'discord',
    title: 'Discord Webhook配置教程',
    description: '5分钟完成Discord Webhook创建和配置',
    estimatedTime: '5分钟',
    difficulty: '简单',
    category: 'configuration',
    icon: '💬',
    steps: [
      {
        id: 1,
        title: '打开服务器设置',
        content: '在Discord中，右键点击要接收消息的服务器图标，选择"服务器设置"',
        image: '/images/tutorials/discord-step1.png',
        tips: [
          '您需要有服务器管理权限',
          '如果没有权限，请联系服务器管理员'
        ],
        warnings: null,
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 2,
        title: '进入整合设置',
        content: '在左侧菜单中找到"整合"（Integrations）并点击',
        image: '/images/tutorials/discord-step2.png',
        tips: [
          '有些语言版本可能显示为"集成"或"Integrations"'
        ],
        warnings: null,
        video: null,
        estimatedTime: '20秒'
      },
      {
        id: 3,
        title: '创建Webhook',
        content: '点击"创建Webhook"或"查看Webhooks" → "新建Webhook"',
        image: '/images/tutorials/discord-step3.png',
        tips: [
          '可以为Webhook设置自定义名称和头像',
          '名称会显示为消息发送者'
        ],
        warnings: [
          '一个服务器最多可以创建10个Webhook'
        ],
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 4,
        title: '选择目标频道',
        content: '选择要接收转发消息的频道',
        image: '/images/tutorials/discord-step4.png',
        tips: [
          '可以选择任何文字频道',
          '建议创建专门的转发频道',
          '不同的KOOK频道可以转发到不同的Discord频道'
        ],
        warnings: null,
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 5,
        title: '复制Webhook URL',
        content: '点击"复制Webhook URL"按钮',
        image: '/images/tutorials/discord-step5.png',
        tips: [
          'URL格式类似：https://discord.com/api/webhooks/...',
          '不要分享这个URL给任何人',
          'URL泄露会导致任何人都可以发送消息到您的频道'
        ],
        warnings: [
          '⚠️ 妥善保管Webhook URL',
          '⚠️ 如果泄露，请立即删除重建'
        ],
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 6,
        title: '在系统中配置',
        content: '返回KOOK消息转发系统，在"Bot配置"页面粘贴Webhook URL',
        image: '/images/tutorials/discord-step6.png',
        tips: [
          '可以为Webhook设置一个容易识别的名称',
          '点击"测试连接"验证配置是否正确',
          '测试成功后会在Discord频道看到测试消息'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      }
    ],
    faq: [
      {
        question: '一个Discord服务器可以创建多少个Webhook？',
        answer: '一个Discord服务器最多可以创建10个Webhook。如果需要更多，可以在不同的频道创建，或删除不用的Webhook。'
      },
      {
        question: 'Webhook URL泄露了怎么办？',
        answer: '立即在Discord服务器设置中删除该Webhook，然后重新创建一个新的。更新系统中的配置即可。'
      },
      {
        question: '可以转发到多个Discord服务器吗？',
        answer: '可以。为每个服务器创建Webhook，在频道映射时可以选择多个目标。'
      },
      {
        question: '转发的消息能显示原发送者吗？',
        answer: '可以。在Bot配置中启用"伪装发送者"选项，消息会显示KOOK用户的名称和头像。'
      }
    ],
    troubleshooting: [
      {
        problem: 'Webhook测试失败，显示404错误',
        solution: 'Webhook URL可能不正确或已被删除。请重新复制URL，确保包含完整链接。'
      },
      {
        problem: '消息发送到Discord后乱码',
        solution: '可能是字符编码问题。在设置中切换"消息格式"选项，或联系技术支持。'
      },
      {
        problem: '图片无法显示',
        solution: '检查图片处理策略设置，建议使用"智能模式"。如果仍有问题，查看图床配置。'
      }
    ]
  },

  // ========== Telegram配置教程 ==========
  telegramGuide: {
    id: 'telegram',
    title: 'Telegram Bot配置教程',
    description: '从创建Bot到获取Chat ID的完整流程',
    estimatedTime: '6分钟',
    difficulty: '简单',
    category: 'configuration',
    icon: '✈️',
    steps: [
      {
        id: 1,
        title: '与BotFather对话',
        content: '在Telegram中搜索 @BotFather 并开始对话',
        image: '/images/tutorials/telegram-step1.png',
        tips: [
          'BotFather是Telegram官方的Bot管理机器人',
          '所有Bot都通过它创建和管理'
        ],
        warnings: [
          '注意是 @BotFather，不是 @BotFather2 等仿冒账号'
        ],
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 2,
        title: '创建新Bot',
        content: '发送命令 /newbot 创建新的Bot',
        image: '/images/tutorials/telegram-step2.png',
        tips: [
          'BotFather会引导您完成创建流程',
          '需要设置Bot的名称和用户名'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟',
        detailedSteps: [
          '1. 发送 /newbot',
          '2. 输入Bot的显示名称（例如：KOOK消息转发）',
          '3. 输入Bot的用户名（必须以bot结尾，例如：kook_forwarder_bot）',
          '4. 创建成功后会收到Bot Token'
        ]
      },
      {
        id: 3,
        title: '保存Bot Token',
        content: '复制BotFather返回的Token（一串以数字和冒号开头的字符串）',
        image: '/images/tutorials/telegram-step3.png',
        tips: [
          'Token格式：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz',
          '妥善保管Token，不要分享给任何人',
          'Token泄露后可通过 /revoke 命令重置'
        ],
        warnings: [
          '⚠️ Token相当于Bot的密码',
          '⚠️ 任何人获得Token都可以控制您的Bot'
        ],
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 4,
        title: '将Bot添加到群组',
        content: '在目标群组中添加刚创建的Bot',
        image: '/images/tutorials/telegram-step4.png',
        tips: [
          '可以将Bot添加到任何您有权限的群组',
          '建议给Bot管理员权限（可选）'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟',
        detailedSteps: [
          '1. 打开目标Telegram群组',
          '2. 点击群组名称进入设置',
          '3. 选择"添加成员"',
          '4. 搜索您的Bot用户名',
          '5. 添加Bot到群组'
        ]
      },
      {
        id: 5,
        title: '获取Chat ID',
        content: '使用系统内置的"自动获取Chat ID"功能',
        image: '/images/tutorials/telegram-step5.png',
        tips: [
          '在系统的Bot配置页面点击"自动获取"',
          '或者手动向Bot发送一条消息，使用 /getid 命令'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟',
        detailedSteps: [
          '方式1（推荐）：',
          '1. 在系统Bot配置页输入Bot Token',
          '2. 点击"自动获取Chat ID"按钮',
          '3. 系统会自动检测并填入',
          '',
          '方式2（手动）：',
          '1. 在群组中 @您的Bot 并发送任意消息',
          '2. 访问 https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates',
          '3. 在返回的JSON中找到 chat.id 字段'
        ]
      },
      {
        id: 6,
        title: '测试连接',
        content: '在系统中点击"测试连接"，验证配置是否正确',
        image: '/images/tutorials/telegram-step6.png',
        tips: [
          '测试成功会在Telegram群组收到测试消息',
          '如果失败，请检查Token和Chat ID是否正确'
        ],
        warnings: null,
        video: null,
        estimatedTime: '30秒'
      }
    ],
    faq: [
      {
        question: 'Chat ID是什么？',
        answer: 'Chat ID是Telegram群组的唯一标识符。负数开头的ID代表群组（例如：-1001234567890），正数开头的代表私聊。'
      },
      {
        question: 'Bot Token忘记了怎么办？',
        answer: '联系 @BotFather，发送 /mybots → 选择您的Bot → API Token 即可查看。'
      },
      {
        question: '可以转发到私聊吗？',
        answer: '理论上可以，但不推荐。建议创建专门的转发群组。'
      }
    ]
  },

  // ========== 飞书配置教程 ==========
  feishuGuide: {
    id: 'feishu',
    title: '飞书应用配置教程',
    description: '创建飞书自建应用并配置机器人',
    estimatedTime: '8分钟',
    difficulty: '中等',
    category: 'configuration',
    icon: '🕊️',
    steps: [
      {
        id: 1,
        title: '访问飞书开放平台',
        content: '打开浏览器访问 https://open.feishu.cn',
        image: '/images/tutorials/feishu-step1.png',
        tips: [
          '需要使用飞书账号登录',
          '个人账号和企业账号都可以'
        ],
        warnings: null,
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 2,
        title: '创建自建应用',
        content: '在开发者后台，点击"创建企业自建应用"',
        image: '/images/tutorials/feishu-step2.png',
        tips: [
          '应用名称可以随意设置',
          '建议设置应用描述和图标'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 3,
        title: '开启机器人能力',
        content: '在应用设置中，找到"机器人"功能并开启',
        image: '/images/tutorials/feishu-step3.png',
        tips: [
          '这是发送消息的必要步骤'
        ],
        warnings: null,
        video: null,
        estimatedTime: '30秒'
      },
      {
        id: 4,
        title: '获取App ID和Secret',
        content: '在"凭证与基础信息"页面，复制App ID和App Secret',
        image: '/images/tutorials/feishu-step4.png',
        tips: [
          'App ID是应用的唯一标识',
          'App Secret相当于应用密码'
        ],
        warnings: [
          '⚠️ 不要泄露App Secret'
        ],
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 5,
        title: '配置权限',
        content: '添加必要的API权限：im:message、im:message:send_as_bot',
        image: '/images/tutorials/feishu-step5.png',
        tips: [
          '权限配置后需要重新发布应用版本'
        ],
        warnings: null,
        video: null,
        estimatedTime: '2分钟'
      },
      {
        id: 6,
        title: '添加到群组',
        content: '在飞书群组中，添加刚创建的机器人',
        image: '/images/tutorials/feishu-step6.png',
        tips: [
          '在群组设置 → 群机器人 → 添加机器人'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 7,
        title: '测试连接',
        content: '在系统中输入App ID和Secret，点击"测试连接"',
        image: '/images/tutorials/feishu-step7.png',
        tips: [
          '测试成功会在飞书群组收到测试消息'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      }
    ],
    faq: [
      {
        question: '飞书配置比Discord/Telegram复杂吗？',
        answer: '稍微复杂一些，因为需要在开放平台创建应用。但按照教程一步步操作，通常10分钟内可以完成。'
      },
      {
        question: '企业应用和个人应用有什么区别？',
        answer: '企业应用适用于企业内部使用，个人应用适用于个人或小团队。功能上没有太大区别，选择适合您的即可。'
      }
    ]
  },

  // ========== 频道映射教程 ==========
  mappingGuide: {
    id: 'mapping',
    title: '频道映射详解教程',
    description: '理解并配置KOOK到目标平台的映射关系',
    estimatedTime: '10分钟',
    difficulty: '简单',
    category: 'configuration',
    icon: '🔀',
    steps: [
      {
        id: 1,
        title: '理解映射关系',
        content: '映射是指将KOOK的某个频道的消息转发到目标平台的某个频道',
        image: '/images/tutorials/mapping-concept.png',
        tips: [
          '一个KOOK频道可以同时转发到多个目标',
          '例如：KOOK #公告 → Discord #announcements + Telegram 公告群'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 2,
        title: '选择映射模式',
        content: '系统提供两种映射模式：智能推荐和手动配置',
        image: '/images/tutorials/mapping-mode.png',
        tips: [
          '智能推荐：AI自动分析频道名称并推荐匹配（推荐新手）',
          '手动配置：完全自定义每个映射关系（适合高级用户）'
        ],
        warnings: null,
        video: null,
        estimatedTime: '1分钟'
      },
      {
        id: 3,
        title: '使用智能推荐（推荐）',
        content: '点击"智能推荐"，系统会自动分析并推荐最佳匹配',
        image: '/images/tutorials/mapping-smart.png',
        tips: [
          '系统会根据频道名称相似度推荐',
          '支持中英文互译（例如："公告" 匹配 "announcements"）',
          '每个推荐都有置信度评分',
          '可以勾选或取消任何推荐'
        ],
        warnings: null,
        video: 'https://example.com/smart-mapping-demo.mp4',
        estimatedTime: '3分钟'
      },
      {
        id: 4,
        title: '手动配置映射',
        content: '如果智能推荐不满意，可以手动配置',
        image: '/images/tutorials/mapping-manual.png',
        tips: [
          '选择源KOOK频道',
          '选择一个或多个目标平台和频道',
          '可以随时修改或删除映射'
        ],
        warnings: null,
        video: null,
        estimatedTime: '5分钟'
      }
    ],
    faq: [
      {
        question: '智能推荐的准确率高吗？',
        answer: '对于常见的频道名称（如"公告"、"闲聊"、"技术"），准确率通常在80%以上。您可以手动调整不满意的推荐。'
      },
      {
        question: '可以一个KOOK频道转发到多个目标吗？',
        answer: '可以。在配置映射时，可以同时选择多个目标平台和频道。'
      }
    ]
  },

  // ========== 常见问题FAQ ==========
  faq: {
    id: 'faq',
    title: '常见问题FAQ',
    description: '快速找到常见问题的解决方案',
    category: 'help',
    icon: '❓',
    sections: [
      {
        title: '🚀 安装和启动',
        questions: [
          {
            question: '安装后无法启动，双击没有反应？',
            answer: `可能原因：
1. 杀毒软件拦截 → 添加到白名单
2. 权限不足 → 以管理员身份运行
3. 端口被占用 → 检查端口9527和6379
4. 系统不兼容 → 查看系统要求

解决方案：
• Windows：右键程序 → 以管理员身份运行
• 检查任务管理器中是否有残留进程
• 查看日志文件（位于用户文档/KookForwarder/logs）`
          },
          {
            question: 'macOS提示"无法打开，因为无法验证开发者"？',
            answer: `这是macOS的安全机制。解决方案：
1. 右键点击应用
2. 选择"打开"
3. 在弹出对话框中再次点击"打开"

或者在系统偏好设置 → 安全性与隐私中允许运行。`
          }
        ]
      },
      {
        title: '🔑 账号和Cookie',
        questions: [
          {
            question: 'Cookie导入后显示"离线"？',
            answer: `可能原因：
1. Cookie已过期
2. Cookie格式不正确
3. 缺少必要的Cookie字段

解决方案：
• 重新登录KOOK网页版
• 重新获取Cookie
• 确保包含 token、session、user_id 三个字段`
          },
          {
            question: 'KOOK账号频繁掉线？',
            answer: `可能原因：
1. Cookie过期
2. IP频繁变更
3. 同时多处登录

解决方案：
• 使用稳定的网络环境
• 不要在太多设备上同时登录
• 定期更新Cookie（建议每周一次）`
          }
        ]
      },
      {
        title: '📨 消息转发',
        questions: [
          {
            question: '消息转发延迟很大（超过10秒）？',
            answer: `可能原因：
1. 网络延迟
2. 队列积压
3. 目标平台限流

解决方案：
• 检查网络连接
• 查看队列状态（主界面）
• 减少映射的频道数量
• 等待队列消化`
          },
          {
            question: '图片转发失败？',
            answer: `可能原因：
1. 图片被防盗链保护
2. 图片文件过大
3. 目标平台限制

解决方案：
• 使用"智能模式"图片策略（默认）
• 检查图床配置
• 查看失败日志获取详细信息`
          }
        ]
      }
    ]
  }
};

/**
 * 根据分类获取教程列表
 */
export function getTutorialsByCategory(category) {
  return Object.values(tutorials).filter(t => t.category === category);
}

/**
 * 根据ID获取教程
 */
export function getTutorialById(id) {
  return tutorials[id] || null;
}

/**
 * 搜索教程
 */
export function searchTutorials(keyword) {
  const results = [];
  const lowerKeyword = keyword.toLowerCase();
  
  for (const tutorial of Object.values(tutorials)) {
    // 搜索标题和描述
    if (
      tutorial.title?.toLowerCase().includes(lowerKeyword) ||
      tutorial.description?.toLowerCase().includes(lowerKeyword)
    ) {
      results.push(tutorial);
      continue;
    }
    
    // 搜索步骤内容
    if (tutorial.steps) {
      for (const step of tutorial.steps) {
        if (
          step.title?.toLowerCase().includes(lowerKeyword) ||
          step.content?.toLowerCase().includes(lowerKeyword)
        ) {
          results.push(tutorial);
          break;
        }
      }
    }
    
    // 搜索FAQ
    if (tutorial.faq) {
      for (const faq of tutorial.faq) {
        if (
          faq.question?.toLowerCase().includes(lowerKeyword) ||
          faq.answer?.toLowerCase().includes(lowerKeyword)
        ) {
          results.push(tutorial);
          break;
        }
      }
    }
  }
  
  return results;
}
