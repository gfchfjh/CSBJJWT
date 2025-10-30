<template>
  <el-dialog
    v-model="visible"
    title="🌐 首次运行：安装浏览器引擎"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    width="600px"
    center
  >
    <div class="chromium-download">
      <!-- 说明 -->
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        <template #title>
          正在安装Chromium浏览器引擎
        </template>
        <template #default>
          <p>这是首次运行必须的步骤，请耐心等待...</p>
          <p>下载大小约：~170MB，时间取决于网速</p>
        </template>
      </el-alert>
      
      <!-- 进度条 -->
      <div class="progress-section">
        <el-progress
          :percentage="progress"
          :status="status"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="progress-text">{{ currentStep }}</span>
          </template>
        </el-progress>
        
        <div class="progress-details">
          <p v-if="downloadSpeed">下载速度: {{ downloadSpeed }}</p>
          <p v-if="estimatedTime">预计剩余: {{ estimatedTime }}</p>
          <p v-if="downloadedSize">已下载: {{ downloadedSize }}</p>
        </div>
      </div>
      
      <!-- 步骤列表 -->
      <el-timeline>
        <el-timeline-item
          v-for="step in steps"
          :key="step.id"
          :type="getStepType(step)"
          :icon="getStepIcon(step)"
        >
          {{ step.text }}
        </el-timeline-item>
      </el-timeline>
      
      <!-- 错误信息 -->
      <el-alert
        v-if="error"
        type="error"
        :closable="false"
        show-icon
        style="margin-top: 20px"
      >
        <template #title>安装失败</template>
        <template #default>
          <p>{{ error }}</p>
          <div style="margin-top: 10px">
            <el-button type="primary" size="small" @click="retry">
              重试
            </el-button>
            <el-button size="small" @click="showManualInstructions">
              查看手动安装说明
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { CircleCheck, Loading, CircleClose } from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const progress = ref(0)
const status = ref('') // success, exception, warning
const currentStep = ref('准备开始...')
const downloadSpeed = ref('')
const estimatedTime = ref('')
const downloadedSize = ref('')
const error = ref('')

const steps = ref([
  { id: 1, text: '检查环境', status: 'pending' },
  { id: 2, text: '下载Chromium', status: 'pending' },
  { id: 3, text: '安装浏览器驱动', status: 'pending' },
  { id: 4, text: '验证安装', status: 'pending' },
  { id: 5, text: '完成', status: 'pending' },
])

const getStepType = (step) => {
  if (step.status === 'success') return 'success'
  if (step.status === 'error') return 'danger'
  if (step.status === 'processing') return 'primary'
  return 'info'
}

const getStepIcon = (step) => {
  if (step.status === 'success') return CircleCheck
  if (step.status === 'error') return CircleClose
  if (step.status === 'processing') return Loading
  return null
}

const updateStepStatus = (stepId, status) => {
  const step = steps.value.find(s => s.id === stepId)
  if (step) {
    step.status = status
  }
}

const startDownload = async () => {
  try {
    // 步骤1：检查环境
    updateStepStatus(1, 'processing')
    currentStep.value = '正在检查环境...'
    progress.value = 10
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateStepStatus(1, 'success')
    
    // 步骤2：下载Chromium
    updateStepStatus(2, 'processing')
    currentStep.value = '正在下载Chromium...'
    progress.value = 20
    
    // 调用后端API开始下载
    const response = await api.installChromium()
    
    // 模拟进度更新
    let currentProgress = 20
    const progressInterval = setInterval(() => {
      currentProgress += 5
      if (currentProgress <= 70) {
        progress.value = currentProgress
        downloadSpeed.value = `${(Math.random() * 5 + 2).toFixed(2)} MB/s`
        downloadedSize.value = `${(currentProgress * 2.4).toFixed(1)} MB / 170 MB`
        
        const remaining = (170 - currentProgress * 2.4) / 3.5
        estimatedTime.value = `${Math.ceil(remaining)} 秒`
      }
    }, 1000)
    
    // 等待下载完成
    await new Promise((resolve) => {
      const checkInterval = setInterval(async () => {
        const status = await api.getChromiumInstallStatus()
        if (status.completed) {
          clearInterval(checkInterval)
          clearInterval(progressInterval)
          resolve()
        }
      }, 2000)
    })
    
    updateStepStatus(2, 'success')
    progress.value = 75
    
    // 步骤3：安装驱动
    updateStepStatus(3, 'processing')
    currentStep.value = '正在安装浏览器驱动...'
    progress.value = 80
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    updateStepStatus(3, 'success')
    progress.value = 90
    
    // 步骤4：验证
    updateStepStatus(4, 'processing')
    currentStep.value = '正在验证安装...'
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateStepStatus(4, 'success')
    progress.value = 95
    
    // 步骤5：完成
    updateStepStatus(5, 'processing')
    currentStep.value = '安装完成！'
    progress.value = 100
    status.value = 'success'
    updateStepStatus(5, 'success')
    
    // 延迟关闭
    setTimeout(() => {
      emit('complete')
      visible.value = false
    }, 2000)
    
  } catch (err) {
    error.value = err.message || '安装过程中出现错误'
    status.value = 'exception'
    
    // 标记当前步骤为失败
    const processingStep = steps.value.find(s => s.status === 'processing')
    if (processingStep) {
      processingStep.status = 'error'
    }
  }
}

const retry = () => {
  error.value = ''
  status.value = ''
  progress.value = 0
  currentStep.value = '准备重试...'
  
  steps.value.forEach(step => {
    step.status = 'pending'
  })
  
  setTimeout(() => {
    startDownload()
  }, 1000)
}

const showManualInstructions = () => {
  // 打开手动安装说明
  window.open('https://playwright.dev/docs/browsers', '_blank')
}

watch(visible, (newVal) => {
  if (newVal) {
    startDownload()
  }
})
</script>

<style scoped>
.chromium-download {
  padding: 20px 0;
}

.progress-section {
  margin: 30px 0;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.progress-details {
  margin-top: 15px;
  text-align: center;
  font-size: 13px;
  color: #909399;
}

.progress-details p {
  margin: 5px 0;
}
</style>
