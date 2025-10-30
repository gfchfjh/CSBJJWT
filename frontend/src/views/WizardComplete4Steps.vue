<template>
  <div class="wizard-complete-container">
    <!-- 进度指示器 -->
    <div class="wizard-progress">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${(currentStep / 4) * 100}%` }"
        ></div>
      </div>
      <div class="progress-steps">
        <div 
          v-for="step in 4" 
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
          <p class="welcome-subtitle">✨ 零代码基础 · 一键安装 · 3分钟上手 ✨</p>
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
              <p>📋 共4个步骤 · 预计耗时 3-5 分钟</p>
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
          <h2>💬 登录 KOOK 账号</h2>
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
                使用浏览器扩展或手动粘贴，3秒完成登录
              </el-alert>

              <div class="cookie-input-area">
                <el-input
                  v-model="cookieText"
                  type="textarea"
                  :rows="6"
                  placeholder="请粘贴 Cookie 内容（JSON格式或文本格式）
示例：[{&quot;name&quot;: &quot;kook_session&quot;, &quot;value&quot;: &quot;...&quot;}]"
                />
                
                <div class="cookie-upload-area">
                  <el-upload
                    drag
                    :auto-upload="false"
                    :on-change="handleCookieFileUpload"
                    accept=".json,.txt"
                  >
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">
                      或拖拽 Cookie 文件到此处
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 .json 和 .txt 格式
                      </div>
                    </template>
                  </el-upload>
                </div>
              </div>

              <div class="help-links">
                <el-link type="primary" :underline="false" @click="showCookieTutorial">
                  <el-icon><QuestionFilled /></el-icon>
                  如何获取 Cookie？
                </el-link>
                <el-link type="success" :underline="false" @click="openChromeExtension">
                  <el-icon><Download /></el-icon>
                  安装 Chrome 扩展
                </el-link>
              </div>

              <el-button 
                type="primary" 
                size="large" 
                style="width: 100%; margin-top: 20px;"
                :loading="verifying"
                :disabled="!cookieText"
                @click="verifyCookie"
              >
                验证并登录
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 账号密码登录 -->
          <el-tab-pane label="账号密码登录" name="password">
            <div class="login-method-content">
              <el-alert 
                type="warning" 
                :closable="false"
                show-icon
                class="mb-4"
              >
                <template #title>
                  <strong>⚠️ 注意</strong>
                </template>
                首次登录可能需要验证码，建议使用 Cookie 导入
              </el-alert>

              <el-form :model="loginForm" label-width="80px">
                <el-form-item label="邮箱">
                  <el-input v-model="loginForm.email" placeholder="请输入 KOOK 邮箱" />
                </el-form-item>
                
                <el-form-item label="密码">
                  <el-input 
                    v-model="loginForm.password" 
                    type="password" 
                    show-password 
                    placeholder="请输入密码"
                  />
                </el-form-item>
              </el-form>

              <el-button 
                type="primary" 
                size="large" 
                style="width: 100%;"
                :loading="logging"
                :disabled="!loginForm.email || !loginForm.password"
                @click="loginWithPassword"
              >
                登录
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 第3步：选择监听的服务器 -->
      <div v-show="currentStep === 3" class="wizard-step step-servers">
        <div class="step-header">
          <h2>🏠 选择要监听的服务器</h2>
          <p>勾选您想要转发消息的服务器和频道</p>
        </div>

        <el-alert 
          type="info" 
          :closable="false"
          show-icon
          class="mb-4"
        >
          <template #title>
            <strong>💡 提示</strong>
          </template>
          可以全选，也可以只选择部分频道。配置完成后可随时修改。
        </el-alert>

        <div class="servers-loading" v-if="loadingServers">
          <el-spin />
          <p>正在加载服务器列表...</p>
        </div>

        <div class="servers-list" v-else>
          <el-empty 
            v-if="servers.length === 0"
            description="未找到服务器"
          />

          <div v-for="server in servers" :key="server.id" class="server-item">
            <div class="server-header">
              <el-checkbox 
                v-model="server.checked"
                @change="toggleServerChannels(server)"
              >
                <div class="server-info">
                  <img 
                    v-if="server.icon" 
                    :src="server.icon" 
                    class="server-icon"
                  />
                  <el-icon v-else class="server-icon-default"><Grid /></el-icon>
                  <span class="server-name">{{ server.name }}</span>
                  <el-tag size="small" type="info">{{ server.channels?.length || 0 }} 个频道</el-tag>
                </div>
              </el-checkbox>
            </div>

            <div v-if="server.channels && server.channels.length > 0" class="channels-list">
              <el-checkbox-group v-model="server.selectedChannels">
                <el-checkbox 
                  v-for="channel in server.channels" 
                  :key="channel.id"
                  :label="channel.id"
                >
                  <div class="channel-info">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>{{ channel.name }}</span>
                  </div>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </div>

        <div class="selection-summary" v-if="selectedChannelsCount > 0">
          <el-tag type="success" size="large">
            已选择 {{ selectedChannelsCount }} 个频道
          </el-tag>
        </div>

        <div class="wizard-actions">
          <el-button size="large" @click="previousStep">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button 
            type="primary" 
            size="large" 
            :disabled="selectedChannelsCount === 0"
            @click="saveServerSelection"
          >
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第4步：完成 -->
      <div v-show="currentStep === 4" class="wizard-step step-complete">
        <div class="complete-header">
          <el-icon class="complete-icon" :size="100" color="#67C23A"><CircleCheck /></el-icon>
          <h1>🎉 配置完成！</h1>
          <p class="complete-subtitle">您已成功完成基础配置</p>
        </div>

        <div class="complete-summary">
          <el-card>
            <template #header>
              <strong>📋 配置摘要</strong>
            </template>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="KOOK 账号">
                <el-tag type="success">已登录</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="监听服务器">
                {{ selectedServersCount }} 个服务器
              </el-descriptions-item>
              <el-descriptions-item label="监听频道">
                {{ selectedChannelsCount }} 个频道
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>

        <div class="next-steps">
          <h3>🚀 接下来您可以：</h3>
          <div class="steps-grid">
            <div class="next-step-card">
              <el-icon :size="40" color="#409EFF"><Setting /></el-icon>
              <h4>1. 配置转发目标</h4>
              <p>设置 Discord / Telegram / 飞书 Bot</p>
            </div>
            <div class="next-step-card">
              <el-icon :size="40" color="#67C23A"><Connection /></el-icon>
              <h4>2. 配置频道映射</h4>
              <p>设置 KOOK 频道到目标平台的映射关系</p>
            </div>
            <div class="next-step-card">
              <el-icon :size="40" color="#E6A23C"><VideoPlay /></el-icon>
              <h4>3. 启动服务</h4>
              <p>一键启动消息转发服务</p>
            </div>
          </div>
        </div>

        <el-alert 
          type="success" 
          :closable="false"
          show-icon
          class="mt-4"
        >
          <template #title>
            <strong>💡 温馨提示</strong>
          </template>
          <ul>
            <li>可以在"账号管理"中修改或添加账号</li>
            <li>可以在"Bot配置"中设置转发目标</li>
            <li>可以随时在"设置"中调整各项参数</li>
          </ul>
        </el-alert>

        <div class="wizard-actions">
          <el-button size="large" @click="runWizardAgain">
            <el-icon><RefreshLeft /></el-icon>
            重新配置
          </el-button>
          <el-button type="primary" size="large" @click="finishWizard">
            进入主界面
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check, Present, Connection, Share, Setting, ArrowRight, ArrowLeft,
  QuestionFilled, Download, UploadFilled, Grid, ChatDotRound,
  CircleCheck, VideoPlay, RefreshLeft
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(1)

// 步骤标签
const stepLabels = ['欢迎', '登录KOOK', '选择服务器', '完成']

// 登录方式
const loginMethod = ref('cookie')

// Cookie文本
const cookieText = ref('')

// 登录表单
const loginForm = reactive({
  email: '',
  password: ''
})

// 加载状态
const verifying = ref(false)
const logging = ref(false)
const loadingServers = ref(false)

// 服务器列表
const servers = ref([])

// 选中的服务器和频道数量
const selectedServersCount = computed(() => {
  return servers.value.filter(s => s.checked).length
})

const selectedChannelsCount = computed(() => {
  return servers.value.reduce((total, server) => {
    return total + (server.selectedChannels?.length || 0)
  }, 0)
})

// 下一步
const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
    
    // 如果进入第3步，加载服务器列表
    if (currentStep.value === 3) {
      loadServers()
    }
  }
}

// 上一步
const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 跳过向导
const skipWizard = async () => {
  try {
    await ElMessageBox.confirm(
      '跳过配置向导后，您需要手动配置所有选项。确定要跳过吗？',
      '确认跳过',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续配置',
        type: 'warning'
      }
    )
    
    // 标记向导已完成
    localStorage.setItem('wizard_completed', 'true')
    
    // 跳转到主界面
    router.push('/')
  } catch {
    // 用户取消
  }
}

// 验证Cookie
const verifyCookie = async () => {
  if (!cookieText.value) {
    ElMessage.warning('请输入 Cookie 内容')
    return
  }
  
  verifying.value = true
  
  try {
    // 尝试解析Cookie
    let cookies
    try {
      cookies = JSON.parse(cookieText.value)
    } catch {
      // 如果不是JSON，尝试按行分割
      ElMessage.error('Cookie 格式不正确，请检查后重试')
      return
    }
    
    // 调用API验证Cookie
    const response = await api.post('/api/accounts/verify-cookie', { cookies })
    
    if (response.data.success) {
      ElMessage.success('Cookie 验证成功！')
      
      // 保存账号
      await api.post('/api/accounts', {
        cookie: cookieText.value,
        source: 'wizard'
      })
      
      nextStep()
    } else {
      ElMessage.error('Cookie 验证失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('验证失败：' + (error.message || '未知错误'))
  } finally {
    verifying.value = false
  }
}

// 账号密码登录
const loginWithPassword = async () => {
  if (!loginForm.email || !loginForm.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  
  logging.value = true
  
  try {
    const response = await api.post('/api/accounts/login', loginForm)
    
    if (response.data.success) {
      ElMessage.success('登录成功！')
      nextStep()
    } else {
      ElMessage.error('登录失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('登录失败：' + (error.message || '未知错误'))
  } finally {
    logging.value = false
  }
}

// 处理Cookie文件上传
const handleCookieFileUpload = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    cookieText.value = e.target.result
    ElMessage.success('文件加载成功！')
  }
  
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  
  reader.readAsText(file.raw)
}

// 显示Cookie教程
const showCookieTutorial = () => {
  ElMessageBox.alert(
    '获取Cookie的步骤：\n\n' +
    '1. 在浏览器中登录 KOOK\n' +
    '2. 按 F12 打开开发者工具\n' +
    '3. 切换到 Application/存储 标签\n' +
    '4. 找到 Cookies → https://www.kookapp.cn\n' +
    '5. 复制所有 Cookie 并粘贴到上方输入框\n\n' +
    '或使用我们提供的 Chrome 扩展一键导出！',
    'Cookie 获取教程',
    {
      confirmButtonText: '我知道了',
      type: 'info'
    }
  )
}

// 打开Chrome扩展
const openChromeExtension = () => {
  window.open('chrome-extension://your-extension-id/popup.html', '_blank')
}

// 加载服务器列表
const loadServers = async () => {
  loadingServers.value = true
  
  try {
    const response = await api.get('/api/servers/discover')
    
    if (response.data.success) {
      servers.value = response.data.servers.map(server => ({
        ...server,
        checked: false,
        selectedChannels: []
      }))
      
      ElMessage.success('服务器列表加载成功')
    }
  } catch (error) {
    ElMessage.error('加载服务器列表失败：' + (error.message || '未知错误'))
  } finally {
    loadingServers.value = false
  }
}

// 切换服务器所有频道
const toggleServerChannels = (server) => {
  if (server.checked) {
    // 全选该服务器的所有频道
    server.selectedChannels = server.channels.map(c => c.id)
  } else {
    // 取消选择
    server.selectedChannels = []
  }
}

// 保存服务器选择
const saveServerSelection = async () => {
  try {
    // 收集选中的频道
    const selectedChannels = []
    servers.value.forEach(server => {
      if (server.selectedChannels && server.selectedChannels.length > 0) {
        server.selectedChannels.forEach(channelId => {
          const channel = server.channels.find(c => c.id === channelId)
          if (channel) {
            selectedChannels.push({
              serverId: server.id,
              serverName: server.name,
              channelId: channel.id,
              channelName: channel.name
            })
          }
        })
      }
    })
    
    // 保存到后端
    await api.post('/api/wizard/save-channels', { channels: selectedChannels })
    
    ElMessage.success('服务器选择已保存')
    nextStep()
  } catch (error) {
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  }
}

// 重新运行向导
const runWizardAgain = () => {
  currentStep.value = 1
  cookieText.value = ''
  loginForm.email = ''
  loginForm.password = ''
  servers.value = []
}

// 完成向导
const finishWizard = () => {
  // 标记向导已完成
  localStorage.setItem('wizard_completed', 'true')
  localStorage.setItem('wizard_completed_at', new Date().toISOString())
  
  ElMessage.success({
    message: '配置完成，欢迎使用 KOOK 消息转发系统！',
    duration: 3000
  })
  
  // 跳转到主界面
  router.push('/')
}
</script>

<style scoped>
.wizard-complete-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.wizard-progress {
  max-width: 900px;
  margin: 0 auto 40px;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: white;
  transition: width 0.3s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.progress-step.active .step-circle {
  background: white;
  color: #667eea;
  transform: scale(1.2);
}

.progress-step.completed .step-circle {
  background: #67C23A;
}

.step-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.progress-step.active .step-label {
  color: white;
  font-weight: bold;
}

.wizard-content {
  max-width: 900px;
  margin: 0 auto;
}

.wizard-step {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

/* 欢迎页 */
.welcome-header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-icon {
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
  text-align: center;
  padding: 30px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.feature-card:hover {
  background: #ecf5ff;
  transform: translateY(-5px);
}

.feature-card h3 {
  margin: 15px 0 10px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
}

.welcome-info {
  margin-bottom: 30px;
}

.info-content p {
  margin: 5px 0;
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 30px;
}

/* 登录步骤 */
.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.step-header p {
  color: #909399;
  font-size: 16px;
}

.login-tabs {
  margin-top: 20px;
}

.login-method-content {
  padding: 20px 0;
}

.cookie-input-area {
  margin: 20px 0;
}

.cookie-upload-area {
  margin-top: 20px;
}

.help-links {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.mb-4 {
  margin-bottom: 20px;
}

/* 服务器选择 */
.servers-loading {
  text-align: center;
  padding: 60px 0;
}

.servers-loading p {
  margin-top: 20px;
  color: #909399;
}

.servers-list {
  max-height: 500px;
  overflow-y: auto;
}

.server-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.server-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.server-header {
  margin-bottom: 15px;
}

.server-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.server-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.server-icon-default {
  width: 32px;
  height: 32px;
  background: #ecf5ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.server-name {
  font-weight: bold;
  font-size: 16px;
}

.channels-list {
  padding-left: 42px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.selection-summary {
  text-align: center;
  margin: 20px 0;
}

/* 完成页 */
.complete-header {
  text-align: center;
  margin-bottom: 40px;
}

.complete-icon {
  margin-bottom: 20px;
}

.complete-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 10px;
}

.complete-subtitle {
  font-size: 18px;
  color: #909399;
}

.complete-summary {
  margin-bottom: 40px;
}

.next-steps h3 {
  text-align: center;
  color: #303133;
  margin-bottom: 30px;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.next-step-card {
  text-align: center;
  padding: 30px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.next-step-card:hover {
  background: #ecf5ff;
  transform: translateY(-5px);
}

.next-step-card h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.next-step-card p {
  color: #909399;
  font-size: 14px;
}

.mt-4 {
  margin-top: 30px;
}

.mt-4 ul {
  margin: 10px 0 0 20px;
}

.mt-4 li {
  margin: 5px 0;
}

.ml-1 {
  margin-left: 4px;
}
</style>
