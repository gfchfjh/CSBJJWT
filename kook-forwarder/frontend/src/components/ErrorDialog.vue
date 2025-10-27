<template>
  <el-dialog
    v-model="visible"
    :title="errorData.title || '发生错误'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="error-dialog"
  >
    <!-- 严重程度标识 -->
    <div class="severity-badge" :class="`severity-${errorData.severity}`">
      <el-icon>
        <WarningFilled v-if="errorData.severity === 'error'" />
        <Warning v-else-if="errorData.severity === 'warning'" />
        <InfoFilled v-else />
      </el-icon>
      <span>{{ severityText }}</span>
    </div>

    <!-- 错误消息 -->
    <div class="error-message">
      {{ errorData.message }}
    </div>

    <!-- 解决方案 -->
    <div v-if="errorData.solution && errorData.solution.length > 0" class="solution-section">
      <h4>💡 解决方案：</h4>
      <ul class="solution-list">
        <li v-for="(step, index) in errorData.solution" :key="index">
          {{ step }}
        </li>
      </ul>
    </div>

    <!-- 自动修复按钮 -->
    <div v-if="errorData.auto_fix" class="auto-fix-section">
      <el-button
        type="primary"
        size="large"
        :loading="fixing"
        @click="autoFix"
      >
        <el-icon><Tools /></el-icon>
        {{ errorData.fix_description || '一键自动修复' }}
      </el-button>
      <p class="fix-hint">点击后系统将尝试自动解决此问题</p>
    </div>

    <!-- 技术详情（可折叠） -->
    <el-collapse v-if="errorData.technical_error" class="technical-details">
      <el-collapse-item>
        <template #title>
          <span class="collapse-title">
            <el-icon><Document /></el-icon>
            查看技术详情
          </span>
        </template>
        <div class="technical-content">
          <pre>{{ errorData.technical_error }}</pre>
          <el-button
            size="small"
            text
            @click="copyError"
          >
            <el-icon><CopyDocument /></el-icon>
            复制错误信息
          </el-button>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">
          {{ errorData.auto_fix ? '稍后处理' : '关闭' }}
        </el-button>
        <el-button
          v-if="showHelpButton"
          type="info"
          @click="goToHelp"
        >
          <el-icon><QuestionFilled /></el-icon>
          查看帮助文档
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  errorData: {
    type: Object,
    default: () => ({
      title: '发生错误',
      message: '系统遇到了一个问题',
      solution: [],
      auto_fix: null,
      fix_description: null,
      severity: 'error',
      category: 'unknown',
      technical_error: ''
    })
  }
})

const emit = defineEmits(['update:modelValue', 'fixed'])

const router = useRouter()
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const fixing = ref(false)

// 严重程度文本
const severityText = computed(() => {
  const map = {
    'error': '🔴 严重错误',
    'warning': '🟡 警告',
    'info': '🔵 提示'
  }
  return map[props.errorData.severity] || '提示'
})

// 是否显示帮助按钮
const showHelpButton = computed(() => {
  return props.errorData.category && props.errorData.category !== 'unknown'
})

// 自动修复
const autoFix = async () => {
  if (!props.errorData.auto_fix) {
    return
  }

  try {
    fixing.value = true
    
    // 调用后端自动修复API
    const response = await api.post('/api/environment-autofix-enhanced/auto-fix', {
      fix_type: props.errorData.auto_fix,
      error_context: props.errorData.technical_error
    })

    if (response.success) {
      ElMessage.success('✅ ' + (response.message || '自动修复成功'))
      emit('fixed', response)
      
      // 3秒后自动关闭对话框
      setTimeout(() => {
        close()
      }, 3000)
    } else {
      ElMessage.error('自动修复失败：' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('自动修复失败:', error)
    ElMessage.error('自动修复失败：' + (error.response?.data?.detail || error.message))
  } finally {
    fixing.value = false
  }
}

// 复制错误信息
const copyError = async () => {
  try {
    await navigator.clipboard.writeText(props.errorData.technical_error)
    ElMessage.success('错误信息已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

// 前往帮助文档
const goToHelp = () => {
  // 根据错误类别跳转到对应帮助页
  const categoryRouteMap = {
    'environment': '/help?section=environment',
    'service': '/help?section=service',
    'auth': '/help?section=login',
    'config': '/help?section=config',
    'network': '/help?section=network',
    'permission': '/help?section=permission',
    'storage': '/help?section=storage'
  }

  const route = categoryRouteMap[props.errorData.category] || '/help'
  router.push(route)
  close()
}

// 关闭对话框
const close = () => {
  visible.value = false
}

// 暴露方法给父组件
defineExpose({
  close
})
</script>

<style scoped>
.error-dialog {
  --el-dialog-padding-primary: 20px;
}

.severity-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 20px;
}

.severity-error {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.severity-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #e6a23c;
}

.severity-info {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #909399;
}

.error-message {
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.solution-section {
  margin: 20px 0;
}

.solution-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 12px;
}

.solution-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.solution-list li {
  padding: 10px 0;
  padding-left: 24px;
  position: relative;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  border-bottom: 1px dashed #e4e7ed;
}

.solution-list li:last-child {
  border-bottom: none;
}

.solution-list li:before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #409eff;
  font-weight: bold;
}

.auto-fix-section {
  margin: 24px 0;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  text-align: center;
}

.auto-fix-section .el-button {
  width: 100%;
  max-width: 300px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.fix-hint {
  margin-top: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.technical-details {
  margin-top: 24px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #909399;
}

.technical-content {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.technical-content pre {
  margin: 0;
  padding: 12px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.dialog-footer .el-button {
  flex: 1;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .error-message {
    background-color: #1d1e1f;
    border-left-color: #409eff;
  }

  .technical-content {
    background-color: #1d1e1f;
  }

  .technical-content pre {
    background-color: #141414;
    border-color: #4c4d4f;
    color: #e5e5e5;
  }
}
</style>
