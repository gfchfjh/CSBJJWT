<template>
  <el-dialog
    v-model="visible"
    :title="tutorial.title"
    width="900px"
    top="5vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="tutorial-container">
      <!-- 步骤导航 -->
      <el-steps
        :active="currentStep"
        finish-status="success"
        align-center
        class="tutorial-steps"
      >
        <el-step
          v-for="(step, index) in tutorial.steps"
          :key="index"
          :title="`步骤${index + 1}`"
          :description="step.title"
        />
      </el-steps>

      <!-- 步骤内容 -->
      <div class="step-content">
        <div class="step-header">
          <h3>
            <el-icon><Document /></el-icon>
            {{ tutorial.steps[currentStep].title }}
          </h3>
          <el-tag v-if="currentStep === tutorial.steps.length - 1" type="success">
            最后一步
          </el-tag>
        </div>
        
        <div class="step-description">
          <p v-html="tutorial.steps[currentStep].description"></p>
        </div>
        
        <!-- 截图 -->
        <div v-if="tutorial.steps[currentStep].image" class="step-image">
          <el-image
            :src="tutorial.steps[currentStep].image"
            fit="contain"
            :preview-src-list="[tutorial.steps[currentStep].image]"
            preview-teleported
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
                <span>图片加载中...</span>
              </div>
            </template>
          </el-image>
          <p class="image-caption">{{ tutorial.steps[currentStep].imageCaption }}</p>
        </div>
        
        <!-- 代码示例 -->
        <div v-if="tutorial.steps[currentStep].code" class="step-code">
          <el-alert
            type="info"
            :closable="false"
            :title="tutorial.steps[currentStep].codeTitle || '代码示例'"
          >
            <pre>{{ tutorial.steps[currentStep].code }}</pre>
          </el-alert>
        </div>
        
        <!-- 注意事项 -->
        <div v-if="tutorial.steps[currentStep].notes" class="step-notes">
          <el-alert
            type="warning"
            :closable="false"
            title="⚠️ 注意事项"
          >
            <ul>
              <li v-for="(note, index) in tutorial.steps[currentStep].notes" :key="index">
                {{ note }}
              </li>
            </ul>
          </el-alert>
        </div>
        
        <!-- 提示 -->
        <div v-if="tutorial.steps[currentStep].tips" class="step-tips">
          <el-alert
            type="success"
            :closable="false"
            title="💡 小提示"
          >
            <ul>
              <li v-for="(tip, index) in tutorial.steps[currentStep].tips" :key="index">
                {{ tip }}
              </li>
            </ul>
          </el-alert>
        </div>
      </div>

      <!-- 进度指示器 -->
      <div class="progress-indicator">
        <span class="progress-text">
          进度: {{ currentStep + 1 }} / {{ tutorial.steps.length }}
        </span>
        <el-progress
          :percentage="((currentStep + 1) / tutorial.steps.length) * 100"
          :stroke-width="8"
          :show-text="false"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button
          :disabled="currentStep === 0"
          @click="previousStep"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一步
        </el-button>
        
        <el-button
          v-if="currentStep < tutorial.steps.length - 1"
          type="primary"
          @click="nextStep"
        >
          下一步
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
        
        <el-button
          v-else
          type="success"
          @click="completeTutorial"
        >
          <el-icon><Check /></el-icon>
          完成教程
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Picture,
  ArrowLeft,
  ArrowRight,
  Check
} from '@element-plus/icons-vue'

const visible = ref(false)
const currentStep = ref(0)

// 教程数据
const tutorial = ref({
  title: '如何获取KOOK Cookie',
  steps: []
})

// 预定义的教程模板
const tutorials = {
  cookie: {
    title: '📖 如何获取KOOK Cookie',
    steps: [
      {
        title: '安装浏览器扩展',
        description: '打开Chrome应用商店，搜索<strong>"EditThisCookie"</strong>扩展并安装。<br>这是最简单的Cookie导出工具。',
        image: '/tutorials/cookie-step1.png',
        imageCaption: '在Chrome应用商店搜索EditThisCookie',
        tips: [
          '如果无法访问Chrome应用商店，可以使用其他Cookie导出扩展',
          '推荐使用EditThisCookie，界面简单易用',
          'Firefox用户可以使用"Cookie Quick Manager"扩展'
        ]
      },
      {
        title: '登录KOOK网页版',
        description: '打开浏览器，访问 <strong>https://www.kookapp.cn</strong> 并登录您的账号。<br>确保登录成功后再进行下一步。',
        image: '/tutorials/cookie-step2.png',
        imageCaption: '在KOOK网页版登录您的账号',
        notes: [
          '必须使用网页版登录，不能使用客户端',
          '登录后会看到服务器列表和频道',
          '如果需要验证码，请先完成验证'
        ]
      },
      {
        title: '导出Cookie',
        description: '点击浏览器右上角的<strong>EditThisCookie图标</strong>，在弹出菜单中：<br>1. 点击<strong>"Export"</strong>按钮<br>2. 选择<strong>"JSON"</strong>格式<br>3. Cookie会自动复制到剪贴板',
        image: '/tutorials/cookie-step3.png',
        imageCaption: '点击Export → JSON',
        code: '[{"name": "token", "value": "xxx", "domain": ".kookapp.cn", ...}]',
        codeTitle: '导出的Cookie应该类似这样（JSON数组格式）',
        tips: [
          '导出后会看到一串JSON代码',
          '不要修改Cookie内容，直接复制即可',
          '如果复制失败，可以手动选中并复制'
        ]
      },
      {
        title: '粘贴Cookie到系统',
        description: '回到本系统的配置向导，在<strong>Cookie输入框</strong>中粘贴刚才复制的Cookie。<br>系统会自动验证Cookie的有效性。',
        image: '/tutorials/cookie-step4.png',
        imageCaption: '将Cookie粘贴到输入框',
        notes: [
          '粘贴后会自动验证，请等待验证完成',
          '如果提示"Cookie无效"，请重新导出',
          '确保Cookie中包含token字段'
        ],
        tips: [
          '也可以直接拖拽Cookie文件到上传区域',
          '系统支持JSON、Netscape、Header多种格式',
          '验证成功后，可以点击"下一步"继续配置'
        ]
      }
    ]
  },
  
  discord: {
    title: '📖 如何创建Discord Webhook',
    steps: [
      {
        title: '打开Discord服务器设置',
        description: '在Discord中，找到您想要接收消息的<strong>服务器</strong>，右键点击服务器图标，选择<strong>"服务器设置"</strong>。',
        image: '/tutorials/discord-step1.png',
        imageCaption: '右键服务器 → 服务器设置',
        notes: [
          '您必须有管理员权限才能创建Webhook',
          '如果没有权限，请联系服务器管理员'
        ]
      },
      {
        title: '进入整合设置',
        description: '在服务器设置页面，找到左侧菜单中的<strong>"整合"</strong>（Integrations）选项并点击。',
        image: '/tutorials/discord-step2.png',
        imageCaption: '点击左侧的"整合"菜单',
      },
      {
        title: '创建Webhook',
        description: '点击<strong>"创建Webhook"</strong>按钮，然后：<br>1. 为Webhook起个名字（例如："KOOK消息转发"）<br>2. 选择要接收消息的<strong>频道</strong><br>3. 可选：上传自定义头像',
        image: '/tutorials/discord-step3.png',
        imageCaption: '填写Webhook信息',
        tips: [
          'Webhook名称会显示为消息发送者',
          '可以为不同频道创建多个Webhook',
          '头像会显示在每条转发消息旁边'
        ]
      },
      {
        title: '复制Webhook URL',
        description: '创建完成后，点击<strong>"复制Webhook URL"</strong>按钮。<br>URL格式类似：<code>https://discord.com/api/webhooks/123456789/abcdefg...</code>',
        image: '/tutorials/discord-step4.png',
        imageCaption: '复制Webhook URL',
        code: 'https://discord.com/api/webhooks/1234567890/ABCdefGHIjklMNOpqrsTUVwxyz',
        codeTitle: 'Webhook URL示例',
        notes: [
          '请妥善保管Webhook URL，不要泄露给他人',
          '任何拥有URL的人都可以向该频道发送消息',
          '如果URL泄露，请删除Webhook并重新创建'
        ]
      },
      {
        title: '粘贴到系统并测试',
        description: '返回本系统，将Webhook URL粘贴到<strong>Discord配置</strong>中，然后点击<strong>"测试连接"</strong>按钮。<br>如果配置正确，Discord频道会收到一条测试消息。',
        image: '/tutorials/discord-step5.png',
        imageCaption: '粘贴URL并测试连接',
        tips: [
          '测试成功后会在Discord频道看到测试消息',
          '如果测试失败，请检查URL是否完整复制',
          '可以创建多个Webhook用于不同频道'
        ]
      }
    ]
  },
  
  telegram: {
    title: '📖 如何创建Telegram Bot',
    steps: [
      {
        title: '与BotFather对话',
        description: '在Telegram中搜索<strong>"@BotFather"</strong>（官方Bot创建工具），点击"Start"开始对话。',
        image: '/tutorials/telegram-step1.png',
        imageCaption: '搜索并打开@BotFather',
        notes: [
          'BotFather是Telegram官方提供的Bot管理工具',
          '注意是@BotFather，不是其他假冒的Bot',
          '如果搜不到，请检查网络连接'
        ]
      },
      {
        title: '创建新Bot',
        description: '发送命令<strong>/newbot</strong>给BotFather，然后按照提示：<br>1. 输入Bot的<strong>显示名称</strong>（例如："KOOK消息转发"）<br>2. 输入Bot的<strong>用户名</strong>（必须以"bot"结尾，例如："kook_forwarder_bot"）',
        image: '/tutorials/telegram-step2.png',
        imageCaption: '发送/newbot命令',
        code: '/newbot\n\nBot名称: KOOK消息转发\nBot用户名: kook_forwarder_bot',
        codeTitle: '对话示例',
        tips: [
          'Bot用户名必须全网唯一，如果被占用需要换一个',
          '用户名只能包含字母、数字和下划线',
          '用户名必须以"bot"或"_bot"结尾'
        ]
      },
      {
        title: '获取Bot Token',
        description: '创建成功后，BotFather会返回一个<strong>Token</strong>（API密钥）。<br>格式类似：<code>1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code><br><br>请妥善保管此Token！',
        image: '/tutorials/telegram-step3.png',
        imageCaption: '复制Bot Token',
        code: '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz',
        codeTitle: 'Bot Token示例',
        notes: [
          '⚠️ Token相当于密码，不要泄露给他人',
          '任何拥有Token的人都可以控制您的Bot',
          '如果Token泄露，请使用/revoke命令撤销并重新生成'
        ]
      },
      {
        title: '将Bot添加到群组',
        description: '在Telegram中：<br>1. 打开您想要接收消息的<strong>群组</strong><br>2. 点击群组名称，进入群组信息页<br>3. 点击<strong>"添加成员"</strong><br>4. 搜索您的Bot用户名并添加',
        image: '/tutorials/telegram-step4.png',
        imageCaption: '将Bot添加到群组',
        tips: [
          '添加后，Bot会显示在群组成员列表中',
          '确保Bot有发送消息的权限',
          '私聊也可以，但需要先发送/start给Bot'
        ]
      },
      {
        title: '获取Chat ID',
        description: '回到本系统，填入<strong>Bot Token</strong>，然后点击<strong>"🔍 自动获取"</strong>按钮。<br>系统会自动检测Bot可以访问的所有群组，选择对应的群组即可。',
        image: '/tutorials/telegram-step5.png',
        imageCaption: '自动获取Chat ID',
        code: '-1001234567890',
        codeTitle: 'Chat ID示例（通常是负数，以-100开头）',
        notes: [
          '如果自动获取失败，请先在群组中发送任意消息',
          'Bot必须在群组中才能检测到Chat ID',
          '群组的Chat ID通常以-100开头'
        ],
        tips: [
          '也可以手动获取：向Bot发送任意消息，查看返回的Chat ID',
          '私聊的Chat ID是正数',
          '频道的Chat ID以-100开头，且需要Bot是管理员'
        ]
      },
      {
        title: '测试连接',
        description: '填写完<strong>Bot Token</strong>和<strong>Chat ID</strong>后，点击<strong>"🧪 测试连接"</strong>按钮。<br>如果配置正确，群组会收到一条测试消息。',
        image: '/tutorials/telegram-step6.png',
        imageCaption: '测试Bot连接',
        tips: [
          '测试成功后，群组会收到"✅ KOOK消息转发系统测试消息"',
          '如果测试失败，请检查Token和Chat ID是否正确',
          '确保Bot在群组中，且有发送消息权限'
        ]
      }
    ]
  },
  
  feishu: {
    title: '📖 如何创建飞书自建应用',
    steps: [
      {
        title: '访问飞书开放平台',
        description: '打开浏览器，访问<strong>https://open.feishu.cn</strong>，使用您的飞书账号登录。',
        image: '/tutorials/feishu-step1.png',
        imageCaption: '访问飞书开放平台',
        notes: [
          '需要企业管理员或开发者权限',
          '个人账号可能无法创建应用'
        ]
      },
      {
        title: '创建自建应用',
        description: '点击<strong>"创建企业自建应用"</strong>按钮，填写：<br>1. 应用名称（例如："KOOK消息转发"）<br>2. 应用描述<br>3. 上传应用图标（可选）',
        image: '/tutorials/feishu-step2.png',
        imageCaption: '创建自建应用',
      },
      {
        title: '开启机器人能力',
        description: '创建完成后，进入应用详情页：<br>1. 点击左侧菜单<strong>"添加应用能力"</strong><br>2. 选择<strong>"机器人"</strong><br>3. 点击<strong>"启用"</strong>',
        image: '/tutorials/feishu-step3.png',
        imageCaption: '开启机器人能力',
      },
      {
        title: '获取App ID和Secret',
        description: '在<strong>"凭证与基础信息"</strong>页面，可以看到：<br>1. <strong>App ID</strong>（类似：cli_a1b2c3d4e5f6g7h8）<br>2. <strong>App Secret</strong>（点击"查看"显示）',
        image: '/tutorials/feishu-step4.png',
        imageCaption: '复制App ID和App Secret',
        code: 'App ID: cli_a1b2c3d4e5f6g7h8\nApp Secret: ABCdefGHIjklMNOpqrs',
        codeTitle: '凭证示例',
        notes: [
          '⚠️ App Secret相当于密码，不要泄露',
          'App ID是公开的，可以分享',
          'App Secret只显示一次，请务必保存'
        ]
      },
      {
        title: '配置权限',
        description: '在<strong>"权限管理"</strong>页面，开启以下权限：<br>• 获取用户发给机器人的单聊消息<br>• 获取群组中所有消息<br>• 以应用身份发消息<br>• 获取群信息',
        image: '/tutorials/feishu-step5.png',
        imageCaption: '配置应用权限',
        notes: [
          '权限配置后需要重新发布应用',
          '缺少权限会导致功能异常'
        ]
      },
      {
        title: '将Bot添加到群组',
        description: '在飞书群聊中：<br>1. 点击右上角<strong>"..."</strong><br>2. 选择<strong>"设置"</strong> → <strong>"群机器人"</strong><br>3. 点击<strong>"添加机器人"</strong><br>4. 搜索并添加您创建的应用',
        image: '/tutorials/feishu-step6.png',
        imageCaption: '添加Bot到群组',
      },
      {
        title: '填写配置并测试',
        description: '返回本系统，填写：<br>• <strong>App ID</strong><br>• <strong>App Secret</strong><br><br>然后点击<strong>"🧪 测试连接"</strong>按钮。',
        image: '/tutorials/feishu-step7.png',
        imageCaption: '填写配置并测试',
        tips: [
          '测试成功后，系统会尝试发送测试消息',
          '如果失败，请检查权限配置',
          '确保Bot已添加到至少一个群组'
        ]
      }
    ]
  }
}

// 方法
const show = (type = 'cookie') => {
  if (tutorials[type]) {
    tutorial.value = tutorials[type]
    visible.value = true
    currentStep.value = 0
  } else {
    ElMessage.warning(`未找到教程: ${type}`)
  }
}

const nextStep = () => {
  if (currentStep.value < tutorial.value.steps.length - 1) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const completeTutorial = () => {
  ElMessage.success('✅ 教程已完成，祝您使用愉快！')
  visible.value = false
}

// 暴露方法供父组件调用
defineExpose({ show })
</script>

<style scoped lang="scss">
.tutorial-container {
  .tutorial-steps {
    margin-bottom: 30px;
  }
  
  .step-content {
    min-height: 400px;
    
    .step-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 2px solid #e4e7ed;
      
      h3 {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
      }
    }
    
    .step-description {
      margin-bottom: 20px;
      
      p {
        font-size: 15px;
        line-height: 1.8;
        color: #606266;
        margin: 0;
        
        :deep(strong) {
          color: #409eff;
          font-weight: 600;
        }
        
        :deep(code) {
          padding: 2px 6px;
          background: #f5f7fa;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: #e6a23c;
        }
      }
    }
    
    .step-image {
      margin: 20px 0;
      text-align: center;
      
      .el-image {
        max-width: 100%;
        border-radius: 8px;
        border: 1px solid #e4e7ed;
        overflow: hidden;
      }
      
      .image-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        background: #f5f7fa;
        
        .el-icon {
          font-size: 48px;
          color: #c0c4cc;
          margin-bottom: 10px;
        }
        
        span {
          color: #909399;
        }
      }
      
      .image-caption {
        margin-top: 10px;
        font-size: 14px;
        color: #909399;
      }
    }
    
    .step-code {
      margin: 20px 0;
      
      pre {
        margin: 10px 0 0 0;
        padding: 15px;
        background: #f5f7fa;
        border-radius: 4px;
        border-left: 4px solid #409eff;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #303133;
        overflow-x: auto;
      }
    }
    
    .step-notes {
      margin: 20px 0;
      
      ul {
        margin: 10px 0;
        padding-left: 20px;
        
        li {
          margin: 8px 0;
          color: #e6a23c;
          line-height: 1.6;
        }
      }
    }
    
    .step-tips {
      margin: 20px 0;
      
      ul {
        margin: 10px 0;
        padding-left: 20px;
        
        li {
          margin: 8px 0;
          color: #67c23a;
          line-height: 1.6;
        }
      }
    }
  }
  
  .progress-indicator {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e4e7ed;
    
    .progress-text {
      display: block;
      text-align: center;
      margin-bottom: 10px;
      font-size: 14px;
      color: #909399;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
