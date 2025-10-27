<template>
  <div class="mapping-visual-editor-ultra">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <el-button type="primary" @click="smartMapping">
        <el-icon><MagicStick /></el-icon>
        智能映射
      </el-button>
      <el-button @click="clearAllMappings">
        <el-icon><Delete /></el-icon>
        清空映射
      </el-button>
      <el-button @click="saveMappings" :loading="saving">
        <el-icon><Check /></el-icon>
        保存映射
      </el-button>
      <el-divider direction="vertical" />
      <el-switch
        v-model="showConnections"
        active-text="显示连接线"
        inactive-text="隐藏连接线"
      />
    </div>

    <!-- 主编辑区域 -->
    <div class="editor-main" ref="editorContainer">
      <!-- 左侧：KOOK频道列表 -->
      <div class="channel-panel left-panel">
        <div class="panel-header">
          <h3>📢 KOOK频道（源）</h3>
          <el-input
            v-model="leftSearch"
            placeholder="搜索频道..."
            clearable
            size="small"
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="panel-content" ref="leftPanel">
          <div
            v-for="server in filteredKookServers"
            :key="server.id"
            class="server-group"
          >
            <div class="server-header">
              <el-icon><FolderOpened /></el-icon>
              <span>{{ server.name }}</span>
              <el-tag size="small">{{ server.channels?.length || 0 }}个频道</el-tag>
            </div>

            <div class="channel-list">
              <div
                v-for="channel in server.channels"
                :key="channel.id"
                :ref="`kook-${channel.id}`"
                class="channel-item kook-channel"
                :class="{ 'is-mapped': isMapped(channel.id) }"
                :data-channel-id="channel.id"
                :draggable="true"
                @dragstart="handleDragStart($event, channel, 'kook')"
                @dragend="handleDragEnd"
              >
                <el-icon v-if="channel.type === 'voice'"><Headset /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
                <span>{{ channel.name }}</span>
                <el-tag
                  v-if="getMappingCount(channel.id) > 0"
                  size="small"
                  type="success"
                >
                  {{ getMappingCount(channel.id) }}个映射
                </el-tag>
              </div>
            </div>
          </div>

          <el-empty
            v-if="filteredKookServers.length === 0"
            description="暂无频道"
            :image-size="80"
          />
        </div>
      </div>

      <!-- SVG连接线画布 -->
      <svg
        v-if="showConnections"
        class="connections-canvas"
        :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
      >
        <defs>
          <!-- 定义渐变色 -->
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#409EFF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#67C23A;stop-opacity:1" />
          </linearGradient>
          <!-- 箭头标记 -->
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#67C23A" />
          </marker>
        </defs>

        <!-- 绘制贝塞尔曲线连接线 -->
        <path
          v-for="(connection, index) in connections"
          :key="`connection-${index}`"
          :d="connection.path"
          stroke="url(#lineGradient)"
          stroke-width="3"
          fill="none"
          marker-end="url(#arrowhead)"
          class="connection-line"
          @click="removeConnection(connection)"
        />

        <!-- 临时拖拽连接线 -->
        <path
          v-if="tempConnection"
          :d="tempConnection"
          stroke="#409EFF"
          stroke-width="3"
          stroke-dasharray="5,5"
          fill="none"
          class="temp-connection-line"
        />
      </svg>

      <!-- 右侧：目标平台Bot列表 -->
      <div class="bot-panel right-panel">
        <div class="panel-header">
          <h3>🤖 目标平台（接收）</h3>
          <el-input
            v-model="rightSearch"
            placeholder="搜索Bot..."
            clearable
            size="small"
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="panel-content" ref="rightPanel">
          <div
            v-for="platform in ['Discord', 'Telegram', '飞书']"
            :key="platform"
            class="platform-group"
          >
            <div class="platform-header">
              <el-icon v-if="platform === 'Discord'"><ChatDotSquare /></el-icon>
              <el-icon v-else-if="platform === 'Telegram'"><Connection /></el-icon>
              <el-icon v-else><Message /></el-icon>
              <span>{{ platform }}</span>
            </div>

            <div class="bot-list">
              <div
                v-for="bot in getBotsBy Platform(platform)"
                :key="bot.id"
                :ref="`bot-${bot.id}`"
                class="bot-item"
                :class="{ 'is-drop-target': dropTargetBot === bot.id }"
                :data-bot-id="bot.id"
                @dragover.prevent="handleBotDragOver($event, bot)"
                @dragleave="handleBotDragLeave"
                @drop="handleBotDrop($event, bot)"
              >
                <div class="bot-info">
                  <div class="bot-icon">{{ platform.substring(0, 1) }}</div>
                  <div class="bot-details">
                    <div class="bot-name">{{ bot.name }}</div>
                    <div class="bot-meta">
                      {{ bot.target_channel || 'ID: ' + bot.id }}
                    </div>
                  </div>
                </div>
                <el-tag
                  v-if="getBotMappingCount(bot.id) > 0"
                  size="small"
                  type="primary"
                >
                  {{ getBotMappingCount(bot.id) }}个映射
                </el-tag>
              </div>
            </div>

            <el-empty
              v-if="getBotsByPlatform(platform).length === 0"
              description="暂无Bot"
              :image-size="60"
            >
              <el-button type="primary" size="small" @click="goToAddBot(platform)">
                添加{{ platform }} Bot
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部映射预览面板 -->
    <div class="mapping-preview-panel">
      <div class="preview-header">
        <h3>📋 映射预览（{{ mappings.length }}个映射关系）</h3>
        <el-button size="small" @click="exportMappings">
          <el-icon><Download /></el-icon>
          导出配置
        </el-button>
      </div>

      <div class="preview-content">
        <div
          v-for="(mapping, index) in mappings"
          :key="index"
          class="mapping-item"
        >
          <div class="mapping-source">
            <el-icon><ChatDotRound /></el-icon>
            <span>{{ getChannelName(mapping.kook_channel_id) }}</span>
          </div>
          <div class="mapping-arrow">
            <el-icon><Right /></el-icon>
          </div>
          <div class="mapping-targets">
            <div
              v-for="target in mapping.targets"
              :key="target.bot_id"
              class="mapping-target"
            >
              <el-tag size="small" :type="getPlatformColor(target.platform)">
                {{ target.platform }}
              </el-tag>
              <span>{{ target.bot_name }}</span>
            </div>
          </div>
          <el-button
            type="danger"
            size="small"
            circle
            @click="removeMapping(index)"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <el-empty
          v-if="mappings.length === 0"
          description="暂无映射关系，请拖拽左侧频道到右侧Bot建立映射"
          :image-size="100"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

// 状态
const loading = ref(false)
const saving = ref(false)
const showConnections = ref(true)
const leftSearch = ref('')
const rightSearch = ref('')
const dropTargetBot = ref(null)
const draggingChannel = ref(null)

// 数据
const kookServers = ref([])
const bots = ref([])
const mappings = ref([])
const connections = ref([])
const tempConnection = ref(null)

// 引用
const editorContainer = ref(null)
const leftPanel = ref(null)
const rightPanel = ref(null)

// 画布尺寸
const canvasWidth = ref(400)
const canvasHeight = ref(800)

// 筛选后的KOOK服务器
const filteredKookServers = computed(() => {
  if (!leftSearch.value) return kookServers.value

  const keyword = leftSearch.value.toLowerCase()
  return kookServers.value.map(server => ({
    ...server,
    channels: server.channels?.filter(ch =>
      ch.name.toLowerCase().includes(keyword)
    ) || []
  })).filter(server => server.channels.length > 0)
})

// 按平台筛选Bot
const getBotsByPlatform = (platform) => {
  let platformBots = bots.value.filter(bot => bot.platform === platform.toLowerCase())
  
  if (rightSearch.value) {
    const keyword = rightSearch.value.toLowerCase()
    platformBots = platformBots.filter(bot =>
      bot.name.toLowerCase().includes(keyword)
    )
  }
  
  return platformBots
}

// 检查频道是否已映射
const isMapped = (channelId) => {
  return mappings.value.some(m => m.kook_channel_id === channelId)
}

// 获取频道的映射数量
const getMappingCount = (channelId) => {
  const mapping = mappings.value.find(m => m.kook_channel_id === channelId)
  return mapping?.targets?.length || 0
}

// 获取Bot的映射数量
const getBotMappingCount = (botId) => {
  let count = 0
  mappings.value.forEach(mapping => {
    if (mapping.targets.some(t => t.bot_id === botId)) {
      count++
    }
  })
  return count
}

// 获取频道名称
const getChannelName = (channelId) => {
  for (const server of kookServers.value) {
    const channel = server.channels?.find(ch => ch.id === channelId)
    if (channel) return channel.name
  }
  return channelId
}

// 获取平台颜色
const getPlatformColor = (platform) => {
  const colors = {
    'discord': 'primary',
    'telegram': 'info',
    'feishu': 'success',
    '飞书': 'success'
  }
  return colors[platform.toLowerCase()] || 'info'
}

// 拖拽开始
const handleDragStart = (event, channel, type) => {
  draggingChannel.value = channel
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('text/plain', JSON.stringify({
    type,
    data: channel
  }))
  
  // 添加拖拽样式
  event.target.classList.add('is-dragging')
}

// 拖拽结束
const handleDragEnd = (event) => {
  event.target.classList.remove('is-dragging')
  draggingChannel.value = null
  tempConnection.value = null
}

// Bot拖拽经过
const handleBotDragOver = (event, bot) => {
  event.preventDefault()
  dropTargetBot.value = bot.id
  
  // 计算临时连接线
  if (draggingChannel.value) {
    updateTempConnection(event)
  }
}

// Bot拖拽离开
const handleBotDragLeave = () => {
  dropTargetBot.value = null
}

// Bot接收拖放
const handleBotDrop = (event, bot) => {
  event.preventDefault()
  dropTargetBot.value = null
  tempConnection.value = null
  
  try {
    const data = JSON.parse(event.dataTransfer.getData('text/plain'))
    
    if (data.type === 'kook' && data.data) {
      const channel = data.data
      addMapping(channel, bot)
    }
  } catch (error) {
    console.error('处理拖放失败:', error)
  }
}

// 更新临时连接线
const updateTempConnection = (event) => {
  if (!draggingChannel.value || !editorContainer.value) return

  // 获取起点位置（左侧频道）
  const channelEl = document.querySelector(`[data-channel-id="${draggingChannel.value.id}"]`)
  if (!channelEl) return

  const containerRect = editorContainer.value.getBoundingClientRect()
  const channelRect = channelEl.getBoundingClientRect()
  
  const startX = channelRect.right - containerRect.left
  const startY = channelRect.top - containerRect.top + channelRect.height / 2
  
  // 获取终点位置（鼠标位置）
  const endX = event.clientX - containerRect.left
  const endY = event.clientY - containerRect.top
  
  // 生成贝塞尔曲线路径
  tempConnection.value = generateCurvePath(startX, startY, endX, endY)
}

// 生成贝塞尔曲线路径
const generateCurvePath = (x1, y1, x2, y2) => {
  const mx = (x1 + x2) / 2
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`
}

// 添加映射
const addMapping = (channel, bot) => {
  // 检查是否已存在
  const existing = mappings.value.find(m => m.kook_channel_id === channel.id)
  
  if (existing) {
    // 已存在，添加目标
    if (!existing.targets.some(t => t.bot_id === bot.id)) {
      existing.targets.push({
        bot_id: bot.id,
        bot_name: bot.name,
        platform: bot.platform,
        target_channel: bot.target_channel || ''
      })
      ElMessage.success(`已将 ${channel.name} 添加到 ${bot.name}`)
    } else {
      ElMessage.warning('该映射已存在')
    }
  } else {
    // 创建新映射
    mappings.value.push({
      kook_channel_id: channel.id,
      kook_channel_name: channel.name,
      kook_server_id: channel.server_id,
      targets: [{
        bot_id: bot.id,
        bot_name: bot.name,
        platform: bot.platform,
        target_channel: bot.target_channel || ''
      }]
    })
    ElMessage.success(`已创建映射：${channel.name} → ${bot.name}`)
  }
  
  // 更新连接线
  updateConnections()
}

// 删除映射
const removeMapping = (index) => {
  const mapping = mappings.value[index]
  ElMessageBox.confirm(
    `确定要删除"${mapping.kook_channel_name}"的映射吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    mappings.value.splice(index, 1)
    updateConnections()
    ElMessage.success('已删除映射')
  }).catch(() => {})
}

// 删除连接线
const removeConnection = (connection) => {
  const mapping = mappings.value.find(
    m => m.kook_channel_id === connection.channelId && 
         m.targets.some(t => t.bot_id === connection.botId)
  )
  
  if (mapping) {
    mapping.targets = mapping.targets.filter(t => t.bot_id !== connection.botId)
    if (mapping.targets.length === 0) {
      const index = mappings.value.indexOf(mapping)
      mappings.value.splice(index, 1)
    }
    updateConnections()
    ElMessage.success('已删除连接')
  }
}

// 更新连接线
const updateConnections = async () => {
  await nextTick()
  
  if (!editorContainer.value || !showConnections.value) return

  connections.value = []
  const containerRect = editorContainer.value.getBoundingClientRect()

  mappings.value.forEach(mapping => {
    const channelEl = document.querySelector(`[data-channel-id="${mapping.kook_channel_id}"]`)
    if (!channelEl) return

    const channelRect = channelEl.getBoundingClientRect()
    const startX = channelRect.right - containerRect.left
    const startY = channelRect.top - containerRect.top + channelRect.height / 2

    mapping.targets.forEach(target => {
      const botEl = document.querySelector(`[data-bot-id="${target.bot_id}"]`)
      if (!botEl) return

      const botRect = botEl.getBoundingClientRect()
      const endX = botRect.left - containerRect.left
      const endY = botRect.top - containerRect.top + botRect.height / 2

      connections.value.push({
        channelId: mapping.kook_channel_id,
        botId: target.bot_id,
        path: generateCurvePath(startX, startY, endX, endY)
      })
    })
  })
}

// 智能映射
const smartMapping = async () => {
  try {
    ElMessageBox.confirm(
      '智能映射将根据频道名称自动匹配Bot，可能会覆盖部分现有映射。是否继续？',
      '智能映射',
      {
        confirmButtonText: '开始匹配',
        cancelButtonText: '取消',
        type: 'info'
      }
    ).then(async () => {
      loading.value = true
      
      const response = await api.post('/api/smart-mapping-enhanced/auto-match', {
        kook_channels: getAllChannels(),
        bots: bots.value
      })
      
      if (response.success) {
        const matched = response.mappings || []
        
        // 合并到现有映射
        matched.forEach(newMapping => {
          const existing = mappings.value.find(
            m => m.kook_channel_id === newMapping.kook_channel_id
          )
          
          if (existing) {
            // 合并目标
            newMapping.targets.forEach(target => {
              if (!existing.targets.some(t => t.bot_id === target.bot_id)) {
                existing.targets.push(target)
              }
            })
          } else {
            mappings.value.push(newMapping)
          }
        })
        
        updateConnections()
        ElMessage.success(`智能匹配完成！创建了 ${matched.length} 个映射`)
      }
    }).catch(() => {})
  } catch (error) {
    console.error('智能映射失败:', error)
    ElMessage.error('智能映射失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 获取所有频道
const getAllChannels = () => {
  const channels = []
  kookServers.value.forEach(server => {
    server.channels?.forEach(channel => {
      channels.push({
        ...channel,
        server_id: server.id,
        server_name: server.name
      })
    })
  })
  return channels
}

// 清空所有映射
const clearAllMappings = () => {
  if (mappings.value.length === 0) {
    ElMessage.info('当前没有映射')
    return
  }

  ElMessageBox.confirm(
    `确定要清空所有 ${mappings.value.length} 个映射吗？此操作不可恢复！`,
    '确认清空',
    {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    mappings.value = []
    connections.value = []
    ElMessage.success('已清空所有映射')
  }).catch(() => {})
}

// 保存映射
const saveMappings = async () => {
  if (mappings.value.length === 0) {
    ElMessage.warning('请先创建至少一个映射')
    return
  }

  try {
    saving.value = true
    
    const response = await api.post('/api/mappings/batch-save', {
      mappings: mappings.value
    })
    
    if (response.success) {
      ElMessage.success('✅ 映射已保存！')
    }
  } catch (error) {
    console.error('保存映射失败:', error)
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 导出映射配置
const exportMappings = () => {
  const data = JSON.stringify(mappings.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mapping-config-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('映射配置已导出')
}

// 前往添加Bot
const goToAddBot = (platform) => {
  router.push(`/bots?platform=${platform.toLowerCase()}`)
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    // 加载服务器和频道
    const serversRes = await api.get('/api/accounts/servers')
    if (serversRes.success) {
      kookServers.value = serversRes.servers || []
    }
    
    // 加载Bot列表
    const botsRes = await api.get('/api/bots')
    if (botsRes.success) {
      bots.value = botsRes.bots || []
    }
    
    // 加载现有映射
    const mappingsRes = await api.get('/api/mappings')
    if (mappingsRes.success) {
      mappings.value = mappingsRes.mappings || []
    }
    
    // 更新连接线
    await nextTick()
    updateConnections()
    
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 监听窗口大小变化
const handleResize = () => {
  if (editorContainer.value) {
    const rect = editorContainer.value.getBoundingClientRect()
    canvasWidth.value = rect.width
    canvasHeight.value = rect.height
    updateConnections()
  }
}

onMounted(() => {
  loadData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
  handleResize()
})
</script>

<style scoped>
.mapping-visual-editor-ultra {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.editor-main {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 面板样式 */
.channel-panel,
.bot-panel {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 服务器组 */
.server-group {
  margin-bottom: 20px;
}

.server-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 12px;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 频道项 */
.channel-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.3s;
}

.channel-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateX(4px);
}

.channel-item.is-dragging {
  opacity: 0.5;
  cursor: grabbing;
}

.channel-item.is-mapped {
  border-color: #67c23a;
  background: #f0f9ff;
}

/* 平台组 */
.platform-group {
  margin-bottom: 20px;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 12px;
}

.bot-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Bot项 */
.bot-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  border: 2px dashed #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.bot-item.is-drop-target {
  border-color: #67c23a;
  background: #f0f9ff;
  border-style: solid;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.bot-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
}

.bot-details {
  display: flex;
  flex-direction: column;
}

.bot-name {
  font-weight: 600;
  color: #303133;
}

.bot-meta {
  font-size: 12px;
  color: #909399;
}

/* SVG连接线 */
.connections-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.connection-line {
  pointer-events: stroke;
  cursor: pointer;
  transition: stroke-width 0.3s;
}

.connection-line:hover {
  stroke-width: 5;
  filter: drop-shadow(0 0 4px rgba(64, 158, 255, 0.6));
}

.temp-connection-line {
  opacity: 0.6;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

/* 映射预览面板 */
.mapping-preview-panel {
  background: white;
  border-top: 1px solid #e4e7ed;
  max-height: 300px;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.mapping-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.mapping-source {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
  font-weight: 600;
  color: #303133;
}

.mapping-arrow {
  color: #409eff;
  font-size: 20px;
}

.mapping-targets {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mapping-target {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border-radius: 6px;
  font-size: 14px;
}
</style>
