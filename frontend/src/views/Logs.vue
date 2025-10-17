<template>
  <div class="logs-view">
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="今日转发" :value="stats.total">
            <template #suffix>条</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="成功率" :value="stats.success_rate" :precision="1">
            <template #suffix>%</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="平均延迟" :value="stats.avg_latency" :precision="0">
            <template #suffix>ms</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="失败消息" :value="stats.failed" value-style="color: #f56c6c">
            <template #suffix>条</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时转发趋势图 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>📈 实时转发趋势（最近1小时）</span>
          <el-radio-group v-model="chartTimeRange" size="small" @change="updateChartData">
            <el-radio-button label="1h">1小时</el-radio-button>
            <el-radio-button label="6h">6小时</el-radio-button>
            <el-radio-button label="24h">24小时</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="chartRef" style="height: 300px"></div>
    </el-card>

    <!-- 日志列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📋 实时转发日志</span>
          <div class="header-actions">
            <el-select 
              v-model="filterStatus" 
              placeholder="状态" 
              style="width: 120px; margin-right: 10px"
              @change="fetchLogs"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="队列中" value="pending" />
            </el-select>
            <el-select 
              v-model="filterPlatform" 
              placeholder="平台" 
              style="width: 120px; margin-right: 10px"
              @change="fetchLogs"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="Discord" value="discord" />
              <el-option label="Telegram" value="telegram" />
              <el-option label="飞书" value="feishu" />
            </el-select>
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              inactive-text="暂停"
              style="margin-right: 10px"
            />
            <el-button size="small" @click="fetchLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredLogs" border style="width: 100%" max-height="500">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="kook_channel_id" label="KOOK频道" width="120">
          <template #default="{ row }">
            <el-tooltip :content="row.kook_channel_id" placement="top">
              <span>{{ getChannelName(row.kook_channel_id) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="sender_name" label="发送者" width="120" />
        <el-table-column prop="content" label="内容" min-width="250">
          <template #default="{ row }">
            <el-tooltip :content="row.content" placement="top">
              <span class="text-ellipsis">
                {{ row.content ? row.content.substring(0, 50) : '' }}{{ row.content && row.content.length > 50 ? '...' : '' }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="message_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getMessageTypeColor(row.message_type)">
              {{ getMessageTypeName(row.message_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_platform" label="目标平台" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.target_platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latency_ms" label="延迟" width="80">
          <template #default="{ row }">
            <span :style="{ color: getLatencyColor(row.latency_ms) }">
              {{ row.latency_ms }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" min-width="200">
          <template #default="{ row }">
            <el-tooltip v-if="row.error_message" :content="row.error_message" placement="top">
              <span class="text-error">
                {{ row.error_message.substring(0, 30) }}{{ row.error_message.length > 30 ? '...' : '' }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="showMessageDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="logs.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="消息详情"
      width="700px"
    >
      <el-descriptions v-if="selectedMessage" :column="2" border>
        <el-descriptions-item label="消息ID">
          {{ selectedMessage.kook_message_id }}
        </el-descriptions-item>
        <el-descriptions-item label="发送时间">
          {{ formatTime(selectedMessage.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="发送者">
          {{ selectedMessage.sender_name }}
        </el-descriptions-item>
        <el-descriptions-item label="消息类型">
          {{ getMessageTypeName(selectedMessage.message_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="KOOK频道">
          {{ selectedMessage.kook_channel_id }}
        </el-descriptions-item>
        <el-descriptions-item label="目标平台">
          {{ selectedMessage.target_platform }}
        </el-descriptions-item>
        <el-descriptions-item label="目标频道">
          {{ selectedMessage.target_channel }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedMessage.status)">
            {{ getStatusText(selectedMessage.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="延迟">
          {{ selectedMessage.latency_ms }}ms
        </el-descriptions-item>
        <el-descriptions-item label="内容" :span="2">
          <div class="message-content">
            {{ selectedMessage.content }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item v-if="selectedMessage.error_message" label="错误信息" :span="2">
          <div class="text-error">
            {{ selectedMessage.error_message }}
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import api from '../api'
import { getLogsWS } from '../utils/websocket'

const logs = ref([])
const stats = ref({
  total: 0,
  success_rate: 0,
  avg_latency: 0,
  failed: 0
})

const filterStatus = ref('')
const filterPlatform = ref('')
const autoRefresh = ref(true)
const currentPage = ref(1)
const pageSize = ref(50)

const chartRef = ref(null)
const chartTimeRange = ref('1h')
let chart = null

const showDetailDialog = ref(false)
const selectedMessage = ref(null)

// 过滤后的日志
const filteredLogs = computed(() => {
  let result = logs.value

  if (filterStatus.value) {
    result = result.filter(log => log.status === filterStatus.value)
  }

  if (filterPlatform.value) {
    result = result.filter(log => log.target_platform === filterPlatform.value)
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 获取日志
const fetchLogs = async () => {
  try {
    logs.value = await api.getLogs(1000, filterStatus.value)
    calculateStats()
  } catch (error) {
    console.error('获取日志失败:', error)
  }
}

// 计算统计数据
const calculateStats = () => {
  const total = logs.value.length
  const successCount = logs.value.filter(log => log.status === 'success').length
  const failedCount = logs.value.filter(log => log.status === 'failed').length
  
  // 计算平均延迟（只统计成功的）
  const successLogs = logs.value.filter(log => log.status === 'success' && log.latency_ms)
  const avgLatency = successLogs.length > 0
    ? successLogs.reduce((sum, log) => sum + (log.latency_ms || 0), 0) / successLogs.length
    : 0

  stats.value = {
    total,
    success_rate: total > 0 ? (successCount / total) * 100 : 0,
    avg_latency: avgLatency,
    failed: failedCount
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChartData()
}

// 更新图表数据
const updateChartData = () => {
  if (!chart) return

  // 生成时间序列数据
  const now = new Date()
  const timeRangeMinutes = chartTimeRange.value === '1h' ? 60 : chartTimeRange.value === '6h' ? 360 : 1440
  const intervalMinutes = chartTimeRange.value === '1h' ? 1 : chartTimeRange.value === '6h' ? 10 : 30

  const timeLabels = []
  const successData = []
  const failedData = []

  // 生成时间点
  for (let i = timeRangeMinutes; i >= 0; i -= intervalMinutes) {
    const time = new Date(now.getTime() - i * 60 * 1000)
    timeLabels.push(formatChartTime(time))
    
    // 统计该时间段的消息数
    const rangeStart = new Date(time.getTime() - intervalMinutes * 60 * 1000)
    const rangeEnd = time

    const logsInRange = logs.value.filter(log => {
      const logTime = new Date(log.created_at)
      return logTime >= rangeStart && logTime <= rangeEnd
    })

    successData.push(logsInRange.filter(log => log.status === 'success').length)
    failedData.push(logsInRange.filter(log => log.status === 'failed').length)
  }

  const option = {
    title: {
      text: ''
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['成功', '失败']
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
      data: timeLabels
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
        data: successData,
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
        data: failedData,
        itemStyle: {
          color: '#F56C6C'
        },
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  }

  chart.setOption(option)
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
}

const formatChartTime = (time) => {
  return `${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`
}

// 获取频道名称
const getChannelName = (channelId) => {
  // TODO: 从映射表中获取频道名称
  return channelId ? channelId.substring(0, 8) : '-'
}

// 获取消息类型名称
const getMessageTypeName = (type) => {
  const typeMap = {
    'text': '文本',
    'image': '图片',
    'file': '文件',
    'video': '视频',
    'audio': '音频',
    'card': '卡片'
  }
  return typeMap[type] || type || '未知'
}

// 获取消息类型颜色
const getMessageTypeColor = (type) => {
  const colorMap = {
    'text': '',
    'image': 'success',
    'file': 'warning',
    'video': 'danger',
    'audio': 'info'
  }
  return colorMap[type] || ''
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'success': 'success',
    'failed': 'danger',
    'pending': 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'success': '✅ 成功',
    'failed': '❌ 失败',
    'pending': '⏳ 队列中'
  }
  return textMap[status] || status
}

// 获取延迟颜色
const getLatencyColor = (latency) => {
  if (!latency) return '#909399'
  if (latency < 1000) return '#67C23A'
  if (latency < 3000) return '#E6A23C'
  return '#F56C6C'
}

// 显示消息详情
const showMessageDetail = (message) => {
  selectedMessage.value = message
  showDetailDialog.value = true
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

let logsInterval = null
let wsClient = null

// 监听数据变化，更新图表
watch(() => logs.value, () => {
  updateChartData()
}, { deep: true })

// 初始化WebSocket连接
const initWebSocket = () => {
  try {
    wsClient = getLogsWS()
    
    // 监听新消息日志
    wsClient.on('new_log', (data) => {
      // 将新日志添加到列表顶部
      logs.value.unshift(data)
      // 重新计算统计
      calculateStats()
      // 显示通知
      if (data.status === 'failed') {
        ElMessage.warning(`消息转发失败: ${data.error_message}`)
      }
    })
    
    // 监听连接状态
    wsClient.on('connected', () => {
      console.log('WebSocket已连接 - 实时日志推送已启用')
    })
    
    wsClient.on('disconnected', () => {
      console.log('WebSocket已断开 - 切换到轮询模式')
    })
    
    wsClient.on('reconnect_failed', () => {
      ElMessage.error('WebSocket连接失败，使用轮询模式')
    })
  } catch (error) {
    console.error('WebSocket初始化失败:', error)
    // 降级到轮询模式
  }
}

onMounted(async () => {
  await fetchLogs()
  await nextTick()
  initChart()

  // 尝试初始化WebSocket
  initWebSocket()

  // 轮询作为备用方案（如果WebSocket连接失败）
  logsInterval = setInterval(() => {
    if (autoRefresh.value && (!wsClient || wsClient.ws?.readyState !== WebSocket.OPEN)) {
      fetchLogs()
    }
  }, 10000)  // 降低轮询频率到10秒

  // 响应式调整图表大小
  window.addEventListener('resize', () => {
    if (chart) {
      chart.resize()
    }
  })
})

onUnmounted(() => {
  if (logsInterval) {
    clearInterval(logsInterval)
  }
  if (chart) {
    chart.dispose()
  }
  if (wsClient) {
    wsClient.disconnect()
  }
  window.removeEventListener('resize', () => {
    if (chart) {
      chart.resize()
    }
  })
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.text-error {
  color: #f56c6c;
}

.message-content {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
