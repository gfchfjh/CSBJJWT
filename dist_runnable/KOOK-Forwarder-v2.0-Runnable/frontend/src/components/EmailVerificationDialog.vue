<template>
  <el-dialog
    v-model="visible"
    title="邮箱验证"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="邮箱地址">
        <el-input v-model="email" disabled>
          <template #prefix>
            <el-icon><Message /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="验证码" prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入6位验证码"
          maxlength="6"
          :disabled="sending || verifying"
        >
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
          <template #append>
            <el-button
              @click="sendCode"
              :disabled="countdown > 0 || sending"
              :loading="sending"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
            </el-button>
          </template>
        </el-input>
        <div class="code-hint">
          验证码有效期10分钟，请注意查收邮件
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button
          type="primary"
          @click="verifyCode"
          :loading="verifying"
          :disabled="!form.code || form.code.length !== 6"
        >
          验证
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
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

const emit = defineEmits(['update:modelValue', 'verified'])

const visible = ref(props.modelValue)
const formRef = ref(null)
const sending = ref(false)
const verifying = ref(false)
const countdown = ref(0)
let countdownTimer = null

const form = reactive({
  code: ''
})

const rules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码必须为6位数字', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码必须为6位数字', trigger: 'blur' }
  ]
}

// 监听visible变化
watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    // 对话框关闭时清空表单
    form.code = ''
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdown.value = 0
    }
  }
})

// 发送验证码
const sendCode = async () => {
  try {
    sending.value = true
    
    const response = await api.post('/api/password-reset/send-code', {
      email: props.email
    })
    
    if (response.data.success) {
      ElMessage.success('验证码已发送到您的邮箱，请查收')
      
      // 开始倒计时
      countdown.value = 60
      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(countdownTimer)
        }
      }, 1000)
    } else {
      ElMessage.error(response.data.message || '发送验证码失败')
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error(error.response?.data?.detail || '发送验证码失败，请稍后重试')
  } finally {
    sending.value = false
  }
}

// 验证验证码
const verifyCode = async () => {
  try {
    // 先验证表单
    await formRef.value.validate()
    
    verifying.value = true
    
    const response = await api.post('/api/password-reset/verify-code', {
      email: props.email,
      code: form.code
    })
    
    if (response.data.success) {
      ElMessage.success('邮箱验证成功！')
      emit('verified', {
        email: props.email,
        resetToken: response.data.reset_token
      })
      visible.value = false
    } else {
      ElMessage.error(response.data.message || '验证失败')
    }
  } catch (error) {
    console.error('验证失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error !== 'validation-failed') {
      ElMessage.error('验证失败，请稍后重试')
    }
  } finally {
    verifying.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
}
</script>

<style scoped>
.code-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-input-group__append) {
  padding: 0 5px;
}

:deep(.el-input-group__append .el-button) {
  margin: 0;
}
</style>
