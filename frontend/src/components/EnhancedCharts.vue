<template>
  <div class="enhanced-charts">
    <!-- 转发趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="chart-header">
          <span>📈 转发趋势</span>
          <el-radio-group v-model="trendPeriod" size="small">
            <el-radio-button value="hour">最近24小时</el-radio-button>
            <el-radio-button value="day">最近7天</el-radio-button>
            <el-radio-button value="month">最近30天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <v-chart :option="trendChartOption" style="height: 300px" />
    </el-card>

    <!-- 平台分布与成功率 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🎯 平台分布</span>
          </template>
          <v-chart :option="platformPieOption" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>✅ 成功率统计</span>
          </template>
          <v-chart :option="successRateOption" style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 每小时热力图 -->
    <el-card class="chart-card" style="margin-top: 20px">
      <template #header>
        <span>🔥 24小时活动热力图</span>
      </template>
      <v-chart :option="heatmapOption" style="height: 200px" />
    </el-card>

    <!-- 频道排行榜 -->
    <el-card class="chart-card" style="margin-top: 20px">
      <template #header>
        <span>🏆 频道转发排行榜</span>
      </template>
      <v-chart :option="channelRankOption" style="height: 300px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  LineChart,
  PieChart,
  BarChart,
  HeatmapChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '@/api'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
])

const trendPeriod = ref('hour')
const chartData = ref({
  trend: [],
  platforms: [],
  successRate: [],
  heatmap: [],
  channelRank: []
})

// 转发趋势图配置
const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: ['总消息数', '成功', '失败']
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
    data: chartData.value.trend.map(item => item.time)
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '总消息数',
      type: 'line',
      data: chartData.value.trend.map(item => item.total),
      smooth: true,
      itemStyle: { color: '#409EFF' }
    },
    {
      name: '成功',
      type: 'line',
      data: chartData.value.trend.map(item => item.success),
      smooth: true,
      itemStyle: { color: '#67C23A' }
    },
    {
      name: '失败',
      type: 'line',
      data: chartData.value.trend.map(item => item.failed),
      smooth: true,
      itemStyle: { color: '#F56C6C' }
    }
  ]
}))

// 平台分布饼图
const platformPieOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    data: chartData.value.platforms.map(item => item.name)
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
        show: true,
        formatter: '{b}: {d}%'
      },
      data: chartData.value.platforms
    }
  ]
}))

// 成功率柱状图
const successRateOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
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
    data: chartData.value.successRate.map(item => item.platform)
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
      name: '成功率',
      type: 'bar',
      data: chartData.value.successRate.map(item => ({
        value: item.rate,
        itemStyle: {
          color: item.rate >= 95 ? '#67C23A' : item.rate >= 80 ? '#E6A23C' : '#F56C6C'
        }
      })),
      barWidth: '60%',
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%'
      }
    }
  ]
}))

// 24小时热力图
const heatmapOption = computed(() => ({
  tooltip: {
    position: 'top',
    formatter: '{c} 条消息'
  },
  grid: {
    height: '50%',
    top: '10%'
  },
  xAxis: {
    type: 'category',
    data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    splitArea: {
      show: true
    }
  },
  yAxis: {
    type: 'category',
    data: ['转发量'],
    splitArea: {
      show: true
    }
  },
  visualMap: {
    min: 0,
    max: 100,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '15%',
    inRange: {
      color: ['#e0f3ff', '#409EFF', '#1e3a8a']
    }
  },
  series: [
    {
      name: '转发量',
      type: 'heatmap',
      data: chartData.value.heatmap,
      label: {
        show: true
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

// 频道排行榜
const channelRankOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
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
    data: chartData.value.channelRank.map(item => item.name)
  },
  series: [
    {
      name: '转发次数',
      type: 'bar',
      data: chartData.value.channelRank.map((item, index) => ({
        value: item.count,
        itemStyle: {
          color: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#409EFF'
        }
      })),
      label: {
        show: true,
        position: 'right'
      }
    }
  ]
}))

// 加载图表数据
async function loadChartData() {
  try {
    const response = await api.get('/api/stats/charts', {
      params: { period: trendPeriod.value }
    })
    chartData.value = response.data
  } catch (error) {
    console.error('加载图表数据失败:', error)
    // 使用模拟数据
    useMockData()
  }
}

// 模拟数据（开发用）
function useMockData() {
  // 趋势数据
  chartData.value.trend = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    total: Math.floor(Math.random() * 100) + 50,
    success: Math.floor(Math.random() * 90) + 45,
    failed: Math.floor(Math.random() * 10)
  }))

  // 平台分布
  chartData.value.platforms = [
    { name: 'Discord', value: 45 },
    { name: 'Telegram', value: 35 },
    { name: '飞书', value: 20 }
  ]

  // 成功率
  chartData.value.successRate = [
    { platform: 'Discord', rate: 98.5 },
    { platform: 'Telegram', rate: 97.2 },
    { platform: '飞书', rate: 95.8 }
  ]

  // 热力图数据
  chartData.value.heatmap = Array.from({ length: 24 }, (_, i) => [
    i,
    0,
    Math.floor(Math.random() * 100)
  ])

  // 频道排行
  chartData.value.channelRank = [
    { name: '公告频道', count: 1234 },
    { name: '活动频道', count: 987 },
    { name: '更新日志', count: 765 },
    { name: '技术讨论', count: 543 },
    { name: '反馈建议', count: 321 }
  ]
}

onMounted(() => {
  loadChartData()
  
  // 每30秒刷新一次
  setInterval(loadChartData, 30000)
})
</script>

<style scoped>
.enhanced-charts {
  padding: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
