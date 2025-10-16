<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <el-icon class="lock-icon"><Lock /></el-icon>
          <h2>KOOK消息转发系统</h2>
        </div>
      </template>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-width="0"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          :closable="false"
          class="error-alert"
        />
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入应用密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="loginForm.remember">
            记住密码（30天）
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '验证中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="help-links">
        <el-link type="primary" @click="showHelp = true">
          <el-icon><QuestionFilled /></el-icon>
          忘记密码？
        </el-link>
        <el-link type="info" href="https://github.com/yourusername/kook-forwarder" target="_blank">
          <el-icon><Document /></el-icon>
          查看文档
        </el-link>
      </div>
    </el-card>
    
    <!-- 帮助对话框 -->
    <el-dialog
      v-model="showHelp"
      title="密码帮助"
      width="500px"
    >
      <el-alert
        title="忘记密码"
        type="warning"
        :closable="false"
      >
        <p>如果忘记了应用密码，可以通过以下方式重置：</p>
        <ol>
          <li>关闭应用</li>
          <li>找到配置文件位置：
            <ul>
              <li>Windows: <code>C:\Users\[用户名]\Documents\KookForwarder\data\config.db</code></li>
              <li>macOS: <code>/Users/[用户名]/Documents/KookForwarder/data/config.db</code></li>
              <li>Linux: <code>/home/[用户名]/Documents/KookForwarder/data/config.db</code></li>
            </ul>
          </li>
          <li>删除配置文件（会清除所有配置，请提前备份）</li>
          <li>重新启动应用，将不再需要密码</li>
        </ol>
        <p><strong>或者</strong>，联系管理员获取密码。</p>
      </el-alert>
      
      <template #footer>
        <el-button @click="showHelp = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Key, QuestionFilled, Document } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const showHelp = ref(false)

const loginForm = reactive({
  password: '',
  remember: false
})

const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
}

// 检查是否已记住密码
onMounted(() => {
  const savedPassword = localStorage.getItem('app_password')
  const savedExpiry = localStorage.getItem('app_password_expiry')
  
  if (savedPassword && savedExpiry) {
    const expiryTime = parseInt(savedExpiry)
    if (Date.now() < expiryTime) {
      // 密码未过期，自动填充
      loginForm.password = savedPassword
      loginForm.remember = true
    } else {
      // 密码已过期，清除
      localStorage.removeItem('app_password')
      localStorage.removeItem('app_password_expiry')
    }
  }
})

async function handleLogin() {
  errorMessage.value = ''
  
  // 验证表单
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
  } catch (error) {
    return
  }
  
  loading.value = true
  
  try {
    // 调用后端验证密码
    const response = await api.post('/api/auth/verify-password', {
      password: loginForm.password
    })
    
    if (response.data.success) {
      // 密码正确
      
      // 如果选择记住密码
      if (loginForm.remember) {
        const expiryTime = Date.now() + (30 * 24 * 60 * 60 * 1000) // 30天
        localStorage.setItem('app_password', loginForm.password)
        localStorage.setItem('app_password_expiry', expiryTime.toString())
      } else {
        // 清除已保存的密码
        localStorage.removeItem('app_password')
        localStorage.removeItem('app_password_expiry')
      }
      
      // 保存登录状态
      sessionStorage.setItem('is_authenticated', 'true')
      
      ElMessage.success('登录成功')
      
      // 跳转到主页
      router.push('/')
    } else {
      errorMessage.value = '密码错误，请重试'
    }
  } catch (error) {
    console.error('登录失败:', error)
    
    if (error.response?.status === 401) {
      errorMessage.value = '密码错误'
    } else if (error.response?.status === 403) {
      errorMessage.value = '密码保护未启用'
    } else {
      errorMessage.value = '登录失败：' + (error.response?.data?.detail || error.message)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.login-card {
  width: 90%;
  max-width: 420px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.lock-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 10px;
}

.card-header h2 {
  margin: 10px 0 0 0;
  color: #333;
  font-size: 24px;
}

.login-form {
  padding: 20px 0;
}

.error-alert {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 8px;
}

.help-links {
  display: flex;
  justify-content: space-between;
  padding: 15px 0 0 0;
  border-top: 1px solid #eee;
}

.help-links .el-link {
  font-size: 14px;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: -5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-50px) rotate(90deg);
  }
  50% {
    transform: translateY(0) rotate(180deg);
  }
  75% {
    transform: translateY(50px) rotate(270deg);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .login-card {
    width: 95%;
  }
  
  .card-header h2 {
    font-size: 20px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .card-header h2 {
    color: #fff;
  }
}
</style>
