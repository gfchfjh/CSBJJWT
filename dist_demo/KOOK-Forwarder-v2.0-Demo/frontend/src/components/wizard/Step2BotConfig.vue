<template>
  <div class="step2-bot-config">
    <h2>🤖 步骤2: 配置转发Bot</h2>
    <p class="step-desc">选择要转发的目标平台，至少配置一个</p>

    <!-- 平台选择卡片 -->
    <el-row :gutter="20" class="platform-cards">
      <!-- Discord -->
      <el-col :span="8">
        <el-card
          :class="['platform-card', { active: platforms.discord.enabled }]"
          shadow="hover"
          @click="platforms.discord.enabled = !platforms.discord.enabled"
        >
          <div class="platform-header">
            <img src="/icons/discord.svg" alt="Discord" class="platform-icon" />
            <h3>Discord</h3>
          </div>
          <p class="platform-desc">使用Webhook转发消息</p>
          <el-checkbox v-model="platforms.discord.enabled" size="large">
            启用Discord转发
          </el-checkbox>
        </el-card>
      </el-col>

      <!-- Telegram -->
      <el-col :span="8">
        <el-card
          :class="['platform-card', { active: platforms.telegram.enabled }]"
          shadow="hover"
          @click="platforms.telegram.enabled = !platforms.telegram.enabled"
        >
          <div class="platform-header">
            <img src="/icons/telegram.svg" alt="Telegram" class="platform-icon" />
            <h3>Telegram</h3>
          </div>
          <p class="platform-desc">通过Bot API发送消息</p>
          <el-checkbox v-model="platforms.telegram.enabled" size="large">
            启用Telegram转发
          </el-checkbox>
        </el-card>
      </el-col>

      <!-- 飞书 -->
      <el-col :span="8">
        <el-card
          :class="['platform-card', { active: platforms.feishu.enabled }]"
          shadow="hover"
          @click="platforms.feishu.enabled = !platforms.feishu.enabled"
        >
          <div class="platform-header">
            <img src="/icons/feishu.svg" alt="飞书" class="platform-icon" />
            <h3>飞书</h3>
          </div>
          <p class="platform-desc">使用自建应用发送</p>
          <el-checkbox v-model="platforms.feishu.enabled" size="large">
            启用飞书转发
          </el-checkbox>
        </el-card>
      </el-col>
    </el-row>

    <!-- 配置表单 -->
    <el-divider />

    <el-form :model="botForms" label-position="top">
      <!-- Discord配置 -->
      <div v-if="platforms.discord.enabled" class="bot-config-section">
        <h3>
          <el-icon><Connection /></el-icon>
          Discord Webhook配置
          <el-link type="primary" @click="openDiscordGuide" style="margin-left: 10px">
            查看教程
          </el-link>
        </h3>
        
        <el-form-item label="Webhook名称（备注）">
          <el-input
            v-model="botForms.discord.name"
            placeholder="例如：游戏公告Bot"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="Webhook URL">
          <el-input
            v-model="botForms.discord.webhookUrl"
            placeholder="https://discord.com/api/webhooks/..."
            size="large"
          >
            <template #append>
              <el-button @click="testDiscordWebhook" :loading="testing.discord">
                测试连接
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </div>

      <!-- Telegram配置 -->
      <div v-if="platforms.telegram.enabled" class="bot-config-section">
        <h3>
          <el-icon><Connection /></el-icon>
          Telegram Bot配置
          <el-link type="primary" @click="openTelegramGuide" style="margin-left: 10px">
            查看教程
          </el-link>
        </h3>
        
        <el-form-item label="Bot名称（备注）">
          <el-input
            v-model="botForms.telegram.name"
            placeholder="例如：游戏公告TG Bot"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="Bot Token">
          <el-input
            v-model="botForms.telegram.botToken"
            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="Chat ID">
          <el-input
            v-model="botForms.telegram.chatId"
            placeholder="-1001234567890"
            size="large"
          >
            <template #append>
              <el-button @click="autoDetectChatId" :loading="detecting">
                自动获取
              </el-button>
            </template>
          </el-input>
          <template #extra>
            <el-text size="small" type="info">
              点击"自动获取"后，请在群组中发送任意消息
            </el-text>
          </template>
        </el-form-item>

        <el-button @click="testTelegramBot" :loading="testing.telegram" style="margin-top: 10px">
          <el-icon><Check /></el-icon>
          测试连接
        </el-button>
      </div>

      <!-- 飞书配置 -->
      <div v-if="platforms.feishu.enabled" class="bot-config-section">
        <h3>
          <el-icon><Connection /></el-icon>
          飞书应用配置
          <el-link type="primary" @click="openFeishuGuide" style="margin-left: 10px">
            查看教程
          </el-link>
        </h3>
        
        <el-form-item label="应用名称（备注）">
          <el-input
            v-model="botForms.feishu.name"
            placeholder="例如：游戏公告飞书Bot"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="App ID">
          <el-input
            v-model="botForms.feishu.appId"
            placeholder="cli_a1b2c3d4e5f6g7h8"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="App Secret">
          <el-input
            v-model="botForms.feishu.appSecret"
            placeholder="ABCdefGHIjklMNOpqrs"
            type="password"
            show-password
            size="large"
          />
        </el-form-item>

        <el-button @click="testFeishuApp" :loading="testing.feishu" style="margin-top: 10px">
          <el-icon><Check /></el-icon>
          测试连接
        </el-button>
      </div>
    </el-form>

    <!-- 底部操作 -->
    <div class="step-actions">
      <el-button size="large" @click="$emit('prev')">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      
      <el-button
        type="primary"
        size="large"
        :disabled="!hasEnabledPlatform"
        :loading="saving"
        @click="handleNext"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Connection,
  Check,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  accountId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['next', 'prev'])

// 平台启用状态
const platforms = ref({
  discord: { enabled: false },
  telegram: { enabled: false },
  feishu: { enabled: false }
})

// Bot表单数据
const botForms = ref({
  discord: {
    name: '',
    webhookUrl: ''
  },
  telegram: {
    name: '',
    botToken: '',
    chatId: ''
  },
  feishu: {
    name: '',
    appId: '',
    appSecret: ''
  }
})

// 测试状态
const testing = ref({
  discord: false,
  telegram: false,
  feishu: false
})

const detecting = ref(false)
const saving = ref(false)

// 是否至少启用了一个平台
const hasEnabledPlatform = computed(() => {
  return Object.values(platforms.value).some(p => p.enabled)
})

// 测试Discord Webhook
const testDiscordWebhook = async () => {
  if (!botForms.value.discord.webhookUrl) {
    ElMessage.warning('请先输入Webhook URL')
    return
  }
  
  testing.value.discord = true
  
  try {
    const response = await api.post('/api/bots/test-discord', {
      webhook_url: botForms.value.discord.webhookUrl
    })
    
    if (response.data.success) {
      ElMessage.success('✅ Discord Webhook测试成功！')
    } else {
      ElMessage.error('Webhook测试失败：' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + (error.response?.data?.message || error.message))
  } finally {
    testing.value.discord = false
  }
}

// 测试Telegram Bot
const testTelegramBot = async () => {
  if (!botForms.value.telegram.botToken) {
    ElMessage.warning('请先输入Bot Token')
    return
  }
  
  testing.value.telegram = true
  
  try {
    const response = await api.post('/api/bots/test-telegram', {
      bot_token: botForms.value.telegram.botToken,
      chat_id: botForms.value.telegram.chatId
    })
    
    if (response.data.success) {
      ElMessage.success('✅ Telegram Bot测试成功！')
    } else {
      ElMessage.error('Bot测试失败：' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + (error.response?.data?.message || error.message))
  } finally {
    testing.value.telegram = false
  }
}

// 自动获取Chat ID
const autoDetectChatId = async () => {
  if (!botForms.value.telegram.botToken) {
    ElMessage.warning('请先输入Bot Token')
    return
  }
  
  detecting.value = true
  
  ElMessage.info({
    message: '请在目标群组中发送任意消息...',
    duration: 3000
  })
  
  try {
    const response = await api.post('/api/telegram/detect-chat-id', {
      bot_token: botForms.value.telegram.botToken
    })
    
    if (response.data.success && response.data.chat_id) {
      botForms.value.telegram.chatId = response.data.chat_id
      ElMessage.success('✅ 自动获取Chat ID成功！')
    } else {
      ElMessage.warning('未检测到新消息，请确保已将Bot添加到群组并发送消息')
    }
  } catch (error) {
    ElMessage.error('获取失败：' + (error.response?.data?.message || error.message))
  } finally {
    detecting.value = false
  }
}

// 测试飞书应用
const testFeishuApp = async () => {
  if (!botForms.value.feishu.appId || !botForms.value.feishu.appSecret) {
    ElMessage.warning('请先输入App ID和App Secret')
    return
  }
  
  testing.value.feishu = true
  
  try {
    const response = await api.post('/api/bots/test-feishu', {
      app_id: botForms.value.feishu.appId,
      app_secret: botForms.value.feishu.appSecret
    })
    
    if (response.data.success) {
      ElMessage.success('✅ 飞书应用测试成功！')
    } else {
      ElMessage.error('应用测试失败：' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + (error.response?.data?.message || error.message))
  } finally {
    testing.value.feishu = false
  }
}

// 下一步
const handleNext = async () => {
  // 验证必填项
  const configs = []
  
  if (platforms.value.discord.enabled) {
    if (!botForms.value.discord.webhookUrl) {
      ElMessage.warning('请完成Discord Webhook配置')
      return
    }
    configs.push({
      platform: 'discord',
      name: botForms.value.discord.name || 'Discord Bot',
      config: {
        webhook_url: botForms.value.discord.webhookUrl
      }
    })
  }
  
  if (platforms.value.telegram.enabled) {
    if (!botForms.value.telegram.botToken || !botForms.value.telegram.chatId) {
      ElMessage.warning('请完成Telegram Bot配置')
      return
    }
    configs.push({
      platform: 'telegram',
      name: botForms.value.telegram.name || 'Telegram Bot',
      config: {
        bot_token: botForms.value.telegram.botToken,
        chat_id: botForms.value.telegram.chatId
      }
    })
  }
  
  if (platforms.value.feishu.enabled) {
    if (!botForms.value.feishu.appId || !botForms.value.feishu.appSecret) {
      ElMessage.warning('请完成飞书应用配置')
      return
    }
    configs.push({
      platform: 'feishu',
      name: botForms.value.feishu.name || '飞书Bot',
      config: {
        app_id: botForms.value.feishu.appId,
        app_secret: botForms.value.feishu.appSecret
      }
    })
  }
  
  // 保存配置
  saving.value = true
  
  try {
    const savedConfigs = []
    
    for (const config of configs) {
      const response = await api.post('/api/bots', config)
      if (response.data.success) {
        savedConfigs.push({
          id: response.data.bot_id,
          ...config
        })
      }
    }
    
    emit('next', {
      botConfigs: savedConfigs
    })
    
  } catch (error) {
    ElMessage.error('保存配置失败：' + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

// 打开教程
const openDiscordGuide = () => window.open('/help/discord-guide', '_blank')
const openTelegramGuide = () => window.open('/help/telegram-guide', '_blank')
const openFeishuGuide = () => window.open('/help/feishu-guide', '_blank')
</script>

<style scoped>
.step2-bot-config h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
}

.step-desc {
  color: #909399;
  margin: 0 0 30px 0;
}

.platform-cards {
  margin-bottom: 30px;
}

.platform-card {
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.platform-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.platform-card.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
}

.platform-header {
  text-align: center;
  margin-bottom: 15px;
}

.platform-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 10px;
}

.platform-header h3 {
  margin: 0;
  font-size: 18px;
}

.platform-desc {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.platform-card :deep(.el-checkbox) {
  display: flex;
  justify-content: center;
}

.bot-config-section {
  margin: 30px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.bot-config-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
}

.step-actions {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
}
</style>
