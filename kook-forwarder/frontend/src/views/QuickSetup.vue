<template>
  <div class="quick-setup-container">
    <el-card class="setup-card">
      <template #header>
        <div class="setup-header">
          <h2>⚡ 快速配置向导</h2>
          <p>仅需3步，5分钟完成配置</p>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="配置机器人" description="添加转发目标" />
        <el-step title="设置映射" description="频道映射规则" />
        <el-step title="测试验证" description="确认配置" />
      </el-steps>

      <div class="setup-content">
        <!-- 步骤1: 配置机器人 -->
        <div v-if="currentStep === 0" class="step-bots">
          <h3>📱 选择要配置的平台</h3>
          <p class="step-desc">选择您想要转发消息到的平台（可多选）</p>

          <el-row :gutter="20" class="platform-selection">
            <el-col :span="8" v-for="platform in platforms" :key="platform.value">
              <el-card
                :class="['platform-card', { selected: platform.selected }]"
                shadow="hover"
                @click="togglePlatform(platform.value)"
              >
                <div class="platform-content">
                  <div class="platform-icon">{{ platform.icon }}</div>
                  <h4>{{ platform.label }}</h4>
                  <p>{{ platform.description }}</p>
                  <el-checkbox v-model="platform.selected" />
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 配置表单 -->
          <div v-if="selectedPlatforms.length > 0" class="bot-config-forms">
            <el-divider />
            <h3>🔧 配置选中的平台</h3>

            <!-- Discord配置 -->
            <el-card v-if="isPlatformSelected('discord')" class="config-card">
              <template #header>
                <span>Discord 配置</span>
              </template>
              <el-form label-width="120px">
                <el-form-item label="Bot名称">
                  <el-input v-model="botConfigs.discord.name" placeholder="例如：游戏公告Bot" />
                </el-form-item>
                <el-form-item label="Webhook URL">
                  <el-input
                    v-model="botConfigs.discord.webhook_url"
                    type="textarea"
                    :rows="2"
                    placeholder="https://discord.com/api/webhooks/..."
                  />
                </el-form-item>
                <el-form-item>
                  <el-link type="primary" @click="openTutorial('discord')">
                    📖 如何获取Discord Webhook？
                  </el-link>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- Telegram配置 -->
            <el-card v-if="isPlatformSelected('telegram')" class="config-card">
              <template #header>
                <span>Telegram 配置</span>
              </template>
              <el-form label-width="120px">
                <el-form-item label="Bot名称">
                  <el-input v-model="botConfigs.telegram.name" placeholder="例如：游戏公告TG Bot" />
                </el-form-item>
                <el-form-item label="Bot Token">
                  <el-input
                    v-model="botConfigs.telegram.token"
                    type="textarea"
                    :rows="2"
                    placeholder="1234567890:ABCdefGHIjklMNOpqrs..."
                  />
                </el-form-item>
                <el-form-item label="Chat ID">
                  <el-input v-model="botConfigs.telegram.chat_id" placeholder="-1001234567890">
                    <template #append>
                      <el-button
                        type="success"
                        :disabled="!botConfigs.telegram.token"
                        @click="autoDetectChatId"
                      >
                        自动获取
                      </el-button>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-link type="primary" @click="openTutorial('telegram')">
                    📖 如何创建Telegram Bot？
                  </el-link>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 飞书配置 -->
            <el-card v-if="isPlatformSelected('feishu')" class="config-card">
              <template #header>
                <span>飞书 配置</span>
              </template>
              <el-form label-width="120px">
                <el-form-item label="应用名称">
                  <el-input v-model="botConfigs.feishu.name" placeholder="例如：游戏公告飞书Bot" />
                </el-form-item>
                <el-form-item label="App ID">
                  <el-input v-model="botConfigs.feishu.app_id" placeholder="cli_a1b2c3d4e5f6g7h8" />
                </el-form-item>
                <el-form-item label="App Secret">
                  <el-input v-model="botConfigs.feishu.app_secret" placeholder="ABCdefGHIjklMNOpqrs" />
                </el-form-item>
                <el-form-item>
                  <el-link type="primary" @click="openTutorial('feishu')">
                    📖 如何创建飞书自建应用？
                  </el-link>
                </el-form-item>
              </el-form>
            </el-card>
          </div>

          <div class="step-actions">
            <el-button @click="skipSetup">跳过，稍后配置</el-button>
            <el-button
              type="primary"
              :disabled="selectedPlatforms.length === 0"
              @click="saveBotsAndNext"
            >
              下一步：设置映射
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 智能映射 -->
        <div v-if="currentStep === 1" class="step-mapping">
          <h3>🔀 频道映射配置</h3>
          <p class="step-desc">将KOOK频道映射到目标平台</p>

          <el-alert type="info" :closable="false" style="margin-bottom: 20px">
            <template #title>
              💡 智能映射会自动匹配同名频道，您也可以手动调整
            </template>
          </el-alert>

          <el-button type="success" @click="runSmartMapping" :loading="smartMappingRunning">
            <el-icon><MagicStick /></el-icon>
            一键智能映射
          </el-button>

          <!-- 映射预览 -->
          <div v-if="mappingPreview.length > 0" class="mapping-preview">
            <h4>映射预览（共{{ mappingPreview.length }}条）</h4>
            <el-table :data="mappingPreview" border>
              <el-table-column prop="source" label="KOOK频道" width="200" />
              <el-table-column prop="targets" label="转发目标">
                <template #default="{ row }">
                  <el-tag v-for="target in row.targets" :key="target" style="margin-right: 5px">
                    {{ target }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="置信度" width="100">
                <template #default="{ row }">
                  <el-tag :type="getConfidenceType(row.confidence)">
                    {{ row.confidence }}%
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" :disabled="mappingPreview.length === 0" @click="nextStep">
              下一步：测试验证
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 测试验证 -->
        <div v-if="currentStep === 2" class="step-testing">
          <h3>🧪 配置测试验证</h3>
          <p class="step-desc">测试所有配置是否正常工作</p>

          <el-button type="primary" size="large" @click="runTests" :loading="testing">
            <el-icon><Checked /></el-icon>
            开始测试
          </el-button>

          <!-- 测试结果 -->
          <div v-if="testResults.length > 0" class="test-results">
            <el-timeline>
              <el-timeline-item
                v-for="(result, index) in testResults"
                :key="index"
                :timestamp="result.time"
                :type="result.success ? 'success' : 'danger'"
                :icon="result.success ? 'Check' : 'Close'"
              >
                <h4>{{ result.title }}</h4>
                <p>{{ result.message }}</p>
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button
              type="success"
              size="large"
              :disabled="!allTestsPassed"
              @click="completeSetup"
            >
              <el-icon><SuccessFilled /></el-icon>
              完成配置，开始使用
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Checked, SuccessFilled } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 平台配置
const platforms = ref([
  {
    value: 'discord',
    label: 'Discord',
    icon: '💬',
    description: 'Webhook方式，配置简单',
    selected: false
  },
  {
    value: 'telegram',
    label: 'Telegram',
    icon: '✈️',
    description: 'Bot API，支持HTML格式',
    selected: false
  },
  {
    value: 'feishu',
    label: '飞书',
    icon: '🏢',
    description: '自建应用，支持消息卡片',
    selected: false
  }
])

// Bot配置
const botConfigs = ref({
  discord: { name: '', webhook_url: '' },
  telegram: { name: '', token: '', chat_id: '' },
  feishu: { name: '', app_id: '', app_secret: '' }
})

// 智能映射
const smartMappingRunning = ref(false)
const mappingPreview = ref([])

// 测试
const testing = ref(false)
const testResults = ref([])

// 计算属性
const selectedPlatforms = computed(() => 
  platforms.value.filter(p => p.selected).map(p => p.value)
)

const allTestsPassed = computed(() => 
  testResults.value.length > 0 && testResults.value.every(r => r.success)
)

// 切换平台选择
function togglePlatform(platform) {
  const p = platforms.value.find(item => item.value === platform)
  if (p) {
    p.selected = !p.selected
  }
}

// 判断平台是否选中
function isPlatformSelected(platform) {
  return selectedPlatforms.value.includes(platform)
}

// 保存Bot配置并进入下一步
async function saveBotsAndNext() {
  // 验证配置
  const errors = []
  
  selectedPlatforms.value.forEach(platform => {
    const config = botConfigs.value[platform]
    if (!config.name) {
      errors.push(`${platform} 的名称不能为空`)
    }
    
    if (platform === 'discord' && !config.webhook_url) {
      errors.push('Discord Webhook URL 不能为空')
    }
    if (platform === 'telegram' && (!config.token || !config.chat_id)) {
      errors.push('Telegram Bot Token 和 Chat ID 不能为空')
    }
    if (platform === 'feishu' && (!config.app_id || !config.app_secret)) {
      errors.push('飞书 App ID 和 App Secret 不能为空')
    }
  })
  
  if (errors.length > 0) {
    ElMessage.error(errors.join('\n'))
    return
  }
  
  // 保存配置
  try {
    for (const platform of selectedPlatforms.value) {
      await api.post('/api/bots', {
        platform,
        name: botConfigs.value[platform].name,
        config: botConfigs.value[platform]
      })
    }
    
    ElMessage.success('Bot配置保存成功！')
    localStorage.setItem('has_configured_bots', 'true')
    nextStep()
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 运行智能映射
async function runSmartMapping() {
  smartMappingRunning.value = true
  try {
    const response = await api.post('/api/smart-mapping/auto-map')
    mappingPreview.value = response.data.mappings
    ElMessage.success(`智能映射完成！共生成${mappingPreview.value.length}条映射`)
  } catch (error) {
    ElMessage.error('智能映射失败: ' + error.message)
  } finally {
    smartMappingRunning.value = false
  }
}

// 获取置信度标签类型
function getConfidenceType(confidence) {
  if (confidence >= 80) return 'success'
  if (confidence >= 60) return 'warning'
  return 'danger'
}

// 自动检测Telegram Chat ID
async function autoDetectChatId() {
  try {
    const response = await api.post('/api/telegram/detect-chat-id', {
      token: botConfigs.value.telegram.token
    })
    botConfigs.value.telegram.chat_id = response.data.chat_id
    ElMessage.success('Chat ID 获取成功！')
  } catch (error) {
    ElMessage.error('获取失败: ' + error.message)
  }
}

// 运行测试
async function runTests() {
  testing.value = true
  testResults.value = []
  
  const tests = [
    { title: '环境检查', endpoint: '/api/wizard-testing-enhanced/test-environment' },
    { title: 'KOOK账号测试', endpoint: '/api/wizard-testing-enhanced/test-kook-account' },
    { title: 'Bot配置测试', endpoint: '/api/wizard-testing-enhanced/test-bots' },
    { title: '频道映射验证', endpoint: '/api/wizard-testing-enhanced/test-mappings' },
    { title: '真实消息发送', endpoint: '/api/wizard-testing-enhanced/test-real-message' }
  ]
  
  for (const test of tests) {
    try {
      const response = await api.post(test.endpoint)
      testResults.value.push({
        title: test.title,
        message: response.data.message || '测试通过',
        success: response.data.success,
        time: new Date().toLocaleTimeString()
      })
    } catch (error) {
      testResults.value.push({
        title: test.title,
        message: error.message || '测试失败',
        success: false,
        time: new Date().toLocaleTimeString()
      })
    }
    
    // 延迟一下，让用户看到进度
    await new Promise(resolve => setTimeout(resolve, 500))
  }
  
  testing.value = false
  
  if (allTestsPassed.value) {
    ElMessage.success('所有测试通过！')
  } else {
    ElMessage.warning('部分测试未通过，请检查配置')
  }
}

// 完成配置
async function completeSetup() {
  await ElMessageBox.alert(
    '🎉 恭喜！所有配置已完成。\n\n您现在可以：\n1. 在主界面启动转发服务\n2. 在日志页面查看转发记录\n3. 随时在设置中调整配置',
    '配置完成',
    {
      confirmButtonText: '进入主界面',
      type: 'success'
    }
  )
  
  localStorage.setItem('quick_setup_completed', 'true')
  router.push('/')
}

// 跳过配置
async function skipSetup() {
  try {
    await ElMessageBox.confirm(
      '跳过后您可以随时在设置中配置。确定要跳过吗？',
      '确认跳过',
      {
        type: 'warning'
      }
    )
    router.push('/')
  } catch {
    // 用户取消
  }
}

// 打开教程
function openTutorial(platform) {
  window.open(`/help/tutorials/${platform}`, '_blank')
}

// 下一步
function nextStep() {
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

// 上一步
function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}
</script>

<style scoped>
.quick-setup-container {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.setup-card {
  max-width: 1200px;
  margin: 0 auto;
}

.setup-header {
  text-align: center;
}

.setup-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.setup-header p {
  margin: 0;
  color: #909399;
}

.setup-content {
  margin-top: 40px;
  min-height: 400px;
}

.step-desc {
  text-align: center;
  color: #606266;
  margin-bottom: 30px;
}

.platform-selection {
  margin: 30px 0;
}

.platform-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 200px;
}

.platform-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.platform-card.selected {
  border: 2px solid #409EFF;
  background: #ecf5ff;
}

.platform-content {
  text-align: center;
}

.platform-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.platform-content h4 {
  margin: 10px 0;
  font-size: 18px;
}

.platform-content p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.bot-config-forms {
  margin-top: 30px;
}

.config-card {
  margin-bottom: 20px;
}

.mapping-preview {
  margin-top: 30px;
}

.test-results {
  margin-top: 30px;
  max-height: 400px;
  overflow-y: auto;
}

.step-actions {
  margin-top: 40px;
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
}
</style>
