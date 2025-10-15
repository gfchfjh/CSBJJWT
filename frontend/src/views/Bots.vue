<template>
  <div class="bots-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🤖 机器人配置</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加机器人
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activePlatform">
        <el-tab-pane label="Discord" name="discord">
          <bot-list :platform="'discord'" />
        </el-tab-pane>
        
        <el-tab-pane label="Telegram" name="telegram">
          <bot-list :platform="'telegram'" />
        </el-tab-pane>
        
        <el-tab-pane label="飞书" name="feishu">
          <bot-list :platform="'feishu'" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 添加机器人对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加机器人"
      width="600px"
    >
      <el-form :model="botForm" label-width="120px">
        <el-form-item label="平台">
          <el-select v-model="botForm.platform" placeholder="请选择平台">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="机器人名称">
          <el-input v-model="botForm.name" placeholder="用于识别的名称" />
        </el-form-item>
        
        <!-- Discord配置 -->
        <template v-if="botForm.platform === 'discord'">
          <el-form-item label="Webhook URL">
            <el-input v-model="botForm.config.webhook_url" placeholder="https://discord.com/api/webhooks/..." />
          </el-form-item>
        </template>
        
        <!-- Telegram配置 -->
        <template v-if="botForm.platform === 'telegram'">
          <el-form-item label="Bot Token">
            <el-input v-model="botForm.config.token" placeholder="1234567890:ABCdefGHIjklMNOpqrs..." />
          </el-form-item>
          
          <el-form-item label="Chat ID">
            <el-input v-model="botForm.config.chat_id" placeholder="-1001234567890" />
          </el-form-item>
        </template>
        
        <!-- 飞书配置 -->
        <template v-if="botForm.platform === 'feishu'">
          <el-form-item label="App ID">
            <el-input v-model="botForm.config.app_id" placeholder="cli_a1b2c3d4e5f6g7h8" />
          </el-form-item>
          
          <el-form-item label="App Secret">
            <el-input v-model="botForm.config.app_secret" placeholder="ABCdefGHIjklMNOpqrs" />
          </el-form-item>
          
          <el-form-item label="Chat ID">
            <el-input v-model="botForm.config.chat_id" placeholder="oc_xxx" />
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addBot">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import BotList from '../components/BotList.vue'

const activePlatform = ref('discord')
const showAddDialog = ref(false)

const botForm = ref({
  platform: 'discord',
  name: '',
  config: {
    webhook_url: '',
    token: '',
    chat_id: '',
    app_id: '',
    app_secret: ''
  }
})

const addBot = async () => {
  try {
    // 根据平台过滤配置
    let config = {}
    if (botForm.value.platform === 'discord') {
      config = { webhook_url: botForm.value.config.webhook_url }
    } else if (botForm.value.platform === 'telegram') {
      config = {
        token: botForm.value.config.token,
        chat_id: botForm.value.config.chat_id
      }
    } else if (botForm.value.platform === 'feishu') {
      config = {
        app_id: botForm.value.config.app_id,
        app_secret: botForm.value.config.app_secret,
        chat_id: botForm.value.config.chat_id
      }
    }
    
    await api.addBotConfig({
      platform: botForm.value.platform,
      name: botForm.value.name,
      config
    })
    
    ElMessage.success('机器人添加成功')
    showAddDialog.value = false
    
    // 重置表单
    botForm.value = {
      platform: 'discord',
      name: '',
      config: {
        webhook_url: '',
        token: '',
        chat_id: '',
        app_id: '',
        app_secret: ''
      }
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
