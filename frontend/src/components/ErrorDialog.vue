<template>
  <el-dialog
    v-model="visible"
    :title="error.title"
    width="600px"
    :close-on-click-modal="false"
    :show-close="true"
  >
    <el-alert
      :type="getSeverityType(error.severity)"
      :closable="false"
      show-icon
      class="error-alert"
    >
      <template #title>
        <div class="alert-title">{{ error.message }}</div>
      </template>
      
      <div class="error-content">
        <div class="solution-section">
          <h4>💡 解决方案：</h4>
          <pre class="solution-text">{{ error.solution }}</pre>
        </div>

        <div v-if="error.original_error" class="technical-details">
          <el-collapse>
            <el-collapse-item title="🔍 查看技术详情" name="technical">
              <div class="technical-info">
                <p><strong>错误类型：</strong>{{ error.error_type || '未知' }}</p>
                <p><strong>原始错误：</strong></p>
                <pre class="error-stack">{{ error.original_error }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-alert>

    <template #footer>
      <div class="dialog-footer">
        <el-button
          v-if="error.can_auto_fix"
          type="primary"
          size="large"
          @click="handleAutoFix"
          :loading="fixing"
        >
          <el-icon><Tools /></el-icon>
          {{ error.action_label || '自动修复' }}
        </el-button>
        
        <el-button
          size="large"
          @click="viewDetailedLogs"
        >
          <el-icon><Document /></el-icon>
          查看完整日志
        </el-button>
        
        <el-button
          size="large"
          @click="copyErrorInfo"
        >
          <el-icon><CopyDocument /></el-icon>
          复制错误信息
        </el-button>
        
        <el-button
          size="large"
          @click="visible = false"
        >
          关闭
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Tools, Document, CopyDocument } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const props = defineProps({
  error: {
    type: Object,
    required: true,
    default: () => ({
      title: '错误',
      message: '',
      solution: '',
      severity: 'error',
      can_auto_fix: false,
      action: null,
      action_label: null,
      original_error: '',
      error_type: ''
    })
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'fixed'])

const visible = ref(props.modelValue)
const fixing = ref(false)

watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 获取严重程度类型
function getSeverityType(severity) {
  const typeMap = {
    'error': 'error',
    'warning': 'warning',
    'info': 'info'
  }
  return typeMap[severity] || 'error'
}

// 自动修复
async function handleAutoFix() {
  if (!props.error.action) return
  
  fixing.value = true
  try {
    // 调用对应的修复API
    const response = await api.post(`/api/environment-autofix/${props.error.action}`)
    
    if (response.data.success) {
      ElMessage.success('修复成功！')
      emit('fixed')
      visible.value = false
    } else {
      ElMessage.error('修复失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('修复失败: ' + error.message)
  } finally {
    fixing.value = false
  }
}

// 查看详细日志
function viewDetailedLogs() {
  visible.value = false
  router.push('/logs')
}

// 复制错误信息
function copyErrorInfo() {
  const info = `
错误标题：${props.error.title}
错误信息：${props.error.message}
解决方案：${props.error.solution}
原始错误：${props.error.original_error || '无'}
错误类型：${props.error.error_type || '未知'}
`.trim()
  
  // 复制到剪贴板
  navigator.clipboard.writeText(info).then(() => {
    ElMessage.success('错误信息已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.error-alert {
  margin-bottom: 20px;
}

.alert-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
}

.error-content {
  margin-top: 15px;
}

.solution-section {
  margin-bottom: 20px;
}

.solution-section h4 {
  margin: 0 0 10px 0;
  color: #409EFF;
  font-size: 14px;
}

.solution-text {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 14px;
  color: #606266;
  margin: 0;
  font-family: inherit;
}

.technical-details {
  margin-top: 20px;
}

.technical-info {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
}

.technical-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

.technical-info strong {
  color: #303133;
}

.error-stack {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  font-family: 'Courier New', Courier, monospace;
  margin: 10px 0 0 0;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>
