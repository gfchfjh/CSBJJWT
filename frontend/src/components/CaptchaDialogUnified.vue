<template>
  <el-dialog
    v-model="visible"
    title="🔐 需要输入验证码"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    @open="onOpen"
    class="captcha-dialog"
  >
    <div class="captcha-container">
      <!-- 倒计时提示 -->
      <el-alert 
        v-if="countdown > 0 && countdown <= 10"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #title>
          <span class="countdown-text">
            <el-icon class="is-loading"><Loading /></el-icon>
            验证码将在 <strong>{{ countdown }}</strong> 秒后过期
          </span>
        </template>
      </el-alert>
      
      <!-- 验证码图片 -->
      <div class="captcha-image-wrapper" @click="enlargeImage">
        <el-image
          :src="captchaImageSrc"
          :preview-src-list="[captchaImageSrc]"
          fit="contain"
          class="captcha-image"
          :class="{ 'enlarged': isEnlarged }"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>图片加载失败</span>
            </div>
          </template>
        </el-image>
        
        <!-- 刷新按钮 -->
        <el-button
          :icon="RefreshRight"
          circle
          class="refresh-btn"
          @click.stop="refreshCaptcha"
          :loading="refreshing"
          title="刷新验证码"
        />
        
        <!-- 放大提示 -->
        <div class="enlarge-hint">
          <el-icon><ZoomIn /></el-icon>
          点击图片放大
        </div>
      </div>
      
      <!-- 自动识别进度 -->
      <el-card v-if="autoSolveEnabled && autoSolveProgress > 0" shadow="never" class="auto-solve-card">
        <template #header>
          <div class="card-header">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在自动识别验证码...</span>
          </div>
        </template>
        
        <el-progress 
          :percentage="autoSolveProgress"
          :status="autoSolveStatus"
          striped
          striped-flow
        >
          <template #default="{ percentage }">
            <span class="progress-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        
        <div v-if="autoSolveResult" class="auto-solve-result">
          <el-icon color="#67C23A"><SuccessFilled /></el-icon>
          <span>识别结果：<strong>{{ autoSolveResult }}</strong></span>
          <el-button size="small" @click="useAutoSolveResult">使用此结果</el-button>
        </div>
      </el-card>
      
      <!-- 输入框 -->
      <div class="captcha-input-wrapper">
        <el-input
          ref="captchaInputRef"
          v-model="captchaCode"
          placeholder="请输入验证码"
          size="large"
          maxlength="6"
          clearable
          @keyup.enter="submitCaptcha"
          @input="handleInput"
          class="captcha-input"
        >
          <template #prefix>
            <el-icon><Key /></el-icon>
          </template>
          
          <template #suffix>
            <el-tag v-if="captchaCode.length > 0" size="small">
              {{ captchaCode.length }}/6
            </el-tag>
          </template>
        </el-input>
        
        <!-- 输入提示 -->
        <div class="input-hints">
          <el-icon><InfoFilled /></el-icon>
          <span>通常为4-6位字母或数字</span>
        </div>
      </div>
      
      <!-- 历史记录（可选） -->
      <el-collapse v-if="historyEnabled && captchaHistory.length > 0" class="history-collapse">
        <el-collapse-item title="历史记录" name="history">
          <div class="history-list">
            <div 
              v-for="(item, index) in captchaHistory" 
              :key="index"
              class="history-item"
              @click="useCaptchaFromHistory(item)"
            >
              <el-image :src="item.image" fit="cover" class="history-image" />
              <div class="history-info">
                <div class="history-code">{{ item.code }}</div>
                <div class="history-time">{{ formatTime(item.timestamp) }}</div>
              </div>
              <el-tag 
                :type="item.success ? 'success' : 'danger'"
                size="small"
              >
                {{ item.success ? '成功' : '失败' }}
              </el-tag>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-checkbox v-model="enableAutoSolve" @change="toggleAutoSolve">
            使用自动识别
          </el-checkbox>
          
          <el-popover
            placement="top"
            :width="300"
            trigger="hover"
          >
            <template #reference>
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </template>
            <div class="help-content">
              <p><strong>自动识别说明：</strong></p>
              <ul>
                <li>使用2Captcha服务自动识别验证码</li>
                <li>需要在设置中配置API Key</li>
                <li>识别成功后会自动填入</li>
                <li>识别失败时需手动输入</li>
              </ul>
            </div>
          </el-popover>
        </div>
        
        <div class="footer-right">
          <el-button @click="cancel" :disabled="submitting">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="submitCaptcha"
            :loading="submitting"
            :disabled="!captchaCode || captchaCode.length < 4"
          >
            {{ submitting ? '提交中...' : '提交' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Loading, RefreshRight, ZoomIn, Picture, Key, SuccessFilled,
  InfoFilled, QuestionFilled
} from '@element-plus/icons-vue'
import axios from 'axios'

// Props
const props = defineProps({
  historyEnabled: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['submit', 'cancel'])

// Refs
const visible = ref(false)
const captchaImageSrc = ref('')
const captchaCode = ref('')
const captchaInputRef = ref(null)
const countdown = ref(60)
const submitting = ref(false)
const refreshing = ref(false)
const isEnlarged = ref(false)

// Auto solve
const enableAutoSolve = ref(false)
const autoSolveEnabled = ref(false)
const autoSolveProgress = ref(0)
const autoSolveStatus = ref('')
const autoSolveResult = ref('')

// History
const captchaHistory = ref([])

// Timer
let countdownTimer = null
let autoSolveTimer = null

// 对话框打开
function onOpen() {
  // 聚焦输入框
  nextTick(() => {
    captchaInputRef.value?.focus()
  })
  
  // 启动倒计时
  startCountdown()
  
  // 显示桌面通知
  showDesktopNotification()
  
  // 尝试自动识别
  if (autoSolveEnabled.value) {
    tryAutoSolve()
  }
}

// 显示验证码对话框
async function show(options = {}) {
  visible.value = true
  captchaImageSrc.value = options.image || ''
  countdown.value = options.timeout || 60
  autoSolveEnabled.value = options.autoSolve || false
  
  // 重置状态
  captchaCode.value = ''
  autoSolveProgress.value = 0
  autoSolveResult.value = ''
  submitting.value = false
}

// 启动倒计时
function startCountdown() {
  clearInterval(countdownTimer)
  
  countdownTimer = setInterval(() => {
    countdown.value--
    
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      handleTimeout()
    }
  }, 1000)
}

// 超时处理
function handleTimeout() {
  ElNotification.warning({
    title: '验证码输入超时',
    message: '请刷新验证码后重新尝试',
    duration: 5000
  })
  
  // 自动刷新验证码
  refreshCaptcha()
}

// 显示桌面通知
function showDesktopNotification() {
  if (!('Notification' in window)) {
    return
  }
  
  if (Notification.permission === 'granted') {
    const notification = new Notification('需要输入验证码', {
      body: '请在窗口中输入验证码以继续登录',
      icon: '/icon.png',
      badge: '/icon.png',
      tag: 'captcha-required',
      requireInteraction: true
    })
    
    notification.onclick = () => {
      window.focus()
      notification.close()
    }
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        showDesktopNotification()
      }
    })
  }
}

// 刷新验证码
async function refreshCaptcha() {
  refreshing.value = true
  
  try {
    const response = await axios.post('/api/auth/refresh-captcha')
    
    if (response.data.success) {
      captchaImageSrc.value = response.data.image
      countdown.value = 60
      
      // 重启倒计时
      startCountdown()
      
      ElMessage.success('验证码已刷新')
    } else {
      ElMessage.error('验证码刷新失败')
    }
  } catch (error) {
    ElMessage.error('验证码刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

// 放大图片
function enlargeImage() {
  isEnlarged.value = !isEnlarged.value
}

// 输入处理
function handleInput(value) {
  // 自动转大写
  captchaCode.value = value.toUpperCase()
}

// 尝试自动识别
async function tryAutoSolve() {
  autoSolveProgress.value = 0
  autoSolveStatus.value = ''
  autoSolveResult.value = ''
  
  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (autoSolveProgress.value < 90) {
        autoSolveProgress.value += 10
      }
    }, 500)
    
    // 调用识别API
    const response = await axios.post('/api/captcha/auto-solve', {
      image: captchaImageSrc.value
    })
    
    clearInterval(progressInterval)
    
    if (response.data.success) {
      autoSolveProgress.value = 100
      autoSolveStatus.value = 'success'
      autoSolveResult.value = response.data.code
      
      ElNotification.success({
        title: '自动识别成功',
        message: `识别结果：${response.data.code}`,
        duration: 3000
      })
      
      // 自动填入
      captchaCode.value = response.data.code
      
    } else {
      autoSolveProgress.value = 100
      autoSolveStatus.value = 'exception'
      
      ElNotification.warning({
        title: '自动识别失败',
        message: response.data.message || '请手动输入验证码',
        duration: 3000
      })
    }
    
  } catch (error) {
    autoSolveProgress.value = 100
    autoSolveStatus.value = 'exception'
    
    console.error('自动识别异常:', error)
    
    ElNotification.error({
      title: '自动识别异常',
      message: error.message,
      duration: 3000
    })
  }
}

// 使用自动识别结果
function useAutoSolveResult() {
  captchaCode.value = autoSolveResult.value
  captchaInputRef.value?.focus()
}

// 切换自动识别
function toggleAutoSolve(value) {
  if (value && !autoSolveResult.value) {
    tryAutoSolve()
  }
}

// 提交验证码
async function submitCaptcha() {
  if (!captchaCode.value || captchaCode.value.length < 4) {
    ElMessage.warning('请输入验证码（至少4位）')
    return
  }
  
  submitting.value = true
  
  try {
    // 触发提交事件
    emit('submit', {
      code: captchaCode.value,
      timestamp: Date.now()
    })
    
    // 保存到历史
    saveCaptchaToHistory(captchaCode.value, true)
    
    // 关闭对话框
    close()
    
  } catch (error) {
    ElMessage.error('提交失败: ' + error.message)
    
    // 保存到历史（失败）
    saveCaptchaToHistory(captchaCode.value, false)
    
  } finally {
    submitting.value = false
  }
}

// 取消
function cancel() {
  emit('cancel')
  close()
}

// 关闭对话框
function close() {
  visible.value = false
  clearInterval(countdownTimer)
  clearInterval(autoSolveTimer)
  
  // 重置状态
  captchaCode.value = ''
  countdown.value = 60
  autoSolveProgress.value = 0
  autoSolveResult.value = ''
}

// 保存到历史
function saveCaptchaToHistory(code, success) {
  if (!props.historyEnabled) return
  
  const historyItem = {
    image: captchaImageSrc.value,
    code,
    success,
    timestamp: Date.now()
  }
  
  captchaHistory.value.unshift(historyItem)
  
  // 只保留最近10条
  if (captchaHistory.value.length > 10) {
    captchaHistory.value = captchaHistory.value.slice(0, 10)
  }
  
  // 保存到localStorage
  try {
    localStorage.setItem('captcha_history', JSON.stringify(captchaHistory.value))
  } catch (error) {
    console.error('保存历史失败:', error)
  }
}

// 从历史使用验证码
function useCaptchaFromHistory(item) {
  captchaCode.value = item.code
  captchaInputRef.value?.focus()
}

// 格式化时间
function formatTime(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString()
  }
}

// 生命周期
onMounted(() => {
  // 加载历史
  if (props.historyEnabled) {
    try {
      const history = localStorage.getItem('captcha_history')
      if (history) {
        captchaHistory.value = JSON.parse(history)
      }
    } catch (error) {
      console.error('加载历史失败:', error)
    }
  }
  
  // 请求桌面通知权限
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
})

onUnmounted(() => {
  clearInterval(countdownTimer)
  clearInterval(autoSolveTimer)
})

// 暴露方法
defineExpose({
  show,
  close
})
</script>

<style scoped>
.captcha-dialog {
  --el-dialog-padding-primary: 20px;
}

.captcha-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.countdown-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.countdown-text strong {
  font-size: 18px;
  color: #F56C6C;
}

.captcha-image-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  min-height: 120px;
  cursor: pointer;
  transition: all 0.3s;
}

.captcha-image-wrapper:hover {
  background: #ebeef5;
}

.captcha-image {
  max-width: 100%;
  max-height: 150px;
  transition: all 0.3s;
}

.captcha-image.enlarged {
  max-height: 300px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.refresh-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}

.enlarge-hint {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 4px;
}

.auto-solve-card {
  border: 1px solid #409EFF;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.progress-text {
  font-weight: bold;
}

.auto-solve-result {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 4px;
}

.auto-solve-result strong {
  color: #409EFF;
  font-size: 16px;
}

.captcha-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.captcha-input {
  font-size: 18px;
  letter-spacing: 2px;
}

.input-hints {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.history-collapse {
  border: none;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  background: #ebeef5;
}

.history-image {
  width: 60px;
  height: 40px;
  border-radius: 4px;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-code {
  font-weight: bold;
  font-size: 14px;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-right {
  display: flex;
  gap: 12px;
}

.help-icon {
  color: #909399;
  cursor: help;
  font-size: 16px;
}

.help-content {
  font-size: 14px;
}

.help-content ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.help-content li {
  margin: 4px 0;
}

@media (max-width: 768px) {
  .captcha-image {
    max-height: 100px;
  }
  
  .dialog-footer {
    flex-direction: column;
    gap: 12px;
  }
  
  .footer-left, .footer-right {
    width: 100%;
    justify-content: center;
  }
}
</style>
