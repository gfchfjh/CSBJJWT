<template>
  <div class="mapping-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔀 频道映射配置</span>
          <div>
            <el-button type="success" @click="showSmartMappingDialog = true">
              <el-icon><MagicStick /></el-icon>
              智能映射
            </el-button>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加映射
            </el-button>
          </div>
        </div>
      </template>
      
      <el-alert
        title="提示"
        type="info"
        description="频道映射用于将KOOK频道的消息转发到目标平台。一个KOOK频道可以同时转发到多个目标。"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <el-table :data="mappings" border style="width: 100%">
        <el-table-column prop="kook_channel_name" label="KOOK频道" width="200" />
        <el-table-column prop="target_platform" label="目标平台" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.target_platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_channel_id" label="目标频道ID" />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteMapping(row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 智能映射对话框 -->
    <el-dialog
      v-model="showSmartMappingDialog"
      title="💡 智能频道映射"
      width="800px"
    >
      <el-alert
        title="智能映射说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        系统将自动识别KOOK频道名称，并在目标平台查找同名或相似频道，建立映射关系。
      </el-alert>

      <div v-if="!smartSuggestions.length">
        <el-button type="primary" :loading="loadingSuggestions" @click="generateSmartSuggestions">
          🔍 生成映射建议
        </el-button>
      </div>

      <div v-else>
        <el-table :data="smartSuggestions" border max-height="400">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="kook_channel_name" label="KOOK频道" width="150" />
          <el-table-column label="→" width="40" align="center">
            <template>→</template>
          </el-table-column>
          <el-table-column prop="target_channel_name" label="目标频道" width="150" />
          <el-table-column prop="target_platform" label="平台" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.target_platform }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="置信度" width="120">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.round(row.confidence * 100)"
                :color="getConfidenceColor(row.confidence)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="匹配原因" show-overflow-tooltip />
        </el-table>

        <div style="margin-top: 20px; text-align: center">
          <el-button @click="smartSuggestions = []">重新生成</el-button>
          <el-button type="primary" @click="applySmartSuggestions" :loading="applyingMappings">
            应用所有建议
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 添加映射对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加频道映射"
      width="600px"
    >
      <el-form :model="mappingForm" label-width="120px">
        <el-form-item label="KOOK服务器ID">
          <el-input v-model="mappingForm.kook_server_id" placeholder="服务器ID" />
        </el-form-item>
        
        <el-form-item label="KOOK频道ID">
          <el-input v-model="mappingForm.kook_channel_id" placeholder="频道ID" />
        </el-form-item>
        
        <el-form-item label="频道名称">
          <el-input v-model="mappingForm.kook_channel_name" placeholder="用于显示的名称" />
        </el-form-item>
        
        <el-form-item label="目标平台">
          <el-select v-model="mappingForm.target_platform" placeholder="请选择">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标机器人">
          <el-select v-model="mappingForm.target_bot_id" placeholder="请选择">
            <el-option
              v-for="bot in targetBots"
              :key="bot.id"
              :label="bot.name"
              :value="bot.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标频道ID">
          <el-input v-model="mappingForm.target_channel_id" placeholder="目标频道/群组ID" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addMapping">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const showAddDialog = ref(false)
const showSmartMappingDialog = ref(false)
const mappings = ref([])
const bots = ref([])
const smartSuggestions = ref([])
const loadingSuggestions = ref(false)
const applyingMappings = ref(false)

const mappingForm = ref({
  kook_server_id: '',
  kook_channel_id: '',
  kook_channel_name: '',
  target_platform: '',
  target_bot_id: null,
  target_channel_id: ''
})

const targetBots = computed(() => {
  if (!mappingForm.value.target_platform) return []
  return bots.value.filter(b => b.platform === mappingForm.value.target_platform)
})

const fetchMappings = async () => {
  try {
    mappings.value = await api.getMappings()
  } catch (error) {
    console.error('获取映射列表失败:', error)
  }
}

const fetchBots = async () => {
  try {
    bots.value = await api.getBotConfigs()
  } catch (error) {
    console.error('获取机器人列表失败:', error)
  }
}

const addMapping = async () => {
  try {
    await api.addMapping(mappingForm.value)
    ElMessage.success('映射添加成功')
    showAddDialog.value = false
    await fetchMappings()
    
    // 重置表单
    mappingForm.value = {
      kook_server_id: '',
      kook_channel_id: '',
      kook_channel_name: '',
      target_platform: '',
      target_bot_id: null,
      target_channel_id: ''
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}

const deleteMapping = async (mappingId) => {
  try {
    await ElMessageBox.confirm('确定要删除此映射吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteMapping(mappingId)
    ElMessage.success('映射已删除')
    await fetchMappings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 生成智能映射建议
const generateSmartSuggestions = async () => {
  try {
    loadingSuggestions.value = true
    
    // 获取账号列表（简化版，实际应该让用户选择）
    const accounts = await api.getAccounts()
    if (!accounts || accounts.length === 0) {
      ElMessage.warning('请先添加KOOK账号')
      return
    }
    
    // 使用第一个账号（实际应该让用户选择）
    const accountId = accounts[0].id
    
    // 获取KOOK服务器和频道
    const serversData = await api.getServers(accountId)
    const servers = serversData.servers || []
    
    if (servers.length === 0) {
      ElMessage.warning('未找到服务器，请确保账号已启动')
      return
    }
    
    // 获取所有服务器的频道
    const kookServers = []
    for (const server of servers) {
      try {
        const channelsData = await api.getChannels(accountId, server.id)
        kookServers.push({
          id: server.id,
          name: server.name,
          channels: channelsData.channels || []
        })
      } catch (error) {
        console.error(`获取服务器 ${server.name} 的频道失败:`, error)
      }
    }
    
    // 生成智能映射建议
    const result = await api.suggestMappings({
      account_id: accountId,
      kook_servers: kookServers,
      target_bots: bots.value
    })
    
    smartSuggestions.value = result
    
    if (result.length === 0) {
      ElMessage.info('未找到匹配的频道映射建议')
    } else {
      ElMessage.success(`找到 ${result.length} 条映射建议`)
    }
  } catch (error) {
    console.error('生成智能映射建议失败:', error)
    ElMessage.error('生成建议失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingSuggestions.value = false
  }
}

// 应用智能映射建议
const applySmartSuggestions = async () => {
  try {
    applyingMappings.value = true
    
    if (smartSuggestions.value.length === 0) {
      ElMessage.warning('没有可应用的建议')
      return
    }
    
    await api.applySmartMappings(smartSuggestions.value)
    ElMessage.success('智能映射应用成功')
    
    showSmartMappingDialog.value = false
    smartSuggestions.value = []
    await fetchMappings()
  } catch (error) {
    console.error('应用智能映射失败:', error)
    ElMessage.error('应用失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    applyingMappings.value = false
  }
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

watch(() => mappingForm.value.target_platform, () => {
  mappingForm.value.target_bot_id = null
})

onMounted(() => {
  fetchMappings()
  fetchBots()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
