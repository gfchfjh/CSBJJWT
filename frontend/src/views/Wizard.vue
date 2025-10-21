<template>
  <div class="wizard-container">
    <el-card class="wizard-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎" description="开始配置" />
        <el-step title="登录KOOK" description="添加账号" />
        <el-step title="选择服务器" description="监听频道" />
        <el-step title="配置机器人" description="选择平台" />
        <el-step title="完成" description="开始使用" />
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤1: 欢迎页 -->
        <WizardStepWelcome
          v-if="currentStep === 0"
          @next="nextStep"
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

        <!-- 步骤4: 配置机器人 -->
        <WizardStepBots
          v-else-if="currentStep === 3"
          :added-bots="addedBots"
          @next="nextStep"
          @prev="prevStep"
          @addBot="handleAddBot"
          @skip="handleSkipBots"
        />

        <!-- 步骤5: 完成 -->
        <WizardStepComplete
          v-else-if="currentStep === 4"
          :account-added="accountAdded"
          :selected-channels-count="selectedChannelsCount"
          :bots-count="addedBots.length"
          @finish="finishWizard"
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
import WizardStepBots from '@/components/wizard/WizardStepBots.vue'
import WizardStepComplete from '@/components/wizard/WizardStepComplete.vue'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 账号是否已添加
const accountAdded = ref(false)

// 已添加的Bots
const addedBots = ref([])

// 服务器相关
const servers = ref([])
const loadingServers = ref(false)
const loadingChannels = ref({})

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

// 处理服务器选择完成
const handleServerSelectionComplete = () => {
  // 将选中的频道信息保存到localStorage供后续使用
  const selectedData = {
    servers: servers.value
      .filter(s => s.selectedChannels && s.selectedChannels.length > 0)
      .map(s => ({
        id: s.id,
        name: s.name,
        channels: s.channels
          .filter(c => s.selectedChannels.includes(c.id))
          .map(c => ({
            id: c.id,
            name: c.name,
            type: c.type
          }))
      }))
  }
  
  localStorage.setItem('wizard_selected_channels', JSON.stringify(selectedData))
  ElMessage.success(`已保存 ${selectedChannelsCount.value} 个频道`)
  nextStep()
}

// 处理添加Bot
const handleAddBot = async (data, platform) => {
  try {
    const response = await api.addBot(data)
    ElMessage.success('Bot添加成功')
    addedBots.value.push(response.data)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

// 处理跳过Bot配置（v1.12.0+ 优化：更友好的提示）
const handleSkipBots = () => {
  ElMessageBox.confirm(
    '跳过Bot配置后，您将无法立即转发消息。建议至少配置一个目标平台Bot。',
    '确认跳过？',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '返回配置',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.info({
      message: '已跳过机器人配置。您可以稍后在"机器人配置"页面添加Bot。',
      duration: 5000,
      showClose: true
    })
    currentStep.value = 4  // 直接跳转到完成步骤
  }).catch(() => {
    // 用户取消，不做任何操作
  })
}

// 打开视频教程
const openVideoTutorial = (type) => {
  // 这里可以打开视频教程对话框或跳转到教程页面
  ElMessage.info(`打开${type}视频教程（功能开发中）`)
}

// 完成向导（v1.12.0+ 优化：根据配置情况给出不同提示）
const finishWizard = () => {
  // 标记向导已完成
  localStorage.setItem('wizard_completed', 'true')
  
  // 检查配置完整性，给出相应提示
  if (addedBots.value.length === 0) {
    ElMessage.warning({
      message: '提示：您还没有配置任何Bot，无法转发消息。建议进入"机器人配置"页面添加。',
      duration: 8000,
      showClose: true
    })
  } else if (selectedChannelsCount.value === 0) {
    ElMessage.warning({
      message: '提示：您还没有选择任何频道，建议进入"频道映射"页面配置映射关系。',
      duration: 8000,
      showClose: true
    })
  } else {
    ElMessage.success({
      message: '🎉 配置完成！现在可以开始使用消息转发功能了。',
      duration: 5000,
      showClose: true
    })
  }
  
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
