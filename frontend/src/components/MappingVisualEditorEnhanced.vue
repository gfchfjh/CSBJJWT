<!--
  可视化映射编辑器（增强版）
  ✅ P1-2优化：SVG贝塞尔曲线连接线
-->
<template>
  <div class="visual-editor-enhanced" ref="editorRef">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <h3>🎨 拖拽式映射编辑器</h3>
        <el-tag type="info" effect="plain">
          从左侧拖动KOOK频道到右侧Bot卡片
        </el-tag>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="clearAllMappings" :disabled="mappings.length === 0">
          <el-icon><Delete /></el-icon>
          清空所有映射
        </el-button>
        <el-button type="primary" @click="saveMappings" :loading="saving">
          <el-icon><Check /></el-icon>
          保存映射
        </el-button>
      </div>
    </div>
    
    <!-- 主编辑区域 -->
    <div class="editor-main">
      <!-- 左侧：KOOK频道列表 -->
      <div class="kook-channels-panel">
        <div class="panel-header">
          <h4>📱 KOOK频道（源）</h4>
          <el-button size="small" @click="loadKookChannels" :loading="loadingChannels">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        
        <div class="channels-list" v-loading="loadingChannels">
          <div v-if="kookServers.length === 0" class="empty-state">
            <el-empty description="暂无KOOK服务器">
              <el-button type="primary" @click="$router.push('/accounts')">
                添加KOOK账号
              </el-button>
            </el-empty>
          </div>
          
          <el-collapse v-else v-model="expandedServers">
            <el-collapse-item
              v-for="server in kookServers"
              :key="server.id"
              :name="server.id"
            >
              <template #title>
                <div class="server-title">
                  <el-icon><Folder /></el-icon>
                  <span>{{ server.name }}</span>
                  <el-tag size="small" type="info">
                    {{ server.channels?.length || 0 }}个频道
                  </el-tag>
                </div>
              </template>
              
              <div class="channels-container">
                <div
                  v-for="channel in server.channels"
                  :key="channel.id"
                  :data-channel-id="channel.id"
                  :data-server-id="server.id"
                  class="channel-item"
                  draggable="true"
                  @dragstart="handleDragStart($event, server, channel)"
                  @dragend="handleDragEnd"
                >
                  <el-icon><ChatLineSquare /></el-icon>
                  <span class="channel-name">{{ channel.name }}</span>
                  <el-icon class="drag-handle"><Rank /></el-icon>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      
      <!-- 中间：SVG连接线画布 -->
      <svg
        class="connection-canvas"
        ref="svgRef"
        @mousemove="updateDragLine"
      >
        <!-- 静态连接线（已建立的映射） -->
        <path
          v-for="(mapping, index) in mappings"
          :key="`mapping-${index}`"
          :d="getConnectionPath(mapping)"
          class="connection-line"
          :class="{
            active: hoveredMapping === index,
            'same-source': getSameSourceCount(mapping.source_channel_id) > 1
          }"
          :stroke="getConnectionColor(mapping)"
          @mouseenter="hoveredMapping = index"
          @mouseleave="hoveredMapping = null"
          @click="selectMapping(index)"
        />
        
        <!-- 拖拽时的临时连接线 -->
        <path
          v-if="dragging && dragLineEndPos"
          :d="getDragLinePath()"
          class="connection-line dragging"
          stroke="#409EFF"
          stroke-dasharray="5,5"
        />
      </svg>
      
      <!-- 右侧：目标平台Bot列表 -->
      <div class="target-bots-panel">
        <div class="panel-header">
          <h4>🎯 目标平台（接收）</h4>
          <el-button size="small" @click="loadTargetBots" :loading="loadingBots">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        
        <div class="bots-list" v-loading="loadingBots">
          <div v-if="targetBots.length === 0" class="empty-state">
            <el-empty description="暂无配置Bot">
              <el-button type="primary" @click="$router.push('/bots')">
                配置Bot
              </el-button>
            </el-empty>
          </div>
          
          <div
            v-for="bot in targetBots"
            :key="bot.id"
            :data-bot-id="bot.id"
            class="bot-card"
            :class="{ 'drop-target': isDragOverBot === bot.id }"
            @drop="handleDrop($event, bot)"
            @dragover.prevent="handleDragOver($event, bot)"
            @dragleave="handleDragLeave"
          >
            <div class="bot-header">
              <el-icon :size="24" :color="getPlatformColor(bot.platform)">
                <component :is="getPlatformIcon(bot.platform)" />
              </el-icon>
              <div class="bot-info">
                <h4>{{ bot.name }}</h4>
                <el-tag :type="getPlatformTagType(bot.platform)" size="small">
                  {{ bot.platform }}
                </el-tag>
              </div>
            </div>
            
            <div class="bot-mappings">
              <el-tag
                v-for="mapping in getBotMappings(bot.id)"
                :key="mapping.id"
                size="small"
                closable
                @close="removeMapping(mapping)"
              >
                {{ mapping.source_channel_name }}
              </el-tag>
              
              <div v-if="getBotMappings(bot.id).length === 0" class="drop-hint">
                <el-icon><Plus /></el-icon>
                <span>拖拽频道到此</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部：映射预览 -->
    <div class="mapping-preview">
      <div class="preview-header">
        <h4>📋 已配置的映射（{{ mappings.length }}）</h4>
        <el-button-group size="small">
          <el-button @click="exportMappings">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button @click="importMappings">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </el-button-group>
      </div>
      
      <div class="preview-content">
        <el-table
          :data="mappings"
          size="small"
          max-height="200"
          stripe
        >
          <el-table-column label="序号" type="index" width="60" />
          <el-table-column label="KOOK服务器" prop="source_server_name" width="150" />
          <el-table-column label="KOOK频道" prop="source_channel_name" width="150" />
          <el-table-column label="目标平台" prop="target_platform" width="100">
            <template #default="{ row }">
              <el-tag :type="getPlatformTagType(row.target_platform)" size="small">
                {{ row.target_platform }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="目标Bot" prop="target_bot_name" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button
                size="small"
                type="danger"
                link
                @click="removeMapping(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Folder,
  ChatLineSquare,
  Rank,
  Refresh,
  Delete,
  Check,
  Plus,
  Download,
  Upload
} from '@element-plus/icons-vue'
import api from '@/api'

const editorRef = ref(null)
const svgRef = ref(null)

// 数据
const kookServers = ref([])
const targetBots = ref([])
const mappings = ref([])

// 加载状态
const loadingChannels = ref(false)
const loadingBots = ref(false)
const saving = ref(false)

// UI状态
const expandedServers = ref([])
const hoveredMapping = ref(null)
const selectedMapping = ref(null)
const isDragOverBot = ref(null)

// 拖拽状态
const dragging = ref(false)
const dragData = ref(null)
const dragLineStartPos = ref(null)
const dragLineEndPos = ref(null)

// 加载KOOK频道
const loadKookChannels = async () => {
  loadingChannels.value = true
  try {
    const accounts = await api.get('/api/accounts/')
    
    if (!accounts || accounts.length === 0) {
      ElMessage.warning('请先添加KOOK账号')
      return
    }
    
    // 获取第一个在线账号
    const onlineAccount = accounts.find(a => a.status === 'online')
    if (!onlineAccount) {
      ElMessage.warning('没有在线的KOOK账号')
      return
    }
    
    // 获取服务器列表
    const servers = await api.get(`/api/accounts/${onlineAccount.id}/servers`)
    
    // 为每个服务器加载频道
    const serversWithChannels = []
    for (const server of servers) {
      try {
        const channels = await api.get(`/api/accounts/${onlineAccount.id}/servers/${server.id}/channels`)
        serversWithChannels.push({
          ...server,
          channels: channels || []
        })
      } catch (error) {
        console.error(`加载服务器${server.id}的频道失败:`, error)
        serversWithChannels.push({
          ...server,
          channels: []
        })
      }
    }
    
    kookServers.value = serversWithChannels
    
    // 自动展开第一个服务器
    if (serversWithChannels.length > 0) {
      expandedServers.value = [serversWithChannels[0].id]
    }
    
  } catch (error) {
    ElMessage.error('加载KOOK频道失败: ' + error.message)
  } finally {
    loadingChannels.value = false
  }
}

// 加载目标Bot
const loadTargetBots = async () => {
  loadingBots.value = true
  try {
    const bots = await api.get('/api/bots/')
    targetBots.value = bots || []
  } catch (error) {
    ElMessage.error('加载Bot列表失败: ' + error.message)
  } finally {
    loadingBots.value = false
  }
}

// 拖拽开始
const handleDragStart = (event, server, channel) => {
  dragging.value = true
  dragData.value = {
    server,
    channel
  }
  
  // 获取拖拽起点坐标
  const channelEl = event.target
  const rect = channelEl.getBoundingClientRect()
  const editorRect = editorRef.value.getBoundingClientRect()
  
  dragLineStartPos.value = {
    x: rect.right - editorRect.left,
    y: rect.top + rect.height / 2 - editorRect.top
  }
  
  // 设置拖拽数据
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('application/json', JSON.stringify({
    server_id: server.id,
    server_name: server.name,
    channel_id: channel.id,
    channel_name: channel.name
  }))
}

// 拖拽结束
const handleDragEnd = () => {
  dragging.value = false
  dragData.value = null
  dragLineStartPos.value = null
  dragLineEndPos.value = null
}

// 更新拖拽线条
const updateDragLine = (event) => {
  if (!dragging.value || !dragLineStartPos.value) return
  
  const editorRect = editorRef.value.getBoundingClientRect()
  dragLineEndPos.value = {
    x: event.clientX - editorRect.left,
    y: event.clientY - editorRect.top
  }
}

// 拖拽悬停在Bot上
const handleDragOver = (event, bot) => {
  event.preventDefault()
  isDragOverBot.value = bot.id
}

// 离开Bot
const handleDragLeave = () => {
  isDragOverBot.value = null
}

// 放置到Bot上
const handleDrop = (event, bot) => {
  event.preventDefault()
  isDragOverBot.value = null
  
  try {
    const data = JSON.parse(event.dataTransfer.getData('application/json'))
    
    // 检查是否已存在相同映射
    const exists = mappings.value.some(m => 
      m.source_channel_id === data.channel_id && 
      m.target_bot_id === bot.id
    )
    
    if (exists) {
      ElMessage.warning('该映射已存在')
      return
    }
    
    // 添加映射
    const newMapping = {
      id: Date.now(),
      source_server_id: data.server_id,
      source_server_name: data.server_name,
      source_channel_id: data.channel_id,
      source_channel_name: data.channel_name,
      target_bot_id: bot.id,
      target_bot_name: bot.name,
      target_platform: bot.platform,
      enabled: true
    }
    
    mappings.value.push(newMapping)
    
    ElMessage.success(`已创建映射：${data.channel_name} → ${bot.name}`)
    
    // 触发SVG重新渲染
    nextTick(() => {
      updateSvgSize()
    })
    
  } catch (error) {
    console.error('处理拖拽失败:', error)
  } finally {
    dragging.value = false
    dragLineStartPos.value = null
    dragLineEndPos.value = null
  }
}

// ✅ P1-2核心：计算贝塞尔曲线路径
const getConnectionPath = (mapping) => {
  try {
    // 查找源频道元素
    const sourceEl = editorRef.value?.querySelector(
      `[data-channel-id="${mapping.source_channel_id}"]`
    )
    
    // 查找目标Bot元素
    const targetEl = editorRef.value?.querySelector(
      `[data-bot-id="${mapping.target_bot_id}"]`
    )
    
    if (!sourceEl || !targetEl || !editorRef.value) {
      return ''
    }
    
    const editorRect = editorRef.value.getBoundingClientRect()
    const sourceRect = sourceEl.getBoundingClientRect()
    const targetRect = targetEl.getBoundingClientRect()
    
    // 计算起点和终点坐标（相对于编辑器）
    const x1 = sourceRect.right - editorRect.left
    const y1 = sourceRect.top + sourceRect.height / 2 - editorRect.top
    const x2 = targetRect.left - editorRect.left
    const y2 = targetRect.top + targetRect.height / 2 - editorRect.top
    
    // 贝塞尔曲线控制点（使用三次贝塞尔曲线，更平滑）
    const distance = x2 - x1
    const cx1 = x1 + distance * 0.4
    const cy1 = y1
    const cx2 = x1 + distance * 0.6
    const cy2 = y2
    
    return `M ${x1},${y1} C ${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}`
    
  } catch (error) {
    console.error('计算连接路径失败:', error)
    return ''
  }
}

// 计算拖拽线路径
const getDragLinePath = () => {
  if (!dragLineStartPos.value || !dragLineEndPos.value) return ''
  
  const x1 = dragLineStartPos.value.x
  const y1 = dragLineStartPos.value.y
  const x2 = dragLineEndPos.value.x
  const y2 = dragLineEndPos.value.y
  
  const distance = x2 - x1
  const cx1 = x1 + distance * 0.4
  const cy1 = y1
  const cx2 = x1 + distance * 0.6
  const cy2 = y2
  
  return `M ${x1},${y1} C ${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}`
}

// 获取连接线颜色（根据平台）
const getConnectionColor = (mapping) => {
  const colors = {
    discord: '#5865F2',
    telegram: '#0088cc',
    feishu: '#00b96b'
  }
  return colors[mapping.target_platform] || '#409EFF'
}

// 获取平台图标
const getPlatformIcon = (platform) => {
  // 这里可以导入特定平台的图标组件
  return ChatLineSquare
}

// 获取平台颜色
const getPlatformColor = (platform) => {
  const colors = {
    discord: '#5865F2',
    telegram: '#0088cc',
    feishu: '#00b96b'
  }
  return colors[platform] || '#409EFF'
}

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'info',
    feishu: 'success'
  }
  return types[platform] || 'info'
}

// 获取Bot的映射列表
const getBotMappings = (botId) => {
  return mappings.value.filter(m => m.target_bot_id === botId)
}

// 获取相同源的映射数量（用于检测一对多）
const getSameSourceCount = (channelId) => {
  return mappings.value.filter(m => m.source_channel_id === channelId).length
}

// 选择映射
const selectMapping = (index) => {
  selectedMapping.value = index
}

// 删除映射
const removeMapping = (mapping) => {
  const index = mappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    mappings.value.splice(index, 1)
    ElMessage.success('映射已删除')
    nextTick(() => {
      updateSvgSize()
    })
  }
}

// 清空所有映射
const clearAllMappings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有映射吗？此操作不可撤销。',
      '确认清空',
      {
        type: 'warning',
        confirmButtonText: '清空',
        cancelButtonText: '取消'
      }
    )
    
    mappings.value = []
    ElMessage.success('已清空所有映射')
  } catch {
    // 用户取消
  }
}

// 保存映射
const saveMappings = async () => {
  if (mappings.value.length === 0) {
    ElMessage.warning('没有映射需要保存')
    return
  }
  
  saving.value = true
  try {
    // 转换为API格式
    const apiMappings = mappings.value.map(m => ({
      kook_server_id: m.source_server_id,
      kook_channel_id: m.source_channel_id,
      kook_channel_name: m.source_channel_name,
      target_platform: m.target_platform,
      target_bot_id: m.target_bot_id,
      enabled: m.enabled
    }))
    
    await api.post('/api/mappings/batch', { mappings: apiMappings })
    
    ElMessage.success(`成功保存 ${mappings.value.length} 个映射`)
  } catch (error) {
    ElMessage.error('保存映射失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 导出映射
const exportMappings = () => {
  const json = JSON.stringify(mappings.value, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mappings-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('映射已导出')
}

// 导入映射
const importMappings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const imported = JSON.parse(event.target.result)
        if (Array.isArray(imported)) {
          mappings.value = imported
          ElMessage.success(`成功导入 ${imported.length} 个映射`)
          nextTick(() => {
            updateSvgSize()
          })
        } else {
          ElMessage.error('文件格式不正确')
        }
      } catch (error) {
        ElMessage.error('导入失败: ' + error.message)
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

// 更新SVG画布大小
const updateSvgSize = () => {
  if (!svgRef.value || !editorRef.value) return
  
  const rect = editorRef.value.getBoundingClientRect()
  svgRef.value.setAttribute('width', rect.width)
  svgRef.value.setAttribute('height', rect.height)
}

// 窗口大小改变时更新SVG
let resizeObserver = null

onMounted(() => {
  loadKookChannels()
  loadTargetBots()
  
  // 监听窗口大小变化
  resizeObserver = new ResizeObserver(() => {
    updateSvgSize()
  })
  
  if (editorRef.value) {
    resizeObserver.observe(editorRef.value)
  }
  
  // 初始化SVG大小
  nextTick(() => {
    updateSvgSize()
  })
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.visual-editor-enhanced {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

/* 工具栏 */
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(to right, #f5f7fa, #ffffff);
  border-radius: 8px;
  border: 1px solid #DCDFE6;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

/* 主编辑区 */
.editor-main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  position: relative;
  min-height: 400px;
}

/* 左侧面板 */
.kook-channels-panel {
  display: flex;
  flex-direction: column;
  background: white;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
}

.channels-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.channels-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 0;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: white;
  border: 2px solid #E4E7ED;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.3s;
  user-select: none;
}

.channel-item:hover {
  border-color: #409EFF;
  background: #ECF5FF;
  transform: translateX(5px);
}

.channel-item:active {
  cursor: grabbing;
}

.channel-name {
  flex: 1;
  font-weight: 500;
}

.drag-handle {
  color: #909399;
  cursor: grab;
}

/* SVG画布 */
.connection-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-line {
  fill: none;
  stroke-width: 2;
  transition: all 0.3s;
  pointer-events: stroke;
  cursor: pointer;
}

.connection-line:hover,
.connection-line.active {
  stroke-width: 3;
  filter: drop-shadow(0 0 4px currentColor);
}

.connection-line.same-source {
  stroke-dasharray: 5, 3;
}

.connection-line.dragging {
  stroke-width: 2;
  opacity: 0.6;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

/* 右侧面板 */
.target-bots-panel {
  display: flex;
  flex-direction: column;
  background: white;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  z-index: 2;
}

.bots-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bot-card {
  padding: 15px;
  background: white;
  border: 2px dashed #DCDFE6;
  border-radius: 8px;
  transition: all 0.3s;
  min-height: 100px;
}

.bot-card:hover {
  border-color: #409EFF;
  background: #F5F7FA;
}

.bot-card.drop-target {
  border-color: #67C23A;
  background: #F0F9FF;
  border-style: solid;
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.3);
}

.bot-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.bot-info h4 {
  margin: 0 0 5px 0;
  font-size: 15px;
}

.bot-mappings {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  align-items: center;
}

.drop-hint {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 13px;
}

/* 底部预览 */
.mapping-preview {
  background: white;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  padding: 15px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.preview-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.preview-content {
  max-height: 200px;
  overflow-y: auto;
}

/* 空状态 */
.empty-state {
  padding: 40px;
  text-align: center;
}

/* 响应式 */
@media (max-width: 1200px) {
  .editor-main {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .connection-canvas {
    display: none;
  }
}
</style>
