<template>
  <div class="mapping-table-view-container">
    <!-- 顶部工具栏 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <h2>
          <el-icon><Grid /></el-icon>
          表格式频道映射
        </h2>
        <el-tag type="info">{{ mappings.length }}个映射</el-tag>
      </div>
      
      <div class="toolbar-right">
        <el-button :icon="MagicStick" @click="smartMapping">智能映射</el-button>
        <el-button :icon="Upload" @click="importMappings">导入</el-button>
        <el-button :icon="Download" @click="exportMappings">导出</el-button>
        <el-button type="primary" :icon="Plus" @click="showAddMappingDialog">
          添加映射
        </el-button>
        <el-button type="success" :icon="Check" @click="saveMappings" :loading="saving">
          保存映射
        </el-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="KOOK服务器">
          <el-select 
            v-model="filters.serverId" 
            placeholder="全部" 
            clearable
            style="width: 200px"
          >
            <el-option label="全部服务器" value="" />
            <el-option 
              v-for="server in kookServers" 
              :key="server.id" 
              :label="server.name" 
              :value="server.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目标平台">
          <el-select 
            v-model="filters.platform" 
            placeholder="全部" 
            clearable
            style="width: 150px"
          >
            <el-option label="全部平台" value="" />
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select 
            v-model="filters.enabled" 
            placeholder="全部" 
            clearable
            style="width: 120px"
          >
            <el-option label="全部状态" value="" />
            <el-option label="已启用" :value="true" />
            <el-option label="已禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-input 
            v-model="filters.keyword" 
            placeholder="搜索频道名称"
            :prefix-icon="Search"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 映射表格 -->
    <el-table
      :data="filteredMappings"
      stripe
      border
      v-loading="loading"
      @selection-change="handleSelectionChange"
      :default-sort="{ prop: 'kook_server_name', order: 'ascending' }"
      class="mapping-table"
    >
      <!-- 多选 -->
      <el-table-column type="selection" width="55" />
      
      <!-- 序号 -->
      <el-table-column type="index" label="#" width="60" />
      
      <!-- KOOK服务器 -->
      <el-table-column 
        prop="kook_server_name" 
        label="KOOK服务器" 
        width="180"
        sortable
      >
        <template #default="scope">
          <div class="server-cell">
            <el-icon color="#409EFF"><OfficeBuilding /></el-icon>
            <span>{{ scope.row.kook_server_name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <!-- KOOK频道 -->
      <el-table-column 
        prop="kook_channel_name" 
        label="KOOK频道" 
        width="200"
        sortable
      >
        <template #default="scope">
          <div class="channel-cell">
            <el-icon color="#67C23A"><ChatDotRound /></el-icon>
            <span># {{ scope.row.kook_channel_name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <!-- 映射箭头 -->
      <el-table-column label="" width="80" align="center">
        <template #default>
          <el-icon :size="20" color="#909399"><Right /></el-icon>
        </template>
      </el-table-column>
      
      <!-- 目标平台 -->
      <el-table-column 
        prop="target_platform" 
        label="目标平台" 
        width="120"
        sortable
      >
        <template #default="scope">
          <el-tag 
            :type="getPlatformTagType(scope.row.target_platform)"
            effect="plain"
          >
            {{ getPlatformName(scope.row.target_platform) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <!-- Bot名称 -->
      <el-table-column 
        prop="target_bot_name" 
        label="Bot名称" 
        width="150"
      >
        <template #default="scope">
          <div class="bot-cell">
            <el-icon :color="getBotStatusColor(scope.row.target_bot_id)">
              <CircleCheck v-if="isBotOnline(scope.row.target_bot_id)" />
              <CircleClose v-else />
            </el-icon>
            <span>{{ scope.row.target_bot_name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <!-- 目标频道 -->
      <el-table-column 
        prop="target_channel_name" 
        label="目标频道" 
        width="200"
      >
        <template #default="scope">
          <div class="channel-cell">
            <el-icon><Connection /></el-icon>
            <span>{{ scope.row.target_channel_name || scope.row.target_channel_id }}</span>
          </div>
        </template>
      </el-table-column>
      
      <!-- 状态 -->
      <el-table-column 
        prop="enabled" 
        label="状态" 
        width="100"
        sortable
      >
        <template #default="scope">
          <el-switch
            v-model="scope.row.enabled"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      
      <!-- 创建时间 -->
      <el-table-column 
        prop="created_at" 
        label="创建时间" 
        width="160"
        sortable
      >
        <template #default="scope">
          <div class="time-cell">
            <el-icon><Clock /></el-icon>
            <span>{{ formatTime(scope.row.created_at) }}</span>
          </div>
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button-group>
            <el-button 
              type="primary" 
              :icon="View" 
              size="small"
              @click="viewMapping(scope.row)"
            >
              详情
            </el-button>
            <el-button 
              type="warning" 
              :icon="Edit" 
              size="small"
              @click="editMapping(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              :icon="Delete" 
              size="small"
              @click="deleteMapping(scope.row)"
            >
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 批量操作栏 -->
    <div class="batch-actions" v-if="selectedMappings.length > 0">
      <div class="batch-info">
        已选择 <strong>{{ selectedMappings.length }}</strong> 个映射
      </div>
      <div class="batch-buttons">
        <el-button @click="batchEnable">批量启用</el-button>
        <el-button @click="batchDisable">批量禁用</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredMappings.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑映射对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="KOOK服务器" prop="kook_server_id">
          <el-select 
            v-model="formData.kook_server_id" 
            placeholder="请选择服务器"
            @change="handleServerChange"
            style="width: 100%"
          >
            <el-option 
              v-for="server in kookServers" 
              :key="server.id" 
              :label="server.name" 
              :value="server.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="KOOK频道" prop="kook_channel_id">
          <el-select 
            v-model="formData.kook_channel_id" 
            placeholder="请选择频道"
            :disabled="!formData.kook_server_id"
            style="width: 100%"
          >
            <el-option 
              v-for="channel in availableChannels" 
              :key="channel.id" 
              :label="`# ${channel.name}`" 
              :value="channel.id" 
            />
          </el-select>
        </el-form-item>

        <el-divider />

        <el-form-item label="目标平台" prop="target_platform">
          <el-radio-group v-model="formData.target_platform" @change="handlePlatformChange">
            <el-radio label="discord">Discord</el-radio>
            <el-radio label="telegram">Telegram</el-radio>
            <el-radio label="feishu">飞书</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="目标Bot" prop="target_bot_id">
          <el-select 
            v-model="formData.target_bot_id" 
            placeholder="请选择Bot"
            :disabled="!formData.target_platform"
            style="width: 100%"
          >
            <el-option 
              v-for="bot in availableBots" 
              :key="bot.id" 
              :label="bot.name" 
              :value="bot.id" 
            >
              <span>{{ bot.name }}</span>
              <el-tag 
                :type="bot.online ? 'success' : 'danger'" 
                size="small"
                style="margin-left: 10px"
              >
                {{ bot.online ? '在线' : '离线' }}
              </el-tag>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="目标频道" prop="target_channel_id">
          <el-input 
            v-model="formData.target_channel_id" 
            placeholder="请输入目标频道ID或Webhook URL"
          />
          <div class="form-hint">
            Discord: Webhook URL<br>
            Telegram: Chat ID（例如：-1001234567890）<br>
            飞书: 群组ID或Webhook URL
          </div>
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="formData.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMapping" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="映射详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentMapping">
        <el-descriptions-item label="KOOK服务器">
          {{ currentMapping.kook_server_name }}
        </el-descriptions-item>
        <el-descriptions-item label="KOOK频道">
          # {{ currentMapping.kook_channel_name }}
        </el-descriptions-item>
        <el-descriptions-item label="目标平台">
          <el-tag :type="getPlatformTagType(currentMapping.target_platform)">
            {{ getPlatformName(currentMapping.target_platform) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="目标Bot">
          {{ currentMapping.target_bot_name }}
        </el-descriptions-item>
        <el-descriptions-item label="目标频道">
          {{ currentMapping.target_channel_name || currentMapping.target_channel_id }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentMapping.enabled ? 'success' : 'info'">
            {{ currentMapping.enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatTime(currentMapping.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新" :span="2">
          {{ formatTime(currentMapping.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="editMapping(currentMapping)">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, MagicStick, Upload, Download, Plus, Check, Search,
  OfficeBuilding, ChatDotRound, Right, CircleCheck, CircleClose,
  Connection, Clock, View, Edit, Delete
} from '@element-plus/icons-vue'
import api from '@/api'

// 数据
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const mappings = ref([])
const kookServers = ref([])
const bots = ref([])
const selectedMappings = ref([])

// 筛选器
const filters = reactive({
  serverId: '',
  platform: '',
  enabled: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = computed(() => formData.id ? '编辑映射' : '添加映射')

// 表单
const formRef = ref(null)
const formData = reactive({
  id: null,
  kook_server_id: '',
  kook_channel_id: '',
  target_platform: 'discord',
  target_bot_id: '',
  target_channel_id: '',
  enabled: true
})

const formRules = {
  kook_server_id: [{ required: true, message: '请选择KOOK服务器', trigger: 'change' }],
  kook_channel_id: [{ required: true, message: '请选择KOOK频道', trigger: 'change' }],
  target_platform: [{ required: true, message: '请选择目标平台', trigger: 'change' }],
  target_bot_id: [{ required: true, message: '请选择目标Bot', trigger: 'change' }],
  target_channel_id: [{ required: true, message: '请输入目标频道', trigger: 'blur' }]
}

const currentMapping = ref(null)

// 计算属性
const filteredMappings = computed(() => {
  let result = mappings.value

  if (filters.serverId) {
    result = result.filter(m => m.kook_server_id === filters.serverId)
  }

  if (filters.platform) {
    result = result.filter(m => m.target_platform === filters.platform)
  }

  if (filters.enabled !== '') {
    result = result.filter(m => m.enabled === filters.enabled)
  }

  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    result = result.filter(m => 
      m.kook_channel_name.toLowerCase().includes(keyword) ||
      m.kook_server_name.toLowerCase().includes(keyword) ||
      m.target_channel_name?.toLowerCase().includes(keyword)
    )
  }

  return result
})

const availableChannels = computed(() => {
  if (!formData.kook_server_id) return []
  
  const server = kookServers.value.find(s => s.id === formData.kook_server_id)
  return server?.channels || []
})

const availableBots = computed(() => {
  if (!formData.target_platform) return []
  
  return bots.value.filter(b => b.platform === formData.target_platform)
})

// 方法
const loadMappings = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/mappings')
    if (response.data.success) {
      mappings.value = response.data.mappings
    }
  } catch (error) {
    ElMessage.error('加载映射失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadServers = async () => {
  try {
    const response = await api.get('/api/servers/discover')
    if (response.data.success) {
      kookServers.value = response.data.servers
    }
  } catch (error) {
    console.error('加载服务器失败:', error)
  }
}

const loadBots = async () => {
  try {
    const response = await api.get('/api/bots')
    if (response.data.success) {
      bots.value = response.data.bots
    }
  } catch (error) {
    console.error('加载Bot失败:', error)
  }
}

const showAddMappingDialog = () => {
  Object.assign(formData, {
    id: null,
    kook_server_id: '',
    kook_channel_id: '',
    target_platform: 'discord',
    target_bot_id: '',
    target_channel_id: '',
    enabled: true
  })
  
  dialogVisible.value = true
}

const editMapping = (mapping) => {
  detailDialogVisible.value = false
  
  Object.assign(formData, {
    id: mapping.id,
    kook_server_id: mapping.kook_server_id,
    kook_channel_id: mapping.kook_channel_id,
    target_platform: mapping.target_platform,
    target_bot_id: mapping.target_bot_id,
    target_channel_id: mapping.target_channel_id,
    enabled: mapping.enabled
  })
  
  dialogVisible.value = true
}

const viewMapping = (mapping) => {
  currentMapping.value = mapping
  detailDialogVisible.value = true
}

const deleteMapping = async (mapping) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除映射"${mapping.kook_channel_name} → ${mapping.target_channel_name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await api.delete(`/api/mappings/${mapping.id}`)
    
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadMappings()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  }
}

const submitMapping = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const url = formData.id ? `/api/mappings/${formData.id}` : '/api/mappings'
    const method = formData.id ? 'put' : 'post'
    
    const response = await api[method](url, formData)
    
    if (response.data.success) {
      ElMessage.success(formData.id ? '更新成功' : '添加成功')
      dialogVisible.value = false
      loadMappings()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

const saveMappings = async () => {
  saving.value = true
  try {
    const response = await api.post('/api/mappings/batch', {
      mappings: mappings.value
    })
    
    if (response.data.success) {
      ElMessage.success('保存成功')
    }
  } catch (error) {
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedMappings.value = selection
}

const handleStatusChange = (mapping) => {
  ElMessage.info(`${mapping.kook_channel_name} 已${mapping.enabled ? '启用' : '禁用'}`)
}

const handleServerChange = () => {
  formData.kook_channel_id = ''
}

const handlePlatformChange = () => {
  formData.target_bot_id = ''
}

const batchEnable = () => {
  selectedMappings.value.forEach(m => m.enabled = true)
  ElMessage.success(`已启用 ${selectedMappings.value.length} 个映射`)
}

const batchDisable = () => {
  selectedMappings.value.forEach(m => m.enabled = false)
  ElMessage.success(`已禁用 ${selectedMappings.value.length} 个映射`)
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedMappings.value.length} 个映射吗？`,
      '批量删除',
      { type: 'warning' }
    )
    
    const ids = selectedMappings.value.map(m => m.id)
    const response = await api.post('/api/mappings/batch-delete', { ids })
    
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadMappings()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  }
}

const smartMapping = () => {
  ElMessage.info('智能映射功能开发中...')
}

const importMappings = () => {
  ElMessage.info('导入功能开发中...')
}

const exportMappings = () => {
  ElMessage.info('导出功能开发中...')
}

const resetFilters = () => {
  filters.serverId = ''
  filters.platform = ''
  filters.enabled = ''
  filters.keyword = ''
}

const handleSizeChange = () => {
  pagination.page = 1
}

const handleCurrentChange = () => {
  // 页码变化
}

const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

const getPlatformName = (platform) => {
  const names = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  }
  return names[platform] || platform
}

const isBotOnline = (botId) => {
  const bot = bots.value.find(b => b.id === botId)
  return bot?.online || false
}

const getBotStatusColor = (botId) => {
  return isBotOnline(botId) ? '#67C23A' : '#F56C6C'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadMappings()
  loadServers()
  loadBots()
})
</script>

<style scoped>
.mapping-table-view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.toolbar-left h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.filter-bar {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.filter-bar :deep(.el-form-item) {
  margin-bottom: 0;
}

.mapping-table {
  flex: 1;
  margin-bottom: 20px;
}

.server-cell,
.channel-cell,
.bot-cell,
.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  margin-bottom: 20px;
}

.batch-info strong {
  color: #409eff;
}

.batch-buttons {
  display: flex;
  gap: 10px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.6;
}
</style>
