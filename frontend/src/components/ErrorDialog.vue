<template>
  <el-dialog
    v-model="visible"
    :title="errorData.title || '发生错误'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="error-dialog"
  >
    <div class="error-content">
      <!-- 严重程度指示器 -->
      <div class="severity-indicator" :class="`severity-${severity}`">
        <el-icon :size="40">
          <component :is="severityIcon" />
        </el-icon>
        <span class="severity-text">{{ severityText }}</span>
      </div>

      <!-- 错误消息 -->
      <div class="error-message">
        <el-alert
          :type="alertType"
          :closable="false"
          show-icon
        >
          <template #title>
            {{ errorData.error || errorData.title }}
          </template>
          <div class="message-content">
            <p v-for="(line, index) in formattedMessage" :key="index">
              {{ line }}
            </p>
          </div>
        </el-alert>
      </div>

      <!-- 建议操作 -->
      <div v-if="suggestedActions.length > 0" class="suggested-actions">
        <h4>💡 建议操作：</h4>
        <el-space wrap>
          <el-button
            v-for="(action, index) in suggestedActions"
            :key="index"
            size="small"
            @click="handleAction(action)"
          >
            {{ action }}
          </el-button>
        </el-space>
      </div>

      <!-- 技术详情（可折叠） -->
      <div v-if="errorData.technical_info || errorData.technical_detail" class="technical-details">
        <el-collapse v-model="showTechnical">
          <el-collapse-item name="1">
            <template #title>
              <div class="technical-header">
                <el-icon><InfoFilled /></el-icon>
                <span>技术详情（给开发者）</span>
              </div>
            </template>
            <el-input
              :model-value="technicalDetail"
              type="textarea"
              :rows="6"
              readonly
              class="technical-input"
            />
            <el-button
              size="small"
              @click="copyTechnicalDetail"
              style="margin-top: 10px;"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制技术详情
            </el-button>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">
          关闭
        </el-button>
        <el-button type="primary" @click="handleRetry" v-if="retryable">
          <el-icon><Refresh /></el-icon>
          重试
        </el-button>
        <el-button @click="openHelp">
          <el-icon><QuestionFilled /></el-icon>
          查看帮助
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CircleCloseFilled,
  WarningFilled,
  InfoFilled,
  Refresh,
  QuestionFilled,
  DocumentCopy
} from '@element-plus/icons-vue'

const props = defineProps({
  error: {
    type: Object,
    required: false,
    default: () => ({})
  },
  errorData: {
    type: Object,
    required: false,
    default: () => ({})
  },
  retryable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'retry'])

const visible = ref(true)
const showTechnical = ref([])

const errorData = computed(() => props.error || props.errorData || {})

const severity = computed(() => {
  return errorData.value.severity || 'error'
})

const severityIcon = computed(() => {
  const icons = {
    'error': CircleCloseFilled,
    'warning': WarningFilled,
    'info': InfoFilled
  }
  return icons[severity.value] || CircleCloseFilled
})

const severityText = computed(() => {
  const texts = {
    'error': '错误',
    'warning': '警告',
    'info': '提示'
  }
  return texts[severity.value] || '错误'
})

const alertType = computed(() => {
  return severity.value === 'info' ? 'info' : (severity.value === 'warning' ? 'warning' : 'error')
})

const formattedMessage = computed(() => {
  const msg = errorData.value.error_detail || errorData.value.message || '发生未知错误'
  return msg.split('\n').filter(line => line.trim())
})

const suggestedActions = computed(() => {
  return errorData.value.suggested_actions || errorData.value.actions || []
})

const technicalDetail = computed(() => {
  return errorData.value.technical_info || errorData.value.technical_detail || 'No technical details available'
})

const handleClose = () => {
  visible.value = false
  emit('close')
}

const handleRetry = () => {
  visible.value = false
  emit('retry')
}

const handleAction = (action) => {
  console.log('执行建议操作:', action)
  
  // 根据不同的操作执行不同的逻辑
  const actionMap = {
    '重启系统': () => window.location.reload(),
    '刷新页面': () => window.location.reload(),
    '返回首页': () => window.location.href = '/',
    '查看文档': () => openHelp(),
    '查看帮助': () => openHelp(),
    '重新获取Cookie': () => {
      // TODO: 跳转到Cookie获取页面
      ElMessage.info('请前往账号管理页面重新获取Cookie')
    },
    '检查网络': () => {
      ElMessage.info('请检查网络连接是否正常')
    }
  }
  
  const handler = actionMap[action]
  if (handler) {
    handler()
  } else {
    ElMessage.info(`建议操作：${action}`)
  }
}

const copyTechnicalDetail = async () => {
  try {
    await navigator.clipboard.writeText(technicalDetail.value)
    ElMessage.success('技术详情已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const openHelp = () => {
  // TODO: 打开帮助文档
  window.open('https://github.com/gfchfjh/CSBJJWT/blob/main/docs/FAQ-常见问题.md', '_blank')
}
</script>

<style scoped>
.error-dialog :deep(.el-dialog__body) {
  padding: 20px 30px;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.severity-indicator {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  font-weight: 600;
}

.severity-error {
  background: #fef0f0;
  color: #f56c6c;
}

.severity-warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.severity-info {
  background: #f4f4f5;
  color: #909399;
}

.severity-text {
  font-size: 18px;
}

.error-message {
  margin: 0;
}

.message-content p {
  margin: 5px 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.suggested-actions {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.suggested-actions h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.technical-details {
  margin-top: 10px;
}

.technical-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.technical-input :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
