<template>
  <div class="mapping-visual-flow-container">
    <!-- 顶部工具栏 -->
    <div class="flow-toolbar">
      <div class="toolbar-left">
        <h2>
          <el-icon><Share /></el-icon>
          可视化频道映射
        </h2>
        <el-tag type="info">{{ mappingCount }}个映射</el-tag>
      </div>
      
      <div class="toolbar-right">
        <el-button-group>
          <el-button :icon="MagicStick" @click="smartMapping">智能映射</el-button>
          <el-button :icon="Refresh" @click="autoLayout">自动布局</el-button>
          <el-button :icon="ZoomIn" @click="zoomIn">放大</el-button>
          <el-button :icon="ZoomOut" @click="zoomOut">缩小</el-button>
          <el-button :icon="FullScreen" @click="fitView">适应窗口</el-button>
        </el-button-group>
        
        <el-button :icon="Upload" @click="importMappings">导入</el-button>
        <el-button :icon="Download" @click="exportMappings">导出</el-button>
        <el-button type="primary" :icon="Check" @click="saveMappings" :loading="saving">
          保存映射
        </el-button>
      </div>
    </div>
    
    <!-- 主编辑区域 -->
    <div class="flow-editor" v-loading="loading">
      <VueFlow
        v-model="elements"
        :default-zoom="0.8"
        :min-zoom="0.1"
        :max-zoom="2"
        @node-drag-stop="onNodeDragStop"
        @edge-click="onEdgeClick"
        @pane-click="onPaneClick"
        class="vue-flow"
      >
        <!-- 背景网格 -->
        <Background pattern-color="#aaa" :gap="16" />
        
        <!-- 控制器 -->
        <Controls />
        
        <!-- 小地图 -->
        <MiniMap />
        
        <!-- 自定义节点：KOOK频道 -->
        <template #node-kook="nodeProps">
          <div class="kook-node custom-node">
            <Handle type="source" :position="Position.Right" />
            
            <div class="node-header">
              <el-icon color="#409EFF"><OfficeBuilding /></el-icon>
              <span class="server-name">{{ nodeProps.data.serverName }}</span>
            </div>
            
            <div class="node-body">
              <div class="channel-item" v-for="channel in nodeProps.data.channels" :key="channel.id">
                <el-icon :size="14">
                  <ChatDotRound v-if="channel.type === 1" />
                  <Microphone v-else />
                </el-icon>
                <span># {{ channel.name }}</span>
              </div>
            </div>
            
            <div class="node-footer">
              <el-tag size="small">{{ nodeProps.data.channels.length }} 个频道</el-tag>
            </div>
          </div>
        </template>
        
        <!-- 自定义节点：目标Bot -->
        <template #node-target="nodeProps">
          <div class="target-node custom-node">
            <Handle type="target" :position="Position.Left" />
            
            <div class="node-header">
              <el-icon :color="getPlatformColor(nodeProps.data.platform)">
                <component :is="getPlatformIcon(nodeProps.data.platform)" />
              </el-icon>
              <span class="bot-name">{{ nodeProps.data.botName }}</span>
            </div>
            
            <div class="node-body">
              <el-tag :type="getPlatformTagType(nodeProps.data.platform)" size="small">
                {{ nodeProps.data.platform }}
              </el-tag>
              <div class="bot-status">
                <el-icon :color="nodeProps.data.online ? '#67C23A' : '#F56C6C'">
                  <CircleCheck v-if="nodeProps.data.online" />
                  <CircleClose v-else />
                </el-icon>
                <span>{{ nodeProps.data.online ? '在线' : '离线' }}</span>
              </div>
            </div>
            
            <div class="node-footer">
              <el-button size="small" :icon="Connection" @click="testBot(nodeProps.data)">
                测试
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- 自定义边：映射连接线 -->
        <template #edge-custom="edgeProps">
          <BaseEdge
            :id="edgeProps.id"
            :source-x="edgeProps.sourceX"
            :source-y="edgeProps.sourceY"
            :target-x="edgeProps.targetX"
            :target-y="edgeProps.targetY"
            :marker-end="edgeProps.markerEnd"
            :style="{
              stroke: edgeProps.data.active ? '#67C23A' : '#909399',
              strokeWidth: edgeProps.data.active ? 3 : 2
            }"
          />
          
          <!-- 边标签 -->
          <EdgeLabelRenderer>
            <div
              :style="{
                position: 'absolute',
                transform: `translate(-50%, -50%) translate(${edgeProps.labelX}px,${edgeProps.labelY}px)`,
              }"
              class="edge-label"
            >
              <el-tag size="small" closable @close="removeEdge(edgeProps.id)">
                映射
              </el-tag>
            </div>
          </EdgeLabelRenderer>
        </template>
      </VueFlow>
    </div>
    
    <!-- 右侧面板 -->
    <div class="side-panel" v-if="selectedNode">
      <el-card>
        <template #header>
          <div class="panel-header">
            <span>节点详情</span>
            <el-button :icon="Close" circle size="small" @click="selectedNode = null" />
          </div>
        </template>
        
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="类型">
            {{ selectedNode.type }}
          </el-descriptions-item>
          <el-descriptions-item label="名称">
            {{ selectedNode.data.name || selectedNode.data.botName }}
          </el-descriptions-item>
          <el-descriptions-item label="ID">
            {{ selectedNode.id }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="panel-actions">
          <el-button @click="editNode" block>编辑</el-button>
          <el-button @click="deleteNode" type="danger" block>删除</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { VueFlow, useVueFlow, Position, Handle, BaseEdge, EdgeLabelRenderer } from '@vueflow/core'
import { Background } from '@vueflow/background'
import { Controls } from '@vueflow/controls'
import { MiniMap } from '@vueflow/minimap'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Share, MagicStick, Refresh, ZoomIn, ZoomOut, FullScreen, Check,
  Upload, Download, Search, Expand, Fold, Sort, Setting, Close,
  OfficeBuilding, ChatDotRound, Microphone, Connection,
  CircleCheck, CircleClose
} from '@element-plus/icons-vue'
import axios from 'axios'

// Vue Flow实例
const { fitView, zoomIn, zoomOut, addNodes, addEdges, removeNodes, removeEdges } = useVueFlow()

// 状态
const elements = ref([])
const loading = ref(false)
const saving = ref(false)
const selectedNode = ref(null)
const searchKeyword = ref('')

// 映射数量
const mappingCount = computed(() => {
  return elements.value.filter(el => el.type === 'edge' || el.source).length
})

// 生命周期
onMounted(async () => {
  await loadData()
  setTimeout(() => fitView(), 100)
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // 并行加载KOOK服务器和Bot配置
    const [serversRes, botsRes, mappingsRes] = await Promise.all([
      axios.get('/api/servers'),
      axios.get('/api/bots'),
      axios.get('/api/mappings')
    ])
    
    // 转换为Flow节点和边
    const nodes = [
      ...createKookNodes(serversRes.data),
      ...createTargetNodes(botsRes.data)
    ]
    
    const edges = createEdgesFromMappings(mappingsRes.data)
    
    elements.value = [...nodes, ...edges]
    
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 创建KOOK节点
function createKookNodes(servers) {
  return servers.map((server, index) => ({
    id: `kook-${server.id}`,
    type: 'kook',
    position: { x: 50, y: index * 200 },
    data: {
      serverName: server.name,
      serverId: server.id,
      channels: server.channels
    }
  }))
}

// 创建目标节点
function createTargetNodes(bots) {
  return bots.map((bot, index) => ({
    id: `target-${bot.id}`,
    type: 'target',
    position: { x: 600, y: index * 150 },
    data: {
      botName: bot.name,
      botId: bot.id,
      platform: bot.platform,
      online: bot.status === 'active'
    }
  }))
}

// 从映射创建边
function createEdgesFromMappings(mappings) {
  return mappings.map(mapping => ({
    id: `edge-${mapping.id}`,
    source: `kook-${mapping.kook_server_id}`,
    target: `target-${mapping.target_bot_id}`,
    type: 'custom',
    data: {
      active: mapping.enabled,
      mappingId: mapping.id
    }
  }))
}

// 智能映射
async function smartMapping() {
  try {
    const response = await axios.get('/api/smart-mapping/suggest')
    const suggestions = response.data
    
    // 显示建议对话框
    const result = await ElMessageBox.confirm(
      `系统推荐创建${suggestions.length}个映射，是否应用？`,
      '智能映射建议',
      {
        confirmButtonText: '应用',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (result) {
      applySuggestions(suggestions)
      ElMessage.success('智能映射已应用')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('智能映射失败: ' + error.message)
    }
  }
}

// 应用映射建议
function applySuggestions(suggestions) {
  const newEdges = suggestions.map(sug => ({
    id: `edge-new-${Date.now()}-${Math.random()}`,
    source: `kook-${sug.kook_channel.server_id}`,
    target: `target-${sug.target_bot.id}`,
    type: 'custom',
    data: { active: true, suggested: true }
  }))
  
  addEdges(newEdges)
}

// 自动布局
function autoLayout() {
  // 使用dagre算法自动布局
  // 这里简化实现，实际需要集成dagre库
  
  const kookNodes = elements.value.filter(el => el.type === 'kook')
  const targetNodes = elements.value.filter(el => el.type === 'target')
  
  // 左侧排列KOOK节点
  kookNodes.forEach((node, index) => {
    node.position = { x: 50, y: index * 200 + 50 }
  })
  
  // 右侧排列目标节点
  targetNodes.forEach((node, index) => {
    node.position = { x: 700, y: index * 150 + 50 }
  })
  
  ElMessage.success('自动布局完成')
}

// 保存映射
async function saveMappings() {
  saving.value = true
  try {
    const mappings = extractMappingsFromEdges()
    
    await axios.post('/api/mappings/batch', { mappings })
    
    ElMessage.success('映射保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 从边提取映射数据
function extractMappingsFromEdges() {
  return elements.value
    .filter(el => el.source && el.target)
    .map(edge => ({
      kook_server_id: edge.source.replace('kook-', ''),
      target_bot_id: edge.target.replace('target-', ''),
      enabled: edge.data?.active !== false
    }))
}

// 导出映射
function exportMappings() {
  const data = JSON.stringify(extractMappingsFromEdges(), null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mappings-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('映射已导出')
}

// 导入映射
async function importMappings() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    try {
      const text = await file.text()
      const mappings = JSON.parse(text)
      
      // 创建边
      const newEdges = mappings.map(m => ({
        id: `edge-import-${Date.now()}-${Math.random()}`,
        source: `kook-${m.kook_server_id}`,
        target: `target-${m.target_bot_id}`,
        type: 'custom',
        data: { active: m.enabled }
      }))
      
      addEdges(newEdges)
      ElMessage.success(`导入了${newEdges.length}个映射`)
      
    } catch (error) {
      ElMessage.error('导入失败: ' + error.message)
    }
  }
  input.click()
}

// 平台图标
function getPlatformIcon(platform) {
  const iconMap = {
    discord: 'ChatDotRound',
    telegram: 'ChatLineRound',
    feishu: 'Message'
  }
  return iconMap[platform] || 'ChatDotRound'
}

// 平台颜色
function getPlatformColor(platform) {
  const colorMap = {
    discord: '#5865F2',
    telegram: '#0088cc',
    feishu: '#00b96b'
  }
  return colorMap[platform] || '#409EFF'
}

// 平台标签类型
function getPlatformTagType(platform) {
  const typeMap = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return typeMap[platform] || 'info'
}

// 测试Bot
async function testBot(botData) {
  try {
    const response = await axios.post(`/api/bots/${botData.botId}/test`)
    
    if (response.data.success) {
      ElMessage.success(`${botData.botName} 测试成功`)
    } else {
      ElMessage.error(`${botData.botName} 测试失败: ${response.data.message}`)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

// 删除边
function removeEdge(edgeId) {
  removeEdges([edgeId])
  ElMessage.info('映射已删除')
}

// 节点点击
function onPaneClick() {
  selectedNode.value = null
}

// 边点击
function onEdgeClick({ edge }) {
  ElMessageBox.confirm(
    '确定要删除此映射吗？',
    '删除映射',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    removeEdge(edge.id)
  }).catch(() => {})
}

// 节点拖拽停止
function onNodeDragStop({ node }) {
  // 可以在这里保存节点位置
  console.log('Node dragged:', node.id, node.position)
}
</script>

<style scoped>
.mapping-visual-flow-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.flow-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-left h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.flow-editor {
  flex: 1;
  position: relative;
}

.vue-flow {
  background: #fafafa;
}

/* 自定义节点样式 */
.custom-node {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  min-width: 240px;
  transition: all 0.3s;
}

.custom-node:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.kook-node {
  border: 2px solid #409EFF;
}

.target-node {
  border: 2px solid #67C23A;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  font-weight: bold;
}

.node-body {
  padding: 12px 16px;
  max-height: 200px;
  overflow-y: auto;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 0;
  font-size: 14px;
  color: #606266;
}

.node-footer {
  padding: 8px 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bot-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 8px;
}

.edge-label {
  pointer-events: all;
}

/* 侧边面板 */
.side-panel {
  position: absolute;
  right: 20px;
  top: 80px;
  width: 300px;
  z-index: 10;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .flow-toolbar {
    flex-direction: column;
    gap: 12px;
  }
  
  .toolbar-left, .toolbar-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .side-panel {
    position: static;
    width: 100%;
    margin-top: 20px;
  }
}
</style>

<style>
/* Vue Flow样式覆盖 */
@import '@vueflow/core/dist/style.css';
@import '@vueflow/core/dist/theme-default.css';
@import '@vueflow/controls/dist/style.css';
@import '@vueflow/minimap/dist/style.css';
@import '@vueflow/background/dist/style.css';
</style>
