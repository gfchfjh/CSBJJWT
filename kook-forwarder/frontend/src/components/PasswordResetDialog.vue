<template>
  <el-dialog
    v-model="visible"
    title="重置密码"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-alert
      v-if="!emailVerified"
      title="请先验证邮箱"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px"
    >
      为了确保安全，请先验证您的邮箱地址后再重置密码
    </el-alert>

    <el-steps :active="currentStep" finish-status="success" align-center style="margin-bottom: 30px">
      <el-step title="验证邮箱" />
      <el-step title="设置新密码" />
      <el-step title="完成" />
    </el-steps>

    <!-- 步骤1: 验证邮箱 -->
    <div v-if="currentStep === 0">
      <el-form :model="emailForm" label-width="100px">
        <el-form-item label="邮箱地址">
          <el-input v-model="email" disabled>
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <div style="text-align: center; margin-top: 30px">
        <el-button
          type="primary"
          @click="showEmailVerification = true"
        >
          开始验证
        </el-button>
      </div>
    </div>

    <!-- 步骤2: 设置新密码 -->
    <div v-if="currentStep === 1">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（6-128位）"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-alert
          title="密码安全提示"
          type="info"
          :closable="false"
          style="margin-top: 10px"
        >
          <ul style="margin: 5px 0; padding-left: 20px">
            <li>密码长度应在6-128位之间</li>
            <li>建议包含字母、数字和特殊字符</li>
            <li>不要使用过于简单的密码</li>
          </ul>
        </el-alert>
      </el-form>

      <div style="text-align: center; margin-top: 30px">
        <el-button @click="currentStep = 0">上一步</el-button>
        <el-button
          type="primary"
          @click="resetPassword"
          :loading="resetting"
        >
          重置密码
        </el-button>
      </div>
    </div>

    <!-- 步骤3: 完成 -->
    <div v-if="currentStep === 2" style="text-align: center; padding: 30px 0">
      <el-result
        icon="success"
        title="密码重置成功！"
        sub-title="请使用新密码重新登录"
      >
        <template #extra>
          <el-button type="primary" @click="handleComplete">
            确定
          </el-button>
        </template>
      </el-result>
    </div>

    <template #footer v-if="currentStep !== 1 && currentStep !== 2">
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
      </div>
    </template>

    <!-- 邮箱验证对话框 -->
    <EmailVerificationDialog
      v-model="showEmailVerification"
      :email="email"
      @verified="handleEmailVerified"
    />
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import EmailVerificationDialog from './EmailVerificationDialog.vue'
import api from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  email: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
const currentStep = ref(0)
const emailVerified = ref(false)
const showEmailVerification = ref(false)
const resetting = ref(false)
const resetToken = ref('')

const passwordFormRef = ref(null)

const emailForm = reactive({
  email: props.email
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度应在6-128位之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 监听visible变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // 重置状态
    currentStep.value = 0
    emailVerified.value = false
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    resetToken.value = ''
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 邮箱验证成功
const handleEmailVerified = (data) => {
  emailVerified.value = true
  resetToken.value = data.resetToken
  currentStep.value = 1
  ElMessage.success('邮箱验证成功，请设置新密码')
}

// 重置密码
const resetPassword = async () => {
  try {
    // 先验证表单
    await passwordFormRef.value.validate()
    
    if (!resetToken.value) {
      ElMessage.error('验证令牌已过期，请重新验证邮箱')
      currentStep.value = 0
      return
    }
    
    resetting.value = true
    
    const response = await api.post('/api/password-reset/reset-password', {
      email: props.email,
      code: resetToken.value,
      new_password: passwordForm.newPassword
    })
    
    if (response.data.success) {
      currentStep.value = 2
    } else {
      ElMessage.error(response.data.message || '密码重置失败')
    }
  } catch (error) {
    console.error('密码重置失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
      // 如果是令牌过期，返回第一步
      if (error.response.data.detail.includes('过期')) {
        currentStep.value = 0
        emailVerified.value = false
        resetToken.value = ''
      }
    } else if (error !== 'validation-failed') {
      ElMessage.error('密码重置失败，请稍后重试')
    }
  } finally {
    resetting.value = false
  }
}

// 完成
const handleComplete = () => {
  visible.value = false
  emit('success')
  
  // 如果在登录页，可能需要刷新或跳转
  setTimeout(() => {
    ElMessage.info('请使用新密码重新登录')
  }, 300)
}

// 关闭对话框
const handleClose = () => {
  if (currentStep.value === 2) {
    // 完成状态关闭时也触发success
    emit('success')
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-alert__content) {
  line-height: 1.6;
}

:deep(.el-steps) {
  padding: 0 20px;
}
</style>
