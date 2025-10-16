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
        </el-descriptions>
      </div>

      <div class="captcha-image" v-if="imageUrl">
        <el-image
          :src="imageUrl"
          fit="contain"
          style="max-width: 100%; max-height: 200px"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>验证码加载失败</span>
            </div>
          </template>
        </el-image>
      </div>

      <el-form :model="form" label-width="100px" style="margin-top: 20px">
        <el-form-item label="验证码">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            clearable
            @keyup.enter="submitCaptcha"
            autofocus
          />
        </el-form-item>
      </el-form>

      <div class="tips">
        <el-text type="info" size="small">
          💡 提示：请仔细查看图片，输入验证码后点击提交
        </el-text>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="primary"
          @click="submitCaptcha"
          :loading="submitting"
          :disabled="!form.code"
        >
          提交
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
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

const form = ref({
  code: ''
})

// 监听visible变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    // 打开对话框时重置表单
    form.value.code = ''
    submitting.value = false
  }
})

// 监听对话框关闭
watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '--'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// 提交验证码 - 使用HTTP API
const submitCaptcha = async () => {
  if (!form.value.code) {
    ElMessage.warning('请输入验证码')
    return
  }

  submitting.value = true

  try {
    // 通过HTTP API提交验证码
    await api.submitCaptcha(props.accountId, form.value.code)
    
    ElMessage.success('验证码已提交')
    emit('submit', form.value.code)
    dialogVisible.value = false
  } catch (error) {
    console.error('提交验证码失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
  dialogVisible.value = false
}
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
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
