<template>
  <div class="wizard-container">
    <el-card class="wizard-card">
      <!-- ✅ P0-1优化完成: 扩展为5步完整向导 -->
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎" description="开始配置" />
        <el-step title="登录KOOK" description="添加账号" />
        <el-step title="选择服务器" description="监听频道" />
        <el-step title="配置Bot" description="转发目标" />
        <el-step title="频道映射" description="完成配置" />
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤1: 欢迎页 -->
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
          @next="handleServerSelectionComplete"
          @prev="prevStep"
          @loadServers="loadServers"
          @loadChannels="loadChannels"
          @toggleServer="toggleServer"
          @selectAll="selectAll"
          @unselectAll="unselectAll"
        />

        <!-- ✅ 步骤4: Bot配置 -->
        <WizardStepBotConfig
          v-else-if="currentStep === 3"
          @next="handleBotConfigComplete"
          @prev="prevStep"
        />

        <!-- ✅ 步骤5: 快速映射 -->
        <WizardStepQuickMapping
          v-else-if="currentStep === 4"
          :selected-channels="selectedChannels"
          :configured-bots="configuredBots"
          @next="finishWizard"
          @prev="prevStep"
          @complete="finishWizard"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import WizardStepWelcome from '@/components/wizard/WizardStepWelcome.vue'
import WizardStepLogin from '@/components/wizard/WizardStepLogin.vue'
import WizardStepServers from '@/components/wizard/WizardStepServers.vue'
import WizardStepBotConfig from '@/components/wizard/WizardStepBotConfig.vue'
import WizardStepQuickMapping from '@/components/wizard/WizardStepQuickMapping.vue'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 账号是否已添加
const accountAdded = ref(false)

// 服务器相关
const servers = ref([])
const loadingServers = ref(false)
const loadingChannels = ref({})

// ✅ 新增：Bot配置和选中的频道数据
const configuredBots = ref([])
const selectedChannels = ref([])

const selectedChannelsCount = computed(() => {
  return servers.value.reduce((count, server) => {
    return count + (server.selectedChannels?.length || 0)
  }, 0)
})

// 步骤导航
const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
    
    // 如果进入到服务器选择步骤，自动加载服务器列表
    if (currentStep.value === 2 && accountAdded.value && servers.value.length === 0) {
      loadServers()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理免责声明拒绝
const handleRejectDisclaimer = () => {
  ElMessageBox.confirm(
    '您拒绝了免责声明，应用将关闭。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 如果是Electron环境，关闭窗口
    if (window.electron && window.electron.closeWindow) {
      window.electron.closeWindow()
    } else {
      // 否则返回首页
      router.push('/')
    }
  }).catch(() => {
    // 用户取消了
  })
}

// 处理账号添加成功
const handleAccountAdded = () => {
  accountAdded.value = true
  nextStep()
}

// 加载服务器列表
const loadServers = async () => {
  try {
    loadingServers.value = true
    const accounts = await api.getAccounts()
    
    if (!accounts || accounts.length === 0) {
      ElMessage.warning('未找到KOOK账号')
      return
    }

    // 获取第一个在线账号的服务器列表
    const onlineAccount = accounts.find(a => a.status === 'online')
    if (!onlineAccount) {
      ElMessage.warning('账号未在线，请等待账号连接成功后重试')
      return
    }

    const result = await api.getServers(onlineAccount.id)
    servers.value = result.map(server => ({
      ...server,
      selected: false,
      selectedChannels: [],
      channels: null
    }))

    if (servers.value.length === 0) {
      ElMessage.warning('未获取到服务器列表，请确保账号已登录KOOK')
    }
  } catch (error) {
    ElMessage.error('加载服务器失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingServers.value = false
  }
}

// 加载频道列表
const loadChannels = async (serverId) => {
  try {
    loadingChannels.value[serverId] = true
    
    const accounts = await api.getAccounts()
    const onlineAccount = accounts.find(a => a.status === 'online')
    if (!onlineAccount) {
      ElMessage.warning('账号未在线')
      return
    }

    const channels = await api.getChannels(onlineAccount.id, serverId)
    
    const server = servers.value.find(s => s.id === serverId)
    if (server) {
      server.channels = channels
    }
  } catch (error) {
    ElMessage.error('加载频道失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingChannels.value[serverId] = false
  }
}

// 切换服务器选择状态
const toggleServer = (server) => {
  if (server.selected) {
    // 选中服务器时，加载其频道列表
    if (!server.channels) {
      loadChannels(server.id)
    } else {
      // 如果已加载，则全选频道
      server.selectedChannels = server.channels.map(c => c.id)
    }
  } else {
    // 取消选中服务器时，清空已选频道
    server.selectedChannels = []
  }
}

// 全选
const selectAll = () => {
  servers.value.forEach(server => {
    server.selected = true
    if (server.channels) {
      server.selectedChannels = server.channels.map(c => c.id)
    } else {
      loadChannels(server.id)
    }
  })
}

// 全不选
const unselectAll = () => {
  servers.value.forEach(server => {
    server.selected = false
    server.selectedChannels = []
  })
}

// ✅ P0-1优化: 服务器选择完成后进入Bot配置步骤
const handleServerSelectionComplete = () => {
  // 保存选中的频道信息
  selectedChannels.value = servers.value
    .filter(s => s.selectedChannels && s.selectedChannels.length > 0)
    .flatMap(s => 
      s.channels
        .filter(c => s.selectedChannels.includes(c.id))
        .map(c => ({
          server_id: s.id,
          server_name: s.name,
          channel_id: c.id,
          channel_name: c.name,
          channel_type: c.type
        }))
    )
  
  ElMessage.success(`已选择 ${selectedChannelsCount.value} 个频道`)
  
  // 进入Bot配置步骤
  nextStep()
}

// ✅ P0-1优化: Bot配置完成
const handleBotConfigComplete = (data) => {
  configuredBots.value = data.botConfigs || []
  ElMessage.success(`已配置 ${configuredBots.value.length} 个Bot`)
  
  // 进入快速映射步骤
  nextStep()
}

// ✅ P0-1优化: 新增跳过向导功能
const handleSkipWizard = () => {
  ElMessageBox.confirm(
    '跳过配置向导后，您需要手动配置账号和Bot。确定要跳过吗？',
    '跳过配置向导',
    {
      confirmButtonText: '跳过',
      cancelButtonText: '继续配置',
      type: 'warning',
    }
  ).then(() => {
    localStorage.setItem('wizard_completed', 'true')
    ElMessage.info('已跳过配置向导，请手动配置')
    router.push('/')
  }).catch(() => {
    // 用户取消
  })
}

// 打开视频教程
const openVideoTutorial = (type) => {
  // 这里可以打开视频教程对话框或跳转到教程页面
  ElMessage.info(`打开${type}视频教程（功能开发中）`)
}

// ✅ P0-1优化: 完成完整的5步向导
const finishWizard = () => {
  // 标记向导已完成
  localStorage.setItem('wizard_completed', 'true')
  
  // 通知Electron主进程
  if (window.electron && window.electron.ipcRenderer) {
    window.electron.ipcRenderer.send('wizard-completed')
  }
  
  // 显示成功消息
  ElMessage.success({
    message: '🎉 配置完成！系统已开始自动监听和转发消息。',
    duration: 5000,
    showClose: true
  })
  
  // 跳转到主页
  router.push('/')
}
</script>

<style scoped>
.wizard-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: calc(100vh - 40px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.wizard-card {
  width: 900px;
  max-width: 95%;
}

.wizard-content {
  margin-top: 40px;
  min-height: 500px;
}
</style>
