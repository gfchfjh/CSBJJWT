<template>
  <div class="logs-enhanced">
    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <!-- 搜索框 -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索消息内容..."
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @input="handleSearch"
        />
        
        <!-- 筛选器 -->
        <el-select v-model="filterStatus" placeholder="状态" style="width: 120px" @change="handleFilter">
          <el-option label="全部状态" value="all" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="处理中" value="pending" />
        </el-select>
        
        <el-select v-model="filterPlatform" placeholder="平台" style="width: 140px" @change="handleFilter">
          <el-option label="全部平台" value="all" />
          <el-option label="Discord" value="discord" />
          <el-option label="Telegram" value="telegram" />
          <el-option label="飞书" value="feishu" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          @change="handleFilter"
          style="width: 360px"
        />
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button :icon="Download" @click="exportLogs">导出日志</el-button>
          <el-button type="warning" :icon="RefreshRight" @click="retryAllFailed">
            重试所有失败
          </el-button>
          <el-button :icon="Refresh" @click="loadLogs">刷新</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#409EFF"><Message /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statsComputed.total }}</div>
              <div class="stat-label">总消息数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statsComputed.success }}</div>
              <div class="stat-label">成功 ({{ statsComputed.successRate }}%)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#F56C6C"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statsComputed.failed }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#E6A23C"><Timer /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statsComputed.avgLatency }}ms</div>
              <div class="stat-label">平均延迟</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 日志列表 -->
    <el-card shadow="never" class="logs-card" v-loading="loading">
      <el-table
        :data="paginatedLogs"
        stripe
        :default-sort="{ prop: 'timestamp', order: 'descending' }"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="消息ID">{{ row.message_id }}</el-descriptions-item>
                <el-descriptions-item label="频道ID">{{ row.channel_id }}</el-descriptions-item>
                <el-descriptions-item label="发送者">{{ row.sender }}</el-descriptions-item>
                <el-descriptions-item label="延迟">{{ row.latency_ms }}ms</el-descriptions-item>
                <el-descriptions-item label="内容" :span="2">
                  <el-text line-clamp="3">{{ row.content }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item v-if="row.error" label="错误信息" :span="2">
                  <el-text type="danger">{{ row.error }}</el-text>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="频道" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.channel_name || row.channel_id }}
          </template>
        </el-table-column>
        
        <el-table-column label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformType(row.platform)" size="small">
              {{ row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="内容" show-overflow-tooltip>
          <template #default="{ row }">
            <el-text truncated>{{ row.content }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column label="延迟" width="100">
          <template #default="{ row }">
            {{ row.latency_ms }}ms
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'failed'"
              type="primary"
              size="small"
              :icon="RefreshRight"
              @click="retryMessage(row.id)"
            >
              重试
            </el-button>
            <el-button
              type="info"
              size="small"
              :icon="View"
              @click="viewDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredLogs.length"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />
    </el-card>
    
    <!-- 导出格式选择对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出日志" width="400px">
      <el-radio-group v-model="exportFormat">
        <el-radio value="csv">CSV格式</el-radio>
        <el-radio value="json">JSON格式</el-radio>
      </el-radio-group>
      
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="performExport">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Download,
  RefreshRight,
  Refresh,
  Message,
  CircleCheck,
  CircleClose,
  Timer,
  View
} from '@element-plus/icons-vue'
import { useWebSocketEnhanced } from '@/composables/useWebSocketEnhanced'
import api from '@/api'

// 状态
const loading = ref(false)
const logs = ref([])
const searchQuery = ref('')
const filterStatus = ref('all')
const filterPlatform = ref('all')
const dateRange = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)

// 导出
const exportDialogVisible = ref(false)
const exportFormat = ref('csv')

// WebSocket
const { subscribe, unsubscribe } = useWebSocketEnhanced()

// 计算属性
const filteredLogs = computed(() => {
  let result = [...logs.value]
  
  // 搜索过滤
  if (searchQuery.value) {
    result = result.filter(log =>
      log.content?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  // 状态过滤
  if (filterStatus.value !== 'all') {
    result = result.filter(log => log.status === filterStatus.value)
  }
  
  // 平台过滤
  if (filterPlatform.value !== 'all') {
    result = result.filter(log => log.platform === filterPlatform.value)
  }
  
  // 日期范围过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(log => {
      const timestamp = new Date(log.timestamp).getTime()
      return timestamp >= start.getTime() && timestamp <= end.getTime()
    })
  }
  
  return result
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

const statsComputed = computed(() => {
  const total = filteredLogs.value.length
  const success = filteredLogs.value.filter(l => l.status === 'success').length
  const failed = filteredLogs.value.filter(l => l.status === 'failed').length
  const latencies = filteredLogs.value
    .filter(l => l.latency_ms)
    .map(l => l.latency_ms)
  const avgLatency = latencies.length > 0
    ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
    : 0
  const successRate = total > 0 ? ((success / total) * 100).toFixed(1) : 0
  
  return { total, success, failed, avgLatency, successRate }
})

// 方法
const loadLogs = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/logs/list', {
      params: {
        limit: 1000
      }
    })
    logs.value = response.data
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const retryMessage = async (logId) => {
  try {
    await api.post(`/api/logs/retry/${logId}`)
    ElMessage.success('重试请求已发送')
    setTimeout(() => loadLogs(), 1000)
  } catch (error) {
    console.error('重试失败:', error)
    ElMessage.error('重试失败: ' + (error.response?.data?.detail || error.message))
  }
}

const retryAllFailed = async () => {
  const failedCount = logs.value.filter(l => l.status === 'failed').length
  
  if (failedCount === 0) {
    ElMessage.info('没有失败的消息')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要重试 ${failedCount} 条失败消息吗？`,
      '批量重试',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.post('/api/logs/retry-all-failed')
    ElMessage.success('批量重试请求已发送')
    setTimeout(() => loadLogs(), 2000)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量重试失败:', error)
      ElMessage.error('批量重试失败')
    }
  }
}

const exportLogs = () => {
  exportDialogVisible.value = true
}

const performExport = () => {
  const data = filteredLogs.value
  
  if (data.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  if (exportFormat.value === 'csv') {
    const csv = [
      ['时间', '状态', '频道', '平台', '内容', '延迟(ms)', '错误信息'],
      ...data.map(log => [
        formatDate(log.timestamp),
        log.status,
        log.channel_name || log.channel_id,
        log.platform,
        log.content?.replace(/,/g, '，') || '',
        log.latency_ms || '',
        log.error?.replace(/,/g, '，') || ''
      ])
    ].map(row => row.join(',')).join('\n')
    
    downloadFile(csv, `logs_${Date.now()}.csv`, 'text/csv')
  } else if (exportFormat.value === 'json') {
    const json = JSON.stringify(data, null, 2)
    downloadFile(json, `logs_${Date.now()}.json`, 'application/json')
  }
  
  exportDialogVisible.value = false
  ElMessage.success('导出成功')
}

const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const viewDetail = (log) => {
  ElMessageBox.alert(
    `<div style="max-height: 400px; overflow-y: auto;">
      <p><strong>消息ID:</strong> ${log.message_id}</p>
      <p><strong>频道:</strong> ${log.channel_name || log.channel_id}</p>
      <p><strong>平台:</strong> ${log.platform}</p>
      <p><strong>状态:</strong> ${log.status}</p>
      <p><strong>内容:</strong> ${log.content || '-'}</p>
      <p><strong>延迟:</strong> ${log.latency_ms}ms</p>
      ${log.error ? `<p><strong>错误:</strong> <span style="color: #F56C6C">${log.error}</span></p>` : ''}
    </div>`,
    '消息详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  )
}

const getStatusType = (status) => {
  const types = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    success: '✅ 成功',
    failed: '❌ 失败',
    pending: '⏳ 处理中'
  }
  return texts[status] || status
}

const getPlatformType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// WebSocket 实时更新
const handleNewLog = (data) => {
  logs.value.unshift(data)
  // 限制内存中的日志数量
  if (logs.value.length > 2000) {
    logs.value = logs.value.slice(0, 2000)
  }
}

onMounted(() => {
  loadLogs()
  subscribe('log', handleNewLog)
})

onUnmounted(() => {
  unsubscribe('log', handleNewLog)
})
</script>

<style scoped>
.logs-enhanced {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.action-buttons {
  margin-left: auto;
  display: flex;
  gap: 10px;
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

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
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
  color: #909399;
}

.logs-card {
  min-height: 400px;
}

.log-detail {
  padding: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
