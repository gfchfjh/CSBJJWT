<template>
  <div class="home-enhanced">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="48" color="#409EFF">
              <Message />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(stats.total) }}</div>
              <div class="stat-label">今日转发</div>
              <div class="stat-trend" :class="trendClass(stats.trend)">
                <el-icon><TrendCharts /></el-icon>
                {{ stats.trend }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="48" color="#67C23A">
              <CircleCheck />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.success_rate }}%</div>
              <div class="stat-label">成功率</div>
              <el-progress
                :percentage="stats.success_rate"
                :stroke-width="4"
                :show-text="false"
                :color="getSuccessRateColor(stats.success_rate)"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="48" color="#E6A23C">
              <Timer />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avg_latency }}ms</div>
              <div class="stat-label">平均延迟</div>
              <el-tag
                :type="getLatencyType(stats.avg_latency)"
                size="small"
              >
                {{ getLatencyText(stats.avg_latency) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="48" color="#F56C6C">
              <Warning />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStore.status.queue_size || 0 }}</div>
              <div class="stat-label">队列消息</div>
              <el-button
                v-if="systemStore.status.queue_size > 0"
                link
                type="primary"
                size="small"
                @click="viewQueue"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 服务控制 + 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="service-control-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🎮 服务控制</span>
              <el-tag
                :type="serviceStatusType"
                size="large"
                effect="dark"
              >
                {{ serviceStatusText }}
              </el-tag>
            </div>
          </template>
          
          <div class="service-content">
            <div class="service-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="运行状态">
                  <el-tag :type="serviceStatusType">
                    {{ systemStore.status.service_running ? '运行中' : '已停止' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="运行时长">
                  {{ formatUptime(systemStore.status.uptime) }}
                </el-descriptions-item>
                <el-descriptions-item label="账号状态">
                  {{ accountsStore.onlineCount }} / {{ accountsStore.total }} 在线
                </el-descriptions-item>
                <el-descriptions-item label="Bot状态">
                  {{ botsStore.activeCount }} / {{ botsStore.total }} 活跃
                </el-descriptions-item>
              </el-descriptions>
            </div>
            
            <div class="service-actions">
              <el-button-group>
                <el-button
                  v-if="!systemStore.status.service_running"
                  type="success"
                  size="large"
                  :loading="starting"
                  @click="startService"
                >
                  <el-icon><VideoPlay /></el-icon>
                  启动服务
                </el-button>
                
                <el-button
                  v-else
                  type="danger"
                  size="large"
                  :loading="stopping"
                  @click="stopService"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止服务
                </el-button>
                
                <el-button
                  size="large"
                  :loading="restarting"
                  :disabled="!systemStore.status.service_running"
                  @click="restartService"
                >
                  <el-icon><Refresh /></el-icon>
                  重启服务
                </el-button>
              </el-button-group>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="quick-actions-card" shadow="hover">
          <template #header>
            <span>⚡ 快捷操作</span>
          </template>
          
          <div class="quick-actions">
            <el-button
              class="action-button"
              @click="testForward"
              :loading="testing"
            >
              <el-icon><MessageBox /></el-icon>
              测试转发
            </el-button>
            
            <el-button
              class="action-button"
              @click="clearQueue"
              :disabled="systemStore.status.queue_size === 0"
            >
              <el-icon><Delete /></el-icon>
              清空队列
              <el-badge
                v-if="systemStore.status.queue_size > 0"
                :value="systemStore.status.queue_size"
                class="badge"
              />
            </el-button>
            
            <el-button
              class="action-button"
              @click="viewLogs"
            >
              <el-icon><Document /></el-icon>
              查看日志
            </el-button>
            
            <el-button
              class="action-button"
              @click="openSettings"
            >
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实时监控图表 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📈 实时监控（最近24小时）</span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button value="line">折线图</el-radio-button>
                <el-radio-button value="bar">柱状图</el-radio-button>
                <el-radio-button value="area">面积图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          
          <v-chart
            :option="messageChartOption"
            autoresize
            style="height: 300px"
          />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <span>📊 关键指标</span>
          </template>
          
          <div class="key-metrics">
            <div class="metric-item">
              <div class="metric-label">峰值速率</div>
              <div class="metric-value">{{ stats.peakRate }} msg/min</div>
              <el-progress
                :percentage="(stats.peakRate / 100) * 100"
                :stroke-width="6"
                :show-text="false"
                color="#409EFF"
              />
            </div>
            
            <el-divider />
            
            <div class="metric-item">
              <div class="metric-label">平均速率</div>
              <div class="metric-value">{{ stats.avgRate }} msg/min</div>
              <el-progress
                :percentage="(stats.avgRate / stats.peakRate) * 100"
                :stroke-width="6"
                :show-text="false"
                color="#67C23A"
              />
            </div>
            
            <el-divider />
            
            <div class="metric-item">
              <div class="metric-label">当前速率</div>
              <div class="metric-value current">
                {{ stats.currentRate }} msg/min
              </div>
              <el-tag
                :type="getRateTagType(stats.currentRate)"
                effect="dark"
              >
                {{ getRateText(stats.currentRate) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 系统健康状态 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="health-card" shadow="hover">
          <template #header>
            <span>💊 系统健康状态</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="health-item">
                <el-icon :size="32" :color="getHealthColor('backend')">
                  <Monitor />
                </el-icon>
                <div class="health-text">
                  <div class="health-name">后端服务</div>
                  <div class="health-status">{{ healthStatus.backend }}</div>
                </div>
              </div>
            </el-col>
            
            <el-col :span="6">
              <div class="health-item">
                <el-icon :size="32" :color="getHealthColor('redis')">
                  <Connection />
                </el-icon>
                <div class="health-text">
                  <div class="health-name">Redis</div>
                  <div class="health-status">{{ healthStatus.redis }}</div>
                </div>
              </div>
            </el-col>
            
            <el-col :span="6">
              <div class="health-item">
                <el-icon :size="32" :color="getHealthColor('database')">
                  <Coin />
                </el-icon>
                <div class="health-text">
                  <div class="health-name">数据库</div>
                  <div class="health-status">{{ healthStatus.database }}</div>
                </div>
              </div>
            </el-col>
            
            <el-col :span="6">
              <div class="health-item">
                <el-icon :size="32" :color="getHealthColor('playwright')">
                  <Monitor />
                </el-icon>
                <div class="health-text">
                  <div class="health-name">浏览器</div>
                  <div class="health-status">{{ healthStatus.playwright }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
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
  Message,
  CircleCheck,
  Timer,
  Warning,
  VideoPlay,
  VideoPause,
  Refresh,
  MessageBox,
  Delete,
  Document,
  Setting,
  TrendCharts,
  Monitor,
  Connection,
  Coin,
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useSystemStore } from '@/store/system'
import { useAccountsStore } from '@/store/accounts'
import { useBotsStore } from '@/store/bots'
import api from '@/api'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const router = useRouter()
const systemStore = useSystemStore()
const accountsStore = useAccountsStore()
const botsStore = useBotsStore()

const stats = ref({
  total: 1234,
  success_rate: 98.5,
  avg_latency: 1200,
  trend: +15.3,
  peakRate: 85,
  avgRate: 42,
  currentRate: 38,
})

const starting = ref(false)
const stopping = ref(false)
const restarting = ref(false)
const testing = ref(false)

const chartType = ref('line')

const healthStatus = ref({
  backend: '正常',
  redis: '正常',
  database: '正常',
  playwright: '正常',
})

const serviceStatusType = computed(() => {
  return systemStore.status.service_running ? 'success' : 'danger'
})

const serviceStatusText = computed(() => {
  return systemStore.status.service_running ? '🟢 运行中' : '🔴 已停止'
})

const messageChartOption = computed(() => {
  const type = chartType.value
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['成功', '失败', '总计'],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: type !== 'line',
      data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '成功',
        type: type === 'area' ? 'line' : type,
        data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330],
        smooth: true,
        areaStyle: type === 'area' ? {} : undefined,
        itemStyle: {
          color: '#67C23A',
        },
      },
      {
        name: '失败',
        type: type === 'area' ? 'line' : type,
        data: [2, 3, 2, 1, 3, 4, 2, 3, 2, 4, 5, 3],
        smooth: true,
        areaStyle: type === 'area' ? {} : undefined,
        itemStyle: {
          color: '#F56C6C',
        },
      },
      {
        name: '总计',
        type: type === 'area' ? 'line' : type,
        data: [122, 135, 103, 135, 93, 234, 212, 185, 193, 238, 295, 333],
        smooth: true,
        areaStyle: type === 'area' ? {} : undefined,
        itemStyle: {
          color: '#409EFF',
        },
      },
    ],
  }
})

const formatNumber = (num) => {
  return num?.toLocaleString() || 0
}

const formatUptime = (seconds) => {
  if (!seconds) return '0秒'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}天${hours}小时`
  if (hours > 0) return `${hours}小时${minutes}分钟`
  return `${minutes}分钟`
}

const trendClass = (trend) => {
  return trend > 0 ? 'trend-up' : 'trend-down'
}

const getSuccessRateColor = (rate) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 90) return '#E6A23C'
  return '#F56C6C'
}

const getLatencyType = (latency) => {
  if (latency < 1000) return 'success'
  if (latency < 3000) return 'warning'
  return 'danger'
}

const getLatencyText = (latency) => {
  if (latency < 1000) return '优秀'
  if (latency < 3000) return '良好'
  return '较慢'
}

const getRateTagType = (rate) => {
  if (rate > 60) return 'danger'
  if (rate > 40) return 'warning'
  return 'success'
}

const getRateText = (rate) => {
  if (rate > 60) return '高负载'
  if (rate > 40) return '正常'
  return '空闲'
}

const getHealthColor = (service) => {
  const status = healthStatus.value[service]
  if (status === '正常') return '#67C23A'
  if (status === '警告') return '#E6A23C'
  return '#F56C6C'
}

const startService = async () => {
  try {
    starting.value = true
    await api.startService()
    ElMessage.success('服务启动成功')
    systemStore.status.service_running = true
  } catch (error) {
    ElMessage.error('服务启动失败：' + error.message)
  } finally {
    starting.value = false
  }
}

const stopService = async () => {
  try {
    await ElMessageBox.confirm(
      '停止服务将中断所有正在进行的消息转发，确定要停止吗？',
      '确认停止',
      {
        type: 'warning',
        confirmButtonText: '确定停止',
        cancelButtonText: '取消',
      }
    )
    
    stopping.value = true
    await api.stopService()
    ElMessage.success('服务已停止')
    systemStore.status.service_running = false
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('服务停止失败：' + error.message)
    }
  } finally {
    stopping.value = false
  }
}

const restartService = async () => {
  try {
    restarting.value = true
    await api.restartService()
    ElMessage.success('服务重启成功')
  } catch (error) {
    ElMessage.error('服务重启失败：' + error.message)
  } finally {
    restarting.value = false
  }
}

const testForward = async () => {
  try {
    testing.value = true
    const result = await api.testForward()
    
    ElMessageBox.alert(
      `测试消息已发送到所有配置的Bot\n\n成功: ${result.success}\n失败: ${result.failed}`,
      '测试结果',
      {
        type: result.failed === 0 ? 'success' : 'warning',
      }
    )
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  } finally {
    testing.value = false
  }
}

const clearQueue = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清空队列中的 ${systemStore.status.queue_size} 条消息吗？此操作不可恢复。`,
      '确认清空',
      {
        type: 'warning',
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
      }
    )
    
    await api.clearQueue()
    ElMessage.success('队列已清空')
    systemStore.status.queue_size = 0
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败：' + error.message)
    }
  }
}

const viewQueue = () => {
  router.push('/logs?filter=pending')
}

const viewLogs = () => {
  router.push('/logs')
}

const openSettings = () => {
  router.push('/settings')
}

// 定期刷新数据
let refreshTimer = null

onMounted(() => {
  refreshTimer = setInterval(() => {
    // 刷新统计数据
    api.getStats().then(data => {
      Object.assign(stats.value, data)
    })
    
    // 刷新健康状态
    api.getHealth().then(data => {
      Object.assign(healthStatus.value, data)
    })
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.home-enhanced {
  padding: 20px;
}

.stat-card {
  height: 100%;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-trend {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
}

.trend-up {
  color: #67C23A;
}

.trend-down {
  color: #F56C6C;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.service-actions {
  display: flex;
  justify-content: center;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.action-button {
  width: 100%;
  height: 60px;
  font-size: 14px;
}

.chart-card,
.stats-card,
.health-card {
  height: 100%;
}

.key-metrics {
  padding: 10px 0;
}

.metric-item {
  padding: 10px 0;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
}

.metric-value.current {
  color: #409EFF;
}

.health-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  border-radius: 8px;
  background: #f5f7fa;
  transition: all 0.3s;
}

.health-item:hover {
  background: #ecf5ff;
  transform: translateX(5px);
}

.health-text {
  flex: 1;
}

.health-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.health-status {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}
</style>
