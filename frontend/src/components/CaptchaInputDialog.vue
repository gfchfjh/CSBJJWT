<!--
  验证码输入对话框
  ✅ P0-4优化：友好的验证码输入界面
-->
<template>
  <el-dialog
    v-model="visible"
    title="🔐 需要输入验证码"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="true"
    @close="handleCancel"
    class="captcha-dialog"
  >
    <div class="captcha-content">
      <!-- 提示信息 -->
      <el-alert
        title="为了安全验证，KOOK要求输入验证码"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <p style="margin: 5px 0 0 0; font-size: 14px;">
            这是KOOK平台的安全措施，请输入下方图片中的验证码
          </p>
        </template>
      </el-alert>
      
      <!-- 验证码图片 -->
      <div class="captcha-image-wrapper">
        <div v-if="loading" class="captcha-loading">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
          <p>正在加载验证码...</p>
        </div>
        
        <div v-else-if="captchaImageUrl" class="captcha-image-container">
          <img 
            :src="captchaImageUrl" 
            alt="验证码" 
            class="captcha-image"
            @error="handleImageError"
          />
          
          <el-button
            size="small"
            type="info"
            :loading="refreshing"
            @click="refreshCaptcha"
            class="refresh-button"
          >
            <el-icon><RefreshRight /></el-icon>
            看不清？换一张
          </el-button>
        </div>
        
        <div v-else class="captcha-error">
          <el-icon :size="40" color="#F56C6C"><WarningFilled /></el-icon>
          <p>验证码加载失败</p>
          <el-button size="small" @click="refreshCaptcha">
            <el-icon><RefreshRight /></el-icon>
            重新加载
          </el-button>
        </div>
      </div>
      
      <!-- 输入框 -->
      <div class="captcha-input-section">
        <el-input
          v-model="captchaCode"
          placeholder="请输入图中的验证码"
          size="large"
          clearable
          maxlength="8"
          :disabled="submitting"
          @keyup.enter="submitCaptcha"
          ref="captchaInputRef"
        >
          <template #prepend>
            <el-icon><Key /></el-icon>
            验证码
          </template>
        </el-input>
        
        <div class="input-hint">
          <el-icon><InfoFilled /></el-icon>
          <span>通常为4-6位字母或数字</span>
        </div>
      </div>
      
      <!-- 2Captcha状态 -->
      <div v-if="has2Captcha" class="captcha-auto-status">
        <el-alert
          type="success"
          :closable="false"
        >
          <template #title>
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-icon><MagicStick /></el-icon>
              <span>2Captcha自动识别中...（余额：${{ captchaBalance.toFixed(2) }}）</span>
            </div>
          </template>
          <template #default>
            <p style="margin: 5px 0 0 0; font-size: 13px;">
              系统正在尝试自动识别验证码，如果失败请手动输入
            </p>
          </template>
        </el-alert>
      </div>
      
      <div v-else class="captcha-tip">
        <el-alert
          type="info"
          :closable="false"
        >
          <template #title>
            💡 提示：您可以配置2Captcha实现自动识别
          </template>
          <template #default>
            <p style="margin: 5px 0 0 0; font-size: 13px;">
              在"系统设置"中配置2Captcha API Key，验证码将自动识别
            </p>
          </template>
        </el-alert>
      </div>
      
      <!-- 倒计时提示 -->
      <div v-if="timeRemaining > 0" class="timeout-warning">
        <el-icon color="#E6A23C"><Clock /></el-icon>
        <span>请在 {{ formatTime(timeRemaining) }} 内输入验证码</span>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" :disabled="submitting">
          取消登录
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
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  RefreshRight,
  WarningFilled,
  Key,
  InfoFilled,
  MagicStick,
  Clock,
  Check
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  accountId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['success', 'cancel'])

const visible = ref(false)
const loading = ref(false)
const refreshing = ref(false)
const submitting = ref(false)
const captchaImageUrl = ref('')
const captchaCode = ref('')
const has2Captcha = ref(false)
const captchaBalance = ref(0)
const captchaInputRef = ref(null)
const timeRemaining = ref(120) // 120秒超时
let checkInterval = null
let countdownInterval = null

// 格式化时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 检查验证码状态
const checkCaptchaStatus = async () => {
  try {
    const response = await api.get(`/api/captcha/required/${props.accountId}`)
    
    if (response.data.required) {
      captchaImageUrl.value = response.data.image_url
      has2Captcha.value = response.data.has_2captcha
      captchaBalance.value = response.data.captcha_balance || 0
      
      if (!visible.value) {
        visible.value = true
        // 聚焦输入框
        setTimeout(() => {
          captchaInputRef.value?.focus()
        }, 300)
      }
    } else {
      // 不需要验证码，关闭对话框
      if (visible.value) {
        visible.value = false
        emit('success')
      }
    }
  } catch (error) {
    console.error('检查验证码状态失败:', error)
  }
}

// 刷新验证码
const refreshCaptcha = async () => {
  refreshing.value = true
  try {
    await api.post(`/api/captcha/refresh/${props.accountId}`)
    ElMessage.info('正在刷新验证码...')
    
    // 等待新的验证码
    setTimeout(async () => {
      await checkCaptchaStatus()
      refreshing.value = false
    }, 2000)
  } catch (error) {
    ElMessage.error('刷新验证码失败: ' + error.message)
    refreshing.value = false
  }
}

// 提交验证码
const submitCaptcha = async () => {
  if (!captchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  if (captchaCode.value.length < 3) {
    ElMessage.warning('验证码长度不正确')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/api/captcha/submit', {
      account_id: props.accountId,
      code: captchaCode.value
    })
    
    ElMessage.success('验证码已提交，正在验证...')
    
    // 等待验证结果（轮询检查）
    let attempts = 0
    const maxAttempts = 10
    
    const checkResult = setInterval(async () => {
      attempts++
      
      const status = await api.get(`/api/captcha/required/${props.accountId}`)
      
      if (!status.data.required) {
        // 验证成功
        clearInterval(checkResult)
        ElMessage.success('✅ 验证码验证成功！')
        visible.value = false
        emit('success')
      } else if (attempts >= maxAttempts) {
        // 超时或失败
        clearInterval(checkResult)
        ElMessage.error('验证码验证超时，请重试')
        submitting.value = false
        captchaCode.value = ''
      }
    }, 1000)
    
  } catch (error) {
    ElMessage.error('提交验证码失败: ' + error.message)
    submitting.value = false
  }
}

// 处理图片加载错误
const handleImageError = () => {
  ElMessage.error('验证码图片加载失败')
  captchaImageUrl.value = ''
}

// 取消输入
const handleCancel = async () => {
  try {
    await api.delete(`/api/captcha/cancel/${props.accountId}`)
    visible.value = false
    emit('cancel')
  } catch (error) {
    console.error('取消验证码失败:', error)
    visible.value = false
    emit('cancel')
  }
}

// 启动轮询检查
const startChecking = () => {
  checkCaptchaStatus()
  checkInterval = setInterval(checkCaptchaStatus, 2000)
  
  // 启动倒计时
  countdownInterval = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      // 超时
      ElMessage.warning('验证码输入超时，请重新登录')
      handleCancel()
    }
  }, 1000)
}

// 停止轮询检查
const stopChecking = () => {
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
}

// 重置状态
const reset = () => {
  captchaCode.value = ''
  captchaImageUrl.value = ''
  has2Captcha.value = false
  captchaBalance.value = 0
  submitting.value = false
  refreshing.value = false
  timeRemaining.value = 120
}

// 监听对话框显示
watch(visible, (newVal) => {
  if (newVal) {
    reset()
    startChecking()
  } else {
    stopChecking()
  }
})

onMounted(() => {
  startChecking()
})

onUnmounted(() => {
  stopChecking()
})

// 暴露方法
defineExpose({
  show: () => {
    visible.value = true
  },
  hide: () => {
    visible.value = false
  }
})
</script>

<style scoped>
.captcha-dialog {
  --el-dialog-border-radius: 12px;
}

.captcha-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.captcha-image-wrapper {
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.captcha-loading,
.captcha-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  color: #909399;
}

.captcha-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.captcha-image {
  max-width: 100%;
  height: auto;
  border: 2px solid #DCDFE6;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.captcha-image:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.refresh-button {
  width: 100%;
}

.captcha-input-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #909399;
}

.captcha-auto-status,
.captcha-tip {
  margin-top: -10px;
}

.timeout-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #FDF6EC;
  border: 1px solid #F5DAB1;
  border-radius: 6px;
  color: #E6A23C;
  font-size: 14px;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.dialog-footer .el-button {
  flex: 1;
}

/* 动画效果 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.captcha-image.error {
  animation: shake 0.5s ease-in-out;
}

/* 响应式 */
@media (max-width: 768px) {
  .captcha-dialog {
    width: 95vw !important;
  }
}
</style>
