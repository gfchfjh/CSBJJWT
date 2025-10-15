<template>
  <div class="charts-container">
    <!-- 转发量趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <span>📈 消息转发量趋势（最近24小时）</span>
      </template>
      <div ref="trendChart" class="chart" style="height: 300px"></div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 成功率饼图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🎯 转发成功率</span>
          </template>
          <div ref="successChart" class="chart" style="height: 250px"></div>
        </el-card>
      </el-col>

      <!-- 平台分布柱状图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>📊 平台消息分布</span>
          </template>
          <div ref="platformChart" class="chart" style="height: 250px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

// 图表实例
let trendChartInstance = null
let successChartInstance = null
let platformChartInstance = null

// 图表DOM引用
const trendChart = ref(null)
const successChart = ref(null)
const platformChart = ref(null)

// 初始化转发量趋势图
const initTrendChart = (data) => {
  if (!trendChart.value) return

  trendChartInstance = echarts.init(trendChart.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    xAxis: {
      type: 'category',
      data: data.hours || [],
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '消息数'
    },
    series: [
      {
        name: '转发量',
        type: 'line',
        data: data.counts || [],
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ]
          }
        },
        itemStyle: {
          color: '#409EFF'
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }

  trendChartInstance.setOption(option)
}

// 初始化成功率饼图
const initSuccessChart = (data) => {
  if (!successChart.value) return

  successChartInstance = echarts.init(successChart.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '转发状态',
        type: 'pie',
        radius: '60%',
        data: [
          { value: data.success || 0, name: '成功', itemStyle: { color: '#67C23A' } },
          { value: data.failed || 0, name: '失败', itemStyle: { color: '#F56C6C' } }
        ],
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

  successChartInstance.setOption(option)
}

// 初始化平台分布柱状图
const initPlatformChart = (data) => {
  if (!platformChart.value) return

  platformChartInstance = echarts.init(platformChart.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: data.platforms || ['Discord', 'Telegram', '飞书']
    },
    yAxis: {
      type: 'value',
      name: '消息数'
    },
    series: [
      {
        name: '转发量',
        type: 'bar',
        data: data.counts || [0, 0, 0],
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#409EFF' },
              { offset: 1, color: '#79bbff' }
            ]
          }
        },
        barWidth: '50%'
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }

  platformChartInstance.setOption(option)
}

// 获取图表数据
const fetchChartData = async () => {
  try {
    // 获取统计数据
    const stats = await api.getStats()
    
    // 模拟24小时数据（实际应该从后端获取）
    const hours = []
    const counts = []
    for (let i = 23; i >= 0; i--) {
      const hour = new Date()
      hour.setHours(hour.getHours() - i)
      hours.push(hour.getHours() + ':00')
      // 这里应该从后端获取实际数据
      counts.push(Math.floor(Math.random() * 100))
    }

    // 更新趋势图
    initTrendChart({ hours, counts })

    // 更新成功率图
    initSuccessChart({
      success: stats.success || 0,
      failed: stats.failed || 0
    })

    // 更新平台分布图
    // 这里需要后端提供按平台统计的API
    initPlatformChart({
      platforms: ['Discord', 'Telegram', '飞书'],
      counts: [
        Math.floor((stats.total || 0) * 0.5),
        Math.floor((stats.total || 0) * 0.3),
        Math.floor((stats.total || 0) * 0.2)
      ]
    })
  } catch (error) {
    console.error('获取图表数据失败:', error)
  }
}

// 窗口大小变化时调整图表
const handleResize = () => {
  trendChartInstance?.resize()
  successChartInstance?.resize()
  platformChartInstance?.resize()
}

let refreshInterval = null

onMounted(() => {
  // 初始化图表
  fetchChartData()

  // 定时刷新（每分钟）
  refreshInterval = setInterval(fetchChartData, 60000)

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }

  // 销毁图表实例
  trendChartInstance?.dispose()
  successChartInstance?.dispose()
  platformChartInstance?.dispose()

  // 移除事件监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.charts-container {
  width: 100%;
}

.chart-card {
  height: 100%;
}

.chart {
  width: 100%;
}
</style>
