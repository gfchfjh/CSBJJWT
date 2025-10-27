<template>
  <div class="wizard-container">
    <!-- 进度指示器 -->
    <div class="progress-indicator">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="progress-step"
        :class="{
          'is-active': currentStep === index,
          'is-completed': currentStep > index
        }"
      >
        <div class="step-number">
          <el-icon v-if="currentStep > index"><Check /></el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-label">{{ step.title }}</div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 第1步：欢迎页 -->
      <div v-if="currentStep === 0" class="step-panel">
        <div class="welcome-panel">
          <div class="welcome-icon">
            <el-icon :size="120"><Promotion /></el-icon>
          </div>
          <h1>🎉 欢迎使用KOOK消息转发系统</h1>
          <p class="welcome-desc">
            本向导将帮助您快速完成基础配置，只需 <strong>3步</strong>，预计耗时 <strong>3-5分钟</strong>
          </p>
          
          <div class="features">
            <div class="feature-item">
              <el-icon color="#409EFF"><Lightning /></el-icon>
              <span>简单快速</span>
            </div>
            <div class="feature-item">
              <el-icon color="#67C23A"><Lock /></el-icon>
              <span>安全可靠</span>
            </div>
            <div class="feature-item">
              <el-icon color="#E6A23C"><Setting /></el-icon>
              <span>灵活配置</span>
            </div>
          </div>

          <el-alert
            title="💡 提示"
            type="info"
            :closable="false"
            style="margin-top: 30px"
          >
            <p>完成向导后，您可以：</p>
            <ul>
              <li>配置Discord/Telegram/飞书转发Bot（可选）</li>
              <li>设置频道映射关系</li>
              <li>自定义过滤规则</li>
            </ul>
          </el-alert>
        </div>
      </div>

      <!-- 第2步：登录KOOK账号 -->
      <div v-if="currentStep === 1" class="step-panel">
        <h2>📧 登录KOOK账号</h2>
        <p class="step-desc">请选择登录方式，我们将使用此账号监听KOOK消息</p>

        <el-tabs v-model="loginMethod" class="login-tabs">
          <!-- Cookie导入（推荐） -->
          <el-tab-pane label="Cookie导入（推荐）" name="cookie">
            <div class="tab-content">
              <el-alert
                title="推荐：Cookie导入方式更安全快捷"
                type="success"
                :closable="false"
                show-icon
                style="margin-bottom: 20px"
              />
              
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                @click="showCookieImport"
              >
                <el-icon><Upload /></el-icon>
                导入Cookie
              </el-button>

              <div v-if="cookieImported" class="import-success">
                <el-icon color="#67C23A" :size="48"><SuccessFilled /></el-icon>
                <p>✅ Cookie已成功导入</p>
                <p class="account-info">账号：{{ accountInfo.email || '已登录' }}</p>
              </div>

              <div class="help-links">
                <el-link type="primary" @click="showCookieHelp">
                  <el-icon><QuestionFilled /></el-icon>
                  如何获取Cookie？
                </el-link>
                <el-link type="primary" @click="showVideoTutorial">
                  <el-icon><VideoPlay /></el-icon>
                  观看视频教程
                </el-link>
              </div>
            </div>
          </el-tab-pane>

          <!-- 账号密码登录 -->
          <el-tab-pane label="账号密码登录" name="password">
            <div class="tab-content">
              <el-alert
                title="注意：首次登录可能需要验证码"
                type="warning"
                :closable="false"
                show-icon
                style="margin-bottom: 20px"
              />

              <el-form :model="loginForm" label-width="80px">
                <el-form-item label="邮箱">
                  <el-input
                    v-model="loginForm.email"
                    placeholder="请输入KOOK登录邮箱"
                    clearable
                  >
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
                    size="large"
                    style="width: 100%"
                    :loading="logging"
                    :disabled="!loginForm.email || !loginForm.password"
                    @click="handlePasswordLogin"
                  >
                    <el-icon><User /></el-icon>
                    登录
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 第3步：选择监听的服务器 -->
      <div v-if="currentStep === 2" class="step-panel">
        <h2>🏠 选择要监听的KOOK服务器</h2>
        <p class="step-desc">请选择您要监听消息的服务器和频道</p>

        <div v-if="loadingServers" class="loading-state">
          <el-icon class="is-loading" :size="48"><Loading /></el-icon>
          <p>正在加载服务器列表...</p>
        </div>

        <div v-else-if="servers.length === 0" class="empty-state">
          <el-icon :size="64" color="#909399"><FolderOpened /></el-icon>
          <p>未找到任何服务器</p>
          <p class="empty-hint">请确保您的账号已加入至少一个KOOK服务器</p>
        </div>

        <div v-else class="server-list">
          <el-checkbox-group v-model="selectedServers" @change="handleServerChange">
            <div
              v-for="server in servers"
              :key="server.id"
              class="server-card"
              :class="{ 'is-selected': selectedServers.includes(server.id) }"
            >
              <el-checkbox :label="server.id">
                <div class="server-info">
                  <img
                    v-if="server.icon"
                    :src="server.icon"
                    class="server-icon"
                    alt="服务器图标"
                  />
                  <div v-else class="server-icon-placeholder">
                    {{ server.name.substring(0, 1) }}
                  </div>
                  <div class="server-details">
                    <h3>{{ server.name }}</h3>
                    <p>{{ server.channel_count || 0 }} 个频道</p>
                  </div>
                </div>
              </el-checkbox>

              <!-- 频道列表（展开显示） -->
              <div
                v-if="selectedServers.includes(server.id)"
                class="channel-list"
              >
                <el-collapse v-model="expandedChannels">
                  <el-collapse-item :name="server.id">
                    <template #title>
                      <span class="channel-header">
                        <el-icon><List /></el-icon>
                        查看频道列表（{{ server.channels?.length || 0 }}个）
                      </span>
                    </template>
                    <el-checkbox-group
                      v-model="selectedChannels[server.id]"
                      class="channel-checkbox-group"
                    >
                      <div
                        v-for="channel in server.channels"
                        :key="channel.id"
                        class="channel-item"
                      >
                        <el-checkbox :label="channel.id">
                          <el-icon v-if="channel.type === 'voice'"><Headset /></el-icon>
                          <el-icon v-else><ChatDotRound /></el-icon>
                          <span>{{ channel.name }}</span>
                        </el-checkbox>
                      </div>
                    </el-checkbox-group>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </el-checkbox-group>

          <div class="selection-summary">
            <el-tag type="info" size="large">
              已选择 {{ selectedServers.length }} 个服务器
            </el-tag>
            <el-tag type="primary" size="large">
              已选择 {{ totalSelectedChannels }} 个频道
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 第4步：完成 -->
      <div v-if="currentStep === 3" class="step-panel">
        <div class="completion-panel">
          <div class="success-icon">
            <el-icon :size="120" color="#67C23A"><SuccessFilled /></el-icon>
          </div>
          <h1>✅ 配置完成！</h1>
          <p class="completion-desc">
            基础配置已完成，您现在可以：
          </p>

          <div class="next-steps">
            <el-card class="next-step-card" shadow="hover" @click="goToBots">
              <div class="next-step-content">
                <el-icon :size="48" color="#409EFF"><Robot /></el-icon>
                <h3>配置转发Bot</h3>
                <p>添加Discord/Telegram/飞书Bot，开始转发消息</p>
                <el-button type="primary" text>
                  立即配置 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>

            <el-card class="next-step-card" shadow="hover" @click="goToMapping">
              <div class="next-step-content">
                <el-icon :size="48" color="#67C23A"><Connection /></el-icon>
                <h3>设置频道映射</h3>
                <p>建立KOOK频道与目标平台的映射关系</p>
                <el-button type="success" text>
                  立即设置 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>

            <el-card class="next-step-card" shadow="hover" @click="startService">
              <div class="next-step-content">
                <el-icon :size="48" color="#E6A23C"><VideoPlay /></el-icon>
                <h3>直接启动服务</h3>
                <p>跳过高级配置，立即开始监听消息（稍后可配置）</p>
                <el-button type="warning" text>
                  启动服务 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>
          </div>

          <el-alert
            title="💡 温馨提示"
            type="info"
            :closable="false"
            style="margin-top: 30px"
          >
            <ul>
              <li>您可以随时在"设置"中修改这些配置</li>
              <li>建议先配置至少一个Bot，否则消息无法转发</li>
              <li>可以使用"智能映射"功能自动创建频道映射</li>
            </ul>
          </el-alert>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="wizard-footer">
      <el-button
        v-if="currentStep > 0 && currentStep < 3"
        size="large"
        @click="prevStep"
      >
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>

      <div class="footer-spacer"></div>

      <el-button
        v-if="currentStep < 2"
        size="large"
        @click="skipWizard"
      >
        跳过向导
      </el-button>

      <el-button
        v-if="currentStep === 0"
        type="primary"
        size="large"
        @click="nextStep"
      >
        开始配置
        <el-icon><ArrowRight /></el-icon>
      </el-button>

      <el-button
        v-if="currentStep === 1"
        type="primary"
        size="large"
        :disabled="!cookieImported && loginMethod === 'cookie'"
        @click="nextStep"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>

      <el-button
        v-if="currentStep === 2"
        type="primary"
        size="large"
        :disabled="selectedServers.length === 0"
        @click="completeWizard"
      >
        完成配置
        <el-icon><Check /></el-icon>
      </el-button>
    </div>

    <!-- Cookie导入对话框 -->
    <CookieImportDialog
      v-model="cookieDialogVisible"
      @imported="handleCookieImported"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import CookieImportDialog from '@/components/CookieImportDialog.vue'
import api from '@/api'

const router = useRouter()

// 步骤定义
const steps = [
  { title: '欢迎' },
  { title: '登录账号' },
  { title: '选择服务器' },
  { title: '完成' }
]

const currentStep = ref(0)

// 登录相关
const loginMethod = ref('cookie')
const cookieDialogVisible = ref(false)
const cookieImported = ref(false)
const accountInfo = reactive({
  email: '',
  id: null
})

const loginForm = reactive({
  email: '',
  password: ''
})

const logging = ref(false)

// 服务器相关
const loadingServers = ref(false)
const servers = ref([])
const selectedServers = ref([])
const selectedChannels = reactive({})
const expandedChannels = ref([])

// 计算已选频道总数
const totalSelectedChannels = computed(() => {
  let total = 0
  for (const serverId in selectedChannels) {
    total += selectedChannels[serverId]?.length || 0
  }
  return total
})

// 显示Cookie导入
const showCookieImport = () => {
  cookieDialogVisible.value = true
}

// Cookie导入成功
const handleCookieImported = (data) => {
  cookieImported.value = true
  accountInfo.email = data.email || '已登录'
  accountInfo.id = data.id
  ElMessage.success('✅ Cookie导入成功！')
}

// 密码登录
const handlePasswordLogin = async () => {
  try {
    logging.value = true
    
    const response = await api.post('/api/accounts/login', {
      email: loginForm.email,
      password: loginForm.password
    })

    if (response.success) {
      cookieImported.value = true
      accountInfo.email = loginForm.email
      accountInfo.id = response.account_id
      ElMessage.success('✅ 登录成功！')
    } else {
      ElMessage.error('登录失败：' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败：' + (error.response?.data?.detail || error.message))
  } finally {
    logging.value = false
  }
}

// 显示Cookie帮助
const showCookieHelp = () => {
  router.push('/help?section=cookie')
}

// 显示视频教程
const showVideoTutorial = () => {
  router.push('/help?video=cookie-import')
}

// 加载服务器列表
const loadServers = async () => {
  if (!accountInfo.id) {
    ElMessage.error('请先登录账号')
    return
  }

  try {
    loadingServers.value = true
    
    const response = await api.get(`/api/accounts/${accountInfo.id}/servers`)
    
    if (response.success) {
      servers.value = response.servers || []
      
      // 自动加载每个服务器的频道
      for (const server of servers.value) {
        const channelsRes = await api.get(`/api/accounts/${accountInfo.id}/servers/${server.id}/channels`)
        if (channelsRes.success) {
          server.channels = channelsRes.channels || []
          server.channel_count = server.channels.length
        }
      }
    } else {
      ElMessage.error('加载服务器列表失败')
    }
  } catch (error) {
    console.error('加载服务器失败:', error)
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingServers.value = false
  }
}

// 服务器选择变化
const handleServerChange = (selected) => {
  // 初始化选中服务器的频道数组
  for (const serverId of selected) {
    if (!selectedChannels[serverId]) {
      selectedChannels[serverId] = []
      // 默认选中所有频道
      const server = servers.value.find(s => s.id === serverId)
      if (server && server.channels) {
        selectedChannels[serverId] = server.channels.map(c => c.id)
      }
    }
  }
  
  // 删除未选中服务器的频道数据
  const unselected = Object.keys(selectedChannels).filter(id => !selected.includes(id))
  for (const serverId of unselected) {
    delete selectedChannels[serverId]
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 1) {
    // 登录步骤完成，加载服务器
    await loadServers()
  }
  
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 跳过向导
const skipWizard = () => {
  ElMessageBox.confirm(
    '跳过向导将直接进入主界面，您可以稍后在设置中完成配置。确定要跳过吗？',
    '提示',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置',
      type: 'warning'
    }
  ).then(() => {
    localStorage.setItem('wizard_completed', 'skipped')
    router.push('/')
  }).catch(() => {
    // 取消，继续配置
  })
}

// 完成向导
const completeWizard = async () => {
  try {
    // 保存配置
    await api.post('/api/wizard/complete', {
      account_id: accountInfo.id,
      selected_servers: selectedServers.value,
      selected_channels: selectedChannels
    })

    localStorage.setItem('wizard_completed', 'true')
    localStorage.setItem('wizard_completed_time', new Date().toISOString())
    
    // 进入完成页
    currentStep.value = 3
    
    ElMessage.success('✅ 向导配置已完成！')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  }
}

// 前往Bot配置
const goToBots = () => {
  router.push('/bots')
}

// 前往映射配置
const goToMapping = () => {
  router.push('/mapping')
}

// 启动服务
const startService = async () => {
  try {
    await api.post('/api/system/start')
    ElMessage.success('✅ 服务已启动！')
    router.push('/')
  } catch (error) {
    console.error('启动服务失败:', error)
    ElMessage.error('启动失败：' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.wizard-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 进度指示器 */
.progress-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 60px;
  position: relative;
}

.progress-indicator::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 60px;
  right: 60px;
  height: 2px;
  background-color: #e4e7ed;
  z-index: 0;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e4e7ed;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.progress-step.is-active .step-number {
  background-color: #409eff;
  color: white;
  transform: scale(1.2);
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.progress-step.is-completed .step-number {
  background-color: #67c23a;
  color: white;
}

.step-label {
  font-size: 14px;
  color: #909399;
}

.progress-step.is-active .step-label {
  color: #409eff;
  font-weight: 600;
}

/* 步骤内容 */
.wizard-content {
  flex: 1;
  margin-bottom: 40px;
}

.step-panel {
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

.step-panel h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 12px;
}

.step-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 30px;
}

/* 欢迎页 */
.welcome-panel {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 30px;
  color: #409eff;
}

.welcome-panel h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 16px;
}

.welcome-desc {
  font-size: 16px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 40px;
}

.features {
  display: flex;
  justify-content: center;
  gap: 60px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: #606266;
}

.feature-item .el-icon {
  font-size: 48px;
}

/* 登录标签 */
.login-tabs {
  margin-top: 20px;
}

.tab-content {
  padding: 20px 0;
}

.import-success {
  margin: 30px 0;
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
  border-radius: 12px;
}

.import-success p {
  margin: 12px 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #67c23a;
}

.account-info {
  font-size: 14px !important;
  color: #606266 !important;
  font-weight: normal !important;
}

.help-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
}

/* 服务器列表 */
.loading-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #909399;
}

.loading-state p,
.empty-state p {
  margin-top: 20px;
  font-size: 16px;
}

.empty-hint {
  font-size: 14px !important;
  color: #c0c4cc !important;
  margin-top: 8px !important;
}

.server-list {
  padding: 20px 0;
}

.server-card {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s;
  cursor: pointer;
}

.server-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.server-card.is-selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.server-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.server-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.server-icon-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.server-details h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.server-details p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #909399;
}

.channel-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e4e7ed;
}

.channel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.channel-checkbox-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px 0;
}

.channel-item {
  display: flex;
  align-items: center;
}

.channel-item .el-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}

.selection-summary {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px dashed #e4e7ed;
}

/* 完成页 */
.completion-panel {
  text-align: center;
  padding: 20px;
}

.success-icon {
  margin-bottom: 30px;
}

.completion-panel h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 16px;
}

.completion-desc {
  font-size: 16px;
  color: #606266;
  margin-bottom: 40px;
}

.next-steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.next-step-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.next-step-card:hover {
  transform: translateY(-8px);
}

.next-step-content {
  text-align: center;
  padding: 20px;
}

.next-step-content h3 {
  margin: 16px 0 12px 0;
  font-size: 18px;
  color: #303133;
}

.next-step-content p {
  font-size: 14px;
  color: #909399;
  margin-bottom: 16px;
  line-height: 1.6;
}

/* 底部按钮 */
.wizard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
}

.footer-spacer {
  flex: 1;
}
</style>
