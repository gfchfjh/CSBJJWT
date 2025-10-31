<template>
  <div class="home-perfect">
    <!-- 头部状态栏 -->
    <div class="header-bar">
      <div class="header-left">
        <h1>KOOK消息转发系统</h1>
      </div>
      <div class="header-right">
        <el-badge :value="systemStatus.offline_count" :hidden="systemStatus.offline_count === 0">
          <el-tag
            :type="statusType"
            size="large"
            style="cursor: pointer"
            @click="showStatusDetail"
          >
            <el-icon><component :is="statusIcon" /></el-icon>
            {{ statusText }}
          </el-tag>
        </el-badge>
        <el-button text @click="goToSettings">
          <el-icon><Setting /></el-icon> 设置
        </el-button>
        <el-button text @click="goToHelp">
          <el-icon><QuestionFilled /></el-icon> 帮助
        </el-button>
      </div>
    </div>

    <!-- 今日统计 -->
    <el-card class="stats-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>📊 今日统计</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">转发消息</div>
            <div class="stat-value">{{ formatNumber(todayStats.total_messages) }}</div>
            <div class="stat-unit">条</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">成功率</div>
            <div class="stat-value success">{{ todayStats.success_rate }}</div>
            <div class="stat-unit">%</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均延迟</div>
            <div class="stat-value">{{ todayStats.avg_latency }}</div>
            <div class="stat-unit">秒</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">失败消息</div>
            <div class="stat-value danger">{{ todayStats.failed_messages }}</div>
            <div class="stat-unit">
              条
              <el-button
                v-if="todayStats.failed_messages > 0"
                link
                type="danger"
                size="small"
                @click="viewFailedMessages"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 实时监控 -->
    <el-card class="monitor-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataLine /></el-icon>
          <span>📈 实时监控</span>
          <el-button-group class="time-range-buttons">
            <el-button
              :type="timeRange === '1h' ? 'primary' : ''"
              size="small"
              @click="setTimeRange('1h')"
            >
              1小时
            </el-button>
            <el-button
              :type="timeRange === '6h' ? 'primary' : ''"
              size="small"
              @click="setTimeRange('6h')"
            >
              6小时
            </el-button>
            <el-button
              :type="timeRange === '24h' ? 'primary' : ''"
              size="small"
              @click="setTimeRange('24h')"
            >
              24小时
            </el-button>
          </el-button-group>
        </div>
      </template>

      <div class="chart-container">
        <v-chart :option="chartOption" autoresize style="height: 300px" />
      </div>
    </el-card>

    <!-- 快捷操作 -->
    <el-card class="actions-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Operation /></el-icon>
          <span>⚡ 快捷操作</span>
        </div>
      </template>

      <div class="action-buttons">
        <el-button
          v-if="!serviceRunning"
          type="success"
          size="large"
          :loading="isStarting"
          @click="startService"
        >
          <el-icon><VideoPlay /></el-icon>
          启动服务
        </el-button>
        <el-button
          v-else
          type="danger"
          size="large"
          :loading="isStopping"
          @click="stopService"
        >
          <el-icon><VideoPause /></el-icon>
          停止服务
        </el-button>

        <el-button
          size="large"
          :disabled="!serviceRunning"
          :loading="isRestarting"
          @click="restartService"
        >
          <el-icon><Refresh /></el-icon>
          重启服务
        </el-button>

        <el-button
          size="large"
          type="primary"
          @click="testForward"
        >
          <el-icon><Promotion /></el-icon>
          测试转发
        </el-button>

        <el-button
          size="large"
          type="warning"
          :disabled="queueSize === 0"
          @click="clearQueue"
        >
          <el-icon><Delete /></el-icon>
          清空队列
          <el-badge
            v-if="queueSize > 0"
            :value="queueSize"
            :max="99"
            class="badge-margin"
          />
        </el-button>
      </div>
    </el-card>

    <!-- 最近日志 -->
    <el-card class="logs-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>📋 最近日志</span>
          <el-button link type="primary" @click="viewAllLogs">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="recentLogs" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.status === 'success'" color="#67C23A" :size="20">
              <CircleCheck />
            </el-icon>
            <el-icon v-else-if="row.status === 'failed'" color="#F56C6C" :size="20">
              <CircleClose />
            </el-icon>
            <el-icon v-else color="#E6A23C" :size="20">
              <Loading />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column label="路由" min-width="300">
          <template #default="{ row }">
            <el-text truncated>
              {{ row.source_channel }} → {{ row.target_platform }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column label="内容" min-width="200">
          <template #default="{ row }">
            <el-text truncated>{{ row.content }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="延迟" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.latency" size="small" :type="getLatencyType(row.latency)">
              {{ row.latency }}ms
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, QuestionFilled, TrendCharts, DataLine, Operation,
  VideoPlay, VideoPause, Refresh, Promotion, Delete, Document,
  ArrowRight, CircleCheck, CircleClose, Loading,
  SuccessFilled, WarningFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import axios from 'axios'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

// 系统状态
const systemStatus = ref({
  running: false,
  online_count: 0,
  offline_count: 0,
  total_count: 0
})

// 今日统计
const todayStats = ref({
  total_messages: 1234,
  success_rate: 98.5,
  avg_latency: 1.2,
  failed_messages: 18
})

// 服务状态
const serviceRunning = ref(false)
const isStarting = ref(false)
const isStopping = ref(false)
const isRestarting = ref(false)
const queueSize = ref(0)

// 时间范围
const timeRange = ref('1h')

// 图表数据
const chartData = ref({
  times: [],
  values: []
})

// 最近日志
const recentLogs = ref([])

// 定时器
let statsTimer = null
let logsTimer = null

// 计算属性
const statusType = computed(() => {
  if (systemStatus.value.offline_count > 0) return 'danger'
  if (!systemStatus.value.running) return 'info'
  return 'success'
})

const statusIcon = computed(() => {
  if (systemStatus.value.offline_count > 0) return CircleCloseFilled
  if (!systemStatus.value.running) return WarningFilled
  return SuccessFilled
})

const statusText = computed(() => {
  if (systemStatus.value.offline_count > 0) {
    return `${systemStatus.value.offline_count}个账号离线`
  }
  if (!systemStatus.value.running) {
    return '未运行'
  }
  return '运行中'
})

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'line'
    }
  },
  grid: {
    left: '50px',
    right: '50px',
    top: '30px',
    bottom: '30px'
  },
  xAxis: {
    type: 'category',
    data: chartData.value.times,
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    name: '消息数'
  },
  series: [
    {
      name: '每分钟转发量',
      type: 'line',
      data: chartData.value.values,
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#667eea',
        width: 2
      },
      itemStyle: {
        color: '#667eea'
      }
    }
  ]
}))

// 方法
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toLocaleString()
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getLatencyType = (latency) => {
  if (latency < 1000) return 'success'
  if (latency < 3000) return 'warning'
  return 'danger'
}

const showStatusDetail = () => {
  router.push('/settings?tab=status')
}

const goToSettings = () => {
  router.push('/settings')
}

const goToHelp = () => {
  router.push('/help')
}

const viewFailedMessages = () => {
  router.push('/logs?filter=failed')
}

const viewAllLogs = () => {
  router.push('/logs')
}

const setTimeRange = (range) => {
  timeRange.value = range
  loadChartData()
}

// 服务控制
const startService = async () => {
  isStarting.value = true
  try {
    const response = await axios.post('/api/service/start')
    if (response.data.success) {
      serviceRunning.value = true
      ElMessage.success('服务启动成功')
      loadStats()
    } else {
      ElMessage.error(response.data.message || '服务启动失败')
    }
  } catch (error) {
    console.error('启动失败:', error)
    ElMessage.error('服务启动失败')
  } finally {
    isStarting.value = false
  }
}

const stopService = async () => {
  try {
    await ElMessageBox.confirm(
      '停止服务后将不再转发新消息，确定要停止吗？',
      '确认停止',
      {
        type: 'warning',
        confirmButtonText: '确定停止',
        cancelButtonText: '取消'
      }
    )

    isStopping.value = true
    try {
      const response = await axios.post('/api/service/stop')
      if (response.data.success) {
        serviceRunning.value = false
        ElMessage.success('服务已停止')
        loadStats()
      } else {
        ElMessage.error(response.data.message || '服务停止失败')
      }
    } catch (error) {
      console.error('停止失败:', error)
      ElMessage.error('服务停止失败')
    } finally {
      isStopping.value = false
    }
  } catch {
    // 用户取消
  }
}

const restartService = async () => {
  isRestarting.value = true
  try {
    const response = await axios.post('/api/service/restart')
    if (response.data.success) {
      ElMessage.success('服务重启成功')
      loadStats()
    } else {
      ElMessage.error(response.data.message || '服务重启失败')
    }
  } catch (error) {
    console.error('重启失败:', error)
    ElMessage.error('服务重启失败')
  } finally {
    isRestarting.value = false
  }
}

const testForward = async () => {
  try {
    const { value: content } = await ElMessageBox.prompt(
      '请输入测试消息内容',
      '测试转发',
      {
        confirmButtonText: '发送测试',
        cancelButtonText: '取消',
        inputPlaceholder: '这是一条测试消息',
        inputValue: '这是一条测试消息'
      }
    )

    const response = await axios.post('/api/test/forward', {
      content: content
    })

    if (response.data.success) {
      ElMessage.success('测试消息已发送，请查看目标平台')
    } else {
      ElMessage.error(response.data.message || '测试失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('测试失败:', error)
      ElMessage.error('测试失败')
    }
  }
}

const clearQueue = async () => {
  try {
    await ElMessageBox.confirm(
      `队列中有 ${queueSize.value} 条消息，清空后将无法恢复，确定要清空吗？`,
      '确认清空',
      {
        type: 'warning',
        confirmButtonText: '确定清空',
        cancelButtonText: '取消'
      }
    )

    const response = await axios.post('/api/queue/clear')
    if (response.data.success) {
      queueSize.value = 0
      ElMessage.success('队列已清空')
    } else {
      ElMessage.error(response.data.message || '清空失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空失败:', error)
      ElMessage.error('清空失败')
    }
  }
}

// 数据加载
const loadStats = async () => {
  try {
    const response = await axios.get('/api/stats/today')
    if (response.data.success) {
      todayStats.value = response.data.stats
    }

    const statusResponse = await axios.get('/api/service/status')
    if (statusResponse.data.success) {
      serviceRunning.value = statusResponse.data.running
      queueSize.value = statusResponse.data.queue_size || 0
      systemStatus.value = {
        running: statusResponse.data.running,
        online_count: statusResponse.data.online_accounts || 0,
        offline_count: statusResponse.data.offline_accounts || 0,
        total_count: statusResponse.data.total_accounts || 0
      }
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadChartData = async () => {
  try {
    const response = await axios.get('/api/stats/realtime', {
      params: { range: timeRange.value }
    })

    if (response.data.success) {
      chartData.value = {
        times: response.data.times || [],
        values: response.data.values || []
      }
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await axios.get('/api/logs/recent', {
      params: { limit: 10 }
    })

    if (response.data.success) {
      recentLogs.value = response.data.logs || []
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadStats()
  loadChartData()
  loadRecentLogs()

  // 定时刷新
  statsTimer = setInterval(loadStats, 10000) // 10秒
  logsTimer = setInterval(loadRecentLogs, 5000) // 5秒
})

onUnmounted(() => {
  if (statsTimer) clearInterval(statsTimer)
  if (logsTimer) clearInterval(logsTimer)
})
</script>

<style scoped lang="scss">
.home-perfect {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 40px);
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 30px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .header-left {
    h1 {
      margin: 0;
      font-size: 24px;
      color: #303133;
      font-weight: 600;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;

  .time-range-buttons {
    margin-left: auto;
  }
}

.stats-card {
  margin-bottom: 20px;

  .stat-item {
    text-align: center;
    padding: 20px;
    border-right: 1px solid #EBEEF5;

    &:last-child {
      border-right: none;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .stat-value {
      font-size: 36px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 5px;

      &.success {
        color: #67C23A;
      }

      &.danger {
        color: #F56C6C;
      }
    }

    .stat-unit {
      font-size: 14px;
      color: #909399;
    }
  }
}

.monitor-card {
  margin-bottom: 20px;

  .chart-container {
    padding: 20px 0;
  }
}

.actions-card {
  margin-bottom: 20px;

  .action-buttons {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;

    .el-button {
      flex: 1;
      min-width: 150px;
    }

    .badge-margin {
      margin-left: 5px;
    }
  }
}

.logs-card {
  .card-header {
    .el-button {
      margin-left: auto;
    }
  }
}
</style>
