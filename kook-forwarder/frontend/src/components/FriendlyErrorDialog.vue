<!--
  友好错误提示对话框
  ✅ P0-2优化：将技术错误转换为用户友好的提示
-->
<template>
  <el-dialog
    v-model="visible"
    :title="errorData.title || '提示'"
    width="600px"
    :close-on-click-modal="false"
    class="friendly-error-dialog"
  >
    <div class="error-content">
      <!-- 错误图标和标题 -->
      <div class="error-header">
        <el-icon :size="64" :color="severityColor" class="error-icon">
          <component :is="severityIcon" />
        </el-icon>
        <h3 class="error-title">{{ errorData.title }}</h3>
      </div>
      
      <!-- 错误描述 -->
      <div class="error-message">
        <p>{{ errorData.message }}</p>
      </div>
      
      <!-- 解决方法 -->
      <div class="solution-steps" v-if="errorData.solution && errorData.solution.length > 0">
        <h4>💡 解决方法：</h4>
        <ul>
          <li v-for="(step, index) in errorData.solution" :key="index">
            {{ step }}
          </li>
        </ul>
      </div>
      
      <!-- 一键修复按钮 -->
      <div class="auto-fix-section" v-if="errorData.auto_fix">
        <el-alert
          :title="`✨ 好消息：${errorData.fix_description || '此问题可以自动修复'}`"
          type="success"
          :closable="false"
          style="margin-bottom: 15px"
        />
        
        <el-button
          type="primary"
          size="large"
          :loading="fixing"
          @click="handleAutoFix"
          style="width: 100%"
        >
          <el-icon><Tools /></el-icon>
          🔧 一键自动修复
        </el-button>
      </div>
      
      <!-- 技术详情（可折叠） -->
      <el-collapse v-model="activeCollapse" class="technical-details">
        <el-collapse-item name="technical">
          <template #title>
            <span>🔍 查看技术详情（供开发者参考）</span>
          </template>
          
          <div class="technical-error">
            <el-tag :type="getCategoryTagType(errorData.category)" size="small">
              {{ getCategoryLabel(errorData.category) }}
            </el-tag>
            
            <pre class="error-stack">{{ errorData.technical_error || '无详细信息' }}</pre>
            
            <el-button
              size="small"
              @click="copyError"
              style="margin-top: 10px"
            >
              <el-icon><CopyDocument /></el-icon>
              复制错误信息
            </el-button>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="goToHelp">
          <el-icon><QuestionFilled /></el-icon>
          查看帮助文档
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Warning,
  CircleClose,
  InfoFilled,
  CircleCheck,
  Tools,
  CopyDocument,
  QuestionFilled
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const visible = ref(false)
const errorData = ref({
  title: '',
  message: '',
  solution: [],
  auto_fix: null,
  fix_description: null,
  severity: 'error',
  category: 'unknown',
  technical_error: ''
})
const fixing = ref(false)
const activeCollapse = ref([])

// 根据严重程度获取颜色
const severityColor = computed(() => {
  const colors = {
    error: '#F56C6C',
    warning: '#E6A23C',
    info: '#409EFF',
    success: '#67C23A'
  }
  return colors[errorData.value.severity] || '#909399'
})

// 根据严重程度获取图标
const severityIcon = computed(() => {
  const icons = {
    error: CircleClose,
    warning: Warning,
    info: InfoFilled,
    success: CircleCheck
  }
  return icons[errorData.value.severity] || Warning
})

// 获取类别标签
const getCategoryLabel = (category) => {
  const labels = {
    environment: '环境问题',
    service: '服务问题',
    auth: '认证问题',
    config: '配置问题',
    network: '网络问题',
    rate_limit: '限流问题',
    media: '媒体问题',
    storage: '存储问题',
    content: '内容问题',
    permission: '权限问题',
    unknown: '未知问题'
  }
  return labels[category] || category
}

// 获取类别标签类型
const getCategoryTagType = (category) => {
  const types = {
    environment: 'danger',
    service: 'danger',
    auth: 'warning',
    config: 'warning',
    network: 'info',
    rate_limit: 'info',
    media: 'warning',
    storage: 'warning',
    content: 'info',
    permission: 'danger',
    unknown: 'info'
  }
  return types[category] || 'info'
}

// 显示错误
const showError = async (technicalError, errorType = null) => {
  try {
    // 调用后端翻译API
    const response = await api.post('/error-translator/translate', {
      technical_error: technicalError,
      error_type: errorType
    })
    
    errorData.value = response.data
    visible.value = true
  } catch (error) {
    console.error('错误翻译失败:', error)
    // 降级处理：直接显示技术错误
    errorData.value = {
      title: '发生错误',
      message: technicalError,
      solution: ['请查看日志或联系技术支持'],
      auto_fix: null,
      severity: 'error',
      category: 'unknown',
      technical_error: technicalError
    }
    visible.value = true
  }
}

// 处理自动修复
const handleAutoFix = async () => {
  fixing.value = true
  
  try {
    const fixType = errorData.value.auto_fix
    
    ElMessage.info(`正在执行自动修复：${errorData.value.fix_description}`)
    
    // 调用自动修复API
    const response = await api.post(`/environment-autofix-enhanced/auto-fix/${fixType}`)
    
    if (response.data.success) {
      ElMessage.success('✅ 自动修复成功！')
      
      // 询问是否重启应用
      if (response.data.require_restart) {
        ElMessageBox.confirm(
          '修复完成！需要重启应用才能生效，是否立即重启？',
          '需要重启',
          {
            confirmButtonText: '立即重启',
            cancelButtonText: '稍后重启',
            type: 'success'
          }
        ).then(() => {
          // 调用Electron重启API
          if (window.electron && window.electron.relaunch) {
            window.electron.relaunch()
          } else {
            ElMessage.info('请手动重启应用')
          }
        }).catch(() => {
          ElMessage.info('请稍后手动重启应用')
        })
      }
      
      visible.value = false
    } else {
      ElMessage.error(`自动修复失败：${response.data.message}`)
    }
  } catch (error) {
    ElMessage.error(`自动修复失败：${error.message}`)
  } finally {
    fixing.value = false
  }
}

// 复制错误信息
const copyError = () => {
  const errorText = `
【错误标题】${errorData.value.title}
【错误类别】${getCategoryLabel(errorData.value.category)}
【严重程度】${errorData.value.severity}
【错误描述】${errorData.value.message}
【技术详情】${errorData.value.technical_error}
【发生时间】${new Date().toLocaleString()}
  `.trim()
  
  navigator.clipboard.writeText(errorText).then(() => {
    ElMessage.success('✅ 错误信息已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 前往帮助文档
const goToHelp = () => {
  visible.value = false
  router.push('/help')
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 暴露方法供外部调用
defineExpose({
  showError
})
</script>

<style scoped>
.friendly-error-dialog :deep(.el-dialog__body) {
  padding: 30px;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 15px;
}

.error-icon {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.error-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.error-message {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  line-height: 1.6;
}

.error-message p {
  margin: 0;
  color: #606266;
  font-size: 15px;
}

.solution-steps {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background: linear-gradient(to right, #f5f7fa, #e4e7ed);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.solution-steps h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.solution-steps ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.solution-steps li {
  margin-bottom: 10px;
  padding-left: 25px;
  position: relative;
  color: #606266;
  line-height: 1.6;
}

.solution-steps li:before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
  font-size: 18px;
}

.auto-fix-section {
  padding: 20px;
  background-color: #f0f9ff;
  border-radius: 8px;
  border: 2px dashed #409eff;
}

.technical-details {
  margin-top: 10px;
}

.technical-error {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.error-stack {
  margin: 15px 0;
  padding: 15px;
  background-color: #303133;
  color: #00ff00;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .friendly-error-dialog {
    width: 95% !important;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .solution-steps li {
    font-size: 14px;
  }
}
</style>
