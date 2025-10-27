<template>
  <div class="step-bots">
    <h2>🤖 配置转发机器人</h2>
    
    <el-alert
      title="至少配置一个平台的机器人才能继续"
      type="info"
      :closable="false"
      class="help-alert"
    />

    <el-tabs v-model="activePlatform" type="card">
      <!-- Discord -->
      <el-tab-pane label="Discord" name="discord">
        <div class="bot-config-form">
          <el-alert
            title="如何创建Discord Webhook？"
            type="info"
            :closable="false"
          >
            <ol>
              <li>进入Discord服务器设置</li>
              <li>集成 → Webhooks</li>
              <li>新建Webhook并复制URL</li>
            </ol>
            <a href="https://support.discord.com/hc/zh-tw/articles/228383668" target="_blank">
              查看详细教程 →
            </a>
          </el-alert>

          <el-form :model="discordForm" label-width="120px" style="margin-top: 20px">
            <el-form-item label="Bot名称">
              <el-input v-model="discordForm.name" placeholder="例如：游戏公告Bot" />
            </el-form-item>
            <el-form-item label="Webhook URL">
              <el-input
                v-model="discordForm.webhook_url"
                placeholder="https://discord.com/api/webhooks/..."
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdd('discord')">
                添加Discord Bot
              </el-button>
              <el-button @click="handleTest('discord')">测试连接</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- Telegram -->
      <el-tab-pane label="Telegram" name="telegram">
        <div class="bot-config-form">
          <el-alert
            title="如何创建Telegram Bot？"
            type="info"
            :closable="false"
          >
            <ol>
              <li>与 @BotFather 对话</li>
              <li>发送 /newbot 创建Bot</li>
              <li>获取Bot Token</li>
              <li>将Bot添加到目标群组</li>
            </ol>
          </el-alert>

          <el-form :model="telegramForm" label-width="120px" style="margin-top: 20px">
            <el-form-item label="Bot名称">
              <el-input v-model="telegramForm.name" placeholder="例如：游戏公告TG Bot" />
            </el-form-item>
            <el-form-item label="Bot Token">
              <el-input
                v-model="telegramForm.token"
                placeholder="1234567890:ABCdefGHI..."
              />
            </el-form-item>
            <el-form-item label="Chat ID">
              <div style="display: flex; gap: 10px">
                <el-input
                  v-model="telegramForm.chat_id"
                  placeholder="-1001234567890"
                  style="flex: 1"
                />
                <el-button 
                  @click="autoGetChatId" 
                  :loading="gettingChatId"
                  :disabled="!telegramForm.token"
                >
                  🔍 自动获取
                </el-button>
              </div>
              <div style="color: #909399; font-size: 12px; margin-top: 5px">
                提示：请先向Bot发送一条消息，然后点击"自动获取"
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdd('telegram')">
                添加Telegram Bot
              </el-button>
              <el-button @click="handleTest('telegram')">测试连接</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 飞书 -->
      <el-tab-pane label="飞书" name="feishu">
        <div class="bot-config-form">
          <el-alert
            title="如何创建飞书应用？"
            type="info"
            :closable="false"
          >
            <ol>
              <li>访问飞书开放平台</li>
              <li>创建企业自建应用</li>
              <li>开启机器人能力</li>
              <li>获取App ID和App Secret</li>
            </ol>
          </el-alert>

          <el-form :model="feishuForm" label-width="120px" style="margin-top: 20px">
            <el-form-item label="Bot名称">
              <el-input v-model="feishuForm.name" placeholder="例如：游戏公告飞书Bot" />
            </el-form-item>
            <el-form-item label="App ID">
              <el-input
                v-model="feishuForm.app_id"
                placeholder="cli_..."
              />
            </el-form-item>
            <el-form-item label="App Secret">
              <el-input
                v-model="feishuForm.app_secret"
                placeholder="..."
              />
            </el-form-item>
            <el-form-item label="Chat ID">
              <el-input
                v-model="feishuForm.chat_id"
                placeholder="oc_..."
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdd('feishu')">
                添加飞书Bot
              </el-button>
              <el-button @click="handleTest('feishu')">测试连接</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div v-if="addedBots.length > 0" class="added-bots">
      <h3>已添加的机器人（{{ addedBots.length }}个）</h3>
      <el-tag
        v-for="bot in addedBots"
        :key="bot.id"
        type="success"
        size="large"
        style="margin-right: 10px"
      >
        {{ bot.platform }} - {{ bot.name }}
      </el-tag>
    </div>

    <div class="action-buttons">
      <el-button @click="emit('prev')">上一步</el-button>
      <el-button @click="handleSkip" plain>
        跳过，稍后配置
      </el-button>
      <el-button
        type="primary"
        :disabled="addedBots.length === 0"
        @click="emit('next')"
      >
        继续
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  addedBots: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['next', 'prev', 'addBot', 'skip'])

const activePlatform = ref('discord')
const gettingChatId = ref(false)

// Bot表单
const discordForm = ref({ name: '', webhook_url: '' })
const telegramForm = ref({ name: '', token: '', chat_id: '' })
const feishuForm = ref({ name: '', app_id: '', app_secret: '', chat_id: '' })

// 添加Bot
const handleAdd = async (platform) => {
  let data = { platform }

  if (platform === 'discord') {
    if (!discordForm.value.name || !discordForm.value.webhook_url) {
      ElMessage.error('请填写完整信息')
      return
    }
    data.name = discordForm.value.name
    data.config = { webhook_url: discordForm.value.webhook_url }
  } else if (platform === 'telegram') {
    if (!telegramForm.value.name || !telegramForm.value.token || !telegramForm.value.chat_id) {
      ElMessage.error('请填写完整信息')
      return
    }
    data.name = telegramForm.value.name
    data.config = {
      token: telegramForm.value.token,
      chat_id: telegramForm.value.chat_id
    }
  } else if (platform === 'feishu') {
    if (!feishuForm.value.name || !feishuForm.value.app_id || !feishuForm.value.app_secret) {
      ElMessage.error('请填写完整信息')
      return
    }
    data.name = feishuForm.value.name
    data.config = {
      app_id: feishuForm.value.app_id,
      app_secret: feishuForm.value.app_secret,
      chat_id: feishuForm.value.chat_id
    }
  }

  emit('addBot', data, platform)

  // 清空表单
  if (platform === 'discord') {
    discordForm.value = { name: '', webhook_url: '' }
  } else if (platform === 'telegram') {
    telegramForm.value = { name: '', token: '', chat_id: '' }
  } else if (platform === 'feishu') {
    feishuForm.value = { name: '', app_id: '', app_secret: '', chat_id: '' }
  }
}

// 测试Bot连接
const handleTest = async (platform) => {
  let config = {}

  if (platform === 'discord') {
    if (!discordForm.value.webhook_url) {
      ElMessage.error('请先填写Webhook URL')
      return
    }
    config = { webhook_url: discordForm.value.webhook_url }
  } else if (platform === 'telegram') {
    if (!telegramForm.value.token || !telegramForm.value.chat_id) {
      ElMessage.error('请先填写Token和Chat ID')
      return
    }
    config = {
      token: telegramForm.value.token,
      chat_id: telegramForm.value.chat_id
    }
  } else if (platform === 'feishu') {
    if (!feishuForm.value.app_id || !feishuForm.value.app_secret) {
      ElMessage.error('请先填写App ID和App Secret')
      return
    }
    config = {
      app_id: feishuForm.value.app_id,
      app_secret: feishuForm.value.app_secret,
      chat_id: feishuForm.value.chat_id
    }
  }

  try {
    ElMessage.info('正在测试连接...')
    await api.testBotConfigDirect({ platform, config })
    ElMessage.success(`✅ ${platform} 连接测试成功！`)
  } catch (error) {
    ElMessage.error(`❌ 测试失败: ${error.response?.data?.detail || error.message}`)
  }
}

// 自动获取Telegram Chat ID
const autoGetChatId = async () => {
  if (!telegramForm.value.token) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  try {
    gettingChatId.value = true
    const result = await api.getTelegramChatIds(telegramForm.value.token)
    
    if (!result.chat_ids || result.chat_ids.length === 0) {
      ElMessage.warning(result.message || '未找到任何Chat ID。请先在Telegram中向Bot发送一条消息，然后重试。')
      return
    }

    if (result.chat_ids.length === 1) {
      telegramForm.value.chat_id = result.chat_ids[0].id
      ElMessage.success(`已自动填入Chat ID: ${result.chat_ids[0].title}`)
    } else {
      telegramForm.value.chat_id = result.chat_ids[0].id
      ElMessage.success(`找到${result.chat_ids.length}个Chat，已自动填入第一个: ${result.chat_ids[0].title}`)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '获取失败，请检查Token是否正确')
  } finally {
    gettingChatId.value = false
  }
}

const handleSkip = () => {
  emit('skip')
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.help-alert {
  margin-bottom: 20px;
}

.bot-config-form {
  padding: 20px;
}

.added-bots {
  margin-top: 30px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 4px;
}

.added-bots h3 {
  margin-bottom: 15px;
  color: #409eff;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
