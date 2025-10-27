<template>
  <div class="startup-check-container">
    <el-card class="check-card" shadow="always">
      <div class="header">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
        <h1>🚀 KOOK消息转发系统</h1>
        <p class="version">v8.0.0</p>
      </div>

      <!-- 检查进度 -->
      <div class="check-progress">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="环境检测" />
          <el-step title="准备浏览器" />
          <el-step title="启动服务" />
        </el-steps>
      </div>

      <!-- 检查详情 -->
      <div class="check-details">
        <transition-group name="list" tag="div">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="task-item"
            :class="task.status"
          >
            <div class="task-icon">
              <el-icon v-if="task.status === 'success'" :size="20" color="#67C23A">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="task.status === 'loading'" :size="20" color="#409EFF" class="rotating">
                <Loading />
              </el-icon>
              <el-icon v-else-if="task.status === 'error'" :size="20" color="#F56C6C">
                <CircleClose />
              </el-icon>
              <el-icon v-else :size="20" color="#909399">
                <Clock />
              </el-icon>
            </div>
            
            <div class="task-content">
              <div class="task-name">{{ task.name }}</div>
              <div class="task-message">{{ task.message }}</div>
              
              <!-- 进度条（下载时） -->
              <el-progress
                v-if="task.progress !== undefined"
                :percentage="task.progress"
                :status="task.status === 'error' ? 'exception' : undefined"
              />
              
              <!-- 操作按钮 -->
              <div v-if="task.actions" class="task-actions">
                <el-button
                  v-for="action in task.actions"
                  :key="action.label"
                  :type="action.type"
                  size="small"
                  @click="handleAction(task.id, action.action)"
                >
                  {{ action.label }}
                </el-button>
              </div>
            </div>
          </div>
        </transition-group>
      </div>

      <!-- 总体状态 -->
      <div class="overall-status" v-if="overallStatus">
        <el-alert
          :title="overallStatus.title"
          :type="overallStatus.type"
          :description="overallStatus.description"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 底部按钮 -->
      <div class="footer-actions">
        <el-button
          v-if="checkComplete && !checkSuccess"
          @click="retryCheck"
        >
          <el-icon><Refresh /></el-icon>
          重新检测
        </el-button>
        
        <el-button
          v-if="checkComplete && checkSuccess"
          type="primary"
          size="large"
          @click="proceedToWizard"
        >
          继续配置
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
        
        <el-button
          v-if="checkComplete && checkSuccess"
          size="large"
          @click="skipToMain"
        >
          跳过向导
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import {
  CircleCheck, CircleClose, Loading, Clock, Refresh, ArrowRight
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const currentStep = ref(0)
const tasks = ref([])
const checkComplete = ref(false)
const checkSuccess = ref(false)

// 初始化任务列表
const initTasks = () => {
  tasks.value = [
    {
      id: 'python',
      name: 'Python环境',
      message: '等待检测...',
      status: 'pending'
    },
    {
      id: 'chromium',
      name: 'Chromium浏览器',
      message: '等待检测...',
      status: 'pending',
      progress: undefined
    },
    {
      id: 'redis',
      name: 'Redis服务',
      message: '等待检测...',
      status: 'pending'
    },
    {
      id: 'network',
      name: '网络连接',
      message: '等待检测...',
      status: 'pending'
    },
    {
      id: 'ports',
      name: '端口检查',
      message: '等待检测...',
      status: 'pending'
    },
    {
      id: 'disk_space',
      name: '磁盘空间',
      message: '等待检测...',
      status: 'pending'
    }
  ]
}

const updateTask = (id, updates) => {
  const task = tasks.value.find(t => t.id === id)
  if (task) {
    Object.assign(task, updates)
  }
}

const overallStatus = computed(() => {
  if (!checkComplete.value) return null
  
  if (checkSuccess.value) {
    return {
      title: '✅ 环境检测通过',
      type: 'success',
      description: '所有环境准备就绪，可以开始配置'
    }
  } else {
    const errorTasks = tasks.value.filter(t => t.status === 'error')
    const warningTasks = tasks.value.filter(t => t.status === 'warning')
    
    if (errorTasks.length > 0) {
      return {
        title: '❌ 环境检测未通过',
        type: 'error',
        description: `发现 ${errorTasks.length} 个错误，请修复后重试`
      }
    } else if (warningTasks.length > 0) {
      return {
        title: '⚠️ 环境检测完成（有警告）',
        type: 'warning',
        description: `发现 ${warningTasks.length} 个警告，建议修复后使用`
      }
    }
  }
  
  return null
})

const runCheck = async () => {
  checkComplete.value = false
  checkSuccess.value = false
  currentStep.value = 0
  
  try {
    // 第1步：环境检测
    currentStep.value = 0
    await checkEnvironment()
    
    // 第2步：准备浏览器
    currentStep.value = 1
    await prepareChromium()
    
    // 第3步：启动服务
    currentStep.value = 2
    await startServices()
    
    // 检测完成
    currentStep.value = 3
    checkComplete.value = true
    checkSuccess.value = tasks.value.every(t => t.status === 'success' || t.status === 'warning')
    
    if (checkSuccess.value) {
      ElNotification({
        title: '✅ 环境准备就绪',
        message: '所有检测通过，可以开始使用',
        type: 'success'
      })
    }
    
  } catch (error) {
    checkComplete.value = true
    checkSuccess.value = false
    ElMessage.error('环境检测失败：' + (error.message || '未知错误'))
  }
}

const checkEnvironment = async () => {
  // 调用后端API检测环境
  const taskIds = ['python', 'network', 'ports', 'disk_space']
  
  for (const id of taskIds) {
    updateTask(id, { status: 'loading', message: '检测中...' })
  }
  
  try {
    const response = await api.get('/api/startup/check-all')
    const checks = response.data.checks
    
    // 更新各项检测结果
    for (const [id, result] of Object.entries(checks)) {
      const status = result.ok ? 'success' : (result.status === 'error' ? 'error' : 'warning')
      const message = result.message
      const actions = result.auto_fixable ? [
        { label: '自动修复', type: 'primary', action: 'auto_fix' }
      ] : undefined
      
      updateTask(id, { status, message, actions })
    }
    
    // 如果有可自动修复的问题，尝试自动修复
    if (response.data.auto_fixable) {
      await autoFix(response.data)
    }
    
  } catch (error) {
    for (const id of taskIds) {
      updateTask(id, {
        status: 'error',
        message: '检测失败：' + (error.response?.data?.message || '服务器连接失败')
      })
    }
    throw error
  }
}

const prepareChromium = async () => {
  const task = tasks.value.find(t => t.id === 'chromium')
  if (!task) return
  
  updateTask('chromium', { status: 'loading', message: '检测Chromium...' })
  
  try {
    const response = await api.get('/api/startup/check-chromium')
    
    if (response.data.installed) {
      updateTask('chromium', {
        status: 'success',
        message: '✅ Chromium已安装'
      })
    } else {
      // 需要下载
      updateTask('chromium', {
        status: 'loading',
        message: '正在下载Chromium（约200MB）...',
        progress: 0
      })
      
      // 开始下载
      await downloadChromium()
    }
    
  } catch (error) {
    updateTask('chromium', {
      status: 'error',
      message: '❌ Chromium检测失败：' + (error.response?.data?.message || error.message)
    })
  }
}

const downloadChromium = async () => {
  try {
    // 调用下载API
    const response = await api.post('/api/startup/download-chromium')
    
    // 轮询下载进度
    const downloadId = response.data.download_id
    const checkProgress = setInterval(async () => {
      try {
        const progressResponse = await api.get(`/api/startup/download-progress/${downloadId}`)
        const progress = progressResponse.data.progress
        
        updateTask('chromium', {
          message: `正在下载Chromium... ${progress}%`,
          progress
        })
        
        if (progress >= 100) {
          clearInterval(checkProgress)
          updateTask('chromium', {
            status: 'success',
            message: '✅ Chromium下载完成',
            progress: 100
          })
        }
      } catch (error) {
        clearInterval(checkProgress)
        updateTask('chromium', {
          status: 'error',
          message: '❌ 下载失败：' + (error.response?.data?.message || error.message)
        })
      }
    }, 1000)
    
  } catch (error) {
    updateTask('chromium', {
      status: 'error',
      message: '❌ 下载启动失败：' + (error.response?.data?.message || error.message)
    })
    throw error
  }
}

const startServices = async () => {
  // 启动Redis等服务
  updateTask('redis', { status: 'loading', message: '正在启动Redis...' })
  
  try {
    await api.post('/api/startup/start-redis')
    
    updateTask('redis', {
      status: 'success',
      message: '✅ Redis启动成功'
    })
  } catch (error) {
    updateTask('redis', {
      status: 'error',
      message: '❌ Redis启动失败：' + (error.response?.data?.message || error.message)
    })
  }
}

const autoFix = async (checkResults) => {
  ElMessage.info('正在自动修复检测到的问题...')
  
  try {
    const response = await api.post('/api/startup/auto-fix', checkResults)
    const fixed = response.data.fixed
    
    if (fixed.length > 0) {
      ElNotification({
        title: '✅ 自动修复完成',
        message: `已修复: ${fixed.join(', ')}`,
        type: 'success'
      })
      
      // 重新检测
      await runCheck()
    }
  } catch (error) {
    ElMessage.error('自动修复失败：' + (error.response?.data?.message || error.message))
  }
}

const handleAction = async (taskId, action) => {
  if (action === 'auto_fix') {
    // 触发自动修复
    await autoFix({ checks: { [taskId]: tasks.value.find(t => t.id === taskId) } })
  }
}

const retryCheck = () => {
  initTasks()
  runCheck()
}

const proceedToWizard = () => {
  router.push('/wizard')
}

const skipToMain = () => {
  router.push('/')
}

onMounted(() => {
  initTasks()
  // 延迟一下开始检测，让用户看到界面
  setTimeout(() => {
    runCheck()
  }, 500)
})
</script>

<style scoped lang="scss">
.startup-check-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.check-card {
  max-width: 800px;
  width: 100%;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.header {
  text-align: center;
  margin-bottom: 30px;
  
  .logo {
    width: 80px;
    height: 80px;
    margin-bottom: 15px;
  }
  
  h1 {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
    margin: 0 0 5px 0;
  }
  
  .version {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.check-progress {
  margin-bottom: 30px;
}

.check-details {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.task-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  border: 1px solid #EBEEF5;
  transition: all 0.3s;
  
  &.loading {
    background-color: #ECF5FF;
    border-color: #C6E2FF;
  }
  
  &.success {
    background-color: #F0F9FF;
    border-color: #C9E9D7;
  }
  
  &.error {
    background-color: #FEF0F0;
    border-color: #FDE2E2;
  }
  
  &.warning {
    background-color: #FDF6EC;
    border-color: #F5DAB1;
  }
}

.task-icon {
  margin-right: 12px;
  flex-shrink: 0;
}

.task-content {
  flex: 1;
  
  .task-name {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 5px;
  }
  
  .task-message {
    font-size: 14px;
    color: #606266;
    margin-bottom: 10px;
  }
  
  .task-actions {
    margin-top: 10px;
  }
}

.overall-status {
  margin-bottom: 20px;
}

.footer-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
