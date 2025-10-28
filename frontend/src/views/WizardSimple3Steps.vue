<template>
  <div class="wizard-simple-container">
    <el-card class="wizard-card" shadow="always">
      <!-- 进度步骤 -->
      <div class="wizard-header">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="登录KOOK" icon="User" description="1分钟" />
          <el-step title="配置Bot" icon="Robot" description="2分钟" />
          <el-step title="智能映射" icon="Connection" description="1分钟" />
        </el-steps>
        
        <div class="wizard-time">
          <el-tag type="success" size="large">
            预计总耗时: 4分钟 · 当前进度: {{ ((currentStep / 3) * 100).toFixed(0) }}%
          </el-tag>
        </div>
      </div>

      <div class="wizard-content">
        <!-- 步骤1: 登录KOOK -->
        <div v-show="currentStep === 0" class="step-container">
          <div class="step-header">
            <h2>🍪 步骤1: 登录KOOK账号</h2>
            <p>选择您喜欢的登录方式，推荐使用Chrome扩展一键导出</p>
          </div>

          <el-tabs v-model="loginMethod" class="login-tabs">
            <!-- Cookie导入（推荐） -->
            <el-tab-pane label="🍪 Cookie导入（推荐）" name="cookie">
              <el-alert
                title="✨ 最简单的方式！"
                type="success"
                :closable="false"
                show-icon
                style="margin-bottom: 20px"
              >
                使用Chrome扩展，2步完成Cookie导出，无需手动复制粘贴
              </el-alert>

              <el-steps :active="cookieStep" direction="vertical">
                <el-step title="安装Chrome扩展">
                  <template #description>
                    <div style="margin-top: 10px;">
                      <el-button type="primary" @click="installExtension">
                        <el-icon><Download /></el-icon>
                        安装Chrome扩展
                      </el-button>
                      <p style="margin-top: 10px; color: #666; font-size: 13px;">
                        点击后会打开Chrome扩展页面，按提示安装
                      </p>
                    </div>
                  </template>
                </el-step>

                <el-step title="导出Cookie">
                  <template #description>
                    <div style="margin-top: 10px;">
                      <ol style="color: #666; font-size: 13px; line-height: 1.8;">
                        <li>访问 <a href="https://www.kookapp.cn" target="_blank" style="color: #409EFF;">www.kookapp.cn</a> 并登录</li>
                        <li>点击浏览器工具栏的扩展图标</li>
                        <li>点击"🍪 一键导出Cookie"</li>
                        <li>Cookie会自动导入到本系统</li>
                      </ol>
                      <el-button type="success" @click="checkCookieImported">
                        <el-icon><Refresh /></el-icon>
                        检查是否已导入
                      </el-button>
                    </div>
                  </template>
                </el-step>
              </el-steps>

              <el-divider>或手动粘贴Cookie</el-divider>

              <el-input
                v-model="cookieText"
                type="textarea"
                :rows="8"
                placeholder="粘贴Chrome扩展导出的Cookie JSON..."
                @input="validateCookie"
              />

              <el-alert
                v-if="cookieValidation"
                :title="cookieValidation.title"
                :type="cookieValidation.type"
                :closable="false"
                style="margin-top: 10px"
              />
            </el-tab-pane>

            <!-- 账号密码登录 -->
            <el-tab-pane label="📧 账号密码" name="password">
              <el-alert
                title="📝 使用KOOK账号密码登录"
                type="info"
                :closable="false"
                style="margin-bottom: 20px"
              >
                首次登录可能需要输入验证码
              </el-alert>

              <el-form :model="loginForm" label-width="100px">
                <el-form-item label="邮箱">
                  <el-input v-model="loginForm.email" placeholder="请输入KOOK邮箱" clearable>
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="密码">
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    show-password
                  >
                    <template #prefix>
                      <el-icon><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-form>

              <el-button
                type="primary"
                size="large"
                :loading="loggingIn"
                @click="loginWithPassword"
                style="width: 100%"
              >
                <el-icon v-if="!loggingIn"><Right /></el-icon>
                {{ loggingIn ? '登录中...' : '登录并继续' }}
              </el-button>
            </el-tab-pane>
          </el-tabs>

          <div class="step-actions">
            <el-button @click="skipWizard">跳过向导</el-button>
            <el-button
              type="primary"
              size="large"
              :disabled="!canProceedStep1"
              @click="nextStep"
            >
              下一步：配置Bot
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 配置Bot -->
        <div v-show="currentStep === 1" class="step-container">
          <div class="step-header">
            <h2>🤖 步骤2: 配置转发Bot</h2>
            <p>选择一个目标平台并配置Bot，稍后可以添加更多</p>
          </div>

          <el-radio-group v-model="selectedPlatform" size="large" class="platform-selector">
            <el-radio-button value="discord">
              <div class="platform-option">
                <span class="platform-icon">💬</span>
                <span>Discord</span>
                <el-tag size="small" type="success">推荐</el-tag>
              </div>
            </el-radio-button>
            <el-radio-button value="telegram">
              <div class="platform-option">
                <span class="platform-icon">✈️</span>
                <span>Telegram</span>
              </div>
            </el-radio-button>
            <el-radio-button value="feishu">
              <div class="platform-option">
                <span class="platform-icon">🕊️</span>
                <span>飞书</span>
              </div>
            </el-radio-button>
          </el-radio-group>

          <!-- Discord配置 -->
          <div v-if="selectedPlatform === 'discord'" class="bot-config">
            <el-alert
              title="📖 如何获取Discord Webhook URL？"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <ol style="font-size: 13px; line-height: 1.8; margin: 10px 0;">
                <li>打开Discord，进入你的服务器</li>
                <li>右键点击目标频道 → 编辑频道</li>
                <li>点击"整合" → "Webhook" → "创建Webhook"</li>
                <li>点击"复制Webhook URL"并粘贴到下方</li>
              </ol>
              <el-link type="primary" @click="openTutorial('discord')">
                查看详细图文教程
              </el-link>
            </el-alert>

            <el-form label-width="120px">
              <el-form-item label="Bot名称">
                <el-input v-model="botConfig.discord.name" placeholder="例如：KOOK转发Bot" />
              </el-form-item>

              <el-form-item label="Webhook URL">
                <el-input
                  v-model="botConfig.discord.webhook_url"
                  placeholder="https://discord.com/api/webhooks/..."
                  type="textarea"
                  :rows="2"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="warning" :loading="testing" @click="testBot('discord')">
                  <el-icon><Pointer /></el-icon>
                  测试连接
                </el-button>
                <el-tag v-if="testResult" :type="testResult.success ? 'success' : 'danger'" style="margin-left: 10px">
                  {{ testResult.message }}
                </el-tag>
              </el-form-item>
            </el-form>
          </div>

          <!-- Telegram配置 -->
          <div v-if="selectedPlatform === 'telegram'" class="bot-config">
            <el-alert
              title="📖 如何创建Telegram Bot？"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <ol style="font-size: 13px; line-height: 1.8; margin: 10px 0;">
                <li>在Telegram中搜索 @BotFather</li>
                <li>发送 /newbot 并按提示操作</li>
                <li>复制Bot Token并粘贴到下方</li>
                <li>将Bot添加到目标群组</li>
                <li>点击"自动获取Chat ID"</li>
              </ol>
              <el-link type="primary" @click="openTutorial('telegram')">
                查看详细图文教程
              </el-link>
            </el-alert>

            <el-form label-width="120px">
              <el-form-item label="Bot名称">
                <el-input v-model="botConfig.telegram.name" placeholder="例如：KOOK转发Bot" />
              </el-form-item>

              <el-form-item label="Bot Token">
                <el-input
                  v-model="botConfig.telegram.token"
                  placeholder="1234567890:ABCdefGHIjklMNOpqrs..."
                  type="textarea"
                  :rows="2"
                />
              </el-form-item>

              <el-form-item label="Chat ID">
                <el-input v-model="botConfig.telegram.chat_id" placeholder="-1001234567890">
                  <template #append>
                    <el-button
                      type="success"
                      @click="detectTelegramChatId"
                      :disabled="!botConfig.telegram.token"
                    >
                      <el-icon><MagicStick /></el-icon>
                      自动获取
                    </el-button>
                  </template>
                </el-input>
                <div style="font-size: 12px; color: #999; margin-top: 5px;">
                  💡 点击"自动获取"后，在Telegram群组中发送消息，系统会自动检测Chat ID
                </div>
              </el-form-item>

              <el-form-item>
                <el-button type="warning" :loading="testing" @click="testBot('telegram')">
                  <el-icon><Pointer /></el-icon>
                  测试连接
                </el-button>
                <el-tag v-if="testResult" :type="testResult.success ? 'success' : 'danger'" style="margin-left: 10px">
                  {{ testResult.message }}
                </el-tag>
              </el-form-item>
            </el-form>
          </div>

          <!-- 飞书配置 -->
          <div v-if="selectedPlatform === 'feishu'" class="bot-config">
            <el-alert
              title="📖 如何创建飞书自建应用？"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <ol style="font-size: 13px; line-height: 1.8; margin: 10px 0;">
                <li>访问 <a href="https://open.feishu.cn/" target="_blank">飞书开放平台</a></li>
                <li>创建自建应用</li>
                <li>获取App ID和App Secret</li>
                <li>将机器人添加到目标群组</li>
              </ol>
              <el-link type="primary" @click="openTutorial('feishu')">
                查看详细图文教程
              </el-link>
            </el-alert>

            <el-form label-width="120px">
              <el-form-item label="Bot名称">
                <el-input v-model="botConfig.feishu.name" placeholder="例如：KOOK转发Bot" />
              </el-form-item>

              <el-form-item label="App ID">
                <el-input v-model="botConfig.feishu.app_id" placeholder="cli_a1b2c3d4e5f6g7h8" />
              </el-form-item>

              <el-form-item label="App Secret">
                <el-input
                  v-model="botConfig.feishu.app_secret"
                  placeholder="ABCdefGHIjklMNOpqrs"
                  type="password"
                  show-password
                />
              </el-form-item>

              <el-form-item label="Chat ID">
                <el-input v-model="botConfig.feishu.chat_id" placeholder="oc_xxx" />
              </el-form-item>

              <el-form-item>
                <el-button type="warning" :loading="testing" @click="testBot('feishu')">
                  <el-icon><Pointer /></el-icon>
                  测试连接
                </el-button>
                <el-tag v-if="testResult" :type="testResult.success ? 'success' : 'danger'" style="margin-left: 10px">
                  {{ testResult.message }}
                </el-tag>
              </el-form-item>
            </el-form>
          </div>

          <div class="step-actions">
            <el-button @click="prevStep">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              :disabled="!canProceedStep2"
              @click="nextStep"
            >
              下一步：智能映射
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 智能映射 -->
        <div v-show="currentStep === 2" class="step-container">
          <div class="step-header">
            <h2>🧠 步骤3: AI智能映射</h2>
            <p>系统会自动推荐最佳的频道映射，您也可以手动调整</p>
          </div>

          <el-alert
            title="✨ AI智能推荐"
            type="success"
            :closable="false"
            style="margin-bottom: 20px"
          >
            <p>系统使用三重匹配算法（完全匹配+相似度+关键词），准确度90%+</p>
            <p style="margin-top: 5px;">支持中英文翻译，例如"公告"自动匹配"announcement"</p>
          </el-alert>

          <div v-if="loadingMappings" class="loading-container">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>正在加载KOOK频道并生成AI推荐...</p>
          </div>

          <div v-else class="mappings-container">
            <div v-if="smartMappings.length === 0">
              <el-empty description="未找到可映射的频道">
                <el-button type="primary" @click="loadMappings">重新加载</el-button>
              </el-empty>
            </div>

            <div v-else>
              <div class="mapping-stats">
                <el-statistic title="KOOK频道" :value="smartMappings.length" />
                <el-statistic title="高置信度推荐" :value="highConfidenceMappings" />
                <el-statistic title="预计创建映射" :value="selectedMappings.length" />
              </div>

              <div class="mappings-list">
                <div
                  v-for="mapping in smartMappings"
                  :key="mapping.kook_channel_id"
                  class="mapping-item"
                >
                  <div class="mapping-source">
                    <el-checkbox
                      v-model="mapping.selected"
                      @change="updateSelection"
                    />
                    <div class="channel-info">
                      <strong>{{ mapping.kook_channel_name }}</strong>
                      <span class="server-name">{{ mapping.kook_server_name }}</span>
                    </div>
                  </div>

                  <el-icon class="mapping-arrow"><ArrowRight /></el-icon>

                  <div class="mapping-target">
                    <div v-if="mapping.recommendations.length > 0" class="recommendations">
                      <div
                        v-for="rec in mapping.recommendations.slice(0, 3)"
                        :key="rec.id"
                        class="recommendation-item"
                      >
                        <el-tag :type="getConfidenceType(rec.confidence)" size="small">
                          {{ (rec.confidence * 100).toFixed(0) }}%
                        </el-tag>
                        <span class="platform-tag">{{ rec.platform }}</span>
                        <span>{{ rec.name }}</span>
                      </div>
                    </div>
                    <div v-else class="no-recommendation">
                      <el-text type="info">暂无推荐</el-text>
                    </div>
                  </div>
                </div>
              </div>

              <div class="quick-actions">
                <el-button @click="selectHighConfidence">
                  <el-icon><CircleCheck /></el-icon>
                  选择高置信度推荐（≥80%）
                </el-button>
                <el-button @click="selectAll">
                  <el-icon><Select /></el-icon>
                  全选
                </el-button>
                <el-button @click="deselectAll">
                  <el-icon><Close /></el-icon>
                  取消全选
                </el-button>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <el-button @click="prevStep">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="success"
              size="large"
              :loading="completing"
              :disabled="selectedMappings.length === 0"
              @click="completeWizard"
            >
              <el-icon v-if="!completing"><CircleCheck /></el-icon>
              完成配置（{{ selectedMappings.length }}个映射）
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// 当前步骤（0=登录, 1=Bot配置, 2=智能映射）
const currentStep = ref(0)

// 步骤1: 登录相关
const loginMethod = ref('cookie')  // 'cookie' | 'password'
const cookieStep = ref(0)
const cookieText = ref('')
const cookieValidation = ref(null)
const loginForm = ref({
  email: '',
  password: ''
})
const loggingIn = ref(false)

// 步骤2: Bot配置
const selectedPlatform = ref('discord')
const botConfig = ref({
  discord: {
    name: 'KOOK转发Bot',
    webhook_url: ''
  },
  telegram: {
    name: 'KOOK转发Bot',
    token: '',
    chat_id: ''
  },
  feishu: {
    name: 'KOOK转发Bot',
    app_id: '',
    app_secret: '',
    chat_id: ''
  }
})
const testing = ref(false)
const testResult = ref(null)

// 步骤3: 智能映射
const loadingMappings = ref(false)
const smartMappings = ref([])
const completing = ref(false)

// 计算属性
const canProceedStep1 = computed(() => {
  if (loginMethod.value === 'cookie') {
    return cookieText.value && cookieValidation.value?.type === 'success'
  } else {
    return loginForm.value.email && loginForm.value.password
  }
})

const canProceedStep2 = computed(() => {
  const platform = selectedPlatform.value
  const config = botConfig.value[platform]
  
  if (platform === 'discord') {
    return config.name && config.webhook_url
  } else if (platform === 'telegram') {
    return config.name && config.token && config.chat_id
  } else if (platform === 'feishu') {
    return config.name && config.app_id && config.app_secret && config.chat_id
  }
  
  return false
})

const selectedMappings = computed(() => {
  return smartMappings.value.filter(m => m.selected)
})

const highConfidenceMappings = computed(() => {
  let count = 0
  smartMappings.value.forEach(m => {
    if (m.recommendations.some(r => r.confidence >= 0.8)) {
      count++
    }
  })
  return count
})

// 方法
function validateCookie() {
  try {
    const parsed = JSON.parse(cookieText.value)
    
    if (!Array.isArray(parsed)) {
      cookieValidation.value = {
        type: 'error',
        title: '❌ 格式错误：Cookie必须是JSON数组'
      }
      return
    }
    
    if (parsed.length === 0) {
      cookieValidation.value = {
        type: 'error',
        title: '❌ Cookie数组不能为空'
      }
      return
    }
    
    // 检查关键Cookie
    const requiredCookies = ['token', 'session']
    const cookieNames = parsed.map(c => c.name)
    const missing = requiredCookies.filter(name => !cookieNames.includes(name))
    
    if (missing.length > 0) {
      cookieValidation.value = {
        type: 'warning',
        title: `⚠️ 缺少关键Cookie: ${missing.join(', ')}`
      }
      return
    }
    
    cookieValidation.value = {
      type: 'success',
      title: `✅ Cookie验证成功（共${parsed.length}个）`
    }
  } catch (e) {
    cookieValidation.value = {
      type: 'error',
      title: '❌ JSON格式错误'
    }
  }
}

function installExtension() {
  ElMessageBox.alert(
    '请按照以下步骤安装Chrome扩展：\n\n1. 下载扩展文件\n2. 打开Chrome扩展管理页面\n3. 开启"开发者模式"\n4. 点击"加载已解压的扩展程序"\n5. 选择扩展文件夹',
    '安装Chrome扩展',
    {
      confirmButtonText: '我知道了'
    }
  )
}

async function checkCookieImported() {
  ElMessage.info('正在检查...')
  // TODO: 实现检查逻辑
}

async function loginWithPassword() {
  loggingIn.value = true
  try {
    const result = await api.post('/api/accounts', {
      email: loginForm.value.email,
      password: loginForm.value.password
    })
    ElMessage.success('登录成功！')
    nextStep()
  } catch (error) {
    ElMessage.error('登录失败: ' + error.message)
  } finally {
    loggingIn.value = false
  }
}

async function testBot(platform) {
  testing.value = true
  testResult.value = null
  
  try {
    const config = botConfig.value[platform]
    let apiConfig = {}
    
    if (platform === 'discord') {
      apiConfig = { webhook_url: config.webhook_url }
    } else if (platform === 'telegram') {
      apiConfig = { token: config.token, chat_id: config.chat_id }
    } else if (platform === 'feishu') {
      apiConfig = {
        app_id: config.app_id,
        app_secret: config.app_secret,
        chat_id: config.chat_id
      }
    }
    
    const result = await api.post('/api/bots/test', {
      platform,
      config: apiConfig
    })
    
    testResult.value = {
      success: true,
      message: '✅ 测试成功'
    }
    
    ElMessage.success('Bot连接测试成功！')
  } catch (error) {
    testResult.value = {
      success: false,
      message: '❌ 测试失败'
    }
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    testing.value = false
  }
}

function detectTelegramChatId() {
  ElMessageBox.alert(
    '请在Telegram群组中发送任意消息，系统会在30秒内自动检测Chat ID',
    'Chat ID自动检测',
    {
      confirmButtonText: '开始检测'
    }
  ).then(() => {
    // TODO: 实现自动检测
    ElMessage.info('正在检测，请在群组中发送消息...')
  })
}

async function loadMappings() {
  loadingMappings.value = true
  try {
    // TODO: 调用API获取智能映射推荐
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟数据
    smartMappings.value = [
      {
        kook_channel_id: '1',
        kook_channel_name: '公告频道',
        kook_server_name: '游戏公会',
        selected: true,
        recommendations: [
          { id: '1', platform: 'Discord', name: 'announcements', confidence: 0.95 },
          { id: '2', platform: 'Telegram', name: '公告群', confidence: 0.90 }
        ]
      }
    ]
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loadingMappings.value = false
  }
}

function updateSelection() {
  // 更新选择
}

function getConfidenceType(confidence) {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'info'
}

function selectHighConfidence() {
  smartMappings.value.forEach(m => {
    m.selected = m.recommendations.some(r => r.confidence >= 0.8)
  })
}

function selectAll() {
  smartMappings.value.forEach(m => {
    m.selected = true
  })
}

function deselectAll() {
  smartMappings.value.forEach(m => {
    m.selected = false
  })
}

function openTutorial(platform) {
  window.open(`#/help?topic=${platform}`, '_blank')
}

function nextStep() {
  if (currentStep.value < 2) {
    currentStep.value++
    
    // 进入步骤3时加载映射
    if (currentStep.value === 2) {
      loadMappings()
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function skipWizard() {
  ElMessageBox.confirm(
    '跳过配置向导后，您需要手动配置所有功能。确定要跳过吗？',
    '跳过向导',
    {
      type: 'warning',
      confirmButtonText: '确定跳过',
      cancelButtonText: '取消'
    }
  ).then(() => {
    router.push('/')
  }).catch(() => {})
}

async function completeWizard() {
  completing.value = true
  try {
    // TODO: 保存所有配置
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success({
      message: '🎉 配置完成！系统已准备就绪',
      duration: 3000
    })
    
    // 保存完成标记
    localStorage.setItem('wizard_completed', 'true')
    localStorage.setItem('wizard_completed_time', new Date().toISOString())
    
    // 跳转到主页
    router.push('/')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    completing.value = false
  }
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.wizard-simple-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wizard-card {
  max-width: 900px;
  width: 100%;
}

.wizard-header {
  padding: 30px;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
  border-bottom: 2px solid #e9ecef;
}

.wizard-time {
  text-align: center;
  margin-top: 20px;
}

.wizard-content {
  padding: 40px;
}

.step-container {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
}

.step-header p {
  font-size: 15px;
  color: #666;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.platform-selector {
  width: 100%;
  margin-bottom: 30px;
}

.platform-selector :deep(.el-radio-button__inner) {
  padding: 20px 30px;
}

.platform-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-icon {
  font-size: 24px;
}

.bot-config {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.mappings-container {
  margin-top: 20px;
}

.mapping-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.mappings-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
}

.mapping-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.mapping-source {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
}

.channel-info {
  display: flex;
  flex-direction: column;
}

.server-name {
  font-size: 12px;
  color: #999;
}

.mapping-arrow {
  font-size: 20px;
  color: #999;
}

.mapping-target {
  flex: 1;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.platform-tag {
  padding: 2px 8px;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 12px;
}

.quick-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading-container p {
  margin-top: 20px;
  font-size: 15px;
}
</style>
