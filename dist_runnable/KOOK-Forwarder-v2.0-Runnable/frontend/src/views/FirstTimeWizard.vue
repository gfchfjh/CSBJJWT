<template>
  <div class="first-time-wizard">
    <!-- 顶部进度条 -->
    <div class="wizard-progress">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎" />
        <el-step title="登录KOOK" />
        <el-step title="选择频道" />
        <el-step title="完成" />
      </el-steps>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 步骤0: 欢迎页 -->
      <transition name="fade">
        <div v-if="currentStep === 0" class="wizard-step welcome-step">
          <div class="welcome-icon">🎉</div>
          <h1>欢迎使用 KOOK消息转发系统</h1>
          <p class="subtitle">只需3步，即可开始使用</p>
          
          <div class="features">
            <div class="feature-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>自动转发KOOK消息</span>
            </div>
            <div class="feature-item">
              <el-icon><Connection /></el-icon>
              <span>支持Discord/Telegram/飞书</span>
            </div>
            <div class="feature-item">
              <el-icon><MagicStick /></el-icon>
              <span>AI智能映射推荐</span>
            </div>
          </div>
          
          <div class="wizard-actions">
            <el-button type="primary" size="large" @click="nextStep">
              开始配置
            </el-button>
            <el-button size="large" @click="skipWizard">
              跳过向导，稍后配置
            </el-button>
          </div>
        </div>
      </transition>

      <!-- 步骤1: 登录KOOK -->
      <transition name="fade">
        <div v-if="currentStep === 1" class="wizard-step login-step">
          <h2>📧 登录KOOK账号</h2>
          <p class="step-desc">选择一种方式登录KOOK</p>
          
          <el-tabs v-model="loginMethod" class="login-tabs">
            <!-- Chrome扩展方式（推荐） -->
            <el-tab-pane name="extension">
              <template #label>
                <span class="tab-label">
                  <el-icon><ChromeFilled /></el-icon>
                  Chrome扩展（推荐）
                </span>
              </template>
              
              <div class="login-content">
                <el-alert 
                  type="success" 
                  :closable="false" 
                  show-icon
                  style="margin-bottom: 20px"
                >
                  <template #title>
                    <strong>最简单的方式！仅需2步</strong>
                  </template>
                </el-alert>
                
                <ol class="step-list">
                  <li>
                    <div class="step-number">1</div>
                    <div class="step-content">
                      <strong>安装Chrome扩展</strong>
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click="installExtension"
                        style="margin-left: 10px"
                      >
                        {{ extensionInstalled ? '✅ 已安装' : '📥 安装扩展' }}
                      </el-button>
                    </div>
                  </li>
                  <li>
                    <div class="step-number">2</div>
                    <div class="step-content">
                      <strong>登录KOOK并导出Cookie</strong>
                      <el-button 
                        type="primary" 
                        link 
                        @click="openKook"
                      >
                        🔗 打开KOOK
                      </el-button>
                      <p class="hint">登录后点击扩展图标，或按 <kbd>Ctrl+Shift+K</kbd></p>
                    </div>
                  </li>
                </ol>
                
                <el-alert 
                  v-if="cookieDetected" 
                  type="success" 
                  :closable="false"
                  show-icon
                  style="margin-top: 20px"
                >
                  ✅ 检测到Cookie已导入！可以进入下一步
                </el-alert>
                
                <el-alert 
                  v-else-if="waitingForCookie" 
                  type="info" 
                  :closable="false"
                  style="margin-top: 20px"
                >
                  <template #default>
                    <div style="display: flex; align-items: center; gap: 10px">
                      <el-icon class="is-loading"><Loading /></el-icon>
                      <span>等待Cookie导入...</span>
                    </div>
                  </template>
                </el-alert>
              </div>
            </el-tab-pane>

            <!-- 账号密码方式 -->
            <el-tab-pane name="password">
              <template #label>
                <span class="tab-label">
                  <el-icon><Lock /></el-icon>
                  账号密码
                </span>
              </template>
              
              <div class="login-content">
                <el-form 
                  ref="passwordFormRef"
                  :model="passwordForm"
                  :rules="passwordRules"
                  label-width="80px"
                >
                  <el-form-item label="邮箱" prop="email">
                    <el-input 
                      v-model="passwordForm.email"
                      placeholder="your@email.com"
                      clearable
                    >
                      <template #prefix>
                        <el-icon><Message /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item label="密码" prop="password">
                    <el-input 
                      v-model="passwordForm.password"
                      type="password"
                      placeholder="请输入密码"
                      show-password
                      clearable
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="loginWithPassword"
                      :loading="loggingIn"
                      style="width: 100%"
                    >
                      🔐 登录
                    </el-button>
                  </el-form-item>
                </el-form>
                
                <el-alert 
                  v-if="loginError"
                  type="error"
                  :closable="false"
                  show-icon
                >
                  {{ loginError }}
                </el-alert>
              </div>
            </el-tab-pane>
          </el-tabs>
          
          <div class="wizard-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button 
              type="primary" 
              @click="nextStep"
              :disabled="!cookieDetected"
            >
              下一步
            </el-button>
          </div>
        </div>
      </transition>

      <!-- 步骤2: 选择监听频道 -->
      <transition name="fade">
        <div v-if="currentStep === 2" class="wizard-step channels-step">
          <h2>📡 选择要监听的频道</h2>
          <p class="step-desc">选择您要转发消息的KOOK频道</p>
          
          <div v-if="loadingChannels" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p>正在获取服务器和频道列表...</p>
          </div>
          
          <div v-else-if="servers.length > 0" class="channels-container">
            <el-tree
              ref="channelTree"
              :data="serverTree"
              :props="treeProps"
              show-checkbox
              node-key="id"
              default-expand-all
              @check="handleChannelCheck"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon v-if="data.type === 'server'">
                    <Folder />
                  </el-icon>
                  <el-icon v-else>
                    <ChatDotRound />
                  </el-icon>
                  <span>{{ node.label }}</span>
                </span>
              </template>
            </el-tree>
            
            <div v-if="selectedChannels.length > 0" class="selection-summary">
              <el-tag type="success">
                已选择 {{ selectedChannels.length }} 个频道
              </el-tag>
            </div>
          </div>
          
          <el-alert 
            v-else
            type="warning"
            :closable="false"
            show-icon
          >
            未找到服务器，请确保已成功登录KOOK
          </el-alert>
          
          <div class="wizard-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button 
              type="primary" 
              @click="nextStep"
              :disabled="selectedChannels.length === 0"
            >
              下一步
            </el-button>
          </div>
        </div>
      </transition>

      <!-- 步骤3: 完成 -->
      <transition name="fade">
        <div v-if="currentStep === 3" class="wizard-step complete-step">
          <div class="success-icon">✅</div>
          <h1>配置完成！</h1>
          <p class="subtitle">基础配置已完成，您现在可以：</p>
          
          <div class="next-steps">
            <div class="next-step-item">
              <div class="step-icon">🤖</div>
              <div class="step-content">
                <h3>配置转发Bot</h3>
                <p>设置Discord、Telegram或飞书Bot</p>
              </div>
            </div>
            <div class="next-step-item">
              <div class="step-icon">🔀</div>
              <div class="step-content">
                <h3>设置频道映射</h3>
                <p>使用AI智能推荐或手动配置</p>
              </div>
            </div>
            <div class="next-step-item">
              <div class="step-icon">🚀</div>
              <div class="step-content">
                <h3>启动服务</h3>
                <p>开始自动转发消息</p>
              </div>
            </div>
          </div>
          
          <div class="wizard-actions">
            <el-button type="primary" size="large" @click="finishWizard">
              进入主界面
            </el-button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, 
  Connection, 
  MagicStick, 
  ChromeFilled, 
  Lock, 
  Message,
  Loading,
  Folder
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 登录方式
const loginMethod = ref('extension')

// Chrome扩展状态
const extensionInstalled = ref(false)
const cookieDetected = ref(false)
const waitingForCookie = ref(false)

// 账号密码登录
const passwordFormRef = ref(null)
const passwordForm = ref({
  email: '',
  password: ''
})

const passwordRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const loggingIn = ref(false)
const loginError = ref('')

// 服务器和频道
const loadingChannels = ref(false)
const servers = ref([])
const selectedChannels = ref([])

// 树形结构配置
const treeProps = {
  label: 'name',
  children: 'channels'
}

// 服务器树数据
const serverTree = computed(() => {
  return servers.value.map(server => ({
    id: `server-${server.id}`,
    name: server.name,
    type: 'server',
    channels: server.channels.map(channel => ({
      id: `channel-${channel.id}`,
      name: channel.name,
      type: 'channel',
      serverId: server.id,
      channelId: channel.id
    }))
  }))
})

// Cookie导入轮询定时器
let cookiePollingInterval = null

// 方法：下一步
const nextStep = () => {
  if (currentStep.value === 1 && !cookieDetected.value) {
    ElMessage.warning('请先完成登录')
    return
  }
  
  if (currentStep.value === 2) {
    // 保存选中的频道
    saveSelectedChannels()
  }
  
  if (currentStep.value < 3) {
    currentStep.value++
    
    // 进入频道选择步骤时，自动获取频道列表
    if (currentStep.value === 2) {
      fetchChannels()
    }
  }
}

// 方法：上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 方法：跳过向导
const skipWizard = () => {
  if (confirm('确定要跳过配置向导吗？您可以稍后在设置中完成配置。')) {
    // 标记向导已完成（即使跳过）
    localStorage.setItem('wizardCompleted', 'true')
    router.push('/')
  }
}

// 方法：完成向导
const finishWizard = () => {
  // 标记向导已完成
  localStorage.setItem('wizardCompleted', 'true')
  
  ElMessage.success('配置完成！欢迎使用')
  router.push('/')
}

// 方法：安装Chrome扩展
const installExtension = () => {
  // 打开扩展安装页面
  window.open('/chrome-extension/manifest.json', '_blank')
  extensionInstalled.value = true
  
  // 开始轮询Cookie
  startCookiePolling()
}

// 方法：打开KOOK
const openKook = () => {
  window.open('https://www.kookapp.cn', '_blank')
}

// 方法：账号密码登录
const loginWithPassword = async () => {
  const valid = await passwordFormRef.value.validate()
  if (!valid) return
  
  try {
    loggingIn.value = true
    loginError.value = ''
    
    const response = await axios.post('/api/accounts/login', {
      email: passwordForm.value.email,
      password: passwordForm.value.password
    })
    
    if (response.data.success) {
      cookieDetected.value = true
      ElMessage.success('登录成功！')
    } else {
      loginError.value = response.data.message || '登录失败'
    }
  } catch (error) {
    loginError.value = error.response?.data?.detail || '登录异常，请稍后重试'
  } finally {
    loggingIn.value = false
  }
}

// 方法：开始Cookie轮询
const startCookiePolling = () => {
  if (cookiePollingInterval) return
  
  waitingForCookie.value = true
  
  cookiePollingInterval = setInterval(async () => {
    try {
      const response = await axios.get('/api/cookie/check-import')
      if (response.data.imported) {
        cookieDetected.value = true
        waitingForCookie.value = false
        clearInterval(cookiePollingInterval)
        cookiePollingInterval = null
        
        ElMessage.success('Cookie已自动导入！')
      }
    } catch (error) {
      console.error('检查Cookie失败:', error)
    }
  }, 2000) // 每2秒检查一次
}

// 方法：获取频道列表
const fetchChannels = async () => {
  try {
    loadingChannels.value = true
    
    // 获取最新的账号ID
    const accountsResponse = await axios.get('/api/accounts')
    const accounts = accountsResponse.data.accounts || []
    
    if (accounts.length === 0) {
      throw new Error('未找到账号')
    }
    
    const accountId = accounts[0].id
    
    // 自动发现服务器和频道
    const response = await axios.post('/api/servers/discover', {
      account_id: accountId,
      force_refresh: false
    })
    
    servers.value = response.data.servers || []
  } catch (error) {
    console.error('获取频道失败:', error)
    ElMessage.error('获取频道列表失败，请稍后重试')
  } finally {
    loadingChannels.value = false
  }
}

// 方法：处理频道选择
const handleChannelCheck = (data, checked) => {
  const checkedNodes = checked.checkedNodes.filter(node => node.type === 'channel')
  selectedChannels.value = checkedNodes.map(node => ({
    serverId: node.serverId,
    channelId: node.channelId,
    name: node.name
  }))
}

// 方法：保存选中的频道
const saveSelectedChannels = () => {
  // 保存到localStorage（后续会同步到数据库）
  localStorage.setItem('selectedChannels', JSON.stringify(selectedChannels.value))
}

// 生命周期：组件挂载
onMounted(() => {
  // 检查是否已完成向导
  const wizardCompleted = localStorage.getItem('wizardCompleted')
  if (wizardCompleted === 'true') {
    router.push('/')
    return
  }
  
  // 检查Chrome扩展是否已安装
  checkExtensionInstalled()
})

// 生命周期：组件卸载
onUnmounted(() => {
  if (cookiePollingInterval) {
    clearInterval(cookiePollingInterval)
  }
})

// 方法：检查扩展是否已安装
const checkExtensionInstalled = () => {
  // 这里可以通过尝试与扩展通信来检查
  // 暂时简化处理
  extensionInstalled.value = false
}
</script>

<style scoped>
.first-time-wizard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.wizard-progress {
  max-width: 800px;
  margin: 0 auto 40px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.wizard-content {
  max-width: 900px;
  margin: 0 auto;
}

.wizard-step {
  background: white;
  border-radius: 16px;
  padding: 60px 80px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  min-height: 500px;
}

/* 欢迎页 */
.welcome-step {
  text-align: center;
}

.welcome-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.welcome-step h1 {
  font-size: 36px;
  color: #333;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 50px;
}

.features {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 60px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #555;
}

.feature-item .el-icon {
  font-size: 48px;
  color: #667eea;
}

/* 登录步骤 */
.login-step h2,
.channels-step h2,
.complete-step h1 {
  font-size: 28px;
  margin-bottom: 12px;
  color: #333;
}

.step-desc {
  color: #666;
  font-size: 16px;
  margin-bottom: 30px;
}

.login-tabs {
  margin-bottom: 40px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-content {
  padding: 20px 0;
}

.step-list {
  list-style: none;
  padding: 0;
}

.step-list li {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.step-number {
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content strong {
  display: block;
  margin-bottom: 8px;
  color: #333;
}

.hint {
  margin-top: 8px;
  font-size: 13px;
  color: #999;
}

kbd {
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: 2px 6px;
  font-family: monospace;
  font-size: 12px;
}

/* 频道选择步骤 */
.loading-container {
  text-align: center;
  padding: 80px 20px;
}

.loading-container .el-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
}

.channels-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selection-summary {
  margin-top: 20px;
  text-align: center;
}

/* 完成步骤 */
.complete-step {
  text-align: center;
}

.success-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.next-steps {
  max-width: 600px;
  margin: 40px auto 60px;
}

.next-step-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 24px;
  background: #f9f9f9;
  border-radius: 12px;
  margin-bottom: 16px;
  text-align: left;
}

.step-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.next-step-item h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #333;
}

.next-step-item p {
  color: #666;
  font-size: 14px;
}

/* 底部按钮 */
.wizard-actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
