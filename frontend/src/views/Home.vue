<template>
  <div class="home-view">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409EFF"><Message /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total || 0 }}</div>
              <div class="stat-label">今日转发</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.success_rate || 0 }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#E6A23C"><Timer /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avg_latency || 0 }}ms</div>
              <div class="stat-label">平均延迟</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#F56C6C"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ systemStore.status.queue_size || 0 }}</div>
              <div class="stat-label">队列消息</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- ✅ P1-1新增：服务控制卡片 -->
    <el-card class="service-control-card" style="margin-top: 20px">
      <template #header>
        <span>🎮 服务控制</span>
      </template>
      
      <div class="service-status">
        <el-tag 
          :type="systemStore.status.service_running ? 'success' : 'danger'"
          size="large"
          effect="dark"
        >
          {{ systemStore.status.service_running ? '🟢 运行中' : '🔴 已停止' }}
        </el-tag>
        
        <span class="uptime" v-if="systemStore.status.service_running">
          运行时长: {{ formatUptime(systemStore.status.uptime) }}
        </span>
      </div>

      <div class="control-buttons">
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
          <el-icon><RefreshRight /></el-icon>
          重启服务
        </el-button>
        
        <el-button 
          size="large"
          @click="showServiceLog"
        >
          <el-icon><View /></el-icon>
          查看日志
        </el-button>
      </div>

      <div class="service-info">
        <el-descriptions :column="2" size="small" border>
          <el-descriptions-item label="活跃账号">
            {{ systemStore.status.active_accounts || 0 }} 个
          </el-descriptions-item>
          <el-descriptions-item label="配置的Bot">
            {{ systemStore.status.configured_bots || 0 }} 个
          </el-descriptions-item>
          <el-descriptions-item label="频道映射">
            {{ systemStore.status.active_mappings || 0 }} 个
          </el-descriptions-item>
          <el-descriptions-item label="队列消息">
            {{ systemStore.status.queue_size || 0 }} 条
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 快捷操作 -->
    <el-card class="actions-card" style="margin-top: 20px">
      <template #header>
        <span>⚡ 快捷操作</span>
      </template>
      
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/accounts')">
          <el-icon><User /></el-icon>
          管理账号
        </el-button>
        
        <el-button type="success" @click="$router.push('/bots')">
          <el-icon><Robot /></el-icon>
          配置机器人
        </el-button>
        
        <el-button type="warning" @click="$router.push('/mapping')">
          <el-icon><Connection /></el-icon>
          设置映射
        </el-button>
        
        <el-button type="info" @click="$router.push('/logs')">
          <el-icon><Document /></el-icon>
          查看日志
        </el-button>
      </div>
    </el-card>
    
    <!-- 系统状态 -->
    <el-card class="status-card" style="margin-top: 20px">
      <template #header>
        <span>📊 系统状态</span>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="服务状态">
          <el-tag :type="systemStore.status.service_running ? 'success' : 'danger'">
            {{ systemStore.status.service_running ? '运行中' : '已停止' }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="Redis连接">
          <el-tag :type="systemStore.status.redis_connected ? 'success' : 'danger'">
            {{ systemStore.status.redis_connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="活跃抓取器">
          {{ systemStore.status.active_scrapers }} 个
        </el-descriptions-item>
        
        <el-descriptions-item label="队列大小">
          {{ systemStore.status.queue_size }} 条消息
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 数据可视化图表 -->
    <div style="margin-top: 20px">
      <Charts />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../store/system'
import api from '../api'
import Charts from '../components/Charts.vue'

const systemStore = useSystemStore()

const stats = ref({
  total: 0,
  success: 0,
  failed: 0,
  success_rate: 0,
  avg_latency: 0
})

const fetchStats = async () => {
  try {
    const data = await api.getStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

let statsInterval = null

onMounted(() => {
  fetchStats()
  statsInterval = setInterval(fetchStats, 10000)
})

onUnmounted(() => {
  if (statsInterval) {
    clearInterval(statsInterval)
  }
})
</script>

<style scoped>
.home-view {
  height: 100%;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
