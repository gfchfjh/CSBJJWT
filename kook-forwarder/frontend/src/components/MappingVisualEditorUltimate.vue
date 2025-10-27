<template>
  <div class="mapping-editor-ultimate">
    <!-- 三栏布局 -->
    <div class="editor-layout">
      <!-- 左栏: KOOK频道 -->
      <div class="column source-column">
        <div class="column-header">
          <h3><el-icon><Coin /></el-icon> KOOK频道</h3>
          <el-input
            v-model="sourceSearch"
            placeholder="搜索频道..."
            :prefix-icon="Search"
            size="small"
            clearable
          />
        </div>
        
        <div class="channel-list">
          <div
            v-for="channel in filteredSourceChannels"
            :key="channel.id"
            class="channel-item source-item"
            :class="{ active: sourceActive === channel.id }"
            draggable="true"
            @dragstart="handleDragStart(channel, $event)"
            @dragend="handleDragEnd"
            @mouseenter="handleSourceHover(channel)"
            @mouseleave="handleSourceLeave"
          >
            <el-icon><ChatLineSquare /></el-icon>
            <span class="channel-name">{{ channel.name }}</span>
            <el-tag v-if="getMappingCount(channel.id) > 0" size="small" type="success">
              {{ getMappingCount(channel.id) }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <!-- 中间: SVG画布 -->
      <div class="column canvas-column" ref="canvasRef">
        <svg
          class="mapping-canvas"
          :width="canvasWidth"
          :height="canvasHeight"
        >
          <!-- 定义渐变色 -->
          <defs>
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
          
          <!-- 绘制所有映射连线 -->
          <g v-for="(mapping, index) in visibleMappings" :key="index">
            <path
              :d="calculateBezierPath(mapping)"
              :stroke="mapping.isOneToMany ? '#E6A23C' : 'url(#lineGradient)'"
              :stroke-width="mapping.isActive ? 3 : 2"
              fill="none"
              :stroke-dasharray="mapping.isOneToMany ? '5,5' : 'none'"
              marker-end="url(#arrowhead)"
              class="mapping-line"
              :class="{ active: mapping.isActive }"
              @mouseenter="handleLineHover(mapping)"
              @mouseleave="handleLineLeave"
            />
            
            <!-- 置信度标签 -->
            <text
              v-if="mapping.confidence"
              :x="(mapping.sourceX + mapping.targetX) / 2"
              :y="(mapping.sourceY + mapping.targetY) / 2 - 10"
              text-anchor="middle"
              class="confidence-label"
              :class="getConfidenceLevelClass(mapping.confidence)"
            >
              {{ (mapping.confidence * 100).toFixed(0) }}%
            </text>
          </g>
        </svg>
      </div>
      
      <!-- 右栏: 目标Bot -->
      <div class="column target-column">
        <div class="column-header">
          <h3><el-icon><Connection /></el-icon> 目标Bot</h3>
          <el-input
            v-model="targetSearch"
            placeholder="搜索Bot..."
            :prefix-icon="Search"
            size="small"
            clearable
          />
        </div>
        
        <div class="bot-list">
          <div
            v-for="bot in filteredTargetBots"
            :key="bot.id"
            class="bot-item"
            :class="{ 'drop-target': dropTarget === bot.id }"
            @dragover.prevent="handleDragOver(bot, $event)"
            @dragleave="handleDragLeave"
            @drop="handleDrop(bot, $event)"
          >
            <div class="bot-header">
              <el-icon :size="24">
                <component :is="getPlatformIcon(bot.platform)" />
              </el-icon>
              <div class="bot-info">
                <div class="bot-name">{{ bot.name }}</div>
                <el-tag size="small" :type="getPlatformTagType(bot.platform)">
                  {{ bot.platform }}
                </el-tag>
              </div>
            </div>
            
            <div class="bot-channels" v-if="bot.channels && bot.channels.length > 0">
              <div
                v-for="channel in bot.channels"
                :key="channel.id"
                class="target-channel-item"
                :data-channel-id="channel.id"
                :data-bot-id="bot.id"
              >
                <el-icon><ChatDotSquare /></el-icon>
                <span>{{ channel.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 映射预览面板 -->
    <el-card class="preview-panel" shadow="hover">
      <template #header>
        <div class="panel-header">
          <span><el-icon><View /></el-icon> 映射预览（共 {{ mappings.length }} 条）</span>
          <div class="panel-actions">
            <el-button size="small" :icon="MagicStick" @click="autoMapping">
              智能映射
            </el-button>
            <el-button size="small" :icon="Delete" type="danger" @click="clearAllMappings">
              清空映射
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="mappings" stripe max-height="200">
        <el-table-column label="KOOK频道" width="200">
          <template #default="{ row }">
            <el-tag>{{ row.source_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="→" width="50" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.isOneToMany" color="#E6A23C"><Share /></el-icon>
            <el-icon v-else color="#409EFF"><Right /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="目标Bot" width="150">
          <template #default="{ row }">
            <el-tag :type="getPlatformTagType(row.platform)">
              {{ row.bot_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标频道" width="200">
          <template #default="{ row }">
            {{ row.target_name }}
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="120">
          <template #default="{ row }">
            <el-progress
              v-if="row.confidence"
              :percentage="row.confidence * 100"
              :color="getConfidenceColor(row.confidence)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row, $index }">
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="removeMapping($index)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Coin,
  Connection,
  Search,
  ChatLineSquare,
  ChatDotSquare,
  View,
  MagicStick,
  Delete,
  Share,
  Right
} from '@element-plus/icons-vue'
import api from '@/api'

// 状态
const sourceChannels = ref([])
const targetBots = ref([])
const mappings = ref([])
const sourceSearch = ref('')
const targetSearch = ref('')
const sourceActive = ref(null)
const dropTarget = ref(null)
const canvasRef = ref(null)
const canvasWidth = ref(600)
const canvasHeight = ref(800)

// 拖拽状态
const draggingChannel = ref(null)

// 计算属性
const filteredSourceChannels = computed(() => {
  if (!sourceSearch.value) return sourceChannels.value
  
  return sourceChannels.value.filter(channel =>
    channel.name.toLowerCase().includes(sourceSearch.value.toLowerCase())
  )
})

const filteredTargetBots = computed(() => {
  if (!targetSearch.value) return targetBots.value
  
  return targetBots.value.filter(bot =>
    bot.name.toLowerCase().includes(targetSearch.value.toLowerCase()) ||
    bot.channels.some(ch => ch.name.toLowerCase().includes(targetSearch.value.toLowerCase()))
  )
})

const visibleMappings = computed(() => {
  // 计算每个映射的坐标
  return mappings.value.map(mapping => {
    const sourceEl = document.querySelector(`[data-channel-id="${mapping.source_id}"]`)
    const targetEl = document.querySelector(`[data-channel-id="${mapping.target_id}"]`)
    
    if (!sourceEl || !targetEl || !canvasRef.value) {
      return { ...mapping, visible: false }
    }
    
    const canvasRect = canvasRef.value.getBoundingClientRect()
    const sourceRect = sourceEl.getBoundingClientRect()
    const targetRect = targetEl.getBoundingClientRect()
    
    return {
      ...mapping,
      visible: true,
      sourceX: sourceRect.right - canvasRect.left,
      sourceY: sourceRect.top + sourceRect.height / 2 - canvasRect.top,
      targetX: targetRect.left - canvasRect.left,
      targetY: targetRect.top + targetRect.height / 2 - canvasRect.top,
      isActive: sourceActive.value === mapping.source_id
    }
  }).filter(m => m.visible)
})

// 方法
const calculateBezierPath = (mapping) => {
  /**
   * 计算SVG贝塞尔曲线路径（✨ P0-6核心算法）
   * 使用三次贝塞尔曲线实现平滑连接
   */
  const { sourceX, sourceY, targetX, targetY } = mapping
  
  // 控制点：水平距离的1/3和2/3处
  const cx1 = sourceX + (targetX - sourceX) / 3
  const cy1 = sourceY
  const cx2 = targetX - (targetX - sourceX) / 3
  const cy2 = targetY
  
  return `M ${sourceX} ${sourceY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${targetX} ${targetY}`
}

const handleDragStart = (channel, event) => {
  draggingChannel.value = channel
  event.dataTransfer.effectAllowed = 'copy'
}

const handleDragEnd = () => {
  draggingChannel.value = null
  dropTarget.value = null
}

const handleDragOver = (bot, event) => {
  event.preventDefault()
  dropTarget.value = bot.id
}

const handleDragLeave = () => {
  dropTarget.value = null
}

const handleDrop = (bot, event) => {
  event.preventDefault()
  dropTarget.value = null
  
  if (!draggingChannel.value) return
  
  // 选择目标频道（如果bot有多个频道）
  if (bot.channels && bot.channels.length > 1) {
    // 弹出选择对话框
    selectTargetChannel(bot, draggingChannel.value)
  } else if (bot.channels && bot.channels.length === 1) {
    // 直接创建映射
    createMapping(draggingChannel.value, bot, bot.channels[0])
  } else {
    ElMessage.warning('该Bot没有可用的频道')
  }
  
  draggingChannel.value = null
}

const selectTargetChannel = async (bot, sourceChannel) => {
  try {
    const { value } = await ElMessageBox.prompt(
      '请选择目标频道',
      '创建映射',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'select',
        inputOptions: bot.channels.reduce((acc, ch) => {
          acc[ch.id] = ch.name
          return acc
        }, {})
      }
    )
    
    const targetChannel = bot.channels.find(ch => ch.id === value)
    if (targetChannel) {
      createMapping(sourceChannel, bot, targetChannel)
    }
  } catch {
    // 用户取消
  }
}

const createMapping = (sourceChannel, bot, targetChannel) => {
  // 检查是否已存在
  const exists = mappings.value.some(
    m => m.source_id === sourceChannel.id && m.target_id === targetChannel.id
  )
  
  if (exists) {
    ElMessage.warning('该映射已存在')
    return
  }
  
  // 检查是否一对多
  const isOneToMany = mappings.value.some(m => m.source_id === sourceChannel.id)
  
  mappings.value.push({
    source_id: sourceChannel.id,
    source_name: sourceChannel.name,
    target_id: targetChannel.id,
    target_name: targetChannel.name,
    bot_id: bot.id,
    bot_name: bot.name,
    platform: bot.platform,
    isOneToMany: isOneToMany,
    confidence: null
  })
  
  ElMessage.success('映射创建成功')
  
  // 更新画布
  nextTick(() => {
    updateCanvas()
  })
}

const removeMapping = (index) => {
  mappings.value.splice(index, 1)
  updateCanvas()
}

const clearAllMappings = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有映射吗？', '确认清空', {
      type: 'warning'
    })
    
    mappings.value = []
    ElMessage.info('已清空所有映射')
  } catch {
    // 用户取消
  }
}

const autoMapping = async () => {
  try {
    ElMessage.info('正在生成智能映射建议...')
    
    const response = await api.post('/api/smart-mapping-ultimate/suggest', {
      kook_channels: sourceChannels.value,
      target_channels: targetBots.value.flatMap(bot =>
        bot.channels.map(ch => ({
          ...ch,
          bot_id: bot.id,
          bot_name: bot.name,
          platform: bot.platform
        }))
      )
    })
    
    const suggestions = response.data
    
    if (suggestions.length === 0) {
      ElMessage.warning('未找到合适的映射建议')
      return
    }
    
    // 应用建议
    for (const suggestion of suggestions) {
      const exists = mappings.value.some(
        m => m.source_id === suggestion.source_channel_id &&
             m.target_id === suggestion.target_channel_id
      )
      
      if (!exists) {
        mappings.value.push({
          source_id: suggestion.source_channel_id,
          source_name: suggestion.source_channel_name,
          target_id: suggestion.target_channel_id,
          target_name: suggestion.target_channel_name,
          bot_id: suggestion.target_bot_id,
          platform: 'unknown',
          confidence: suggestion.confidence,
          isOneToMany: false
        })
      }
    }
    
    ElMessage.success(`已生成 ${suggestions.length} 条智能映射`)
    
    nextTick(() => {
      updateCanvas()
    })
  } catch (error) {
    console.error('智能映射失败:', error)
    ElMessage.error('智能映射失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleSourceHover = (channel) => {
  sourceActive.value = channel.id
}

const handleSourceLeave = () => {
  sourceActive.value = null
}

const handleLineHover = (mapping) => {
  // 高亮连线
}

const handleLineLeave = () => {
  // 取消高亮
}

const getMappingCount = (sourceId) => {
  return mappings.value.filter(m => m.source_id === sourceId).length
}

const getPlatformIcon = (platform) => {
  const icons = {
    discord: 'ChatLineSquare',
    telegram: 'ChatDotSquare',
    feishu: 'ChatRound'
  }
  return icons[platform] || 'ChatLineSquare'
}

const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

const getConfidenceLevelClass = (confidence) => {
  if (confidence >= 0.8) return 'high-confidence'
  if (confidence >= 0.5) return 'medium-confidence'
  return 'low-confidence'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.5) return '#E6A23C'
  return '#F56C6C'
}

const updateCanvas = () => {
  // 重新计算画布大小
  if (canvasRef.value) {
    canvasWidth.value = canvasRef.value.offsetWidth
    canvasHeight.value = canvasRef.value.offsetHeight
  }
}

const loadData = async () => {
  try {
    // 加载KOOK频道
    const channelsRes = await api.get('/api/accounts/channels')
    sourceChannels.value = channelsRes.data
    
    // 加载目标Bots
    const botsRes = await api.get('/api/bots/list')
    targetBots.value = botsRes.data
    
    // 加载已有映射
    const mappingsRes = await api.get('/api/mappings/list')
    mappings.value = mappingsRes.data
    
    nextTick(() => {
      updateCanvas()
    })
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateCanvas)
})
</script>

<style scoped>
.mapping-editor-ultimate {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.editor-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  gap: 20px;
  min-height: 0;
}

.column {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.column-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.column-header h3 {
  margin: 0 0 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
}

.channel-list,
.bot-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.channel-item,
.bot-item {
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f5f7fa;
}

.source-item:hover {
  background: #ecf5ff;
  transform: translateX(5px);
}

.source-item.active {
  background: #409eff;
  color: white;
}

.source-item[draggable="true"] {
  cursor: grab;
}

.source-item[draggable="true"]:active {
  cursor: grabbing;
}

.channel-name {
  flex: 1;
}

.bot-item {
  background: #f5f7fa;
  border: 2px dashed transparent;
}

.bot-item.drop-target {
  border-color: #67C23A;
  background: #f0f9ff;
}

.bot-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.bot-info {
  flex: 1;
}

.bot-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.bot-channels {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.target-channel-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  margin: 5px 0;
  background: white;
  border-radius: 6px;
  font-size: 13px;
}

/* SVG画布 */
.canvas-column {
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.mapping-canvas {
  width: 100%;
  height: 100%;
}

.mapping-line {
  transition: all 0.3s;
  cursor: pointer;
}

.mapping-line:hover {
  stroke-width: 4;
  filter: drop-shadow(0 0 5px rgba(64, 158, 255, 0.5));
}

.mapping-line.active {
  stroke-width: 4;
  filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.8));
}

.confidence-label {
  font-size: 12px;
  font-weight: bold;
  fill: #606266;
  pointer-events: none;
}

.high-confidence {
  fill: #67C23A;
}

.medium-confidence {
  fill: #E6A23C;
}

.low-confidence {
  fill: #F56C6C;
}

/* 预览面板 */
.preview-panel {
  height: 280px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-actions {
  display: flex;
  gap: 10px;
}

/* 暗黑模式 */
.dark .column {
  background: #2c2c2c;
}

.dark .source-item {
  background: #3a3a3a;
}

.dark .source-item:hover {
  background: #4a4a4a;
}

.dark .bot-item {
  background: #3a3a3a;
}

.dark .target-channel-item {
  background: #2c2c2c;
}

.dark .canvas-column {
  background: linear-gradient(135deg, #2c2c2c 0%, #3a3a3a 100%);
}
</style>
