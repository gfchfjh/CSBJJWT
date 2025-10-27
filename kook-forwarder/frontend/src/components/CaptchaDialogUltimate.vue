<template>
  <el-dialog
    v-model="visible"
    title="🔐 验证码识别"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @open="onDialogOpen"
    @close="onDialogClose"
  >
    <div class="captcha-container">
      <!-- 大图预览（300x150px） -->
      <div class="captcha-image-wrapper" @click="refreshCaptcha">
        <el-image
          :src="captchaImage"
          fit="contain"
          class="captcha-image-large"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <p>加载失败，点击刷新</p>
            </div>
          </template>
        </el-image>
        <div class="click-hint">点击图片可刷新</div>
      </div>
      
      <!-- 倒计时进度条（120秒） -->
      <el-progress
        :percentage="timeLeftPercentage"
        :color="progressColor"
        :stroke-width="12"
        :format="formatTime"
        class="captcha-progress"
      />
      
      <!-- 输入框（自动聚焦） -->
      <el-input
        ref="captchaInputRef"
        v-model="captchaCode"
        placeholder="请输入验证码"
        size="large"
        class="captcha-input"
        maxlength="6"
        clearable
        @keyup.enter="submitCaptcha"
      >
        <template #prefix>
          <el-icon><Key /></el-icon>
        </template>
      </el-input>
      
      <!-- 动态提示（倒计时<30秒时显示） -->
      <el-alert
        v-if="timeLeft < 30"
        type="warning"
        :closable="false"
        show-icon
        class="warning-alert"
      >
        <template #title>
          <span class="blink">⚠️ 验证码即将过期，请尽快输入！</span>
        </template>
      </el-alert>
      
      <!-- 操作按钮 -->
      <div class="button-group">
        <el-button @click="refreshCaptcha" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          看不清？刷新
        </el-button>
        <el-button
          type="primary"
          @click="submitCaptcha"
          :disabled="!captchaCode || submitting"
          :loading="submitting"
        >
          <el-icon><Check /></el-icon>
          提交验证码
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, Key, Refresh, Check } from '@element-plus/icons-vue'
import { useWebSocketEnhanced } from '@/composables/useWebSocketEnhanced'
import api from '@/api'

const TIMEOUT = 120 // 120秒

const visible = ref(false)
const captchaImage = ref('')
const captchaCode = ref('')
const timeLeft = ref(TIMEOUT)
const refreshing = ref(false)
const submitting = ref(false)
const captchaInputRef = ref(null)
let timer = null

// WebSocket实时接收验证码推送
const { subscribe, unsubscribe } = useWebSocketEnhanced()

const captchaHandler = (data) => {
  console.log('✨ 收到验证码推送:', data)
  captchaImage.value = `data:image/png;base64,${data.image_base64}`
  visible.value = true
  startTimer()
}

// 订阅验证码事件
subscribe('captcha_required', captchaHandler)

// 计算属性
const timeLeftPercentage = computed(() => (timeLeft.value / TIMEOUT) * 100)

const progressColor = computed(() => {
  if (timeLeft.value > 60) return '#67C23A'
  if (timeLeft.value > 30) return '#E6A23C'
  return '#F56C6C'
})

const formatTime = () => {
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  if (minutes > 0) {
    return `${minutes}分${seconds}秒`
  }
  return `${seconds}秒`
}

// 方法
const startTimer = () => {
  clearInterval(timer)
  timeLeft.value = TIMEOUT
  
  timer = setInterval(() => {
    timeLeft.value--
    
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      ElMessage.error('验证码已过期，请刷新')
      captchaCode.value = ''
    }
  }, 1000)
}

const refreshCaptcha = async () => {
  if (refreshing.value) return
  
  refreshing.value = true
  
  try {
    const response = await api.post('/api/captcha/refresh')
    
    if (response.data.image_base64) {
      captchaImage.value = `data:image/png;base64,${response.data.image_base64}`
      ElMessage.success('验证码已刷新')
      startTimer()
      captchaCode.value = ''
      
      // 刷新后自动聚焦输入框
      nextTick(() => {
        captchaInputRef.value?.focus()
      })
    }
  } catch (error) {
    console.error('刷新验证码失败:', error)
    ElMessage.error('刷新验证码失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    refreshing.value = false
  }
}

const submitCaptcha = async () => {
  if (!captchaCode.value || submitting.value) return
  
  submitting.value = true
  
  try {
    await api.post('/api/captcha/submit', {
      code: captchaCode.value
    })
    
    ElMessage.success('✅ 验证码提交成功')
    visible.value = false
    captchaCode.value = ''
    clearInterval(timer)
  } catch (error) {
    console.error('验证码提交失败:', error)
    
    const errorMsg = error.response?.data?.detail || error.message
    
    if (errorMsg.includes('验证码错误') || errorMsg.includes('incorrect')) {
      ElMessage.error('❌ 验证码错误，请重新输入')
      captchaCode.value = ''
      
      // 自动聚焦输入框
      nextTick(() => {
        captchaInputRef.value?.focus()
      })
    } else {
      ElMessage.error('提交失败: ' + errorMsg)
    }
  } finally {
    submitting.value = false
  }
}

const onDialogOpen = () => {
  // 对话框打开时自动聚焦输入框
  nextTick(() => {
    captchaInputRef.value?.focus()
  })
}

const onDialogClose = () => {
  // 清理定时器
  clearInterval(timer)
  captchaCode.value = ''
}

// 组件卸载时清理
onUnmounted(() => {
  clearInterval(timer)
  unsubscribe('captcha_required', captchaHandler)
})

// 监听visible变化
watch(visible, (val) => {
  if (val) {
    onDialogOpen()
  } else {
    onDialogClose()
  }
})
</script>

<style scoped>
.captcha-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.captcha-image-wrapper {
  position: relative;
  width: 300px;
  height: 150px;
  margin: 0 auto;
  cursor: pointer;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.captcha-image-wrapper:hover {
  border-color: #409eff;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.captcha-image-large {
  width: 100%;
  height: 100%;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.image-error .el-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.click-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  text-align: center;
  padding: 5px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.captcha-image-wrapper:hover .click-hint {
  opacity: 1;
}

.captcha-progress {
  margin: 10px 0;
}

.captcha-input {
  font-size: 18px;
  letter-spacing: 4px;
}

.captcha-input :deep(.el-input__inner) {
  text-align: center;
  font-weight: bold;
}

.warning-alert {
  margin: 10px 0;
}

.blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50%, 100% {
    opacity: 1;
  }
  25%, 75% {
    opacity: 0.5;
  }
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
}

.button-group .el-button {
  flex: 1;
}

/* 暗黑模式支持 */
.dark .captcha-image-wrapper {
  border-color: #4c4d4f;
}

.dark .captcha-image-wrapper:hover {
  border-color: #409eff;
}
</style>
