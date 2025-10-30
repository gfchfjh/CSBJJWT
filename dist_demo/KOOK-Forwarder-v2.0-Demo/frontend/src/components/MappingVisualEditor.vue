<template>
  <div class="mapping-visual-editor">
    <div class="editor-header">
      <h2>🔀 可视化频道映射编辑器</h2>
      <p>从左侧拖拽KOOK频道到右侧目标平台，建立映射关系</p>
    </div>

    <div class="editor-layout">
      <!-- 左侧：KOOK频道源 -->
      <div class="source-panel">
        <div class="panel-header">
          <h3>📥 KOOK频道（消息来源）</h3>
          <el-button size="small" @click="refreshKookChannels">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div class="server-tree" v-loading="loadingServers">
          <el-collapse v-model="expandedServers">
            <el-collapse-item
              v-for="server in kookServers"
              :key="server.id"
              :name="server.id"
            >
              <template #title>
                <div class="server-title">
                  <el-icon><Folder /></el-icon>
                  <span>{{ server.name }}</span>
                  <el-tag size="small" type="info">{{ server.channels?.length || 0 }}个频道</el-tag>
                </div>
              </template>

              <div class="channel-list">
                <div
                  v-for="channel in server.channels"
                  :key="channel.id"
                  class="channel-item"
                  draggable="true"
                  @dragstart="handleDragStart($event, server, channel)"
                  @dragend="handleDragEnd"
                >
                  <el-icon><Document /></el-icon>
                  <span>{{ channel.name }}</span>
                  <el-badge
                    v-if="getChannelMappingCount(channel.id) > 0"
                    :value="getChannelMappingCount(channel.id)"
                    class="mapping-badge"
                  />
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>

          <el-empty v-if="kookServers.length === 0" description="暂无KOOK服务器">
            <el-button type="primary" @click="goToAccounts">前往添加账号</el-button>
          </el-empty>
        </div>
      </div>

      <!-- 中间：映射连接线 -->
      <div class="connection-area">
        <svg class="connection-svg" ref="connectionSvg">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#409EFF" />
            </marker>
          </defs>
          
          <g v-for="(line, index) in connectionLines" :key="index">
            <path
              :d="line.path"
              :stroke="line.color"
              stroke-width="2"
              fill="none"
              marker-end="url(#arrowhead)"
              class="connection-line"
            />
            <text
              :x="line.labelX"
              :y="line.labelY"
              class="line-label"
              fill="#606266"
              font-size="12"
            >
              {{ line.label }}
            </text>
          </g>
        </svg>

        <div class="connection-hint">
          <el-icon><Connection /></el-icon>
          <p>拖拽建立映射</p>
        </div>
      </div>

      <!-- 右侧：目标平台 -->
      <div class="target-panel">
        <div class="panel-header">
          <h3>📤 转发目标（接收平台）</h3>
          <el-button size="small" type="primary" @click="goToBots">
            <el-icon><Plus /></el-icon>
            添加Bot
          </el-button>
        </div>

        <div class="bot-list" v-loading="loadingBots">
          <div
            v-for="bot in configuredBots"
            :key="bot.id"
            class="bot-card"
            @drop="handleDrop($event, bot)"
            @dragover.prevent="handleDragOver($event, bot)"
            @dragleave="handleDragLeave($event, bot)"
            :class="{ 'drag-over': bot.isDragOver }"
          >
            <div class="bot-card-header">
              <el-tag :type="getPlatformTagType(bot.platform)" size="large">
                {{ getPlatformIcon(bot.platform) }} {{ bot.platform }}
              </el-tag>
              <h4>{{ bot.name }}</h4>
            </div>

            <div class="bot-card-body">
              <div v-if="bot.mappedChannels.length === 0" class="drop-zone-hint">
                <el-icon><Upload /></el-icon>
                <p>拖拽KOOK频道到此处</p>
              </div>

              <div v-else class="mapped-channels-list">
                <div
                  v-for="mapping in bot.mappedChannels"
                  :key="mapping.id"
                  class="mapped-channel-item"
                >
                  <div class="channel-info">
                    <el-icon><Document /></el-icon>
                    <span>{{ mapping.kook_channel_name }}</span>
                  </div>
                  <div class="channel-actions">
                    <el-tag size="small" :type="getConfidenceType(mapping.confidence)">
                      {{ mapping.confidence || 100 }}%
                    </el-tag>
                    <el-button
                      size="small"
                      type="danger"
                      text
                      @click="removeMapping(mapping.id)"
                    >
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div class="bot-card-footer">
              <el-statistic title="已映射" :value="bot.mappedChannels.length" />
              <el-button size="small" @click="testBot(bot.id)">
                <el-icon><CircleCheck /></el-icon>
                测试
              </el-button>
            </div>
          </div>

          <el-empty v-if="configuredBots.length === 0" description="暂无配置的Bot">
            <el-button type="primary" @click="goToBots">前往配置Bot</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 底部：映射预览与操作 -->
    <div class="mapping-preview-section">
      <el-divider />
      
      <div class="preview-header">
        <h3>📋 映射预览（共{{ allMappings.length }}条）</h3>
        <div class="preview-actions">
          <el-button @click="exportMappings">
            <el-icon><Download /></el-icon>
            导出配置
          </el-button>
          <el-button @click="importMappings">
            <el-icon><Upload /></el-icon>
            导入配置
          </el-button>
          <el-button type="warning" @click="clearAllMappings">
            <el-icon><Delete /></el-icon>
            清空所有映射
          </el-button>
        </div>
      </div>

      <div class="preview-content">
        <el-row :gutter="10">
          <el-col
            :span="8"
            v-for="(preview, index) in mappingPreviews"
            :key="index"
          >
            <el-card class="preview-card" shadow="hover">
              <div class="preview-item">
                <div class="preview-source">
                  <el-icon color="#409EFF"><Folder /></el-icon>
                  <span>{{ preview.source }}</span>
                </div>
                <el-icon class="preview-arrow"><Right /></el-icon>
                <div class="preview-targets">
                  <el-tag
                    v-for="target in preview.targets"
                    :key="target"
                    size="small"
                    style="margin: 2px"
                  >
                    {{ target }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="mappingPreviews.length === 0" description="还没有建立任何映射">
          <p style="color: #909399">从左侧拖拽KOOK频道到右侧Bot卡片，建立映射关系</p>
        </el-empty>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button size="large" @click="useSmartMapping">
        <el-icon><MagicStick /></el-icon>
        智能映射
      </el-button>
      <el-button type="success" size="large" @click="saveMappings" :loading="saving">
        <el-icon><Check /></el-icon>
        保存映射配置
      </el-button>
      <el-button type="primary" size="large" @click="testAllMappings">
        <el-icon><CircleCheck /></el-icon>
        测试所有映射
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Folder,
  Document,
  Refresh,
  Plus,
  Upload,
  Close,
  CircleCheck,
  Download,
  Delete,
  MagicStick,
  Check,
  Right,
  Connection
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 数据
const kookServers = ref([])
const configuredBots = ref([])
const expandedServers = ref([])
const loadingServers = ref(false)
const loadingBots = ref(false)
const saving = ref(false)

// 拖拽状态
const dragData = ref(null)

// SVG连接线
const connectionSvg = ref(null)
const connectionLines = ref([])

// 加载KOOK服务器和频道
async function loadKookChannels() {
  loadingServers.value = true
  try {
    const response = await api.get('/api/accounts')
    const accounts = response.data
    
    // 为每个账号加载服务器
    const serversPromises = accounts.map(account => 
      api.get(`/api/accounts/${account.id}/servers`)
    )
    
    const serversResponses = await Promise.all(serversPromises)
    
    kookServers.value = []
    for (const response of serversResponses) {
      if (response.data.servers) {
        for (const server of response.data.servers) {
          // 加载频道
          const channelsResponse = await api.get(
            `/api/accounts/${server.account_id}/servers/${server.id}/channels`
          )
          server.channels = channelsResponse.data.channels || []
          kookServers.value.push(server)
        }
      }
    }
    
    // 默认展开第一个服务器
    if (kookServers.value.length > 0) {
      expandedServers.value = [kookServers.value[0].id]
    }
  } catch (error) {
    ElMessage.error('加载KOOK频道失败: ' + error.message)
  } finally {
    loadingServers.value = false
  }
}

// 加载已配置的Bot
async function loadConfiguredBots() {
  loadingBots.value = true
  try {
    const response = await api.get('/api/bots')
    configuredBots.value = response.data.map(bot => ({
      ...bot,
      mappedChannels: [],
      isDragOver: false
    }))
    
    // 加载每个Bot的映射关系
    await loadAllMappings()
  } catch (error) {
    ElMessage.error('加载Bot配置失败: ' + error.message)
  } finally {
    loadingBots.value = false
  }
}

// 加载所有映射关系
async function loadAllMappings() {
  try {
    const response = await api.get('/api/mappings')
    const mappings = response.data
    
    // 将映射关系分配到对应的Bot
    configuredBots.value.forEach(bot => {
      bot.mappedChannels = mappings.filter(m => m.target_bot_id === bot.id)
    })
    
    // 更新连接线
    await nextTick()
    updateConnectionLines()
  } catch (error) {
    console.error('加载映射关系失败:', error)
  }
}

// 拖拽开始
function handleDragStart(event, server, channel) {
  dragData.value = {
    server,
    channel
  }
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('text/plain', JSON.stringify({
    server_id: server.id,
    server_name: server.name,
    channel_id: channel.id,
    channel_name: channel.name
  }))
}

// 拖拽结束
function handleDragEnd() {
  dragData.value = null
  // 清除所有dragOver状态
  configuredBots.value.forEach(bot => {
    bot.isDragOver = false
  })
}

// 拖拽悬停
function handleDragOver(event, bot) {
  event.preventDefault()
  bot.isDragOver = true
}

// 离开拖拽区域
function handleDragLeave(event, bot) {
  bot.isDragOver = false
}

// 放置到目标
async function handleDrop(event, bot) {
  event.preventDefault()
  bot.isDragOver = false
  
  if (!dragData.value) return
  
  const { server, channel } = dragData.value
  
  // 检查是否已存在映射
  const existing = bot.mappedChannels.find(
    m => m.kook_channel_id === channel.id
  )
  
  if (existing) {
    ElMessage.warning('该频道已映射到此Bot')
    return
  }
  
  // 创建映射
  try {
    const response = await api.post('/api/mappings', {
      kook_server_id: server.id,
      kook_channel_id: channel.id,
      kook_channel_name: channel.name,
      target_platform: bot.platform,
      target_bot_id: bot.id,
      target_channel_id: 'auto', // 自动使用Bot的默认频道
      enabled: true
    })
    
    // 添加到Bot的映射列表
    bot.mappedChannels.push(response.data)
    
    ElMessage.success(`已添加映射：${channel.name} → ${bot.name}`)
    
    // 更新连接线
    await nextTick()
    updateConnectionLines()
  } catch (error) {
    ElMessage.error('创建映射失败: ' + error.message)
  }
}

// 删除映射
async function removeMapping(mappingId) {
  try {
    await ElMessageBox.confirm('确定要删除此映射吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/api/mappings/${mappingId}`)
    
    // 从Bot列表中移除
    configuredBots.value.forEach(bot => {
      const index = bot.mappedChannels.findIndex(m => m.id === mappingId)
      if (index !== -1) {
        bot.mappedChannels.splice(index, 1)
      }
    })
    
    ElMessage.success('映射已删除')
    
    // 更新连接线
    await nextTick()
    updateConnectionLines()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 更新SVG连接线
function updateConnectionLines() {
  if (!connectionSvg.value) return
  
  const lines = []
  const svgRect = connectionSvg.value.getBoundingClientRect()
  
  configuredBots.value.forEach(bot => {
    bot.mappedChannels.forEach(mapping => {
      // 查找源频道元素
      const sourceEl = document.querySelector(`[data-channel-id="${mapping.kook_channel_id}"]`)
      // 查找目标Bot元素
      const targetEl = document.querySelector(`[data-bot-id="${bot.id}"]`)
      
      if (sourceEl && targetEl) {
        const sourceRect = sourceEl.getBoundingClientRect()
        const targetRect = targetEl.getBoundingClientRect()
        
        const startX = sourceRect.right - svgRect.left
        const startY = sourceRect.top + sourceRect.height / 2 - svgRect.top
        const endX = targetRect.left - svgRect.left
        const endY = targetRect.top + targetRect.height / 2 - svgRect.top
        
        // 贝塞尔曲线路径
        const controlX = (startX + endX) / 2
        const path = `M ${startX} ${startY} Q ${controlX} ${startY}, ${controlX} ${(startY + endY) / 2} T ${endX} ${endY}`
        
        lines.push({
          path,
          color: '#409EFF',
          label: mapping.kook_channel_name,
          labelX: controlX,
          labelY: (startY + endY) / 2 - 10
        })
      }
    })
  })
  
  connectionLines.value = lines
}

// 获取频道映射数量
function getChannelMappingCount(channelId) {
  let count = 0
  configuredBots.value.forEach(bot => {
    count += bot.mappedChannels.filter(m => m.kook_channel_id === channelId).length
  })
  return count
}

// 获取平台图标
function getPlatformIcon(platform) {
  const icons = {
    discord: '💬',
    telegram: '✈️',
    feishu: '🏢'
  }
  return icons[platform] || '🤖'
}

// 获取平台标签类型
function getPlatformTagType(platform) {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

// 获取置信度类型
function getConfidenceType(confidence) {
  if (confidence >= 80) return 'success'
  if (confidence >= 60) return 'warning'
  return 'danger'
}

// 所有映射
const allMappings = computed(() => {
  const mappings = []
  configuredBots.value.forEach(bot => {
    mappings.push(...bot.mappedChannels)
  })
  return mappings
})

// 映射预览
const mappingPreviews = computed(() => {
  const previews = new Map()
  
  allMappings.value.forEach(mapping => {
    const key = `${mapping.kook_server_id}-${mapping.kook_channel_id}`
    
    if (!previews.has(key)) {
      previews.set(key, {
        source: mapping.kook_channel_name,
        targets: []
      })
    }
    
    const bot = configuredBots.value.find(b => b.id === mapping.target_bot_id)
    if (bot) {
      previews.get(key).targets.push(`${bot.platform}:${bot.name}`)
    }
  })
  
  return Array.from(previews.values())
})

// 智能映射
async function useSmartMapping() {
  try {
    await ElMessageBox.confirm(
      '智能映射会自动匹配同名或相似的频道，是否继续？',
      '智能映射',
      { type: 'info' }
    )
    
    const response = await api.post('/api/smart-mapping/auto-map')
    
    ElMessage.success(`智能映射完成！共生成${response.data.count}条映射`)
    
    // 重新加载映射
    await loadAllMappings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('智能映射失败: ' + error.message)
    }
  }
}

// 保存映射
async function saveMappings() {
  saving.value = true
  try {
    // 映射已经在创建时保存，这里只是确认
    ElMessage.success('映射配置已保存')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 测试所有映射
async function testAllMappings() {
  try {
    await ElMessageBox.confirm(
      '将向所有映射的目标平台发送测试消息，是否继续？',
      '测试映射',
      { type: 'warning' }
    )
    
    const response = await api.post('/api/mappings/test-all')
    
    ElMessage.success(`测试完成！成功：${response.data.success}，失败：${response.data.failed}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('测试失败: ' + error.message)
    }
  }
}

// 测试单个Bot
async function testBot(botId) {
  try {
    await api.post(`/api/bots/${botId}/test`)
    ElMessage.success('测试消息发送成功！')
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

// 导出映射
function exportMappings() {
  const data = JSON.stringify(allMappings.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mappings-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('映射配置已导出')
}

// 导入映射
async function importMappings() {
  // TODO: 实现导入功能
  ElMessage.info('导入功能开发中...')
}

// 清空所有映射
async function clearAllMappings() {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有映射吗？此操作不可恢复！',
      '危险操作',
      { type: 'error' }
    )
    
    await api.delete('/api/mappings/all')
    
    configuredBots.value.forEach(bot => {
      bot.mappedChannels = []
    })
    
    connectionLines.value = []
    
    ElMessage.success('已清空所有映射')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

// 刷新KOOK频道
function refreshKookChannels() {
  loadKookChannels()
}

// 跳转到账号管理
function goToAccounts() {
  router.push('/accounts')
}

// 跳转到Bot配置
function goToBots() {
  router.push('/bots')
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadKookChannels(),
    loadConfiguredBots()
  ])
})
</script>

<style scoped>
.mapping-visual-editor {
  padding: 20px;
}

.editor-header {
  text-align: center;
  margin-bottom: 30px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.editor-header p {
  margin: 0;
  color: #909399;
}

.editor-layout {
  display: flex;
  gap: 20px;
  min-height: 600px;
  margin-bottom: 30px;
}

.source-panel,
.target-panel {
  flex: 1;
  border: 2px dashed #DCDFE6;
  border-radius: 12px;
  padding: 20px;
  background: #FAFAFA;
  overflow-y: auto;
  max-height: 700px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #E4E7ED;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.channel-list {
  padding-left: 20px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  margin: 5px 0;
  background: white;
  border: 1px solid #E4E7ED;
  border-radius: 6px;
  cursor: move;
  transition: all 0.3s;
}

.channel-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  transform: translateX(5px);
}

.mapping-badge {
  margin-left: auto;
}

.connection-area {
  width: 150px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.connection-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connection-line {
  transition: all 0.3s;
}

.connection-line:hover {
  stroke-width: 3;
}

.line-label {
  font-size: 12px;
  text-anchor: middle;
}

.connection-hint {
  text-align: center;
  color: #909399;
}

.connection-hint p {
  margin-top: 10px;
  font-size: 14px;
}

.bot-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bot-card {
  border: 2px solid #E4E7ED;
  border-radius: 12px;
  padding: 15px;
  background: white;
  transition: all 0.3s;
}

.bot-card.drag-over {
  border-color: #67C23A;
  background: #F0F9FF;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.bot-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.bot-card-header h4 {
  margin: 0;
  font-size: 16px;
}

.bot-card-body {
  min-height: 100px;
}

.drop-zone-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  border: 2px dashed #DCDFE6;
  border-radius: 8px;
  color: #909399;
}

.mapped-channels-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mapped-channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #F5F7FA;
  border-radius: 6px;
  transition: all 0.2s;
}

.mapped-channel-item:hover {
  background: #E4E7ED;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.channel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bot-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #E4E7ED;
}

.mapping-preview-section {
  margin-top: 30px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.preview-header h3 {
  margin: 0;
  font-size: 18px;
}

.preview-actions {
  display: flex;
  gap: 10px;
}

.preview-content {
  max-height: 300px;
  overflow-y: auto;
}

.preview-card {
  margin-bottom: 10px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-source {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
}

.preview-arrow {
  color: #409EFF;
}

.preview-targets {
  flex: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.action-bar {
  margin-top: 30px;
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 12px;
}
</style>
