<template>
  <div class="wizard-container">
    <!-- 进度条 -->
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="欢迎" icon="InfoFilled"></el-step>
      <el-step title="登录KOOK" icon="User"></el-step>
      <el-step title="选择服务器" icon="OfficeBuilding"></el-step>
      <el-step title="配置Bot" icon="Setting"></el-step>
      <el-step title="频道映射" icon="Connection"></el-step>
    </el-steps>

    <!-- 步骤内容 -->
    <div class="step-content">
      <!-- 步骤0: 欢迎页 -->
      <div v-if="currentStep === 0" class="step-welcome">
        <div class="welcome-icon">🎉</div>
        <h1>欢迎使用 KOOK消息转发系统</h1>
        <p class="subtitle">本向导将帮助您完成基础配置</p>
        <p class="time-estimate">⏱️ 预计耗时：3-5分钟</p>
        
        <el-card class="feature-card">
          <h3>✨ 主要功能</h3>
          <ul>
            <li>🔄 实时转发KOOK消息到Discord/Telegram/飞书</li>
            <li>🎨 智能格式转换，保留原始排版</li>
            <li>🖼️ 自动处理图片和附件</li>
            <li>⚡ 零代码配置，图形化操作</li>
          </ul>
        </el-card>

        <el-card class="disclaimer-card">
          <h3>⚠️ 免责声明</h3>
          <div class="disclaimer-content">
            <p>请注意：</p>
            <ol>
              <li>本软件通过浏览器自动化抓取KOOK消息，可能违反KOOK服务条款</li>
              <li>使用本软件可能导致账号被封禁，请仅在已获授权的场景下使用</li>
              <li>转发的消息内容可能涉及版权，请遵守相关法律法规</li>
              <li>本软件仅供学习交流使用，开发者不承担任何法律责任</li>
            </ol>
            <el-checkbox v-model="disclaimerAccepted" style="margin-top: 20px">
              我已阅读并同意以上条款
            </el-checkbox>
          </div>
        </el-card>

        <div class="step-actions">
          <el-button type="primary" size="large" @click="nextStep" :disabled="!disclaimerAccepted">
            开始配置 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" @click="skipWizard">跳过向导</el-button>
        </div>
      </div>

      <!-- 步骤1: 登录KOOK -->
      <div v-if="currentStep === 1" class="step-login">
        <h2>📧 登录KOOK账号</h2>
        
        <el-tabs v-model="loginMethod" class="login-tabs">
          <!-- 方式1: Cookie导入（推荐） -->
          <el-tab-pane label="Cookie导入（推荐）" name="cookie">
            <el-alert
              title="💡 推荐方式：使用Chrome扩展一键导出"
              type="success"
              :closable="false"
              style="margin-bottom: 20px">
              <p>成功率高达99%，仅需5秒即可完成</p>
              <el-button type="primary" size="small" @click="openChromeExtension">
                安装Chrome扩展
              </el-button>
            </el-alert>

            <el-card>
              <el-upload
                drag
                :auto-upload="false"
                :on-change="handleCookieFile"
                :show-file-list="false"
                accept=".json,.txt">
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  将Cookie JSON文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">支持JSON、Netscape、HTTP Header等多种格式</div>
                </template>
              </el-upload>

              <el-divider>或</el-divider>

              <el-form-item label="直接粘贴Cookie">
                <el-input
                  v-model="cookieText"
                  type="textarea"
                  :rows="6"
                  placeholder="粘贴从浏览器复制的Cookie内容">
                </el-input>
              </el-form-item>

              <el-button type="primary" @click="validateCookie" :loading="validating">
                验证Cookie
              </el-button>
              <el-button @click="showCookieHelp">
                📖 如何获取Cookie？
              </el-button>
            </el-card>
          </el-tab-pane>

          <!-- 方式2: 账号密码 -->
          <el-tab-pane label="账号密码" name="password">
            <el-form :model="loginForm" label-width="100px">
              <el-form-item label="邮箱">
                <el-input v-model="loginForm.email" placeholder="your@email.com"></el-input>
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="loginForm.password" type="password" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loginWithPassword" :loading="loggingIn">
                  登录
                </el-button>
              </el-form-item>
            </el-form>

            <el-alert
              title="⚠️ 提示"
              type="warning"
              :closable="false">
              首次登录可能需要输入验证码，请耐心等待
            </el-alert>
          </el-tab-pane>
        </el-tabs>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="!accountConnected">
            下一步
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 选择服务器 -->
      <div v-if="currentStep === 2" class="step-servers">
        <h2>🏠 选择要监听的KOOK服务器</h2>
        
        <el-alert
          title="加载中..."
          type="info"
          v-if="loadingServers"
          :closable="false">
          正在获取服务器列表，请稍候...
        </el-alert>

        <div v-else class="servers-grid">
          <el-card 
            v-for="server in servers" 
            :key="server.id"
            class="server-card"
            :class="{ 'selected': selectedServers.includes(server.id) }"
            @click="toggleServer(server.id)">
            <div class="server-icon">
              <img v-if="server.icon" :src="server.icon" />
              <div v-else class="server-icon-placeholder">{{ server.name[0] }}</div>
            </div>
            <div class="server-name">{{ server.name }}</div>
            <el-icon v-if="selectedServers.includes(server.id)" class="selected-icon">
              <CircleCheckFilled />
            </el-icon>
            
            <!-- 频道列表 -->
            <div v-if="selectedServers.includes(server.id)" class="channels-list">
              <el-divider>频道列表</el-divider>
              <el-checkbox-group v-model="selectedChannels[server.id]">
                <el-checkbox 
                  v-for="channel in server.channels" 
                  :key="channel.id"
                  :label="channel.id">
                  # {{ channel.name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </el-card>
        </div>

        <div class="quick-actions">
          <el-button @click="selectAllServers">全选</el-button>
          <el-button @click="deselectAllServers">全不选</el-button>
        </div>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="selectedServers.length === 0">
            下一步（已选 {{ selectedServers.length }} 个服务器）
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 配置Bot -->
      <div v-if="currentStep === 3" class="step-bots">
        <h2>🤖 配置转发Bot</h2>
        
        <el-tabs v-model="activeBotTab" type="card">
          <el-tab-pane label="Discord" name="discord">
            <el-form label-width="120px">
              <el-form-item label="Webhook名称">
                <el-input v-model="discordBot.name" placeholder="例如：游戏公告Bot"></el-input>
              </el-form-item>
              <el-form-item label="Webhook URL">
                <el-input 
                  v-model="discordBot.webhook_url" 
                  placeholder="https://discord.com/api/webhooks/...">
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="testBot('discord')" :loading="testingBot">
                  🧪 测试连接
                </el-button>
                <el-button @click="showDiscordHelp">
                  📖 如何创建Webhook？
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="Telegram" name="telegram">
            <el-form label-width="120px">
              <el-form-item label="Bot名称">
                <el-input v-model="telegramBot.name" placeholder="例如：游戏公告TG Bot"></el-input>
              </el-form-item>
              <el-form-item label="Bot Token">
                <el-input 
                  v-model="telegramBot.token" 
                  placeholder="1234567890:ABCdefGHIjklMNOpqrs">
                </el-input>
              </el-form-item>
              <el-form-item label="Chat ID">
                <el-input v-model="telegramBot.chat_id" placeholder="-1001234567890">
                  <template #append>
                    <el-button @click="autoGetChatId">🔍 自动获取</el-button>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="testBot('telegram')" :loading="testingBot">
                  🧪 测试连接
                </el-button>
                <el-button @click="showTelegramHelp">
                  📖 配置教程
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="飞书" name="feishu">
            <el-form label-width="120px">
              <el-form-item label="应用名称">
                <el-input v-model="feishuBot.name" placeholder="例如：游戏公告飞书Bot"></el-input>
              </el-form-item>
              <el-form-item label="App ID">
                <el-input v-model="feishuBot.app_id" placeholder="cli_a1b2c3d4e5f6g7h8"></el-input>
              </el-form-item>
              <el-form-item label="App Secret">
                <el-input v-model="feishuBot.app_secret" type="password" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="testBot('feishu')" :loading="testingBot">
                  🧪 测试连接
                </el-button>
                <el-button @click="showFeishuHelp">
                  📺 观看视频教程
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <div class="configured-bots">
          <h3>已配置的Bot</h3>
          <el-empty v-if="configuredBots.length === 0" description="还没有配置Bot"></el-empty>
          <el-tag
            v-for="bot in configuredBots"
            :key="bot.id"
            type="success"
            closable
            @close="removeBot(bot.id)"
            style="margin-right: 10px">
            {{ bot.platform }} - {{ bot.name }}
          </el-tag>
        </div>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="configuredBots.length === 0">
            下一步（已配置 {{ configuredBots.length }} 个Bot）
          </el-button>
        </div>
      </div>

      <!-- 步骤4: 频道映射 -->
      <div v-if="currentStep === 4" class="step-mapping">
        <h2>🔀 频道映射配置</h2>
        
        <el-alert
          title="💡 推荐：使用智能映射自动匹配同名频道"
          type="info"
          :closable="false"
          style="margin-bottom: 20px">
          <el-button type="primary" @click="autoMap" :loading="autoMapping">
            <el-icon><Magic /></el-icon>
            一键智能映射（95%准确）
          </el-button>
        </el-alert>

        <el-radio-group v-model="mappingMode" class="mapping-mode">
          <el-radio-button label="auto">智能映射（推荐）</el-radio-button>
          <el-radio-button label="manual">手动映射</el-radio-button>
        </el-radio-group>

        <!-- 映射预览 -->
        <el-card v-if="mappings.length > 0" class="mapping-preview">
          <template #header>
            <span>📋 映射预览（共 {{ mappings.length }} 条）</span>
          </template>
          <el-table :data="mappings" style="width: 100%">
            <el-table-column prop="kook_channel" label="KOOK频道" width="200"></el-table-column>
            <el-table-column label="目标" width="150">
              <template #default="{ row }">
                <el-tag :type="getPlatformType(row.platform)">
                  {{ row.platform }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="target_channel" label="目标频道"></el-table-column>
            <el-table-column label="匹配度" width="100" v-if="mappingMode === 'auto'">
              <template #default="{ row }">
                <el-tag :type="row.confidence > 0.8 ? 'success' : 'warning'">
                  {{ (row.confidence * 100).toFixed(0) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="editMapping(row)">调整</el-button>
                <el-button size="small" type="danger" @click="deleteMapping(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-empty v-else description="还没有映射规则">
          <el-button type="primary" @click="addMapping">手动添加映射</el-button>
        </el-empty>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="success" size="large" @click="completeWizard" :disabled="mappings.length === 0">
            <el-icon><Check /></el-icon>
            完成配置，开始转发！
          </el-button>
        </div>
      </div>

      <!-- 步骤5: 完成 -->
      <div v-if="currentStep === 5" class="step-complete">
        <div class="success-icon">✅</div>
        <h1>配置完成！</h1>
        <p class="subtitle">KOOK消息转发系统已准备就绪</p>

        <el-card class="summary-card">
          <h3>📊 配置摘要</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="KOOK账号">
              {{ accountEmail }}
            </el-descriptions-item>
            <el-descriptions-item label="监听服务器">
              {{ selectedServers.length }} 个
            </el-descriptions-item>
            <el-descriptions-item label="配置Bot">
              {{ configuredBots.length }} 个
            </el-descriptions-item>
            <el-descriptions-item label="频道映射">
              {{ mappings.length }} 条
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="next-steps">
          <h3>🎯 接下来您可以：</h3>
          <ol>
            <li>查看实时转发日志</li>
            <li>调整过滤规则</li>
            <li>配置更多Bot</li>
            <li>优化映射关系</li>
          </ol>
        </el-card>

        <div class="step-actions">
          <el-button type="primary" size="large" @click="goToHome">
            <el-icon><HomeFilled /></el-icon>
            进入主界面
          </el-button>
        </div>
      </div>
    </div>

    <!-- 进度保存提示 -->
    <div class="progress-indicator">
      <el-icon><Loading /></el-icon>
      配置进度自动保存中...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 步骤0: 欢迎页
const disclaimerAccepted = ref(false)

// 步骤1: 登录
const loginMethod = ref('cookie')
const cookieText = ref('')
const loginForm = ref({
  email: '',
  password: ''
})
const validating = ref(false)
const loggingIn = ref(false)
const accountConnected = ref(false)
const accountEmail = ref('')

// 步骤2: 服务器选择
const loadingServers = ref(false)
const servers = ref([])
const selectedServers = ref([])
const selectedChannels = ref({})

// 步骤3: Bot配置
const activeBotTab = ref('discord')
const discordBot = ref({ name: '', webhook_url: '' })
const telegramBot = ref({ name: '', token: '', chat_id: '' })
const feishuBot = ref({ name: '', app_id: '', app_secret: '' })
const testingBot = ref(false)
const configuredBots = ref([])

// 步骤4: 映射
const mappingMode = ref('auto')
const autoMapping = ref(false)
const mappings = ref([])

// 方法
const nextStep = () => {
  if (currentStep.value === 1) {
    // 验证登录
    if (!accountConnected.value) {
      ElMessage.warning('请先完成KOOK账号登录')
      return
    }
    // 加载服务器
    loadServers()
  }
  
  if (currentStep.value < 5) {
    currentStep.value++
    saveProgress()
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const skipWizard = () => {
  ElMessageBox.confirm(
    '跳过向导后需要手动配置所有选项，确定要跳过吗？',
    '提示',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置',
      type: 'warning'
    }
  ).then(() => {
    markWizardCompleted()
    router.push('/home')
  })
}

const handleCookieFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    cookieText.value = e.target.result
  }
  reader.readAsText(file.raw)
}

const validateCookie = async () => {
  if (!cookieText.value) {
    ElMessage.warning('请输入Cookie内容')
    return
  }
  
  validating.value = true
  try {
    const res = await api.post('/api/cookie/validate', {
      cookie: cookieText.value
    })
    
    if (res.data.valid) {
      ElMessage.success('Cookie验证成功！')
      accountConnected.value = true
      accountEmail.value = res.data.email || '未知'
      
      // 保存账号
      await api.post('/api/accounts', {
        cookie: cookieText.value
      })
    } else {
      ElMessage.error('Cookie无效：' + res.data.reason)
    }
  } catch (error) {
    ElMessage.error('验证失败：' + error.message)
  } finally {
    validating.value = false
  }
}

const loginWithPassword = async () => {
  loggingIn.value = true
  try {
    const res = await api.post('/api/auth/login', loginForm.value)
    if (res.data.success) {
      ElMessage.success('登录成功！')
      accountConnected.value = true
      accountEmail.value = loginForm.value.email
    }
  } catch (error) {
    ElMessage.error('登录失败：' + error.message)
  } finally {
    loggingIn.value = false
  }
}

const loadServers = async () => {
  loadingServers.value = true
  try {
    const res = await api.get('/api/servers')
    servers.value = res.data.servers
    
    // 为每个服务器加载频道
    for (const server of servers.value) {
      const channelsRes = await api.get(`/api/servers/${server.id}/channels`)
      server.channels = channelsRes.data.channels
    }
  } catch (error) {
    ElMessage.error('加载服务器失败：' + error.message)
  } finally {
    loadingServers.value = false
  }
}

const toggleServer = (serverId) => {
  const index = selectedServers.value.indexOf(serverId)
  if (index > -1) {
    selectedServers.value.splice(index, 1)
    delete selectedChannels.value[serverId]
  } else {
    selectedServers.value.push(serverId)
    // 默认选择所有频道
    const server = servers.value.find(s => s.id === serverId)
    selectedChannels.value[serverId] = server.channels.map(c => c.id)
  }
}

const selectAllServers = () => {
  selectedServers.value = servers.value.map(s => s.id)
  servers.value.forEach(server => {
    selectedChannels.value[server.id] = server.channels.map(c => c.id)
  })
}

const deselectAllServers = () => {
  selectedServers.value = []
  selectedChannels.value = {}
}

const testBot = async (platform) => {
  testingBot.value = true
  try {
    let config = {}
    if (platform === 'discord') {
      config = { webhook_url: discordBot.value.webhook_url }
    } else if (platform === 'telegram') {
      config = { token: telegramBot.value.token, chat_id: telegramBot.value.chat_id }
    } else if (platform === 'feishu') {
      config = { app_id: feishuBot.value.app_id, app_secret: feishuBot.value.app_secret }
    }
    
    const res = await api.post(`/api/bots/test`, {
      platform,
      config
    })
    
    if (res.data.success) {
      ElMessage.success('连接测试成功！')
      
      // 保存Bot配置
      const botData = {
        platform,
        name: platform === 'discord' ? discordBot.value.name : 
              platform === 'telegram' ? telegramBot.value.name : 
              feishuBot.value.name,
        config
      }
      
      const saveRes = await api.post('/api/bots', botData)
      configuredBots.value.push({
        id: saveRes.data.id,
        ...botData
      })
    } else {
      ElMessage.error('连接测试失败：' + res.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  } finally {
    testingBot.value = false
  }
}

const autoMap = async () => {
  autoMapping.value = true
  try {
    const res = await api.post('/api/mappings/auto-create', {
      servers: selectedServers.value,
      bots: configuredBots.value.map(b => b.id)
    })
    
    mappings.value = res.data.mappings
    ElMessage.success(`自动创建了 ${mappings.value.length} 条映射`)
  } catch (error) {
    ElMessage.error('智能映射失败：' + error.message)
  } finally {
    autoMapping.value = false
  }
}

const getPlatformType = (platform) => {
  const types = {
    'discord': 'primary',
    'telegram': 'success',
    'feishu': 'warning'
  }
  return types[platform] || ''
}

const editMapping = (mapping) => {
  // TODO: 打开编辑对话框
}

const deleteMapping = (mapping) => {
  const index = mappings.value.indexOf(mapping)
  if (index > -1) {
    mappings.value.splice(index, 1)
  }
}

const completeWizard = async () => {
  try {
    // 保存所有映射
    for (const mapping of mappings.value) {
      await api.post('/api/mappings', mapping)
    }
    
    markWizardCompleted()
    currentStep.value = 5
  } catch (error) {
    ElMessage.error('保存配置失败：' + error.message)
  }
}

const markWizardCompleted = () => {
  localStorage.setItem('wizard_completed', 'true')
  localStorage.setItem('wizard_completed_at', new Date().toISOString())
}

const saveProgress = () => {
  const progress = {
    step: currentStep.value,
    disclaimerAccepted: disclaimerAccepted.value,
    accountConnected: accountConnected.value,
    selectedServers: selectedServers.value,
    configuredBots: configuredBots.value,
    mappings: mappings.value
  }
  localStorage.setItem('wizard_progress', JSON.stringify(progress))
}

const loadProgress = () => {
  const saved = localStorage.getItem('wizard_progress')
  if (saved) {
    const progress = JSON.parse(saved)
    currentStep.value = progress.step || 0
    disclaimerAccepted.value = progress.disclaimerAccepted || false
    accountConnected.value = progress.accountConnected || false
    selectedServers.value = progress.selectedServers || []
    configuredBots.value = progress.configuredBots || []
    mappings.value = progress.mappings || []
  }
}

const goToHome = () => {
  router.push('/home')
}

const openChromeExtension = () => {
  window.open('chrome-extension://YOUR_EXTENSION_ID/popup.html')
}

const showCookieHelp = () => {
  router.push('/help/cookie-guide')
}

const showDiscordHelp = () => {
  router.push('/help/discord-guide')
}

const showTelegramHelp = () => {
  router.push('/help/telegram-guide')
}

const showFeishuHelp = () => {
  router.push('/help/feishu-guide')
}

// 生命周期
onMounted(() => {
  // 检查是否已完成向导
  if (localStorage.getItem('wizard_completed')) {
    router.push('/home')
    return
  }
  
  // 加载保存的进度
  loadProgress()
})

// 监听步骤变化，自动保存
watch(currentStep, () => {
  saveProgress()
})
</script>

<style scoped>
.wizard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.step-content {
  margin-top: 40px;
  min-height: 500px;
}

.step-welcome {
  text-align: center;
}

.welcome-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}

.time-estimate {
  color: #409EFF;
  font-size: 16px;
  margin-bottom: 30px;
}

.feature-card, .disclaimer-card {
  max-width: 600px;
  margin: 20px auto;
  text-align: left;
}

.disclaimer-content ol {
  padding-left: 20px;
}

.step-actions {
  margin-top: 40px;
  text-align: center;
}

.step-actions .el-button {
  margin: 0 10px;
}

.login-tabs {
  margin-top: 20px;
}

.servers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.server-card {
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.server-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.server-card.selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.3);
}

.server-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 10px;
  border-radius: 50%;
  overflow: hidden;
}

.server-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.server-icon-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
}

.server-name {
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
}

.selected-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  color: #67C23A;
}

.channels-list {
  text-align: left;
}

.quick-actions {
  margin-top: 20px;
  text-align: center;
}

.configured-bots {
  margin-top: 30px;
}

.mapping-mode {
  margin: 20px 0;
}

.mapping-preview {
  margin-top: 20px;
}

.step-complete {
  text-align: center;
}

.success-icon {
  font-size: 100px;
  margin-bottom: 20px;
}

.summary-card, .next-steps {
  max-width: 600px;
  margin: 20px auto;
  text-align: left;
}

.progress-indicator {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
