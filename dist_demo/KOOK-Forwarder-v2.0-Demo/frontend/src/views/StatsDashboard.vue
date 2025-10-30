<template>
  <div class="stats-dashboard-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>
        <el-icon><TrendCharts /></el-icon>
        统计面板
      </h1>
      
      <div class="header-actions">
        <el-radio-group v-model="timeRange" @change="loadData">
          <el-radio-button label="today">今日</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
          <el-radio-button label="all">全部</el-radio-button>
        </el-radio-group>
        
        <el-button :icon="Refresh" @click="loadData" :loading="loading">
          刷新
        </el-button>
        
        <el-button :icon="Download" @click="exportReport">
          导出报表
        </el-button>
      </div>
    </div>
    
    <!-- 核心指标卡片 -->
    <el-row :gutter="16" class="metrics-row">
      <el-col :span="6" v-for="metric in coreMetrics" :key="metric.key">
        <el-card class="metric-card" shadow="hover" :body-style="{ padding: '20px' }">
          <div class="metric-content">
            <div class="metric-icon" :style="{ background: metric.color }">
              <el-icon :size="32" color="#fff">
                <component :is="metric.icon" />
              </el-icon>
            </div>
            
            <div class="metric-data">
              <div class="metric-value">
                {{ formatNumber(metric.value) }}
                <el-tag v-if="metric.change !== undefined" :type="getChangeType(metric.change)" size="small">
                  <el-icon>
                    <component :is="metric.change >= 0 ? 'Top' : 'Bottom'" />
                  </el-icon>
                  {{ Math.abs(metric.change) }}%
                </el-tag>
              </div>
              <div class="metric-label">{{ metric.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="16" class="charts-row">
      <!-- 转发趋势图 -->
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📈 转发趋势</span>
              <el-radio-group v-model="trendType" size="small" @change="updateTrendChart">
                <el-radio-button label="hourly">按小时</el-radio-button>
                <el-radio-button label="daily">按天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 成功率饼图 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>📊 成功率分布</span>
          </template>
          <div ref="successChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="16" class="charts-row">
      <!-- 平台分布 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>🎯 平台分布</span>
          </template>
          <div ref="platformChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 延迟分布 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>⏱️ 延迟分布</span>
          </template>
          <div ref="latencyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 消息类型分布 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>📝 消息类型</span>
          </template>
          <div ref="messageTypeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Top频道排行 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🏆 Top 10 活跃频道</span>
          </template>
          <div ref="topChannelsChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 实时监控 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>⚡ 实时监控</span>
              <el-tag :type="realtimeStatus.type" size="small">
                {{ realtimeStatus.text }}
              </el-tag>
            </div>
          </template>
          <div class="realtime-stats">
            <el-row :gutter="16">
              <el-col :span="12" v-for="stat in realtimeStats" :key="stat.key">
                <div class="realtime-item">
                  <div class="realtime-icon" :style="{ background: stat.color }">
                    <el-icon :size="24">
                      <component :is="stat.icon" />
                    </el-icon>
                  </div>
                  <div class="realtime-data">
                    <div class="realtime-value">{{ stat.value }}</div>
                    <div class="realtime-label">{{ stat.label }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <el-divider />
            
            <!-- 最近错误 -->
            <div class="recent-errors">
              <h4>最近错误</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="error in recentErrors"
                  :key="error.id"
                  :timestamp="formatTime(error.timestamp)"
                  type="danger"
                  size="small"
                >
                  {{ error.message }}
                </el-timeline-item>
              </el-timeline>
              <el-empty v-if="recentErrors.length === 0" description="暂无错误" :image-size="60" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, Refresh, Download, Message, CircleCheck, CircleClose,
  Timer, Top, Bottom, Connection, User, ChatDotRound
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// Refs
const loading = ref(false)
const timeRange = ref('today')
const trendType = ref('hourly')

// 图表refs
const trendChartRef = ref(null)
const successChartRef = ref(null)
const platformChartRef = ref(null)
const latencyChartRef = ref(null)
const messageTypeChartRef = ref(null)
const topChannelsChartRef = ref(null)

// 图表实例
let trendChart = null
let successChart = null
let platformChart = null
let latencyChart = null
let messageTypeChart = null
let topChannelsChart = null

// 数据
const statsData = ref({})

// 核心指标
const coreMetrics = computed(() => [
  {
    key: 'total',
    label: '总消息数',
    value: statsData.value.total || 0,
    change: statsData.value.totalChange,
    icon: Message,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    key: 'success',
    label: '成功转发',
    value: statsData.value.success || 0,
    change: statsData.value.successChange,
    icon: CircleCheck,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    key: 'failed',
    label: '失败数',
    value: statsData.value.failed || 0,
    change: statsData.value.failedChange,
    icon: CircleClose,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    key: 'avgLatency',
    label: '平均延迟',
    value: (statsData.value.avgLatency || 0) + 'ms',
    change: statsData.value.latencyChange,
    icon: Timer,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  }
])

// 实时状态
const realtimeStatus = computed(() => {
  const online = statsData.value.onlineAccounts || 0
  const total = statsData.value.totalAccounts || 0
  
  if (online === total && total > 0) {
    return { type: 'success', text: '全部在线' }
  } else if (online > 0) {
    return { type: 'warning', text: '部分在线' }
  } else {
    return { type: 'danger', text: '全部离线' }
  }
})

// 实时统计
const realtimeStats = computed(() => [
  {
    key: 'online',
    label: '在线账号',
    value: `${statsData.value.onlineAccounts || 0}/${statsData.value.totalAccounts || 0}`,
    icon: User,
    color: '#67C23A'
  },
  {
    key: 'active',
    label: '活跃Bot',
    value: statsData.value.activeBots || 0,
    icon: Connection,
    color: '#409EFF'
  },
  {
    key: 'channels',
    label: '监听频道',
    value: statsData.value.activeChannels || 0,
    icon: ChatDotRound,
    color: '#E6A23C'
  },
  {
    key: 'qps',
    label: '当前QPS',
    value: statsData.value.currentQPS || 0,
    icon: TrendCharts,
    color: '#F56C6C'
  }
])

// 最近错误
const recentErrors = ref([])

// 加载数据
async function loadData() {
  loading.value = true
  
  try {
    const response = await axios.get('/api/stats', {
      params: { range: timeRange.value }
    })
    
    statsData.value = response.data
    recentErrors.value = response.data.recentErrors || []
    
    // 更新所有图表
    updateAllCharts()
    
  } catch (error) {
    ElMessage.error('加载统计数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 初始化图表
function initCharts() {
  // 转发趋势图
  trendChart = echarts.init(trendChartRef.value)
  
  // 成功率饼图
  successChart = echarts.init(successChartRef.value)
  
  // 平台分布图
  platformChart = echarts.init(platformChartRef.value)
  
  // 延迟分布图
  latencyChart = echarts.init(latencyChartRef.value)
  
  // 消息类型图
  messageTypeChart = echarts.init(messageTypeChartRef.value)
  
  // Top频道图
  topChannelsChart = echarts.init(topChannelsChartRef.value)
  
  // 响应式调整
  window.addEventListener('resize', handleResize)
}

// 更新所有图表
function updateAllCharts() {
  updateTrendChart()
  updateSuccessChart()
  updatePlatformChart()
  updateLatencyChart()
  updateMessageTypeChart()
  updateTopChannelsChart()
}

// 更新转发趋势图
function updateTrendChart() {
  const data = statsData.value.trend || []
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['成功', '失败', '总计']
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
      data: data.map(d => d.time)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '成功',
        type: 'line',
        smooth: true,
        data: data.map(d => d.success),
        itemStyle: { color: '#67C23A' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: data.map(d => d.failed),
        itemStyle: { color: '#F56C6C' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '总计',
        type: 'line',
        smooth: true,
        data: data.map(d => d.total),
        itemStyle: { color: '#409EFF' }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 更新成功率饼图
function updateSuccessChart() {
  const total = statsData.value.total || 0
  const success = statsData.value.success || 0
  const failed = statsData.value.failed || 0
  const pending = statsData.value.pending || 0
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '状态分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        data: [
          { value: success, name: '成功', itemStyle: { color: '#67C23A' } },
          { value: failed, name: '失败', itemStyle: { color: '#F56C6C' } },
          { value: pending, name: '队列中', itemStyle: { color: '#E6A23C' } }
        ]
      }
    ]
  }
  
  successChart.setOption(option)
}

// 更新平台分布图
function updatePlatformChart() {
  const platforms = statsData.value.platforms || []
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        data: platforms.map(p => ({
          value: p.count,
          name: p.platform
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  platformChart.setOption(option)
}

// 更新延迟分布图
function updateLatencyChart() {
  const latency = statsData.value.latency || []
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: latency.map(l => l.range)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: latency.map(l => l.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  }
  
  latencyChart.setOption(option)
}

// 更新消息类型图
function updateMessageTypeChart() {
  const types = statsData.value.messageTypes || []
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        data: types.map(t => ({
          value: t.count,
          name: t.type
        }))
      }
    ]
  }
  
  messageTypeChart.setOption(option)
}

// 更新Top频道图
function updateTopChannelsChart() {
  const channels = statsData.value.topChannels || []
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: channels.map(c => c.name).reverse()
    },
    series: [
      {
        type: 'bar',
        data: channels.map(c => c.count).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        label: {
          show: true,
          position: 'right'
        }
      }
    ]
  }
  
  topChannelsChart.setOption(option)
}

// 导出报表
function exportReport() {
  const data = {
    time: new Date().toISOString(),
    range: timeRange.value,
    metrics: coreMetrics.value,
    ...statsData.value
  }
  
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `stats-report-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('报表已导出')
}

// 工具函数
function formatNumber(num) {
  if (typeof num !== 'number') return num
  return num.toLocaleString()
}

function getChangeType(change) {
  if (change === undefined) return 'info'
  return change >= 0 ? 'success' : 'danger'
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

function handleResize() {
  trendChart?.resize()
  successChart?.resize()
  platformChart?.resize()
  latencyChart?.resize()
  messageTypeChart?.resize()
  topChannelsChart?.resize()
}

// 生命周期
onMounted(() => {
  initCharts()
  loadData()
  
  // 30秒自动刷新
  const timer = setInterval(loadData, 30000)
  
  onUnmounted(() => {
    clearInterval(timer)
    window.removeEventListener('resize', handleResize)
    
    trendChart?.dispose()
    successChart?.dispose()
    platformChart?.dispose()
    latencyChart?.dispose()
    messageTypeChart?.dispose()
    topChannelsChart?.dispose()
  })
})
</script>

<style scoped>
.stats-dashboard-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  cursor: pointer;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-data {
  flex: 1;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #909399;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 320px;
}

.realtime-stats {
  height: 320px;
  overflow-y: auto;
}

.realtime-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.realtime-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.realtime-data {
  flex: 1;
}

.realtime-value {
  font-size: 24px;
  font-weight: 600;
}

.realtime-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.recent-errors h4 {
  margin: 16px 0 12px 0;
}
</style>
