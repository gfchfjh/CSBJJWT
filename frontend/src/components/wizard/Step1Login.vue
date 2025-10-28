<template>
  <div class="step1-login">
    <h2>📧 步骤1: 登录KOOK账号</h2>
    <p class="step-desc">选择以下任一方式登录，推荐使用Cookie导入（更快更安全）</p>

    <!-- 登录方式切换 -->
    <el-radio-group v-model="loginMethod" size="large" class="login-method-selector">
      <el-radio-button value="cookie">
        <el-icon><DocumentCopy /></el-icon>
        Cookie导入（推荐）
      </el-radio-button>
      <el-radio-button value="password">
        <el-icon><Lock /></el-icon>
        账号密码登录
      </el-radio-button>
    </el-radio-group>

    <!-- Cookie导入方式 -->
    <div v-if="loginMethod === 'cookie'" class="cookie-import-section">
      <el-alert
        title="💡 提示：使用Chrome扩展可一键导出Cookie"
        type="success"
        :closable="false"
        show-icon
      >
        <template #default>
          <p>1. 安装Chrome扩展：<el-link type="primary" @click="openExtensionGuide">查看教程</el-link></p>
          <p>2. 登录KOOK网页版：<el-link href="https://www.kookapp.cn" target="_blank">www.kookapp.cn</el-link></p>
          <p>3. 点击扩展图标，自动导入到本系统</p>
        </template>
      </el-alert>

      <el-divider>或手动粘贴Cookie</el-divider>

      <!-- Cookie输入框 -->
      <el-form :model="cookieForm" ref="cookieFormRef" :rules="cookieRules" label-position="top">
        <el-form-item label="Cookie内容（JSON格式）" prop="cookieData">
          <el-input
            v-model="cookieForm.cookieData"
            type="textarea"
            :rows="6"
            placeholder='粘贴Cookie JSON数据，例如：
[
  {"name": "token", "value": "xxxxx", "domain": ".kookapp.cn"},
  {"name": "session", "value": "yyyyy", "domain": ".kookapp.cn"}
]'
          />
        </el-form-item>

        <el-form-item label="或拖拽JSON文件到此处">
          <el-upload
            drag
            accept=".json,.txt"
            :auto-upload="false"
            :on-change="handleFileUpload"
            :show-file-list="false"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此 或 <em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleCookieLogin"
          style="width: 100%"
        >
          <el-icon v-if="!loading"><Check /></el-icon>
          验证并登录
        </el-button>
      </el-form>
    </div>

    <!-- 账号密码登录方式 -->
    <div v-else class="password-login-section">
      <el-alert
        title="⚠️ 注意：账号密码登录可能需要验证码"
        type="warning"
        :closable="false"
        show-icon
      />

      <el-form
        :model="passwordForm"
        ref="passwordFormRef"
        :rules="passwordRules"
        label-position="top"
        style="margin-top: 20px"
      >
        <el-form-item label="KOOK邮箱" prop="email">
          <el-input
            v-model="passwordForm.email"
            placeholder="your-email@example.com"
            size="large"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="passwordForm.password"
            type="password"
            placeholder="输入KOOK密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handlePasswordLogin"
          style="width: 100%"
        >
          <el-icon v-if="!loading"><Check /></el-icon>
          登录并继续
        </el-button>
      </el-form>
    </div>

    <!-- 底部操作 -->
    <div class="step-actions">
      <el-button size="large" @click="$emit('skip')">
        跳过向导
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DocumentCopy,
  Lock,
  UploadFilled,
  Check,
  Message
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'skip'])

// 登录方式
const loginMethod = ref('cookie')

// Loading状态
const loading = ref(false)

// Cookie表单
const cookieForm = ref({
  cookieData: ''
})

const cookieFormRef = ref(null)

const cookieRules = {
  cookieData: [
    { required: true, message: '请输入Cookie数据', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        try {
          const cookies = JSON.parse(value)
          if (!Array.isArray(cookies)) {
            callback(new Error('Cookie必须是数组格式'))
          } else if (cookies.length === 0) {
            callback(new Error('Cookie数组不能为空'))
          } else {
            callback()
          }
        } catch (e) {
          callback(new Error('Cookie格式错误，必须是有效的JSON'))
        }
      },
      trigger: 'blur'
    }
  ]
}

// 密码表单
const passwordForm = ref({
  email: '',
  password: ''
})

const passwordFormRef = ref(null)

const passwordRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

// Cookie登录
const handleCookieLogin = async () => {
  try {
    await cookieFormRef.value.validate()
    
    loading.value = true
    
    // 解析Cookie
    const cookies = JSON.parse(cookieForm.value.cookieData)
    
    // 提交到后端
    const response = await api.post('/api/accounts/cookie-login', {
      cookies: cookies
    })
    
    if (response.data.success) {
      ElMessage.success('Cookie验证成功！')
      
      // 传递账号ID到下一步
      emit('next', {
        accountId: response.data.account_id,
        email: response.data.email
      })
    } else {
      ElMessage.error(response.data.message || 'Cookie无效或已过期')
    }
    
  } catch (error) {
    if (error.errors) {
      // 表单验证错误
      return
    }
    console.error('Cookie登录失败:', error)
    ElMessage.error('登录失败：' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 账号密码登录
const handlePasswordLogin = async () => {
  try {
    await passwordFormRef.value.validate()
    
    loading.value = true
    
    const response = await api.post('/api/accounts/password-login', {
      email: passwordForm.value.email,
      password: passwordForm.value.password
    })
    
    if (response.data.success) {
      ElMessage.success('登录成功！')
      
      emit('next', {
        accountId: response.data.account_id,
        email: passwordForm.value.email
      })
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
    
  } catch (error) {
    if (error.errors) {
      return
    }
    console.error('密码登录失败:', error)
    ElMessage.error('登录失败：' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 文件上传
const handleFileUpload = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      const content = e.target.result
      // 验证是否是有效JSON
      JSON.parse(content)
      cookieForm.value.cookieData = content
      ElMessage.success('文件加载成功！')
    } catch (error) {
      ElMessage.error('文件格式错误，必须是有效的JSON文件')
    }
  }
  
  reader.readAsText(file.raw)
}

// 打开扩展教程
const openExtensionGuide = () => {
  window.open('/help/cookie-guide', '_blank')
}
</script>

<style scoped>
.step1-login h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: #303133;
}

.step-desc {
  color: #909399;
  margin: 0 0 30px 0;
}

.login-method-selector {
  width: 100%;
  margin-bottom: 30px;
}

.login-method-selector :deep(.el-radio-button__inner) {
  width: 100%;
  padding: 20px 30px;
  font-size: 16px;
}

.cookie-import-section,
.password-login-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-actions {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

/* 深色主题 */
.dark .step1-login h2 {
  color: #e5eaf3;
}
</style>
