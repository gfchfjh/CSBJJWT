<template>
  <div class="server-selection-step">
    <h2>📡 步骤2: 选择监听的服务器和频道</h2>
    <p class="step-desc">
      勾选您想要监听的KOOK服务器和频道，系统将自动转发这些频道的消息
    </p>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>正在获取服务器列表...</p>
      <p class="loading-tip">{{ loadingTip }}</p>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    >
      <template #default>
        <el-button type="primary" size="small" @click="refreshServers">
          重新获取
        </el-button>
      </template>
    </el-alert>

    <!-- 服务器列表 -->
    <div v-if="!loading && servers.length > 0" class="servers-container">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button size="small" @click="selectAll">全选</el-button>
        <el-button size="small" @click="selectNone">全不选</el-button>
        <el-button 
          size="small" 
          :icon="RefreshRight" 
          @click="refreshServers"
          :loading="refreshing"
        >
          刷新列表
        </el-button>
        
        <div class="stats">
          已选择: <span class="highlight">{{ selectedServersCount }}</span> 个服务器, 
          <span class="highlight">{{ selectedChannelsCount }}</span> 个频道
        </div>
      </div>

      <!-- 服务器卡片列表 -->
      <div class="server-list">
        <el-card
          v-for="server in servers"
          :key="server.id"
          class="server-card"
          :class="{ 'selected': isServerSelected(server.id) }"
        >
          <!-- 服务器头部 -->
          <template #header>
            <div class="server-header">
              <el-checkbox
                v-model="serverSelections[server.id]"
                @change="toggleServer(server.id)"
                size="large"
              >
                <div class="server-info">
                  <img
                    v-if="server.icon"
                    :src="server.icon"
                    class="server-icon"
                    alt="服务器图标"
                  />
                  <div v-else class="server-icon-placeholder">
                    {{ server.name.charAt(0) }}
                  </div>
                  <div class="server-details">
                    <span class="server-name">{{ server.name }}</span>
                    <span class="server-stats">
                      {{ server.channels?.length || 0 }} 个频道
                      <template v-if="server.member_count">
                        · {{ server.member_count }} 成员
                      </template>
                    </span>
                  </div>
                </div>
              </el-checkbox>
            </div>
          </template>

          <!-- 频道列表 -->
          <div v-if="server.channels && server.channels.length > 0" class="channels-container">
            <div class="channels-header">
              <span>频道列表</span>
              <el-button-group size="small">
                <el-button @click="selectAllChannels(server.id)">全选</el-button>
                <el-button @click="selectNoChannels(server.id)">全不选</el-button>
              </el-button-group>
            </div>

            <el-scrollbar max-height="300px">
              <div class="channel-list">
                <el-checkbox
                  v-for="channel in server.channels"
                  :key="channel.id"
                  v-model="channelSelections[channel.id]"
                  @change="onChannelChange(server.id)"
                  class="channel-item"
                >
                  <el-icon v-if="channel.type === 'text'">
                    <ChatDotSquare />
                  </el-icon>
                  <el-icon v-else>
                    <Microphone />
                  </el-icon>
                  <span class="channel-name">{{ channel.name }}</span>
                  <el-tag
                    v-if="channel.category"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    {{ channel.category }}
                  </el-tag>
                </el-checkbox>
              </div>
            </el-scrollbar>
          </div>

          <!-- 无频道提示 -->
          <el-empty
            v-else
            description="该服务器没有频道"
            :image-size="60"
          />
        </el-card>
      </div>

      <!-- 底部操作按钮 -->
      <div class="footer-actions">
        <el-button @click="$emit('prev')">上一步</el-button>
        <el-button
          type="primary"
          @click="confirmSelection"
          :disabled="selectedChannelsCount === 0"
        >
          下一步 (已选择 {{ selectedChannelsCount }} 个频道)
        </el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && !error && servers.length === 0"
      description="未找到任何服务器"
    >
      <el-button type="primary" @click="refreshServers">重新获取</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Loading, 
  RefreshRight, 
  ChatDotSquare, 
  Microphone 
} from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  accountId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['next', 'prev', 'update:selections'])

// 状态
const loading = ref(false)
const refreshing = ref(false)
const error = ref('')
const loadingTip = ref('正在连接KOOK服务器...')
const servers = ref([])
const serverSelections = reactive({})
const channelSelections = reactive({})

// 计算属性
const selectedServersCount = computed(() => {
  return Object.values(serverSelections).filter(v => v).length
})

const selectedChannelsCount = computed(() => {
  return Object.values(channelSelections).filter(v => v).length
})

// 检查服务器是否被选中
const isServerSelected = (serverId) => {
  return serverSelections[serverId]
}

// 切换服务器选择
const toggleServer = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  if (!server || !server.channels) return

  const isSelected = serverSelections[serverId]

  // 同时选择/取消选择所有频道
  server.channels.forEach(channel => {
    channelSelections[channel.id] = isSelected
  })
}

// 频道选择变化时检查服务器状态
const onChannelChange = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  if (!server || !server.channels) return

  // 检查是否所有频道都被选中
  const allSelected = server.channels.every(ch => channelSelections[ch.id])
  const noneSelected = server.channels.every(ch => !channelSelections[ch.id])

  if (allSelected) {
    serverSelections[serverId] = true
  } else if (noneSelected) {
    serverSelections[serverId] = false
  }
}

// 全选
const selectAll = () => {
  servers.value.forEach(server => {
    serverSelections[server.id] = true
    if (server.channels) {
      server.channels.forEach(channel => {
        channelSelections[channel.id] = true
      })
    }
  })
}

// 全不选
const selectNone = () => {
  Object.keys(serverSelections).forEach(key => {
    serverSelections[key] = false
  })
  Object.keys(channelSelections).forEach(key => {
    channelSelections[key] = false
  })
}

// 选择服务器的所有频道
const selectAllChannels = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  if (!server || !server.channels) return

  server.channels.forEach(channel => {
    channelSelections[channel.id] = true
  })
  serverSelections[serverId] = true
}

// 取消选择服务器的所有频道
const selectNoChannels = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  if (!server || !server.channels) return

  server.channels.forEach(channel => {
    channelSelections[channel.id] = false
  })
  serverSelections[serverId] = false
}

// 获取服务器列表
const fetchServers = async () => {
  loading.value = true
  error.value = ''

  try {
    loadingTip.value = '正在连接KOOK服务器...'
    
    // 先尝试从缓存获取
    const cachedResponse = await axios.get(
      `/api/server-discovery/cached/${props.accountId}`
    )

    if (cachedResponse.data.success && cachedResponse.data.servers.length > 0) {
      servers.value = cachedResponse.data.servers
      initializeSelections()
      loadingTip.value = '从缓存加载成功'
      loading.value = false

      // 后台刷新数据
      refreshInBackground()
      return
    }

    // 没有缓存，从KOOK实时获取
    loadingTip.value = '正在从KOOK获取服务器列表，请稍候...'
    
    const response = await axios.post(
      `/api/server-discovery/fetch/${props.accountId}`
    )

    if (response.data.success) {
      servers.value = response.data.servers
      initializeSelections()
      ElMessage.success(response.data.message)
    } else {
      throw new Error(response.data.message || '获取失败')
    }

  } catch (err) {
    console.error('获取服务器列表失败:', err)
    error.value = err.response?.data?.detail || err.message || '获取服务器列表失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 后台刷新数据
const refreshInBackground = async () => {
  try {
    const response = await axios.post(
      `/api/server-discovery/fetch/${props.accountId}`
    )

    if (response.data.success && response.data.servers.length > 0) {
      // 静默更新数据（保持用户的选择）
      const newServers = response.data.servers
      
      // 合并新旧数据
      servers.value = newServers
      
      console.log('服务器列表已后台更新')
    }
  } catch (err) {
    console.error('后台刷新失败:', err)
  }
}

// 刷新服务器列表
const refreshServers = async () => {
  refreshing.value = true
  error.value = ''

  try {
    const response = await axios.get(
      `/api/server-discovery/refresh/${props.accountId}`
    )

    if (response.data.success) {
      servers.value = response.data.servers
      initializeSelections()
      ElMessage.success('服务器列表已刷新')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '刷新失败'
    ElMessage.error(error.value)
  } finally {
    refreshing.value = false
  }
}

// 初始化选择状态
const initializeSelections = () => {
  servers.value.forEach(server => {
    if (!(server.id in serverSelections)) {
      serverSelections[server.id] = false
    }

    if (server.channels) {
      server.channels.forEach(channel => {
        if (!(channel.id in channelSelections)) {
          channelSelections[channel.id] = false
        }
      })
    }
  })
}

// 确认选择
const confirmSelection = async () => {
  const selectedChannels = []

  servers.value.forEach(server => {
    if (server.channels) {
      server.channels.forEach(channel => {
        if (channelSelections[channel.id]) {
          selectedChannels.push({
            serverId: server.id,
            serverName: server.name,
            channelId: channel.id,
            channelName: channel.name,
            channelType: channel.type
          })
        }
      })
    }
  })

  if (selectedChannels.length === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }

  // 发送选择结果到父组件
  emit('update:selections', selectedChannels)
  emit('next')
}

// 组件挂载时获取服务器列表
onMounted(() => {
  fetchServers()
})
</script>

<style scoped>
.server-selection-step {
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  color: #303133;
  font-size: 24px;
  margin-bottom: 10px;
}

.step-desc {
  color: #606266;
  margin-bottom: 30px;
}

.loading-container {
  text-align: center;
  padding: 60px 0;
}

.loading-container p {
  margin-top: 20px;
  color: #909399;
}

.loading-tip {
  font-size: 14px;
  color: #409EFF;
}

.servers-container {
  padding: 20px 0;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stats {
  margin-left: auto;
  font-size: 14px;
  color: #606266;
}

.stats .highlight {
  color: #409EFF;
  font-weight: bold;
  font-size: 16px;
}

.server-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.server-card {
  transition: all 0.3s;
}

.server-card.selected {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.server-header {
  display: flex;
  align-items: center;
}

.server-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.server-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.server-icon-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.server-details {
  display: flex;
  flex-direction: column;
}

.server-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.server-stats {
  font-size: 13px;
  color: #909399;
}

.channels-container {
  margin-top: 10px;
}

.channels-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #EBEEF5;
  font-size: 14px;
  color: #606266;
  font-weight: bold;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}

.channel-item:hover {
  background: #f5f7fa;
}

.channel-name {
  flex: 1;
  font-size: 14px;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #EBEEF5;
}
</style>
