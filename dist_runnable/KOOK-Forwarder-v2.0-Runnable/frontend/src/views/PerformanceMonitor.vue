<!--
性能监控面板
✅ P0-29: 实时性能指标和历史趋势分析
-->
<template>
  <div class="performance-monitor-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📊 性能监控</h2>
      <div class="header-actions">
        <el-button-group>
          <el-button :type="refreshEnabled ? 'primary' : ''" @click="toggleAutoRefresh">
            {{ refreshEnabled ? '⏸️ 停止刷新' : '▶️ 自动刷新' }}
          </el-button>
          <el-button @click="refreshData">🔄 立即刷新</el-button>
          <el-button @click="exportMetrics">📥 导出数据</el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="16" class="metrics-cards">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <i class="el-icon-cpu"></i>
          </div>
          <div class="metric-content">
            <div class="metric-label">CPU使用率</div>
            <div class="metric-value">{{ cpuUsage }}%</div>
            <el-progress :percentage="cpuUsage" :color="getProgressColor(cpuUsage)" :show-text="false"></el-progress>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <i class="el-icon-memory"></i>
          </div>
          <div class="metric-content">
            <div class="metric-label">内存使用率</div>
            <div class="metric-value">{{ memoryUsage }}%</div>
            <el-progress :percentage="memoryUsage" :color="getProgressColor(memoryUsage)" :show-text="false"></el-progress>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <i class="el-icon-clock"></i>
          </div>
          <div class="metric-content">
            <div class="metric-label">平均响应时间</div>
            <div class="metric-value">{{ avgResponseTime }}ms</div>
            <div class="metric-detail">最近1分钟</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <i class="el-icon-message"></i>
          </div>
          <div class="metric-content">
            <div class="metric-label">消息吞吐量</div>
            <div class="metric-value">{{ messageRate }}/s</div>
            <div class="metric-detail">每秒消息数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时趋势图 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>CPU & 内存使用率</span>
              <el-select v-model="resourceTimeRange" size="small" style="width: 120px;">
                <el-option label="最近1小时" value="1h"></el-option>
                <el-option label="最近6小时" value="6h"></el-option>
                <el-option label="最近24小时" value="24h"></el-option>
              </el-select>
            </div>
          </template>
          <div ref="resourceChartRef" class="chart-container" v-loading="loading"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>响应时间趋势</span>
              <el-select v-model="responseTimeRange" size="small" style="width: 120px;">
                <el-option label="最近1小时" value="1h"></el-option>
                <el-option label="最近6小时" value="6h"></el-option>
                <el-option label="最近24小时" value="24h"></el-option>
              </el-select>
            </div>
          </template>
          <div ref="responseTimeChartRef" class="chart-container" v-loading="loading"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>消息吞吐量</span>
          </template>
          <div ref="throughputChartRef" class="chart-container" v-loading="loading"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>队列长度</span>
          </template>
          <div ref="queueChartRef" class="chart-container" v-loading="loading"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警设置 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚠️ 告警阈值设置</span>
          <el-button size="small" type="primary" @click="saveAlertThresholds">💾 保存</el-button>
        </div>
      </template>

      <el-form :model="alertThresholds" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="CPU使用率告警">
              <el-input-number v-model="alertThresholds.cpu" :min="0" :max="100" :step="5">
                <template #append>%</template>
              </el-input-number>
              <span class="threshold-hint">超过此值将触发告警</span>
            </el-form-item>

            <el-form-item label="内存使用率告警">
              <el-input-number v-model="alertThresholds.memory" :min="0" :max="100" :step="5">
                <template #append>%</template>
              </el-input-number>
            </el-form-item>

            <el-form-item label="响应时间告警">
              <el-input-number v-model="alertThresholds.responseTime" :min="0" :step="100">
                <template #append>ms</template>
              </el-input-number>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="队列长度告警">
              <el-input-number v-model="alertThresholds.queueLength" :min="0" :step="10">
                <template #append>条</template>
              </el-input-number>
            </el-form-item>

            <el-form-item label="磁盘使用率告警">
              <el-input-number v-model="alertThresholds.disk" :min="0" :max="100" :step="5">
                <template #append>%</template>
              </el-input-number>
            </el-form-item>

            <el-form-item label="告警通知方式">
              <el-checkbox-group v-model="alertMethods">
                <el-checkbox label="桌面通知"></el-checkbox>
                <el-checkbox label="邮件通知"></el-checkbox>
                <el-checkbox label="系统日志"></el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 详细指标表格 -->
    <el-card>
      <template #header>
        <span>📋 详细性能指标</span>
      </template>

      <el-table :data="detailedMetrics" style="width: 100%">
        <el-table-column prop="name" label="指标名称" width="200"></el-table-column>
        <el-table-column prop="current" label="当前值" width="150"></el-table-column>
        <el-table-column prop="avg" label="平均值" width="150"></el-table-column>
        <el-table-column prop="max" label="峰值" width="150"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 核心指标
const cpuUsage = ref(0)
const memoryUsage = ref(0)
const avgResponseTime = ref(0)
const messageRate = ref(0)

// 图表引用
const resourceChartRef = ref(null)
const responseTimeChartRef = ref(null)
const throughputChartRef = ref(null)
const queueChartRef = ref(null)

// 图表实例
let resourceChart = null
let responseTimeChart = null
let throughputChart = null
let queueChart = null

// 时间范围
const resourceTimeRange = ref('1h')
const responseTimeRange = ref('1h')

// 加载状态
const loading = ref(false)

// 自动刷新
const refreshEnabled = ref(true)
let refreshTimer = null

// 告警阈值
const alertThresholds = ref({
  cpu: 80,
  memory: 85,
  responseTime: 5000,
  queueLength: 100,
  disk: 90
})

const alertMethods = ref(['桌面通知', '系统日志'])

// 详细指标
const detailedMetrics = ref([])

// 初始化
onMounted(async () => {
  await initCharts()
  await loadData()
  await loadAlertThresholds()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  disposeCharts()
})

// 初始化图表
async function initCharts() {
  // 资源使用率图表
  resourceChart = echarts.init(resourceChartRef.value)
  resourceChart.setOption(getResourceChartOption())

  // 响应时间图表
  responseTimeChart = echarts.init(responseTimeChartRef.value)
  responseTimeChart.setOption(getResponseTimeChartOption())

  // 吞吐量图表
  throughputChart = echarts.init(throughputChartRef.value)
  throughputChart.setOption(getThroughputChartOption())

  // 队列长度图表
  queueChart = echarts.init(queueChartRef.value)
  queueChart.setOption(getQueueChartOption())

  // 响应式
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  resourceChart?.resize()
  responseTimeChart?.resize()
  throughputChart?.resize()
  queueChart?.resize()
}

function disposeCharts() {
  resourceChart?.dispose()
  responseTimeChart?.dispose()
  throughputChart?.dispose()
  queueChart?.dispose()
  window.removeEventListener('resize', handleResize)
}

// 加载数据
async function loadData() {
  loading.value = true

  try {
    const response = await axios.get('/api/performance/metrics')
    const data = response.data

    // 更新核心指标
    cpuUsage.value = Math.round(data.cpu?.current || 0)
    memoryUsage.value = Math.round(data.memory?.current || 0)
    avgResponseTime.value = Math.round(data.responseTime?.avg || 0)
    messageRate.value = Math.round(data.throughput?.rate || 0)

    // 更新图表
    updateResourceChart(data.history?.resource || [])
    updateResponseTimeChart(data.history?.responseTime || [])
    updateThroughputChart(data.history?.throughput || [])
    updateQueueChart(data.history?.queue || [])

    // 更新详细指标
    updateDetailedMetrics(data)

  } catch (error) {
    console.error('加载性能数据失败:', error)
    ElMessage.error('加载性能数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
function updateResourceChart(data) {
  const timestamps = data.map(d => d.timestamp)
  const cpuData = data.map(d => d.cpu)
  const memoryData = data.map(d => d.memory)

  resourceChart.setOption({
    xAxis: { data: timestamps },
    series: [
      { data: cpuData },
      { data: memoryData }
    ]
  })
}

function updateResponseTimeChart(data) {
  const timestamps = data.map(d => d.timestamp)
  const responseData = data.map(d => d.value)

  responseTimeChart.setOption({
    xAxis: { data: timestamps },
    series: [{ data: responseData }]
  })
}

function updateThroughputChart(data) {
  const timestamps = data.map(d => d.timestamp)
  const throughputData = data.map(d => d.value)

  throughputChart.setOption({
    xAxis: { data: timestamps },
    series: [{ data: throughputData }]
  })
}

function updateQueueChart(data) {
  const timestamps = data.map(d => d.timestamp)
  const queueData = data.map(d => d.value)

  queueChart.setOption({
    xAxis: { data: timestamps },
    series: [{ data: queueData }]
  })
}

function updateDetailedMetrics(data) {
  detailedMetrics.value = [
    {
      name: 'CPU使用率',
      current: `${data.cpu?.current || 0}%`,
      avg: `${data.cpu?.avg || 0}%`,
      max: `${data.cpu?.max || 0}%`,
      status: data.cpu?.current > 80 ? '告警' : '正常',
      description: '服务器CPU使用情况'
    },
    {
      name: '内存使用率',
      current: `${data.memory?.current || 0}%`,
      avg: `${data.memory?.avg || 0}%`,
      max: `${data.memory?.max || 0}%`,
      status: data.memory?.current > 85 ? '告警' : '正常',
      description: '服务器内存使用情况'
    },
    {
      name: '平均响应时间',
      current: `${data.responseTime?.current || 0}ms`,
      avg: `${data.responseTime?.avg || 0}ms`,
      max: `${data.responseTime?.max || 0}ms`,
      status: data.responseTime?.avg > 5000 ? '慢' : '正常',
      description: 'API平均响应时间'
    },
    {
      name: '消息吞吐量',
      current: `${data.throughput?.rate || 0}/s`,
      avg: `${data.throughput?.avgRate || 0}/s`,
      max: `${data.throughput?.maxRate || 0}/s`,
      status: '正常',
      description: '每秒处理消息数'
    },
    {
      name: '队列长度',
      current: data.queue?.length || 0,
      avg: data.queue?.avgLength || 0,
      max: data.queue?.maxLength || 0,
      status: data.queue?.length > 100 ? '积压' : '正常',
      description: '待处理消息数'
    }
  ]
}

// 图表配置
function getResourceChartOption() {
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['CPU', '内存'] },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [
      { name: 'CPU', type: 'line', smooth: true, data: [], itemStyle: { color: '#667eea' } },
      { name: '内存', type: 'line', smooth: true, data: [], itemStyle: { color: '#f093fb' } }
    ]
  }
}

function getResponseTimeChartOption() {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}ms' } },
    series: [
      { name: '响应时间', type: 'line', smooth: true, data: [], itemStyle: { color: '#4facfe' }, areaStyle: { opacity: 0.3 } }
    ]
  }
}

function getThroughputChartOption() {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}/s' } },
    series: [
      { name: '吞吐量', type: 'bar', data: [], itemStyle: { color: '#fa709a' } }
    ]
  }
}

function getQueueChartOption() {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [
      { name: '队列长度', type: 'line', smooth: true, data: [], itemStyle: { color: '#fee140' }, areaStyle: { opacity: 0.3 } }
    ]
  }
}

// 自动刷新
function startAutoRefresh() {
  if (refreshTimer) return
  refreshTimer = setInterval(() => {
    if (refreshEnabled.value) {
      loadData()
    }
  }, 10000) // 每10秒刷新
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

function toggleAutoRefresh() {
  refreshEnabled.value = !refreshEnabled.value
}

function refreshData() {
  loadData()
  ElMessage.success('数据已刷新')
}

// 导出数据
async function exportMetrics() {
  try {
    const response = await axios.get('/api/performance/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `performance_metrics_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 告警阈值
async function loadAlertThresholds() {
  try {
    const response = await axios.get('/api/performance/alert-thresholds')
    alertThresholds.value = response.data
  } catch (error) {
    console.error('加载告警阈值失败:', error)
  }
}

async function saveAlertThresholds() {
  try {
    await axios.post('/api/performance/alert-thresholds', alertThresholds.value)
    ElMessage.success('告警阈值已保存')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 工具函数
function getProgressColor(value) {
  if (value >= 90) return '#F56C6C'
  if (value >= 70) return '#E6A23C'
  return '#67C23A'
}

function getStatusType(status) {
  const typeMap = {
    '正常': 'success',
    '告警': 'danger',
    '慢': 'warning',
    '积压': 'warning'
  }
  return typeMap[status] || 'info'
}
</script>

<style scoped>
.performance-monitor-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.metrics-cards {
  margin-bottom: 20px;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  margin-right: 15px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.metric-detail {
  font-size: 12px;
  color: #C0C4CC;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.threshold-hint {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}
</style>
