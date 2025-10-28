<template>
  <div class="wizard-final-container">
    <el-card class="wizard-card" shadow="always">
      <!-- 标题 -->
      <div class="wizard-header">
        <h1>🚀 KOOK消息转发系统</h1>
        <p class="subtitle">3步配置，5分钟完成 · 零代码基础可用</p>
      </div>

      <!-- 进度指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps-bar">
        <el-step title="步骤1" description="连接KOOK">
          <template #icon>
            <el-icon :size="24"><Connection /></el-icon>
          </template>
        </el-step>
        <el-step title="步骤2" description="配置转发目标">
          <template #icon>
            <el-icon :size="24"><Setting /></el-icon>
          </template>
        </el-step>
        <el-step title="步骤3" description="智能映射">
          <template #icon>
            <el-icon :size="24"><Link /></el-icon>
          </template>
        </el-step>
      </el-steps>

      <!-- 步骤内容 -->
      <div class="wizard-content">
        <!-- ==================== 步骤1: 连接KOOK ==================== -->
        <div v-if="currentStep === 0" class="step-container step-1">
          <div class="step-header">
            <h2>📧 步骤1/3: 连接KOOK账号</h2>
            <p class="step-desc">选择一种方式连接您的KOOK账号（推荐Cookie导入，仅需30秒）</p>
          </div>

          <!-- 登录方式选择 -->
          <el-radio-group v-model="loginMethod" size="large" class="login-method-group">
            <el-radio-button value="cookie">
              <el-icon><Document /></el-icon>
              Cookie导入（推荐）
              <el-tag size="small" type="success">快速</el-tag>
            </el-radio-button>
            <el-radio-button value="password">
              <el-icon><Key /></el-icon>
              账号密码登录
            </el-radio-button>
          </el-radio-group>

          <!-- Cookie导入区域 -->
          <div v-if="loginMethod === 'cookie'" class="cookie-area">
            <el-alert
              title="📖 如何获取Cookie？"
              type="info"
              :closable="false"
              class="cookie-help"
            >
              <div class="help-content">
                <p><strong>方法1：浏览器扩展</strong>（最简单）</p>
                <ol>
                  <li>安装 <a href="#" @click.prevent="openCookieExtension">EditThisCookie</a> 扩展</li>
                  <li>打开 kookapp.cn 并登录</li>
                  <li>点击扩展 → Export → JSON格式</li>
                  <li>复制并粘贴到下方</li>
                </ol>
                <el-button link type="primary" @click="showCookieTutorial">
                  📺 观看视频教程
                </el-button>
              </div>
            </el-alert>

            <!-- 拖拽上传 -->
            <el-upload
              drag
              :auto-upload="false"
              :on-change="handleCookieFile"
              :show-file-list="false"
              accept=".json,.txt,.cookie"
              class="cookie-upload"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽Cookie文件到此处<br>
                或 <em>点击选择文件</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">支持JSON、Netscape、Header格式</div>
              </template>
            </el-upload>

            <!-- 或粘贴 -->
            <el-divider>或直接粘贴</el-divider>

            <el-input
              v-model="cookieText"
              type="textarea"
              :rows="6"
              placeholder="粘贴Cookie内容（自动识别格式）..."
              @input="handleCookiePaste"
              class="cookie-textarea"
            />

            <!-- 验证状态 -->
            <transition name="el-fade-in">
              <div v-if="cookieValidation.status" class="validation-result">
                <el-alert
                  :title="cookieValidation.message"
                  :type="cookieValidation.status"
                  :description="cookieValidation.detail"
                  show-icon
                  :closable="false"
                />
              </div>
            </transition>
          </div>

          <!-- 账号密码登录区域 -->
          <div v-else class="password-area">
            <el-form :model="loginForm" label-position="top" size="large">
              <el-form-item label="📧 KOOK邮箱">
                <el-input
                  v-model="loginForm.email"
                  placeholder="your@email.com"
                  clearable
                />
              </el-form-item>
              <el-form-item label="🔑 密码">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  clearable
                />
              </el-form-item>
            </el-form>

            <el-alert
              title="⚠️ 首次登录可能需要验证码"
              type="warning"
              :closable="false"
              description="如果出现验证码，系统会自动弹窗让您输入"
            />
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button size="large" @click="skipWizard">跳过向导</el-button>
            <el-button
              type="primary"
              size="large"
              :loading="step1Loading"
              :disabled="!canProceedStep1"
              @click="handleStep1Next"
            >
              下一步：配置Bot
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- ==================== 步骤2: 配置转发目标 ==================== -->
        <div v-if="currentStep === 1" class="step-container step-2">
          <div class="step-header">
            <h2>🤖 步骤2/3: 配置转发目标</h2>
            <p class="step-desc">添加至少一个Bot以接收转发消息</p>
          </div>

          <!-- Bot平台选择 -->
          <el-tabs v-model="activePlatform" class="bot-tabs">
            <!-- Discord -->
            <el-tab-pane label="Discord" name="discord">
              <div class="bot-config-panel">
                <div class="platform-icon">
                  <img src="@/assets/platforms/discord.svg" alt="Discord" />
                </div>
                
                <el-form :model="discordForm" label-position="top" size="large">
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
                      clearable
                    />
                    <template #extra>
                      <el-button link type="primary" @click="showDiscordTutorial">
                        📖 如何创建Discord Webhook?
                      </el-button>
                    </template>
                  </el-form-item>
                </el-form>

                <div class="bot-actions">
                  <el-button
                    size="large"
                    :loading="testingBot"
                    @click="testDiscordBot"
                  >
                    🧪 测试连接
                  </el-button>
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!discordForm.webhook_url"
                    @click="addDiscordBot"
                  >
                    ➕ 添加此Bot
                  </el-button>
                </div>
              </div>
            </el-tab-pane>

            <!-- Telegram -->
            <el-tab-pane label="Telegram" name="telegram">
              <div class="bot-config-panel">
                <div class="platform-icon">
                  <img src="@/assets/platforms/telegram.svg" alt="Telegram" />
                </div>
                
                <el-form :model="telegramForm" label-position="top" size="large">
                  <el-form-item label="Bot名称">
                    <el-input
                      v-model="telegramForm.name"
                      placeholder="例如：游戏公告TG Bot"
                    />
                  </el-form-item>
                  
                  <el-form-item label="Bot Token">
                    <el-input
                      v-model="telegramForm.bot_token"
                      placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                      clearable
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="Chat ID">
                    <el-input
                      v-model="telegramForm.chat_id"
                      placeholder="-1001234567890"
                      clearable
                    >
                      <template #append>
                        <el-button @click="autoGetChatId" :loading="gettingChatId">
                          🔍 自动获取
                        </el-button>
                      </template>
                    </el-input>
                    <template #extra>
                      <el-button link type="primary" @click="showTelegramTutorial">
                        📖 如何创建Telegram Bot?
                      </el-button>
                    </template>
                  </el-form-item>
                </el-form>

                <div class="bot-actions">
                  <el-button
                    size="large"
                    :loading="testingBot"
                    @click="testTelegramBot"
                  >
                    🧪 测试连接
                  </el-button>
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!telegramForm.bot_token || !telegramForm.chat_id"
                    @click="addTelegramBot"
                  >
                    ➕ 添加此Bot
                  </el-button>
                </div>
              </div>
            </el-tab-pane>

            <!-- 飞书 -->
            <el-tab-pane label="飞书" name="feishu">
              <div class="bot-config-panel">
                <div class="platform-icon">
                  <img src="@/assets/platforms/feishu.svg" alt="飞书" />
                </div>
                
                <el-form :model="feishuForm" label-position="top" size="large">
                  <el-form-item label="应用名称">
                    <el-input
                      v-model="feishuForm.name"
                      placeholder="例如：游戏公告飞书Bot"
                    />
                  </el-form-item>
                  
                  <el-form-item label="App ID">
                    <el-input
                      v-model="feishuForm.app_id"
                      placeholder="cli_a1b2c3d4e5f6g7h8"
                      clearable
                    />
                  </el-form-item>
                  
                  <el-form-item label="App Secret">
                    <el-input
                      v-model="feishuForm.app_secret"
                      placeholder="ABCdefGHIjklMNOpqrs"
                      clearable
                      show-password
                    />
                    <template #extra>
                      <el-button link type="primary" @click="showFeishuTutorial">
                        📖 如何创建飞书应用?
                      </el-button>
                    </template>
                  </el-form-item>
                </el-form>

                <div class="bot-actions">
                  <el-button
                    size="large"
                    :loading="testingBot"
                    @click="testFeishuBot"
                  >
                    🧪 测试连接
                  </el-button>
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!feishuForm.app_id || !feishuForm.app_secret"
                    @click="addFeishuBot"
                  >
                    ➕ 添加此Bot
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 已添加的Bot列表 -->
          <div v-if="addedBots.length > 0" class="added-bots">
            <el-divider content-position="left">
              <el-icon><Check /></el-icon>
              已添加的Bot ({{ addedBots.length }})
            </el-divider>
            
            <div class="bots-list">
              <el-tag
                v-for="bot in addedBots"
                :key="bot.id"
                size="large"
                closable
                @close="removeBot(bot.id)"
                class="bot-tag"
              >
                <el-icon><Select /></el-icon>
                {{ bot.name }} ({{ bot.platform }})
              </el-tag>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button size="large" @click="currentStep = 0">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              :disabled="addedBots.length === 0"
              @click="handleStep2Next"
            >
              下一步：智能映射
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- ==================== 步骤3: 智能映射 ==================== -->
        <div v-if="currentStep === 2" class="step-container step-3">
          <div class="step-header">
            <h2>🔀 步骤3/3: 智能映射</h2>
            <p class="step-desc">自动匹配KOOK频道到转发目标</p>
          </div>

          <!-- 映射模式选择 -->
          <el-radio-group v-model="mappingMode" size="large" class="mapping-mode-group">
            <el-radio-button value="auto">
              <el-icon><MagicStick /></el-icon>
              智能自动映射
              <el-tag size="small" type="success">推荐</el-tag>
            </el-radio-button>
            <el-radio-button value="manual">
              <el-icon><Edit /></el-icon>
              手动配置
            </el-radio-button>
          </el-radio-group>

          <!-- 智能映射区域 -->
          <div v-if="mappingMode === 'auto'" class="auto-mapping-area">
            <el-alert
              title="🤖 智能映射说明"
              type="info"
              :closable="false"
              class="mapping-info"
            >
              <p>系统将自动识别KOOK频道名称，并在目标平台查找同名或相似频道建立映射关系。</p>
              <p><strong>示例：</strong></p>
              <ul>
                <li>KOOK "#公告" → Discord "#announcements" (规则匹配)</li>
                <li>KOOK "#技术讨论" → Telegram "技术讨论群" (完全匹配)</li>
              </ul>
            </el-alert>

            <div v-if="!mappingGenerated" class="generate-mapping">
              <el-button
                type="primary"
                size="large"
                :loading="generatingMapping"
                @click="generateAutoMapping"
              >
                <el-icon><MagicStick /></el-icon>
                开始自动匹配
              </el-button>
            </div>

            <!-- 映射预览 -->
            <div v-else class="mapping-preview">
              <div class="preview-header">
                <h3>
                  <el-icon><View /></el-icon>
                  映射预览（共 {{ autoMappings.length }} 个）
                </h3>
                <p>您可以调整或删除不正确的映射</p>
              </div>

              <el-table :data="autoMappings" border stripe>
                <el-table-column label="KOOK频道" width="250">
                  <template #default="{ row }">
                    <div class="channel-cell">
                      <el-icon><Folder /></el-icon>
                      <span class="server-name">{{ row.kook_server }}</span>
                      <el-icon><ArrowRight /></el-icon>
                      <span class="channel-name">{{ row.kook_channel }}</span>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="" width="60" align="center">
                  <template #default>
                    <el-icon :size="20"><Right /></el-icon>
                  </template>
                </el-table-column>

                <el-table-column label="转发目标" min-width="250">
                  <template #default="{ row }">
                    <el-select
                      v-model="row.target"
                      placeholder="选择目标频道"
                      filterable
                      size="large"
                    >
                      <el-option
                        v-for="target in availableTargets"
                        :key="target.id"
                        :label="`${target.bot_name} - ${target.channel_name}`"
                        :value="target.id"
                      />
                    </el-select>
                  </template>
                </el-table-column>

                <el-table-column label="匹配度" width="120">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="row.confidence * 100"
                      :status="row.confidence > 0.8 ? 'success' : 'warning'"
                      :stroke-width="8"
                    />
                  </template>
                </el-table-column>

                <el-table-column label="匹配理由" width="150">
                  <template #default="{ row }">
                    <el-tag
                      :type="row.confidence > 0.8 ? 'success' : 'warning'"
                      size="small"
                    >
                      {{ row.match_reason }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row, $index }">
                    <el-button
                      type="danger"
                      link
                      @click="removeMapping($index)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 批量操作 -->
              <div class="batch-actions">
                <el-button @click="regenerateMapping">
                  <el-icon><Refresh /></el-icon>
                  重新生成
                </el-button>
                <el-button @click="addManualMapping">
                  <el-icon><Plus /></el-icon>
                  手动添加
                </el-button>
              </div>
            </div>
          </div>

          <!-- 手动映射区域 -->
          <div v-else class="manual-mapping-area">
            <p class="manual-tip">请手动选择KOOK频道和转发目标建立映射关系</p>
            <!-- 手动映射界面 -->
            <!-- 此处可以复用现有的手动映射组件 -->
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button size="large" @click="currentStep = 1">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="success"
              size="large"
              :disabled="!canComplete"
              :loading="completing"
              @click="completeWizard"
            >
              <el-icon><Check /></el-icon>
              完成配置并启动
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
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  Connection, Setting, Link, Document, Key, Upload, UploadFilled,
  ArrowRight, ArrowLeft, Check, Select, MagicStick, Edit, View,
  Folder, Right, Refresh, Plus
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// ==================== 步骤控制 ====================
const currentStep = ref(0)

// ==================== 步骤1：连接KOOK ====================
const loginMethod = ref('cookie')
const cookieText = ref('')
const cookieValidation = ref({
  status: '',
  message: '',
  detail: ''
})
const loginForm = ref({
  email: '',
  password: ''
})
const step1Loading = ref(false)
const accountId = ref(null)

// Cookie文件上传处理（完整实现）
const handleCookieFile = (file) => {
  const reader = new FileReader()
  
  reader.onload = async (e) => {
    try {
      let cookieContent = e.target.result
      
      // 尝试解析为JSON
      try {
        const cookieJson = JSON.parse(cookieContent)
        
        // Netscape格式（数组）- EditThisCookie导出格式
        if (Array.isArray(cookieJson)) {
          // 验证是否包含必要字段
          const hasRequiredFields = cookieJson.every(c => 
            c.hasOwnProperty('name') && 
            c.hasOwnProperty('value') &&
            c.hasOwnProperty('domain')
          )
          
          if (hasRequiredFields) {
            cookieText.value = JSON.stringify(cookieJson, null, 2)
            ElMessage.success('✅ Cookie文件加载成功（JSON格式）')
          } else {
            ElMessage.warning('⚠️ Cookie文件格式不完整，请检查')
            return
          }
        } 
        // 对象格式
        else if (typeof cookieJson === 'object') {
          // 转换为数组格式
          const cookieArray = Object.entries(cookieJson).map(([name, value]) => ({
            name,
            value: String(value),
            domain: '.kookapp.cn',
            path: '/',
            secure: true,
            httpOnly: false
          }))
          
          cookieText.value = JSON.stringify(cookieArray, null, 2)
          ElMessage.success('✅ Cookie文件加载成功（对象格式已转换）')
        }
      } catch (jsonError) {
        // 不是JSON格式，尝试解析为Netscape格式
        // Netscape格式示例：
        // # Netscape HTTP Cookie File
        // .kookapp.cn	TRUE	/	TRUE	0	token	xxx
        
        if (cookieContent.includes('Netscape HTTP Cookie File')) {
          const lines = cookieContent.split('\n')
          const cookies = []
          
          for (const line of lines) {
            // 跳过注释行和空行
            if (line.startsWith('#') || !line.trim()) continue
            
            const parts = line.split('\t')
            if (parts.length >= 7) {
              cookies.push({
                name: parts[5],
                value: parts[6],
                domain: parts[0],
                path: parts[2],
                secure: parts[3] === 'TRUE',
                httpOnly: false,
                expirationDate: parseInt(parts[4]) || undefined
              })
            }
          }
          
          if (cookies.length > 0) {
            cookieText.value = JSON.stringify(cookies, null, 2)
            ElMessage.success(`✅ Cookie文件加载成功（Netscape格式，共${cookies.length}个）`)
          } else {
            ElMessage.error('❌ 无法解析Netscape格式Cookie')
            return
          }
        } else {
          // 纯文本格式，可能是Header String格式
          // 格式: name1=value1; name2=value2; ...
          if (cookieContent.includes('=')) {
            const pairs = cookieContent.split(';').map(p => p.trim())
            const cookies = []
            
            for (const pair of pairs) {
              const [name, value] = pair.split('=')
              if (name && value) {
                cookies.push({
                  name: name.trim(),
                  value: value.trim(),
                  domain: '.kookapp.cn',
                  path: '/',
                  secure: true,
                  httpOnly: false
                })
              }
            }
            
            if (cookies.length > 0) {
              cookieText.value = JSON.stringify(cookies, null, 2)
              ElMessage.success(`✅ Cookie加载成功（Header格式，共${cookies.length}个）`)
            } else {
              ElMessage.error('❌ 无法解析Cookie格式')
              return
            }
          } else {
            ElMessage.error('❌ Cookie文件格式不支持')
            return
          }
        }
      }
      
      // 触发验证
      await handleCookiePaste()
      
    } catch (error) {
      ElMessage.error('❌ Cookie文件解析失败: ' + error.message)
      console.error('Cookie解析错误:', error)
    }
  }
  
  reader.onerror = () => {
    ElMessage.error('❌ 文件读取失败')
  }
  
  reader.readAsText(file.raw)
}

// Cookie粘贴处理
const handleCookiePaste = async () => {
  if (!cookieText.value.trim()) {
    cookieValidation.value = { status: '', message: '', detail: '' }
    return
  }

  cookieValidation.value = {
    status: 'info',
    message: '正在验证Cookie...',
    detail: ''
  }

  try {
    const response = await api.post('/api/cookie-import/validate', {
      cookie: cookieText.value
    })

    if (response.data.valid) {
      cookieValidation.value = {
        status: 'success',
        message: '✅ Cookie验证成功',
        detail: `域名验证通过 · 格式：${response.data.format} · 有效期：${response.data.expiry_days}天`
      }
    } else {
      cookieValidation.value = {
        status: 'error',
        message: '❌ Cookie验证失败',
        detail: response.data.error || '无法识别Cookie格式或Cookie已过期'
      }
    }
  } catch (error) {
    cookieValidation.value = {
      status: 'error',
      message: '❌ 验证失败',
      detail: error.response?.data?.message || '服务器连接失败'
    }
  }
}

const canProceedStep1 = computed(() => {
  if (loginMethod.value === 'cookie') {
    return cookieValidation.value.status === 'success'
  } else {
    return loginForm.value.email && loginForm.value.password
  }
})

const handleStep1Next = async () => {
  step1Loading.value = true
  
  try {
    if (loginMethod.value === 'cookie') {
      // Cookie登录
      const response = await api.post('/api/accounts/add-by-cookie', {
        cookie: cookieText.value
      })
      accountId.value = response.data.account_id
      ElMessage.success('✅ KOOK账号连接成功')
    } else {
      // 账号密码登录
      const response = await api.post('/api/accounts/add-by-password', {
        email: loginForm.value.email,
        password: loginForm.value.password
      })
      accountId.value = response.data.account_id
      ElMessage.success('✅ KOOK账号登录成功')
    }
    
    currentStep.value = 1
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '连接失败，请检查Cookie或账号密码')
  } finally {
    step1Loading.value = false
  }
}

// ==================== 步骤2：配置Bot ====================
const activePlatform = ref('discord')
const addedBots = ref([])
const testingBot = ref(false)
const gettingChatId = ref(false)

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
  app_secret: ''
})

const testDiscordBot = async () => {
  if (!discordForm.value.webhook_url) {
    ElMessage.warning('请先输入Webhook URL')
    return
  }

  testingBot.value = true
  try {
    await api.post('/api/bots/test', {
      platform: 'discord',
      config: { webhook_url: discordForm.value.webhook_url }
    })
    ElMessage.success('✅ Discord Bot测试成功')
  } catch (error) {
    ElMessage.error('❌ 测试失败：' + (error.response?.data?.message || '连接失败'))
  } finally {
    testingBot.value = false
  }
}

const addDiscordBot = async () => {
  try {
    const response = await api.post('/api/bots/add', {
      platform: 'discord',
      name: discordForm.value.name || 'Discord Bot',
      config: { webhook_url: discordForm.value.webhook_url }
    })
    
    addedBots.value.push({
      id: response.data.bot_id,
      name: discordForm.value.name || 'Discord Bot',
      platform: 'Discord'
    })
    
    ElMessage.success('✅ Discord Bot添加成功')
    discordForm.value = { name: '', webhook_url: '' }
  } catch (error) {
    ElMessage.error('添加失败：' + (error.response?.data?.message || '服务器错误'))
  }
}

const testTelegramBot = async () => {
  testingBot.value = true
  try {
    await api.post('/api/bots/test', {
      platform: 'telegram',
      config: {
        bot_token: telegramForm.value.bot_token,
        chat_id: telegramForm.value.chat_id
      }
    })
    ElMessage.success('✅ Telegram Bot测试成功')
  } catch (error) {
    ElMessage.error('❌ 测试失败：' + (error.response?.data?.message || '连接失败'))
  } finally {
    testingBot.value = false
  }
}

const autoGetChatId = async () => {
  if (!telegramForm.value.bot_token) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  gettingChatId.value = true
  try {
    const response = await api.post('/api/telegram-helper/get-chat-id', {
      bot_token: telegramForm.value.bot_token
    })
    telegramForm.value.chat_id = response.data.chat_id
    ElMessage.success('✅ Chat ID获取成功')
  } catch (error) {
    ElMessage.error('获取失败：' + (error.response?.data?.message || '请确保Bot已添加到群组'))
  } finally {
    gettingChatId.value = false
  }
}

const addTelegramBot = async () => {
  try {
    const response = await api.post('/api/bots/add', {
      platform: 'telegram',
      name: telegramForm.value.name || 'Telegram Bot',
      config: {
        bot_token: telegramForm.value.bot_token,
        chat_id: telegramForm.value.chat_id
      }
    })
    
    addedBots.value.push({
      id: response.data.bot_id,
      name: telegramForm.value.name || 'Telegram Bot',
      platform: 'Telegram'
    })
    
    ElMessage.success('✅ Telegram Bot添加成功')
    telegramForm.value = { name: '', bot_token: '', chat_id: '' }
  } catch (error) {
    ElMessage.error('添加失败：' + (error.response?.data?.message || '服务器错误'))
  }
}

const testFeishuBot = async () => {
  testingBot.value = true
  try {
    await api.post('/api/bots/test', {
      platform: 'feishu',
      config: {
        app_id: feishuForm.value.app_id,
        app_secret: feishuForm.value.app_secret
      }
    })
    ElMessage.success('✅ 飞书Bot测试成功')
  } catch (error) {
    ElMessage.error('❌ 测试失败：' + (error.response?.data?.message || '连接失败'))
  } finally {
    testingBot.value = false
  }
}

const addFeishuBot = async () => {
  try {
    const response = await api.post('/api/bots/add', {
      platform: 'feishu',
      name: feishuForm.value.name || '飞书Bot',
      config: {
        app_id: feishuForm.value.app_id,
        app_secret: feishuForm.value.app_secret
      }
    })
    
    addedBots.value.push({
      id: response.data.bot_id,
      name: feishuForm.value.name || '飞书Bot',
      platform: '飞书'
    })
    
    ElMessage.success('✅ 飞书Bot添加成功')
    feishuForm.value = { name: '', app_id: '', app_secret: '' }
  } catch (error) {
    ElMessage.error('添加失败：' + (error.response?.data?.message || '服务器错误'))
  }
}

const removeBot = (botId) => {
  addedBots.value = addedBots.value.filter(b => b.id !== botId)
}

const handleStep2Next = () => {
  currentStep.value = 2
}

// ==================== 步骤3：智能映射 ====================
const mappingMode = ref('auto')
const mappingGenerated = ref(false)
const generatingMapping = ref(false)
const autoMappings = ref([])
const availableTargets = ref([])

const generateAutoMapping = async () => {
  generatingMapping.value = true
  
  try {
    const response = await api.post('/api/smart-mapping/auto-match', {
      account_id: accountId.value,
      bot_ids: addedBots.value.map(b => b.id)
    })
    
    autoMappings.value = response.data.mappings
    availableTargets.value = response.data.available_targets
    mappingGenerated.value = true
    
    ElNotification({
      title: '✅ 智能映射完成',
      message: `成功匹配 ${autoMappings.value.length} 个频道`,
      type: 'success'
    })
  } catch (error) {
    ElMessage.error('自动匹配失败：' + (error.response?.data?.message || '服务器错误'))
  } finally {
    generatingMapping.value = false
  }
}

const removeMapping = (index) => {
  autoMappings.value.splice(index, 1)
}

const regenerateMapping = () => {
  mappingGenerated.value = false
  autoMappings.value = []
}

const addManualMapping = () => {
  // 打开手动添加映射对话框
  ElMessage.info('手动添加功能开发中')
}

const canComplete = computed(() => {
  return autoMappings.value.length > 0
})

const completing = ref(false)

const completeWizard = async () => {
  completing.value = true
  
  try {
    // 保存映射
    await api.post('/api/mappings/batch-save', {
      mappings: autoMappings.value
    })
    
    // 启动服务
    await api.post('/api/system/start')
    
    ElNotification({
      title: '🎉 配置完成',
      message: '系统已启动，开始转发消息！',
      type: 'success',
      duration: 5000
    })
    
    // 跳转到主界面
    router.push('/')
  } catch (error) {
    ElMessage.error('完成配置失败：' + (error.response?.data?.message || '服务器错误'))
  } finally {
    completing.value = false
  }
}

// ==================== 辅助功能 ====================
const skipWizard = () => {
  ElMessageBox.confirm(
    '跳过向导后，您需要在主界面手动配置所有设置。确定跳过吗？',
    '确认跳过',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置',
      type: 'warning'
    }
  ).then(() => {
    router.push('/')
  }).catch(() => {})
}

const openCookieExtension = () => {
  window.open('https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg', '_blank')
}

const showCookieTutorial = () => {
  // 打开Cookie教程对话框
  ElMessage.info('教程功能开发中')
}

const showDiscordTutorial = () => {
  // 打开Discord教程
  ElMessage.info('教程功能开发中')
}

const showTelegramTutorial = () => {
  // 打开Telegram教程
  ElMessage.info('教程功能开发中')
}

const showFeishuTutorial = () => {
  // 打开飞书教程
  ElMessage.info('教程功能开发中')
}

onMounted(() => {
  // 检查是否已经配置过
  // 如果已配置，询问是否重新配置
})
</script>

<style scoped lang="scss">
.wizard-final-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.wizard-card {
  max-width: 1000px;
  width: 100%;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.wizard-header {
  text-align: center;
  padding: 20px 0;
  
  h1 {
    font-size: 32px;
    font-weight: bold;
    color: #303133;
    margin: 0 0 10px 0;
  }
  
  .subtitle {
    font-size: 16px;
    color: #909399;
    margin: 0;
  }
}

.steps-bar {
  margin: 30px 0;
}

.wizard-content {
  min-height: 500px;
  padding: 20px;
}

.step-container {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
  
  h2 {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin: 0 0 10px 0;
  }
  
  .step-desc {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.login-method-group {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  
  :deep(.el-radio-button) {
    margin: 0 10px;
  }
}

.cookie-area,
.password-area {
  max-width: 700px;
  margin: 0 auto;
}

.cookie-help {
  margin-bottom: 20px;
  
  .help-content {
    ol {
      margin: 10px 0;
      padding-left: 20px;
      
      li {
        margin: 5px 0;
      }
    }
  }
}

.cookie-upload {
  margin: 20px 0;
}

.cookie-textarea {
  margin: 20px 0;
}

.validation-result {
  margin-top: 20px;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.bot-tabs {
  margin-bottom: 30px;
}

.bot-config-panel {
  max-width: 600px;
  margin: 0 auto;
  
  .platform-icon {
    text-align: center;
    margin-bottom: 20px;
    
    img {
      width: 80px;
      height: 80px;
    }
  }
}

.bot-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.added-bots {
  margin-top: 30px;
  
  .bots-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    
    .bot-tag {
      font-size: 14px;
      padding: 8px 16px;
    }
  }
}

.mapping-mode-group {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.auto-mapping-area {
  .mapping-info {
    margin-bottom: 30px;
    
    ul {
      margin: 10px 0;
      padding-left: 20px;
      
      li {
        margin: 5px 0;
      }
    }
  }
  
  .generate-mapping {
    text-align: center;
    padding: 40px 0;
  }
}

.mapping-preview {
  .preview-header {
    margin-bottom: 20px;
    
    h3 {
      font-size: 18px;
      font-weight: bold;
      margin: 0 0 5px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    p {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }
  
  .channel-cell {
    display: flex;
    align-items: center;
    gap: 5px;
    
    .server-name {
      color: #909399;
      font-size: 12px;
    }
    
    .channel-name {
      font-weight: bold;
    }
  }
  
  .batch-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
  }
}

.manual-mapping-area {
  .manual-tip {
    text-align: center;
    color: #909399;
    margin-bottom: 20px;
  }
}
</style>
