<template>
  <!-- ✅ P1-2优化: 智能映射向导组件 -->
  <div class="smart-mapping-wizard">
    <el-steps :active="currentStep" align-center style="margin-bottom: 30px;">
      <el-step title="选择源频道" icon="Folder" />
      <el-step title="智能匹配" icon="MagicStick" />
      <el-step title="预览确认" icon="View" />
      <el-step title="完成" icon="CircleCheck" />
    </el-steps>

    <!-- 步骤1: 选择源频道 -->
    <div v-show="currentStep === 0" class="step-content">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #title>
          请选择需要转发的KOOK频道
        </template>
        <p>系统将自动在Discord/Telegram/飞书中查找相似名称的频道并建立映射关系</p>
      </el-alert>

      <el-tree
        ref="channelTree"
        :data="kookServersTree"
        show-checkbox
        node-key="id"
        :props="{ label: 'name', children: 'channels' }"
        default-expand-all
      >
        <template #default="{ node, data }">
          <span class="tree-node-label">
            <el-icon v-if="!data.channels">
              <ChatDotSquare />
            </el-icon>
            <el-icon v-else>
              <Folder />
            </el-icon>
            {{ data.name }}
            <el-tag v-if="data.channels" size="small" type="info">
              {{ data.channels.length }}个频道
            </el-tag>
          </span>
        </template>
      </el-tree>

      <div class="step-actions">
        <el-space :size="10">
          <el-button @click="selectAll">全选</el-button>
          <el-button @click="selectNone">全不选</el-button>
        </el-space>
        <el-button 
          type="primary" 
          @click="startSmartMapping"
          :disabled="selectedChannelsCount === 0"
        >
          下一步：开始智能匹配 ({{ selectedChannelsCount }}个频道)
        </el-button>
      </div>
    </div>

    <!-- 步骤2: 智能匹配中 -->
    <div v-show="currentStep === 1" class="step-content">
      <el-result icon="loading" title="正在智能匹配...">
        <template #sub-title>
          <p>正在分析 {{ selectedChannelsCount }} 个频道</p>
          <p>预计耗时: {{ estimatedTime }}秒</p>
        </template>
      </el-result>

      <!-- 实时进度 -->
      <el-progress 
        :percentage="matchingProgress" 
        :status="matchingProgress === 100 ? 'success' : ''"
        style="margin: 20px 0;"
      >
        <template #default="{ percentage }">
          <span style="font-size: 16px;">{{ percentage }}%</span>
          <span style="margin-left: 10px; font-size: 12px; color: #909399;">
            {{ matchedCount }}/{{ selectedChannelsCount }} 已完成
          </span>
        </template>
      </el-progress>

      <el-alert type="info" :closable="false">
        <template #title>
          匹配原理
        </template>
        <ul style="margin: 5px 0; padding-left: 20px;">
          <li>分析KOOK频道名称（如"公告"、"更新"）</li>
          <li>在目标平台查找相似名称</li>
          <li>计算相似度并排序</li>
          <li>自动建立最佳匹配</li>
        </ul>
      </el-alert>
    </div>

    <!-- 步骤3: 预览映射结果 -->
    <div v-show="currentStep === 2" class="step-content">
      <el-alert
        :type="matchedCount > 0 ? 'success' : 'warning'"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #title>
          智能匹配完成：成功匹配 <strong>{{ matchedCount }}</strong> 个频道，
          未匹配 <strong>{{ unmatchedCount }}</strong> 个
        </template>
      </el-alert>

      <!-- 匹配结果表格 -->
      <el-table :data="smartMappingResults" border max-height="500">
        <el-table-column label="KOOK频道" width="220" fixed>
          <template #default="{ row }">
            <div class="channel-info">
              <el-icon><ChatDotSquare /></el-icon>
              <span>{{ row.kook_server_name }}</span>
              <el-icon style="margin: 0 4px;"><Right /></el-icon>
              <strong>{{ row.kook_channel_name }}</strong>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="匹配目标" min-width="350">
          <template #default="{ row }">
            <div v-if="row.matched_targets && row.matched_targets.length > 0">
              <el-tag
                v-for="target in row.matched_targets"
                :key="target.id"
                :type="getSimilarityTagType(target.similarity)"
                style="margin: 2px;"
              >
                <div style="display: flex; align-items: center; gap: 4px;">
                  <span>{{ getPlatformIcon(target.platform) }}</span>
                  <span>{{ target.platform }}</span>
                  <el-divider direction="vertical" />
                  <span>{{ target.channel_name }}</span>
                  <el-divider direction="vertical" />
                  <span style="color: #67C23A; font-weight: bold;">
                    {{ target.similarity }}%
                  </span>
                </div>
              </el-tag>
            </div>
            <el-tag v-else type="info">
              <el-icon><WarningFilled /></el-icon>
              未找到匹配
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.matched_targets && row.matched_targets.length > 0 ? 'success' : 'warning'">
              {{ row.matched_targets && row.matched_targets.length > 0 ? '✅ 已匹配' : '⚠️ 需手动' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-space :size="5">
              <el-button 
                size="small" 
                @click="editMapping(row)"
              >
                <el-icon><Edit /></el-icon>
                调整
              </el-button>
              <el-button 
                v-if="!row.matched_targets || row.matched_targets.length === 0"
                size="small" 
                type="primary"
                @click="manualMatch(row)"
              >
                <el-icon><Plus /></el-icon>
                手动配置
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="step-actions">
        <el-button @click="currentStep = 0">
          <el-icon><Back /></el-icon>
          返回重新选择
        </el-button>
        <el-button 
          type="primary" 
          @click="confirmSmartMapping"
          :disabled="matchedCount === 0"
        >
          <el-icon><CircleCheck /></el-icon>
          确认并保存映射 ({{ matchedCount }}个)
        </el-button>
      </div>
    </div>

    <!-- 步骤4: 完成 -->
    <div v-show="currentStep === 3" class="step-content">
      <el-result icon="success" title="🎉 智能映射完成！">
        <template #sub-title>
          <p>成功创建 <strong>{{ savedMappingsCount }}</strong> 个频道映射</p>
          <p style="margin-top: 10px;">您现在可以启动转发服务了</p>
        </template>
        <template #extra>
          <el-space :size="15">
            <el-button type="primary" size="large" @click="handleFinish">
              <el-icon><Select /></el-icon>
              完成
            </el-button>
            <el-button size="large" @click="handleViewMappings">
              <el-icon><View /></el-icon>
              查看所有映射
            </el-button>
          </el-space>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Folder, ChatDotSquare, MagicStick, View, CircleCheck,
  WarningFilled, Edit, Plus, Back, Right, Select
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['finish', 'cancel'])

const currentStep = ref(0)
const channelTree = ref(null)
const kookServersTree = ref([])
const selectedChannelsCount = ref(0)
const matchingProgress = ref(0)
const matchedCount = ref(0)
const unmatchedCount = ref(0)
const smartMappingResults = ref([])
const savedMappingsCount = ref(0)

const estimatedTime = computed(() => {
  return Math.ceil(selectedChannelsCount.value * 0.5) // 每个频道约0.5秒
})

onMounted(() => {
  loadKookServers()
})

// 加载KOOK服务器和频道
const loadKookServers = async () => {
  try {
    // 这里应该调用API获取实际数据
    // 示例数据
    kookServersTree.value = [
      {
        id: 'server1',
        name: '游戏公告服务器',
        channels: [
          { id: 'ch1', name: '公告频道', type: 'text', server_id: 'server1', server_name: '游戏公告服务器' },
          { id: 'ch2', name: '活动频道', type: 'text', server_id: 'server1', server_name: '游戏公告服务器' },
          { id: 'ch3', name: '更新日志', type: 'text', server_id: 'server1', server_name: '游戏公告服务器' }
        ]
      },
      {
        id: 'server2',
        name: '技术交流服务器',
        channels: [
          { id: 'ch4', name: '技术讨论', type: 'text', server_id: 'server2', server_name: '技术交流服务器' }
        ]
      }
    ]
  } catch (error) {
    ElMessage.error('加载服务器失败: ' + error.message)
  }
}

// 全选
const selectAll = () => {
  if (channelTree.value) {
    channelTree.value.setCheckedNodes(getAllChannels())
    updateSelectedCount()
  }
}

// 全不选
const selectNone = () => {
  if (channelTree.value) {
    channelTree.value.setCheckedKeys([])
    updateSelectedCount()
  }
}

// 获取所有频道节点
const getAllChannels = () => {
  const channels = []
  kookServersTree.value.forEach(server => {
    if (server.channels) {
      channels.push(...server.channels)
    }
  })
  return channels
}

// 更新选中数量
const updateSelectedCount = () => {
  if (channelTree.value) {
    const checked = channelTree.value.getCheckedNodes()
    selectedChannelsCount.value = checked.filter(n => !n.channels).length
  }
}

// 开始智能匹配
const startSmartMapping = async () => {
  const selectedChannels = channelTree.value.getCheckedNodes().filter(n => !n.channels)
  selectedChannelsCount.value = selectedChannels.length

  if (selectedChannelsCount.value === 0) {
    ElMessage.warning('请至少选择一个频道')
    return
  }

  currentStep.value = 1
  matchingProgress.value = 0
  matchedCount.value = 0

  try {
    // 调用智能映射API
    const response = await api.post('/api/smart-mapping/auto', {
      kook_channels: selectedChannels.map(ch => ({
        id: ch.id,
        name: ch.name,
        server_id: ch.server_id,
        server_name: ch.server_name
      }))
    })

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (matchingProgress.value < 90) {
        matchingProgress.value += 10
        matchedCount.value = Math.floor((matchingProgress.value / 100) * selectedChannelsCount.value)
      }
    }, 200)

    // 等待API响应
    await new Promise(resolve => setTimeout(resolve, 2000))

    clearInterval(progressInterval)
    matchingProgress.value = 100
    matchedCount.value = response.matched_count || 0
    unmatchedCount.value = response.unmatched_count || 0
    smartMappingResults.value = response.results || []

    currentStep.value = 2
  } catch (error) {
    ElMessage.error('智能匹配失败: ' + error.message)
    currentStep.value = 0
  }
}

// 获取相似度标签类型
const getSimilarityTagType = (similarity) => {
  if (similarity >= 90) return 'success'
  if (similarity >= 70) return 'warning'
  return 'info'
}

// 获取平台图标
const getPlatformIcon = (platform) => {
  const icons = {
    'discord': '💬',
    'telegram': '✈️',
    'feishu': '🏢'
  }
  return icons[platform] || '📱'
}

// 编辑映射
const editMapping = (row) => {
  ElMessage.info('编辑功能开发中...')
}

// 手动匹配
const manualMatch = (row) => {
  ElMessage.info('手动配置功能开发中...')
}

// 确认智能映射
const confirmSmartMapping = async () => {
  try {
    // 保存所有匹配的映射
    const mappingsToSave = smartMappingResults.value
      .filter(r => r.matched_targets && r.matched_targets.length > 0)
      .flatMap(r => 
        r.matched_targets.map(target => ({
          kook_server_id: r.kook_server_id,
          kook_channel_id: r.kook_channel_id,
          kook_channel_name: r.kook_channel_name,
          target_platform: target.platform,
          target_bot_id: target.bot_id,
          target_channel_id: target.channel_id,
          similarity: target.similarity
        }))
      )

    await api.post('/api/mappings/batch', {
      mappings: mappingsToSave
    })

    savedMappingsCount.value = mappingsToSave.length
    currentStep.value = 3

    ElMessage.success(`成功保存 ${mappingsToSave.length} 个映射`)
  } catch (error) {
    ElMessage.error('保存映射失败: ' + error.message)
  }
}

// 完成
const handleFinish = () => {
  emit('finish')
}

// 查看所有映射
const handleViewMappings = () => {
  emit('finish')
  // 跳转到映射列表
}
</script>

<style scoped>
.smart-mapping-wizard {
  padding: 20px;
}

.step-content {
  min-height: 400px;
  margin-top: 20px;
}

.tree-node-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.step-actions {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}
</style>
