<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>🔒 KOOK消息转发系统</h2>
          <p>{{ isSetup ? '首次设置密码' : '请输入主密码' }}</p>
        </div>
      </template>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item v-if="isSetup" label="设置密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请设置6-20位主密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="isSetup" label="确认密码" prop="confirmPassword">
          <el-input
            v-model="loginForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="!isSetup" label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入主密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="!isSetup">
          <el-checkbox v-model="loginForm.remember">记住密码（30天）</el-checkbox>
        </el-form-item>
      </el-form>

      <div class="login-actions">
        <el-button type="primary" size="large" :loading="loading" @click="handleLogin">
          {{ isSetup ? '设置密码' : '登录' }}
        </el-button>
        
        <el-button v-if="!isSetup" size="large" @click="showResetDialog">
          忘记密码？
        </el-button>
      </div>

      <div v-if="isSetup" class="setup-tips">
        <el-alert
          title="密码提示"
          type="info"
          :closable="false"
          show-icon
        >
          <ul>
            <li>密码长度为6-20位</li>
            <li>建议包含字母和数字</li>
            <li>请妥善保管密码</li>
            <li>忘记密码需要通过验证码重置</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetDialogVisible"
      title="重置密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="请联系管理员或查看日志文件获取验证码"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <p>验证码已生成并写入日志文件：</p>
        <code>backend/data/logs/app.log</code>
      </el-alert>

      <el-form :model="resetForm" label-width="100px">
        <el-form-item label="验证码">
          <el-input
            v-model="resetForm.verificationCode"
            placeholder="请输入6位验证码"
            maxlength="6"
          />
        </el-form-item>

        <el-form-item label="新密码">
          <el-input
            v-model="resetForm.newPassword"
            type="password"
            placeholder="请输入新密码（6-20位）"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码">
          <el-input
            v-model="resetForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="handleReset">
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
import api from '@/api'

const router = useRouter()
const loginFormRef = ref(null)

const isSetup = ref(false)
const loading = ref(false)
const resetting = ref(false)
const resetDialogVisible = ref(false)

const loginForm = reactive({
  password: '',
  confirmPassword: '',
  remember: false
})

const resetForm = reactive({
  verificationCode: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== loginForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 检查是否已设置密码
const checkAuthStatus = async () => {
  try {
    const data = await api.getAuthStatus()
    isSetup.value = !data.password_set
  } catch (error) {
    console.error('检查认证状态失败:', error)
    ElMessage.error('检查认证状态失败')
  }
}

// 登录/设置密码
const handleLogin = async () => {
  try {
    // 表单验证
    if (!loginFormRef.value) return
    await loginFormRef.value.validate()

    loading.value = true

    if (isSetup.value) {
      // 首次设置密码
      await api.setupPassword({ password: loginForm.password })
      ElMessage.success('密码设置成功')
      
      // 设置成功后自动登录
      const loginData = await api.login({
        password: loginForm.password,
        remember: true
      })
      
      // 保存Token
      localStorage.setItem('auth_token', loginData.token)
      
      // 跳转到向导页面
      router.push('/wizard')
    } else {
      // 登录
      const data = await api.login({
        password: loginForm.password,
        remember: loginForm.remember
      })
      
      // 保存Token
      localStorage.setItem('auth_token', data.token)
      
      if (loginForm.remember) {
        // 记住30天
        const expireTime = Date.now() + 30 * 24 * 3600 * 1000
        localStorage.setItem('auth_token_expire', expireTime.toString())
      }
      
      ElMessage.success('登录成功')
      
      // 检查是否完成配置向导
      const wizardCompleted = localStorage.getItem('wizard_completed')
      if (wizardCompleted) {
        router.push('/')
      } else {
        router.push('/wizard')
      }
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

// 显示重置密码对话框
const showResetDialog = () => {
  resetDialogVisible.value = true
  resetForm.verificationCode = ''
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
  
  // 生成验证码（后端API）
  api.generateResetCode().catch(err => {
    console.error('生成验证码失败:', err)
  })
}

// 重置密码
const handleReset = async () => {
  try {
    // 验证
    if (!resetForm.verificationCode) {
      ElMessage.warning('请输入验证码')
      return
    }
    if (!resetForm.newPassword || resetForm.newPassword.length < 6) {
      ElMessage.warning('密码长度为6-20位')
      return
    }
    if (resetForm.newPassword !== resetForm.confirmPassword) {
      ElMessage.warning('两次输入密码不一致')
      return
    }

    resetting.value = true

    await api.resetPassword({
      verification_code: resetForm.verificationCode,
      new_password: resetForm.newPassword
    })

    ElMessage.success('密码重置成功，请重新登录')
    resetDialogVisible.value = false
    
    // 清空登录表单
    loginForm.password = ''
    loginForm.remember = false
  } catch (error) {
    console.error('重置密码失败:', error)
    ElMessage.error(error.response?.data?.detail || '重置密码失败')
  } finally {
    resetting.value = false
  }
}

onMounted(() => {
  checkAuthStatus()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 450px;
  max-width: 100%;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.login-actions .el-button {
  width: 100%;
}

.setup-tips {
  margin-top: 20px;
}

.setup-tips ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.setup-tips li {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}
</style>
