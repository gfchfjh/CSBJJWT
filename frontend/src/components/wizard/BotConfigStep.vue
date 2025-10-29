<template>
  <div class="bot-config-step">
    <div class="step-header">
      <h2>🤖 第2步：配置转发Bot</h2>
      <p>至少配置一个转发目标（Discord/Telegram/飞书）</p>
    </div>

    <el-tabs v-model="activePlatform" type="border-card">
      <!-- Discord -->
      <el-tab-pane label="Discord" name="discord">
        <template #label>
          <span class="tab-label">
            <img src="/images/discord-icon.png" alt="Discord" class="platform-icon" />
            Discord
          </span>
        </template>

        <div class="platform-content">
          <el-alert
            title="📘 Discord Webhook配置"
            type="info"
            :closable="false"
            show-icon
          >
            <p>Webhook是Discord提供的最简单的消息发送方式</p>
          </el-alert>

          <el-button 
            type="text" 
            @click="showDiscordTutorial = true"
            style="margin: 10px 0;"
          >
            <el-icon><QuestionFilled /></el-icon>
            如何获取Discord Webhook URL？
          </el-button>

          <el-form 
            :model="discordForm"
            label-width="120px"
            style="margin-top: 20px;"
          >
            <el-form-item label="Webhook名称">
              <el-input 
                v-model="discordForm.name"
                placeholder="例如：游戏公告Bot"
              />
            </el-form-item>

            <el-form-item label="Webhook URL">
              <el-input 
                v-model="discordForm.webhook_url"
                placeholder="https://discord.com/api/webhooks/..."
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                @click="testDiscordWebhook"
                :loading="testing.discord"
              >
                测试连接
              </el-button>
              <el-button 
                @click="saveDiscordBot"
                :disabled="!discordForm.webhook_url"
              >
                保存配置
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 已配置的Webhook列表 -->
          <div class="saved-bots" v-if="configuredBots.discord.length > 0">
            <h4>已配置的Discord Webhook：</h4>
            <el-card 
              v-for="(bot, index) in configuredBots.discord"
              :key="index"
              class="bot-card"
            >
              <div class="bot-info">
                <div>
                  <strong>{{ bot.name }}</strong>
                  <p class="bot-url">{{ bot.webhook_url }}</p>
                  <el-tag 
                    :type="bot.tested ? 'success' : 'info'"
                    size="small"
                  >
                    {{ bot.tested ? '✅ 已测试' : '未测试' }}
                  </el-tag>
                </div>
                <div class="bot-actions">
                  <el-button size="small" @click="editBot('discord', index)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteBot('discord', index)">
                    删除
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- Telegram -->
      <el-tab-pane label="Telegram" name="telegram">
        <template #label>
          <span class="tab-label">
            <img src="/images/telegram-icon.png" alt="Telegram" class="platform-icon" />
            Telegram
          </span>
        </template>

        <div class="platform-content">
          <el-alert
            title="📱 Telegram Bot配置"
            type="info"
            :closable="false"
            show-icon
          >
            <p>需要先创建Telegram Bot并获取Token</p>
          </el-alert>

          <el-button 
            type="text" 
            @click="showTelegramTutorial = true"
            style="margin: 10px 0;"
          >
            <el-icon><QuestionFilled /></el-icon>
            如何创建Telegram Bot？
          </el-button>

          <el-form 
            :model="telegramForm"
            label-width="120px"
            style="margin-top: 20px;"
          >
            <el-form-item label="Bot名称">
              <el-input 
                v-model="telegramForm.name"
                placeholder="例如：KOOK转发Bot"
              />
            </el-form-item>

            <el-form-item label="Bot Token">
              <el-input 
                v-model="telegramForm.bot_token"
                placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              />
            </el-form-item>

            <el-form-item label="Chat ID">
              <el-input 
                v-model="telegramForm.chat_id"
                placeholder="-1001234567890"
              >
                <template #append>
                  <el-button 
                    @click="autoGetChatId"
                    :loading="gettingChatId"
                  >
                    自动获取
                  </el-button>
                </template>
              </el-input>
              <div class="form-tip">
                将Bot添加到群组后，点击"自动获取"按钮
              </div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                @click="testTelegramBot"
                :loading="testing.telegram"
              >
                测试连接
              </el-button>
              <el-button 
                @click="saveTelegramBot"
                :disabled="!telegramForm.bot_token || !telegramForm.chat_id"
              >
                保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 飞书 -->
      <el-tab-pane label="飞书" name="feishu">
        <template #label>
          <span class="tab-label">
            <img src="/images/feishu-icon.png" alt="飞书" class="platform-icon" />
            飞书
          </span>
        </template>

        <div class="platform-content">
          <el-alert
            title="🕊️ 飞书应用配置"
            type="info"
            :closable="false"
            show-icon
          >
            <p>需要在飞书开放平台创建自建应用</p>
          </el-alert>

          <el-button 
            type="text" 
            @click="showFeishuTutorial = true"
            style="margin: 10px 0;"
          >
            <el-icon><QuestionFilled /></el-icon>
            如何创建飞书应用？
          </el-button>

          <el-form 
            :model="feishuForm"
            label-width="120px"
            style="margin-top: 20px;"
          >
            <el-form-item label="应用名称">
              <el-input 
                v-model="feishuForm.name"
                placeholder="例如：KOOK消息转发"
              />
            </el-form-item>

            <el-form-item label="App ID">
              <el-input 
                v-model="feishuForm.app_id"
                placeholder="cli_a1b2c3d4e5f6g7h8"
              />
            </el-form-item>

            <el-form-item label="App Secret">
              <el-input 
                v-model="feishuForm.app_secret"
                placeholder="ABCdefGHIjklMNOpqrsTUVwxyz"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item label="Webhook（可选）">
              <el-input 
                v-model="feishuForm.webhook_url"
                placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                @click="testFeishuBot"
                :loading="testing.feishu"
              >
                测试连接
              </el-button>
              <el-button 
                @click="saveFeishuBot"
                :disabled="!feishuForm.app_id || !feishuForm.app_secret"
              >
                保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 底部按钮 -->
    <div class="step-footer">
      <el-button @click="handlePrev">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      
      <el-button 
        type="primary" 
        @click="handleNext"
        :disabled="!hasConfiguredBot"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>

    <!-- 教程对话框 -->
    <el-dialog v-model="showDiscordTutorial" title="Discord Webhook获取教程" width="700px">
      <!-- Discord教程内容 -->
    </el-dialog>

    <el-dialog v-model="showTelegramTutorial" title="Telegram Bot创建教程" width="700px">
      <!-- Telegram教程内容 -->
    </el-dialog>

    <el-dialog v-model="showFeishuTutorial" title="飞书应用创建教程" width="700px">
      <!-- 飞书教程内容 -->
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

const activePlatform = ref('discord')

const discordForm = reactive({
  name: '',
  webhook_url: ''
})

const telegramForm = reactive({
  name: '',
  bot_token: '',
  chat_id: ''
})

const feishuForm = reactive({
  name: '',
  app_id: '',
  app_secret: '',
  webhook_url: ''
})

const configuredBots = reactive({
  discord: [],
  telegram: [],
  feishu: []
})

const testing = reactive({
  discord: false,
  telegram: false,
  feishu: false
})

const gettingChatId = ref(false)
const showDiscordTutorial = ref(false)
const showTelegramTutorial = ref(false)
const showFeishuTutorial = ref(false)

const hasConfiguredBot = computed(() => {
  return configuredBots.discord.length > 0 ||
         configuredBots.telegram.length > 0 ||
         configuredBots.feishu.length > 0
})

// Discord方法
const testDiscordWebhook = async () => {
  if (!discordForm.webhook_url) {
    ElMessage.error('请输入Webhook URL')
    return
  }

  testing.discord = true
  try {
    const response = await api.post('/api/bots/test/discord', {
      webhook_url: discordForm.webhook_url
    })

    if (response.data.success) {
      ElMessage.success('✅ Discord连接测试成功！')
      discordForm.tested = true
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  } finally {
    testing.discord = false
  }
}

const saveDiscordBot = () => {
  configuredBots.discord.push({ ...discordForm })
  Object.assign(discordForm, { name: '', webhook_url: '', tested: false })
  ElMessage.success('Discord配置已保存')
}

// Telegram方法
const autoGetChatId = async () => {
  if (!telegramForm.bot_token) {
    ElMessage.error('请先输入Bot Token')
    return
  }

  gettingChatId.value = true
  try {
    const response = await api.post('/api/telegram/get-chat-id', {
      bot_token: telegramForm.bot_token
    })

    if (response.data.success) {
      telegramForm.chat_id = response.data.chat_id
      ElMessage.success('✅ Chat ID获取成功！')
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('获取失败：' + error.message)
  } finally {
    gettingChatId.value = false
  }
}

const testTelegramBot = async () => {
  testing.telegram = true
  try {
    const response = await api.post('/api/bots/test/telegram', {
      bot_token: telegramForm.bot_token,
      chat_id: telegramForm.chat_id
    })

    if (response.data.success) {
      ElMessage.success('✅ Telegram连接测试成功！')
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  } finally {
    testing.telegram = false
  }
}

const saveTelegramBot = () => {
  configuredBots.telegram.push({ ...telegramForm })
  Object.assign(telegramForm, { name: '', bot_token: '', chat_id: '' })
  ElMessage.success('Telegram配置已保存')
}

// 飞书方法
const testFeishuBot = async () => {
  testing.feishu = true
  try {
    const response = await api.post('/api/bots/test/feishu', {
      app_id: feishuForm.app_id,
      app_secret: feishuForm.app_secret
    })

    if (response.data.success) {
      ElMessage.success('✅ 飞书连接测试成功！')
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  } finally {
    testing.feishu = false
  }
}

const saveFeishuBot = () => {
  configuredBots.feishu.push({ ...feishuForm })
  Object.assign(feishuForm, { name: '', app_id: '', app_secret: '', webhook_url: '' })
  ElMessage.success('飞书配置已保存')
}

// 通用方法
const editBot = (platform, index) => {
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能')
}

const deleteBot = (platform, index) => {
  configuredBots[platform].splice(index, 1)
  ElMessage.success('已删除')
}

const handlePrev = () => {
  emit('prev')
}

const handleNext = () => {
  if (!hasConfiguredBot.value) {
    ElMessage.warning('请至少配置一个转发Bot')
    return
  }

  emit('next', configuredBots)
}
</script>

<style scoped>
.bot-config-step {
  max-width: 800px;
  margin: 0 auto;
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 10px 0;
}

.step-header p {
  color: #909399;
  font-size: 14px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-icon {
  width: 20px;
  height: 20px;
}

.platform-content {
  padding: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.saved-bots {
  margin-top: 30px;
}

.saved-bots h4 {
  margin-bottom: 15px;
  color: #303133;
}

.bot-card {
  margin-bottom: 10px;
}

.bot-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bot-info strong {
  font-size: 16px;
  color: #303133;
}

.bot-url {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
  word-break: break-all;
}

.bot-actions {
  display: flex;
  gap: 10px;
}

.step-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #DCDFE6;
  display: flex;
  justify-content: space-between;
}
</style>
