<template>
  <div class="wizard-unified-container">
    <!-- 进度指示器 -->
    <div class="wizard-progress">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${(currentStep / 3) * 100}%` }"
        ></div>
      </div>
      <div class="progress-steps">
        <div 
          v-for="step in 3" 
          :key="step"
          class="progress-step"
          :class="{ 
            active: currentStep === step, 
            completed: currentStep > step 
          }"
        >
          <div class="step-circle">
            <el-icon v-if="currentStep > step"><Check /></el-icon>
            <span v-else>{{ step }}</span>
          </div>
          <div class="step-label">{{ stepLabels[step - 1] }}</div>
        </div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 第1步：欢迎页 -->
      <div v-show="currentStep === 1" class="wizard-step step-welcome">
        <div class="welcome-header">
          <el-icon class="welcome-icon" :size="80"><Present /></el-icon>
          <h1>欢迎使用 KOOK 消息转发系统</h1>
          <p class="welcome-subtitle">零代码基础 · 一键安装 · 3分钟上手</p>
        </div>

        <div class="welcome-features">
          <div class="feature-card">
            <el-icon :size="40" color="#409EFF"><Connection /></el-icon>
            <h3>自动监听</h3>
            <p>实时监听 KOOK 频道消息</p>
          </div>
          <div class="feature-card">
            <el-icon :size="40" color="#67C23A"><Share /></el-icon>
            <h3>多平台转发</h3>
            <p>支持 Discord / Telegram / 飞书</p>
          </div>
          <div class="feature-card">
            <el-icon :size="40" color="#E6A23C"><Setting /></el-icon>
            <h3>智能配置</h3>
            <p>可视化映射 · 一键测试</p>
          </div>
        </div>

        <div class="welcome-info">
          <el-alert 
            type="info" 
            :closable="false"
            show-icon
          >
            <template #title>
              <strong>本向导将帮助您完成基础配置</strong>
            </template>
            <div class="info-content">
              <p>📋 共3个步骤 · 预计耗时 3-5 分钟</p>
              <p>💡 可随时退出，下次启动会继续</p>
            </div>
          </el-alert>
        </div>

        <div class="wizard-actions">
          <el-button size="large" @click="skipWizard">跳过向导</el-button>
          <el-button type="primary" size="large" @click="nextStep">
            开始配置 <el-icon class="ml-1"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第2步：登录KOOK -->
      <div v-show="currentStep === 2" class="wizard-step step-login">
        <div class="step-header">
          <h2>登录 KOOK 账号</h2>
          <p>选择一种方式登录您的 KOOK 账号</p>
        </div>

        <el-tabs v-model="loginMethod" class="login-tabs">
          <!-- Cookie导入（推荐） -->
          <el-tab-pane label="Cookie 一键导入（推荐）" name="cookie">
            <div class="login-method-content">
              <el-alert 
                type="success" 
                :closable="false"
                show-icon
                class="mb-4"
              >
                <template #title>
                  <strong>✨ 最简单的方式！</strong>
                </template>
                <p>使用 Chrome 扩展，点击一下即可完成导入</p>
              </el-alert>

              <el-steps :active="cookieStep" align-center>
                <el-step title="安装扩展" description="下载并安装 Chrome 扩展"></el-step>
                <el-step title="登录 KOOK" description="在网页版登录账号"></el-step>
                <el-step title="一键导入" description="点击扩展图标完成"></el-step>
              </el-steps>

              <div class="cookie-actions mt-4">
                <el-button 
                  type="primary" 
                  :icon="Download"
                  @click="downloadExtension"
                  v-if="!extensionInstalled"
                >
                  下载 Chrome 扩展
                </el-button>

                <el-button 
                  type="success" 
                  :icon="Link"
                  @click="openKookWeb"
                >
                  打开 KOOK 网页版
                </el-button>

                <div class="cookie-status mt-4" v-if="cookieImportStatus">
                  <el-result 
                    :icon="cookieImportStatus.icon"
                    :title="cookieImportStatus.title"
                    :sub-title="cookieImportStatus.message"
                  >
                    <template #extra>
                      <el-button 
                        type="primary" 
                        @click="verifyCookieAndNext"
                        v-if="cookieImportStatus.success"
                      >
                        继续下一步
                      </el-button>
                    </template>
                  </el-result>
                </div>

                <div class="cookie-waiting mt-4" v-else-if="waitingForCookie">
                  <el-icon class="is-loading" :size="40"><Loading /></el-icon>
                  <p class="mt-2">等待 Cookie 导入中...</p>
                  <p class="text-muted">请在 KOOK 网页版点击扩展图标</p>
                </div>
              </div>

              <!-- 手动导入Cookie -->
              <el-collapse class="mt-4">
                <el-collapse-item title="🔧 高级：手动导入 Cookie" name="manual">
                  <el-input
                    v-model="cookieInput"
                    type="textarea"
                    :rows="6"
                    placeholder="粘贴 Cookie JSON 数据..."
                  ></el-input>
                  <el-button 
                    type="primary" 
                    class="mt-2"
                    @click="importCookieManually"
                    :loading="importingCookie"
                  >
                    导入
                  </el-button>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-tab-pane>

          <!-- 账号密码登录 -->
          <el-tab-pane label="账号密码登录" name="password">
            <div class="login-method-content">
              <el-alert 
                type="warning" 
                :closable="false"
                class="mb-4"
              >
                <p>首次登录可能需要输入验证码</p>
              </el-alert>

              <el-form 
                :model="loginForm" 
                :rules="loginRules"
                ref="loginFormRef"
                label-width="80px"
                size="large"
              >
                <el-form-item label="邮箱" prop="email">
                  <el-input 
                    v-model="loginForm.email"
                    placeholder="请输入 KOOK 邮箱"
                    :prefix-icon="Message"
                  ></el-input>
                </el-form-item>

                <el-form-item label="密码" prop="password">
                  <el-input 
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    :prefix-icon="Lock"
                    show-password
                  ></el-input>
                </el-form-item>

                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="loginWithPassword"
                    :loading="loggingIn"
                    style="width: 100%"
                  >
                    登录
                  </el-button>
                </el-form-item>
              </el-form>

              <div v-if="loginError" class="login-error mt-4">
                <el-alert type="error" :closable="false">
                  {{ loginError }}
                </el-alert>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="wizard-actions">
          <el-button size="large" @click="prevStep">
            <el-icon><ArrowLeft /></el-icon> 上一步
          </el-button>
          <el-button 
            type="primary" 
            size="large" 
            @click="nextStep"
            :disabled="!accountLoggedIn"
          >
            下一步 <el-icon class="ml-1"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第3步：选择频道 -->
      <div v-show="currentStep === 3" class="wizard-step step-channels">
        <div class="step-header">
          <h2>选择要监听的频道</h2>
          <p>勾选您想要监听的 KOOK 服务器和频道</p>
        </div>

        <div class="channels-toolbar">
          <el-input
            v-model="channelSearchKeyword"
            placeholder="搜索服务器或频道..."
            :prefix-icon="Search"
            clearable
            class="search-input"
          ></el-input>

          <div class="toolbar-actions">
            <el-button @click="expandAll">展开所有</el-button>
            <el-button @click="collapseAll">折叠所有</el-button>
            <el-button @click="selectAllChannels">全选</el-button>
            <el-button @click="deselectAllChannels">全不选</el-button>
          </div>
        </div>

        <div class="channels-container" v-loading="loadingChannels">
          <el-empty 
            v-if="!loadingChannels && filteredServers.length === 0"
            description="未找到服务器，请检查账号登录状态"
          ></el-empty>

          <el-tree
            v-else
            ref="channelTreeRef"
            :data="filteredServers"
            node-key="id"
            show-checkbox
            :props="treeProps"
            :default-expanded-keys="expandedKeys"
            @check="handleChannelCheck"
            class="channel-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node-content">
                <el-icon v-if="data.type === 'server'" class="mr-1"><OfficeBuilding /></el-icon>
                <el-icon v-else-if="data.channelType === 1" class="mr-1"><ChatDotRound /></el-icon>
                <el-icon v-else-if="data.channelType === 2" class="mr-1"><Microphone /></el-icon>
                <span>{{ node.label }}</span>
                <el-tag 
                  v-if="data.type === 'server'" 
                  size="small" 
                  class="ml-2"
                  type="info"
                >
                  {{ data.children.length }} 个频道
                </el-tag>
              </div>
            </template>
          </el-tree>
        </div>

        <div class="selected-summary">
          <el-alert type="info" :closable="false">
            已选择 <strong>{{ selectedChannelCount }}</strong> 个频道
          </el-alert>
        </div>

        <div class="wizard-actions">
          <el-button size="large" @click="prevStep">
            <el-icon><ArrowLeft /></el-icon> 上一步
          </el-button>
          <el-button 
            type="primary" 
            size="large" 
            @click="completeWizard"
            :loading="completing"
            :disabled="selectedChannelCount === 0"
          >
            完成配置 <el-icon class="ml-1"><Check /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 底部帮助链接 -->
    <div class="wizard-footer">
      <el-link :icon="QuestionFilled" @click="showHelp">需要帮助？</el-link>
      <el-divider direction="vertical" />
      <el-link :icon="VideoPlay" @click="watchTutorial">观看视频教程</el-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Present, Connection, Share, Setting, Check, ArrowRight, ArrowLeft,
  Download, Link, Loading, Message, Lock, Search, OfficeBuilding,
  ChatDotRound, Microphone, QuestionFilled, VideoPlay
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// ========== 状态管理 ==========
const currentStep = ref(1)
const stepLabels = ['欢迎', '登录 KOOK', '选择频道']

// 登录相关
const loginMethod = ref('cookie')
const cookieStep = ref(0)
const extensionInstalled = ref(false)
const waitingForCookie = ref(false)
const cookieImportStatus = ref(null)
const cookieInput = ref('')
const importingCookie = ref(false)
const accountLoggedIn = ref(false)
const currentAccountId = ref(null)

// 账号密码登录
const loginForm = ref({
  email: '',
  password: ''
})
const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}
const loginFormRef = ref(null)
const loggingIn = ref(false)
const loginError = ref('')

// 频道选择相关
const servers = ref([])
const loadingChannels = ref(false)
const channelSearchKeyword = ref('')
const expandedKeys = ref([])
const channelTreeRef = ref(null)
const selectedChannels = ref([])
const completing = ref(false)

// WebSocket连接（监听Cookie导入）
let ws = null

// ========== 计算属性 ==========
const filteredServers = computed(() => {
  if (!channelSearchKeyword.value) {
    return servers.value
  }
  
  const keyword = channelSearchKeyword.value.toLowerCase()
  return servers.value
    .map(server => {
      const matchedChannels = server.children.filter(channel =>
        channel.label.toLowerCase().includes(keyword)
      )
      
      if (server.label.toLowerCase().includes(keyword) || matchedChannels.length > 0) {
        return {
          ...server,
          children: matchedChannels.length > 0 ? matchedChannels : server.children
        }
      }
      return null
    })
    .filter(Boolean)
})

const selectedChannelCount = computed(() => {
  if (!channelTreeRef.value) return 0
  const checkedNodes = channelTreeRef.value.getCheckedNodes()
  return checkedNodes.filter(node => node.type === 'channel').length
})

const treeProps = {
  children: 'children',
  label: 'label',
  disabled: 'disabled'
}

// ========== 生命周期 ==========
onMounted(() => {
  checkWizardProgress()
  initWebSocket()
  checkExtensionInstalled()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})

// ========== 方法 ==========
async function checkWizardProgress() {
  try {
    const response = await axios.get('http://localhost:9527/api/wizard/progress')
    if (response.data.completed) {
      // 向导已完成，询问是否重新配置
      const result = await ElMessageBox.confirm(
        '检测到您已完成过配置向导，是否要重新配置？',
        '提示',
        {
          confirmButtonText: '重新配置',
          cancelButtonText: '返回主页',
          type: 'info'
        }
      ).catch(() => false)
      
      if (!result) {
        router.push('/')
      }
    } else if (response.data.step) {
      currentStep.value = response.data.step
    }
  } catch (error) {
    console.error('Failed to check wizard progress:', error)
  }
}

function initWebSocket() {
  ws = new WebSocket('ws://localhost:9527/ws/cookie-import')
  
  ws.onopen = () => {
    console.log('WebSocket connected')
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleCookieImport(data)
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket closed')
    // 尝试重连
    setTimeout(() => {
      if (currentStep.value === 2 && !accountLoggedIn.value) {
        initWebSocket()
      }
    }, 3000)
  }
}

function checkExtensionInstalled() {
  // 检查扩展是否已安装
  // 实际实现需要通过特定的检测机制
  extensionInstalled.value = false
}

function handleCookieImport(data) {
  if (data.type === 'cookie_imported') {
    waitingForCookie.value = false
    cookieStep.value = 3
    
    if (data.success) {
      cookieImportStatus.value = {
        icon: 'success',
        title: '✅ Cookie 导入成功！',
        message: `已成功导入账号：${data.account?.email || '未知'}`,
        success: true
      }
      accountLoggedIn.value = true
      currentAccountId.value = data.account?.id
    } else {
      cookieImportStatus.value = {
        icon: 'error',
        title: '❌ Cookie 导入失败',
        message: data.message || '请检查 Cookie 是否有效',
        success: false
      }
    }
  }
}

function downloadExtension() {
  window.open('/chrome-extension.zip', '_blank')
  cookieStep.value = 1
  ElMessage.success('扩展下载已开始，请按照说明安装')
}

function openKookWeb() {
  window.open('https://www.kookapp.cn', '_blank')
  cookieStep.value = 2
  waitingForCookie.value = true
  ElMessage.info('请在 KOOK 网页版登录后，点击扩展图标导入 Cookie')
}

async function importCookieManually() {
  if (!cookieInput.value.trim()) {
    ElMessage.warning('请粘贴 Cookie 数据')
    return
  }
  
  importingCookie.value = true
  try {
    const response = await axios.post('http://localhost:9527/api/cookie/import', {
      cookies: JSON.parse(cookieInput.value),
      source: 'manual'
    })
    
    if (response.data.success) {
      ElMessage.success('Cookie 导入成功！')
      accountLoggedIn.value = true
      currentAccountId.value = response.data.account_id
      cookieImportStatus.value = {
        icon: 'success',
        title: '✅ Cookie 导入成功！',
        message: '您的账号已成功登录',
        success: true
      }
    } else {
      ElMessage.error(response.data.message || 'Cookie 导入失败')
    }
  } catch (error) {
    ElMessage.error('Cookie 导入失败：' + (error.response?.data?.message || error.message))
  } finally {
    importingCookie.value = false
  }
}

async function loginWithPassword() {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loggingIn.value = true
    loginError.value = ''
    
    try {
      const response = await axios.post('http://localhost:9527/api/accounts/login', {
        email: loginForm.value.email,
        password: loginForm.value.password
      })
      
      if (response.data.success) {
        ElMessage.success('登录成功！')
        accountLoggedIn.value = true
        currentAccountId.value = response.data.account_id
      } else {
        loginError.value = response.data.message || '登录失败'
      }
    } catch (error) {
      loginError.value = error.response?.data?.message || '登录失败，请检查网络连接'
    } finally {
      loggingIn.value = false
    }
  })
}

async function verifyCookieAndNext() {
  nextStep()
}

async function loadServersAndChannels() {
  if (!currentAccountId.value) {
    ElMessage.error('请先登录账号')
    return
  }
  
  loadingChannels.value = true
  try {
    const response = await axios.get(`http://localhost:9527/api/servers/discover/${currentAccountId.value}`)
    
    if (response.data.success) {
      // 转换为树形结构
      servers.value = response.data.servers.map(server => ({
        id: `server-${server.id}`,
        label: server.name,
        type: 'server',
        serverId: server.id,
        children: server.channels.map(channel => ({
          id: `channel-${channel.id}`,
          label: `# ${channel.name}`,
          type: 'channel',
          serverId: server.id,
          channelId: channel.id,
          channelType: channel.type
        }))
      }))
      
      // 默认展开第一个服务器
      if (servers.value.length > 0) {
        expandedKeys.value = [servers.value[0].id]
      }
    } else {
      ElMessage.error('获取服务器列表失败')
    }
  } catch (error) {
    ElMessage.error('获取服务器列表失败：' + (error.response?.data?.message || error.message))
  } finally {
    loadingChannels.value = false
  }
}

function expandAll() {
  expandedKeys.value = servers.value.map(s => s.id)
}

function collapseAll() {
  expandedKeys.value = []
}

function selectAllChannels() {
  if (!channelTreeRef.value) return
  
  const allChannelNodes = []
  servers.value.forEach(server => {
    server.children.forEach(channel => {
      allChannelNodes.push(channel)
    })
  })
  
  channelTreeRef.value.setCheckedNodes(allChannelNodes)
}

function deselectAllChannels() {
  if (!channelTreeRef.value) return
  channelTreeRef.value.setCheckedKeys([])
}

function handleChannelCheck() {
  // 获取选中的频道
  if (!channelTreeRef.value) return
  const checkedNodes = channelTreeRef.value.getCheckedNodes()
  selectedChannels.value = checkedNodes.filter(node => node.type === 'channel')
}

async function completeWizard() {
  if (selectedChannels.value.length === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }
  
  completing.value = true
  
  try {
    // 保存选择的频道
    await axios.post('http://localhost:9527/api/wizard/complete', {
      account_id: currentAccountId.value,
      channels: selectedChannels.value.map(ch => ({
        server_id: ch.serverId,
        channel_id: ch.channelId,
        channel_name: ch.label
      }))
    })
    
    ElMessage.success('配置完成！')
    
    // 保存向导完成标记
    localStorage.setItem('wizard_completed', 'true')
    
    // 跳转到主页
    setTimeout(() => {
      router.push('/')
    }, 1000)
  } catch (error) {
    ElMessage.error('保存配置失败：' + (error.response?.data?.message || error.message))
  } finally {
    completing.value = false
  }
}

function nextStep() {
  if (currentStep.value < 3) {
    currentStep.value++
    
    // 进入第3步时加载频道
    if (currentStep.value === 3) {
      loadServersAndChannels()
    }
    
    // 保存进度
    saveProgress()
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
    saveProgress()
  }
}

async function saveProgress() {
  try {
    await axios.post('http://localhost:9527/api/wizard/progress', {
      step: currentStep.value
    })
  } catch (error) {
    console.error('Failed to save progress:', error)
  }
}

async function skipWizard() {
  const result = await ElMessageBox.confirm(
    '跳过向导后，您需要手动配置所有设置。确定要跳过吗？',
    '跳过配置向导',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (result) {
    localStorage.setItem('wizard_completed', 'true')
    router.push('/')
  }
}

function showHelp() {
  router.push('/help')
}

function watchTutorial() {
  window.open('https://example.com/tutorial', '_blank')
}
</script>

<style scoped>
.wizard-unified-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.wizard-progress {
  max-width: 800px;
  margin: 0 auto 40px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  transition: width 0.3s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
}

.progress-step {
  flex: 1;
  text-align: center;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #999;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.progress-step.active .step-circle {
  background: #409EFF;
  color: white;
  transform: scale(1.1);
}

.progress-step.completed .step-circle {
  background: #67C23A;
  color: white;
}

.step-label {
  font-size: 14px;
  color: #666;
}

.progress-step.active .step-label {
  color: #409EFF;
  font-weight: bold;
}

.wizard-content {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

/* 第1步：欢迎页 */
.step-welcome {
  text-align: center;
}

.welcome-header {
  margin-bottom: 40px;
}

.welcome-icon {
  color: #409EFF;
  margin-bottom: 20px;
}

.welcome-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 18px;
  color: #909399;
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.feature-card {
  padding: 24px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.feature-card h3 {
  margin: 16px 0 8px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
}

.welcome-info {
  margin-bottom: 40px;
}

.info-content p {
  margin: 8px 0;
  font-size: 14px;
}

/* 第2步：登录 */
.step-header {
  margin-bottom: 30px;
  text-align: center;
}

.step-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.step-header p {
  color: #909399;
  font-size: 14px;
}

.login-tabs {
  margin-bottom: 30px;
}

.login-method-content {
  padding: 20px;
}

.cookie-actions {
  text-align: center;
}

.cookie-status, .cookie-waiting {
  text-align: center;
  padding: 20px;
}

.text-muted {
  color: #909399;
  font-size: 14px;
}

.login-error {
  margin-top: 16px;
}

/* 第3步：选择频道 */
.channels-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.channels-container {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.channel-tree {
  background: transparent;
}

.tree-node-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.selected-summary {
  margin-bottom: 20px;
}

/* 底部操作 */
.wizard-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.wizard-footer {
  max-width: 900px;
  margin: 20px auto 0;
  text-align: center;
  color: white;
}

.wizard-footer .el-link {
  color: white;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-features {
    grid-template-columns: 1fr;
  }
  
  .channels-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-actions {
    width: 100%;
    justify-content: space-between;
  }
}

/* 工具类 */
.ml-1 {
  margin-left: 4px;
}

.ml-2 {
  margin-left: 8px;
}

.mr-1 {
  margin-right: 4px;
}

.mt-2 {
  margin-top: 8px;
}

.mt-4 {
  margin-top: 16px;
}

.mb-4 {
  margin-bottom: 16px;
}
</style>
