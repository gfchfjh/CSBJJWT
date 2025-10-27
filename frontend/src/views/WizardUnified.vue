<template>
  <div class="wizard-unified">
    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" align-center finish-status="success">
      <el-step title="连接KOOK" icon="Link" />
      <el-step title="配置转发" icon="Setting" />
      <el-step title="开始使用" icon="Check" />
    </el-steps>

    <!-- 模式选择（首次显示） -->
    <transition name="fade">
      <div v-if="showModeSelection" class="mode-selection">
        <h2>🚀 选择配置模式</h2>
        <p class="mode-desc">根据您的需求选择合适的配置方式</p>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-card 
              class="mode-card quick-mode" 
              shadow="hover"
              @click="selectMode('quick')"
            >
              <div class="mode-icon">🚀</div>
              <h3>快速模式</h3>
              <div class="mode-badge">推荐新手</div>
              <p class="mode-time">⏱️ 预计3分钟完成</p>
              <ul class="mode-features">
                <li>✅ Cookie一键导入</li>
                <li>✅ 智能频道映射</li>
                <li>✅ 自动测试配置</li>
                <li>✅ 开箱即用</li>
              </ul>
              <el-button type="primary" size="large" round>
                立即开始
              </el-button>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card 
              class="mode-card advanced-mode" 
              shadow="hover"
              @click="selectMode('advanced')"
            >
              <div class="mode-icon">🛠️</div>
              <h3>专业模式</h3>
              <div class="mode-badge advanced">高级用户</div>
              <p class="mode-time">⏱️ 预计10分钟完成</p>
              <ul class="mode-features">
                <li>✅ 多账号管理</li>
                <li>✅ 精细化映射</li>
                <li>✅ 过滤规则配置</li>
                <li>✅ 高级功能</li>
              </ul>
              <el-button type="info" size="large" round>
                自定义配置
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </transition>

    <!-- 动态步骤组件 -->
    <transition name="slide-fade" mode="out-in">
      <component 
        v-if="!showModeSelection"
        :is="currentStepComponent" 
        :key="currentStep"
        :mode="selectedMode"
        :wizard-data="wizardData"
        @next="handleNext"
        @prev="handlePrev"
        @complete="handleComplete"
        @update-data="updateWizardData"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 步骤组件（动态导入）
import StepQuickConnect from '@/components/wizard/StepQuickConnect.vue'
import StepQuickConfigure from '@/components/wizard/StepQuickConfigure.vue'
import StepComplete from '@/components/wizard/StepComplete.vue'
import StepLogin from '@/components/wizard/WizardStepLogin.vue'
import StepServers from '@/components/wizard/WizardStepServers.vue'
import StepBots from '@/components/wizard/WizardStepBotConfig.vue'
import StepMapping from '@/components/wizard/WizardStepQuickMapping.vue'

const router = useRouter()

const currentStep = ref(0)
const selectedMode = ref(null)
const showModeSelection = ref(true)
const wizardData = ref({
  accountId: null,
  accounts: [],
  servers: [],
  selectedChannels: [],
  botConfigs: [],
  mappings: []
})

// 快速模式步骤：连接→配置→完成
const quickModeSteps = [
  StepQuickConnect,     // Cookie导入 + 自动验证
  StepQuickConfigure,   // Bot配置 + 智能映射
  StepComplete          // 配置摘要 + 启动按钮
]

// 专业模式步骤：登录→服务器→Bot→映射→完成
const advancedModeSteps = [
  StepLogin,
  StepServers,
  StepBots,
  StepMapping,
  StepComplete
]

const currentStepComponent = computed(() => {
  const steps = selectedMode.value === 'quick' ? quickModeSteps : advancedModeSteps
  return steps[currentStep.value]
})

const totalSteps = computed(() => {
  return selectedMode.value === 'quick' ? 3 : 5
})

const selectMode = (mode) => {
  selectedMode.value = mode
  showModeSelection.value = false
  currentStep.value = 0
  
  ElMessage.success({
    message: mode === 'quick' 
      ? '🚀 已选择快速模式，让我们开始吧！' 
      : '🛠️ 已选择专业模式，您可以完全控制配置',
    duration: 3000
  })
}

const handleNext = (data) => {
  // 更新向导数据
  if (data) {
    Object.assign(wizardData.value, data)
  }

  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++
  }
}

const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  } else {
    // 返回模式选择
    showModeSelection.value = true
    selectedMode.value = null
  }
}

const updateWizardData = (data) => {
  Object.assign(wizardData.value, data)
}

const handleComplete = () => {
  // 标记向导已完成
  localStorage.setItem('wizard_completed', 'true')
  localStorage.setItem('wizard_mode', selectedMode.value)
  localStorage.setItem('wizard_completed_time', new Date().toISOString())
  
  // 保存配置摘要
  localStorage.setItem('wizard_summary', JSON.stringify({
    mode: selectedMode.value,
    accounts: wizardData.value.accounts.length,
    channels: wizardData.value.selectedChannels.length,
    bots: wizardData.value.botConfigs.length,
    mappings: wizardData.value.mappings.length
  }))

  // 通知Electron主进程
  if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.send('wizard-completed', {
      mode: selectedMode.value,
      summary: wizardData.value
    })
  }

  ElMessage.success({
    message: '🎉 配置完成！系统已准备就绪',
    duration: 5000,
    showClose: true
  })

  // 跳转到主页
  setTimeout(() => {
    router.push('/')
  }, 1000)
}
</script>

<style scoped>
.wizard-unified {
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.el-steps {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

/* 模式选择 */
.mode-selection {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.mode-selection h2 {
  color: white;
  font-size: 36px;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.mode-desc {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  margin-bottom: 40px;
}

.mode-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 16px;
  padding: 40px 30px;
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 3px solid transparent;
}

.mode-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.quick-mode:hover {
  border-color: #409EFF;
}

.advanced-mode:hover {
  border-color: #909399;
}

.mode-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.mode-card h3 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #303133;
}

.mode-badge {
  display: inline-block;
  padding: 6px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 15px;
}

.mode-badge.advanced {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.mode-time {
  color: #909399;
  font-size: 16px;
  margin-bottom: 20px;
}

.mode-features {
  list-style: none;
  padding: 0;
  margin: 20px 0;
  text-align: left;
  flex: 1;
}

.mode-features li {
  padding: 12px 0;
  font-size: 16px;
  color: #606266;
  border-bottom: 1px solid #EBEEF5;
}

.mode-features li:last-child {
  border-bottom: none;
}

.mode-card .el-button {
  width: 100%;
  font-size: 18px;
  padding: 16px;
  margin-top: 20px;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>
