<template>
  <el-dialog
    v-model="visible"
    title="🔢 请输入验证码"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    class="captcha-dialog"
  >
    <!-- 验证码图片 -->
    <div class="captcha-image-container">
      <el-image
        v-if="captchaImageUrl"
        :src="captchaImageUrl"
        fit="contain"
        class="captcha-image"
        :class="{ 'is-loading': refreshing }"
      >
        <template #placeholder>
          <div class="image-placeholder">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
        </template>
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
            <span>图片加载失败</span>
          </div>
        </template>
      </el-image>
      
      <el-button
        class="refresh-button"
        circle
        size="large"
        :loading="refreshing"
        @click="refreshCaptcha"
      >
        <el-icon><RefreshRight /></el-icon>
      </el-button>
    </div>

    <!-- 输入框 -->
    <div class="input-container">
      <el-input
        ref="captchaInput"
        v-model="captchaCode"
        size="large"
        placeholder="请输入验证码"
        clearable
        maxlength="6"
        @keyup.enter="submitCaptcha"
      >
        <template #prefix>
          <el-icon><Key /></el-icon>
        </template>
      </el-input>
      
      <div class="input-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>请输入图片中的验证码（不区分大小写）</span>
      </div>
    </div>

    <!-- 倒计时提示 -->
    <div class="countdown-container">
      <el-progress
        :percentage="countdownPercentage"
        :color="countdownColor"
        :show-text="false"
        :stroke-width="4"
      />
      <div class="countdown-text">
        <el-icon><Timer /></el-icon>
        <span>剩余时间：{{ remainingSeconds }} 秒</span>
      </div>
    </div>

    <!-- 自动识别状态 -->
    <div v-if="autoRecognizing" class="auto-recognize-status">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        <template #title>
          <div class="recognize-title">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在自动识别验证码...</span>
          </div>
        </template>
        <p>使用2Captcha或本地OCR自动识别中，识别失败会切换到手动输入</p>
      </el-alert>
    </div>

    <!-- 操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button
          size="large"
          @click="cancelCaptcha"
        >
          取消登录
        </el-button>
        <el-button
          type="primary"
          size="large"
          :disabled="!captchaCode || captchaCode.length < 4"
          :loading="submitting"
          @click="submitCaptcha"
        >
          <el-icon><Check /></el-icon>
          确认提交
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

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
    default: ''
  },
  timeout: {
    type: Number,
    default: 120 // 默认120秒
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel', 'timeout'])

// WebSocket连接
let ws = null

// 状态
const captchaCode = ref('')
const captchaImageUrl = ref('')
const submitting = ref(false)
const refreshing = ref(false)
const autoRecognizing = ref(false)
const remainingSeconds = ref(props.timeout)
const captchaInput = ref(null)

// 倒计时定时器
let countdownTimer = null

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 倒计时百分比
const countdownPercentage = computed(() => {
  return (remainingSeconds.value / props.timeout) * 100
})

// 倒计时颜色
const countdownColor = computed(() => {
  const percentage = countdownPercentage.value
  if (percentage > 50) return '#67c23a'
  if (percentage > 20) return '#e6a23c'
  return '#f56c6c'
})

// 初始化WebSocket连接
const initWebSocket = () => {
  if (ws) {
    ws.close()
  }

  const wsUrl = `ws://localhost:9527/ws/captcha/${props.accountId}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('✅ 验证码WebSocket已连接')
    // 发送心跳
    startHeartbeat()
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    } catch (error) {
      console.error('解析WebSocket消息失败:', error)
    }
  }

  ws.onerror = (error) => {
    console.error('验证码WebSocket错误:', error)
    ElMessage.error('验证码连接失败，请刷新页面重试')
  }

  ws.onclose = () => {
    console.log('验证码WebSocket已断开')
    stopHeartbeat()
  }
}

// 处理WebSocket消息
const handleWebSocketMessage = (data) => {
  console.log('收到WebSocket消息:', data)

  switch (data.type) {
    case 'captcha_required':
      // 收到验证码请求
      captchaImageUrl.value = data.data?.image_url || ''
      autoRecognizing.value = data.data?.auto_recognizing || false
      startCountdown()
      break

    case 'captcha_received':
      // 验证码已接收确认
      if (data.success) {
        ElMessage.success('验证码已提交')
      }
      break

    case 'refresh_result':
      // 刷新验证码结果
      refreshing.value = false
      if (data.success) {
        captchaImageUrl.value = data.image_url
        captchaCode.value = ''
      } else {
        ElMessage.warning(data.message || '刷新失败')
      }
      break

    case 'pong':
      // 心跳响应
      break

    default:
      console.log('未知消息类型:', data.type)
  }
}

// 心跳定时器
let heartbeatTimer = null

const startHeartbeat = () => {
  heartbeatTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000) // 每30秒发送一次心跳
}

const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

// 开始倒计时
const startCountdown = () => {
  remainingSeconds.value = props.timeout

  if (countdownTimer) {
    clearInterval(countdownTimer)
  }

  countdownTimer = setInterval(() => {
    remainingSeconds.value--

    if (remainingSeconds.value <= 0) {
      clearInterval(countdownTimer)
      handleTimeout()
    }
  }, 1000)
}

// 超时处理
const handleTimeout = () => {
  ElMessage.warning('验证码输入超时')
  emit('timeout')
  close()
}

// 刷新验证码
const refreshCaptcha = () => {
  refreshing.value = true
  captchaCode.value = ''
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'refresh_captcha'
    }))
  } else {
    ElMessage.error('WebSocket未连接')
    refreshing.value = false
  }
}

// 提交验证码
const submitCaptcha = () => {
  if (!captchaCode.value || captchaCode.value.length < 4) {
    ElMessage.warning('请输入完整的验证码')
    return
  }

  submitting.value = true

  // 通过WebSocket发送验证码
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'captcha_input',
      code: captchaCode.value
    }))

    emit('submit', captchaCode.value)
    
    // 延迟关闭，等待后端处理
    setTimeout(() => {
      submitting.value = false
      close()
    }, 1000)
  } else {
    ElMessage.error('WebSocket未连接，无法提交验证码')
    submitting.value = false
  }
}

// 取消验证码
const cancelCaptcha = () => {
  emit('cancel')
  close()
}

// 关闭对话框
const close = () => {
  // 清理定时器
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }

  // 关闭WebSocket
  if (ws) {
    ws.close()
    ws = null
  }

  visible.value = false
  captchaCode.value = ''
  captchaImageUrl.value = ''
  autoRecognizing.value = false
}

// 监听对话框打开
watch(visible, async (newVal) => {
  if (newVal) {
    // 对话框打开
    captchaImageUrl.value = props.imageUrl
    initWebSocket()
    startCountdown()
    
    // 自动聚焦输入框
    await nextTick()
    if (captchaInput.value) {
      captchaInput.value.focus()
    }
  } else {
    // 对话框关闭，清理资源
    close()
  }
})

onMounted(() => {
  if (visible.value) {
    captchaImageUrl.value = props.imageUrl
    initWebSocket()
    startCountdown()
  }
})

onUnmounted(() => {
  close()
})
</script>

<style scoped>
.captcha-dialog {
  --el-dialog-padding-primary: 24px;
}

.captcha-image-container {
  position: relative;
  width: 100%;
  height: 180px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.captcha-image {
  width: 100%;
  height: 100%;
  background-color: white;
}

.captcha-image.is-loading {
  opacity: 0.5;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
}

.image-placeholder,
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #909399;
}

.image-placeholder .el-icon,
.image-error .el-icon {
  font-size: 48px;
}

.refresh-button {
  position: absolute;
  top: 12px;
  right: 12px;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

.refresh-button:hover {
  background-color: white;
  transform: rotate(180deg);
  transition: all 0.3s;
}

.input-container {
  margin-bottom: 20px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.countdown-container {
  margin-bottom: 20px;
}

.countdown-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.auto-recognize-status {
  margin-bottom: 20px;
}

.recognize-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.dialog-footer .el-button {
  flex: 1;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .captcha-image-container {
    background: linear-gradient(135deg, #434343 0%, #000000 100%);
  }
}
</style>
