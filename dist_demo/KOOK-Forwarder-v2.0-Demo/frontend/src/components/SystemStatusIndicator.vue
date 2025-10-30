<template>
  <div class="system-status-indicator">
    <!-- 主状态按钮 -->
    <el-badge :value="offlineCount" :hidden="offlineCount === 0" :max="9">
      <el-button
        :type="statusType"
        :icon="StatusIcon"
        @click="showDetail = true"
        class="status-button"
      >
        <span class="status-text">{{ statusText }}</span>
      </el-button>
    </el-badge>

    <!-- 详细状态对话框 -->
    <el-dialog
      v-model="showDetail"
      title="系统状态详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <!-- 总体状态 -->
      <div class="overall-status">
        <el-alert
          :title="overallStatusTitle"
          :type="statusType"
          :description="overallStatusDesc"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 账号状态 -->
      <el-divider content-position="left">
        <el-icon><User /></el-icon>
        KOOK账号连接状态
      </el-divider>
      
      <el-table :data="accounts" stripe>
        <el-table-column label="账号" prop="email" min-width="200" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getAccountStatusType(row.status)"
              :icon="getAccountStatusIcon(row.status)"
            >
              {{ getAccountStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后活跃" width="160">
          <template #default="{ row }">
            {{ formatTime(row.last_active) }}
          </template>
        </el-table-column>
        <el-table-column label="重连次数" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.reconnect_count > 0" type="warning" size="small">
              {{ row.reconnect_count }}次
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="200">
          <template #default="{ row }">
            <el-text v-if="row.error_message" type="danger" size="small">
              {{ row.error_message }}
            </el-text>
            <span v-else class="text-muted">正常</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'offline'"
              type="primary"
              size="small"
              @click="reconnectAccount(row.id)"
            >
              重连
            </el-button>
            <el-button
              v-else-if="row.status === 'reconnecting'"
              size="small"
              disabled
            >
              重连中...
            </el-button>
            <el-text v-else type="success" size="small">运行正常</el-text>
          </template>
        </el-table-column>
      </el-table>

      <!-- 服务状态 -->
      <el-divider content-position="left">
        <el-icon><Service /></el-icon>
        后端服务状态
      </el-divider>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="service-header">
                <el-icon><Monitor /></el-icon>
                <span>后端API</span>
              </div>
            </template>
            <div class="service-content">
              <el-tag type="success" size="large">运行中</el-tag>
              <div class="service-info">
                <p>端口: 9527</p>
                <p>版本: v8.0.0</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="service-header">
                <el-icon><DataLine /></el-icon>
                <span>Redis</span>
              </div>
            </template>
            <div class="service-content">
              <el-tag
                :type="services.redis?.status === 'online' ? 'success' : 'danger'"
                size="large"
              >
                {{ services.redis?.status === 'online' ? '运行中' : '已停止' }}
              </el-tag>
              <div v-if="services.redis?.status === 'online'" class="service-info">
                <p>版本: {{ services.redis.version }}</p>
                <p>内存: {{ services.redis.memory_used }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="service-header">
                <el-icon><List /></el-icon>
                <span>消息队列</span>
              </div>
            </template>
            <div class="service-content">
              <el-tag
                :type="getQueueStatusType(services.queue?.status)"
                size="large"
              >
                {{ getQueueStatusLabel(services.queue?.status) }}
              </el-tag>
              <div class="service-info">
                <p>待处理: {{ services.queue?.size || 0 }} 条</p>
                <p>处理中: {{ services.queue?.processing || 0 }} 条</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 实时统计 -->
      <el-divider content-position="left">
        <el-icon><DataAnalysis /></el-icon>
        实时统计
      </el-divider>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="今日转发" :value="statistics.today?.total_messages || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="成功率"
            :value="statistics.today?.success_rate || 0"
            suffix="%"
            :precision="1"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="平均延迟"
            :value="statistics.today?.avg_latency || 0"
            suffix="ms"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="每分钟消息数"
            :value="statistics.realtime?.messages_per_minute || 0"
          />
        </el-col>
      </el-row>

      <template #footer>
        <el-button @click="refreshStatus">
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>
        <el-button type="primary" @click="showDetail = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User, Service, Monitor, DataLine, List, DataAnalysis, Refresh,
  SuccessFilled, Loading, WarningFilled, CircleClose
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const showDetail = ref(false)
const accounts = ref([])
const services = ref({})
const statistics = ref({})
let ws = null

// 状态计算
const onlineCount = computed(() => {
  return accounts.value.filter(a => a.status === 'online').length
})

const offlineCount = computed(() => {
  return accounts.value.filter(a => a.status === 'offline').length
})

const reconnectingCount = computed(() => {
  return accounts.value.filter(a => a.status === 'reconnecting').length
})

const statusType = computed(() => {
  if (offlineCount.value > 0) return 'danger'
  if (reconnectingCount.value > 0) return 'warning'
  return 'success'
})

const StatusIcon = computed(() => {
  if (offlineCount.value > 0) return CircleClose
  if (reconnectingCount.value > 0) return Loading
  return SuccessFilled
})

const statusText = computed(() => {
  const total = accounts.value.length
  if (total === 0) return '未配置'
  return `${onlineCount.value}/${total} 在线`
})

const overallStatusTitle = computed(() => {
  if (offlineCount.value > 0) {
    return `⚠️ ${offlineCount.value} 个账号离线`
  }
  if (reconnectingCount.value > 0) {
    return `🔄 ${reconnectingCount.value} 个账号重连中`
  }
  return '✅ 所有账号运行正常'
})

const overallStatusDesc = computed(() => {
  if (offlineCount.value > 0) {
    return '部分账号连接失败，请检查网络或Cookie是否过期'
  }
  if (reconnectingCount.value > 0) {
    return '系统正在尝试重新连接，请稍候...'
  }
  return '所有KOOK账号已连接，消息转发服务运行正常'
})

// WebSocket连接
const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.hostname}:9527/api/ws/system-status`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('✅ WebSocket连接已建立')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'status_update') {
        accounts.value = data.accounts || []
        services.value = data.services || {}
        statistics.value = data.statistics || {}
      } else if (data.type === 'account_status_change') {
        // 账号状态变化
        const account = accounts.value.find(a => a.id === data.account_id)
        if (account) {
          account.status = data.status
          account.error_message = data.message || ''
        }
      } else if (data.type === 'notification') {
        // 系统通知
        ElMessage({
          message: data.message,
          type: data.notification_type,
          duration: 5000
        })
      }
    } catch (error) {
      console.error('WebSocket消息解析失败:', error)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
  }
  
  ws.onclose = () => {
    console.log('❌ WebSocket连接已关闭，5秒后重连...')
    setTimeout(() => {
      if (!ws || ws.readyState === WebSocket.CLOSED) {
        connectWebSocket()
      }
    }, 5000)
  }
}

const disconnectWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

// 辅助函数
const getAccountStatusType = (status) => {
  const types = {
    'online': 'success',
    'offline': 'danger',
    'reconnecting': 'warning'
  }
  return types[status] || 'info'
}

const getAccountStatusIcon = (status) => {
  const icons = {
    'online': SuccessFilled,
    'offline': CircleClose,
    'reconnecting': Loading
  }
  return icons[status] || null
}

const getAccountStatusLabel = (status) => {
  const labels = {
    'online': '在线',
    'offline': '离线',
    'reconnecting': '重连中'
  }
  return labels[status] || '未知'
}

const getQueueStatusType = (status) => {
  const types = {
    'normal': 'success',
    'high_load': 'warning',
    'unknown': 'info'
  }
  return types[status] || 'info'
}

const getQueueStatusLabel = (status) => {
  const labels = {
    'normal': '正常',
    'high_load': '负载高',
    'unknown': '未知'
  }
  return labels[status] || '未知'
}

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).fromNow()
}

// 操作
const reconnectAccount = (accountId) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'reconnect_account',
      account_id: accountId
    }))
    
    ElMessage.info('已发送重连请求...')
  }
}

const refreshStatus = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'get_status'
    }))
  }
}

// 生命周期
onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<style scoped lang="scss">
.system-status-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.status-button {
  .status-text {
    margin-left: 5px;
  }
}

.overall-status {
  margin-bottom: 20px;
}

.service-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.service-content {
  text-align: center;
  
  .service-info {
    margin-top: 15px;
    text-align: left;
    
    p {
      margin: 5px 0;
      font-size: 14px;
      color: #606266;
    }
  }
}

.text-muted {
  color: #909399;
  font-size: 12px;
}
</style>
