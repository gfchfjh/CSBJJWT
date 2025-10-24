<template>
  <el-dialog
    v-model="dialogVisible"
    title="🔒 需要验证码"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="captcha-container">
      <el-alert
        title="检测到登录需要验证码，请输入以继续"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <div class="account-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="账号ID">
            {{ accountId }}
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ formatTime(timestamp) }}
          </el-descriptions-item>
          <!-- ✅ P0-3优化：倒计时显示 -->
          <el-descriptions-item label="剩余时间">
            <el-tag :type="countdown > 10 ? 'success' : 'danger'" effect="dark">
              <el-icon><Clock /></el-icon>
              {{ countdown }} 秒
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="captcha-image" v-if="imageUrl">
        <el-image
          :src="currentImageUrl"
          fit="contain"
          style="max-width: 100%; max-height: 200px"
          :key="imageRefreshKey"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>验证码加载失败</span>
            </div>
          </template>
        </el-image>
        
        <!-- ✅ P0-3优化："看不清？刷新"按钮 -->
        <div class="refresh-btn-container">
          <el-button
            type="text"
            @click="refreshCaptcha"
            :loading="refreshing"
            style="margin-top: 10px"
          >
            <el-icon><Refresh /></el-icon>
            看不清？点击刷新
          </el-button>
        </div>
      </div>

      <el-form :model="form" label-width="100px" style="margin-top: 20px">
        <el-form-item label="验证码">
          <el-input
            ref="captchaInput"
            v-model="form.code"
            placeholder="请输入验证码（4-6位）"
            clearable
            @keyup.enter="submitCaptcha"
            maxlength="6"
            autocomplete="off"
          >
            <template #append>
              <el-button @click="submitCaptcha" :disabled="!form.code || submitting">
                提交
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <div class="tips">
        <el-alert type="info" :closable="false">
          <template #default>
            <div>
              <p>💡 <strong>提示：</strong></p>
              <ul style="margin: 5px 0; padding-left: 20px;">
                <li>请仔细查看图片，区分相似字符（如0和O、1和l）</li>
                <li>如果看不清，点击"刷新"按钮获取新验证码</li>
                <li>验证码区分大小写</li>
                <li>倒计时归零后需要刷新验证码</li>
              </ul>
            </div>
          </template>
        </el-alert>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel" :disabled="submitting">取消</el-button>
        <el-button
          type="primary"
          @click="submitCaptcha"
          :loading="submitting"
          :disabled="!form.code || countdown <= 0"
        >
          {{ submitting ? '提交中...' : '提交验证码' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Refresh, Picture } from '@element-plus/icons-vue'
import api from '../api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  accountId: {
    type: Number,
    default: 0
  },
  imageUrl: {
    type: String,
    default: ''
  },
  timestamp: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:visible', 'submit', 'cancel'])

const dialogVisible = ref(false)
const submitting = ref(false)
const refreshing = ref(false)

// ✅ P0-3优化：倒计时功能
const countdown = ref(60)
let countdownTimer = null

// ✅ P0-3优化：刷新验证码
const imageRefreshKey = ref(0)
const currentImageUrl = ref('')

// ✅ P0-3优化：自动聚焦输入框
const captchaInput = ref(null)

const form = ref({
  code: ''
})

// 监听visible变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    // 打开对话框时重置
    form.value.code = ''
    submitting.value = false
    currentImageUrl.value = props.imageUrl
    
    // ✅ P0-3优化：启动倒计时
    startCountdown()
    
    // ✅ P0-3优化：自动聚焦
    nextTick(() => {
      captchaInput.value?.focus()
    })
  } else {
    // 关闭时停止倒计时
    stopCountdown()
  }
})

// 监听对话框关闭
watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// ✅ P0-3优化：倒计时功能
const startCountdown = () => {
  countdown.value = 60
  stopCountdown() // 先清除旧定时器
  
  countdownTimer = setInterval(() => {
    countdown.value--
    
    if (countdown.value <= 0) {
      stopCountdown()
      ElMessage.warning({
        message: '验证码已超时，请点击"刷新"获取新验证码',
        duration: 5000
      })
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// ✅ P0-3优化：刷新验证码功能
const refreshCaptcha = async () => {
  try {
    refreshing.value = true
    form.value.code = ''  // 清空输入
    
    // 请求后端刷新验证码
    const response = await api.refreshCaptcha(props.accountId)
    
    if (response && response.image_url) {
      currentImageUrl.value = response.image_url
      imageRefreshKey.value++  // 强制重新渲染图片
      
      // 重启倒计时
      startCountdown()
      
      ElMessage.success('验证码已刷新')
      
      // 重新聚焦输入框
      nextTick(() => {
        captchaInput.value?.focus()
      })
    }
    
  } catch (error) {
    console.error('刷新验证码失败:', error)
    ElMessage.error('刷新失败：' + (error.response?.data?.detail || error.message))
  } finally {
    refreshing.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '--'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// 提交验证码
const submitCaptcha = async () => {
  if (!form.value.code) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  if (countdown.value <= 0) {
    ElMessage.warning('验证码已超时，请刷新后重试')
    return
  }

  submitting.value = true

  try {
    // 通过HTTP API提交验证码
    await api.submitCaptcha(props.accountId, form.value.code)
    
    ElMessage.success('验证码提交成功')
    emit('submit', form.value.code)
    dialogVisible.value = false
    
  } catch (error) {
    console.error('提交验证码失败:', error)
    const errorMsg = error.response?.data?.detail || error.message
    
    if (errorMsg.includes('incorrect') || errorMsg.includes('错误')) {
      ElMessage.error('验证码错误，请重试')
      // 清空输入框
      form.value.code = ''
      // 自动刷新验证码
      setTimeout(() => {
        refreshCaptcha()
      }, 1000)
    } else {
      ElMessage.error('提交失败：' + errorMsg)
    }
    
  } finally {
    submitting.value = false
  }
}

// 取消
const handleCancel = () => {
  stopCountdown()
  emit('cancel')
  dialogVisible.value = false
}

// ✅ P0-3优化：组件卸载时清理定时器
onUnmounted(() => {
  stopCountdown()
})
</script>

<style scoped>
.captcha-container {
  padding: 10px 0;
}

.account-info {
  margin: 20px 0;
}

.captcha-image {
  margin: 20px 0;
  text-align: center;
  padding: 20px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.image-error .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.tips {
  margin-top: 15px;
}

/* ✅ P0-3优化：刷新按钮样式 */
.refresh-btn-container {
  text-align: center;
  margin-top: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* ✅ P0-3优化：倒计时动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.el-tag {
  animation: pulse 2s ease-in-out infinite;
}

.el-tag.is-danger {
  animation: pulse 1s ease-in-out infinite;
}
</style>
