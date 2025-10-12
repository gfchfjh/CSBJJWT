<template>
  <div class="logs-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📋 实时转发日志</span>
          <div>
            <el-button size="small" @click="fetchLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="logs" border style="width: 100%" max-height="600">
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column prop="sender_name" label="发送者" width="120" />
        <el-table-column prop="content" label="内容" width="300">
          <template #default="{ row }">
            {{ row.content.substring(0, 50) }}{{ row.content.length > 50 ? '...' : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="target_platform" label="目标平台" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.target_platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latency_ms" label="延迟(ms)" width="100" />
        <el-table-column prop="error_message" label="错误信息" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../api'

const logs = ref([])

const fetchLogs = async () => {
  try {
    logs.value = await api.getLogs(100)
  } catch (error) {
    console.error('获取日志失败:', error)
  }
}

let logsInterval = null

onMounted(() => {
  fetchLogs()
  logsInterval = setInterval(fetchLogs, 5000)
})

onUnmounted(() => {
  if (logsInterval) {
    clearInterval(logsInterval)
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
