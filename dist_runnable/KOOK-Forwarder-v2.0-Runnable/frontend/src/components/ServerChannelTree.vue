<template>
  <div class="server-channel-tree">
    <!-- 搜索栏 -->
    <div class="tree-search">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索服务器或频道..."
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
        size="large"
      >
        <template #append>
          <el-button :icon="Refresh" @click="refreshTree" :loading="loading" />
        </template>
      </el-input>
    </div>
    
    <!-- 工具栏 -->
    <div class="tree-toolbar">
      <el-button-group size="small">
        <el-button :icon="Expand" @click="expandAll">展开</el-button>
        <el-button :icon="Fold" @click="collapseAll">折叠</el-button>
      </el-button-group>
      
      <el-button-group size="small">
        <el-button @click="selectAll">全选</el-button>
        <el-button @click="deselectAll">清空</el-button>
      </el-button-group>
      
      <el-dropdown @command="handleSort" trigger="click">
        <el-button size="small" :icon="Sort">
          排序
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="name">
              <el-icon><Sort /></el-icon>按名称
            </el-dropdown-item>
            <el-dropdown-item command="time">
              <el-icon><Clock /></el-icon>按时间
            </el-dropdown-item>
            <el-dropdown-item command="activity">
              <el-icon><TrendCharts /></el-icon>按活跃度
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <!-- 树形结构 -->
    <div class="tree-container" v-loading="loading">
      <el-tree
        ref="treeRef"
        :data="filteredServers"
        node-key="id"
        show-checkbox
        :props="treeProps"
        :default-expanded-keys="expandedKeys"
        :filter-node-method="filterNode"
        @check="handleCheck"
        @node-click="handleNodeClick"
        class="channel-tree"
        draggable
        @node-drop="handleDrop"
        :allow-drop="allowDrop"
        :allow-drag="allowDrag"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <!-- 图标 -->
            <el-icon class="node-icon" :color="getNodeColor(data)">
              <component :is="getNodeIcon(data)" />
            </el-icon>
            
            <!-- 名称 -->
            <span class="node-label" :class="{ 'is-server': data.type === 'server' }">
              {{ node.label }}
            </span>
            
            <!-- 频道类型标识 -->
            <el-tag 
              v-if="data.type === 'channel'"
              :type="getChannelTypeTag(data.channelType)"
              size="small"
              class="channel-type-tag"
            >
              {{ getChannelTypeText(data.channelType) }}
            </el-tag>
            
            <!-- 徽章 -->
            <el-badge 
              v-if="data.type === 'server' && data.channelCount"
              :value="data.channelCount"
              :max="99"
              class="channel-badge"
            />
            
            <!-- 状态指示器 -->
            <el-tooltip 
              v-if="data.status"
              :content="getStatusTooltip(data.status)"
              placement="top"
            >
              <div 
                class="status-indicator"
                :class="`status-${data.status}`"
              />
            </el-tooltip>
            
            <!-- 活跃度指示器 -->
            <el-tooltip 
              v-if="data.activity !== undefined"
              :content="`活跃度: ${data.activity}%`"
              placement="top"
            >
              <el-progress
                :percentage="data.activity"
                :show-text="false"
                :stroke-width="4"
                class="activity-progress"
                :color="getActivityColor(data.activity)"
              />
            </el-tooltip>
            
            <!-- 操作按钮 -->
            <div class="node-actions" @click.stop>
              <el-dropdown trigger="click" @command="handleNodeAction">
                <el-button
                  :icon="More"
                  circle
                  size="small"
                  text
                />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      :command="{ action: 'settings', data }"
                      :icon="Setting"
                    >
                      设置
                    </el-dropdown-item>
                    <el-dropdown-item 
                      v-if="data.type === 'channel'"
                      :command="{ action: 'test', data }"
                      :icon="Connection"
                    >
                      测试转发
                    </el-dropdown-item>
                    <el-dropdown-item 
                      :command="{ action: 'copy', data }"
                      :icon="CopyDocument"
                    >
                      复制ID
                    </el-dropdown-item>
                    <el-dropdown-item 
                      v-if="data.type === 'server'"
                      :command="{ action: 'refresh', data }"
                      :icon="Refresh"
                      divided
                    >
                      刷新频道
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
      </el-tree>
      
      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && filteredServers.length === 0"
        description="没有找到服务器或频道"
        :image-size="120"
      >
        <el-button type="primary" @click="refreshTree">
          刷新列表
        </el-button>
      </el-empty>
    </div>
    
    <!-- 统计信息 -->
    <div class="tree-stats">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-statistic title="服务器" :value="selectedServerCount">
            <template #suffix>/ {{ totalServerCount }}</template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="频道" :value="selectedChannelCount">
            <template #suffix>/ {{ totalChannelCount }}</template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="映射" :value="mappedChannelCount">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Expand, Fold, Sort, Refresh, Clock, TrendCharts,
  OfficeBuilding, ChatDotRound, Microphone, More, Setting,
  Connection, CopyDocument, CircleCheck, ArrowDown
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useClipboard } from '@vueuse/core'

// Props
const props = defineProps({
  accountId: {
    type: Number,
    default: null
  },
  selectable: {
    type: Boolean,
    default: true
  },
  draggableNodes: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['selection-change', 'node-click', 'node-drop'])

// Refs
const treeRef = ref(null)
const searchKeyword = ref('')
const loading = ref(false)
const servers = ref([])
const expandedKeys = ref([])
const sortBy = ref('name')

// 剪贴板
const { copy } = useClipboard()

// Tree props
const treeProps = {
  label: 'name',
  children: 'children',
  disabled: (data) => data.disabled || false
}

// 过滤后的服务器
const filteredServers = computed(() => {
  let result = servers.value
  
  // 搜索过滤
  if (searchKeyword.value) {
    result = filterServersRecursive(result, searchKeyword.value.toLowerCase())
  }
  
  // 排序
  result = sortServers(result, sortBy.value)
  
  return result
})

// 统计
const totalServerCount = computed(() => {
  return servers.value.length
})

const totalChannelCount = computed(() => {
  return servers.value.reduce((sum, server) => {
    return sum + (server.children?.length || 0)
  }, 0)
})

const selectedServerCount = computed(() => {
  if (!treeRef.value) return 0
  return treeRef.value.getCheckedNodes().filter(n => n.type === 'server').length
})

const selectedChannelCount = computed(() => {
  if (!treeRef.value) return 0
  return treeRef.value.getCheckedNodes().filter(n => n.type === 'channel').length
})

const mappedChannelCount = computed(() => {
  return servers.value.reduce((sum, server) => {
    return sum + (server.children?.filter(ch => ch.mapped).length || 0)
  }, 0)
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const response = await axios.get('/api/servers', {
      params: { account_id: props.accountId }
    })
    
    servers.value = transformServersData(response.data)
    
    // 默认展开所有服务器
    expandedKeys.value = servers.value.map(s => s.id)
    
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 转换服务器数据为树形结构
function transformServersData(data) {
  return data.map(server => ({
    id: `server-${server.id}`,
    name: server.name,
    type: 'server',
    serverId: server.id,
    channelCount: server.channels?.length || 0,
    status: server.status || 'online',
    activity: server.activity || 0,
    children: server.channels?.map(channel => ({
      id: `channel-${channel.id}`,
      name: channel.name,
      type: 'channel',
      channelType: channel.type,
      channelId: channel.id,
      serverId: server.id,
      mapped: channel.mapped || false,
      status: channel.status || 'active'
    })) || []
  }))
}

// 搜索过滤
function filterServersRecursive(items, keyword) {
  return items.map(item => {
    const children = item.children ? filterServersRecursive(item.children, keyword) : []
    
    const nameMatch = item.name.toLowerCase().includes(keyword)
    const hasMatchingChildren = children.length > 0
    
    if (nameMatch || hasMatchingChildren) {
      return {
        ...item,
        children
      }
    }
    
    return null
  }).filter(Boolean)
}

// 排序
function sortServers(items, sortKey) {
  const sorted = [...items]
  
  if (sortKey === 'name') {
    sorted.sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortKey === 'time') {
    sorted.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0))
  } else if (sortKey === 'activity') {
    sorted.sort((a, b) => (b.activity || 0) - (a.activity || 0))
  }
  
  // 递归排序子节点
  sorted.forEach(item => {
    if (item.children) {
      item.children = sortServers(item.children, sortKey)
    }
  })
  
  return sorted
}

// 节点图标
function getNodeIcon(data) {
  if (data.type === 'server') return OfficeBuilding
  if (data.channelType === 1) return ChatDotRound
  if (data.channelType === 2) return Microphone
  return ChatDotRound
}

// 节点颜色
function getNodeColor(data) {
  if (data.type === 'server') return '#409EFF'
  if (data.channelType === 1) return '#67C23A'
  if (data.channelType === 2) return '#E6A23C'
  return '#909399'
}

// 频道类型标签
function getChannelTypeTag(type) {
  return type === 1 ? 'success' : 'warning'
}

function getChannelTypeText(type) {
  return type === 1 ? '文字' : '语音'
}

// 状态提示
function getStatusTooltip(status) {
  const tooltips = {
    online: '在线',
    offline: '离线',
    error: '异常',
    active: '活跃',
    inactive: '不活跃'
  }
  return tooltips[status] || status
}

// 活跃度颜色
function getActivityColor(activity) {
  if (activity >= 80) return '#67C23A'
  if (activity >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 刷新树
async function refreshTree() {
  await loadData()
  ElMessage.success('刷新成功')
}

// 搜索处理
function handleSearch() {
  // 搜索时展开所有节点
  if (searchKeyword.value) {
    expandAll()
  }
}

// 展开所有
function expandAll() {
  const allKeys = []
  const collectKeys = (items) => {
    items.forEach(item => {
      allKeys.push(item.id)
      if (item.children) {
        collectKeys(item.children)
      }
    })
  }
  collectKeys(servers.value)
  expandedKeys.value = allKeys
}

// 折叠所有
function collapseAll() {
  expandedKeys.value = []
}

// 全选
function selectAll() {
  const allNodes = []
  const collectNodes = (items) => {
    items.forEach(item => {
      allNodes.push(item)
      if (item.children) {
        collectNodes(item.children)
      }
    })
  }
  collectNodes(servers.value)
  treeRef.value.setCheckedNodes(allNodes)
}

// 清空选择
function deselectAll() {
  treeRef.value.setCheckedKeys([])
}

// 排序处理
function handleSort(command) {
  sortBy.value = command
  ElMessage.info(`按${command === 'name' ? '名称' : command === 'time' ? '时间' : '活跃度'}排序`)
}

// 选择变化
function handleCheck() {
  const checked = treeRef.value.getCheckedNodes()
  emit('selection-change', checked)
}

// 节点点击
function handleNodeClick(data, node) {
  emit('node-click', { data, node })
}

// 节点操作
async function handleNodeAction({ action, data }) {
  switch (action) {
    case 'settings':
      // 打开设置对话框
      emit('node-settings', data)
      break
      
    case 'test':
      // 测试转发
      await testForward(data)
      break
      
    case 'copy':
      // 复制ID
      const id = data.channelId || data.serverId
      await copy(id)
      ElMessage.success('已复制到剪贴板')
      break
      
    case 'refresh':
      // 刷新服务器频道
      await refreshServerChannels(data)
      break
  }
}

// 测试转发
async function testForward(channelData) {
  try {
    const response = await axios.post('/api/test-forward', {
      channel_id: channelData.channelId
    })
    
    if (response.data.success) {
      ElMessage.success('测试消息已发送')
    } else {
      ElMessage.error('测试失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

// 刷新服务器频道
async function refreshServerChannels(serverData) {
  try {
    const response = await axios.post(`/api/servers/${serverData.serverId}/refresh`)
    
    if (response.data.success) {
      await loadData()
      ElMessage.success('频道列表已更新')
    }
  } catch (error) {
    ElMessage.error('刷新失败: ' + error.message)
  }
}

// 拖拽相关
function allowDrop(draggingNode, dropNode, type) {
  if (!props.draggableNodes) return false
  
  // 只允许同类型拖拽
  if (draggingNode.data.type !== dropNode.data.type) {
    return false
  }
  
  // 只允许inner类型
  return type === 'inner'
}

function allowDrag(draggingNode) {
  return props.draggableNodes && draggingNode.data.type === 'channel'
}

function handleDrop(draggingNode, dropNode, dropType) {
  emit('node-drop', { draggingNode, dropNode, dropType })
  
  // 保存新的排序
  saveNodeOrder()
}

async function saveNodeOrder() {
  try {
    const order = extractNodeOrder(servers.value)
    await axios.post('/api/servers/order', { order })
    ElMessage.success('排序已保存')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

function extractNodeOrder(items) {
  const order = []
  
  items.forEach((item, index) => {
    order.push({ id: item.id, order: index })
    
    if (item.children) {
      order.push(...extractNodeOrder(item.children))
    }
  })
  
  return order
}

// 过滤节点方法
function filterNode(value, data) {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

// 暴露方法
defineExpose({
  getCheckedNodes: () => treeRef.value?.getCheckedNodes() || [],
  setCheckedKeys: (keys) => treeRef.value?.setCheckedKeys(keys),
  refresh: loadData
})

// 初始化
loadData()
</script>

<style scoped>
.server-channel-tree {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.tree-search {
  margin-bottom: 16px;
}

.tree-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.tree-container {
  flex: 1;
  overflow-y: auto;
  min-height: 300px;
}

.channel-tree {
  background: transparent;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 8px;
}

.node-icon {
  font-size: 18px;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-label.is-server {
  font-weight: 600;
  font-size: 15px;
}

.channel-type-tag {
  font-size: 12px;
}

.channel-badge {
  margin-left: 4px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-online {
  background: #67C23A;
}

.status-offline {
  background: #909399;
}

.status-error {
  background: #F56C6C;
}

.activity-progress {
  width: 60px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.3s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.tree-stats {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* 自定义树节点样式 */
:deep(.el-tree-node__content) {
  height: 40px;
  padding: 0 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.el-tree-node__content:hover) {
  background: #f5f7fa;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: #ecf5ff;
}
</style>
