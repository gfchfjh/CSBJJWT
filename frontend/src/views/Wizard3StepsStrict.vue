<template>
  <div class="wizard-3-steps-strict">
    <!-- 步骤指示器 -->
    <div class="wizard-header">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="欢迎" description="了解基本功能" />
        <el-step title="KOOK账号登录" description="配置消息源" />
        <el-step title="选择监听服务器" description="选择要监听的频道" />
      </el-steps>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 第1步：欢迎页 -->
      <div v-show="currentStep === 0" class="wizard-step step-welcome">
        <div class="welcome-header">
          <el-icon class="welcome-icon" :size="100"><Present /></el-icon>
          <h1>欢迎使用 KOOK 消息转发系统</h1>
          <p class="welcome-subtitle">本向导将帮助您完成基础配置</p>
          <p class="welcome-time">预计耗时：3-5 分钟</p>
        </div>

        <div class="welcome-features">
          <div class="feature-card">
            <el-icon :size="50" color="#409EFF"><Connection /></el-icon>
            <h3>自动监听</h3>
            <p>实时监听 KOOK 频道消息</p>
          </div>
          <div class="feature-card">
            <el-icon :size="50" color="#67C23A"><Share /></el-icon>
            <h3>多平台转发</h3>
            <p>支持 Discord / Telegram / 飞书</p>
          </div>
          <div class="feature-card">
            <el-icon :size="50" color="#E6A23C"><Setting /></el-icon>
            <h3>智能配置</h3>
            <p>可视化映射 · 一键测试</p>
          </div>
        </div>

        <div class="welcome-actions">
          <el-button size="large" @click="skipWizard">跳过向导</el-button>
          <el-button type="primary" size="large" @click="nextStep">
            下一步 <el-icon class="ml-1"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第2步：KOOK账号登录 -->
      <div v-show="currentStep === 1" class="wizard-step step-login">
        <div class="step-title">
          <h2>📧 登录KOOK账号</h2>
          <p>请选择登录方式，首次登录可能需要验证码</p>
        </div>

        <el-tabs v-model="loginMethod" class="login-tabs">
          <!-- 账号密码登录 -->
          <el-tab-pane label="账号密码登录" name="password">
            <el-form :model="loginForm" label-width="100px" class="login-form">
              <el-form-item label="邮箱">
                <el-input
                  v-model="loginForm.email"
                  placeholder="your@email.com"
                  :prefix-icon="Message"
                  size="large"
                />
              </el-form-item>
              <el-form-item label="密码">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="isLoggingIn"
                  @click="loginWithPassword"
                  style="width: 100%"
                >
                  {{ isLoggingIn ? '登录中...' : '登录' }}
                </el-button>
              </el-form-item>
            </el-form>
            <el-alert
              type="info"
              :closable="false"
              show-icon
              title="ℹ️ 首次登录可能需要验证码"
            >
              <p>如果出现验证码弹窗，请根据提示完成验证</p>
            </el-alert>
          </el-tab-pane>

          <!-- Cookie导入 -->
          <el-tab-pane label="Cookie导入" name="cookie">
            <el-radio-group v-model="cookieMethod" class="cookie-methods">
              <el-radio value="file" size="large">上传JSON文件</el-radio>
              <el-radio value="text" size="large">粘贴Cookie文本</el-radio>
            </el-radio-group>

            <!-- 文件上传 -->
            <div v-if="cookieMethod === 'file'" class="cookie-upload">
              <el-upload
                drag
                :auto-upload="false"
                :on-change="handleCookieFileUpload"
                :show-file-list="false"
                accept=".json"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将Cookie JSON文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持JSON格式的Cookie文件
                  </div>
                </template>
              </el-upload>
            </div>

            <!-- 文本粘贴 -->
            <div v-if="cookieMethod === 'text'" class="cookie-text">
              <el-input
                v-model="cookieText"
                type="textarea"
                :rows="8"
                placeholder="请粘贴Cookie文本（JSON格式）"
              />
              <el-button
                type="primary"
                size="large"
                :loading="isLoggingIn"
                @click="loginWithCookie"
                style="width: 100%; margin-top: 10px"
              >
                验证并添加
              </el-button>
            </div>

            <!-- 教程链接 -->
            <div class="cookie-tutorial">
              <el-divider>📖 如何获取Cookie？</el-divider>
              <div class="tutorial-buttons">
                <el-button @click="openTutorial('cookie-browser')">
                  <el-icon><Document /></el-icon>
                  浏览器F12方法
                </el-button>
                <el-button @click="openTutorial('cookie-extension')">
                  <el-icon><Promotion /></el-icon>
                  Chrome扩展方法
                </el-button>
                <el-button @click="openVideoTutorial('cookie')">
                  <el-icon><VideoPlay /></el-icon>
                  观看视频教程
                </el-button>
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
            :disabled="!isLoggedIn"
            @click="nextStep"
          >
            下一步 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第3步：选择监听的服务器 -->
      <div v-show="currentStep === 2" class="wizard-step step-servers">
        <div class="step-title">
          <h2>🏠 选择要监听的KOOK服务器</h2>
          <p>请勾选您想要监听的服务器和频道</p>
        </div>

        <div class="server-selection">
          <div class="selection-toolbar">
            <el-button size="small" @click="selectAll">全选</el-button>
            <el-button size="small" @click="deselectAll">全不选</el-button>
            <el-button
              size="small"
              type="primary"
              :loading="isLoadingServers"
              @click="refreshServers"
            >
              <el-icon><Refresh /></el-icon> 刷新列表
            </el-button>
          </div>

          <el-scrollbar height="400px" v-loading="isLoadingServers">
            <el-tree
              ref="serverTreeRef"
              :data="serverTree"
              :props="treeProps"
              show-checkbox
              node-key="id"
              :default-expand-all="true"
              @check="handleServerCheck"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon v-if="data.type === 'server'"><OfficeBuilding /></el-icon>
                  <el-icon v-else><ChatLineSquare /></el-icon>
                  <span class="node-label">{{ data.label }}</span>
                  <el-tag v-if="data.type === 'channel'" size="small" type="info">
                    {{ data.channel_type }}
                  </el-tag>
                </span>
              </template>
            </el-tree>
          </el-scrollbar>

          <div class="selection-summary">
            <el-alert type="success" :closable="false">
              <template #title>
                已选择 <strong>{{ selectedServersCount }}</strong> 个服务器，
                <strong>{{ selectedChannelsCount }}</strong> 个频道
              </template>
            </el-alert>
          </div>
        </div>

        <div class="wizard-actions">
          <el-button size="large" @click="prevStep">
            <el-icon><ArrowLeft /></el-icon> 上一步
          </el-button>
          <el-button
            type="primary"
            size="large"
            :disabled="selectedChannelsCount === 0"
            :loading="isSaving"
            @click="completeWizard"
          >
            <el-icon><Check /></el-icon> 完成配置
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Present, Connection, Share, Setting, ArrowRight, ArrowLeft,
  Message, Lock, UploadFilled, Document, Promotion, VideoPlay,
  Refresh, OfficeBuilding, ChatLineSquare, Check
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// 当前步骤（0-2，共3步）
const currentStep = ref(0)

// 登录相关
const loginMethod = ref('password')
const loginForm = ref({
  email: '',
  password: ''
})
const cookieMethod = ref('file')
const cookieText = ref('')
const isLoggingIn = ref(false)
const isLoggedIn = ref(false)
const currentAccountId = ref(null)

// 服务器选择
const serverTreeRef = ref(null)
const serverTree = ref([])
const isLoadingServers = ref(false)
const isSaving = ref(false)
const treeProps = {
  children: 'children',
  label: 'label'
}

// 计算已选择的数量
const selectedServersCount = computed(() => {
  if (!serverTreeRef.value) return 0
  const checkedNodes = serverTreeRef.value.getCheckedNodes()
  return checkedNodes.filter(node => node.type === 'server').length
})

const selectedChannelsCount = computed(() => {
  if (!serverTreeRef.value) return 0
  const checkedNodes = serverTreeRef.value.getCheckedNodes()
  return checkedNodes.filter(node => node.type === 'channel').length
})

// 步骤控制
const nextStep = () => {
  if (currentStep.value < 2) {
    currentStep.value++
    
    // 进入第3步时加载服务器列表
    if (currentStep.value === 2) {
      loadServers()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const skipWizard = async () => {
  try {
    await ElMessageBox.confirm(
      '跳过配置向导后，您需要手动配置账号和映射关系。确定要跳过吗？',
      '确认跳过',
      {
        type: 'warning',
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续配置'
      }
    )
    
    // 标记向导已完成
    localStorage.setItem('wizard_completed', 'true')
    router.push('/')
  } catch {
    // 用户取消
  }
}

// 账号密码登录
const loginWithPassword = async () => {
  if (!loginForm.value.email || !loginForm.value.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }

  isLoggingIn.value = true
  try {
    const response = await axios.post('/api/accounts/login', {
      email: loginForm.value.email,
      password: loginForm.value.password
    })

    if (response.data.success) {
      isLoggedIn.value = true
      currentAccountId.value = response.data.account_id
      ElMessage.success('登录成功！Cookie已自动保存')
      
      // 自动进入下一步
      setTimeout(() => {
        nextStep()
      }, 1000)
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查邮箱和密码')
  } finally {
    isLoggingIn.value = false
  }
}

// Cookie文件上传
const handleCookieFileUpload = (file) => {
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const content = e.target.result
      const cookies = JSON.parse(content)
      await importCookies(cookies)
    } catch (error) {
      ElMessage.error('Cookie文件格式错误，请检查文件内容')
    }
  }
  reader.readAsText(file.raw)
}

// Cookie文本导入
const loginWithCookie = async () => {
  if (!cookieText.value.trim()) {
    ElMessage.warning('请粘贴Cookie文本')
    return
  }

  try {
    const cookies = JSON.parse(cookieText.value)
    await importCookies(cookies)
  } catch (error) {
    ElMessage.error('Cookie格式错误，请确保是有效的JSON格式')
  }
}

// 导入Cookies
const importCookies = async (cookies) => {
  isLoggingIn.value = true
  try {
    const response = await axios.post('/api/accounts/import-cookie', {
      cookies: cookies
    })

    if (response.data.success) {
      isLoggedIn.value = true
      currentAccountId.value = response.data.account_id
      ElMessage.success('Cookie导入成功！')
      
      // 自动进入下一步
      setTimeout(() => {
        nextStep()
      }, 1000)
    } else {
      ElMessage.error(response.data.message || 'Cookie验证失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || 'Cookie导入失败')
  } finally {
    isLoggingIn.value = false
  }
}

// 加载服务器列表
const loadServers = async () => {
  if (!currentAccountId.value) {
    ElMessage.warning('请先登录账号')
    return
  }

  isLoadingServers.value = true
  try {
    const response = await axios.get(`/api/accounts/${currentAccountId.value}/servers`)

    if (response.data.success) {
      // 转换为树形结构
      serverTree.value = response.data.servers.map(server => ({
        id: `server-${server.id}`,
        label: server.name,
        type: 'server',
        server_id: server.id,
        children: server.channels.map(channel => ({
          id: `channel-${channel.id}`,
          label: channel.name,
          type: 'channel',
          channel_id: channel.id,
          channel_type: channel.type,
          server_id: server.id
        }))
      }))
    } else {
      ElMessage.error('加载服务器列表失败')
    }
  } catch (error) {
    console.error('加载服务器失败:', error)
    ElMessage.error('加载服务器列表失败，请检查网络连接')
  } finally {
    isLoadingServers.value = false
  }
}

// 刷新服务器列表
const refreshServers = () => {
  loadServers()
}

// 全选/全不选
const selectAll = () => {
  serverTreeRef.value?.setCheckedNodes(serverTree.value)
}

const deselectAll = () => {
  serverTreeRef.value?.setCheckedNodes([])
}

const handleServerCheck = (data, checked) => {
  // 可以添加自定义逻辑
}

// 完成向导
const completeWizard = async () => {
  const checkedNodes = serverTreeRef.value.getCheckedNodes()
  const channels = checkedNodes.filter(node => node.type === 'channel')

  if (channels.length === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }

  isSaving.value = true
  try {
    // 保存监听配置
    const response = await axios.post('/api/accounts/monitoring-config', {
      account_id: currentAccountId.value,
      channels: channels.map(ch => ({
        server_id: ch.server_id,
        channel_id: ch.channel_id,
        channel_name: ch.label
      }))
    })

    if (response.data.success) {
      // 标记向导完成
      localStorage.setItem('wizard_completed', 'true')
      
      ElMessage.success({
        message: '配置完成！',
        duration: 2000
      })

      // 显示下一步引导
      await ElMessageBox.alert(
        `
        <div style="text-align: left;">
          <h3>✅ 基础配置已完成！</h3>
          <p>接下来您可以：</p>
          <ol>
            <li>配置 Discord/Telegram/飞书 机器人</li>
            <li>设置频道映射关系</li>
            <li>启动消息转发服务</li>
          </ol>
          <p style="color: #67C23A;">💡 提示：可随时在设置中修改配置</p>
        </div>
        `,
        '配置完成',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '进入主界面',
          type: 'success'
        }
      )

      // 跳转到主界面
      router.push('/')
    } else {
      ElMessage.error('保存配置失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存配置失败，请重试')
  } finally {
    isSaving.value = false
  }
}

// 打开教程
const openTutorial = (type) => {
  router.push(`/help?tutorial=${type}`)
}

const openVideoTutorial = (type) => {
  router.push(`/help?video=${type}`)
}

onMounted(() => {
  // 检查是否已完成向导
  const completed = localStorage.getItem('wizard_completed')
  if (completed) {
    ElMessageBox.confirm(
      '您已完成过配置向导，是否直接进入主界面？',
      '提示',
      {
        confirmButtonText: '进入主界面',
        cancelButtonText: '重新配置',
        type: 'info'
      }
    ).then(() => {
      router.push('/')
    }).catch(() => {
      // 用户选择重新配置
    })
  }
})
</script>

<style scoped lang="scss">
.wizard-3-steps-strict {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.wizard-header {
  max-width: 900px;
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
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

/* 欢迎页 */
.step-welcome {
  text-align: center;
}

.welcome-header {
  margin-bottom: 40px;

  .welcome-icon {
    color: #667eea;
    margin-bottom: 20px;
  }

  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 10px;
  }

  .welcome-subtitle {
    font-size: 18px;
    color: #606266;
    margin-bottom: 5px;
  }

  .welcome-time {
    font-size: 16px;
    color: #909399;
  }
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  margin-bottom: 40px;
}

.feature-card {
  padding: 30px;
  border: 2px solid #EBEEF5;
  border-radius: 8px;
  transition: all 0.3s;

  &:hover {
    border-color: #667eea;
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
  }

  h3 {
    margin: 15px 0 10px;
    font-size: 20px;
    color: #303133;
  }

  p {
    color: #606266;
    font-size: 14px;
  }
}

.welcome-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 登录页 */
.step-login {
  .step-title {
    text-align: center;
    margin-bottom: 30px;

    h2 {
      font-size: 28px;
      color: #303133;
      margin-bottom: 10px;
    }

    p {
      color: #606266;
      font-size: 16px;
    }
  }

  .login-tabs {
    margin-bottom: 30px;
  }

  .login-form {
    max-width: 500px;
    margin: 30px auto;
  }

  .cookie-methods {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
  }

  .cookie-upload,
  .cookie-text {
    max-width: 600px;
    margin: 0 auto;
  }

  .cookie-tutorial {
    margin-top: 30px;

    .tutorial-buttons {
      display: flex;
      justify-content: center;
      gap: 15px;
      flex-wrap: wrap;
    }
  }
}

/* 服务器选择 */
.step-servers {
  .step-title {
    text-align: center;
    margin-bottom: 30px;

    h2 {
      font-size: 28px;
      color: #303133;
      margin-bottom: 10px;
    }

    p {
      color: #606266;
      font-size: 16px;
    }
  }

  .server-selection {
    margin-bottom: 30px;

    .selection-toolbar {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
    }

    .tree-node {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;

      .node-label {
        flex: 1;
      }
    }

    .selection-summary {
      margin-top: 20px;
    }
  }
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  padding-top: 30px;
  border-top: 1px solid #EBEEF5;
}

.ml-1 {
  margin-left: 5px;
}
</style>
