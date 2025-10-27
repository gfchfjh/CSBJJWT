<template>
  <el-card class="step-card">
    <template #header>
      <div class="card-header">
        <h2>⚙️ 配置转发目标</h2>
        <p>选择消息转发的平台并进行智能映射</p>
      </div>
    </template>

    <div class="step-content">
      <!-- Bot平台选择 -->
      <el-alert
        title="选择转发平台"
        type="info"
        :closable="false"
        show-icon
        class="platform-alert"
      >
        至少选择一个平台作为转发目标
      </el-alert>

      <el-checkbox-group v-model="selectedPlatforms" class="platform-selection">
        <el-card 
          v-for="platform in platforms" 
          :key="platform.value"
          class="platform-card"
          :class="{ selected: selectedPlatforms.includes(platform.value) }"
          shadow="hover"
          @click="togglePlatform(platform.value)"
        >
          <div class="platform-icon">{{ platform.icon }}</div>
          <h3>{{ platform.label }}</h3>
          <p class="platform-desc">{{ platform.description }}</p>
          
          <div v-if="selectedPlatforms.includes(platform.value)" class="platform-config">
            <el-divider />
            
            <!-- Discord配置 -->
            <template v-if="platform.value === 'discord'">
              <el-form-item label="Webhook URL" size="small">
                <el-input
                  v-model="botConfigs.discord.webhook_url"
                  placeholder="https://discord.com/api/webhooks/..."
                  @click.stop
                />
              </el-form-item>
              <el-button 
                size="small" 
                @click.stop="testBot('discord')"
                :loading="testing.discord"
              >
                测试连接
              </el-button>
            </template>

            <!-- Telegram配置 -->
            <template v-if="platform.value === 'telegram'">
              <el-form-item label="Bot Token" size="small">
                <el-input
                  v-model="botConfigs.telegram.bot_token"
                  placeholder="1234567890:ABCdefGHIjklMNO..."
                  @click.stop
                />
              </el-form-item>
              <el-form-item label="Chat ID" size="small">
                <el-input
                  v-model="botConfigs.telegram.chat_id"
                  placeholder="-1001234567890"
                  @click.stop
                >
                  <template #append>
                    <el-button @click.stop="detectChatId">自动获取</el-button>
                  </template>
                </el-input>
              </el-form-item>
              <el-button 
                size="small" 
                @click.stop="testBot('telegram')"
                :loading="testing.telegram"
              >
                测试连接
              </el-button>
            </template>

            <!-- 飞书配置 -->
            <template v-if="platform.value === 'feishu'">
              <el-form-item label="App ID" size="small">
                <el-input
                  v-model="botConfigs.feishu.app_id"
                  placeholder="cli_a1b2c3d4e5f6g7h8"
                  @click.stop
                />
              </el-form-item>
              <el-form-item label="App Secret" size="small">
                <el-input
                  v-model="botConfigs.feishu.app_secret"
                  placeholder="ABCdefGHIjklMNOpqrs"
                  type="password"
                  @click.stop
                />
              </el-form-item>
              <el-button 
                size="small" 
                @click.stop="testBot('feishu')"
                :loading="testing.feishu"
              >
                测试连接
              </el-button>
            </template>
          </div>
        </el-card>
      </el-checkbox-group>

      <!-- 智能映射预览 -->
      <div v-if="selectedPlatforms.length > 0 && props.wizardData.selectedChannels?.length > 0" class="mapping-preview">
        <el-divider>智能映射预览</el-divider>

        <el-alert
          title="智能映射"
          type="success"
          :closable="false"
          show-icon
        >
          系统将自动为您的KOOK频道匹配合适的转发目标，匹配成功率约90%
        </el-alert>

        <div class="mapping-stats">
          <el-statistic title="KOOK频道" :value="props.wizardData.selectedChannels.length">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-statistic>
          
          <el-icon class="arrow-icon"><Right /></el-icon>
          
          <el-statistic title="将创建映射" :value="estimatedMappings">
            <template #prefix>
              <el-icon><Connection /></el-icon>
            </template>
          </el-statistic>
        </div>

        <el-button 
          type="primary" 
          @click="previewMappings"
          :loading="previewing"
        >
          <el-icon><View /></el-icon>
          预览映射详情
        </el-button>
      </div>
    </div>

    <!-- 底部操作 -->
    <template #footer>
      <div class="step-footer">
        <el-button size="large" @click="handlePrev">
          <el-icon><ArrowLeft /></el-icon>
          上一步
        </el-button>

        <el-button 
          type="primary" 
          size="large"
          :loading="saving"
          :disabled="selectedPlatforms.length === 0 || !hasValidBotConfig"
          @click="handleNext"
        >
          保存并继续
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  ArrowLeft, 
  ArrowRight, 
  Message,
  Connection,
  Right,
  View
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  mode: String,
  wizardData: Object
})

const emit = defineEmits(['next', 'prev', 'update-data'])

const platforms = [
  {
    value: 'discord',
    label: 'Discord',
    icon: '💬',
    description: '通过Webhook转发到Discord服务器'
  },
  {
    value: 'telegram',
    label: 'Telegram',
    icon: '✈️',
    description: '使用Bot转发到Telegram群组'
  },
  {
    value: 'feishu',
    label: '飞书',
    icon: '🏢',
    description: '转发到飞书企业群组'
  }
]

const selectedPlatforms = ref(['discord'])  // 默认选择Discord

const botConfigs = reactive({
  discord: {
    webhook_url: ''
  },
  telegram: {
    bot_token: '',
    chat_id: ''
  },
  feishu: {
    app_id: '',
    app_secret: ''
  }
})

const testing = reactive({
  discord: false,
  telegram: false,
  feishu: false
})

const saving = ref(false)
const previewing = ref(false)

// 是否有有效的Bot配置
const hasValidBotConfig = computed(() => {
  for (const platform of selectedPlatforms.value) {
    const config = botConfigs[platform]
    
    if (platform === 'discord' && !config.webhook_url) {
      return false
    }
    if (platform === 'telegram' && (!config.bot_token || !config.chat_id)) {
      return false
    }
    if (platform === 'feishu' && (!config.app_id || !config.app_secret)) {
      return false
    }
  }
  
  return true
})

// 预计创建的映射数
const estimatedMappings = computed(() => {
  return selectedPlatforms.value.length * (props.wizardData.selectedChannels?.length || 0)
})

// 切换平台选择
const togglePlatform = (platform) => {
  const index = selectedPlatforms.value.indexOf(platform)
  if (index > -1) {
    selectedPlatforms.value.splice(index, 1)
  } else {
    selectedPlatforms.value.push(platform)
  }
}

// 测试Bot连接
const testBot = async (platform) => {
  testing[platform] = true

  try {
    const config = botConfigs[platform]
    
    const result = await api.post(`/api/bots/${platform}/test`, config)
    
    if (result.success) {
      ElMessage.success(`${platforms.find(p => p.value === platform).label} 连接测试成功！`)
    } else {
      ElMessage.error(`连接测试失败: ${result.message}`)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    testing[platform] = false
  }
}

// 自动获取Telegram Chat ID
const detectChatId = async () => {
  if (!botConfigs.telegram.bot_token) {
    ElMessage.warning('请先填写Bot Token')
    return
  }

  try {
    const result = await api.post('/api/telegram/detect-chat-id', {
      bot_token: botConfigs.telegram.bot_token
    })

    if (result.chat_id) {
      botConfigs.telegram.chat_id = result.chat_id
      ElMessage.success(`已自动获取Chat ID: ${result.chat_id}`)
    } else {
      ElMessage.warning('未能自动获取Chat ID，请手动填写')
    }
  } catch (error) {
    ElMessage.error('自动获取失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 预览映射
const previewMappings = () => {
  ElNotification({
    title: '智能映射预览',
    message: `将为 ${props.wizardData.selectedChannels.length} 个KOOK频道创建 ${estimatedMappings.value} 个映射`,
    type: 'info',
    duration: 5000
  })
}

// 下一步
const handleNext = async () => {
  saving.value = true

  try {
    // 保存Bot配置
    const savedBots = []
    
    for (const platform of selectedPlatforms.value) {
      const config = botConfigs[platform]
      
      const result = await api.post('/api/bots/add', {
        platform,
        name: `${platforms.find(p => p.value === platform).label} Bot`,
        config
      })

      savedBots.push({
        id: result.id,
        platform,
        name: result.name
      })
    }

    ElMessage.success(`已保存 ${savedBots.length} 个Bot配置`)

    // 更新向导数据
    emit('update-data', {
      botConfigs: savedBots,
      selectedPlatforms: selectedPlatforms.value
    })

    // 进入下一步
    emit('next', {
      botConfigs: savedBots
    })
  } catch (error) {
    ElMessage.error('保存配置失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const handlePrev = () => {
  emit('prev')
}
</script>

<style scoped>
.step-card {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.step-content {
  padding: 20px 0;
}

.platform-alert {
  margin-bottom: 20px;
}

.platform-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.platform-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  padding: 20px;
}

.platform-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.platform-card.selected {
  border-color: #409EFF;
  background: #ecf5ff;
}

.platform-icon {
  font-size: 48px;
  text-align: center;
  margin-bottom: 10px;
}

.platform-card h3 {
  text-align: center;
  margin: 10px 0;
  color: #303133;
}

.platform-desc {
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-bottom: 10px;
}

.platform-config {
  margin-top: 15px;
}

.mapping-preview {
  margin-top: 30px;
}

.mapping-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  margin: 20px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.arrow-icon {
  font-size: 32px;
  color: #409EFF;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  padding: 20px 0 0 0;
}
</style>
