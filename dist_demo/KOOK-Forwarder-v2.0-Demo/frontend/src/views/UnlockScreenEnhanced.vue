<template>
  <div class="unlock-screen">
    <!-- ✅ P0-7优化: 主密码保护完善 - 记住30天 + 美化界面 -->
    
    <!-- 背景渐变 -->
    <div class="background-gradient">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 解锁卡片 -->
    <el-card class="unlock-card">
      <!-- Logo和标题 -->
      <div class="unlock-header">
        <div class="app-icon">
          <el-icon :size="60"><Lock /></el-icon>
        </div>
        <h1>KOOK消息转发系统</h1>
        <p class="version">v6.7.0</p>
      </div>

      <!-- 解锁表单 -->
      <el-form 
        ref="unlockForm" 
        :model="form" 
        :rules="rules"
        @submit.prevent="handleUnlock"
        class="unlock-form"
      >
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入主密码"
            size="large"
            show-password
            clearable
            @keyup.enter="handleUnlock"
            :disabled="unlocking"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 记住我选项 -->
        <el-form-item class="remember-me">
          <el-checkbox v-model="form.rememberMe" size="large">
            <span class="remember-text">
              记住密码（30天）
              <el-tooltip content="在此设备上30天内无需再次输入密码" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </el-checkbox>
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

        <!-- 解锁按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="unlocking"
            @click="handleUnlock"
            class="unlock-button"
            block
          >
            <el-icon v-if="!unlocking"><Unlock /></el-icon>
            {{ unlocking ? '验证中...' : '解锁' }}
          </el-button>
        </el-form-item>

        <!-- 忘记密码链接 -->
        <div class="forgot-password">
          <el-button link type="primary" @click="showForgotPasswordDialog">
            <el-icon><QuestionFilled /></el-icon>
            忘记密码？
          </el-button>
        </div>
      </el-form>

      <!-- 底部信息 -->
      <div class="unlock-footer">
        <p>
          <el-icon><Lock /></el-icon>
          您的数据已加密存储，安全可靠
        </p>
      </div>
    </el-card>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="showForgotDialog"
      title="重置主密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-steps :active="resetStep" align-center finish-status="success">
        <el-step title="验证邮箱" />
        <el-step title="重置密码" />
        <el-step title="完成" />
      </el-steps>

      <div class="reset-content">
        <!-- 步骤1: 验证邮箱 -->
        <div v-if="resetStep === 0" class="reset-step">
          <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px;">
            我们将向您的注册邮箱发送验证码
          </el-alert>

          <el-form :model="resetForm" label-width="80px">
            <el-form-item label="邮箱">
              <el-input
                v-model="resetForm.email"
                placeholder="请输入注册时使用的邮箱"
                clearable
              >
                <template #prefix><el-icon><Message /></el-icon></template>
              </el-input>
            </el-form-item>

            <el-form-item label="验证码">
              <div class="captcha-input-group">
                <el-input
                  v-model="resetForm.code"
                  placeholder="6位验证码"
                  maxlength="6"
                  clearable
                >
                  <template #prefix><el-icon><Key /></el-icon></template>
                </el-input>
                <el-button
                  type="primary"
                  @click="sendVerificationCode"
                  :disabled="codeSent || countdown > 0"
                  :loading="sendingCode"
                >
                  {{ countdown > 0 ? `${countdown}秒后重试` : (codeSent ? '已发送' : '发送验证码') }}
                </el-button>
              </div>
            </el-form-item>
          </el-form>

          <el-button
            type="primary"
            @click="verifyCode"
            :disabled="!resetForm.email || !resetForm.code"
            :loading="verifying"
            block
          >
            下一步
          </el-button>
        </div>

        <!-- 步骤2: 重置密码 -->
        <div v-else-if="resetStep === 1" class="reset-step">
          <el-alert type="success" :closable="false" show-icon style="margin-bottom: 20px;">
            ✅ 验证码验证成功，请设置新密码
          </el-alert>

          <el-form :model="resetForm" label-width="100px">
            <el-form-item label="新密码">
              <el-input
                v-model="resetForm.newPassword"
                type="password"
                placeholder="6-20位，建议包含字母和数字"
                show-password
                clearable
              />
            </el-form-item>

            <el-form-item label="确认密码">
              <el-input
                v-model="resetForm.confirmPassword"
                type="password"
                placeholder="再次输入新密码"
                show-password
                clearable
              />
            </el-form-item>
          </el-form>

          <!-- 密码强度指示器 -->
          <div class="password-strength" v-if="resetForm.newPassword">
            <div class="strength-label">密码强度:</div>
            <el-progress
              :percentage="passwordStrength.percentage"
              :color="passwordStrength.color"
              :status="passwordStrength.status"
            />
            <div class="strength-text">{{ passwordStrength.text }}</div>
          </div>

          <el-button
            type="primary"
            @click="resetPassword"
            :disabled="!canResetPassword"
            :loading="resetting"
            block
          >
            重置密码
          </el-button>
        </div>

        <!-- 步骤3: 完成 -->
        <div v-else-if="resetStep === 2" class="reset-step reset-success">
          <el-result
            icon="success"
            title="密码重置成功！"
            sub-title="您的新密码已设置完成，请使用新密码登录"
          >
            <template #extra>
              <el-button type="primary" @click="closeResetDialog">
                返回登录
              </el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Lock, Unlock, QuestionFilled, Message, Key
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 表单数据
const form = ref({
  password: '',
  rememberMe: false
})

// 验证规则
const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ]
}

// UI状态
const unlocking = ref(false)
const errorMessage = ref('')

// 忘记密码
const showForgotDialog = ref(false)
const resetStep = ref(0)
const resetForm = ref({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const sendingCode = ref(false)
const codeSent = ref(false)
const countdown = ref(0)
const verifying = ref(false)
const resetting = ref(false)

// 计算属性
const canResetPassword = computed(() => {
  return resetForm.value.newPassword &&
         resetForm.value.confirmPassword &&
         resetForm.value.newPassword === resetForm.value.confirmPassword &&
         resetForm.value.newPassword.length >= 6
})

const passwordStrength = computed(() => {
  const pwd = resetForm.value.newPassword
  if (!pwd) return { percentage: 0, color: '#909399', status: '', text: '' }
  
  let strength = 0
  let text = ''
  let color = ''
  
  // 长度
  if (pwd.length >= 8) strength += 25
  if (pwd.length >= 12) strength += 25
  
  // 包含数字
  if (/\d/.test(pwd)) strength += 15
  
  // 包含字母
  if (/[a-zA-Z]/.test(pwd)) strength += 15
  
  // 包含大小写
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength += 10
  
  // 包含特殊字符
  if (/[^a-zA-Z0-9]/.test(pwd)) strength += 10
  
  if (strength < 40) {
    text = '弱'
    color = '#F56C6C'
  } else if (strength < 70) {
    text = '中等'
    color = '#E6A23C'
  } else {
    text = '强'
    color = '#67C23A'
  }
  
  return { percentage: strength, color, status: '', text }
})

// 解锁操作
const handleUnlock = async () => {
  if (!form.value.password) {
    errorMessage.value = '请输入密码'
    return
  }
  
  unlocking.value = true
  errorMessage.value = ''
  
  try {
    const response = await api.post('/auth/verify-master-password', {
      password: form.value.password
    })
    
    if (response.data.success) {
      const token = response.data.token
      const tokenExpire = response.data.expire_at
      
      // 存储Token
      localStorage.setItem('auth_token', token)
      localStorage.setItem('auth_token_expire', tokenExpire)
      
      // 如果勾选了"记住我"，存储设备令牌（30天有效）
      if (form.value.rememberMe) {
        const deviceToken = response.data.device_token
        const deviceTokenExpire = Date.now() + (30 * 24 * 60 * 60 * 1000) // 30天
        
        localStorage.setItem('device_token', deviceToken)
        localStorage.setItem('device_token_expire', deviceTokenExpire)
        
        ElMessage.success('✅ 解锁成功！30天内无需再次输入密码')
      } else {
        ElMessage.success('✅ 解锁成功！')
      }
      
      // 跳转到主页
      router.push('/')
    } else {
      errorMessage.value = response.data.message || '密码错误，请重试'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '验证失败: ' + error.message
  } finally {
    unlocking.value = false
  }
}

// 忘记密码流程
const showForgotPasswordDialog = () => {
  resetStep.value = 0
  resetForm.value = {
    email: '',
    code: '',
    newPassword: '',
    confirmPassword: ''
  }
  showForgotDialog.value = true
}

const sendVerificationCode = async () => {
  if (!resetForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  
  sendingCode.value = true
  
  try {
    const response = await api.post('/auth/send-reset-code', {
      email: resetForm.value.email
    })
    
    if (response.data.success) {
      codeSent.value = true
      countdown.value = 60
      
      // 倒计时
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
      
      ElMessage.success('✅ 验证码已发送，请查收邮件')
    } else {
      ElMessage.error(response.data.message || '发送失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '发送失败: ' + error.message)
  } finally {
    sendingCode.value = false
  }
}

const verifyCode = async () => {
  if (!resetForm.value.code || resetForm.value.code.length !== 6) {
    ElMessage.warning('请输入6位验证码')
    return
  }
  
  verifying.value = true
  
  try {
    const response = await api.post('/auth/verify-reset-code', {
      email: resetForm.value.email,
      code: resetForm.value.code
    })
    
    if (response.data.success) {
      resetStep.value = 1
      ElMessage.success('✅ 验证成功，请设置新密码')
    } else {
      ElMessage.error(response.data.message || '验证码错误')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '验证失败: ' + error.message)
  } finally {
    verifying.value = false
  }
}

const resetPassword = async () => {
  if (!canResetPassword.value) {
    ElMessage.warning('请正确填写新密码')
    return
  }
  
  resetting.value = true
  
  try {
    const response = await api.post('/auth/reset-master-password', {
      email: resetForm.value.email,
      code: resetForm.value.code,
      new_password: resetForm.value.newPassword
    })
    
    if (response.data.success) {
      resetStep.value = 2
      ElMessage.success('✅ 密码重置成功！')
    } else {
      ElMessage.error(response.data.message || '重置失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '重置失败: ' + error.message)
  } finally {
    resetting.value = false
  }
}

const closeResetDialog = () => {
  showForgotDialog.value = false
  resetStep.value = 0
  resetForm.value = {
    email: '',
    code: '',
    newPassword: '',
    confirmPassword: ''
  }
}

// 检查是否有设备令牌（记住30天）
const checkDeviceToken = async () => {
  const deviceToken = localStorage.getItem('device_token')
  const deviceTokenExpire = localStorage.getItem('device_token_expire')
  
  if (deviceToken && deviceTokenExpire) {
    if (Date.now() < parseInt(deviceTokenExpire)) {
      // 设备令牌有效，尝试自动解锁
      try {
        const response = await api.post('/auth/verify-device-token', {
          device_token: deviceToken
        })
        
        if (response.data.success) {
          // 自动解锁成功
          const token = response.data.token
          const tokenExpire = response.data.expire_at
          
          localStorage.setItem('auth_token', token)
          localStorage.setItem('auth_token_expire', tokenExpire)
          
          ElMessage.success('✅ 自动解锁成功！')
          router.push('/')
          return true
        }
      } catch (error) {
        // 自动解锁失败，清除设备令牌
        localStorage.removeItem('device_token')
        localStorage.removeItem('device_token_expire')
      }
    } else {
      // 设备令牌已过期
      localStorage.removeItem('device_token')
      localStorage.removeItem('device_token_expire')
    }
  }
  
  return false
}

// 生命周期
onMounted(async () => {
  // 检查设备令牌
  const autoUnlocked = await checkDeviceToken()
  
  if (!autoUnlocked) {
    // 聚焦到密码输入框
    // 延迟一下等待组件渲染
    setTimeout(() => {
      const passwordInput = document.querySelector('input[type="password"]')
      if (passwordInput) {
        passwordInput.focus()
      }
    }, 300)
  }
})
</script>

<style scoped lang="scss">
.unlock-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 背景渐变动画 */
.background-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  animation: float 20s infinite;
  
  &.orb-1 {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, #ffeaa7 0%, transparent 70%);
    top: -10%;
    left: -10%;
    animation-delay: 0s;
  }
  
  &.orb-2 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, #74b9ff 0%, transparent 70%);
    bottom: -10%;
    right: -10%;
    animation-delay: 7s;
  }
  
  &.orb-3 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, #a29bfe 0%, transparent 70%);
    top: 50%;
    left: 50%;
    animation-delay: 14s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  33% {
    transform: translate(30px, -30px);
  }
  66% {
    transform: translate(-20px, 20px);
  }
}

/* 解锁卡片 */
.unlock-card {
  position: relative;
  z-index: 1;
  width: 450px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
}

.unlock-header {
  text-align: center;
  margin-bottom: 40px;
  
  .app-icon {
    width: 100px;
    height: 100px;
    margin: 0 auto 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  }
  
  h1 {
    font-size: 28px;
    margin: 0 0 10px 0;
    color: #303133;
  }
  
  .version {
    color: #909399;
    font-size: 14px;
  }
}

.unlock-form {
  .remember-me {
    margin-bottom: 15px;
    
    .remember-text {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
  }
  
  .error-alert {
    margin-bottom: 20px;
  }
  
  .unlock-button {
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    
    &:hover {
      background: linear-gradient(135deg, #5a6fd8 0%, #6a4292 100%);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
  }
}

.forgot-password {
  text-align: center;
  margin-top: 15px;
}

.unlock-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
  
  p {
    color: #909399;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    margin: 0;
  }
}

/* 重置密码对话框 */
.reset-content {
  margin-top: 30px;
}

.reset-step {
  .captcha-input-group {
    display: flex;
    gap: 10px;
  }
}

.password-strength {
  margin-bottom: 20px;
  
  .strength-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
  }
  
  .strength-text {
    text-align: right;
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}

.reset-success {
  text-align: center;
  padding: 40px 0;
}
</style>
