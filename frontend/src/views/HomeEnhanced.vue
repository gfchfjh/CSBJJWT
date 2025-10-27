<template>
  <div class="home-enhanced">
    <!-- 顶部状态栏 -->
    <div class="top-bar">
      <div class="status-info">
        <el-tag :type="serviceStatusType" size="large" effect="dark">
          <el-icon><component :is="ServiceStatusIcon" /></el-icon>
          {{ serviceStatusText }}
        </el-tag>
        
        <el-divider direction="vertical" />
        
        <div class="runtime-info">
          <span class="label">运行时长:</span>
          <span class="value">{{ runtime }}</span>
        </div>
      </div>
      
      <div class="quick-actions">
        <el-button-group>
          <el-button
            :type="isRunning ? 'danger' : 'success'"
            :icon="isRunning ? VideoPause : VideoPlay"
            @click="toggleService"
          >
            {{ isRunning ? '停止服务' : '启动服务' }}
          </el-button>
          <el-button :icon="Refresh" @click="restartService">重启服务</el-button>
          <el-button :icon="Promotion" @click="testForward">测试转发</el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 今日统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="今日转发消息" :value="stats.today_messages">
            <template #prefix>
              <el-icon :size="20" color="#409EFF"><ChatLineSquare /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span :class="stats.today_trend >= 0 ? 'trend-up' : 'trend-down'">
              {{ stats.today_trend >= 0 ? '↑' : '↓' }} {{ Math.abs(stats.today_trend) }}%
            </span>
            <span class="label">较昨日</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="成功率" :value="stats.success_rate" suffix="%">
            <template #prefix>
              <el-icon :size="20" color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span class="label">成功: {{ stats.success }} / 失败: {{ stats.failed }}</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="平均延迟" :value="stats.avg_latency" suffix="ms">
            <template #prefix>
              <el-icon :size="20" color="#E6A23C"><Timer /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span class="label">
              <el-tag :type="getLatencyType(stats.avg_latency)" size="small">
                {{ getLatencyLabel(stats.avg_latency) }}
              </el-tag>
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="失败消息" :value="stats.failed">
            <template #prefix>
              <el-icon :size="20" color="#F56C6C"><CircleClose /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <el-button type="text" size="small" @click="viewFailedMessages">
              查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时监控图表 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><TrendCharts /></el-icon>
            实时监控
          </span>
          <div class="chart-controls">
            <el-radio-group v-model="chartTimeRange" size="small">
              <el-radio-button label="1h">最近1小时</el-radio-button>
              <el-radio-button label="6h">最近6小时</el-radio-button>
              <el-radio-button label="24h">最近24小时</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <!-- 限流监控 -->
    <el-card class="rate-limit-card" shadow="hover">
      <template #header>
        <span>
          <el-icon><Timer /></el-icon>
          限流监控
        </span>
      </template>
      
      <RateLimitMonitor />
    </el-card>

    <!-- 快捷操作区 -->
    <el-row :gutter="20" class="quick-ops">
      <el-col :span="8">
        <el-card shadow="hover" class="op-card" @click="navigateTo('/accounts')">
          <div class="op-content">
            <el-icon :size="40" color="#409EFF"><User /></el-icon>
            <div class="op-info">
              <h4>账号管理</h4>
              <p>当前 {{ accountsCount }} 个账号</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="op-card" @click="navigateTo('/bots')">
          <div class="op-content">
            <el-icon :size="40" color="#67C23A"><ChatDotRound /></el-icon>
            <div class="op-info">
              <h4>Bot管理</h4>
              <p>当前 {{ botsCount }} 个Bot</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="op-card" @click="navigateTo('/mapping')">
          <div class="op-content">
            <el-icon :size="40" color="#E6A23C"><Connection /></el-icon>
            <div class="op-info">
              <h4>频道映射</h4>
              <p>当前 {{ mappingsCount }} 个映射</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatLineSquare, CircleCheck, CircleClose, Timer, TrendCharts,
  User, ChatDotRound, Connection, VideoPlay, VideoPause, Refresh, Promotion,
  SuccessFilled, Loading, WarningFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'
import RateLimitMonitor from '@/components/RateLimitMonitor.vue'

const router = useRouter()

// 服务状态
const isRunning = ref(false)
const runtime = ref('0小时0分钟')

const serviceStatusType = computed(() => {
  return isRunning.value ? 'success' : 'danger'
})

const ServiceStatusIcon = computed(() => {
  return isRunning.value ? SuccessFilled : WarningFilled
})

const serviceStatusText = computed(() => {
  return isRunning.value ? '运行中' : '已停止'
})

// 统计数据
const stats = ref({
  today_messages: 0,
  today_trend: 0,
  success_rate: 0,
  success: 0,
  failed: 0,
  avg_latency: 0
})

// 图表
const chartRef = ref(null)
const chartTimeRange = ref('1h')
let chartInstance = null

// 快捷操作数据
const accountsCount = ref(0)
const botsCount = ref(0)
const mappingsCount = ref(0)

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['转发消息', '成功', '失败']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '转发消息',
        type: 'line',
        data: [],
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '成功',
        type: 'line',
        data: [],
        smooth: true,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: '失败',
        type: 'line',
        data: [],
        smooth: true,
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }
  
  chartInstance.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 更新图表数据
const updateChartData = async () => {
  try {
    const response = await api.get('/api/statistics/realtime', {
      params: { range: chartTimeRange.value }
    })
    
    const data = response.data
    
    chartInstance?.setOption({
      xAxis: {
        data: data.timestamps
      },
      series: [
        { data: data.total },
        { data: data.success },
        { data: data.failed }
      ]
    })
  } catch (error) {
    console.error('更新图表数据失败:', error)
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await api.get('/api/statistics/today')
    stats.value = response.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取服务状态
const fetchServiceStatus = async () => {
  try {
    const response = await api.get('/api/system/status')
    isRunning.value = response.data.running
    runtime.value = response.data.runtime
  } catch (error) {
    console.error('获取服务状态失败:', error)
  }
}

// 获取快捷操作数据
const fetchQuickOpsData = async () => {
  try {
    const [accounts, bots, mappings] = await Promise.all([
      api.get('/api/accounts/count'),
      api.get('/api/bots/count'),
      api.get('/api/mappings/count')
    ])
    
    accountsCount.value = accounts.data.count
    botsCount.value = bots.data.count
    mappingsCount.value = mappings.data.count
  } catch (error) {
    console.error('获取快捷操作数据失败:', error)
  }
}

// 切换服务
const toggleService = async () => {
  const action = isRunning.value ? 'stop' : 'start'
  const actionText = isRunning.value ? '停止' : '启动'
  
  try {
    await api.post(`/api/system/${action}`)
    ElMessage.success(`✅ 服务已${actionText}`)
    await fetchServiceStatus()
  } catch (error) {
    ElMessage.error(`❌ ${actionText}失败: ` + (error.response?.data?.message || error.message))
  }
}

// 重启服务
const restartService = async () => {
  ElMessageBox.confirm(
    '重启服务将暂停消息转发，确定继续吗？',
    '确认重启',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.post('/api/system/restart')
      ElMessage.success('✅ 服务重启中...')
      setTimeout(() => {
        fetchServiceStatus()
      }, 3000)
    } catch (error) {
      ElMessage.error('❌ 重启失败: ' + (error.response?.data?.message || error.message))
    }
  }).catch(() => {})
}

// 测试转发
const testForward = () => {
  ElMessageBox.prompt('请输入测试消息内容', '测试转发', {
    confirmButtonText: '发送',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '消息内容不能为空'
  }).then(async ({ value }) => {
    try {
      await api.post('/api/system/test-forward', { message: value })
      ElMessage.success('✅ 测试消息已发送')
    } catch (error) {
      ElMessage.error('❌ 发送失败: ' + (error.response?.data?.message || error.message))
    }
  }).catch(() => {})
}

// 查看失败消息
const viewFailedMessages = () => {
  router.push('/logs?status=failed')
}

// 导航
const navigateTo = (path) => {
  router.push(path)
}

// 辅助函数
const getLatencyType = (latency) => {
  if (latency < 1000) return 'success'
  if (latency < 3000) return 'warning'
  return 'danger'
}

const getLatencyLabel = (latency) => {
  if (latency < 1000) return '优秀'
  if (latency < 3000) return '良好'
  return '较慢'
}

let intervalId = null

onMounted(() => {
  initChart()
  fetchStats()
  fetchServiceStatus()
  fetchQuickOpsData()
  updateChartData()
  
  // 定时刷新
  intervalId = setInterval(() => {
    fetchStats()
    fetchServiceStatus()
    updateChartData()
  }, 5000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped lang="scss">
.home-enhanced {
  padding: 20px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  
  .status-info {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .runtime-info {
      .label {
        color: #909399;
        margin-right: 5px;
      }
      
      .value {
        font-weight: bold;
        color: #303133;
      }
    }
  }
}

.stats-cards {
  margin-bottom: 20px;
  
  .stat-card {
    .stat-footer {
      margin-top: 10px;
      font-size: 12px;
      color: #909399;
      
      .trend-up {
        color: #67C23A;
        margin-right: 5px;
      }
      
      .trend-down {
        color: #F56C6C;
        margin-right: 5px;
      }
    }
  }
}

.chart-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    > span {
      display: flex;
      align-items: center;
      gap: 5px;
      font-weight: bold;
    }
  }
  
  .chart-container {
    width: 100%;
    height: 300px;
  }
}

.rate-limit-card {
  margin-bottom: 20px;
}

.quick-ops {
  .op-card {
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    
    .op-content {
      display: flex;
      align-items: center;
      gap: 15px;
      
      .op-info {
        h4 {
          margin: 0 0 5px 0;
          font-size: 16px;
          color: #303133;
        }
        
        p {
          margin: 0;
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}
</style>
