<template>
  <div class="realtime-logs-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>
        <el-icon><Document /></el-icon>
        实时转发日志
      </h1>
      
      <div class="header-actions">
        <el-tag :type="wsConnected ? 'success' : 'danger'">
          {{ wsConnected ? '🟢 实时同步' : '🔴 已断开' }}
        </el-tag>
        
        <el-button-group>
          <el-button 
            :icon="Refresh" 
            @click="refreshLogs"
            :loading="loading"
          >
            刷新
          </el-button>
          
          <el-button 
            :icon="Download" 
            @click="exportLogs"
          >
            导出
          </el-button>
          
          <el-button 
            :icon="Delete" 
            type="danger"
            @click="clearLogs"
          >
            清空
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 过滤器 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="全部" value="" />
            <el-option label="成功" value="success">
              <el-tag type="success" size="small">成功</el-tag>
            </el-option>
            <el-option label="失败" value="failed">
              <el-tag type="danger" size="small">失败</el-tag>
            </el-option>
            <el-option label="队列中" value="pending">
              <el-tag type="warning" size="small">队列中</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="平台">
          <el-select v-model="filterForm.platform" placeholder="全部平台" clearable>
            <el-option label="全部" value="" />
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索消息内容..."
            :prefix-icon="Search"
            clearable
            style="width: 300px;"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilter">
            应用过滤
          </el-button>
          <el-button @click="resetFilter">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 统计信息 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总消息数" :value="stats.total">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="成功" :value="stats.success">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
            <template #suffix>
              <el-text type="success">{{ successRate }}%</el-text>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="失败" :value="stats.failed">
            <template #prefix>
              <el-icon color="#F56C6C"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="平均延迟" :value="stats.avgLatency" suffix="ms">
            <template #prefix>
              <el-icon color="#E6A23C"><Timer /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 日志列表 -->
    <el-card class="logs-card">
      <div class="logs-header">
        <span>日志列表（共 {{ filteredLogs.length }} 条）</span>
        
        <el-switch
          v-model="autoScroll"
          active-text="自动滚动"
          inactive-text="手动控制"
        />
      </div>
      
      <div 
        ref="logsContainer" 
        class="logs-container"
        v-loading="loading"
      >
        <el-empty 
          v-if="filteredLogs.length === 0 && !loading"
          description="暂无日志数据"
        />
        
        <el-timeline v-else>
          <el-timeline-item
            v-for="log in filteredLogs"
            :key="log.id"
            :timestamp="formatTime(log.timestamp)"
            :type="getLogType(log.status)"
            :icon="getLogIcon(log.status)"
            :color="getLogColor(log.status)"
          >
            <el-card class="log-item" shadow="hover">
              <div class="log-header">
                <el-space>
                  <el-tag :type="getLogTagType(log.status)" size="small">
                    {{ getStatusLabel(log.status) }}
                  </el-tag>
                  
                  <el-tag type="info" size="small">
                    {{ log.platform }}
                  </el-tag>
                  
                  <el-text type="info" size="small">
                    延迟: {{ log.latency }}ms
                  </el-text>
                </el-space>
                
                <el-button-group size="small">
                  <el-button :icon="View" @click="viewDetails(log)">
                    详情
                  </el-button>
                  
                  <el-button 
                    v-if="log.status === 'failed'"
                    :icon="Refresh"
                    type="warning"
                    @click="retryLog(log)"
                  >
                    重试
                  </el-button>
                </el-button-group>
              </div>
              
              <div class="log-content">
                <div class="log-route">
                  <el-text size="small">
                    <el-icon><OfficeBuilding /></el-icon>
                    {{ log.source_server }}
                  </el-text>
                  <el-icon><Right /></el-icon>
                  <el-text size="small">
                    <el-icon><ChatDotRound /></el-icon>
                    #{{ log.source_channel }}
                  </el-text>
                  <el-icon><Right /></el-icon>
                  <el-text size="small">
                    <el-icon><Connection /></el-icon>
                    {{ log.target_bot }}
                  </el-text>
                </div>
                
                <div class="log-message">
                  <el-text v-if="log.message_type === 'text'">
                    📝 {{ truncateText(log.content, 100) }}
                  </el-text>
                  <el-text v-else-if="log.message_type === 'image'">
                    🖼️ [图片消息]
                  </el-text>
                  <el-text v-else>
                    📎 [{{ log.message_type }}]
                  </el-text>
                </div>
                
                <div v-if="log.error_message" class="log-error">
                  <el-alert
                    :title="log.error_message"
                    type="error"
                    :closable="false"
                    show-icon
                  />
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
    
    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="消息详情"
      width="800px"
    >
      <el-descriptions v-if="currentLog" :column="2" border>
        <el-descriptions-item label="消息ID">
          {{ currentLog.message_id }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getLogTagType(currentLog.status)">
            {{ getStatusLabel(currentLog.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="源服务器">
          {{ currentLog.source_server }}
        </el-descriptions-item>
        <el-descriptions-item label="源频道">
          #{{ currentLog.source_channel }}
        </el-descriptions-item>
        <el-descriptions-item label="目标平台">
          {{ currentLog.platform }}
        </el-descriptions-item>
        <el-descriptions-item label="目标Bot">
          {{ currentLog.target_bot }}
        </el-descriptions-item>
        <el-descriptions-item label="消息类型">
          {{ currentLog.message_type }}
        </el-descriptions-item>
        <el-descriptions-item label="延迟">
          {{ currentLog.latency }}ms
        </el-descriptions-item>
        <el-descriptions-item label="时间戳" :span="2">
          {{ formatFullTime(currentLog.timestamp) }}
        </el-descriptions-item>
        <el-descriptions-item label="消息内容" :span="2">
          <pre class="log-content-pre">{{ currentLog.content }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLog.error_message" label="错误信息" :span="2">
          <el-text type="danger">{{ currentLog.error_message }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Refresh, Download, Delete, Search, Message,
  CircleCheck, CircleClose, Timer, View, Right,
  OfficeBuilding, ChatDotRound, Connection
} from '@element-plus/icons-vue'
import axios from 'axios'

// WebSocket连接
let ws = null
const wsConnected = ref(false)

// 状态
const loading = ref(false)
const logs = ref([])
const autoScroll = ref(true)
const detailDialogVisible = ref(false)
const currentLog = ref(null)
const logsContainer = ref(null)

// 过滤表单
const filterForm = ref({
  status: '',
  platform: '',
  timeRange: null,
  keyword: ''
})

// 统计
const stats = ref({
  total: 0,
  success: 0,
  failed: 0,
  pending: 0,
  avgLatency: 0
})

// 计算属性
const successRate = computed(() => {
  if (stats.value.total === 0) return 0
  return ((stats.value.success / stats.value.total) * 100).toFixed(1)
})

const filteredLogs = computed(() => {
  let result = logs.value
  
  // 状态过滤
  if (filterForm.value.status) {
    result = result.filter(log => log.status === filterForm.value.status)
  }
  
  // 平台过滤
  if (filterForm.value.platform) {
    result = result.filter(log => log.platform === filterForm.value.platform)
  }
  
  // 时间范围过滤
  if (filterForm.value.timeRange && filterForm.value.timeRange.length === 2) {
    const [start, end] = filterForm.value.timeRange
    result = result.filter(log => {
      const logTime = new Date(log.timestamp)
      return logTime >= start && logTime <= end
    })
  }
  
  // 关键词搜索
  if (filterForm.value.keyword) {
    const keyword = filterForm.value.keyword.toLowerCase()
    result = result.filter(log => 
      log.content.toLowerCase().includes(keyword) ||
      log.source_channel.toLowerCase().includes(keyword) ||
      log.target_bot.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 初始化WebSocket
function initWebSocket() {
  const wsUrl = `ws://localhost:9527/ws/logs`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    wsConnected.value = true
    console.log('WebSocket连接成功')
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'log') {
      // 新日志
      logs.value.unshift(data.log)
      
      // 限制日志数量
      if (logs.value.length > 1000) {
        logs.value = logs.value.slice(0, 1000)
      }
      
      // 更新统计
      updateStats()
      
      // 自动滚动
      if (autoScroll.value) {
        scrollToTop()
      }
    } else if (data.type === 'stats') {
      // 统计更新
      stats.value = data.stats
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
    wsConnected.value = false
  }
  
  ws.onclose = () => {
    wsConnected.value = false
    console.log('WebSocket连接断开，5秒后重连...')
    
    // 5秒后重连
    setTimeout(() => {
      initWebSocket()
    }, 5000)
  }
}

// 加载日志
async function refreshLogs() {
  loading.value = true
  
  try {
    const response = await axios.get('/api/logs', {
      params: {
        limit: 1000
      }
    })
    
    logs.value = response.data.logs
    stats.value = response.data.stats
    
    ElMessage.success('日志已刷新')
  } catch (error) {
    ElMessage.error('加载日志失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 更新统计
function updateStats() {
  stats.value.total = logs.value.length
  stats.value.success = logs.value.filter(l => l.status === 'success').length
  stats.value.failed = logs.value.filter(l => l.status === 'failed').length
  stats.value.pending = logs.value.filter(l => l.status === 'pending').length
  
  const latencies = logs.value
    .filter(l => l.latency)
    .map(l => l.latency)
  
  if (latencies.length > 0) {
    stats.value.avgLatency = Math.round(
      latencies.reduce((sum, l) => sum + l, 0) / latencies.length
    )
  }
}

// 应用过滤
function applyFilter() {
  ElMessage.info(`过滤后显示 ${filteredLogs.value.length} 条日志`)
}

// 重置过滤
function resetFilter() {
  filterForm.value = {
    status: '',
    platform: '',
    timeRange: null,
    keyword: ''
  }
  ElMessage.success('过滤条件已重置')
}

// 导出日志
function exportLogs() {
  const data = filteredLogs.value.map(log => ({
    时间: formatFullTime(log.timestamp),
    状态: getStatusLabel(log.status),
    源服务器: log.source_server,
    源频道: log.source_channel,
    目标平台: log.platform,
    目标Bot: log.target_bot,
    消息类型: log.message_type,
    延迟: `${log.latency}ms`,
    内容: log.content,
    错误: log.error_message || ''
  }))
  
  // 转换为CSV
  const csv = convertToCSV(data)
  
  // 下载
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs-${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success(`已导出 ${data.length} 条日志`)
}

// 转换为CSV
function convertToCSV(data) {
  if (data.length === 0) return ''
  
  const header = Object.keys(data[0]).join(',')
  const rows = data.map(row => 
    Object.values(row).map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')
  )
  
  return [header, ...rows].join('\n')
}

// 清空日志
function clearLogs() {
  ElMessageBox.confirm(
    '确定要清空所有日志吗？此操作不可恢复。',
    '清空日志',
    {
      confirmButtonText: '清空',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete('/api/logs')
      logs.value = []
      updateStats()
      ElMessage.success('日志已清空')
    } catch (error) {
      ElMessage.error('清空失败: ' + error.message)
    }
  }).catch(() => {})
}

// 查看详情
function viewDetails(log) {
  currentLog.value = log
  detailDialogVisible.value = true
}

// 重试
async function retryLog(log) {
  try {
    const response = await axios.post(`/api/logs/${log.id}/retry`)
    
    if (response.data.success) {
      ElMessage.success('重试成功')
      await refreshLogs()
    } else {
      ElMessage.error(response.data.message || '重试失败')
    }
  } catch (error) {
    ElMessage.error('重试失败: ' + error.message)
  }
}

// 工具函数
function getLogType(status) {
  const types = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return types[status] || 'info'
}

function getLogIcon(status) {
  const icons = {
    success: CircleCheck,
    failed: CircleClose,
    pending: Timer
  }
  return icons[status] || Message
}

function getLogColor(status) {
  const colors = {
    success: '#67C23A',
    failed: '#F56C6C',
    pending: '#E6A23C'
  }
  return colors[status] || '#909399'
}

function getLogTagType(status) {
  const types = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return types[status] || 'info'
}

function getStatusLabel(status) {
  const labels = {
    success: '成功',
    failed: '失败',
    pending: '队列中'
  }
  return labels[status] || status
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

function formatFullTime(timestamp) {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function truncateText(text, maxLength) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

function scrollToTop() {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTo({ top: 0, behavior: 'smooth' })
    }
  })
}

// 生命周期
onMounted(() => {
  refreshLogs()
  initWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.realtime-logs-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.logs-card {
  height: calc(100vh - 450px);
  min-height: 500px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.logs-container {
  height: calc(100% - 50px);
  overflow-y: auto;
}

.log-item {
  margin: 8px 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-route {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.log-message {
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.log-error {
  margin-top: 8px;
}

.log-content-pre {
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
