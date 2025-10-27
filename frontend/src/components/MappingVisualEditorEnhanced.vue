<template>
  <div class="mapping-visual-editor">
    <!-- ✅ P0-5优化: 可视化映射编辑器增强 - SVG贝塞尔曲线 + 拖拽操作 -->
    
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <h2>🔀 拖拽式可视化映射编辑器</h2>
        <p class="subtitle">从左侧拖动KOOK频道到右侧Bot卡片建立映射</p>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="autoMatch" type="success">
          <el-icon><MagicStick /></el-icon>
          智能映射（60+规则）
        </el-button>
        <el-button @click="clearAllMappings" type="warning">
          <el-icon><Delete /></el-icon>
          清空所有
        </el-button>
        <el-button @click="saveMappings" type="primary" :loading="saving">
          <el-icon><Check /></el-icon>
          保存映射
        </el-button>
      </div>
    </div>

    <!-- 主编辑区域 -->
    <div class="editor-main" ref="editorContainer">
      <!-- 左侧：KOOK频道列表 -->
      <div class="left-panel">
        <div class="panel-header gradient-blue">
          <h3>📡 KOOK频道（源）</h3>
          <el-input
            v-model="kookSearchKeyword"
            placeholder="搜索频道"
            size="small"
            clearable
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>

        <div class="channels-list">
          <!-- 按服务器分组 -->
          <el-collapse v-model="activeKookServers" accordion>
            <el-collapse-item
              v-for="server in filteredKookServers"
              :key="server.id"
              :name="server.id"
            >
              <template #title>
                <div class="server-title">
                  <img v-if="server.icon" :src="server.icon" class="server-icon" />
                  <div v-else class="server-icon-placeholder">
                    {{ server.name.charAt(0) }}
                  </div>
                  <span>{{ server.name }}</span>
                  <el-tag size="small">{{ server.channels.length }}</el-tag>
                </div>
              </template>

              <!-- 频道列表（可拖拽） -->
              <div class="channels-draggable">
                <div
                  v-for="channel in server.channels"
                  :key="channel.id"
                  class="channel-item"
                  :class="{ 'is-mapped': isMapped(channel.id) }"
                  draggable="true"
                  @dragstart="handleDragStart(channel, $event)"
                  @dragend="handleDragEnd"
                >
                  <div class="channel-drag-handle">
                    <el-icon><Rank /></el-icon>
                  </div>
                  
                  <div class="channel-info">
                    <el-icon v-if="channel.type === 'text'"><ChatDotRound /></el-icon>
                    <el-icon v-else><Microphone /></el-icon>
                    <span class="channel-name"># {{ channel.name }}</span>
                  </div>

                  <el-tag
                    v-if="getMappingCount(channel.id) > 0"
                    size="small"
                    type="success"
                  >
                    {{ getMappingCount(channel.id) }}个映射
                  </el-tag>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 中间：SVG连接线画布 -->
      <svg
        class="connection-svg"
        :width="svgWidth"
        :height="svgHeight"
        ref="svgCanvas"
      >
        <!-- 渐变色定义 -->
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#409EFF" />
            <stop offset="100%" stop-color="#67C23A" />
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

        <!-- 绘制连接线（贝塞尔曲线） -->
        <g v-for="(line, index) in connectionLines" :key="index">
          <path
            :d="line.path"
            :stroke="line.color || 'url(#lineGradient)'"
            stroke-width="3"
            fill="none"
            marker-end="url(#arrowhead)"
            class="connection-line"
            :class="{ 'line-hover': line.isHover }"
            @mouseenter="line.isHover = true"
            @mouseleave="line.isHover = false"
            @click="removeMapping(line.mappingId)"
          />
          
          <!-- 连接线文字标签 -->
          <text
            :x="line.midX"
            :y="line.midY"
            text-anchor="middle"
            class="connection-label"
            v-if="line.isHover"
          >
            <tspan>{{ line.label }}</tspan>
            <tspan x="line.midX" dy="15" class="remove-hint">点击删除</tspan>
          </text>
        </g>
      </svg>

      <!-- 右侧：目标Bot列表 -->
      <div class="right-panel">
        <div class="panel-header gradient-green">
          <h3>🎯 目标Bot（接收）</h3>
          <el-select v-model="selectedPlatform" size="small" placeholder="筛选平台">
            <el-option label="全部" value="" />
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </div>

        <div class="bots-list">
          <div
            v-for="bot in filteredBots"
            :key="bot.id"
            class="bot-card"
            :class="{ 'is-drop-target': isDragTarget && dragTargetBot === bot.id }"
            @dragover="handleBotDragOver(bot, $event)"
            @dragleave="handleBotDragLeave"
            @drop="handleBotDrop(bot, $event)"
          >
            <div class="bot-header">
              <div class="bot-icon" :class="`platform-${bot.platform}`">
                <el-icon v-if="bot.platform === 'discord'"><ChatLineRound /></el-icon>
                <el-icon v-else-if="bot.platform === 'telegram'"><ChatLineSquare /></el-icon>
                <el-icon v-else><Message /></el-icon>
              </div>
              
              <div class="bot-info">
                <h4>{{ bot.name }}</h4>
                <el-tag :type="platformTagType(bot.platform)" size="small">
                  {{ platformText(bot.platform) }}
                </el-tag>
              </div>
            </div>

            <div class="bot-stats">
              <div class="stat-item">
                <span class="stat-label">映射数</span>
                <span class="stat-value">{{ getBotMappingCount(bot.id) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">状态</span>
                <el-tag :type="bot.status === 'active' ? 'success' : 'info'" size="small">
                  {{ bot.status === 'active' ? '活跃' : '未激活' }}
                </el-tag>
              </div>
            </div>

            <!-- 已映射的频道列表 -->
            <div v-if="getBotMappings(bot.id).length > 0" class="bot-mappings">
              <div class="mappings-label">已映射频道:</div>
              <div
                v-for="mapping in getBotMappings(bot.id)"
                :key="mapping.id"
                class="mapping-item"
              >
                <span># {{ mapping.kook_channel_name }}</span>
                <el-button
                  size="small"
                  type="danger"
                  link
                  @click="removeMapping(mapping.id)"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 拖拽提示 -->
            <div v-else class="drop-hint">
              <el-icon><Upload /></el-icon>
              <span>拖拽频道到此处</span>
            </div>
          </div>

          <!-- 无Bot提示 -->
          <el-empty
            v-if="filteredBots.length === 0"
            description="还没有配置Bot"
            :image-size="80"
          >
            <el-button type="primary" @click="goToBots">
              去配置Bot
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 底部：映射预览面板 -->
    <div class="preview-panel">
      <div class="preview-header">
        <h3>📋 映射预览（{{ mappings.length }}条）</h3>
        <div class="preview-actions">
          <el-button @click="exportMappings" size="small">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button @click="importMappings" size="small">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
      </div>

      <div class="preview-content">
        <el-scrollbar height="200px">
          <div class="mapping-preview-list">
            <div
              v-for="mapping in mappings"
              :key="mapping.id"
              class="preview-item"
            >
              <div class="preview-source">
                <el-tag type="info">KOOK</el-tag>
                <span># {{ mapping.kook_channel_name }}</span>
              </div>

              <div class="preview-arrow">
                <el-icon><Right /></el-icon>
              </div>

              <div class="preview-target">
                <el-tag :type="platformTagType(mapping.target_platform)">
                  {{ platformText(mapping.target_platform) }}
                </el-tag>
                <span>{{ getBotName(mapping.target_bot_id) }}</span>
              </div>

              <div class="preview-actions">
                <el-button
                  size="small"
                  type="danger"
                  link
                  @click="removeMapping(mapping.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <el-empty
              v-if="mappings.length === 0"
              description="还没有建立任何映射"
              :image-size="60"
            />
          </div>
        </el-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick, Delete, Check, Search, Rank, ChatDotRound, Microphone,
  Upload, Close, Download, Right, Message, ChatLineRound, ChatLineSquare
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 数据
const kookServers = ref([])
const bots = ref([])
const mappings = ref([])

// UI状态
const activeKookServers = ref([])
const kookSearchKeyword = ref('')
const selectedPlatform = ref('')
const saving = ref(false)

// 拖拽状态
const isDragging = ref(false)
const isDragTarget = ref(false)
const dragTargetBot = ref(null)
const draggedChannel = ref(null)

// SVG画布
const editorContainer = ref(null)
const svgCanvas = ref(null)
const svgWidth = ref(400)
const svgHeight = ref(600)
const connectionLines = ref([])

// 计算属性
const filteredKookServers = computed(() => {
  if (!kookSearchKeyword.value) return kookServers.value
  
  const keyword = kookSearchKeyword.value.toLowerCase()
  return kookServers.value.map(server => ({
    ...server,
    channels: server.channels.filter(ch =>
      ch.name.toLowerCase().includes(keyword)
    )
  })).filter(server => server.channels.length > 0)
})

const filteredBots = computed(() => {
  if (!selectedPlatform.value) return bots.value
  return bots.value.filter(bot => bot.platform === selectedPlatform.value)
})

// 拖拽处理
const handleDragStart = (channel, event) => {
  isDragging.value = true
  draggedChannel.value = channel
  
  // 设置拖拽数据
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('text/plain', JSON.stringify(channel))
  
  // 添加拖拽样式
  event.target.style.opacity = '0.5'
}

const handleDragEnd = (event) => {
  isDragging.value = false
  draggedChannel.value = null
  event.target.style.opacity = '1'
}

const handleBotDragOver = (bot, event) => {
  event.preventDefault()
  isDragTarget.value = true
  dragTargetBot.value = bot.id
  event.dataTransfer.dropEffect = 'copy'
}

const handleBotDragLeave = () => {
  isDragTarget.value = false
  dragTargetBot.value = null
}

const handleBotDrop = async (bot, event) => {
  event.preventDefault()
  isDragTarget.value = false
  dragTargetBot.value = null
  
  if (!draggedChannel.value) return
  
  // 创建映射
  await createMapping(draggedChannel.value, bot)
}

// 映射操作
const createMapping = async (channel, bot) => {
  try {
    // 检查是否已存在映射
    const existing = mappings.value.find(m =>
      m.kook_channel_id === channel.id && m.target_bot_id === bot.id
    )
    
    if (existing) {
      ElMessage.warning('该映射已存在')
      return
    }
    
    // 创建新映射
    const newMapping = {
      id: Date.now(), // 临时ID
      kook_server_id: channel.server_id,
      kook_channel_id: channel.id,
      kook_channel_name: channel.name,
      target_platform: bot.platform,
      target_bot_id: bot.id,
      target_channel_id: bot.default_channel || '',
      enabled: true
    }
    
    mappings.value.push(newMapping)
    
    ElMessage.success(`✅ 已添加映射: ${channel.name} → ${bot.name}`)
    
    // 重新计算连接线
    await nextTick()
    updateConnectionLines()
  } catch (error) {
    ElMessage.error('创建映射失败: ' + error.message)
  }
}

const removeMapping = (mappingId) => {
  const index = mappings.value.findIndex(m => m.id === mappingId)
  if (index > -1) {
    const mapping = mappings.value[index]
    mappings.value.splice(index, 1)
    ElMessage.success(`已删除映射: ${mapping.kook_channel_name}`)
    updateConnectionLines()
  }
}

const clearAllMappings = () => {
  ElMessageBox.confirm(
    '确定要清空所有映射吗？',
    '确认清空',
    {
      type: 'warning'
    }
  ).then(() => {
    mappings.value = []
    connectionLines.value = []
    ElMessage.success('已清空所有映射')
  })
}

const saveMappings = async () => {
  if (mappings.value.length === 0) {
    ElMessage.warning('没有可保存的映射')
    return
  }
  
  saving.value = true
  
  try {
    const response = await api.post('/api/mappings/batch-save', {
      mappings: mappings.value
    })
    
    if (response.data.success) {
      ElMessage.success(`✅ 成功保存 ${mappings.value.length} 条映射`)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 智能映射
const autoMatch = async () => {
  try {
    const response = await api.post('/api/smart-mapping-enhanced/auto-match', {
      kook_channels: kookServers.value.flatMap(s => s.channels),
      target_bots: bots.value,
      min_confidence: 0.6
    })
    
    if (response.data.success) {
      const suggestions = response.data.suggestions
      
      ElMessageBox.confirm(
        `智能映射找到了 ${suggestions.length} 条推荐映射，是否应用？`,
        '智能映射结果',
        {
          type: 'success',
          confirmButtonText: '应用推荐',
          cancelButtonText: '取消'
        }
      ).then(() => {
        // 应用推荐映射
        suggestions.forEach(sug => {
          if (sug.confidence_level === 'high' || sug.confidence_level === 'medium') {
            mappings.value.push({
              id: Date.now() + Math.random(),
              kook_server_id: sug.kook_server_id,
              kook_channel_id: sug.kook_channel_id,
              kook_channel_name: sug.kook_channel_name,
              target_platform: sug.target_platform,
              target_bot_id: sug.target_bot_id,
              target_channel_id: sug.target_channel_id,
              enabled: true,
              confidence: sug.confidence_score
            })
          }
        })
        
        ElMessage.success(`✅ 已应用 ${suggestions.length} 条映射`)
        updateConnectionLines()
      })
    }
  } catch (error) {
    ElMessage.error('智能映射失败: ' + error.message)
  }
}

// SVG连接线计算
const updateConnectionLines = () => {
  connectionLines.value = []
  
  // 计算每条映射的连接线
  mappings.value.forEach(mapping => {
    // 获取源频道和目标Bot的DOM元素位置
    // 这里简化处理，实际需要计算真实DOM位置
    const line = calculateBezierPath(mapping)
    if (line) {
      connectionLines.value.push(line)
    }
  })
}

const calculateBezierPath = (mapping) => {
  // 简化的贝塞尔曲线路径计算
  // 实际应该根据DOM元素位置计算
  
  const startX = 50
  const startY = 100 + (mappings.value.indexOf(mapping) * 30)
  const endX = svgWidth.value - 50
  const endY = startY
  
  // 控制点（贝塞尔曲线）
  const controlX1 = startX + (endX - startX) * 0.3
  const controlY1 = startY
  const controlX2 = startX + (endX - startX) * 0.7
  const controlY2 = endY
  
  // 生成路径
  const path = `M ${startX},${startY} C ${controlX1},${controlY1} ${controlX2},${controlY2} ${endX},${endY}`
  
  // 中点（用于显示标签）
  const midX = (startX + endX) / 2
  const midY = (startY + endY) / 2
  
  return {
    path,
    midX,
    midY,
    mappingId: mapping.id,
    label: `${mapping.kook_channel_name} → ${getBotName(mapping.target_bot_id)}`,
    color: 'url(#lineGradient)',
    isHover: false
  }
}

// 工具函数
const isMapped = (channelId) => {
  return mappings.value.some(m => m.kook_channel_id === channelId)
}

const getMappingCount = (channelId) => {
  return mappings.value.filter(m => m.kook_channel_id === channelId).length
}

const getBotMappings = (botId) => {
  return mappings.value.filter(m => m.target_bot_id === botId)
}

const getBotMappingCount = (botId) => {
  return getBotMappings(botId).length
}

const getBotName = (botId) => {
  const bot = bots.value.find(b => b.id === botId)
  return bot ? bot.name : '未知'
}

const platformText = (platform) => {
  const texts = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  }
  return texts[platform] || platform
}

const platformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

const goToBots = () => {
  router.push('/bots')
}

const exportMappings = () => {
  const data = JSON.stringify(mappings.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mappings_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('映射已导出')
}

const importMappings = () => {
  // TODO: 实现导入功能
  ElMessage.info('导入功能开发中...')
}

// 生命周期
onMounted(async () => {
  await loadKookServers()
  await loadBots()
  await loadMappings()
  
  // 计算SVG画布大小
  if (editorContainer.value) {
    const rect = editorContainer.value.getBoundingClientRect()
    svgHeight.value = rect.height
  }
  
  // 初始化连接线
  await nextTick()
  updateConnectionLines()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (editorContainer.value) {
    const rect = editorContainer.value.getBoundingClientRect()
    svgHeight.value = rect.height
    updateConnectionLines()
  }
}

const loadKookServers = async () => {
  // TODO: 从API加载
}

const loadBots = async () => {
  // TODO: 从API加载
}

const loadMappings = async () => {
  // TODO: 从API加载
}
</script>

<style scoped lang="scss">
.mapping-visual-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #EBEEF5;
  
  .toolbar-left {
    h2 {
      margin: 0 0 5px 0;
      font-size: 24px;
    }
    
    .subtitle {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 10px;
  }
}

.editor-main {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr 350px;
  position: relative;
  overflow: hidden;
}

/* 左右面板通用样式 */
.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  background: #F5F7FA;
  border-right: 1px solid #EBEEF5;
}

.right-panel {
  border-right: none;
  border-left: 1px solid #EBEEF5;
}

.panel-header {
  padding: 20px;
  color: white;
  
  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
  }
}

.gradient-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

/* 左侧频道列表 */
.channels-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 10px;
  
  .server-icon {
    width: 30px;
    height: 30px;
    border-radius: 6px;
  }
  
  .server-icon-placeholder {
    width: 30px;
    height: 30px;
    border-radius: 6px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
  }
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin: 8px 0;
  background: white;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.3s;
  border: 2px solid transparent;
  
  &:hover {
    border-color: #409EFF;
    transform: translateX(5px);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }
  
  &:active {
    cursor: grabbing;
  }
  
  &.is-mapped {
    background: #F0F9FF;
    border-color: #67C23A;
  }
  
  .channel-drag-handle {
    color: #909399;
  }
  
  .channel-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 5px;
    
    .channel-name {
      font-weight: 500;
    }
  }
}

/* 右侧Bot列表 */
.bots-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bot-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 3px dashed transparent;
  transition: all 0.3s;
  
  &.is-drop-target {
    border-color: #67C23A;
    background: #F0F9FF;
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
    animation: pulse 1s infinite;
  }
  
  .bot-header {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    
    .bot-icon {
      width: 50px;
      height: 50px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: white;
      
      &.platform-discord {
        background: linear-gradient(135deg, #5865F2 0%, #7289DA 100%);
      }
      
      &.platform-telegram {
        background: linear-gradient(135deg, #0088cc 0%, #00aaff 100%);
      }
      
      &.platform-feishu {
        background: linear-gradient(135deg, #00b96b 0%, #00d68f 100%);
      }
    }
    
    .bot-info {
      flex: 1;
      
      h4 {
        margin: 0 0 8px 0;
        font-size: 16px;
      }
    }
  }
  
  .bot-stats {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #EBEEF5;
    
    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 5px;
      
      .stat-label {
        font-size: 12px;
        color: #909399;
      }
      
      .stat-value {
        font-size: 18px;
        font-weight: 600;
        color: #409EFF;
      }
    }
  }
  
  .bot-mappings {
    .mappings-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 10px;
    }
    
    .mapping-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: #F5F7FA;
      border-radius: 6px;
      margin-bottom: 6px;
      font-size: 13px;
    }
  }
  
  .drop-hint {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 30px;
    color: #C0C4CC;
    border: 2px dashed #DCDFE6;
    border-radius: 8px;
    
    .el-icon {
      font-size: 36px;
    }
  }
}

/* SVG连接线 */
.connection-svg {
  position: absolute;
  left: 350px;
  top: 0;
  pointer-events: none;
  z-index: 10;
}

.connection-line {
  pointer-events: stroke;
  cursor: pointer;
  transition: all 0.3s;
  
  &.line-hover {
    stroke-width: 5;
    filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.6));
  }
}

.connection-label {
  fill: #409EFF;
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
  
  .remove-hint {
    fill: #F56C6C;
    font-size: 10px;
  }
}

/* 底部预览面板 */
.preview-panel {
  background: white;
  border-top: 1px solid #EBEEF5;
  padding: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  h3 {
    margin: 0;
    font-size: 16px;
  }
  
  .preview-actions {
    display: flex;
    gap: 10px;
  }
}

.mapping-preview-list {
  .preview-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 12px;
    background: #FAFAFA;
    border-radius: 8px;
    margin-bottom: 10px;
    
    .preview-source,
    .preview-target {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .preview-arrow {
      color: #409EFF;
      font-size: 18px;
    }
    
    .preview-actions {
      margin-left: auto;
    }
  }
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}
</style>
