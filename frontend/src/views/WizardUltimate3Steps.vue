<template>
  <div class="wizard-ultimate-container">
    <el-card class="wizard-card">
      <!-- ✅ P0-9深度优化: 真正的3步配置向导 -->
      <div class="wizard-header">
        <h1>🚀 KOOK消息转发系统 - 快速配置</h1>
        <p class="subtitle">真正的3步配置，5分钟完成设置</p>
      </div>

      <!-- 进度指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps-indicator">
        <el-step title="步骤1: 连接KOOK" description="导入Cookie或账号登录">
          <template #icon><el-icon><Connection /></el-icon></template>
        </el-step>
        <el-step title="步骤2: 配置转发目标" description="添加Bot">
          <template #icon><el-icon><Setting /></el-icon></template>
        </el-step>
        <el-step title="步骤3: 智能映射" description="自动匹配频道">
          <template #icon><el-icon><Link /></el-icon></template>
        </el-step>
      </el-steps>

      <div class="wizard-content">
        <!-- ======================== -->
        <!-- 步骤1: 连接KOOK           -->
        <!-- ======================== -->
        <div v-if="currentStep === 0" class="step-container">
          <div class="step-header">
            <h2>📧 步骤1: 连接KOOK账号</h2>
            <p>选择一种方式连接您的KOOK账号</p>
          </div>

          <el-radio-group v-model="loginMethod" class="login-method-selector">
            <el-radio-button value="cookie">📂 Cookie导入（推荐）</el-radio-button>
            <el-radio-button value="password">🔑 账号密码登录</el-radio-button>
          </el-radio-group>

          <!-- Cookie导入方式 -->
          <div v-if="loginMethod === 'cookie'" class="cookie-import-area">
            <el-alert
              title="Cookie获取方法"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            >
              <p>1. 使用浏览器扩展（推荐）：<a href="#" @click.prevent="openCookieHelp">查看教程</a></p>
              <p>2. 浏览器开发者工具：F12 → Application → Cookies</p>
              <p>3. 支持格式：JSON、Netscape、Header格式</p>
            </el-alert>

            <!-- 拖拽上传区域 -->
            <el-upload
              drag
              :auto-upload="false"
              :on-change="handleCookieFile"
              accept=".json,.txt"
              class="cookie-upload"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将Cookie文件拖到此处，或<em>点击上传</em>
              </div>
            </el-upload>

            <!-- 或直接粘贴 -->
            <div style="margin: 20px 0; text-align: center;">或</div>
            
            <el-input
              v-model="cookieText"
              type="textarea"
              :rows="6"
              placeholder="直接粘贴Cookie内容..."
              @input="validateCookie"
            />

            <!-- Cookie验证状态 -->
            <div v-if="cookieValidation.status" class="validation-status">
              <el-alert
                :title="cookieValidation.message"
                :type="cookieValidation.status"
                show-icon
                :closable="false"
              />
            </div>
          </div>

          <!-- 账号密码登录方式 -->
          <div v-else class="password-login-area">
            <el-form :model="loginForm" label-width="100px">
              <el-form-item label="邮箱">
                <el-input v-model="loginForm.email" placeholder="your@email.com" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="loginForm.password" type="password" show-password />
              </el-form-item>
              
              <el-alert
                title="首次登录可能需要验证码"
                type="warning"
                :closable="false"
              />
            </el-form>
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button type="primary" size="large" @click="nextStep" :loading="loading">
              下一步：配置Bot
            </el-button>
          </div>
        </div>

        <!-- ======================== -->
        <!-- 步骤2: 配置转发目标（Bot）  -->
        <!-- ======================== -->
        <div v-if="currentStep === 1" class="step-container">
          <div class="step-header">
            <h2>🤖 步骤2: 配置转发目标</h2>
            <p>至少添加一个Bot用于接收消息</p>
          </div>

          <!-- 平台选择 -->
          <el-tabs v-model="selectedPlatform" class="platform-tabs">
            <el-tab-pane label="Discord" name="discord">
              <div class="platform-config">
                <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
                  <p><strong>如何创建Discord Webhook？</strong></p>
                  <ol>
                    <li>进入Discord服务器设置 → 集成 → Webhook</li>
                    <li>点击"新建Webhook"</li>
                    <li>复制Webhook URL</li>
                    <li>粘贴到下方输入框</li>
                  </ol>
                  <el-link type="primary" @click="openDiscordHelp">📖 查看详细教程</el-link>
                </el-alert>

                <el-form label-width="120px">
                  <el-form-item label="Webhook名称">
                    <el-input v-model="discordBot.name" placeholder="例如：游戏公告Bot" />
                  </el-form-item>
                  <el-form-item label="Webhook URL">
                    <el-input v-model="discordBot.webhookUrl" placeholder="https://discord.com/api/webhooks/..." />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="success" @click="testDiscordBot" :loading="testing">
                      🧪 测试连接
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Telegram" name="telegram">
              <div class="platform-config">
                <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
                  <p><strong>如何创建Telegram Bot？</strong></p>
                  <ol>
                    <li>与 @BotFather 对话</li>
                    <li>发送 /newbot 创建Bot</li>
                    <li>获取Bot Token</li>
                    <li>将Bot添加到群组</li>
                    <li>使用"自动获取"按钮获取Chat ID</li>
                  </ol>
                  <el-link type="primary" @click="openTelegramHelp">📖 查看详细教程</el-link>
                </el-alert>

                <el-form label-width="120px">
                  <el-form-item label="Bot名称">
                    <el-input v-model="telegramBot.name" placeholder="例如：游戏公告TG Bot" />
                  </el-form-item>
                  <el-form-item label="Bot Token">
                    <el-input v-model="telegramBot.token" placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" />
                  </el-form-item>
                  <el-form-item label="Chat ID">
                    <el-input v-model="telegramBot.chatId" placeholder="-1001234567890">
                      <template #append>
                        <el-button @click="autoGetChatId" :loading="gettingChatId">
                          🔍 自动获取
                        </el-button>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="success" @click="testTelegramBot" :loading="testing">
                      🧪 测试连接
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="飞书" name="feishu">
              <div class="platform-config">
                <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
                  <p><strong>如何创建飞书Bot？</strong></p>
                  <ol>
                    <li>访问飞书开放平台</li>
                    <li>创建自建应用</li>
                    <li>开启机器人能力</li>
                    <li>获取App ID和App Secret</li>
                    <li>将机器人添加到群组</li>
                  </ol>
                  <el-link type="primary" @click="openFeishuHelp">📖 查看详细教程</el-link>
                </el-alert>

                <el-form label-width="120px">
                  <el-form-item label="应用名称">
                    <el-input v-model="feishuBot.name" placeholder="例如：游戏公告飞书Bot" />
                  </el-form-item>
                  <el-form-item label="App ID">
                    <el-input v-model="feishuBot.appId" placeholder="cli_a1b2c3d4e5f6g7h8" />
                  </el-form-item>
                  <el-form-item label="App Secret">
                    <el-input v-model="feishuBot.appSecret" placeholder="ABCdefGHIjklMNOpqrs" show-password />
                  </el-form-item>
                  <el-form-item label="群组Webhook">
                    <el-input v-model="feishuBot.webhook" placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..." />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="success" @click="testFeishuBot" :loading="testing">
                      🧪 测试连接
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" @click="nextStep" :disabled="!hasValidBot">
              下一步：智能映射
            </el-button>
            <el-button @click="skipBotConfig" type="text">
              跳过（稍后配置）
            </el-button>
          </div>
        </div>

        <!-- ======================== -->
        <!-- 步骤3: 智能映射           -->
        <!-- ======================== -->
        <div v-if="currentStep === 2" class="step-container">
          <div class="step-header">
            <h2>🔀 步骤3: 智能频道映射</h2>
            <p>自动匹配KOOK频道到目标平台</p>
          </div>

          <el-alert type="success" :closable="false" style="margin-bottom: 20px;">
            <p><strong>✨ 智能映射功能</strong></p>
            <p>系统会自动识别KOOK频道名称，并在目标平台查找同名或相似频道建立映射关系。</p>
            <p>示例：KOOK "#公告" → Discord "#announcements" / Telegram "公告群"</p>
          </el-alert>

          <!-- 智能映射选项 -->
          <div class="mapping-options">
            <el-radio-group v-model="mappingMode" size="large">
              <el-radio-button value="auto">
                🤖 智能映射（推荐）
              </el-radio-button>
              <el-radio-button value="manual">
                ✋ 手动映射
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- 自动映射模式 -->
          <div v-if="mappingMode === 'auto'" class="auto-mapping-area">
            <el-button 
              type="primary" 
              size="large" 
              @click="runAutoMapping" 
              :loading="mapping"
              style="width: 100%; margin: 20px 0;"
            >
              🚀 开始智能映射
            </el-button>

            <!-- 映射结果 -->
            <div v-if="autoMappingResults.length > 0" class="mapping-results">
              <h3>✅ 智能映射结果（共 {{ autoMappingResults.length }} 条）</h3>
              
              <el-table :data="autoMappingResults" border style="margin-top: 10px;">
                <el-table-column prop="kookChannel" label="KOOK频道" width="200" />
                <el-table-column label="映射目标" min-width="300">
                  <template #default="{ row }">
                    <el-tag 
                      v-for="(target, idx) in row.targets" 
                      :key="idx"
                      style="margin-right: 5px;"
                      :type="target.confidence === 'high' ? 'success' : 'warning'"
                    >
                      {{ target.platform }}: {{ target.channel }}
                      <span style="font-size: 12px; opacity: 0.7;">
                        ({{ target.confidence }})
                      </span>
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button size="small" @click="editMapping(row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="removeMapping(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 手动映射模式 -->
          <div v-else class="manual-mapping-area">
            <p>请手动选择KOOK频道和目标平台频道建立映射</p>
            
            <div class="mapping-editor">
              <div class="source-channels">
                <h4>KOOK频道（源）</h4>
                <el-tree
                  :data="kookServers"
                  node-key="id"
                  :props="treeProps"
                  show-checkbox
                  @check="handleChannelSelect"
                />
              </div>

              <div class="mapping-arrow">→</div>

              <div class="target-channels">
                <h4>目标平台（接收）</h4>
                <el-select v-model="selectedTargetBot" placeholder="选择Bot">
                  <el-option 
                    v-for="bot in configuredBots" 
                    :key="bot.id" 
                    :label="`${bot.platform}: ${bot.name}`" 
                    :value="bot.id"
                  />
                </el-select>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button 
              type="primary" 
              size="large" 
              @click="finishWizard" 
              :disabled="autoMappingResults.length === 0 && mappingMode === 'auto'"
            >
              🎉 完成配置
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// ============ 状态管理 ============
const currentStep = ref(0)
const loading = ref(false)
const testing = ref(false)
const mapping = ref(false)
const gettingChatId = ref(false)

// 步骤1: 登录相关
const loginMethod = ref('cookie')  // 'cookie' or 'password'
const cookieText = ref('')
const cookieValidation = ref({ status: null, message: '' })

const loginForm = ref({
  email: '',
  password: ''
})

// 步骤2: Bot配置
const selectedPlatform = ref('discord')
const discordBot = ref({ name: '', webhookUrl: '' })
const telegramBot = ref({ name: '', token: '', chatId: '' })
const feishuBot = ref({ name: '', appId: '', appSecret: '', webhook: '' })
const configuredBots = ref([])

// 步骤3: 映射配置
const mappingMode = ref('auto')  // 'auto' or 'manual'
const autoMappingResults = ref([])
const kookServers = ref([])
const selectedTargetBot = ref(null)

// ============ 计算属性 ============
const hasValidBot = computed(() => {
  return configuredBots.value.length > 0
})

const treeProps = {
  children: 'channels',
  label: 'name'
}

// ============ 方法 ============

// 步骤导航
function nextStep() {
  if (currentStep.value === 0) {
    // 验证步骤1
    if (!validateStep1()) return
    
    // 执行登录
    performLogin()
  } else if (currentStep.value === 1) {
    // 验证步骤2
    if (!hasValidBot.value) {
      ElMessage.warning('请至少配置一个Bot')
      return
    }
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 步骤1: Cookie处理
function handleCookieFile(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    cookieText.value = e.target.result
    validateCookie()
  }
  reader.readAsText(file.raw)
}

function validateCookie() {
  if (!cookieText.value) {
    cookieValidation.value = { status: null, message: '' }
    return
  }

  try {
    // 尝试解析JSON
    JSON.parse(cookieText.value)
    cookieValidation.value = {
      status: 'success',
      message: '✅ Cookie格式验证通过'
    }
  } catch {
    // 可能是其他格式
    cookieValidation.value = {
      status: 'warning',
      message: '⚠️ 非JSON格式，将尝试自动识别'
    }
  }
}

function validateStep1() {
  if (loginMethod.value === 'cookie') {
    if (!cookieText.value) {
      ElMessage.error('请输入或上传Cookie')
      return false
    }
  } else {
    if (!loginForm.value.email || !loginForm.value.password) {
      ElMessage.error('请输入邮箱和密码')
      return false
    }
  }
  return true
}

async function performLogin() {
  loading.value = true
  try {
    const payload = loginMethod.value === 'cookie' 
      ? { cookie: cookieText.value }
      : { email: loginForm.value.email, password: loginForm.value.password }
    
    const response = await axios.post('http://localhost:9527/api/accounts', payload)
    
    if (response.data.success) {
      ElMessage.success('✅ KOOK账号添加成功')
      currentStep.value++
    } else {
      ElMessage.error(response.data.message || '添加账号失败')
    }
  } catch (error) {
    ElMessage.error('连接后端失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 步骤2: Bot配置
async function testDiscordBot() {
  if (!discordBot.value.webhookUrl) {
    ElMessage.warning('请输入Webhook URL')
    return
  }

  testing.value = true
  try {
    const response = await axios.post('http://localhost:9527/api/bots/test', {
      platform: 'discord',
      config: { webhook_url: discordBot.value.webhookUrl }
    })

    if (response.data.success) {
      ElMessage.success('✅ Discord连接测试成功')
      
      // 保存Bot配置
      await saveBotConfig('discord', discordBot.value.name || 'Discord Bot', {
        webhook_url: discordBot.value.webhookUrl
      })
    } else {
      ElMessage.error('连接测试失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    testing.value = false
  }
}

async function saveBotConfig(platform, name, config) {
  const response = await axios.post('http://localhost:9527/api/bots', {
    platform,
    name,
    config
  })

  if (response.data.id) {
    configuredBots.value.push({
      id: response.data.id,
      platform,
      name,
      config
    })
    ElMessage.success(`✅ ${platform} Bot配置已保存`)
  }
}

function skipBotConfig() {
  ElMessageBox.confirm(
    '跳过Bot配置后，您需要在"机器人配置"页面手动添加。是否继续？',
    '确认跳过',
    {
      type: 'warning'
    }
  ).then(() => {
    currentStep.value++
  })
}

// 步骤3: 智能映射
async function runAutoMapping() {
  mapping.value = true
  try {
    const response = await axios.post('http://localhost:9527/api/mappings/auto-map', {
      strategy: 'smart',  // 使用智能匹配策略
      min_confidence: 0.6  // 最低置信度60%
    })

    if (response.data.mappings) {
      autoMappingResults.value = response.data.mappings
      ElMessage.success(`✅ 智能映射完成，共匹配 ${autoMappingResults.value.length} 条映射`)
    }
  } catch (error) {
    ElMessage.error('智能映射失败: ' + error.message)
  } finally {
    mapping.value = false
  }
}

// 完成向导
async function finishWizard() {
  try {
    // 标记向导已完成
    localStorage.setItem('wizard_completed', 'true')
    
    ElMessageBox.confirm(
      '配置已完成！接下来您可以：\n1. 查看概览页面，启动服务\n2. 在设置中调整高级配置\n3. 查看实时日志监控转发状态',
      '✅ 配置完成',
      {
        type: 'success',
        confirmButtonText: '进入主界面',
        showCancelButton: false
      }
    ).then(() => {
      router.push('/')
    })
  } catch (error) {
    console.error(error)
  }
}

// 辅助函数
function openCookieHelp() {
  window.open('https://github.com/gfchfjh/CSBJJWT/wiki/Cookie%E8%8E%B7%E5%8F%96%E6%95%99%E7%A8%8B', '_blank')
}

function openDiscordHelp() {
  window.open('https://support.discord.com/hc/zh-tw/articles/228383668', '_blank')
}

function openTelegramHelp() {
  window.open('https://core.telegram.org/bots#creating-a-new-bot', '_blank')
}

function openFeishuHelp() {
  window.open('https://open.feishu.cn/document/home/introduction-to-custom-app-development', '_blank')
}

async function autoGetChatId() {
  if (!telegramBot.value.token) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  gettingChatId.value = true
  try {
    const response = await axios.post('http://localhost:9527/api/telegram/get-chat-id', {
      token: telegramBot.value.token
    })

    if (response.data.chat_id) {
      telegramBot.value.chatId = response.data.chat_id
      ElMessage.success('✅ Chat ID获取成功')
    }
  } catch (error) {
    ElMessage.error('获取Chat ID失败: ' + error.message)
  } finally {
    gettingChatId.value = false
  }
}

function testTelegramBot() {
  ElMessage.info('Telegram测试功能开发中')
}

function testFeishuBot() {
  ElMessage.info('飞书测试功能开发中')
}

function editMapping(row) {
  ElMessage.info('映射编辑功能开发中')
}

function removeMapping(row) {
  const index = autoMappingResults.value.indexOf(row)
  if (index > -1) {
    autoMappingResults.value.splice(index, 1)
    ElMessage.success('已删除映射')
  }
}

function handleChannelSelect(data, checked) {
  console.log('Channel selected:', data, checked)
}
</script>

<style scoped>
.wizard-ultimate-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.wizard-card {
  width: 100%;
  max-width: 900px;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.wizard-header {
  text-align: center;
  margin-bottom: 40px;
}

.wizard-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 16px;
  color: #909399;
}

.steps-indicator {
  margin-bottom: 40px;
}

.step-container {
  min-height: 400px;
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.step-header p {
  color: #909399;
}

.login-method-selector {
  width: 100%;
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}

.cookie-upload {
  margin: 20px 0;
}

.step-actions {
  margin-top: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-tabs {
  margin: 20px 0;
}

.mapping-options {
  text-align: center;
  margin: 30px 0;
}

.auto-mapping-area {
  margin-top: 20px;
}

.mapping-results {
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.manual-mapping-area {
  margin-top: 20px;
}

.mapping-editor {
  display: grid;
  grid-template-columns: 2fr auto 2fr;
  gap: 20px;
  align-items: center;
  margin-top: 20px;
}

.mapping-arrow {
  font-size: 36px;
  color: #409EFF;
  text-align: center;
}

.validation-status {
  margin-top: 15px;
}
</style>
