<template>
  <div class="wizard-simplified-container">
    <el-card class="wizard-card">
      <!-- ✅ 简化版配置向导：仅3步核心流程 -->
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎使用" description="开始配置" />
        <el-step title="登录KOOK" description="添加账号" />
        <el-step title="选择服务器" description="监听频道" />
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤1: 欢迎页 + 免责声明 -->
        <WizardStepWelcome
          v-if="currentStep === 0"
          @next="nextStep"
          @skip="handleSkipWizard"
          @reject="handleRejectDisclaimer"
        />

        <!-- 步骤2: KOOK账号登录 -->
        <WizardStepLogin
          v-else-if="currentStep === 1"
          @next="handleAccountAdded"
          @prev="prevStep"
          @openVideo="openVideoTutorial"
        />

        <!-- 步骤3: 选择服务器和频道 -->
        <WizardStepServers
          v-else-if="currentStep === 2"
          :servers="servers"
          :loading="loadingServers"
          :loading-channels="loadingChannels"
          :account-added="accountAdded"
          @next="finishWizard"
          @prev="prevStep"
          @loadServers="loadServers"
          @loadChannels="loadChannels"
          @toggleServer="toggleServer"
          @selectAll="selectAll"
          @unselectAll="unselectAll"
        />
      </div>
    </el-card>

    <!-- 视频教程对话框 -->
    <el-dialog
      v-model="showVideoDialog"
      title="视频教程"
      width="80%"
      :close-on-click-modal="false"
    >
      <VideoTutorial :video-id="currentVideoId" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import WizardStepWelcome from '@/components/wizard/WizardStepWelcome.vue'
import WizardStepLogin from '@/components/wizard/WizardStepLogin.vue'
import WizardStepServers from '@/components/wizard/WizardStepServers.vue'
import VideoTutorial from '@/components/VideoTutorial.vue'

// ✅ P0-3优化：导入自定义样式
import '@/assets/wizard-complete.css'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 账号是否已添加
const accountAdded = ref(false)

// 服务器相关
const servers = ref([])
const loadingServers = ref(false)
const loadingChannels = ref({})

// 视频教程
const showVideoDialog = ref(false)
const currentVideoId = ref('')

// 下一步
function nextStep() {
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

// 上一步
function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理账号添加完成
async function handleAccountAdded(accountId) {
  accountAdded.value = true
  ElMessage.success('账号添加成功！正在加载服务器列表...')
  
  // 自动加载服务器
  await loadServers(accountId)
  
  // 进入下一步
  nextStep()
}

// 加载服务器列表
async function loadServers(accountId) {
  loadingServers.value = true
  try {
    const response = await api.get(`/api/accounts/${accountId}/servers`)
    servers.value = response.data.servers.map(server => ({
      ...server,
      selected: false,
      channels: [],
      channelsLoaded: false
    }))
  } catch (error) {
    ElMessage.error('加载服务器列表失败: ' + error.message)
  } finally {
    loadingServers.value = false
  }
}

// 加载频道列表
async function loadChannels(serverId) {
  const server = servers.value.find(s => s.id === serverId)
  if (!server || server.channelsLoaded) return

  loadingChannels.value[serverId] = true
  try {
    const response = await api.get(`/api/accounts/${server.account_id}/servers/${serverId}/channels`)
    server.channels = response.data.channels.map(channel => ({
      ...channel,
      selected: true // 默认全选
    }))
    server.channelsLoaded = true
  } catch (error) {
    ElMessage.error('加载频道列表失败: ' + error.message)
  } finally {
    loadingChannels.value[serverId] = false
  }
}

// 切换服务器选择
function toggleServer(serverId) {
  const server = servers.value.find(s => s.id === serverId)
  if (server) {
    server.selected = !server.selected
    
    // 如果选中且未加载频道，则加载
    if (server.selected && !server.channelsLoaded) {
      loadChannels(serverId)
    }
  }
}

// 全选
function selectAll() {
  servers.value.forEach(server => {
    server.selected = true
    if (!server.channelsLoaded) {
      loadChannels(server.id)
    }
  })
}

// 取消全选
function unselectAll() {
  servers.value.forEach(server => {
    server.selected = false
  })
}

// 完成配置向导
async function finishWizard() {
  // 统计选中的频道
  const selectedChannels = []
  servers.value.forEach(server => {
    if (server.selected) {
      server.channels.forEach(channel => {
        if (channel.selected) {
          selectedChannels.push({
            server_id: server.id,
            server_name: server.name,
            channel_id: channel.id,
            channel_name: channel.name
          })
        }
      })
    }
  })

  if (selectedChannels.length === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }

  try {
    // 保存配置
    await api.post('/api/wizard/complete', {
      selectedChannels
    })

    ElMessage.success('配置完成！')
    
    // 标记向导已完成
    localStorage.setItem('wizard_completed', 'true')
    
    // 显示首次使用提示，然后跳转到主界面
    await ElMessageBox.confirm(
      '配置向导已完成！接下来您可以：\n\n' +
      '1. 配置Discord/Telegram/飞书机器人\n' +
      '2. 设置频道映射规则\n' +
      '3. 开始转发消息\n\n' +
      '现在开始快速配置吗？',
      '🎉 欢迎使用',
      {
        confirmButtonText: '开始配置（推荐）',
        cancelButtonText: '稍后配置',
        type: 'success'
      }
    )
    
    // 用户选择立即配置，跳转到快速配置
    router.push('/quick-setup')
    
  } catch (error) {
    // 用户选择稍后配置
    if (error === 'cancel') {
      router.push('/')
    } else {
      ElMessage.error('保存配置失败: ' + error.message)
    }
  }
}

// 跳过向导
async function handleSkipWizard() {
  try {
    await ElMessageBox.confirm(
      '跳过向导后，您需要手动配置所有功能。确定要跳过吗？',
      '确认跳过',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续配置',
        type: 'warning'
      }
    )
    
    localStorage.setItem('wizard_skipped', 'true')
    router.push('/')
  } catch {
    // 用户取消
  }
}

// 拒绝免责声明
function handleRejectDisclaimer() {
  ElMessage.error('您必须同意免责声明才能使用本软件')
  
  // 退出应用（如果是Electron环境）
  if (window.electronAPI) {
    window.electronAPI.quit()
  }
}

// 打开视频教程
function openVideoTutorial(videoId) {
  currentVideoId.value = videoId
  showVideoDialog.value = true
}
</script>

<style scoped>
.wizard-simplified-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.wizard-card {
  width: 100%;
  max-width: 1000px;
  min-height: 600px;
}

.wizard-content {
  margin-top: 40px;
  padding: 20px;
}
</style>
