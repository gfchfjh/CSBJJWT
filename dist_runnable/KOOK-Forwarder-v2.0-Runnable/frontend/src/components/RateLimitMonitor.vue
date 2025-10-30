<template>
  <div class="rate-limit-monitor">
    <h3>
      <el-icon><Timer /></el-icon>
      限流监控
    </h3>
    
    <el-row :gutter="20">
      <!-- Discord -->
      <el-col :span="8">
        <el-card shadow="hover" class="platform-card discord">
          <template #header>
            <div class="card-header">
              <img src="@/assets/platforms/discord.svg" alt="Discord" class="platform-icon" />
              <span class="platform-name">Discord</span>
              <el-tag :type="getStatusType(discord.status)" size="small">
                {{ getStatusLabel(discord.status) }}
              </el-tag>
            </div>
          </template>
          
          <div class="rate-info">
            <el-statistic title="当前速率" :value="discord.current_rate" suffix="条/5秒" />
            <el-divider />
            <div class="capacity-info">
              <span class="label">容量使用</span>
              <el-progress
                :percentage="discord.usage"
                :status="discord.usage > 80 ? 'exception' : 'success'"
                :stroke-width="8"
              />
            </div>
            
            <transition name="el-fade-in">
              <div v-if="discord.queue > 0" class="queue-alert">
                <el-alert
                  type="warning"
                  :closable="false"
                  :title="`⏳ 队列中: ${discord.queue} 条消息等待发送`"
                />
              </div>
            </transition>
          </div>
        </el-card>
      </el-col>
      
      <!-- Telegram -->
      <el-col :span="8">
        <el-card shadow="hover" class="platform-card telegram">
          <template #header>
            <div class="card-header">
              <img src="@/assets/platforms/telegram.svg" alt="Telegram" class="platform-icon" />
              <span class="platform-name">Telegram</span>
              <el-tag :type="getStatusType(telegram.status)" size="small">
                {{ getStatusLabel(telegram.status) }}
              </el-tag>
            </div>
          </template>
          
          <div class="rate-info">
            <el-statistic title="当前速率" :value="telegram.current_rate" suffix="条/秒" />
            <el-divider />
            <div class="capacity-info">
              <span class="label">容量使用</span>
              <el-progress
                :percentage="telegram.usage"
                :status="telegram.usage > 80 ? 'exception' : 'success'"
                :stroke-width="8"
              />
            </div>
            
            <transition name="el-fade-in">
              <div v-if="telegram.queue > 0" class="queue-alert">
                <el-alert
                  type="warning"
                  :closable="false"
                  :title="`⏳ 队列中: ${telegram.queue} 条消息等待发送`"
                />
              </div>
            </transition>
          </div>
        </el-card>
      </el-col>
      
      <!-- 飞书 -->
      <el-col :span="8">
        <el-card shadow="hover" class="platform-card feishu">
          <template #header>
            <div class="card-header">
              <img src="@/assets/platforms/feishu.svg" alt="飞书" class="platform-icon" />
              <span class="platform-name">飞书</span>
              <el-tag :type="getStatusType(feishu.status)" size="small">
                {{ getStatusLabel(feishu.status) }}
              </el-tag>
            </div>
          </template>
          
          <div class="rate-info">
            <el-statistic title="当前速率" :value="feishu.current_rate" suffix="条/秒" />
            <el-divider />
            <div class="capacity-info">
              <span class="label">容量使用</span>
              <el-progress
                :percentage="feishu.usage"
                :status="feishu.usage > 80 ? 'exception' : 'success'"
                :stroke-width="8"
              />
            </div>
            
            <transition name="el-fade-in">
              <div v-if="feishu.queue > 0" class="queue-alert">
                <el-alert
                  type="warning"
                  :closable="false"
                  :title="`⏳ 队列中: ${feishu.queue} 条消息等待发送`"
                />
              </div>
            </transition>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 总队列状态 -->
    <transition name="el-zoom-in-top">
      <el-card v-if="totalQueue > 0" class="total-queue-card" shadow="always">
        <div class="total-queue-header">
          <el-icon :size="24"><Clock /></el-icon>
          <h4>消息队列总览</h4>
        </div>
        
        <el-descriptions :column="4" border>
          <el-descriptions-item label="总队列">
            <el-tag type="warning" size="large">{{ totalQueue }} 条</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="正在发送">
            <el-tag type="primary" size="large">{{ sending }} 条</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预计等待">
            <el-tag type="info" size="large">{{ estimatedWait }} 秒</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作">
            <el-button type="primary" size="small" @click="showQueueDetail = true">
              查看详情
            </el-button>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </transition>
    
    <!-- 队列详情对话框 -->
    <el-dialog v-model="showQueueDetail" title="队列详情" width="70%">
      <el-table :data="queueMessages" stripe max-height="400">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="目标平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformType(row.platform)">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="频道" prop="channel" min-width="150" />
        <el-table-column label="内容" prop="content" min-width="200" show-overflow-tooltip />
        <el-table-column label="预计发送" width="120">
          <template #default="{ row }">
            {{ formatEta(row.eta) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'queued' ? 'warning' : 'primary'" size="small">
              {{ row.status === 'queued' ? '队列中' : '发送中' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Timer, Clock } from '@element-plus/icons-vue'
import api from '@/api'

const discord = ref({
  current_rate: 0,
  capacity: 5,
  usage: 0,
  queue: 0,
  status: 'normal'
})

const telegram = ref({
  current_rate: 0,
  capacity: 30,
  usage: 0,
  queue: 0,
  status: 'normal'
})

const feishu = ref({
  current_rate: 0,
  capacity: 20,
  usage: 0,
  queue: 0,
  status: 'normal'
})

const totalQueue = computed(() => {
  return discord.value.queue + telegram.value.queue + feishu.value.queue
})

const sending = ref(0)
const estimatedWait = ref(0)
const showQueueDetail = ref(false)
const queueMessages = ref([])

let intervalId = null

const fetchRateLimitStatus = async () => {
  try {
    const response = await api.get('/api/rate-limit/status')
    const data = response.data
    
    discord.value = {
      current_rate: data.discord.rate || 0,
      capacity: data.discord.capacity || 5,
      usage: data.discord.usage || 0,
      queue: data.discord.queue || 0,
      status: data.discord.status || 'normal'
    }
    
    telegram.value = {
      current_rate: data.telegram.rate || 0,
      capacity: data.telegram.capacity || 30,
      usage: data.telegram.usage || 0,
      queue: data.telegram.queue || 0,
      status: data.telegram.status || 'normal'
    }
    
    feishu.value = {
      current_rate: data.feishu.rate || 0,
      capacity: data.feishu.capacity || 20,
      usage: data.feishu.usage || 0,
      queue: data.feishu.queue || 0,
      status: data.feishu.status || 'normal'
    }
    
    sending.value = data.sending || 0
    estimatedWait.value = data.estimated_wait || 0
    
  } catch (error) {
    console.error('获取限流状态失败:', error)
  }
}

const getStatusType = (status) => {
  const types = {
    'normal': 'success',
    'warning': 'warning',
    'high_load': 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'normal': '正常',
    'warning': '警告',
    'high_load': '高负载'
  }
  return labels[status] || '未知'
}

const getPlatformType = (platform) => {
  const types = {
    'discord': 'primary',
    'telegram': 'success',
    'feishu': 'warning'
  }
  return types[platform.toLowerCase()] || 'info'
}

const formatEta = (seconds) => {
  if (seconds < 60) {
    return `${seconds}秒后`
  } else {
    const minutes = Math.floor(seconds / 60)
    return `${minutes}分钟后`
  }
}

onMounted(() => {
  fetchRateLimitStatus()
  // 每2秒更新一次
  intervalId = setInterval(fetchRateLimitStatus, 2000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped lang="scss">
.rate-limit-monitor {
  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: bold;
  }
}

.platform-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .platform-icon {
      width: 24px;
      height: 24px;
    }
    
    .platform-name {
      flex: 1;
      font-weight: bold;
    }
  }
}

.rate-info {
  .capacity-info {
    .label {
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      color: #606266;
    }
  }
  
  .queue-alert {
    margin-top: 15px;
  }
}

.total-queue-card {
  margin-top: 20px;
  
  .total-queue-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
    
    h4 {
      margin: 0;
      font-size: 16px;
    }
  }
}
</style>
