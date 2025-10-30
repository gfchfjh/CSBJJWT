<template>
  <div class="drag-mapping-view">
    <el-alert
      title="拖拽式映射"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <p>从左侧的KOOK频道拖拽到右侧的目标平台频道，即可快速建立映射关系。</p>
      <p>💡 提示：可以将一个KOOK频道拖拽到多个目标频道</p>
    </el-alert>

    <div class="drag-mapping-container">
      <!-- 左侧：KOOK频道列表 -->
      <div class="channels-panel kook-channels">
        <div class="panel-header">
          <h3>📱 KOOK频道</h3>
          <el-input
            v-model="kookSearchKeyword"
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

        <div class="channels-list">
          <el-collapse v-model="activeKookServers" accordion>
            <el-collapse-item
              v-for="server in filteredKookServers"
              :key="server.id"
              :name="server.id"
            >
              <template #title>
                <div class="server-title">
                  <img v-if="server.icon" :src="server.icon" class="server-icon" alt="icon" />
                  <span>{{ server.name }}</span>
                  <el-tag size="small" type="info" style="margin-left: auto">
                    {{ server.channels?.length || 0 }}个频道
                  </el-tag>
                </div>
              </template>

              <draggable
                v-model="server.channels"
                :group="{ name: 'channels', pull: 'clone', put: false }"
                :clone="cloneChannel"
                item-key="id"
                class="draggable-channels"
              >
                <template #item="{ element }">
                  <div
                    class="channel-item kook-channel"
                    :class="{ 'is-mapped': isChannelMapped(element.id) }"
                  >
                    <span class="channel-icon">#</span>
                    <span class="channel-name">{{ element.name }}</span>
                    <el-tag v-if="isChannelMapped(element.id)" size="small" type="success">
                      已映射
                    </el-tag>
                  </div>
                </template>
              </draggable>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 中间：映射关系可视化 -->
      <div class="mapping-visualization">
        <div class="connections-svg" ref="connectionsRef">
          <svg :width="connectionsSvgWidth" :height="connectionsSvgHeight">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#409eff" />
              </marker>
            </defs>
            <path
              v-for="(connection, index) in connections"
              :key="index"
              :d="connection.path"
              stroke="#409eff"
              stroke-width="2"
              fill="none"
              marker-end="url(#arrowhead)"
              class="connection-line"
            />
          </svg>
        </div>
        <div class="mapping-count">
          <el-statistic title="已建立映射" :value="currentMappings.length" />
        </div>
      </div>

      <!-- 右侧：目标平台频道 -->
      <div class="channels-panel target-channels">
        <div class="panel-header">
          <h3>🎯 目标平台</h3>
          <el-select
            v-model="selectedTargetPlatform"
            placeholder="选择平台"
            size="small"
            style="width: 150px"
          >
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </div>

        <div class="channels-list">
          <div v-if="selectedTargetPlatform" class="target-platform-section">
            <h4>{{ getPlatformName(selectedTargetPlatform) }} 机器人</h4>
            <el-collapse v-model="activeTargetBots" accordion>
              <el-collapse-item
                v-for="bot in targetBots"
                :key="bot.id"
                :name="bot.id"
              >
                <template #title>
                  <div class="bot-title">
                    <span>🤖 {{ bot.name }}</span>
                  </div>
                </template>

                <draggable
                  v-model="bot.channels"
                  :group="{ name: 'channels', pull: false, put: true }"
                  @add="handleDrop($event, bot)"
                  item-key="id"
                  class="draggable-channels drop-zone"
                >
                  <template #item="{ element }">
                    <div class="channel-item target-channel">
                      <span class="channel-icon">#</span>
                      <span class="channel-name">{{ element.kook_channel_name }}</span>
                      <el-button
                        type="danger"
                        size="small"
                        circle
                        @click="removeMapping(element)"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </div>
                  </template>

                  <template #footer>
                    <div v-if="!bot.channels || bot.channels.length === 0" class="drop-hint">
                      <el-icon><Plus /></el-icon>
                      <span>拖拽频道到这里</span>
                    </div>
                  </template>
                </draggable>
              </el-collapse-item>
            </el-collapse>
          </div>

          <el-empty v-else description="请先选择目标平台" />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button @click="emit('cancel')">取消</el-button>
      <el-button @click="clearAllMappings">清空全部</el-button>
      <el-button type="primary" @click="saveMappings" :loading="saving">
        <el-icon><Check /></el-icon>
        保存映射 ({{ currentMappings.length }}个)
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Close, Check } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import api from '@/api'

const emit = defineEmits(['save', 'cancel'])

// 搜索关键词
const kookSearchKeyword = ref('')

// KOOK服务器和频道
const kookServers = ref([])
const activeKookServers = ref([])

// 目标平台
const selectedTargetPlatform = ref('')
const targetBots = ref([])
const activeTargetBots = ref([])

// 当前映射
const currentMappings = ref([])

// 连接线
const connections = ref([])
const connectionsRef = ref(null)
const connectionsSvgWidth = ref(800)
const connectionsSvgHeight = ref(600)

// 保存状态
const saving = ref(false)

// 过滤后的KOOK服务器
const filteredKookServers = computed(() => {
  if (!kookSearchKeyword.value) return kookServers.value
  
  return kookServers.value
    .map(server => ({
      ...server,
      channels: server.channels?.filter(ch => 
        ch.name.toLowerCase().includes(kookSearchKeyword.value.toLowerCase())
      ) || []
    }))
    .filter(server => server.channels.length > 0)
})

// 获取平台名称
const getPlatformName = (platform) => {
  const names = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  }
  return names[platform] || platform
}

// 检查频道是否已映射
const isChannelMapped = (channelId) => {
  return currentMappings.value.some(m => m.kook_channel_id === channelId)
}

// 克隆频道数据（用于拖拽）
const cloneChannel = (channel) => {
  return {
    ...channel,
    kook_channel_id: channel.id,
    kook_channel_name: channel.name,
    kook_server_id: channel.server_id
  }
}

// 处理拖放事件
const handleDrop = (event, bot) => {
  const droppedChannel = event.item._underlying_vm_
  
  // 检查是否已存在相同映射
  const exists = currentMappings.value.some(m => 
    m.kook_channel_id === droppedChannel.kook_channel_id &&
    m.target_bot_id === bot.id
  )

  if (exists) {
    ElMessage.warning('该映射关系已存在')
    // 移除重复项
    bot.channels.splice(event.newIndex, 1)
    return
  }

  // 添加映射
  const mapping = {
    id: Date.now(),  // 临时ID
    kook_server_id: droppedChannel.kook_server_id || droppedChannel.server_id,
    kook_channel_id: droppedChannel.kook_channel_id || droppedChannel.id,
    kook_channel_name: droppedChannel.kook_channel_name || droppedChannel.name,
    target_platform: selectedTargetPlatform.value,
    target_bot_id: bot.id,
    target_channel_id: '', // 用户需要后续填写
    enabled: true
  }

  currentMappings.value.push(mapping)
  
  // 更新Bot的channels列表
  const index = bot.channels.findIndex(ch => ch.id === mapping.id)
  if (index !== -1) {
    bot.channels[index] = mapping
  }

  ElMessage.success('映射添加成功！')
  
  // 更新连接线
  nextTick(() => {
    updateConnections()
  })
}

// 移除映射
const removeMapping = (mapping) => {
  const index = currentMappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    currentMappings.value.splice(index, 1)
  }

  // 从Bot的channels中移除
  targetBots.value.forEach(bot => {
    const chIndex = bot.channels?.findIndex(ch => ch.id === mapping.id)
    if (chIndex !== -1) {
      bot.channels.splice(chIndex, 1)
    }
  })

  ElMessage.success('映射已移除')
  updateConnections()
}

// 清空所有映射
const clearAllMappings = () => {
  ElMessageBox.confirm(
    '确定要清空所有映射吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    currentMappings.value = []
    targetBots.value.forEach(bot => {
      bot.channels = []
    })
    connections.value = []
    ElMessage.success('已清空所有映射')
  }).catch(() => {
    // 取消
  })
}

// 更新连接线
const updateConnections = () => {
  // 这里可以计算连接线的路径
  // 由于需要获取DOM元素位置，暂时简化实现
  connections.value = []
}

// 保存映射
const saveMappings = async () => {
  if (currentMappings.value.length === 0) {
    ElMessage.warning('请先添加映射关系')
    return
  }

  // 检查是否有空的target_channel_id
  const incompleteMapping = currentMappings.value.find(m => !m.target_channel_id)
  if (incompleteMapping) {
    ElMessage.warning('请为所有映射填写目标频道ID')
    return
  }

  try {
    saving.value = true
    
    // 批量保存映射
    for (const mapping of currentMappings.value) {
      await api.addMapping({
        kook_server_id: mapping.kook_server_id,
        kook_channel_id: mapping.kook_channel_id,
        kook_channel_name: mapping.kook_channel_name,
        target_platform: mapping.target_platform,
        target_bot_id: mapping.target_bot_id,
        target_channel_id: mapping.target_channel_id,
        enabled: mapping.enabled
      })
    }

    ElMessage.success(`成功保存 ${currentMappings.value.length} 个映射`)
    emit('save')
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 加载KOOK服务器和频道
const loadKookChannels = async () => {
  try {
    const accounts = await api.getAccounts()
    const onlineAccount = accounts.find(a => a.status === 'online')
    
    if (!onlineAccount) {
      ElMessage.warning('没有在线的KOOK账号')
      return
    }

    const servers = await api.getServers(onlineAccount.id)
    
    // 为每个服务器加载频道
    for (const server of servers) {
      const channels = await api.getChannels(onlineAccount.id, server.id)
      server.channels = channels.map(ch => ({
        ...ch,
        server_id: server.id
      }))
    }

    kookServers.value = servers
  } catch (error) {
    ElMessage.error('加载KOOK频道失败：' + (error.response?.data?.detail || error.message))
  }
}

// 加载目标平台机器人
const loadTargetBots = async (platform) => {
  try {
    const bots = await api.getBots()
    targetBots.value = bots
      .filter(bot => bot.platform === platform)
      .map(bot => ({
        ...bot,
        channels: []
      }))
  } catch (error) {
    ElMessage.error('加载机器人失败：' + (error.response?.data?.detail || error.message))
  }
}

// 监听平台切换
const handlePlatformChange = async (platform) => {
  await loadTargetBots(platform)
}

onMounted(async () => {
  await loadKookChannels()
})

// 监听平台选择
watch(() => selectedTargetPlatform.value, (newVal) => {
  if (newVal) {
    loadTargetBots(newVal)
  }
})
</script>

<script>
import { watch } from 'vue'
export default {
  name: 'DragMappingView'
}
</script>

<style scoped>
.drag-mapping-view {
  padding: 20px;
}

.drag-mapping-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  height: 600px;
}

.channels-panel {
  flex: 1;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f5f7fa;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.channels-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.server-title,
.bot-title {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.server-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.draggable-channels {
  min-height: 50px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  margin: 5px 0;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: move;
  transition: all 0.3s;
}

.channel-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.kook-channel.is-mapped {
  background: #f0f9ff;
  border-color: #67c23a;
}

.channel-icon {
  color: #909399;
  font-weight: bold;
}

.channel-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.target-channel {
  cursor: default;
  background: #f0f9ff;
}

.drop-zone {
  min-height: 100px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

.drop-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: #909399;
  font-size: 14px;
}

.drop-hint .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.mapping-visualization {
  width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-line {
  transition: all 0.3s;
}

.connection-line:hover {
  stroke-width: 3;
}

.mapping-count {
  z-index: 2;
}

.action-bar {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.target-platform-section h4 {
  margin: 10px 0;
  color: #303133;
  font-size: 14px;
}

/* 拖拽时的样式 */
.sortable-ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.sortable-drag {
  opacity: 0.8;
  transform: rotate(5deg);
}
</style>
