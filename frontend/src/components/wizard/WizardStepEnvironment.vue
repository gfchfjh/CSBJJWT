<template>
  <!-- ✅ P0-4优化: 环境检查组件 -->
  <div class="environment-step">
    <el-result 
      :icon="getResultIcon()"
      :title="getTitle()"
    >
      <template #sub-title>
        <div class="check-content">
          <!-- 检查项列表 -->
          <el-space direction="vertical" :size="15" style="width: 100%;">
            <!-- 1. Python环境 -->
            <div class="check-item">
              <div class="check-header">
                <el-icon :size="20" :color="getStatusColor('python')">
                  <component :is="getStatusIcon('python')" />
                </el-icon>
                <span class="check-label">Python 运行环境</span>
                <el-tag :type="getStatusTagType('python')">
                  {{ envStatus.python.message }}
                </el-tag>
              </div>
              <el-progress
                v-if="envStatus.python.status === 'checking'"
                :percentage="envStatus.python.progress"
                :status="envStatus.python.progress === 100 ? 'success' : ''"
              />
            </div>

            <!-- 2. Chromium浏览器 -->
            <div class="check-item">
              <div class="check-header">
                <el-icon :size="20" :color="getStatusColor('chromium')">
                  <component :is="getStatusIcon('chromium')" />
                </el-icon>
                <span class="check-label">Chromium 浏览器</span>
                <el-tag :type="getStatusTagType('chromium')">
                  {{ envStatus.chromium.message }}
                </el-tag>
              </div>
              <el-progress
                v-if="envStatus.chromium.status === 'checking' || 
                      envStatus.chromium.status === 'downloading'"
                :percentage="envStatus.chromium.progress"
                :status="envStatus.chromium.progress === 100 ? 'success' : ''"
              >
                <template #default="{ percentage }">
                  <span>{{ percentage }}%</span>
                  <span v-if="envStatus.chromium.downloadSpeed" 
                        style="margin-left: 10px; font-size: 12px; color: #909399;">
                    ({{ envStatus.chromium.downloadSpeed }})
                  </span>
                </template>
              </el-progress>
              <div v-if="envStatus.chromium.status === 'downloading'" class="check-detail">
                <el-text size="small" type="info">
                  正在下载: {{ envStatus.chromium.downloadedSize }} / {{ envStatus.chromium.totalSize }}
                  <br/>
                  预计剩余时间: {{ envStatus.chromium.estimatedTime }}
                </el-text>
              </div>
            </div>

            <!-- 3. Redis服务 -->
            <div class="check-item">
              <div class="check-header">
                <el-icon :size="20" :color="getStatusColor('redis')">
                  <component :is="getStatusIcon('redis')" />
                </el-icon>
                <span class="check-label">Redis 消息队列</span>
                <el-tag :type="getStatusTagType('redis')">
                  {{ envStatus.redis.message }}
                </el-tag>
              </div>
              <el-progress
                v-if="envStatus.redis.status === 'checking' || 
                      envStatus.redis.status === 'starting'"
                :percentage="envStatus.redis.progress"
                :status="envStatus.redis.progress === 100 ? 'success' : ''"
              />
            </div>

            <!-- 4. 网络连接 -->
            <div class="check-item">
              <div class="check-header">
                <el-icon :size="20" :color="getStatusColor('network')">
                  <component :is="getStatusIcon('network')" />
                </el-icon>
                <span class="check-label">网络连接</span>
                <el-tag :type="getStatusTagType('network')">
                  {{ envStatus.network.message }}
                </el-tag>
              </div>
            </div>
          </el-space>

          <!-- 错误提示和解决方案 -->
          <el-collapse v-if="hasErrors" style="margin-top: 20px;">
            <el-collapse-item 
              v-for="(error, key) in errors" 
              :key="key"
              :name="key"
            >
              <template #title>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-icon color="#F56C6C"><WarningFilled /></el-icon>
                  <strong>{{ error.title }}</strong>
                </div>
              </template>
              
              <el-alert :type="error.type" :closable="false">
                <template #title>
                  <strong>问题描述:</strong> {{ error.description }}
                </template>
              </el-alert>

              <div class="solution" style="margin-top: 10px;">
                <strong>解决方案:</strong>
                <ol style="margin: 10px 0; padding-left: 20px;">
                  <li v-for="(step, idx) in error.solutions" :key="idx">
                    {{ step }}
                  </li>
                </ol>
              </div>

              <el-button 
                v-if="error.fixable"
                type="primary" 
                size="small"
                @click="autoFix(key)"
              >
                <el-icon><Tools /></el-icon>
                自动修复
              </el-button>
            </el-collapse-item>
          </el-collapse>
        </div>
      </template>
      <template #extra>
        <el-space>
          <el-button 
            v-if="checkStatus === 'error'"
            @click="retryCheck"
          >
            <el-icon><RefreshRight /></el-icon>
            重新检查
          </el-button>
          <el-button 
            v-if="checkStatus === 'success'"
            type="primary" 
            @click="handleNext"
          >
            继续配置
          </el-button>
          <el-button 
            v-if="checkStatus === 'error' && canSkip"
            @click="handleSkip"
          >
            忽略错误并继续
          </el-button>
        </el-space>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  WarningFilled, Tools, RefreshRight, 
  CircleCheck, CircleClose, Loading 
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

const checkStatus = ref('checking') // checking / success / error
const envStatus = reactive({
  python: {
    status: 'pending',
    message: '等待检查',
    progress: 0
  },
  chromium: {
    status: 'pending',
    message: '等待检查',
    progress: 0,
    downloadSpeed: '',
    downloadedSize: '',
    totalSize: '',
    estimatedTime: ''
  },
  redis: {
    status: 'pending',
    message: '等待检查',
    progress: 0
  },
  network: {
    status: 'pending',
    message: '等待检查',
    progress: 0
  }
})

const errors = ref({})
const hasErrors = computed(() => Object.keys(errors.value).length > 0)
const canSkip = ref(false)

onMounted(() => {
  startEnvironmentCheck()
})

// 环境检查
const startEnvironmentCheck = async () => {
  checkStatus.value = 'checking'
  
  try {
    // 1. 检查Python
    await checkPython()
    
    // 2. 检查Chromium
    await checkChromium()
    
    // 3. 检查Redis
    await checkRedis()
    
    // 4. 检查网络
    await checkNetwork()
    
    // 全部通过
    if (!hasErrors.value) {
      checkStatus.value = 'success'
    } else {
      checkStatus.value = 'error'
      // 如果只是警告级别的错误，允许跳过
      canSkip.value = !Object.values(errors.value).some(e => e.critical)
    }
  } catch (error) {
    checkStatus.value = 'error'
    ElMessage.error('环境检查失败: ' + error.message)
  }
}

// 检查Python
const checkPython = async () => {
  envStatus.python.status = 'checking'
  envStatus.python.message = '检查中...'
  
  try {
    const response = await api.get('/api/system/check-python')
    
    if (response.installed) {
      envStatus.python.status = 'success'
      envStatus.python.message = `已安装 (${response.version})`
      envStatus.python.progress = 100
    } else {
      envStatus.python.status = 'error'
      envStatus.python.message = '未安装'
      errors.value.python = {
        title: 'Python未安装',
        description: '系统未检测到Python运行环境',
        type: 'error',
        critical: true,
        fixable: false,
        solutions: [
          '请访问 https://www.python.org/downloads/ 下载安装Python 3.11+',
          '安装完成后重新运行本程序',
          '如已安装，请检查环境变量配置'
        ]
      }
    }
  } catch (error) {
    envStatus.python.status = 'error'
    envStatus.python.message = '检查失败'
  }
}

// 检查Chromium
const checkChromium = async () => {
  envStatus.chromium.status = 'checking'
  envStatus.chromium.message = '检查中...'
  
  try {
    const response = await api.get('/api/system/check-chromium')
    
    if (response.installed) {
      envStatus.chromium.status = 'success'
      envStatus.chromium.message = '已安装'
      envStatus.chromium.progress = 100
    } else {
      // 自动下载Chromium
      envStatus.chromium.status = 'downloading'
      envStatus.chromium.message = '正在下载...'
      
      await downloadChromium()
    }
  } catch (error) {
    envStatus.chromium.status = 'error'
    envStatus.chromium.message = '下载失败'
    errors.value.chromium = {
      title: 'Chromium下载失败',
      description: error.message,
      type: 'error',
      critical: false,
      fixable: true,
      solutions: [
        '检查网络连接是否正常',
        '关闭代理或VPN后重试',
        '点击"自动修复"重新下载',
        '或手动下载后放置到指定目录'
      ]
    }
  }
}

// 下载Chromium
const downloadChromium = async () => {
  try {
    // 开始下载
    const downloadResponse = await api.post('/api/system/download-chromium')
    const downloadId = downloadResponse.download_id
    
    // 轮询下载进度
    const pollInterval = setInterval(async () => {
      try {
        const progressResponse = await api.get(`/api/system/download-progress/${downloadId}`)
        const progress = progressResponse
        
        envStatus.chromium.progress = progress.percentage
        envStatus.chromium.downloadSpeed = progress.speed
        envStatus.chromium.downloadedSize = progress.downloaded_size
        envStatus.chromium.totalSize = progress.total_size
        envStatus.chromium.estimatedTime = progress.estimated_time
        
        if (progress.percentage === 100) {
          clearInterval(pollInterval)
          envStatus.chromium.status = 'success'
          envStatus.chromium.message = '下载完成'
        }
      } catch (error) {
        clearInterval(pollInterval)
        throw error
      }
    }, 1000)
  } catch (error) {
    throw error
  }
}

// 检查Redis
const checkRedis = async () => {
  envStatus.redis.status = 'checking'
  envStatus.redis.message = '检查中...'
  
  try {
    const response = await api.get('/api/system/check-redis')
    
    if (response.running) {
      envStatus.redis.status = 'success'
      envStatus.redis.message = '运行中'
      envStatus.redis.progress = 100
    } else {
      // 自动启动Redis
      envStatus.redis.status = 'starting'
      envStatus.redis.message = '正在启动...'
      
      await api.post('/api/system/start-redis')
      
      // 等待启动完成
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 再次检查
      const checkResponse = await api.get('/api/system/check-redis')
      if (checkResponse.running) {
        envStatus.redis.status = 'success'
        envStatus.redis.message = '已启动'
        envStatus.redis.progress = 100
      } else {
        throw new Error('Redis启动失败')
      }
    }
  } catch (error) {
    envStatus.redis.status = 'error'
    envStatus.redis.message = '启动失败'
    errors.value.redis = {
      title: 'Redis启动失败',
      description: error.message,
      type: 'error',
      critical: false,
      fixable: true,
      solutions: [
        '检查端口6379是否被占用',
        '检查防火墙设置',
        '点击"自动修复"重新启动',
        '或手动启动Redis服务'
      ]
    }
  }
}

// 检查网络
const checkNetwork = async () => {
  envStatus.network.status = 'checking'
  envStatus.network.message = '检查中...'
  
  try {
    const response = await api.get('/api/system/check-network')
    
    if (response.connected) {
      envStatus.network.status = 'success'
      envStatus.network.message = `连接正常 (延迟: ${response.latency}ms)`
      envStatus.network.progress = 100
    } else {
      envStatus.network.status = 'error'
      envStatus.network.message = '无法连接'
      errors.value.network = {
        title: '网络连接异常',
        description: '无法连接到KOOK服务器',
        type: 'warning',
        critical: false,
        fixable: false,
        solutions: [
          '检查网络连接',
          '检查防火墙或安全软件设置',
          '尝试使用代理或VPN',
          '联系网络管理员'
        ]
      }
    }
  } catch (error) {
    envStatus.network.status = 'error'
    envStatus.network.message = '检查失败'
  }
}

// 获取结果图标
const getResultIcon = () => {
  if (checkStatus.value === 'checking') return 'loading'
  if (checkStatus.value === 'success') return 'success'
  return 'error'
}

// 获取标题
const getTitle = () => {
  if (checkStatus.value === 'checking') {
    return '正在检查系统环境...'
  } else if (checkStatus.value === 'success') {
    return '✅ 环境检查通过！'
  } else {
    return '⚠️ 发现环境问题'
  }
}

// 获取状态图标
const getStatusIcon = (key) => {
  const status = envStatus[key].status
  if (status === 'success') return 'CircleCheck'
  if (status === 'error') return 'CircleClose'
  if (status === 'checking' || status === 'downloading' || status === 'starting') {
    return 'Loading'
  }
  return 'Remove'
}

// 获取状态颜色
const getStatusColor = (key) => {
  const status = envStatus[key].status
  if (status === 'success') return '#67C23A'
  if (status === 'error') return '#F56C6C'
  if (status === 'checking' || status === 'downloading' || status === 'starting') {
    return '#409EFF'
  }
  return '#909399'
}

// 获取Tag类型
const getStatusTagType = (key) => {
  const status = envStatus[key].status
  if (status === 'success') return 'success'
  if (status === 'error') return 'danger'
  if (status === 'checking' || status === 'downloading' || status === 'starting') {
    return 'primary'
  }
  return 'info'
}

// 重试检查
const retryCheck = () => {
  errors.value = {}
  startEnvironmentCheck()
}

// 自动修复
const autoFix = async (key) => {
  if (key === 'chromium') {
    await downloadChromium()
  } else if (key === 'redis') {
    await checkRedis()
  }
}

// 下一步
const handleNext = () => {
  emit('next')
}

// 跳过
const handleSkip = () => {
  ElMessage.warning('已忽略环境检查错误，部分功能可能无法正常使用')
  emit('next')
}
</script>

<style scoped>
.check-item {
  padding: 15px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  background-color: #FAFAFA;
}

.check-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.check-label {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
}

.check-detail {
  margin-top: 10px;
  padding: 10px;
  background-color: #F5F7FA;
  border-radius: 4px;
}
</style>
