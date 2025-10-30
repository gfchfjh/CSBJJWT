<template>
  <div class="performance-monitor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📊 性能监控</span>
          <el-button-group size="small">
            <el-button :type="timeRange === '1h' ? 'primary' : ''" @click="changeTimeRange('1h')">
              1小时
            </el-button>
            <el-button :type="timeRange === '6h' ? 'primary' : ''" @click="changeTimeRange('6h')">
              6小时
            </el-button>
            <el-button :type="timeRange === '24h' ? 'primary' : ''" @click="changeTimeRange('24h')">
              24小时
            </el-button>
          </el-button-group>
        </div>
      </template>

      <!-- 实时指标卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <el-statistic title="CPU使用率" :value="metrics.cpuUsage" suffix="%" :precision="1">
              <template #prefix>
                <el-icon color="#409EFF"><Cpu /></el-icon>
              </template>
            </el-statistic>
            <el-progress
              :percentage="metrics.cpuUsage"
              :color="getProgressColor(metrics.cpuUsage)"
              :show-text="false"
              style="margin-top: 10px"
            />
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <el-statistic title="内存使用" :value="metrics.memoryUsage" suffix="%" :precision="1">
              <template #prefix>
                <el-icon color="#67C23A"><Monitor /></el-icon>
              </template>
            </el-statistic>
            <el-progress
              :percentage="metrics.memoryUsage"
              :color="getProgressColor(metrics.memoryUsage)"
              :show-text="false"
              style="margin-top: 10px"
            />
            <div class="metric-detail">
              {{ metrics.memoryUsedMB }} MB / {{ metrics.memoryTotalMB }} MB
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <el-statistic title="消息处理速度" :value="metrics.processingRate" suffix="条/分钟" :precision="0">
              <template #prefix>
                <el-icon color="#E6A23C"><ChatLineRound /></el-icon>
              </template>
            </el-statistic>
            <div class="metric-trend">
              <el-icon v-if="metrics.processingTrend > 0" color="#67C23A"><CaretTop /></el-icon>
              <el-icon v-else-if="metrics.processingTrend < 0" color="#F56C6C"><CaretBottom /></el-icon>
              <el-icon v-else color="#909399"><Minus /></el-icon>
              <span :style="{ color: getTrendColor(metrics.processingTrend) }">
                {{ Math.abs(metrics.processingTrend).toFixed(1) }}%
              </span>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <el-statistic title="队列积压" :value="metrics.queueSize" suffix="条" :precision="0">
              <template #prefix>
                <el-icon color="#F56C6C"><List /></el-icon>
              </template>
            </el-statistic>
            <el-tag
              :type="metrics.queueSize > 100 ? 'danger' : metrics.queueSize > 50 ? 'warning' : 'success'"
              style="margin-top: 10px"
            >
              {{ metrics.queueSize > 100 ? '拥堵' : metrics.queueSize > 50 ? '正常' : '畅通' }}
            </el-tag>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-title">消息处理趋势</div>
            <div ref="messageChart" style="height: 300px"></div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-title">系统资源使用</div>
            <div ref="resourceChart" style="height: 300px"></div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-title">平台转发分布</div>
            <div ref="platformChart" style="height: 300px"></div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-title">错误率趋势</div>
            <div ref="errorChart" style="height: 300px"></div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

// 响应式数据
const timeRange = ref('1h')
const metrics = ref({
  cpuUsage: 0,
  memoryUsage: 0,
  memoryUsedMB: 0,
  memoryTotalMB: 0,
  processingRate: 0,
  processingTrend: 0,
  queueSize: 0
})

// ECharts实例
let messageChartInstance = null
let resourceChartInstance = null
let platformChartInstance = null
let errorChartInstance = null

// 图表元素引用
const messageChart = ref(null)
const resourceChart = ref(null)
const platformChart = ref(null)
const errorChart = ref(null)

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

// 获取趋势颜色
const getTrendColor = (trend) => {
  if (trend > 0) return '#67C23A'
  if (trend < 0) return '#F56C6C'
  return '#909399'
}

// 切换时间范围
const changeTimeRange = (range) => {
  timeRange.value = range
  fetchData()
}

// 获取性能数据
const fetchData = async () => {
  try {
    const data = await api.getPerformanceMetrics(timeRange.value)
    
    // 更新实时指标
    metrics.value = data.metrics
    
    // 更新图表
    updateMessageChart(data.messageData)
    updateResourceChart(data.resourceData)
    updatePlatformChart(data.platformData)
    updateErrorChart(data.errorData)
  } catch (error) {
    console.error('获取性能数据失败:', error)
  }
}

// 初始化消息处理趋势图
const initMessageChart = () => {
  if (!messageChart.value) return
  
  messageChartInstance = echarts.init(messageChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['成功', '失败', '待处理']
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
      type: 'value',
      name: '消息数'
    },
    series: [
      {
        name: '成功',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          opacity: 0.3
        }
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#F56C6C'
        }
      },
      {
        name: '待处理',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#E6A23C'
        }
      }
    ]
  }
  
  messageChartInstance.setOption(option)
}

// 更新消息处理趋势图
const updateMessageChart = (data) => {
  if (!messageChartInstance || !data) return
  
  messageChartInstance.setOption({
    xAxis: {
      data: data.timeLabels
    },
    series: [
      { data: data.success },
      { data: data.failed },
      { data: data.pending }
    ]
  })
}

// 初始化资源使用图
const initResourceChart = () => {
  if (!resourceChart.value) return
  
  resourceChartInstance = echarts.init(resourceChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function (params) {
        let result = params[0].axisValueLabel + '<br/>'
        params.forEach(item => {
          result += item.marker + item.seriesName + ': ' + item.value.toFixed(1) + '%<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['CPU', '内存']
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
      type: 'value',
      name: '使用率 (%)',
      max: 100
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          opacity: 0.3
        }
      },
      {
        name: '内存',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  }
  
  resourceChartInstance.setOption(option)
}

// 更新资源使用图
const updateResourceChart = (data) => {
  if (!resourceChartInstance || !data) return
  
  resourceChartInstance.setOption({
    xAxis: {
      data: data.timeLabels
    },
    series: [
      { data: data.cpu },
      { data: data.memory }
    ]
  })
}

// 初始化平台分布饼图
const initPlatformChart = () => {
  if (!platformChart.value) return
  
  platformChartInstance = echarts.init(platformChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '平台分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: []
      }
    ]
  }
  
  platformChartInstance.setOption(option)
}

// 更新平台分布图
const updatePlatformChart = (data) => {
  if (!platformChartInstance || !data) return
  
  const colors = {
    'Discord': '#5865F2',
    'Telegram': '#0088CC',
    'Feishu': '#00B96B'
  }
  
  const seriesData = data.map(item => ({
    value: item.count,
    name: item.platform,
    itemStyle: {
      color: colors[item.platform] || '#409EFF'
    }
  }))
  
  platformChartInstance.setOption({
    series: [{
      data: seriesData
    }]
  })
}

// 初始化错误率趋势图
const initErrorChart = () => {
  if (!errorChart.value) return
  
  errorChartInstance = echarts.init(errorChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line'
      },
      formatter: function (params) {
        return params[0].axisValueLabel + '<br/>' +
               params[0].marker + '错误率: ' + params[0].value.toFixed(2) + '%'
      }
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
      type: 'value',
      name: '错误率 (%)',
      max: 10
    },
    series: [
      {
        name: '错误率',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#F56C6C'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(245, 108, 108, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(245, 108, 108, 0.05)'
            }
          ])
        },
        markLine: {
          data: [
            { type: 'average', name: '平均值' }
          ]
        }
      }
    ]
  }
  
  errorChartInstance.setOption(option)
}

// 更新错误率图
const updateErrorChart = (data) => {
  if (!errorChartInstance || !data) return
  
  errorChartInstance.setOption({
    xAxis: {
      data: data.timeLabels
    },
    series: [{
      data: data.errorRates
    }]
  })
}

// 定时刷新
let refreshInterval = null

onMounted(() => {
  // 初始化所有图表
  initMessageChart()
  initResourceChart()
  initPlatformChart()
  initErrorChart()
  
  // 窗口大小改变时重绘图表
  window.addEventListener('resize', () => {
    messageChartInstance?.resize()
    resourceChartInstance?.resize()
    platformChartInstance?.resize()
    errorChartInstance?.resize()
  })
  
  // 首次加载数据
  fetchData()
  
  // 每30秒刷新一次
  refreshInterval = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  
  // 销毁图表实例
  messageChartInstance?.dispose()
  resourceChartInstance?.dispose()
  platformChartInstance?.dispose()
  errorChartInstance?.dispose()
})
</script>

<style scoped>
.performance-monitor {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  text-align: center;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-detail {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.metric-trend {
  margin-top: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.chart-container {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.chart-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}
</style>
