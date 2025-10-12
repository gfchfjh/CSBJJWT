<template>
  <div class="mapping-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔀 频道映射配置</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加映射
          </el-button>
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
const mappings = ref([])
const bots = ref([])

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
