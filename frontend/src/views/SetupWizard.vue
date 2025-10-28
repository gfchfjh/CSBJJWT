<template>
  <div class="setup-wizard">
    <div class="wizard-header">
      <h1>🎉 欢迎使用KOOK消息转发系统</h1>
      <p class="subtitle">3步快速配置，4分钟即可开始使用</p>
    </div>

    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" finish-status="success" align-center class="steps-bar">
      <el-step title="登录KOOK" description="1分钟">
        <template #icon>
          <el-icon><User /></el-icon>
        </template>
      </el-step>
      <el-step title="配置Bot" description="2分钟">
        <template #icon>
          <el-icon><Connection /></el-icon>
        </template>
      </el-step>
      <el-step title="智能映射" description="1分钟">
        <template #icon>
          <el-icon><MagicStick /></el-icon>
        </template>
      </el-step>
    </el-steps>

    <!-- 步骤内容 -->
    <el-card class="wizard-content" shadow="never">
      <!-- 步骤1: 登录KOOK -->
      <Step1Login
        v-if="currentStep === 0"
        @next="handleStep1Complete"
        @skip="handleSkipWizard"
      />

      <!-- 步骤2: 配置Bot -->
      <Step2BotConfig
        v-else-if="currentStep === 1"
        :account-id="accountId"
        @next="handleStep2Complete"
        @prev="currentStep = 0"
      />

      <!-- 步骤3: AI智能映射 -->
      <Step3SmartMapping
        v-else-if="currentStep === 2"
        :account-id="accountId"
        :bot-configs="botConfigs"
        @complete="handleWizardComplete"
        @prev="currentStep = 1"
      />
    </el-card>

    <!-- 底部提示 -->
    <div class="wizard-footer">
      <el-alert
        title="提示：所有配置稍后都可以在设置页面修改"
        type="info"
        :closable="false"
        show-icon
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Connection, MagicStick } from '@element-plus/icons-vue'
import Step1Login from '@/components/wizard/Step1Login.vue'
import Step2BotConfig from '@/components/wizard/Step2BotConfig.vue'
import Step3SmartMapping from '@/components/wizard/Step3SmartMapping.vue'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 步骤间传递的数据
const accountId = ref(null)
const botConfigs = ref([])

// 步骤1完成
const handleStep1Complete = (data) => {
  accountId.value = data.accountId
  currentStep.value = 1
  
  ElMessage.success({
    message: '✅ 登录成功！继续配置Bot...',
    duration: 2000
  })
}

// 步骤2完成
const handleStep2Complete = (data) => {
  botConfigs.value = data.botConfigs
  currentStep.value = 2
  
  ElMessage.success({
    message: `✅ 已配置${data.botConfigs.length}个Bot！开始智能映射...`,
    duration: 2000
  })
}

// 向导完成
const handleWizardComplete = async (data) => {
  try {
    // 标记向导已完成
    await api.post('/api/system/config', {
      key: 'wizard_completed',
      value: 'true'
    })
    
    ElMessage.success({
      message: '🎉 配置完成！正在启动服务...',
      duration: 2000
    })
    
    // 跳转到主页
    setTimeout(() => {
      router.push('/')
    }, 2000)
    
  } catch (error) {
    console.error('标记向导完成失败:', error)
    // 即使失败也跳转
    router.push('/')
  }
}

// 跳过向导
const handleSkipWizard = async () => {
  try {
    await ElMessageBox.confirm(
      '跳过向导后需要手动配置账号、Bot和映射关系。确定跳过吗？',
      '确认跳过',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续配置',
        type: 'warning'
      }
    )
    
    router.push('/')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.setup-wizard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.wizard-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.wizard-header h1 {
  font-size: 36px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.wizard-header .subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
}

.steps-bar {
  max-width: 800px;
  margin: 0 auto 40px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.wizard-content {
  max-width: 900px;
  margin: 0 auto;
  border-radius: 12px;
  min-height: 500px;
}

.wizard-content :deep(.el-card__body) {
  padding: 40px;
}

.wizard-footer {
  max-width: 900px;
  margin: 20px auto 0;
}

/* 深色主题适配 */
.dark .setup-wizard {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.dark .steps-bar {
  background: #1e1e1e;
}
</style>
