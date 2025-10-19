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
    
    <!-- 添加机器人对话框（v1.7.2增强版 - 带表单验证） -->
    <el-dialog
      v-model="showAddDialog"
      title="添加机器人"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="botForm" :rules="botFormRules" ref="botFormRef" label-width="120px">
        <el-form-item label="平台" prop="platform">
          <el-select v-model="botForm.platform" placeholder="请选择平台">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="机器人名称" prop="name">
          <el-input 
            v-model="botForm.name" 
            placeholder="用于识别的名称（例如：游戏公告Bot）" 
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <!-- Discord配置 -->
        <template v-if="botForm.platform === 'discord'">
          <el-form-item label="Webhook URL" prop="config.webhook_url">
            <el-input 
              v-model="botForm.config.webhook_url" 
              placeholder="https://discord.com/api/webhooks/..." 
              type="textarea"
              :rows="2"
            />
            <div class="form-help-text">
              💡 <el-link type="primary" href="#" @click.prevent="openTutorial('discord')">
                如何获取Discord Webhook URL？
              </el-link>
            </div>
          </el-form-item>
        </template>
        
        <!-- Telegram配置 -->
        <template v-if="botForm.platform === 'telegram'">
          <el-form-item label="Bot Token" prop="config.token">
            <el-input 
              v-model="botForm.config.token" 
              placeholder="1234567890:ABCdefGHIjklMNOpqrs..." 
              type="textarea"
              :rows="2"
            />
            <div class="form-help-text">
              💡 <el-link type="primary" href="#" @click.prevent="openTutorial('telegram')">
                如何创建Telegram Bot？
              </el-link>
            </div>
          </el-form-item>
          
          <el-form-item label="Chat ID" prop="config.chat_id">
            <el-input 
              v-model="botForm.config.chat_id" 
              placeholder="-1001234567890" 
            />
            <div class="form-help-text">
              💡 Chat ID通常是负数，表示群组
            </div>
          </el-form-item>
        </template>
        
        <!-- 飞书配置 -->
        <template v-if="botForm.platform === 'feishu'">
          <el-form-item label="App ID" prop="config.app_id">
            <el-input 
              v-model="botForm.config.app_id" 
              placeholder="cli_a1b2c3d4e5f6g7h8" 
            />
          </el-form-item>
          
          <el-form-item label="App Secret" prop="config.app_secret">
            <el-input 
              v-model="botForm.config.app_secret" 
              placeholder="ABCdefGHIjklMNOpqrs" 
              type="password"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="Chat ID" prop="config.chat_id">
            <el-input 
              v-model="botForm.config.chat_id" 
              placeholder="oc_xxx" 
            />
            <div class="form-help-text">
              💡 <el-link type="primary" href="#" @click.prevent="openTutorial('feishu')">
                如何获取飞书Chat ID？
              </el-link>
            </div>
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="warning" :loading="isTesting" @click="testBot">
          <el-icon><Pointer /></el-icon>
          测试连接
        </el-button>
        <el-button type="primary" :loading="isAdding" @click="addBot">
          <el-icon><Check /></el-icon>
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import BotList from '../components/BotList.vue'

const activePlatform = ref('discord')
const showAddDialog = ref(false)
const isAdding = ref(false)
const isTesting = ref(false)
const botFormRef = ref(null)

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

// v1.7.2新增：表单验证规则
const botFormRules = computed(() => {
  const baseRules = {
    platform: [
      { required: true, message: '请选择平台', trigger: 'change' }
    ],
    name: [
      { required: true, message: '请输入机器人名称', trigger: 'blur' },
      { min: 2, max: 50, message: '名称长度在2-50个字符', trigger: 'blur' }
    ]
  }
  
  // 根据平台动态添加验证规则
  if (botForm.value.platform === 'discord') {
    baseRules['config.webhook_url'] = [
      { required: true, message: '请输入Webhook URL', trigger: 'blur' },
      { 
        pattern: /^https:\/\/discord\.com\/api\/webhooks\/\d{10,20}\/[a-zA-Z0-9_-]{20,}$/,
        message: 'Webhook URL格式不正确',
        trigger: 'blur'
      }
    ]
  } else if (botForm.value.platform === 'telegram') {
    baseRules['config.token'] = [
      { required: true, message: '请输入Bot Token', trigger: 'blur' },
      { 
        pattern: /^\d{8,10}:[a-zA-Z0-9_-]{30,40}$/,
        message: 'Bot Token格式不正确（格式：1234567890:ABC...）',
        trigger: 'blur'
      }
    ]
    baseRules['config.chat_id'] = [
      { required: true, message: '请输入Chat ID', trigger: 'blur' },
      { 
        pattern: /^-?\d{8,15}$/,
        message: 'Chat ID格式不正确（应为数字）',
        trigger: 'blur'
      }
    ]
  } else if (botForm.value.platform === 'feishu') {
    baseRules['config.app_id'] = [
      { required: true, message: '请输入App ID', trigger: 'blur' },
      { 
        pattern: /^cli_[a-zA-Z0-9]{16,}$/,
        message: 'App ID格式不正确（格式：cli_...）',
        trigger: 'blur'
      }
    ]
    baseRules['config.app_secret'] = [
      { required: true, message: '请输入App Secret', trigger: 'blur' },
      { 
        min: 20,
        message: 'App Secret长度不足',
        trigger: 'blur'
      }
    ]
    baseRules['config.chat_id'] = [
      { required: true, message: '请输入Chat ID', trigger: 'blur' }
    ]
  }
  
  return baseRules
})

// 测试机器人连接（v1.7.2新增）
const testBot = async () => {
  // 先验证表单
  if (!botFormRef.value) return
  
  try {
    await botFormRef.value.validate()
  } catch (error) {
    ElMessage.warning('请先填写完整的配置信息')
    return
  }
  
  try {
    isTesting.value = true
    
    // 根据平台构建配置
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
    
    // 调用测试API
    const result = await api.testBot({
      platform: botForm.value.platform,
      config
    })
    
    if (result.success) {
      ElMessage.success('✅ 连接测试成功！')
    } else {
      ElMessage.error(`❌ 连接测试失败: ${result.message}`)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    isTesting.value = false
  }
}

const addBot = async () => {
  // v1.7.2增强：先验证表单
  if (!botFormRef.value) return
  
  try {
    await botFormRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  try {
    isAdding.value = true
    
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
    
    ElMessage.success('✅ 机器人添加成功')
    showAddDialog.value = false
    
    // 重置表单
    botFormRef.value?.resetFields()
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
    ElMessage.error('添加失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    isAdding.value = false
  }
}

// 打开教程
const openTutorial = (platform) => {
  const tutorialMap = {
    discord: 'Discord配置教程.md',
    telegram: 'Telegram配置教程.md',
    feishu: '飞书配置教程.md'
  }
  
  ElMessageBox.alert(
    `请查看帮助中心的"${tutorialMap[platform]}"获取详细配置步骤`,
    '配置教程',
    {
      confirmButtonText: '前往帮助中心',
      callback: () => {
        // 可以跳转到帮助中心页面
        window.open('#/help', '_blank')
      }
    }
  )
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>
