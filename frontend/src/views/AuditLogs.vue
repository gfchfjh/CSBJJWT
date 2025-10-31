<template>
  <div class="audit-logs-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔍 审计日志</span>
          <div class="header-actions">
            <el-button @click="refreshLogs" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportLogs">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button type="danger" @click="showCleanDialog = true">
              <el-icon><Delete /></el-icon>
              清理旧日志
            </el-button>
          </div>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic title="总操作数" :value="statistics.total_count || 0">
            <template #prefix>
              <el-icon><DocumentCopy /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="成功操作" :value="statistics.success_count || 0">
            <template #prefix>
              <el-icon style="color: #67C23A;"><SuccessFilled /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="失败操作" :value="statistics.failed_count || 0">
            <template #prefix>
              <el-icon style="color: #F56C6C;"><CircleCloseFilled /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="成功率" 
            :value="successRate" 
            suffix="%"
            :precision="1"
          >
            <template #prefix>
              <el-icon style="color: #409EFF;"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider />

      <!-- 筛选器 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="操作类型">
          <el-select v-model="filters.action" placeholder="全部操作" clearable style="width: 200px;">
            <el-option
              v-for="action in availableActions"
              :key="action.value"
              :label="action.label"
              :value="action.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="严重级别">
          <el-select v-model="filters.level" placeholder="全部级别" clearable style="width: 150px;">
            <el-option
              v-for="level in availableLevels"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.success_only" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="仅成功" :value="true" />
            <el-option label="仅失败" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="applyFilters">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 日志表格 -->
      <el-table
        :data="logs"
        v-loading="loading"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="timestamp" label="时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="username" label="用户" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.username" size="small">{{ row.username }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="action" label="操作" width="150">
          <template #default="{ row }">
            {{ getActionLabel(row.action) }}
          </template>
        </el-table-column>

        <el-table-column prop="resource_type" label="资源" width="120">
          <template #default="{ row }">
            <span v-if="row.resource_type">{{ row.resource_type }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ getLevelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="success" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="ip_address" label="IP地址" width="140" />

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetails(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsDialogVisible"
      title="审计日志详情"
      width="60%"
    >
      <el-descriptions :column="2" border v-if="selectedLog">
        <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatTime(selectedLog.timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ selectedLog.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ selectedLog.user_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作">{{ getActionLabel(selectedLog.action) }}</el-descriptions-item>
        <el-descriptions-item label="严重级别">
          <el-tag :type="getLevelType(selectedLog.level)">
            {{ getLevelLabel(selectedLog.level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ selectedLog.resource_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ selectedLog.resource_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="selectedLog.success ? 'success' : 'danger'">
            {{ selectedLog.success ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ selectedLog.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="User Agent" :span="2">
          {{ selectedLog.user_agent || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="selectedLog.error_message">
          <el-alert type="error" :closable="false" show-icon>
            {{ selectedLog.error_message }}
          </el-alert>
        </el-descriptions-item>
        <el-descriptions-item label="详细信息" :span="2" v-if="selectedLog.details">
          <pre style="background: #f5f7fa; padding: 10px; border-radius: 4px; overflow-x: auto;">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 清理对话框 -->
    <el-dialog
      v-model="showCleanDialog"
      title="清理旧日志"
      width="400px"
    >
      <el-form label-width="120px">
        <el-form-item label="保留天数">
          <el-input-number
            v-model="cleanDays"
            :min="7"
            :max="365"
            :step="1"
          />
          <div class="form-item-tip">清理指定天数之前的日志（最少保留7天）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCleanDialog = false">取消</el-button>
        <el-button type="danger" @click="cleanOldLogs">
          确认清理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Download, Delete, Search, RefreshLeft, View,
  DocumentCopy, SuccessFilled, CircleCloseFilled, TrendCharts
} from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = 'http://localhost:9527'

// 数据
const logs = ref([])
const statistics = ref({})
const availableActions = ref([])
const availableLevels = ref([])
const loading = ref(false)
const detailsDialogVisible = ref(false)
const selectedLog = ref(null)
const showCleanDialog = ref(false)
const cleanDays = ref(90)

// 筛选器
const filters = ref({
  action: null,
  level: null,
  success_only: null,
  start_date: null,
  end_date: null
})

const dateRange = ref(null)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 计算成功率
const successRate = computed(() => {
  const total = statistics.value.total_count || 0
  const success = statistics.value.success_count || 0
  return total > 0 ? (success / total * 100) : 0
})

// 方法
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getActionLabel = (action) => {
  const found = availableActions.value.find(a => a.value === action)
  return found ? found.label : action
}

const getLevelLabel = (level) => {
  const found = availableLevels.value.find(l => l.value === level)
  return found ? found.label : level
}

const getLevelType = (level) => {
  const map = {
    'info': 'primary',
    'warning': 'warning',
    'error': 'danger',
    'critical': 'danger'
  }
  return map[level] || 'info'
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      ...filters.value
    }

    const response = await axios.get(`${API_BASE}/api/audit-logs/`, { params })
    
    if (response.data.success) {
      logs.value = response.data.data.logs
      pagination.value.total = response.data.data.total
    }
  } catch (error) {
    ElMessage.error('加载审计日志失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/audit-logs/statistics`, {
      params: { days: 30 }
    })
    
    if (response.data.success) {
      statistics.value = response.data.data
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadActions = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/audit-logs/actions`)
    if (response.data.success) {
      availableActions.value = response.data.data.actions
    }
  } catch (error) {
    console.error('加载操作类型失败:', error)
  }
}

const loadLevels = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/audit-logs/levels`)
    if (response.data.success) {
      availableLevels.value = response.data.data.levels
    }
  } catch (error) {
    console.error('加载严重级别失败:', error)
  }
}

const refreshLogs = () => {
  loadLogs()
  loadStatistics()
}

const applyFilters = () => {
  pagination.value.page = 1
  loadLogs()
}

const resetFilters = () => {
  filters.value = {
    action: null,
    level: null,
    success_only: null,
    start_date: null,
    end_date: null
  }
  dateRange.value = null
  applyFilters()
}

const handleDateChange = (dates) => {
  if (dates && dates.length === 2) {
    filters.value.start_date = dates[0]
    filters.value.end_date = dates[1]
  } else {
    filters.value.start_date = null
    filters.value.end_date = null
  }
}

const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  loadLogs()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadLogs()
}

const handleSortChange = ({ prop, order }) => {
  // 实现排序逻辑
  loadLogs()
}

const showDetails = (log) => {
  selectedLog.value = log
  detailsDialogVisible.value = true
}

const exportLogs = async () => {
  try {
    const params = new URLSearchParams({
      format: 'csv',
      ...filters.value
    })
    
    window.open(`${API_BASE}/api/audit-logs/export?${params.toString()}`, '_blank')
    ElMessage.success('导出任务已启动')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

const cleanOldLogs = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${cleanDays.value} 天前的审计日志吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await axios.post(`${API_BASE}/api/audit-logs/clean`, null, {
      params: { days: cleanDays.value }
    })

    if (response.data.success) {
      ElMessage.success(response.data.data.message)
      showCleanDialog.value = false
      refreshLogs()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败: ' + error.message)
    }
  }
}

// 初始化
onMounted(() => {
  loadActions()
  loadLevels()
  loadLogs()
  loadStatistics()
})
</script>

<style scoped>
.audit-logs-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.text-muted {
  color: #909399;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

:deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
}
</style>
