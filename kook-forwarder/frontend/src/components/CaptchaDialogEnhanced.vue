<template>
  <el-dialog
    v-model="visible"
    title=""
    :width="550"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    class="captcha-dialog"
  >
    <!-- ✅ P0-4优化: 美观的验证码输入对话框 -->
    <div class="captcha-container">
      <!-- 标题 -->
      <div class="captcha-header">
        <el-icon :size="50" color="#409EFF">
          <Lock />
        </el-icon>
        <h2>需要验证码</h2>
        <p>请输入下方图片中的验证码</p>
      </div>

      <!-- 验证码图片预览 -->
      <div class="captcha-image-container">
        <el-image
          v-if="imageUrl"
          :src="imageUrl"
          fit="contain"
          class="captcha-image"
          :preview-src-list="[imageUrl]"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>验证码加载失败</span>
            </div>
          </template>
          <template #placeholder>
            <div class="image-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
          </template>
        </el-image>

        <div v-else class="no-image">
          <el-icon><Warning /></el-icon>
          <span>暂无验证码图片</span>
        </div>

        <!-- 刷新按钮 -->
        <el-button
          class="refresh-button"
          circle
          @click="refreshCaptcha"
          :loading="refreshing"
          :disabled="refreshing"
        >
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>

      <!-- 验证码输入 -->
      <div class="captcha-input-container">
        <el-input
          ref="captchaInput"
          v-model="captchaCode"
          placeholder="请输入验证码"
          size="large"
          clearable
          maxlength="10"
          @keyup.enter="submitCaptcha"
          :disabled="submitting"
        >
          <template #prefix>
            <el-icon><Key /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 倒计时进度条 -->
      <div class="countdown-container">
        <div class="countdown-header">
          <span class="countdown-label">
            <el-icon><Timer /></el-icon>
            剩余时间
          </span>
          <span class="countdown-time" :class="{ 'time-warning': remainingTime < 30 }">
            {{ formatTime(remainingTime) }}
          </span>
        </div>

        <el-progress
          :percentage="timePercentage"
          :color="progressColor"
          :show-text="false"
          :stroke-width="12"
        />

        <p v-if="remainingTime < 30" class="timeout-warning">
          <el-icon><Warning /></el-icon>
          验证码即将超时，请尽快输入
        </p>
      </div>

      <!-- 提示信息 -->
      <el-alert
        v-if="errorMessage"
        type="error"
        :closable="false"
        show-icon
        class="error-alert"
      >
        {{ errorMessage }}
      </el-alert>

      <el-alert
        v-else
        type="info"
        :closable="false"
        show-icon
        class="info-alert"
      >
        <ul class="tips-list">
          <li>请仔细辨认验证码中的字符</li>
          <li>不区分大小写</li>
          <li>输入完成后按回车或点击提交</li>
        </ul>
      </el-alert>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button
          size="large"
          @click="handleCancel"
          :disabled="submitting"
        >
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          @click="submitCaptcha"
          :loading="submitting"
          :disabled="!captchaCode || submitting"
        >
          <el-icon v-if="!submitting"><Check /></el-icon>
          {{ submitting ? '提交中...' : '提交' }}
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Lock, Picture, Loading, Warning, Refresh, Key, Timer, Check
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  accountId: {
    type: Number,
    required: true
  },
  imageUrl: {
    type: String,
    required: true
  },
  timeout: {
    type: Number,
    default: 120
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel', 'timeout', 'refresh'])

// 对话框显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 验证码输入
const captchaCode = ref('')
const captchaInput = ref(null)

// 状态
const submitting = ref(false)
const refreshing = ref(false)
const errorMessage = ref('')

// 倒计时
const remainingTime = ref(props.timeout)
const startTime = ref(Date.now())
let countdownTimer = null

// 计算属性
const timePercentage = computed(() => {
  return (remainingTime.value / props.timeout) * 100
})

const progressColor = computed(() => {
  if (remainingTime.value < 30) return '#F56C6C'
  if (remainingTime.value < 60) return '#E6A23C'
  return '#409EFF'
})

// 格式化时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 启动倒计时
const startCountdown = () => {
  stopCountdown()
  
  countdownTimer = setInterval(() => {
    remainingTime.value--
    
    if (remainingTime.value <= 0) {
      stopCountdown()
      handleTimeout()
    }
  }, 1000)
}

// 停止倒计时
const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// 刷新验证码
const refreshCaptcha = async () => {
  refreshing.value = true
  errorMessage.value = ''
  
  try {
    emit('refresh')
    
    // 重置倒计时
    remainingTime.value = props.timeout
    startTime.value = Date.now()
    
    ElMessage.success('验证码已刷新')
  } catch (error) {
    ElMessage.error('刷新验证码失败: ' + error.message)
    errorMessage.value = '刷新失败，请重试'
  } finally {
    refreshing.value = false
  }
}

// 提交验证码
const submitCaptcha = async () => {
  if (!captchaCode.value || submitting.value) {
    return
  }
  
  submitting.value = true
  errorMessage.value = ''
  
  try {
    emit('submit', captchaCode.value)
    
    ElMessage.success('验证码已提交')
    
    // 提交成功后关闭对话框
    setTimeout(() => {
      visible.value = false
    }, 500)
  } catch (error) {
    ElMessage.error('提交失败: ' + error.message)
    errorMessage.value = error.message || '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}

// 取消
const handleCancel = () => {
  stopCountdown()
  emit('cancel')
  visible.value = false
}

// 超时处理
const handleTimeout = () => {
  ElMessage.error('验证码已超时')
  errorMessage.value = '验证码已超时，请刷新后重试'
  emit('timeout')
}

// 监听对话框打开
watch(visible, (newVal) => {
  if (newVal) {
    // 对话框打开时
    captchaCode.value = ''
    errorMessage.value = ''
    remainingTime.value = props.timeout
    startTime.value = Date.now()
    
    // 启动倒计时
    startCountdown()
    
    // 自动聚焦到输入框
    nextTick(() => {
      if (captchaInput.value) {
        captchaInput.value.focus()
      }
    })
  } else {
    // 对话框关闭时
    stopCountdown()
  }
})

// 生命周期
onMounted(() => {
  if (visible.value) {
    startCountdown()
  }
})

onBeforeUnmount(() => {
  stopCountdown()
})
</script>

<style scoped lang="scss">
.captcha-dialog {
  :deep(.el-dialog__header) {
    display: none;
  }

  :deep(.el-dialog__body) {
    padding: 30px;
  }
}

.captcha-container {
  text-align: center;
}

.captcha-header {
  margin-bottom: 30px;
  
  h2 {
    font-size: 24px;
    margin: 15px 0 10px;
    color: #303133;
  }
  
  p {
    color: #909399;
    font-size: 14px;
  }
}

.captcha-image-container {
  position: relative;
  background: #F5F7FA;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  border: 2px solid #DCDFE6;
  
  .captcha-image {
    width: 100%;
    max-height: 200px;
    border-radius: 8px;
  }
  
  .image-error,
  .image-loading,
  .no-image {
    height: 150px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #909399;
    
    .el-icon {
      font-size: 48px;
    }
  }
  
  .refresh-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(5px);
    
    &:hover {
      background: #409EFF;
      color: white;
      transform: rotate(180deg);
      transition: all 0.3s;
    }
  }
}

.captcha-input-container {
  margin-bottom: 25px;
  
  .el-input {
    font-size: 18px;
    
    :deep(.el-input__inner) {
      text-align: center;
      letter-spacing: 3px;
      font-weight: 600;
    }
  }
}

.countdown-container {
  margin-bottom: 20px;
  
  .countdown-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .countdown-label {
      display: flex;
      align-items: center;
      gap: 5px;
      color: #606266;
      font-weight: 600;
    }
    
    .countdown-time {
      font-size: 20px;
      font-weight: 700;
      font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
      color: #409EFF;
      
      &.time-warning {
        color: #F56C6C;
        animation: blink 1s infinite;
      }
    }
  }
  
  .timeout-warning {
    margin-top: 10px;
    color: #F56C6C;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    animation: shake 0.5s;
  }
}

.error-alert,
.info-alert {
  margin-bottom: 20px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  text-align: left;
  line-height: 1.8;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  
  .el-button {
    flex: 1;
    max-width: 200px;
  }
}

/* 动画 */
@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}
</style>
