<template>
  <div class="bot-list">
    <el-empty v-if="bots.length === 0" description="暂无机器人配置" />
    
    <el-table v-else :data="bots" border style="width: 100%">
      <el-table-column prop="name" label="名称" width="180" />
      
      <el-table-column label="配置信息">
        <template #default="{ row }">
          <div v-if="platform === 'discord'">
            Webhook: {{ row.config.webhook_url?.substring(0, 40) }}...
          </div>
          <div v-else-if="platform === 'telegram'">
            Token: {{ row.config.token?.substring(0, 20) }}...<br/>
            Chat ID: {{ row.config.chat_id }}
          </div>
          <div v-else-if="platform === 'feishu'">
            App ID: {{ row.config.app_id }}<br/>
            Chat ID: {{ row.config.chat_id }}
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '活跃' : '未知' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="testBot(row.id)">
            <el-icon><Connection /></el-icon>
            测试
          </el-button>
          
          <el-button size="small" type="danger" @click="deleteBot(row.id)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const props = defineProps({
  platform: {
    type: String,
    required: true
  }
})

const bots = ref([])

const fetchBots = async () => {
  try {
    bots.value = await api.getBotConfigs(props.platform)
  } catch (error) {
    console.error('获取机器人列表失败:', error)
  }
}

const testBot = async (botId) => {
  try {
    const result = await api.testBotConfig(botId)
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

const deleteBot = async (botId) => {
  try {
    await ElMessageBox.confirm('确定要删除此机器人配置吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteBotConfig(botId)
    ElMessage.success('机器人已删除')
    await fetchBots()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

watch(() => props.platform, () => {
  fetchBots()
})

onMounted(() => {
  fetchBots()
})
</script>

<style scoped>
.bot-list {
  min-height: 300px;
}
</style>
