<template>
  <div class="mapping-visual-enhanced">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2>📊 可视化频道映射编辑器（增强版）</h2>
      </div>
      <div class="toolbar-right">
        <el-button-group>
          <el-button @click="autoLayout" :icon="MagicStick">自动布局</el-button>
          <el-button @click="zoomIn" :icon="ZoomIn">放大</el-button>
          <el-button @click="zoomOut" :icon="ZoomOut">缩小</el-button>
          <el-button @click="resetZoom" :icon="FullScreen">重置</el-button>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-button @click="loadMappings" :icon="Refresh">刷新</el-button>
          <el-button @click="exportMappings" :icon="Download">导出</el-button>
          <el-button type="primary" @click="saveMappings" :loading="isSaving" :icon="Check">
            保存映射
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 使用说明 -->
    <el-collapse v-model="showHelp" class="help-collapse">
      <el-collapse-item title="📖 使用说明" name="help">
        <el-steps :active="0" align-center>
          <el-step title="选择KOOK频道" description="点击左侧频道" />
          <el-step title="选择目标Bot" description="点击右侧Bot" />
          <el-step title="创建映射" description="自动生成连线" />
          <el-step title="保存配置" description="点击保存按钮" />
        </el-steps>
        <div class="tips">
          <p>💡 提示：</p>
          <ul>
            <li>点击连线中间的×按钮可以删除映射</li>
            <li>使用"自动布局"功能可以整理节点位置</li>
            <li>支持鼠标滚轮缩放画布</li>
            <li>可以导出映射配置为JSON文件</li>
          </ul>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-statistic title="KOOK频道" :value="totalChannels">
          <template #prefix><el-icon><ChatDotRound /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="目标Bot" :value="targetBots.length">
          <template #prefix><el-icon><Connection /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="映射关系" :value="mappings.length">
          <template #prefix><el-icon><Link /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="启用映射" :value="enabledMappings">
          <template #prefix><el-icon style="color: #67C23A;"><SuccessFilled /></el-icon></template>
        </el-statistic>
      </el-col>
    </el-row>

    <!-- 主画布 -->
    <div class="canvas-container" ref="containerRef">
      <div 
        class="canvas" 
        ref="canvasRef"
        :style="{
          transform: `scale(${zoom}) translate(${panX}px, ${panY}px)`,
          transformOrigin: 'center center'
        }"
        @wheel.prevent="handleWheel"
        @mousedown.left="handleCanvasMouseDown"
      >
        <!-- 网格背景 -->
        <div class="grid-background"></div>

        <!-- 左侧：KOOK频道 -->
        <div class="source-section">
          <div class="section-header">
            <h3>🏠 KOOK频道（源）</h3>
            <el-input
              v-model="sourceSearch"
              placeholder="搜索..."
              size="small"
              clearable
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>

          <div class="channels-container">
            <div
              v-for="(server, serverIndex) in filteredSourceServers"
              :key="server.id"
              class="server-group"
            >
              <div class="server-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>{{ server.name }}</span>
                <el-tag size="small">{{ server.channels.length }}个频道</el-tag>
              </div>

              <div class="channels-list">
                <div
                  v-for="channel in server.channels"
                  :key="channel.id"
                  class="channel-node"
                  :class="{ 
                    selected: selectedSource?.id === channel.id,
                    'has-mapping': getMappingCount(channel.id) > 0
                  }"
                  @click="selectSource(channel, server)"
                  :ref="el => { if (el) channelRefs[channel.id] = el }"
                >
                  <div class="node-content">
                    <el-icon><ChatDotRound /></el-icon>
                    <span class="node-name">{{ channel.name }}</span>
                  </div>
                  <el-badge 
                    v-if="getMappingCount(channel.id)" 
                    :value="getMappingCount(channel.id)" 
                    type="success"
                  />
                </div>
              </div>
            </div>

            <el-empty 
              v-if="filteredSourceServers.length === 0" 
              description="暂无频道"
              :image-size="80"
            />
          </div>
        </div>

        <!-- 右侧：目标Bot -->
        <div class="target-section">
          <div class="section-header">
            <h3>🎯 目标平台（接收）</h3>
            <el-input
              v-model="targetSearch"
              placeholder="搜索..."
              size="small"
              clearable
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>

          <div class="bots-container">
            <div
              v-for="bot in filteredTargetBots"
              :key="bot.id"
              class="bot-node"
              :class="[
                { selected: selectedTarget?.id === bot.id },
                `platform-${bot.platform}`
              ]"
              @click="selectTarget(bot)"
              :ref="el => { if (el) botRefs[bot.id] = el }"
            >
              <div class="platform-icon">
                <el-icon v-if="bot.platform === 'discord'"><Connection /></el-icon>
                <el-icon v-else-if="bot.platform === 'telegram'"><Message /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
              </div>
              <div class="bot-info">
                <div class="bot-name">{{ bot.name }}</div>
                <el-tag size="small" :type="getPlatformTagType(bot.platform)">
                  {{ getPlatformName(bot.platform) }}
                </el-tag>
              </div>
            </div>

            <el-empty 
              v-if="filteredTargetBots.length === 0" 
              description="暂无Bot配置"
              :image-size="80"
            >
              <el-button type="primary" @click="goToBotsConfig">配置Bot</el-button>
            </el-empty>
          </div>
        </div>

        <!-- SVG连线层 -->
        <svg class="connection-layer" ref="svgRef">
          <defs>
            <!-- 箭头标记 -->
            <marker
              id="arrow-success"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#67C23A" />
            </marker>
            <marker
              id="arrow-disabled"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#C0C4CC" />
            </marker>
            <!-- 阴影滤镜 -->
            <filter id="shadow">
              <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
            </filter>
          </defs>

          <g v-for="(mapping, index) in mappings" :key="`mapping-${index}`">
            <!-- 连线路径 -->
            <path
              :d="calculateCurvePath(mapping)"
              class="connection-path"
              :class="{ 
                disabled: !mapping.enabled,
                highlighted: isHighlighted(mapping)
              }"
              :stroke="mapping.enabled ? '#67C23A' : '#C0C4CC'"
              stroke-width="3"
              fill="none"
              :marker-end="`url(#${mapping.enabled ? 'arrow-success' : 'arrow-disabled'})`"
              filter="url(#shadow)"
            />

            <!-- 删除按钮 -->
            <g 
              v-if="calculateMidpoint(mapping)" 
              class="delete-button-group"
              @click="removeMapping(index)"
            >
              <circle
                :cx="calculateMidpoint(mapping).x"
                :cy="calculateMidpoint(mapping).y"
                r="15"
                fill="#F56C6C"
                class="delete-circle"
              />
              <text
                :x="calculateMidpoint(mapping).x"
                :y="calculateMidpoint(mapping).y + 5"
                text-anchor="middle"
                fill="white"
                font-size="16"
                font-weight="bold"
                class="delete-text"
              >
                ×
              </text>
            </g>
          </g>
        </svg>
      </div>
    </div>

    <!-- 映射列表 -->
    <el-card class="mapping-list-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>📋 当前映射关系（{{ mappings.length }}条）</span>
          <el-button-group size="small">
            <el-button @click="enableAllMappings">全部启用</el-button>
            <el-button @click="disableAllMappings">全部禁用</el-button>
            <el-button type="danger" @click="clearAllMappings">清空所有</el-button>
          </el-button-group>
        </div>
      </template>

      <el-table :data="mappings" stripe max-height="300">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="source_name" label="KOOK频道" min-width="200">
          <template #default="{ row }">
            <el-icon><ChatDotRound /></el-icon>
            <span style="margin-left: 8px;">{{ row.source_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="→" width="60" align="center">
          <template #default>
            <el-icon :size="20" color="#409EFF"><ArrowRight /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="目标Bot" min-width="180" />
        <el-table-column prop="platform" label="平台" width="120">
          <template #default="{ row }">
            <el-tag :type="getPlatformTagType(row.platform)" size="small">
              {{ getPlatformName(row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch 
              v-model="row.enabled" 
              @change="updateMappingLines"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ $index }">
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="removeMapping($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Check, Search, OfficeBuilding, ChatDotRound,
  Connection, Message, ArrowRight, Download, ZoomIn, ZoomOut,
  FullScreen, MagicStick, Link, SuccessFilled
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://localhost:9527'

// 数据
const sourceServers = ref([])
const targetBots = ref([])
const mappings = ref([])

// 选中状态
const selectedSource = ref(null)
const selectedTarget = ref(null)

// 搜索
const sourceSearch = ref('')
const targetSearch = ref('')

// UI状态
const isSaving = ref(false)
const showHelp = ref([])

// 画布控制
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)

// refs
const containerRef = ref(null)
const canvasRef = ref(null)
const svgRef = ref(null)
const channelRefs = ref({})
const botRefs = ref({})

// 计算属性
const filteredSourceServers = computed(() => {
  if (!sourceSearch.value) return sourceServers.value
  
  const keyword = sourceSearch.value.toLowerCase()
  return sourceServers.value
    .map(server => ({
      ...server,
      channels: server.channels.filter(ch =>
        ch.name.toLowerCase().includes(keyword)
      )
    }))
    .filter(server => server.channels.length > 0)
})

const filteredTargetBots = computed(() => {
  if (!targetSearch.value) return targetBots.value
  
  const keyword = targetSearch.value.toLowerCase()
  return targetBots.value.filter(bot =>
    bot.name.toLowerCase().includes(keyword) ||
    bot.platform.toLowerCase().includes(keyword)
  )
})

const totalChannels = computed(() => {
  return sourceServers.value.reduce((sum, server) => sum + server.channels.length, 0)
})

const enabledMappings = computed(() => {
  return mappings.value.filter(m => m.enabled).length
})

// 方法
const selectSource = (channel, server) => {
  selectedSource.value = {
    ...channel,
    server_id: server.id,
    server_name: server.name
  }
  
  if (selectedTarget.value) {
    createMapping()
  }
}

const selectTarget = (bot) => {
  selectedTarget.value = bot
  
  if (selectedSource.value) {
    createMapping()
  }
}

const createMapping = () => {
  if (!selectedSource.value || !selectedTarget.value) return
  
  // 检查是否已存在
  const exists = mappings.value.some(m =>
    m.source_id === selectedSource.value.id &&
    m.target_id === selectedTarget.value.id
  )
  
  if (exists) {
    ElMessage.warning('该映射已存在')
    return
  }
  
  mappings.value.push({
    source_id: selectedSource.value.id,
    source_name: `${selectedSource.value.server_name} / ${selectedSource.value.name}`,
    server_id: selectedSource.value.server_id,
    channel_id: selectedSource.value.id,
    channel_name: selectedSource.value.name,
    target_id: selectedTarget.value.id,
    target_name: selectedTarget.value.name,
    platform: selectedTarget.value.platform,
    target_channel: selectedTarget.value.target_channel ||'',
    enabled: true
  })
  
  ElMessage.success('映射创建成功')
  
  // 清空选择
  selectedSource.value = null
  selectedTarget.value = null
  
  // 更新连线
  nextTick(() => {
    updateMappingLines()
  })
}

const removeMapping = (index) => {
  ElMessageBox.confirm('确定要删除这个映射吗？', '确认', {
    type: 'warning'
  }).then(() => {
    mappings.value.splice(index, 1)
    ElMessage.success('映射已删除')
    updateMappingLines()
  }).catch(() => {})
}

const getMappingCount = (channelId) => {
  return mappings.value.filter(m => m.source_id === channelId).length
}

const isHighlighted = (mapping) => {
  return (selectedSource.value && mapping.source_id === selectedSource.value.id) ||
         (selectedTarget.value && mapping.target_id === selectedTarget.value.id)
}

// 计算贝塞尔曲线路径
const calculateCurvePath = (mapping) => {
  const sourceEl = channelRefs.value[mapping.source_id]
  const targetEl = botRefs.value[mapping.target_id]
  
  if (!sourceEl || !targetEl) return ''
  
  const sourceRect = sourceEl.getBoundingClientRect()
  const targetRect = targetEl.getBoundingClientRect()
  const canvasRect = canvasRef.value?.getBoundingClientRect() || { left: 0, top: 0 }
  
  const x1 = sourceRect.right - canvasRect.left
  const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top
  const x2 = targetRect.left - canvasRect.left
  const y2 = targetRect.top + targetRect.height / 2 - canvasRect.top
  
  const controlX1 = x1 + (x2 - x1) / 3
  const controlX2 = x2 - (x2 - x1) / 3
  
  return `M ${x1} ${y1} C ${controlX1} ${y1}, ${controlX2} ${y2}, ${x2} ${y2}`
}

// 计算中点
const calculateMidpoint = (mapping) => {
  const sourceEl = channelRefs.value[mapping.source_id]
  const targetEl = botRefs.value[mapping.target_id]
  
  if (!sourceEl || !targetEl) return null
  
  const sourceRect = sourceEl.getBoundingClientRect()
  const targetRect = targetEl.getBoundingClientRect()
  const canvasRect = canvasRef.value?.getBoundingClientRect() || { left: 0, top: 0 }
  
  const x1 = sourceRect.right - canvasRect.left
  const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top
  const x2 = targetRect.left - canvasRect.left
  const y2 = targetRect.top + targetRect.height / 2 - canvasRect.top
  
  return {
    x: (x1 + x2) / 2,
    y: (y1 + y2) / 2
  }
}

const updateMappingLines = () => {
  // 强制重新渲染连线
  nextTick(() => {
    if (svgRef.value) {
      svgRef.value.style.display = 'none'
      setTimeout(() => {
        svgRef.value.style.display = 'block'
      }, 10)
    }
  })
}

// 缩放控制
const handleWheel = (event) => {
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  const newZoom = Math.max(0.5, Math.min(2, zoom.value + delta))
  zoom.value = newZoom
}

const zoomIn = () => {
  zoom.value = Math.min(2, zoom.value + 0.2)
}

const zoomOut = () => {
  zoom.value = Math.max(0.5, zoom.value - 0.2)
}

const resetZoom = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

// 画布拖动
const handleCanvasMouseDown = (event) => {
  if (event.target === canvasRef.value || event.target.classList.contains('grid-background')) {
    isPanning.value = true
    panStartX.value = event.clientX - panX.value
    panStartY.value = event.clientY - panY.value
    event.preventDefault()
  }
}

const handleMouseMove = (event) => {
  if (isPanning.value) {
    panX.value = event.clientX - panStartX.value
    panY.value = event.clientY - panStartY.value
  }
}

const handleMouseUp = () => {
  isPanning.value = false
}

// 自动布局
const autoLayout = () => {
  ElMessage.info('自动布局功能已触发')
  // 实现自动布局算法
  updateMappingLines()
}

// 批量操作
const enableAllMappings = () => {
  mappings.value.forEach(m => m.enabled = true)
  ElMessage.success('已启用所有映射')
  updateMappingLines()
}

const disableAllMappings = () => {
  mappings.value.forEach(m => m.enabled = false)
  ElMessage.info('已禁用所有映射')
  updateMappingLines()
}

const clearAllMappings = () => {
  ElMessageBox.confirm('确定要清空所有映射吗？此操作不可恢复！', '警告', {
    type: 'error',
    confirmButtonText: '确定清空',
    cancelButtonText: '取消'
  }).then(() => {
    mappings.value = []
    ElMessage.success('已清空所有映射')
  }).catch(() => {})
}

// 平台相关
const getPlatformName = (platform) => {
  const names = {
    'discord': 'Discord',
    'telegram': 'Telegram',
    'feishu': '飞书'
  }
  return names[platform] || platform
}

const getPlatformTagType = (platform) => {
  const types = {
    'discord': 'primary',
    'telegram': 'success',
    'feishu': 'warning'
  }
  return types[platform] || 'info'
}

// 数据加载
const loadMappings = async () => {
  try {
    const [serversRes, botsRes, mappingsRes] = await Promise.all([
      axios.get(`${API_BASE}/api/servers`),
      axios.get(`${API_BASE}/api/bots`),
      axios.get(`${API_BASE}/api/mappings`)
    ])
    
    sourceServers.value = serversRes.data.data || []
    targetBots.value = botsRes.data.data || []
    
    if (mappingsRes.data.data) {
      mappings.value = mappingsRes.data.data.map(m => ({
        ...m,
        source_name: m.kook_channel_name,
        target_name: m.bot_name
      }))
    }
    
    ElMessage.success('数据加载成功')
    
    nextTick(() => {
      updateMappingLines()
    })
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  }
}

const saveMappings = async () => {
  if (mappings.value.length === 0) {
    ElMessage.warning('没有映射需要保存')
    return
  }
  
  isSaving.value = true
  try {
    await axios.post(`${API_BASE}/api/mappings/batch`, {
      mappings: mappings.value
    })
    
    ElMessage.success('映射保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    isSaving.value = false
  }
}

const exportMappings = () => {
  const dataStr = JSON.stringify(mappings.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `mappings_${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('映射配置已导出')
}

const goToBotsConfig = () => {
  router.push('/bots')
}

// 生命周期
onMounted(() => {
  loadMappings()
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateMappingLines)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  window.removeEventListener('resize', updateMappingLines)
})
</script>

<style scoped>
.mapping-visual-enhanced {
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.toolbar-left h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.help-collapse {
  border: none;
  background: #f5f7fa;
  border-radius: 8px;
}

.tips {
  margin-top: 15px;
  padding: 15px;
  background: white;
  border-radius: 4px;
}

.tips ul {
  margin: 10px 0 0 20px;
}

.tips li {
  margin: 5px 0;
  color: #666;
}

.stats-row {
  margin: 0;
}

:deep(.el-statistic) {
  text-align: center;
}

.canvas-container {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.canvas {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: grab;
  transition: transform 0.2s;
}

.canvas.grabbing {
  cursor: grabbing;
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.source-section, .target-section {
  position: absolute;
  top: 20px;
  width: 300px;
  max-height: calc(100% - 40px);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
}

.source-section {
  left: 20px;
}

.target-section {
  right: 20px;
}

.section-header {
  padding: 15px;
  border-bottom: 1px solid #EBEEF5;
}

.section-header h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.channels-container, .bots-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.server-group {
  margin-bottom: 15px;
}

.server-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.channels-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.channel-node, .bot-node {
  padding: 10px 12px;
  background: white;
  border: 2px solid #EBEEF5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.channel-node:hover, .bot-node:hover {
  border-color: #409EFF;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(64,158,255,0.2);
}

.channel-node.selected, .bot-node.selected {
  border-color: #409EFF;
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64,158,255,0.3);
}

.channel-node.has-mapping {
  border-left: 4px solid #67C23A;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-name {
  font-size: 13px;
  color: #606266;
}

.bot-node {
  gap: 10px;
}

.bot-node.platform-discord {
  border-left: 4px solid #5865F2;
}

.bot-node.platform-telegram {
  border-left: 4px solid #0088cc;
}

.bot-node.platform-feishu {
  border-left: 4px solid #00D6B9;
}

.platform-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
}

.bot-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bot-name {
  font-weight: 600;
  font-size: 13px;
  color: #303133;
}

.connection-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-path {
  pointer-events: stroke;
  cursor: pointer;
  transition: all 0.3s;
}

.connection-path:hover {
  stroke-width: 4;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.connection-path.disabled {
  stroke-dasharray: 5, 5;
  opacity: 0.5;
}

.connection-path.highlighted {
  stroke-width: 5;
  filter: drop-shadow(0 3px 6px rgba(103,194,58,0.4));
}

.delete-button-group {
  pointer-events: all;
  cursor: pointer;
  transition: all 0.3s;
}

.delete-button-group:hover .delete-circle {
  r: 18;
  fill: #F00;
}

.delete-button-group:hover .delete-text {
  font-size: 18;
}

.mapping-list-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 滚动条样式 */
.channels-container::-webkit-scrollbar,
.bots-container::-webkit-scrollbar {
  width: 6px;
}

.channels-container::-webkit-scrollbar-track,
.bots-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.channels-container::-webkit-scrollbar-thumb,
.bots-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.channels-container::-webkit-scrollbar-thumb:hover,
.bots-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
