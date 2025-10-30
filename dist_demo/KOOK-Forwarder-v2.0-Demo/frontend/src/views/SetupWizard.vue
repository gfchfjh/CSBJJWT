<template>
  <div class="setup-wizard">
    <el-card class="wizard-card" shadow="always">
      <!-- 欢迎头部 -->
      <template #header>
        <div class="wizard-header">
          <h1>🎉 欢迎使用 KOOK消息转发系统</h1>
          <p>让我们用3步快速完成配置，预计耗时：5分钟</p>
        </div>
      </template>

      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="连接KOOK" description="登录您的KOOK账号" />
        <el-step title="配置Bot" description="设置转发目标" />
        <el-step title="频道映射" description="建立转发关系" />
        <el-step title="完成配置" description="开始使用" />
      </el-steps>

      <div class="wizard-content">
        <!-- 第1步：KOOK账号登录 -->
        <div v-show="currentStep === 0" class="step-content">
          <WelcomeStep @next="handleWelcomeComplete" />
        </div>

        <!-- 第2步：KOOK账号登录 -->
        <div v-show="currentStep === 1" class="step-content">
          <AccountLoginStep 
            @next="handleAccountComplete" 
            @prev="prevStep"
          />
        </div>

        <!-- 第3步：配置Bot -->
        <div v-show="currentStep === 2" class="step-content">
          <BotConfigStep 
            @next="handleBotComplete" 
            @prev="prevStep"
          />
        </div>

        <!-- 第4步：频道映射 -->
        <div v-show="currentStep === 3" class="step-content">
          <ChannelMappingStep 
            @next="handleMappingComplete" 
            @prev="prevStep"
          />
        </div>

        <!-- 第5步：完成 -->
        <div v-show="currentStep === 4" class="step-content">
          <CompletionStep @finish="handleFinish" />
        </div>
      </div>

      <!-- 底部进度提示 -->
      <template #footer>
        <div class="wizard-footer">
          <el-progress 
            :percentage="progress" 
            :stroke-width="8"
            :color="progressColor"
          />
          <p class="progress-text">
            已完成 {{ currentStep }}/4 步 - {{ progressText }}
          </p>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import WelcomeStep from '@/components/wizard/WelcomeStep.vue'
import AccountLoginStep from '@/components/wizard/AccountLoginStep.vue'
import BotConfigStep from '@/components/wizard/BotConfigStep.vue'
import ChannelMappingStep from '@/components/wizard/ChannelMappingStep.vue'
import CompletionStep from '@/components/wizard/CompletionStep.vue'
import api from '@/api'

const router = useRouter()
const currentStep = ref(0)
const wizardData = ref({
  account: null,
  bots: [],
  mappings: []
})

// 进度计算
const progress = computed(() => {
  return (currentStep.value / 4) * 100
})

const progressColor = computed(() => {
  if (progress.value < 25) return '#909399'
  if (progress.value < 50) return '#E6A23C'
  if (progress.value < 75) return '#409EFF'
  return '#67C23A'
})

const progressText = computed(() => {
  const texts = [
    '准备开始',
    '连接KOOK账号',
    '配置转发Bot',
    '设置频道映射',
    '配置完成！'
  ]
  return texts[currentStep.value] || ''
})

// 步骤处理
const handleWelcomeComplete = () => {
  currentStep.value = 1
}

const handleAccountComplete = (accountData) => {
  wizardData.value.account = accountData
  currentStep.value = 2
  ElMessage.success('KOOK账号连接成功！')
}

const handleBotComplete = (botData) => {
  wizardData.value.bots = botData
  currentStep.value = 3
  ElMessage.success('Bot配置完成！')
}

const handleMappingComplete = (mappingData) => {
  wizardData.value.mappings = mappingData
  currentStep.value = 4
  ElMessage.success('频道映射设置完成！')
}

const handleFinish = async () => {
  try {
    // 标记设置完成
    await api.post('/api/first-run/mark-completed')
    
    ElMessage.success('🎉 配置完成！正在跳转到主界面...')
    
    // 跳转到主页
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } catch (error) {
    ElMessage.error('保存配置失败：' + error.message)
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}
</script>

<style scoped>
.setup-wizard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.wizard-card {
  width: 100%;
  max-width: 900px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.wizard-header {
  text-align: center;
  padding: 20px 0;
}

.wizard-header h1 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 10px 0;
}

.wizard-header p {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.wizard-content {
  margin: 40px 0;
  min-height: 400px;
}

.step-content {
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

.wizard-footer {
  padding: 20px 0 10px 0;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

:deep(.el-card__footer) {
  background: #f5f7fa;
}
</style>
