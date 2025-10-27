<template>
  <div class="wizard-quick-container">
    <el-card class="wizard-card">
      <!-- ✅ P0-2优化: 极简3步配置向导 -->
      <div class="wizard-header">
        <h1>🎉 欢迎使用KOOK消息转发系统</h1>
        <p class="subtitle">仅需3步，5分钟完成配置</p>
      </div>

      <!-- 进度指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps-indicator">
        <el-step title="欢迎" description="开始配置">
          <template #icon><el-icon><House /></el-icon></template>
        </el-step>
        <el-step title="登录KOOK" description="添加账号">
          <template #icon><el-icon><User /></el-icon></template>
        </el-step>
        <el-step title="选择服务器" description="完成配置">
          <template #icon><el-icon><Check /></el-icon></template>
        </el-step>
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤0: 欢迎页 + 免责声明 -->
        <div v-if="currentStep === 0" class="step-welcome">
          <div class="welcome-banner">
            <el-icon :size="80" color="#409EFF"><SuccessFilled /></el-icon>
            <h2>让我们开始吧！</h2>
            <p>本向导将帮助您快速配置KOOK消息转发系统</p>
          </div>

          <!-- 免责声明（折叠面板，默认展开） -->
          <el-collapse v-model="activeDisclaimer" class="disclaimer-collapse">
            <el-collapse-item name="1">
              <template #title>
                <div class="disclaimer-title">
                  <el-icon color="#E6A23C"><Warning /></el-icon>
                  <span>⚠️ 请阅读免责声明（重要）</span>
                </div>
              </template>
              
              <div class="disclaimer-content">
                <el-scrollbar height="300px" ref="disclaimerScroll" @scroll="handleDisclaimerScroll">
                  <div class="disclaimer-text">
                    <h3>1. 软件性质声明</h3>
                    <p>本软件是一个开源的消息转发工具，仅供学习和研究使用。使用本软件转发KOOK平台的消息可能违反KOOK服务条款。</p>
                    
                    <h3>2. 使用风险提示</h3>
                    <p><strong style="color: #F56C6C;">⚠️ 警告：</strong></p>
                    <ul>
                      <li>使用本软件可能导致您的KOOK账号被封禁</li>
                      <li>使用本软件可能违反相关法律法规</li>
                      <li>转发的消息内容可能涉及版权问题</li>
                    </ul>

                    <h3>3. 授权限制</h3>
                    <p>您承诺：</p>
                    <ul>
                      <li>仅在已获授权的场景下使用本软件</li>
                      <li>不将本软件用于任何商业用途</li>
                      <li>不利用本软件进行任何非法活动</li>
                    </ul>

                    <h3>4. 免责条款</h3>
                    <p>开发者声明：</p>
                    <ul>
                      <li>本软件按"现状"提供，不提供任何明示或暗示的保证</li>
                      <li>开发者不对使用本软件造成的任何直接或间接损失负责</li>
                      <li>使用本软件产生的一切法律责任由使用者自行承担</li>
                    </ul>

                    <h3>5. 数据安全</h3>
                    <p>本软件会处理您的KOOK账号信息和消息内容，这些数据仅存储在您的本地设备上，不会上传到任何服务器。</p>

                    <h3>6. 隐私保护</h3>
                    <p>我们尊重您的隐私，不会收集、存储或分享您的个人信息。所有配置数据均加密存储在本地。</p>

                    <h3>7. 服务变更</h3>
                    <p>我们保留随时修改或终止本软件服务的权利，恕不另行通知。</p>

                    <h3>8. 最终解释权</h3>
                    <p>本声明的最终解释权归开发者所有。继续使用即表示您已阅读、理解并同意本声明的所有条款。</p>
                  </div>
                </el-scrollbar>

                <!-- 阅读进度条 -->
                <el-progress 
                  :percentage="readProgress" 
                  :color="progressColor"
                  :show-text="true"
                  :format="formatProgress"
                  class="read-progress"
                />
              </div>

              <!-- 同意确认 -->
              <div class="disclaimer-agreement">
                <el-checkbox 
                  v-model="agreedToDisclaimer" 
                  :disabled="!hasReadFully"
                  size="large"
                >
                  <span :class="{ 'disabled-text': !hasReadFully }">
                    我已仔细阅读并完全理解上述声明，自愿承担所有风险
                  </span>
                </el-checkbox>
                
                <el-alert 
                  v-if="!hasReadFully" 
                  type="warning" 
                  :closable="false"
                  show-icon
                  class="read-tip"
                >
                  请滚动到底部阅读完整声明后，才能勾选同意
                </el-alert>
              </div>
            </el-collapse-item>
          </el-collapse>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button @click="handleReject" size="large">
              拒绝并退出
            </el-button>
            <el-button 
              type="primary" 
              @click="handleAgree" 
              size="large"
              :disabled="!agreedToDisclaimer"
            >
              同意并继续
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤1: KOOK账号登录 -->
        <div v-else-if="currentStep === 1" class="step-login">
          <div class="step-header">
            <h2>📧 登录KOOK账号</h2>
            <p>请选择一种方式登录您的KOOK账号</p>
          </div>

          <!-- 登录方式选择 -->
          <el-radio-group v-model="loginMethod" size="large" class="login-method-group">
            <el-radio-button value="cookie">
              <el-icon><Document /></el-icon>
              Cookie导入（推荐）
            </el-radio-button>
            <el-radio-button value="password">
              <el-icon><Lock /></el-icon>
              账号密码登录
            </el-radio-button>
          </el-radio-group>

          <!-- Cookie导入方式 -->
          <div v-if="loginMethod === 'cookie'" class="login-cookie">
            <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px;">
              <template #title>
                💡 为什么推荐Cookie导入？
              </template>
              <ul style="margin: 10px 0 0 20px; line-height: 1.8;">
                <li>更安全：不需要输入密码</li>
                <li>更快速：直接导入，无需验证码</li>
                <li>更稳定：不容易触发风控</li>
              </ul>
            </el-alert>

            <!-- Cookie导入区域 -->
            <div 
              class="cookie-drop-zone"
              :class="{ 'is-dragover': isDragover }"
              @drop="handleDrop"
              @dragover="handleDragOver"
              @dragleave="handleDragLeave"
            >
              <el-icon :size="60" color="#409EFF"><Upload /></el-icon>
              <h3>拖拽Cookie文件到此处</h3>
              <p>支持 JSON / Netscape / Header 格式</p>
              
              <div class="cookie-actions">
                <el-button type="primary" @click="selectCookieFile">
                  <el-icon><FolderOpened /></el-icon>
                  选择文件
                </el-button>
                <el-button @click="showPasteDialog">
                  <el-icon><Document /></el-icon>
                  粘贴Cookie
                </el-button>
              </div>

              <input 
                ref="fileInput" 
                type="file" 
                accept=".json,.txt" 
                style="display: none"
                @change="handleFileSelect"
              />
            </div>

            <!-- Cookie预览 -->
            <div v-if="parsedCookies.length > 0" class="cookie-preview">
              <h4>✅ Cookie已解析（{{ parsedCookies.length }}条）</h4>
              <el-table :data="parsedCookies.slice(0, 5)" size="small" max-height="200">
                <el-table-column prop="name" label="名称" width="150" />
                <el-table-column prop="value" label="值" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span>{{ maskValue(row.value) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="domain" label="域名" width="150" />
              </el-table>
              <p v-if="parsedCookies.length > 5" class="more-cookies">
                还有 {{ parsedCookies.length - 5 }} 条Cookie未显示...
              </p>
            </div>

            <!-- 帮助链接 -->
            <div class="help-links">
              <el-button link type="primary" @click="openCookieTutorial">
                <el-icon><QuestionFilled /></el-icon>
                如何获取Cookie？查看图文教程
              </el-button>
              <el-button link type="success" @click="openVideoTutorial">
                <el-icon><VideoPlay /></el-icon>
                观看视频教程（3分钟）
              </el-button>
            </div>
          </div>

          <!-- 账号密码登录方式 -->
          <div v-else class="login-password">
            <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 20px;">
              ⚠️ 使用账号密码登录可能需要验证码，建议使用Cookie导入方式
            </el-alert>

            <el-form :model="loginForm" label-width="80px" size="large">
              <el-form-item label="邮箱">
                <el-input 
                  v-model="loginForm.email" 
                  placeholder="请输入KOOK邮箱"
                  clearable
                >
                  <template #prefix><el-icon><Message /></el-icon></template>
                </el-input>
              </el-form-item>

              <el-form-item label="密码">
                <el-input 
                  v-model="loginForm.password" 
                  type="password" 
                  placeholder="请输入密码"
                  show-password
                  clearable
                >
                  <template #prefix><el-icon><Lock /></el-icon></template>
                </el-input>
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="loginForm.savePassword">
                  保存密码（加密存储）
                </el-checkbox>
              </el-form-item>
            </el-form>
          </div>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button @click="prevStep" size="large">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button 
              type="primary" 
              @click="handleLogin" 
              size="large"
              :loading="isLogging"
              :disabled="!canLogin"
            >
              {{ isLogging ? '登录中...' : '登录并继续' }}
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 选择服务器 -->
        <div v-else-if="currentStep === 2" class="step-servers">
          <div class="step-header">
            <h2>🏠 选择要监听的服务器</h2>
            <p>勾选您想要转发消息的KOOK服务器和频道</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="loadingServers" class="loading-state">
            <el-skeleton :rows="5" animated />
            <p class="loading-text">正在加载您的服务器列表...</p>
          </div>

          <!-- 服务器列表 -->
          <div v-else-if="servers.length > 0" class="servers-list">
            <!-- 快捷操作 -->
            <div class="servers-toolbar">
              <el-button @click="selectAllServers" size="small">
                <el-icon><Check /></el-icon>
                全选
              </el-button>
              <el-button @click="unselectAllServers" size="small">
                <el-icon><Close /></el-icon>
                全不选
              </el-button>
              <div class="servers-stats">
                已选择: <strong>{{ selectedServersCount }}</strong> 个服务器, 
                <strong>{{ selectedChannelsCount }}</strong> 个频道
              </div>
            </div>

            <!-- 服务器卡片 -->
            <div class="servers-grid">
              <el-card 
                v-for="server in servers" 
                :key="server.id"
                :class="{ 'server-selected': server.selected }"
                class="server-card"
                shadow="hover"
              >
                <template #header>
                  <div class="server-header">
                    <el-checkbox 
                      v-model="server.selected" 
                      @change="toggleServer(server)"
                      size="large"
                    >
                      <div class="server-info">
                        <img 
                          v-if="server.icon" 
                          :src="server.icon" 
                          class="server-icon"
                        />
                        <div v-else class="server-icon-placeholder">
                          {{ server.name.charAt(0) }}
                        </div>
                        <strong>{{ server.name }}</strong>
                      </div>
                    </el-checkbox>
                  </div>
                </template>

                <!-- 频道列表 -->
                <div v-if="server.selected" class="channels-list">
                  <el-button 
                    v-if="!server.channelsLoaded"
                    @click="loadChannels(server)"
                    :loading="server.loadingChannels"
                    size="small"
                    text
                  >
                    <el-icon><View /></el-icon>
                    加载频道列表
                  </el-button>

                  <div v-else-if="server.channels && server.channels.length > 0">
                    <div class="channels-toolbar">
                      <el-button 
                        @click="selectAllChannels(server)" 
                        size="small"
                        text
                      >
                        全选频道
                      </el-button>
                    </div>
                    
                    <el-checkbox-group v-model="server.selectedChannels" class="channels-group">
                      <el-checkbox 
                        v-for="channel in server.channels" 
                        :key="channel.id"
                        :label="channel.id"
                        :value="channel.id"
                      >
                        <span class="channel-name">
                          <el-icon v-if="channel.type === 'text'"><ChatDotRound /></el-icon>
                          <el-icon v-else><Microphone /></el-icon>
                          # {{ channel.name }}
                        </span>
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>

                  <el-empty 
                    v-else 
                    description="该服务器没有可用频道"
                    :image-size="60"
                  />
                </div>

                <div v-else class="server-unselected-tip">
                  <el-icon><InfoFilled /></el-icon>
                  勾选服务器后可查看频道列表
                </div>
              </el-card>
            </div>
          </div>

          <!-- 无服务器状态 -->
          <el-empty 
            v-else 
            description="未找到任何服务器，请检查账号登录状态"
            :image-size="100"
          >
            <el-button type="primary" @click="retryLoadServers">
              <el-icon><Refresh /></el-icon>
              重新加载
            </el-button>
          </el-empty>

          <!-- 操作按钮 -->
          <div class="step-actions">
            <el-button @click="prevStep" size="large">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button 
              type="success" 
              @click="finishWizard" 
              size="large"
              :disabled="selectedChannelsCount === 0"
            >
              <el-icon><Check /></el-icon>
              完成配置
            </el-button>
          </div>

          <!-- 提示信息 -->
          <el-alert 
            v-if="selectedChannelsCount === 0"
            type="warning" 
            :closable="false"
            show-icon
            style="margin-top: 20px;"
          >
            请至少选择一个频道后再完成配置
          </el-alert>
        </div>
      </div>
    </el-card>

    <!-- Cookie粘贴对话框 -->
    <el-dialog 
      v-model="showCookiePasteDialog" 
      title="粘贴Cookie" 
      width="600px"
    >
      <el-input
        v-model="cookiePasteText"
        type="textarea"
        :rows="10"
        placeholder="请粘贴Cookie内容（支持JSON、Netscape、Header格式）"
      />
      <template #footer>
        <el-button @click="showCookiePasteDialog = false">取消</el-button>
        <el-button type="primary" @click="parsePastedCookie">
          <el-icon><Check /></el-icon>
          解析并导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  House, User, Check, SuccessFilled, Warning, ArrowRight, ArrowLeft,
  Document, Lock, Upload, FolderOpened, QuestionFilled, VideoPlay,
  Message, Close, View, ChatDotRound, Microphone, InfoFilled, Refresh
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// ========== 步骤0: 免责声明相关 ==========
const activeDisclaimer = ref(['1'])
const agreedToDisclaimer = ref(false)
const hasReadFully = ref(false)
const readProgress = ref(0)
const disclaimerScroll = ref(null)

const progressColor = computed(() => {
  if (readProgress.value < 50) return '#E6A23C'
  if (readProgress.value < 100) return '#409EFF'
  return '#67C23A'
})

const formatProgress = (percentage) => {
  if (percentage < 100) return `请继续阅读 ${percentage}%`
  return '✅ 已阅读完毕'
}

const handleDisclaimerScroll = ({ scrollTop, scrollLeft }) => {
  const scrollbar = disclaimerScroll.value
  if (!scrollbar) return
  
  const { wrap } = scrollbar
  if (!wrap) return
  
  const scrollHeight = wrap.scrollHeight - wrap.clientHeight
  const progress = Math.min(100, Math.round((scrollTop / scrollHeight) * 100))
  readProgress.value = progress
  
  if (progress >= 95) {
    hasReadFully.value = true
  }
}

const handleReject = () => {
  ElMessageBox.confirm(
    '您拒绝了免责声明，应用将关闭。',
    '确认退出',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '返回继续阅读',
      type: 'warning'
    }
  ).then(() => {
    if (window.electron && window.electron.closeWindow) {
      window.electron.closeWindow()
    } else {
      router.push('/')
    }
  })
}

const handleAgree = () => {
  if (!agreedToDisclaimer.value) {
    ElMessage.warning('请先勾选同意声明')
    return
  }
  
  // 记录同意时间
  localStorage.setItem('disclaimer_agreed', 'true')
  localStorage.setItem('disclaimer_agreed_time', new Date().toISOString())
  localStorage.setItem('disclaimer_version', '1.0')
  
  nextStep()
}

// ========== 步骤1: 登录相关 ==========
const loginMethod = ref('cookie')
const isDragover = ref(false)
const parsedCookies = ref([])
const showCookiePasteDialog = ref(false)
const cookiePasteText = ref('')
const fileInput = ref(null)
const isLogging = ref(false)

const loginForm = ref({
  email: '',
  password: '',
  savePassword: false
})

const canLogin = computed(() => {
  if (loginMethod.value === 'cookie') {
    return parsedCookies.value.length > 0
  } else {
    return loginForm.value.email && loginForm.value.password
  }
})

const handleDragOver = (e) => {
  e.preventDefault()
  isDragover.value = true
}

const handleDragLeave = () => {
  isDragover.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragover.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleCookieFile(files[0])
  }
}

const selectCookieFile = () => {
  fileInput.value.click()
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    handleCookieFile(files[0])
  }
}

const handleCookieFile = async (file) => {
  try {
    const text = await file.text()
    parseCookieText(text)
  } catch (error) {
    ElMessage.error('文件读取失败: ' + error.message)
  }
}

const showPasteDialog = () => {
  cookiePasteText.value = ''
  showCookiePasteDialog.value = true
}

const parsePastedCookie = () => {
  if (!cookiePasteText.value.trim()) {
    ElMessage.warning('请粘贴Cookie内容')
    return
  }
  
  parseCookieText(cookiePasteText.value)
  showCookiePasteDialog.value = false
}

const parseCookieText = (text) => {
  try {
    // 尝试使用后端API解析Cookie
    api.post('/api/cookie-import-enhanced/parse', { cookie: text })
      .then(response => {
        if (response.data.success) {
          parsedCookies.value = response.data.cookies
          ElMessage.success(`✅ 成功解析 ${response.data.cookies.length} 条Cookie`)
        } else {
          ElMessage.error('Cookie解析失败: ' + response.data.message)
        }
      })
      .catch(error => {
        ElMessage.error('Cookie解析失败: ' + error.message)
      })
  } catch (error) {
    ElMessage.error('Cookie解析失败: ' + error.message)
  }
}

const maskValue = (value) => {
  if (!value || value.length < 10) return value
  return value.substring(0, 5) + '***' + value.substring(value.length - 5)
}

const openCookieTutorial = () => {
  router.push('/help?topic=cookie')
}

const openVideoTutorial = () => {
  router.push('/help/videos?id=cookie-import')
}

const handleLogin = async () => {
  isLogging.value = true
  
  try {
    if (loginMethod.value === 'cookie') {
      // Cookie登录
      const response = await api.post('/api/accounts/add', {
        cookie: JSON.stringify(parsedCookies.value),
        login_method: 'cookie'
      })
      
      if (response.data.success) {
        accountId.value = response.data.account_id
        ElMessage.success('✅ Cookie导入成功！')
        await nextTick()
        nextStep()
        // 自动加载服务器
        await loadServers()
      } else {
        ElMessage.error('登录失败: ' + response.data.message)
      }
    } else {
      // 账号密码登录
      const response = await api.post('/api/accounts/add', {
        email: loginForm.value.email,
        password: loginForm.value.password,
        save_password: loginForm.value.savePassword,
        login_method: 'password'
      })
      
      if (response.data.success) {
        accountId.value = response.data.account_id
        ElMessage.success('✅ 登录成功！')
        await nextTick()
        nextStep()
        // 自动加载服务器
        await loadServers()
      } else {
        ElMessage.error('登录失败: ' + response.data.message)
      }
    }
  } catch (error) {
    ElMessage.error('登录失败: ' + error.message)
  } finally {
    isLogging.value = false
  }
}

// ========== 步骤2: 服务器选择相关 ==========
const accountId = ref(null)
const servers = ref([])
const loadingServers = ref(false)

const selectedServersCount = computed(() => {
  return servers.value.filter(s => s.selected).length
})

const selectedChannelsCount = computed(() => {
  return servers.value.reduce((count, server) => {
    return count + (server.selectedChannels?.length || 0)
  }, 0)
})

const loadServers = async () => {
  if (!accountId.value) {
    ElMessage.error('账号ID不存在')
    return
  }
  
  loadingServers.value = true
  
  try {
    const response = await api.get(`/api/accounts/${accountId.value}/servers`)
    
    if (response.data.success) {
      servers.value = response.data.servers.map(s => ({
        ...s,
        selected: false,
        channelsLoaded: false,
        loadingChannels: false,
        channels: [],
        selectedChannels: []
      }))
      
      ElMessage.success(`✅ 加载了 ${servers.value.length} 个服务器`)
    } else {
      ElMessage.error('加载服务器失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('加载服务器失败: ' + error.message)
  } finally {
    loadingServers.value = false
  }
}

const retryLoadServers = () => {
  loadServers()
}

const toggleServer = async (server) => {
  if (server.selected && !server.channelsLoaded) {
    await loadChannels(server)
  }
}

const loadChannels = async (server) => {
  server.loadingChannels = true
  
  try {
    const response = await api.get(`/api/accounts/${accountId.value}/servers/${server.id}/channels`)
    
    if (response.data.success) {
      server.channels = response.data.channels
      server.channelsLoaded = true
      // 默认全选
      server.selectedChannels = server.channels.map(c => c.id)
      ElMessage.success(`✅ 加载了 ${server.channels.length} 个频道`)
    } else {
      ElMessage.error('加载频道失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('加载频道失败: ' + error.message)
  } finally {
    server.loadingChannels = false
  }
}

const selectAllServers = () => {
  servers.value.forEach(s => {
    s.selected = true
    if (!s.channelsLoaded) {
      loadChannels(s)
    }
  })
}

const unselectAllServers = () => {
  servers.value.forEach(s => {
    s.selected = false
    s.selectedChannels = []
  })
}

const selectAllChannels = (server) => {
  server.selectedChannels = server.channels.map(c => c.id)
}

// ========== 导航相关 ==========
const nextStep = () => {
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const finishWizard = async () => {
  if (selectedChannelsCount.value === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }
  
  // 保存配置
  const selectedData = {
    account_id: accountId.value,
    servers: servers.value
      .filter(s => s.selected)
      .map(s => ({
        id: s.id,
        name: s.name,
        channels: s.channels
          .filter(c => s.selectedChannels.includes(c.id))
          .map(c => ({ id: c.id, name: c.name }))
      }))
  }
  
  try {
    // 保存到localStorage
    localStorage.setItem('wizard_completed', 'true')
    localStorage.setItem('wizard_completed_time', new Date().toISOString())
    localStorage.setItem('wizard_config', JSON.stringify(selectedData))
    
    // 显示完成通知
    ElNotification({
      title: '🎉 配置完成！',
      message: '基础配置已完成，您现在可以：\n1. 配置Bot（Discord/Telegram/飞书）\n2. 设置频道映射\n3. 直接启动服务开始转发',
      type: 'success',
      duration: 6000
    })
    
    // 弹窗询问下一步
    ElMessageBox.confirm(
      '基础配置已完成！接下来您想要：',
      '选择下一步操作',
      {
        confirmButtonText: '配置Bot和映射',
        cancelButtonText: '直接进入主界面',
        distinguishCancelAndClose: true,
        type: 'success'
      }
    ).then(() => {
      router.push('/bots')
    }).catch(() => {
      router.push('/')
    })
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  // 检查是否已经同意免责声明
  const agreed = localStorage.getItem('disclaimer_agreed')
  if (agreed === 'true') {
    agreedToDisclaimer.value = true
    hasReadFully.value = true
    readProgress.value = 100
  }
})
</script>

<style scoped lang="scss">
.wizard-quick-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.wizard-card {
  max-width: 900px;
  width: 100%;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.wizard-header {
  text-align: center;
  padding: 20px 0;
  
  h1 {
    font-size: 32px;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .subtitle {
    font-size: 16px;
    color: #909399;
  }
}

.steps-indicator {
  margin: 30px 0;
}

.wizard-content {
  padding: 30px 0;
  min-height: 400px;
}

/* 欢迎页样式 */
.step-welcome {
  .welcome-banner {
    text-align: center;
    padding: 40px 0;
    
    h2 {
      font-size: 28px;
      margin: 20px 0 10px;
    }
    
    p {
      font-size: 16px;
      color: #606266;
    }
  }
  
  .disclaimer-collapse {
    margin: 30px 0;
    border: 2px solid #E6A23C;
    border-radius: 8px;
  }
  
  .disclaimer-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: bold;
    font-size: 16px;
  }
  
  .disclaimer-content {
    .disclaimer-text {
      padding: 20px;
      line-height: 1.8;
      
      h3 {
        color: #303133;
        margin: 20px 0 10px;
        font-size: 18px;
      }
      
      p {
        margin: 10px 0;
        color: #606266;
      }
      
      ul {
        margin: 10px 0;
        padding-left: 30px;
        
        li {
          margin: 8px 0;
          color: #606266;
        }
      }
    }
    
    .read-progress {
      margin-top: 20px;
    }
  }
  
  .disclaimer-agreement {
    margin-top: 20px;
    
    .disabled-text {
      color: #C0C4CC;
    }
    
    .read-tip {
      margin-top: 15px;
    }
  }
}

/* 登录页样式 */
.step-login {
  .step-header {
    text-align: center;
    margin-bottom: 30px;
    
    h2 {
      font-size: 24px;
      margin-bottom: 10px;
    }
    
    p {
      color: #909399;
    }
  }
  
  .login-method-group {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
  }
  
  .cookie-drop-zone {
    border: 3px dashed #DCDFE6;
    border-radius: 12px;
    padding: 60px 40px;
    text-align: center;
    transition: all 0.3s;
    background: #FAFAFA;
    
    &.is-dragover {
      border-color: #409EFF;
      background: #ECF5FF;
      animation: pulse 1s infinite;
    }
    
    h3 {
      margin: 20px 0 10px;
      font-size: 20px;
    }
    
    p {
      color: #909399;
      margin-bottom: 30px;
    }
    
    .cookie-actions {
      display: flex;
      gap: 15px;
      justify-content: center;
    }
  }
  
  .cookie-preview {
    margin-top: 30px;
    
    h4 {
      margin-bottom: 15px;
      color: #67C23A;
    }
    
    .more-cookies {
      text-align: center;
      color: #909399;
      margin-top: 10px;
    }
  }
  
  .help-links {
    margin-top: 30px;
    text-align: center;
    display: flex;
    gap: 20px;
    justify-content: center;
  }
}

/* 服务器选择页样式 */
.step-servers {
  .step-header {
    text-align: center;
    margin-bottom: 30px;
    
    h2 {
      font-size: 24px;
      margin-bottom: 10px;
    }
    
    p {
      color: #909399;
    }
  }
  
  .loading-state {
    text-align: center;
    
    .loading-text {
      margin-top: 20px;
      color: #909399;
    }
  }
  
  .servers-toolbar {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: #F5F7FA;
    border-radius: 8px;
    
    .servers-stats {
      margin-left: auto;
      color: #606266;
      
      strong {
        color: #409EFF;
      }
    }
  }
  
  .servers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .server-card {
    transition: all 0.3s;
    
    &.server-selected {
      border-color: #409EFF;
      box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
    }
    
    .server-header {
      .server-info {
        display: flex;
        align-items: center;
        gap: 10px;
        
        .server-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
        }
        
        .server-icon-placeholder {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 20px;
          font-weight: bold;
        }
      }
    }
    
    .channels-list {
      .channels-toolbar {
        margin-bottom: 10px;
      }
      
      .channels-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .channel-name {
          display: flex;
          align-items: center;
          gap: 5px;
        }
      }
    }
    
    .server-unselected-tip {
      text-align: center;
      padding: 20px;
      color: #909399;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
    }
  }
}

/* 操作按钮 */
.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #EBEEF5;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}
</style>
