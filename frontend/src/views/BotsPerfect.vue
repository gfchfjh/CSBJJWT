<template>
  <div class="bots-perfect">
    <div class="page-header">
      <h1>🤖 机器人配置</h1>
      <p>配置Discord、Telegram、飞书机器人，用于接收转发的消息</p>
    </div>

    <!-- 平台选择 -->
    <el-card shadow="hover" class="platform-selector-card">
      <div class="platform-tabs">
        <el-radio-group v-model="selectedPlatform" size="large">
          <el-radio-button value="discord">
            <el-icon><Share /></el-icon>
            Discord
          </el-radio-button>
          <el-radio-button value="telegram">
            <el-icon><ChatDotRound /></el-icon>
            Telegram
          </el-radio-button>
          <el-radio-button value="feishu">
            <el-icon><Message /></el-icon>
            飞书
          </el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <!-- Discord配置 -->
    <div v-show="selectedPlatform === 'discord'" class="platform-config">
      <el-card shadow="hover">
        <template #header>
          <div class="config-header">
            <h2>═══════════════ Discord配置 ═══════════════</h2>
          </div>
        </template>

        <el-form
          ref="discordFormRef"
          :model="discordForm"
          :rules="discordRules"
          label-width="140px"
          class="config-form"
        >
          <el-form-item label="Webhook名称" prop="name">
            <el-input
              v-model="discordForm.name"
              placeholder="游戏公告Bot"
              style="width: 400px"
            />
            <span class="form-tip">（备注用）</span>
          </el-form-item>

          <el-form-item label="Webhook URL" prop="webhook_url">
            <el-input
              v-model="discordForm.webhook_url"
              placeholder="https://discord.com/api/webhooks/123456..."
              style="width: 600px"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              link
              type="primary"
              @click="openTutorial('discord-webhook')"
            >
              <el-icon><QuestionFilled /></el-icon>
              📖 如何创建Discord Webhook？
            </el-button>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="isTesting"
              @click="testConnection('discord')"
            >
              <el-icon><Promotion /></el-icon>
              🧪 测试连接
            </el-button>
            <el-button @click="resetForm('discord')">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button
              type="success"
              :loading="isSaving"
              @click="saveBot('discord')"
            >
              <el-icon><CircleCheck /></el-icon>
              保存配置
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="bot-list-section">
          <h4>已配置的Webhook：</h4>

          <el-empty v-if="discordBots.length === 0" description="暂无配置" />

          <div v-else class="bot-list">
            <el-card
              v-for="bot in discordBots"
              :key="bot.id"
              shadow="hover"
              class="bot-card"
            >
              <div class="bot-info">
                <div class="bot-name">
                  <el-tag type="success" size="large">🟢</el-tag>
                  <strong>{{ bot.name }}</strong>
                </div>
                <div class="bot-url">
                  <el-text truncated>{{ bot.webhook_url }}</el-text>
                </div>
                <div class="bot-status">
                  <span v-if="bot.last_test_time">
                    最后测试：
                    <el-tag :type="bot.last_test_success ? 'success' : 'danger'" size="small">
                      {{ bot.last_test_success ? '成功' : '失败' }}
                    </el-tag>
                    ({{ formatTime(bot.last_test_time) }})
                  </span>
                  <span v-else class="text-muted">未测试</span>
                </div>
              </div>
              <div class="bot-actions">
                <el-button size="small" @click="editBot('discord', bot)">
                  <el-icon><Edit /></el-icon>
                  ✏️ 编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteBot('discord', bot.id)"
                >
                  <el-icon><Delete /></el-icon>
                  🗑️ 删除
                </el-button>
              </div>
            </el-card>
          </div>

          <el-button type="primary" plain @click="addNewBot('discord')">
            <el-icon><Plus /></el-icon>
            ➕ 添加新Webhook
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- Telegram配置 -->
    <div v-show="selectedPlatform === 'telegram'" class="platform-config">
      <el-card shadow="hover">
        <template #header>
          <div class="config-header">
            <h2>═══════════════ Telegram配置 ═══════════════</h2>
          </div>
        </template>

        <el-form
          ref="telegramFormRef"
          :model="telegramForm"
          :rules="telegramRules"
          label-width="140px"
          class="config-form"
        >
          <el-form-item label="Bot名称" prop="name">
            <el-input
              v-model="telegramForm.name"
              placeholder="游戏公告TG Bot"
              style="width: 400px"
            />
          </el-form-item>

          <el-form-item label="Bot Token" prop="bot_token">
            <el-input
              v-model="telegramForm.bot_token"
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              style="width: 600px"
              show-password
            />
          </el-form-item>

          <el-form-item label="Chat ID" prop="chat_id">
            <el-input
              v-model="telegramForm.chat_id"
              placeholder="-1001234567890"
              style="width: 300px"
            />
            <el-button
              type="primary"
              link
              :loading="isGettingChatId"
              @click="autoGetChatId"
            >
              <el-icon><MagicStick /></el-icon>
              🔍 自动获取
            </el-button>
          </el-form-item>

          <el-form-item>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>📖 配置教程：</template>
              <ol style="margin: 5px 0; padding-left: 20px;">
                <li>
                  与 @BotFather 对话创建Bot
                  <el-button link type="primary" size="small" @click="openTutorial('telegram-bot')">
                    查看教程
                  </el-button>
                </li>
                <li>将Bot添加到群组</li>
                <li>点击"自动获取"按钮，软件会自动检测Chat ID</li>
              </ol>
            </el-alert>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="isTesting"
              @click="testConnection('telegram')"
            >
              <el-icon><Promotion /></el-icon>
              🧪 测试连接
            </el-button>
            <el-button @click="resetForm('telegram')">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button
              type="success"
              :loading="isSaving"
              @click="saveBot('telegram')"
            >
              <el-icon><CircleCheck /></el-icon>
              保存配置
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="bot-list-section">
          <h4>已配置的Bot：</h4>

          <el-empty v-if="telegramBots.length === 0" description="暂无配置" />

          <div v-else class="bot-list">
            <el-card
              v-for="bot in telegramBots"
              :key="bot.id"
              shadow="hover"
              class="bot-card"
            >
              <div class="bot-info">
                <div class="bot-name">
                  <el-tag type="success" size="large">🟢</el-tag>
                  <strong>{{ bot.name }}</strong>
                </div>
                <div class="bot-config-info">
                  <p><strong>Bot Token:</strong> {{ maskToken(bot.bot_token) }}</p>
                  <p><strong>Chat ID:</strong> {{ bot.chat_id }}</p>
                </div>
                <div class="bot-status">
                  <span v-if="bot.last_test_time">
                    最后测试：
                    <el-tag :type="bot.last_test_success ? 'success' : 'danger'" size="small">
                      {{ bot.last_test_success ? '成功' : '失败' }}
                    </el-tag>
                    ({{ formatTime(bot.last_test_time) }})
                  </span>
                  <span v-else class="text-muted">未测试</span>
                </div>
              </div>
              <div class="bot-actions">
                <el-button size="small" @click="editBot('telegram', bot)">
                  <el-icon><Edit /></el-icon>
                  ✏️ 编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteBot('telegram', bot.id)"
                >
                  <el-icon><Delete /></el-icon>
                  🗑️ 删除
                </el-button>
              </div>
            </el-card>
          </div>

          <el-button type="primary" plain @click="addNewBot('telegram')">
            <el-icon><Plus /></el-icon>
            ➕ 添加新Bot
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 飞书配置 -->
    <div v-show="selectedPlatform === 'feishu'" class="platform-config">
      <el-card shadow="hover">
        <template #header>
          <div class="config-header">
            <h2>═══════════════ 飞书配置 ═══════════════</h2>
          </div>
        </template>

        <el-form
          ref="feishuFormRef"
          :model="feishuForm"
          :rules="feishuRules"
          label-width="180px"
          class="config-form"
        >
          <el-form-item label="应用名称" prop="name">
            <el-input
              v-model="feishuForm.name"
              placeholder="游戏公告飞书Bot"
              style="width: 400px"
            />
          </el-form-item>

          <el-form-item label="App ID" prop="app_id">
            <el-input
              v-model="feishuForm.app_id"
              placeholder="cli_a1b2c3d4e5f6g7h8"
              style="width: 400px"
            />
          </el-form-item>

          <el-form-item label="App Secret" prop="app_secret">
            <el-input
              v-model="feishuForm.app_secret"
              placeholder="ABCdefGHIjklMNOpqrs"
              style="width: 400px"
              show-password
            />
          </el-form-item>

          <el-form-item label="群组Webhook（可选）">
            <el-input
              v-model="feishuForm.webhook_url"
              placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
              style="width: 600px"
            />
          </el-form-item>

          <el-form-item>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>📖 配置教程：</template>
              <ol style="margin: 5px 0; padding-left: 20px;">
                <li>
                  在飞书开放平台创建自建应用
                  <el-button link type="primary" size="small" @click="openTutorial('feishu-app')">
                    查看教程
                  </el-button>
                </li>
                <li>开启机器人能力</li>
                <li>将机器人添加到群组</li>
              </ol>
              <p style="margin-top: 10px;">
                <el-button link type="primary" @click="openVideoTutorial('feishu')">
                  <el-icon><VideoPlay /></el-icon>
                  📺 观看视频教程
                </el-button>
              </p>
            </el-alert>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="isTesting"
              @click="testConnection('feishu')"
            >
              <el-icon><Promotion /></el-icon>
              🧪 测试连接
            </el-button>
            <el-button @click="resetForm('feishu')">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button
              type="success"
              :loading="isSaving"
              @click="saveBot('feishu')"
            >
              <el-icon><CircleCheck /></el-icon>
              保存配置
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="bot-list-section">
          <h4>已配置的应用：</h4>

          <el-empty v-if="feishuBots.length === 0" description="暂无配置" />

          <div v-else class="bot-list">
            <el-card
              v-for="bot in feishuBots"
              :key="bot.id"
              shadow="hover"
              class="bot-card"
            >
              <div class="bot-info">
                <div class="bot-name">
                  <el-tag type="success" size="large">🟢</el-tag>
                  <strong>{{ bot.name }}</strong>
                </div>
                <div class="bot-config-info">
                  <p><strong>App ID:</strong> {{ bot.app_id }}</p>
                  <p><strong>App Secret:</strong> {{ maskToken(bot.app_secret) }}</p>
                  <p v-if="bot.webhook_url"><strong>Webhook:</strong> 已配置</p>
                </div>
                <div class="bot-status">
                  <span v-if="bot.last_test_time">
                    最后测试：
                    <el-tag :type="bot.last_test_success ? 'success' : 'danger'" size="small">
                      {{ bot.last_test_success ? '成功' : '失败' }}
                    </el-tag>
                    ({{ formatTime(bot.last_test_time) }})
                  </span>
                  <span v-else class="text-muted">未测试</span>
                </div>
              </div>
              <div class="bot-actions">
                <el-button size="small" @click="editBot('feishu', bot)">
                  <el-icon><Edit /></el-icon>
                  ✏️ 编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteBot('feishu', bot.id)"
                >
                  <el-icon><Delete /></el-icon>
                  🗑️ 删除
                </el-button>
              </div>
            </el-card>
          </div>

          <el-button type="primary" plain @click="addNewBot('feishu')">
            <el-icon><Plus /></el-icon>
            ➕ 添加新应用
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Share, ChatDotRound, Message, QuestionFilled, Promotion,
  RefreshLeft, CircleCheck, Edit, Delete, Plus, MagicStick,
  VideoPlay
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import axios from 'axios'

dayjs.extend(relativeTime)

const router = useRouter()

// 选中的平台
const selectedPlatform = ref('discord')

// 表单引用
const discordFormRef = ref(null)
const telegramFormRef = ref(null)
const feishuFormRef = ref(null)

// 表单数据
const discordForm = ref({
  name: '',
  webhook_url: ''
})

const telegramForm = ref({
  name: '',
  bot_token: '',
  chat_id: ''
})

const feishuForm = ref({
  name: '',
  app_id: '',
  app_secret: '',
  webhook_url: ''
})

// 表单验证规则
const discordRules = {
  name: [{ required: true, message: '请输入Webhook名称', trigger: 'blur' }],
  webhook_url: [
    { required: true, message: '请输入Webhook URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

const telegramRules = {
  name: [{ required: true, message: '请输入Bot名称', trigger: 'blur' }],
  bot_token: [{ required: true, message: '请输入Bot Token', trigger: 'blur' }],
  chat_id: [{ required: true, message: '请输入Chat ID', trigger: 'blur' }]
}

const feishuRules = {
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  app_id: [{ required: true, message: '请输入App ID', trigger: 'blur' }],
  app_secret: [{ required: true, message: '请输入App Secret', trigger: 'blur' }]
}

// Bot列表
const discordBots = ref([])
const telegramBots = ref([])
const feishuBots = ref([])

// 加载状态
const isTesting = ref(false)
const isSaving = ref(false)
const isGettingChatId = ref(false)

// 编辑模式
const editingBotId = ref(null)

// 方法
const formatTime = (time) => {
  return dayjs(time).fromNow()
}

const maskToken = (token) => {
  if (!token) return ''
  if (token.length <= 10) return '******'
  return token.substring(0, 5) + '******' + token.substring(token.length - 5)
}

const openTutorial = (type) => {
  router.push(`/help?tutorial=${type}`)
}

const openVideoTutorial = (type) => {
  router.push(`/help?video=${type}`)
}

// 测试连接
const testConnection = async (platform) => {
  const formRef = platform === 'discord' ? discordFormRef.value :
                   platform === 'telegram' ? telegramFormRef.value :
                   feishuFormRef.value

  try {
    await formRef.validate()
  } catch {
    ElMessage.warning('请先填写完整配置信息')
    return
  }

  isTesting.value = true
  try {
    const config = platform === 'discord' ? discordForm.value :
                    platform === 'telegram' ? telegramForm.value :
                    feishuForm.value

    const response = await axios.post(`/api/bots/${platform}/test`, config)

    if (response.data.success) {
      ElMessage.success('测试成功！已发送测试消息到目标平台')
    } else {
      ElMessage.error(response.data.message || '测试失败')
    }
  } catch (error) {
    console.error('测试失败:', error)
    ElMessage.error(error.response?.data?.detail || '测试失败')
  } finally {
    isTesting.value = false
  }
}

// 自动获取Chat ID (Telegram)
const autoGetChatId = async () => {
  if (!telegramForm.value.bot_token) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  isGettingChatId.value = true
  try {
    const response = await axios.post('/api/bots/telegram/get-chat-id', {
      bot_token: telegramForm.value.bot_token
    })

    if (response.data.success) {
      telegramForm.value.chat_id = response.data.chat_id
      ElMessage.success('Chat ID获取成功')
    } else {
      ElMessage.error(response.data.message || 'Chat ID获取失败')
    }
  } catch (error) {
    console.error('获取失败:', error)
    ElMessage.error('Chat ID获取失败，请手动输入')
  } finally {
    isGettingChatId.value = false
  }
}

// 保存Bot配置
const saveBot = async (platform) => {
  const formRef = platform === 'discord' ? discordFormRef.value :
                   platform === 'telegram' ? telegramFormRef.value :
                   feishuFormRef.value

  try {
    await formRef.validate()
  } catch {
    ElMessage.warning('请填写完整配置信息')
    return
  }

  isSaving.value = true
  try {
    const config = platform === 'discord' ? discordForm.value :
                    platform === 'telegram' ? telegramForm.value :
                    feishuForm.value

    const url = editingBotId.value
      ? `/api/bots/${platform}/${editingBotId.value}`
      : `/api/bots/${platform}`

    const method = editingBotId.value ? 'put' : 'post'

    const response = await axios[method](url, config)

    if (response.data.success) {
      ElMessage.success(editingBotId.value ? '更新成功' : '保存成功')
      loadBots(platform)
      resetForm(platform)
      editingBotId.value = null
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    isSaving.value = false
  }
}

// 重置表单
const resetForm = (platform) => {
  if (platform === 'discord') {
    discordForm.value = { name: '', webhook_url: '' }
    discordFormRef.value?.resetFields()
  } else if (platform === 'telegram') {
    telegramForm.value = { name: '', bot_token: '', chat_id: '' }
    telegramFormRef.value?.resetFields()
  } else if (platform === 'feishu') {
    feishuForm.value = { name: '', app_id: '', app_secret: '', webhook_url: '' }
    feishuFormRef.value?.resetFields()
  }
  editingBotId.value = null
}

// 编辑Bot
const editBot = (platform, bot) => {
  if (platform === 'discord') {
    discordForm.value = { ...bot }
  } else if (platform === 'telegram') {
    telegramForm.value = { ...bot }
  } else if (platform === 'feishu') {
    feishuForm.value = { ...bot }
  }
  editingBotId.value = bot.id

  // 滚动到表单
  window.scrollTo({ top: 0, behavior: 'smooth' })
  ElMessage.info('编辑模式，修改后点击保存')
}

// 删除Bot
const deleteBot = async (platform, botId) => {
  try {
    await ElMessageBox.confirm(
      '删除后将无法恢复，确定要删除吗？',
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )

    const response = await axios.delete(`/api/bots/${platform}/${botId}`)

    if (response.data.success) {
      ElMessage.success('删除成功')
      loadBots(platform)
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 添加新Bot
const addNewBot = (platform) => {
  resetForm(platform)
  window.scrollTo({ top: 0, behavior: 'smooth' })
  ElMessage.info('请填写配置信息')
}

// 加载Bot列表
const loadBots = async (platform) => {
  try {
    const response = await axios.get(`/api/bots/${platform}`)

    if (response.data.success) {
      if (platform === 'discord') {
        discordBots.value = response.data.bots || []
      } else if (platform === 'telegram') {
        telegramBots.value = response.data.bots || []
      } else if (platform === 'feishu') {
        feishuBots.value = response.data.bots || []
      }
    }
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadBots('discord')
  loadBots('telegram')
  loadBots('feishu')
})
</script>

<style scoped lang="scss">
.bots-perfect {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;

  h1 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    color: #606266;
    font-size: 16px;
  }
}

.platform-selector-card {
  margin-bottom: 20px;

  .platform-tabs {
    display: flex;
    justify-content: center;
  }
}

.platform-config {
  .config-header {
    h2 {
      text-align: center;
      color: #303133;
      font-size: 20px;
      font-weight: 600;
    }
  }

  .config-form {
    max-width: 800px;
    margin: 20px auto;

    .form-tip {
      margin-left: 10px;
      color: #909399;
      font-size: 14px;
    }
  }

  .bot-list-section {
    margin-top: 30px;

    h4 {
      font-size: 18px;
      color: #303133;
      margin-bottom: 15px;
    }

    .bot-list {
      display: grid;
      gap: 15px;
      margin-bottom: 20px;

      .bot-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;

        .bot-info {
          flex: 1;

          .bot-name {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;

            strong {
              font-size: 16px;
              color: #303133;
            }
          }

          .bot-url,
          .bot-config-info {
            margin-bottom: 10px;
            color: #606266;
            font-size: 14px;

            p {
              margin: 5px 0;
            }
          }

          .bot-status {
            font-size: 14px;
            color: #909399;

            .text-muted {
              color: #C0C4CC;
            }
          }
        }

        .bot-actions {
          display: flex;
          gap: 10px;
        }
      }
    }
  }
}

.text-muted {
  color: #909399;
}
</style>
