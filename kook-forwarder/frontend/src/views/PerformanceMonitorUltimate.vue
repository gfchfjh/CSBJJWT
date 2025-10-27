<template>
  <div class="performance-monitor">
    <!-- 系统资源卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card cpu-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40"><Cpu /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.cpu_percent }}%</div>
              <div class="stat-label">CPU使用率</div>
            </div>
          </div>
          <el-progress
            :percentage="systemStats.cpu_percent"
            :color="getResourceColor(systemStats.cpu_percent)"
            :show-text="false"
          />
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card memory-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40"><Odometer /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.memory_percent }}%</div>
              <div class="stat-label">内存使用率</div>
            </div>
          </div>
          <el-progress
            :percentage="systemStats.memory_percent"
            :color="getResourceColor(systemStats.memory_percent)"
            :show-text="false"
          />
          <div class="stat-detail">
            {{ systemStats.memory_used_mb }} MB / {{ systemStats.memory_total_mb }} MB
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card disk-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40"><FolderOpened /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.disk_percent }}%</div>
              <div class="stat-label">磁盘使用率</div>
            </div>
          </div>
          <el-progress
            :percentage="systemStats.disk_percent"
            :color="getResourceColor(systemStats.disk_percent)"
            :show-text="false"
          />
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card network-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40"><Connection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.network_mbps }}</div>
              <div class="stat-label">网络速度 (Mbps)</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实时性能图表 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span><el-icon><TrendCharts /></el-icon> CPU/内存使用率（最近1小时）</span>
          </template>
          <div ref="cpuChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span><el-icon><DataLine /></el-icon> 消息处理速率（最近1小时）</span>
          </template>
          <div ref="messageChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 性能瓶颈分析 -->
    <el-card shadow="never" class="analysis-card">
      <template #header>
        <span><el-icon><Warning /></el-icon> 性能瓶颈分析</span>
      </template>
      
      <el-table :data="bottlenecks" stripe>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="component" label="组件" width="150" />
        <el-table-column prop="issue" label="问题" />
        <el-table-column label="建议" width="200">
          <template #default="{ row }">
            <el-button size="small" text @click="showSolution(row)">
              查看解决方案
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 慢查询分析 -->
    <el-card shadow="never" class="slow-queries-card">
      <template #header>
        <span><el-icon><Timer /></el-icon> 慢操作分析（耗时>1秒）</span>
      </template>
      
      <el-table :data="slowQueries" stripe>
        <el-table-column prop="operation" label="操作" width="200" />
        <el-table-column label="耗时" width="120">
          <template #default="{ row }">
            <el-tag type="warning">{{ row.duration }}ms</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="details" label="详情" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import {
  Cpu,
  Odometer,
  FolderOpened,
  Connection,
  TrendCharts,
  DataLine,
  Warning,
  Timer
} from '@element-plus/icons-vue'
import api from '@/api'

const systemStats = ref({
  cpu_percent: 0,
  memory_percent: 0,
  memory_used_mb: 0,
  memory_total_mb: 0,
  disk_percent: 0,
  network_mbps: 0
})

const bottlenecks = ref([])
const slowQueries = ref([])

const cpuChartRef = ref(null)
const messageChartRef = ref(null)
let cpuChart = null
let messageChart = null
let updateInterval = null

const cpuData = ref([])
const memoryData = ref([])
const messageRateData = ref([])
const timeLabels = ref([])

const getResourceColor = (percentage) => {
  if (percentage >= 90) return '#F56C6C'
  if (percentage >= 70) return '#E6A23C'
  return '#67C23A'
}

const getSeverityType = (severity) => {
  const types = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[severity] || 'info'
}

const getSeverityText = (severity) => {
  const texts = {
    critical: '严重',
    warning: '警告',
    info: '提示'
  }
  return texts[severity] || severity
}

const showSolution = (bottleneck) => {
  ElMessageBox.alert(bottleneck.solution, '解决方案', {
    confirmButtonText: '知道了'
  })
}

const initCharts = () => {
  // CPU/内存图表
  if (cpuChartRef.value) {
    cpuChart = echarts.init(cpuChartRef.value)
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['CPU', '内存']
      },
      xAxis: {
        type: 'category',
        data: timeLabels.value,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: 'CPU',
          type: 'line',
          smooth: true,
          data: cpuData.value,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '内存',
          type: 'line',
          smooth: true,
          data: memoryData.value,
          itemStyle: { color: '#67C23A' }
        }
      ]
    }
    
    cpuChart.setOption(option)
  }
  
  // 消息处理速率图表
  if (messageChartRef.value) {
    messageChart = echarts.init(messageChartRef.value)
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: timeLabels.value,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value} 条/分'
        }
      },
      series: [
        {
          name: '消息速率',
          type: 'line',
          smooth: true,
          data: messageRateData.value,
          areaStyle: {},
          itemStyle: { color: '#E6A23C' }
        }
      ]
    }
    
    messageChart.setOption(option)
  }
}

const updateStats = async () => {
  try {
    const response = await api.get('/api/performance/stats')
    const data = response.data
    
    systemStats.value = data.system
    
    // 更新图表数据
    const now = new Date().toLocaleTimeString()
    timeLabels.value.push(now)
    cpuData.value.push(data.system.cpu_percent)
    memoryData.value.push(data.system.memory_percent)
    messageRateData.value.push(data.message_rate || 0)
    
    // 保持最近60个数据点（1小时，每分钟更新）
    if (timeLabels.value.length > 60) {
      timeLabels.value.shift()
      cpuData.value.shift()
      memoryData.value.shift()
      messageRateData.value.shift()
    }
    
    // 更新图表
    if (cpuChart) {
      cpuChart.setOption({
        xAxis: { data: timeLabels.value },
        series: [
          { data: cpuData.value },
          { data: memoryData.value }
        ]
      })
    }
    
    if (messageChart) {
      messageChart.setOption({
        xAxis: { data: timeLabels.value },
        series: [{ data: messageRateData.value }]
      })
    }
    
  } catch (error) {
    console.error('更新性能统计失败:', error)
  }
}

const analyzeBottlenecks = async () => {
  try {
    const response = await api.get('/api/performance/bottlenecks')
    bottlenecks.value = response.data
  } catch (error) {
    console.error('分析性能瓶颈失败:', error)
  }
}

const loadSlowQueries = async () => {
  try {
    const response = await api.get('/api/performance/slow-queries')
    slowQueries.value = response.data
  } catch (error) {
    console.error('加载慢查询失败:', error)
  }
}

onMounted(() => {
  initCharts()
  updateStats()
  analyzeBottlenecks()
  loadSlowQueries()
  
  // 每分钟更新一次
  updateInterval = setInterval(() => {
    updateStats()
    analyzeBottlenecks()
    loadSlowQueries()
  }, 60000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  
  if (cpuChart) {
    cpuChart.dispose()
  }
  
  if (messageChart) {
    messageChart.dispose()
  }
})
</script>

<style scoped>
.performance-monitor {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.cpu-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.memory-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.disk-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.network-card {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.stat-detail {
  margin-top: 10px;
  font-size: 12px;
  opacity: 0.8;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.analysis-card,
.slow-queries-card {
  margin-top: 20px;
}
</style>
