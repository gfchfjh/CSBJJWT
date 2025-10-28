<template>
  <div class="progress-feedback">
    <el-card shadow="hover" :class="['progress-card', `status-${status}`]">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :class="['status-icon', `icon-${status}`]">
              <component :is="statusIcon" />
            </el-icon>
            <span class="title">{{ title }}</span>
          </div>
          <el-tag :type="statusType" size="small">
            {{ statusText }}
          </el-tag>
        </div>
      </template>

      <div class="progress-content">
        <!-- 进度条 -->
        <div v-if="showProgress" class="progress-bar-wrapper">
          <el-progress
            :percentage="progress"
            :status="progressStatus"
            :stroke-width="12"
            :show-text="true"
          >
            <template #default="{ percentage }">
              <span class="progress-text">{{ percentage }}%</span>
            </template>
          </el-progress>
          
          <div class="progress-info">
            <span class="current-step">{{ currentStep }}</span>
            <span class="elapsed-time" v-if="elapsedTime">{{ elapsedTime }}</span>
          </div>
        </div>

        <!-- 步骤列表 -->
        <div v-if="steps && steps.length > 0" class="steps-list">
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in steps"
              :key="index"
              :timestamp="step.timestamp"
              :type="getStepType(step.status)"
              :icon="getStepIcon(step.status)"
              :color="getStepColor(step.status)"
              placement="top"
            >
              <div class="step-content">
                <div class="step-title">
                  {{ step.title }}
                  <el-tag
                    v-if="step.status === 'running'"
                    type="primary"
                    size="small"
                    effect="plain"
                  >
                    进行中
                  </el-tag>
                </div>
                
                <div v-if="step.description" class="step-description">
                  {{ step.description }}
                </div>
                
                <!-- 步骤进度 -->
                <div v-if="step.status === 'running' && step.progress !== undefined" class="step-progress">
                  <el-progress
                    :percentage="step.progress"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
                
                <!-- 步骤详情（可折叠） -->
                <div v-if="step.details" class="step-details">
                  <el-collapse accordion>
                    <el-collapse-item title="查看详情">
                      <pre>{{ step.details }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
                
                <!-- 错误信息 -->
                <div v-if="step.status === 'error' && step.error" class="step-error">
                  <el-alert
                    type="error"
                    :title="step.error"
                    :closable="false"
                    show-icon
                  />
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 操作按钮 -->
        <div v-if="actions && actions.length > 0" class="action-buttons">
          <el-button
            v-for="action in actions"
            :key="action.label"
            :type="action.type || 'default'"
            :icon="action.icon"
            :loading="action.loading"
            :disabled="action.disabled"
            @click="handleAction(action)"
          >
            {{ action.label }}
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import {
  Loading,
  CircleCheck,
  CircleClose,
  Warning,
  Clock,
  Check,
  Close,
  QuestionFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '操作进度'
  },
  status: {
    type: String,
    default: 'pending', // pending, running, success, error, warning
    validator: (value) => ['pending', 'running', 'success', 'error', 'warning'].includes(value)
  },
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  currentStep: {
    type: String,
    default: ''
  },
  steps: {
    type: Array,
    default: () => []
  },
  actions: {
    type: Array,
    default: () => []
  },
  showProgress: {
    type: Boolean,
    default: true
  },
  autoUpdateTime: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['action-click'])

// 开始时间
const startTime = ref(Date.now())
const elapsedTime = ref('')
let timeInterval = null

// 状态图标
const statusIcon = computed(() => {
  const iconMap = {
    pending: QuestionFilled,
    running: Loading,
    success: CircleCheck,
    error: CircleClose,
    warning: Warning
  }
  return iconMap[props.status] || QuestionFilled
})

// 状态类型
const statusType = computed(() => {
  const typeMap = {
    pending: 'info',
    running: 'primary',
    success: 'success',
    error: 'danger',
    warning: 'warning'
  }
  return typeMap[props.status] || 'info'
})

// 状态文本
const statusText = computed(() => {
  const textMap = {
    pending: '等待中',
    running: '进行中',
    success: '已完成',
    error: '失败',
    warning: '警告'
  }
  return textMap[props.status] || '未知'
})

// 进度条状态
const progressStatus = computed(() => {
  if (props.status === 'success') return 'success'
  if (props.status === 'error') return 'exception'
  if (props.status === 'warning') return 'warning'
  return undefined
})

// 获取步骤类型
const getStepType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'primary',
    success: 'success',
    error: 'danger',
    warning: 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取步骤图标
const getStepIcon = (status) => {
  const iconMap = {
    pending: Clock,
    running: Loading,
    success: Check,
    error: Close,
    warning: Warning
  }
  return iconMap[status] || Clock
}

// 获取步骤颜色
const getStepColor = (status) => {
  const colorMap = {
    pending: '#909399',
    running: '#409eff',
    success: '#67c23a',
    error: '#f56c6c',
    warning: '#e6a23c'
  }
  return colorMap[status]
}

// 处理操作点击
const handleAction = (action) => {
  emit('action-click', action)
  if (action.onClick) {
    action.onClick()
  }
}

// 更新经过时间
const updateElapsedTime = () => {
  const elapsed = Date.now() - startTime.value
  const seconds = Math.floor(elapsed / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) {
    elapsedTime.value = `已用时: ${hours}小时${minutes % 60}分${seconds % 60}秒`
  } else if (minutes > 0) {
    elapsedTime.value = `已用时: ${minutes}分${seconds % 60}秒`
  } else {
    elapsedTime.value = `已用时: ${seconds}秒`
  }
}

// 监听状态变化
watch(() => props.status, (newStatus) => {
  if (newStatus === 'running' && props.autoUpdateTime) {
    // 开始计时
    startTime.value = Date.now()
    timeInterval = setInterval(updateElapsedTime, 1000)
  } else if (newStatus === 'success' || newStatus === 'error') {
    // 停止计时
    if (timeInterval) {
      clearInterval(timeInterval)
      updateElapsedTime() // 最后更新一次
    }
  }
})

// 组件卸载时清理
onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped lang="scss">
.progress-feedback {
  .progress-card {
    transition: all 0.3s ease;
    
    &.status-pending {
      border-left: 4px solid #909399;
    }
    
    &.status-running {
      border-left: 4px solid #409eff;
      
      .status-icon {
        animation: rotate 1.5s linear infinite;
      }
    }
    
    &.status-success {
      border-left: 4px solid #67c23a;
    }
    
    &.status-error {
      border-left: 4px solid #f56c6c;
    }
    
    &.status-warning {
      border-left: 4px solid #e6a23c;
    }
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .status-icon {
        font-size: 24px;
        
        &.icon-pending { color: #909399; }
        &.icon-running { color: #409eff; }
        &.icon-success { color: #67c23a; }
        &.icon-error { color: #f56c6c; }
        &.icon-warning { color: #e6a23c; }
      }
      
      .title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .progress-content {
    .progress-bar-wrapper {
      margin-bottom: 20px;
      
      .progress-info {
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 13px;
        color: #606266;
        
        .current-step {
          font-weight: 500;
        }
        
        .elapsed-time {
          color: #909399;
        }
      }
    }
    
    .steps-list {
      margin-top: 20px;
      
      .step-content {
        .step-title {
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .step-description {
          color: #606266;
          font-size: 13px;
          margin-bottom: 8px;
        }
        
        .step-progress {
          margin: 10px 0;
        }
        
        .step-details {
          margin-top: 10px;
          
          pre {
            background: #f5f7fa;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #606266;
            overflow-x: auto;
            max-height: 200px;
          }
        }
        
        .step-error {
          margin-top: 10px;
        }
      }
    }
    
    .action-buttons {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
