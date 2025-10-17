<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon :size="60" color="#409EFF"><Lock /></el-icon>
        <h2>KOOK消息转发系统</h2>
        <p>请输入密码以继续</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            size="large"
            placeholder="请输入密码"
            show-password
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
            autofocus
          >
            <template #prepend>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember">
            记住30天
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="logging"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ logging ? '验证中...' : '登录' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-link type="primary" @click="showResetDialog = true">
            忘记密码？
          </el-link>
        </el-form-item>
      </el-form>

      <!-- 首次设置密码 -->
      <div v-if="isFirstTime" class="first-time-notice">
        <el-alert
          title="首次使用"
          type="info"
          :closable="false"
          show-icon
        >
          <p>检测到您是首次使用本系统，请设置一个登录密码。</p>
          <p style="color: #F56C6C; margin-top: 10px">
            <strong>⚠️ 请务必记住密码，遗忘后需要通过邮箱重置！</strong>
          </p>
        </el-alert>

        <el-button
          type="success"
          size="large"
          style="width: 100%; margin-top: 15px"
          @click="showSetPasswordDialog = true"
        >
          设置密码
        </el-button>
      </div>
    </div>

    <!-- 设置密码对话框 -->
    <el-dialog
      v-model="showSetPasswordDialog"
      title="设置登录密码"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="setPasswordFormRef"
        :model="setPasswordForm"
        :rules="setPasswordRules"
        label-width="100px"
      >
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="setPasswordForm.password"
            type="password"
            show-password
            placeholder="6-20位密码"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="setPasswordForm.confirmPassword"
            type="password"
            show-password
            placeholder="再次输入密码"
          />
        </el-form-item>

        <el-form-item label="邮箱（可选）" prop="email">
          <el-input
            v-model="setPasswordForm.email"
            placeholder="用于密码重置"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 5px">
            建议设置邮箱，以便忘记密码时重置
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showSetPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSetPassword">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="showResetDialog"
      title="重置密码"
      width="450px"
    >
      <el-alert
        title="密码重置功能"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <p>如果您设置了邮箱，系统会向您的邮箱发送重置链接。</p>
        <p style="margin-top: 10px">如果未设置邮箱，请联系管理员或重新安装系统。</p>
      </el-alert>

      <el-form label-width="80px">
        <el-form-item label="邮箱">
          <el-input
            v-model="resetEmail"
            placeholder="请输入注册时的邮箱"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">
          发送重置邮件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

const logging = ref(false)
const isFirstTime = ref(false)

const loginFormRef = ref(null)
const setPasswordFormRef = ref(null)

const loginForm = ref({
  password: '',
  remember: false
})

const setPasswordForm = ref({
  password: '',
  confirmPassword: '',
  email: ''
})

const loginRules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ]
}

const setPasswordRules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== setPasswordForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const showSetPasswordDialog = ref(false)
const showResetDialog = ref(false)
const resetEmail = ref('')

// 检查是否已设置密码
const checkPasswordExists = async () => {
  try {
    const result = await api.checkPasswordExists()
    isFirstTime.value = !result.exists
  } catch (error) {
    console.error('检查密码状态失败:', error)
  }
}

// 处理登录
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    
    logging.value = true
    
    const result = await api.verifyPassword({
      password: loginForm.value.password,
      remember: loginForm.value.remember
    })
    
    if (result.success) {
      // 保存token到本地
      if (result.token) {
        if (loginForm.value.remember) {
          localStorage.setItem('auth_token', result.token)
        } else {
          sessionStorage.setItem('auth_token', result.token)
        }
      }
      
      ElMessage.success('登录成功')
      
      // 检查是否需要引导向导
      const wizardCompleted = localStorage.getItem('wizard_completed')
      if (!wizardCompleted) {
        router.push('/wizard')
      } else {
        router.push('/')
      }
    } else {
      ElMessage.error('密码错误')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    logging.value = false
  }
}

// 设置密码
const handleSetPassword = async () => {
  try {
    await setPasswordFormRef.value.validate()
    
    const result = await api.setPassword({
      password: setPasswordForm.value.password,
      email: setPasswordForm.value.email || null
    })
    
    if (result.success) {
      ElMessage.success('密码设置成功，请登录')
      showSetPasswordDialog.value = false
      isFirstTime.value = false
      
      // 自动填入密码
      loginForm.value.password = setPasswordForm.value.password
      
      // 清空表单
      setPasswordForm.value = {
        password: '',
        confirmPassword: '',
        email: ''
      }
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '设置失败')
  }
}

// 重置密码
const handleResetPassword = async () => {
  if (!resetEmail.value) {
    ElMessage.warning('请输入邮箱')
    return
  }
  
  try {
    await api.resetPassword({ email: resetEmail.value })
    ElMessage.success('重置邮件已发送，请查收邮箱')
    showResetDialog.value = false
    resetEmail.value = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送失败')
  }
}

onMounted(() => {
  checkPasswordExists()
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 20px 0 10px;
  font-size: 24px;
  color: #303133;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.first-time-notice {
  margin-top: 20px;
}
</style>
