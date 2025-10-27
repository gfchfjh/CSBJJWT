<template>
  <div class="draggable-mapping-view">
    <h2>🔀 拖拽式频道映射</h2>
    <p class="description">
      从左侧拖拽 KOOK 频道到右侧目标平台，即可建立映射关系
    </p>

    <el-row :gutter="20">
      <!-- 左侧：KOOK 频道列表 -->
      <el-col :span="10">
        <el-card class="source-panel">
          <template #header>
            <div class="panel-header">
              <span>📁 KOOK 频道（源）</span>
              <el-button size="small" @click="loadKookChannels">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <!-- 服务器筛选 -->
          <el-select
            v-model="selectedServerId"
            placeholder="选择服务器"
            style="width: 100%; margin-bottom: 15px"
            @change="handleServerChange"
          >
            <el-option
              v-for="server in kookServers"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>

          <!-- 可拖拽的频道列表 -->
          <draggable
            v-model="kookChannels"
            :group="{ name: 'channels', pull: 'clone', put: false }"
            :clone="cloneChannel"
            item-key="id"
            class="channel-list"
          >
            <template #item="{ element }">
              <div class="channel-item draggable-item">
                <el-icon>
                  <ChatDotRound v-if="element.type === 'text'" />
                  <Microphone v-else />
                </el-icon>
                <span class="channel-name">{{ element.name }}</span>
                <el-tag size="small" type="info">
                  拖我 →
                </el-tag>
              </div>
            </template>
          </draggable>

          <el-empty
            v-if="kookChannels.length === 0"
            description="请先选择服务器"
            :image-size="80"
          />
        </el-card>
      </el-col>

      <!-- 中间：智能匹配建议 -->
      <el-col :span="4" class="smart-match-col">
        <el-button
          type="primary"
          size="large"
          circle
          @click="handleSmartMatch"
          :loading="smartMatching"
        >
          <el-icon><MagicStick /></el-icon>
        </el-button>
        <p class="smart-match-text">智能匹配</p>
        
        <el-progress
          v-if="smartMatching"
          type="circle"
          :percentage="matchProgress"
          :width="80"
        />
      </el-col>

      <!-- 右侧：目标平台 -->
      <el-col :span="10">
        <el-card class="target-panel">
          <template #header>
            <div class="panel-header">
              <span>🎯 目标平台（接收）</span>
              <el-select
                v-model="targetPlatform"
                size="small"
                style="width: 150px"
                @change="loadTargetChannels"
              >
                <el-option label="Discord" value="discord" />
                <el-option label="Telegram" value="telegram" />
                <el-option label="飞书" value="feishu" />
              </el-select>
            </div>
          </template>

          <!-- 拖拽目标区域 -->
          <div class="drop-zones">
            <draggable
              v-model="mappings"
              :group="{ name: 'channels' }"
              item-key="id"
              class="mapping-list"
              @add="handleMappingAdd"
              @remove="handleMappingRemove"
            >
              <template #item="{ element }">
                <div class="mapping-card">
                  <div class="mapping-source">
                    <el-tag>KOOK</el-tag>
                    <span>{{ element.kook_channel_name }}</span>
                  </div>
                  <el-icon class="mapping-arrow"><Right /></el-icon>
                  <div class="mapping-target">
                    <el-select
                      v-model="element.target_channel_id"
                      placeholder="选择目标频道"
                      style="width: 100%"
                      @change="handleTargetSelect(element)"
                    >
                      <el-option
                        v-for="channel in targetChannels"
                        :key="channel.id"
                        :label="channel.name"
                        :value="channel.id"
                      />
                    </el-select>
                  </div>
                  <el-button
                    type="danger"
                    size="small"
                    circle
                    @click="handleRemoveMapping(element)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
            </draggable>

            <!-- 空状态 -->
            <div v-if="mappings.length === 0" class="drop-zone-empty">
              <el-icon class="drop-icon"><Download /></el-icon>
              <p>拖拽左侧频道到此处</p>
              <p class="hint">或点击"智能匹配"自动建立映射</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作栏 -->
    <div class="actions">
      <el-button @click="handlePreview">
        <el-icon><View /></el-icon>
        预览映射
      </el-button>
      <el-button type="success" @click="handleSave" :disabled="mappings.length === 0">
        <el-icon><Check /></el-icon>
        保存全部（{{ mappings.length }} 条）
      </el-button>
      <el-button type="warning" @click="handleClear">
        <el-icon><Delete /></el-icon>
        清空
      </el-button>
    </div>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="映射预览" width="70%">
      <el-table :data="mappings" border>
        <el-table-column prop="kook_channel_name" label="KOOK 频道" />
        <el-table-column prop="target_platform" label="目标平台" />
        <el-table-column label="目标频道">
          <template #default="{ row }">
            {{ getTargetChannelName(row.target_channel_id) }}
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.target_channel_id ? 'success' : 'warning'">
              {{ row.target_channel_id ? '已配置' : '待配置' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import draggable from 'vuedraggable'
import {
  ChatDotRound,
  Microphone,
  Refresh,
  MagicStick,
  Right,
  Delete,
  Download,
  View,
  Check
} from '@element-plus/icons-vue'
import api from '@/api'

// 状态
const selectedServerId = ref('')
const targetPlatform = ref('discord')
const kookServers = ref([])
const kookChannels = ref([])
const targetChannels = ref([])
const mappings = ref([])
const smartMatching = ref(false)
const matchProgress = ref(0)
const previewVisible = ref(false)

// 方法
const loadKookChannels = async () => {
  try {
    if (!selectedServerId.value) {
      ElMessage.warning('请先选择服务器')
      return
    }

    const accounts = await api.get('/api/accounts')
    const onlineAccount = accounts.find(a => a.status === 'online')
    
    if (!onlineAccount) {
      ElMessage.warning('账号未在线')
      return
    }

    const channels = await api.get(`/api/accounts/${onlineAccount.id}/servers/${selectedServerId.value}/channels`)
    kookChannels.value = channels.filter(c => c.type === 'text')
    
  } catch (error) {
    ElMessage.error('加载频道失败：' + error.message)
  }
}

const loadTargetChannels = async () => {
  try {
    // 根据平台加载目标频道
    if (targetPlatform.value === 'discord') {
      // 从 Discord Webhook 提取频道信息
      const bots = await api.get('/api/bots')
      const discordBots = bots.filter(b => b.platform === 'discord')
      // 这里需要实现从 Webhook URL 提取频道信息的逻辑
    }
    
  } catch (error) {
    ElMessage.error('加载目标频道失败：' + error.message)
  }
}

const cloneChannel = (channel) => {
  return {
    ...channel,
    id: `mapping_${Date.now()}_${Math.random()}`,
    kook_channel_id: channel.id,
    kook_channel_name: channel.name,
    target_platform: targetPlatform.value,
    target_channel_id: ''
  }
}

const handleMappingAdd = (event) => {
  ElMessage.success('频道已添加到映射列表')
}

const handleMappingRemove = (event) => {
  ElMessage.info('频道已从映射列表移除')
}

const handleTargetSelect = (mapping) => {
  ElMessage.success(`已选择目标频道`)
}

const handleRemoveMapping = (mapping) => {
  const index = mappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    mappings.value.splice(index, 1)
  }
}

const handleSmartMatch = async () => {
  try {
    if (kookChannels.value.length === 0) {
      ElMessage.warning('请先加载 KOOK 频道')
      return
    }

    if (targetChannels.value.length === 0) {
      ElMessage.warning('请先加载目标频道')
      return
    }

    smartMatching.value = true
    matchProgress.value = 0

    // 调用智能匹配 API
    const response = await api.post('/api/smart-mapping/v2/batch-match', {
      kook_channels: kookChannels.value,
      target_channels: targetChannels.value,
      auto_apply_threshold: 90
    })

    matchProgress.value = 100

    // 显示结果
    const { results } = response
    
    ElMessageBox.alert(
      `智能匹配完成！
      
      总计: ${results.total} 个频道
      自动匹配: ${results.auto_applied} 个（高置信度）
      需审核: ${results.needs_review} 个（中等置信度）
      未匹配: ${results.unmatched} 个
      `,
      '匹配结果',
      {
        confirmButtonText: '应用匹配结果',
        callback: () => {
          applySmartMatchResults(results.mappings)
        }
      }
    )

  } catch (error) {
    ElMessage.error('智能匹配失败：' + error.message)
  } finally {
    smartMatching.value = false
  }
}

const applySmartMatchResults = (matchedMappings) => {
  // 应用智能匹配结果
  mappings.value = matchedMappings
    .filter(m => m.target_channel)
    .map(m => ({
      id: `mapping_${Date.now()}_${Math.random()}`,
      kook_channel_id: m.kook_channel.id,
      kook_channel_name: m.kook_channel.name,
      target_platform: targetPlatform.value,
      target_channel_id: m.target_channel.id,
      score: m.score,
      confidence: m.confidence
    }))
  
  ElMessage.success(`已应用 ${mappings.value.length} 条映射`)
}

const handlePreview = () => {
  previewVisible.value = true
}

const handleSave = async () => {
  try {
    // 验证所有映射都已配置目标频道
    const incomplete = mappings.value.filter(m => !m.target_channel_id)
    
    if (incomplete.length > 0) {
      ElMessage.warning(`有 ${incomplete.length} 条映射未选择目标频道`)
      return
    }

    // 保存映射
    for (const mapping of mappings.value) {
      await api.post('/api/mappings', {
        kook_server_id: selectedServerId.value,
        kook_channel_id: mapping.kook_channel_id,
        kook_channel_name: mapping.kook_channel_name,
        target_platform: mapping.target_platform,
        target_channel_id: mapping.target_channel_id
      })
    }

    ElMessage.success(`✅ 已保存 ${mappings.value.length} 条映射`)

  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const handleClear = () => {
  ElMessageBox.confirm('确定要清空所有映射吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    mappings.value = []
    ElMessage.info('已清空')
  }).catch(() => {})
}

const handleServerChange = () => {
  kookChannels.value = []
  loadKookChannels()
}

const getTargetChannelName = (channelId) => {
  const channel = targetChannels.value.find(c => c.id === channelId)
  return channel ? channel.name : '未选择'
}

onMounted(() => {
  // 加载服务器列表
  api.get('/api/accounts')
    .then(accounts => {
      const onlineAccount = accounts.find(a => a.status === 'online')
      if (onlineAccount) {
        return api.get(`/api/accounts/${onlineAccount.id}/servers`)
      }
    })
    .then(servers => {
      if (servers) {
        kookServers.value = servers
      }
    })
    .catch(error => {
      console.error('加载服务器失败:', error)
    })
  
  // 加载目标频道
  loadTargetChannels()
})
</script>

<style scoped>
.draggable-mapping-view {
  padding: 20px;
}

h2 {
  margin-bottom: 10px;
}

.description {
  color: #666;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-panel,
.target-panel {
  height: 600px;
}

.channel-list {
  max-height: 450px;
  overflow-y: auto;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin-bottom: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: move;
  transition: all 0.3s;
}

.channel-item:hover {
  background: #e0e0e0;
  transform: translateX(5px);
}

.draggable-item.sortable-ghost {
  opacity: 0.5;
  background: #409eff;
  color: white;
}

.channel-name {
  flex: 1;
  font-size: 14px;
}

.smart-match-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.smart-match-text {
  font-size: 12px;
  color: #666;
}

.mapping-list {
  min-height: 450px;
  padding: 10px;
  background: #fafafa;
  border: 2px dashed #ddd;
  border-radius: 4px;
}

.drop-zone-empty {
  text-align: center;
  padding: 100px 20px;
  color: #999;
}

.drop-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.hint {
  font-size: 12px;
  margin-top: 10px;
}

.mapping-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin-bottom: 10px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  transition: all 0.3s;
}

.mapping-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.mapping-source,
.mapping-target {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mapping-arrow {
  font-size: 20px;
  color: #409eff;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
