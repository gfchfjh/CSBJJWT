<template>
  <div class="unlock-screen">
    <div class="unlock-container">
      <el-card class="unlock-card" shadow="always">
        <!-- Logo和标题 -->
        <div class="unlock-header">
          <div class="lock-icon">
            <el-icon :size="80" color="#409EFF">
              <Lock />
            </el-icon>
          </div>
          <h1>KOOK消息转发系统</h1>
          <p class="subtitle">请输入主密码解锁</p>
        </div>

        <!-- 解锁表单 -->
        <el-form
          ref="unlockFormRef"
          :model="unlockForm"
          :rules="rules"
          @submit.prevent="handleUnlock"
          class="unlock-form"
        >
          <el-form-item prop="password">
            <el-input
              v-model="unlockForm.password"
              type="password"
              placeholder="请输入主密码"
              size="large"
              show-password
              autofocus
              @keyup.enter="handleUnlock"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="unlockForm.rememberDays">
              <span>记住密码</span>
            </el-checkbox>
            <el-select
              v-if="unlockForm.rememberDays"
              v-model="unlockForm.rememberDuration"
              size="small"
              style="width: 100px; margin-left: 10px"
            >
              <el-option label="1天" :value="1" />
              <el-option label="7天" :value="7" />
              <el-option label="30天" :value="30" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="unlocking"
              @click="handleUnlock"
            >
              <el-icon v-if="!unlocking"><Unlock /></el-icon>
              {{ unlocking ? '验证中...' : '解锁' }}
            </el-button>
          </el-form-item>

          <!-- 错误提示 -->
          <el-alert
            v-if="errorMessage"
            :title="errorMessage"
            type="error"
            :closable="false"
            show-icon
            class="error-alert"
          />

          <!-- 帮助链接 -->
          <div class="help-links">
            <el-button
              text
              type="primary"
              @click="showForgotPassword"
            >
              <el-icon><QuestionFilled /></el-icon>
              忘记密码？
            </el-button>
          </div>
        </el-form>

        <!-- 统计信息 -->
        <div class="unlock-footer">
          <el-text size="small" type="info">
            版本 v4.1.0 | 安全模式已启用
          </el-text>
        </div>
      </el-card>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="forgotPasswordVisible"
      title="忘记密码"
      width="500px"
    >
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #title>
          重置密码需要验证您的邮箱
        </template>
      </el-alert>

      <el-form :model="resetForm" label-width="100px">
        <el-form-item label="邮箱地址">
          <el-input
            v-model="resetForm.email"
            placeholder="请输入注册时使用的邮箱"
          />
        </el-form-item>

        <el-form-item label="验证码">
          <el-input v-model="resetForm.code" placeholder="请输入邮箱验证码">
            <template #append>
              <el-button
                :disabled="sendingCode || countdown > 0"
                @click="sendVerificationCode"
              >
                {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="forgotPasswordVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="resetting"
          @click="handleResetPassword"
        >
          重置密码
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Unlock, QuestionFilled } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const unlockFormRef = ref(null)

// 解锁表单
const unlockForm = reactive({
  password: '',
  rememberDays: false,
  rememberDuration: 7
})

// 验证规则
const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20位之间', trigger: 'blur' }
  ]
}

// 状态
const unlocking = ref(false)
const errorMessage = ref('')
const forgotPasswordVisible = ref(false)
const sendingCode = ref(false)
const resetting = ref(false)
const countdown = ref(0)

// 重置密码表单
const resetForm = reactive({
  email: '',
  code: ''
})

// 解锁
const handleUnlock = async () => {
  try {
    await unlockFormRef.value?.validate()
  } catch {
    return
  }

  unlocking.value = true
  errorMessage.value = ''

  try {
    const response = await api.post('/api/auth/unlock', {
      password: unlockForm.password,
      remember_days: unlockForm.rememberDays ? unlockForm.rememberDuration : 0
    })

    if (response.success) {
      // 保存Token
      localStorage.setItem('master_token', response.token)

      ElMessage.success('✅ 解锁成功')

      // 跳转到主页
      setTimeout(() => {
        router.push('/')
      }, 500)
    } else {
      errorMessage.value = response.message || '解锁失败'
    }
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = '密码错误，请重试'
    } else {
      errorMessage.value = '解锁失败：' + (error.response?.data?.detail || error.message)
    }
  } finally {
    unlocking.value = false
  }
}

// 显示忘记密码对话框
const showForgotPassword = () => {
  forgotPasswordVisible.value = true
}

// 发送验证码
const sendVerificationCode = async () => {
  if (!resetForm.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }

  // 邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(resetForm.email)) {
    ElMessage.warning('邮箱格式不正确')
    return
  }

  sendingCode.value = true

  try {
    const response = await api.post('/api/auth/send-reset-code', {
      email: resetForm.email
    })

    if (response.success) {
      ElMessage.success('验证码已发送到您的邮箱')

      // 开始倒计时（60秒）
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }
  } catch (error) {
    ElMessage.error('发送验证码失败：' + (error.response?.data?.detail || error.message))
  } finally {
    sendingCode.value = false
  }
}

// 重置密码
const handleResetPassword = async () => {
  if (!resetForm.email || !resetForm.code) {
    ElMessage.warning('请填写完整信息')
    return
  }

  resetting.value = true

  try {
    const response = await api.post('/api/auth/reset-password', {
      email: resetForm.email,
      verification_code: resetForm.code
    })

    if (response.success) {
      ElMessage.success('密码已重置')

      // 显示临时密码
      ElMessageBox.alert(
        `<p>您的临时密码是：</p><h3 style="color:#409EFF;user-select:all">${response.temporary_password}</h3><p>请复制并使用此密码登录，登录后请立即修改密码。</p>`,
        '临时密码',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我已复制'
        }
      ).then(() => {
        forgotPasswordVisible.value = false
        // 清空密码框，让用户输入临时密码
        unlockForm.password = ''
      })
    }
  } catch (error) {
    ElMessage.error('重置失败：' + (error.response?.data?.detail || error.message))
  } finally {
    resetting.value = false
  }
}

// 检查是否需要解锁
onMounted(async () => {
  try {
    const response = await api.get('/api/auth/master-password-status')

    if (!response.password_set) {
      // 未设置主密码，直接进入主页
      router.push('/')
    }
  } catch (error) {
    console.error('检查主密码状态失败:', error)
  }
})
</script>

<style scoped>
.unlock-screen {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.unlock-container {
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.unlock-card {
  border-radius: 16px;
}

.unlock-header {
  text-align: center;
  margin-bottom: 30px;
}

.lock-icon {
  margin-bottom: 20px;
}

.unlock-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 10px 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 5px 0 0 0;
}

.unlock-form {
  padding: 0 20px;
}

.error-alert {
  margin-top: 16px;
}

.help-links {
  text-align: center;
  margin-top: 20px;
}

.unlock-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .unlock-screen {
    background: linear-gradient(135deg, #434343 0%, #000000 100%);
  }

  .unlock-header h1 {
    color: #E4E7ED;
  }
}
</style>
