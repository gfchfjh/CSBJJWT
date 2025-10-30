<template>
  <div class="step-testing">
    <div class="testing-header">
      <h2>🧪 配置测试与验证</h2>
      <p class="subtitle">正在验证您的配置是否正确，请稍候...</p>
    </div>

    <!-- 测试进度总览 -->
    <el-card class="progress-card" shadow="hover">
      <div class="overall-progress">
        <el-progress 
          :percentage="overallProgress" 
          :status="overallStatus"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="progress-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        
        <div class="progress-summary">
          <el-tag :type="getSummaryType()" size="large">
            {{ getProgressText() }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 各项测试详情 -->
    <div class="test-items">
      <!-- 1. 环境检查 -->
      <el-card class="test-item" :class="getTestClass(environmentTest.status)">
        <div class="test-header">
          <div class="test-info">
            <el-icon :size="32">
              <component :is="getStatusIcon(environmentTest.status)" />
            </el-icon>
            <div>
              <h3>1️⃣ 环境检查</h3>
              <p class="test-desc">检查Redis、Chromium等依赖是否正常</p>
            </div>
          </div>
          <el-tag :type="getStatusType(environmentTest.status)" size="large">
            {{ getStatusText(environmentTest.status) }}
          </el-tag>
        </div>
        
        <el-collapse-transition>
          <div v-show="environmentTest.details" class="test-details">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item 
                v-for="(detail, key) in environmentTest.details"
                :key="key"
                :label="detail.label"
              >
                <el-tag :type="detail.passed ? 'success' : 'danger'" size="small">
                  {{ detail.passed ? '✅ 通过' : '❌ 失败' }}
                </el-tag>
                <span class="detail-message">{{ detail.message }}</span>
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 自动修复按钮 -->
            <el-button 
              v-if="environmentTest.status === 'failed' && environmentTest.autoFixAvailable"
              type="warning"
              size="small"
              :loading="environmentTest.autoFixing"
              @click="autoFixEnvironment"
              style="margin-top: 10px"
            >
              <el-icon><Tools /></el-icon>
              一键自动修复
            </el-button>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 2. KOOK账号测试 -->
      <el-card class="test-item" :class="getTestClass(accountTest.status)">
        <div class="test-header">
          <div class="test-info">
            <el-icon :size="32">
              <component :is="getStatusIcon(accountTest.status)" />
            </el-icon>
            <div>
              <h3>2️⃣ KOOK账号测试</h3>
              <p class="test-desc">验证账号登录状态和权限</p>
            </div>
          </div>
          <el-tag :type="getStatusType(accountTest.status)" size="large">
            {{ getStatusText(accountTest.status) }}
          </el-tag>
        </div>
        
        <el-collapse-transition>
          <div v-show="accountTest.accounts && accountTest.accounts.length > 0" class="test-details">
            <div v-for="account in accountTest.accounts" :key="account.id" class="account-test-item">
              <el-result
                :icon="account.passed ? 'success' : 'error'"
                :title="account.email"
                :sub-title="account.message"
              >
                <template #extra>
                  <el-descriptions :column="2" size="small" border>
                    <el-descriptions-item label="状态">
                      <el-tag :type="account.status === 'online' ? 'success' : 'danger'">
                        {{ account.status }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="监听服务器">
                      {{ account.server_count || 0 }} 个
                    </el-descriptions-item>
                    <el-descriptions-item label="监听频道">
                      {{ account.channel_count || 0 }} 个
                    </el-descriptions-item>
                    <el-descriptions-item label="响应时间">
                      {{ account.response_time || 'N/A' }}
                    </el-descriptions-item>
                  </el-descriptions>
                </template>
              </el-result>
            </div>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 3. Bot配置测试 -->
      <el-card class="test-item" :class="getTestClass(botTest.status)">
        <div class="test-header">
          <div class="test-info">
            <el-icon :size="32">
              <component :is="getStatusIcon(botTest.status)" />
            </el-icon>
            <div>
              <h3>3️⃣ 机器人配置测试</h3>
              <p class="test-desc">测试Discord/Telegram/飞书连接</p>
            </div>
          </div>
          <el-tag :type="getStatusType(botTest.status)" size="large">
            {{ getStatusText(botTest.status) }}
          </el-tag>
        </div>
        
        <el-collapse-transition>
          <div v-show="botTest.bots && botTest.bots.length > 0" class="test-details">
            <div v-for="bot in botTest.bots" :key="bot.id" class="bot-test-item">
              <div class="bot-test-header">
                <div>
                  <el-tag :type="bot.platform === 'discord' ? 'primary' : bot.platform === 'telegram' ? 'success' : 'warning'">
                    {{ bot.platform }}
                  </el-tag>
                  <strong>{{ bot.name }}</strong>
                </div>
                <el-tag :type="bot.passed ? 'success' : 'danger'">
                  {{ bot.passed ? '✅ 连接成功' : '❌ 连接失败' }}
                </el-tag>
              </div>
              
              <p class="bot-test-message">{{ bot.message }}</p>
              
              <el-alert
                v-if="!bot.passed && bot.solution"
                type="error"
                :title="bot.solution.title"
                :closable="false"
                show-icon
              >
                <template #default>
                  <ol class="solution-steps">
                    <li v-for="(step, idx) in bot.solution.steps" :key="idx">
                      {{ step }}
                    </li>
                  </ol>
                  <el-button 
                    v-if="bot.solution.autoFixAvailable"
                    type="primary"
                    size="small"
                    @click="autoFixBot(bot.id)"
                    style="margin-top: 10px"
                  >
                    立即修复
                  </el-button>
                </template>
              </el-alert>
            </div>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 4. 频道映射测试 -->
      <el-card class="test-item" :class="getTestClass(mappingTest.status)">
        <div class="test-header">
          <div class="test-info">
            <el-icon :size="32">
              <component :is="getStatusIcon(mappingTest.status)" />
            </el-icon>
            <div>
              <h3>4️⃣ 频道映射测试</h3>
              <p class="test-desc">验证映射配置是否有效</p>
            </div>
          </div>
          <el-tag :type="getStatusType(mappingTest.status)" size="large">
            {{ getStatusText(mappingTest.status) }}
          </el-tag>
        </div>
        
        <el-collapse-transition>
          <div v-show="mappingTest.mappings && mappingTest.mappings.length > 0" class="test-details">
            <el-alert
              type="info"
              :closable="false"
              style="margin-bottom: 15px"
            >
              <p>已配置 <strong>{{ mappingTest.mappings.length }}</strong> 个频道映射</p>
            </el-alert>
            
            <el-table :data="mappingTest.mappings" size="small" border>
              <el-table-column prop="kook_channel_name" label="KOOK频道" width="150" />
              <el-table-column prop="target_platform" label="目标平台" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.target_platform }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="target_channel_id" label="目标频道" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.valid ? 'success' : 'warning'" size="small">
                    {{ row.valid ? '有效' : '待验证' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 5. 实际消息发送测试 -->
      <el-card class="test-item" :class="getTestClass(messageTest.status)">
        <div class="test-header">
          <div class="test-info">
            <el-icon :size="32">
              <component :is="getStatusIcon(messageTest.status)" />
            </el-icon>
            <div>
              <h3>5️⃣ 真实消息发送测试 🎯</h3>
              <p class="test-desc">发送测试消息到所有配置的Bot</p>
            </div>
          </div>
          <el-tag :type="getStatusType(messageTest.status)" size="large">
            {{ getStatusText(messageTest.status) }}
          </el-tag>
        </div>
        
        <el-collapse-transition>
          <div v-show="messageTest.status !== 'pending'" class="test-details">
            <el-alert
              type="warning"
              :closable="false"
              style="margin-bottom: 15px"
            >
              <p>
                <el-icon><InfoFilled /></el-icon>
                我们将向您配置的所有Bot发送一条<strong>真实的测试消息</strong>，
                请在对应平台（Discord/Telegram/飞书）中查看是否收到消息。
              </p>
            </el-alert>
            
            <div v-if="messageTest.results && messageTest.results.length > 0">
              <div 
                v-for="result in messageTest.results" 
                :key="result.bot_id"
                class="message-result"
              >
                <el-result
                  :icon="result.success ? 'success' : 'error'"
                  :title="`${result.platform} - ${result.bot_name}`"
                  :sub-title="result.message"
                >
                  <template #extra>
                    <div v-if="result.success" class="success-info">
                      <el-alert type="success" :closable="false" show-icon>
                        <p>✅ 测试消息已成功发送！</p>
                        <p><strong>发送时间</strong>: {{ formatTime(result.sent_at) }}</p>
                        <p><strong>延迟</strong>: {{ result.latency }}ms</p>
                        <p><strong>消息ID</strong>: {{ result.message_id }}</p>
                      </el-alert>
                      
                      <el-button 
                        type="primary" 
                        plain
                        size="small"
                        @click="openPlatform(result.platform)"
                        style="margin-top: 10px"
                      >
                        <el-icon><View /></el-icon>
                        前往{{ result.platform }}查看
                      </el-button>
                    </div>
                    
                    <div v-else class="error-info">
                      <el-alert type="error" :closable="false" show-icon>
                        <p><strong>错误原因</strong>: {{ result.error }}</p>
                      </el-alert>
                      
                      <el-button 
                        type="warning"
                        size="small"
                        @click="retryBot(result.bot_id)"
                        :loading="retryingBots[result.bot_id]"
                        style="margin-top: 10px"
                      >
                        <el-icon><RefreshRight /></el-icon>
                        重新测试
                      </el-button>
                      
                      <el-button 
                        size="small"
                        @click="showErrorSolution(result)"
                        style="margin-top: 10px"
                      >
                        <el-icon><QuestionFilled /></el-icon>
                        查看解决方案
                      </el-button>
                    </div>
                  </template>
                </el-result>
              </div>
            </div>
            
            <!-- 重新测试所有 -->
            <div class="retry-all" v-if="messageTest.status === 'failed'">
              <el-button 
                type="primary"
                size="large"
                :loading="retestingAll"
                @click="retestAll"
              >
                <el-icon><RefreshRight /></el-icon>
                重新测试所有配置
              </el-button>
            </div>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>

    <!-- 测试结果总结 -->
    <el-card class="summary-card" v-if="testingComplete">
      <template #header>
        <span>📊 测试结果总结</span>
      </template>
      
      <el-result
        :icon="allTestsPassed ? 'success' : 'warning'"
        :title="allTestsPassed ? '🎉 所有测试通过！' : '⚠️ 部分测试未通过'"
        :sub-title="getSummaryMessage()"
      >
        <template #extra>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="环境检查">
              <el-tag :type="environmentTest.status === 'passed' ? 'success' : 'danger'">
                {{ environmentTest.status === 'passed' ? '✅ 通过' : '❌ 失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="账号验证">
              <el-tag :type="accountTest.status === 'passed' ? 'success' : 'danger'">
                {{ accountTest.passedCount }}/{{ accountTest.totalCount }} 通过
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Bot配置">
              <el-tag :type="botTest.status === 'passed' ? 'success' : 'danger'">
                {{ botTest.passedCount }}/{{ botTest.totalCount }} 通过
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="消息发送">
              <el-tag :type="messageTest.status === 'passed' ? 'success' : 'danger'">
                {{ messageTest.passedCount }}/{{ messageTest.totalCount }} 成功
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="summary-actions">
            <el-button 
              v-if="allTestsPassed"
              type="success"
              size="large"
              @click="completeWizard"
            >
              <el-icon><CircleCheck /></el-icon>
              完成配置，开始使用
            </el-button>
            
            <el-button 
              v-else
              type="primary"
              size="large"
              @click="handlePartialSuccess"
            >
              <el-icon><Warning /></el-icon>
              部分通过，继续使用
            </el-button>
            
            <el-button 
              size="large"
              @click="backToConfig"
            >
              <el-icon><Back /></el-icon>
              返回修改配置
            </el-button>
          </div>
        </template>
      </el-result>
    </el-card>

    <!-- 测试日志（可展开） -->
    <el-card class="log-card" v-if="testLogs.length > 0">
      <template #header>
        <div class="log-header">
          <span>📝 测试日志</span>
          <el-button size="small" @click="exportLogs">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
        </div>
      </template>
      
      <div class="log-content">
        <div 
          v-for="(log, index) in testLogs" 
          :key="index"
          class="log-entry"
          :class="log.level"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <el-tag :type="getLogType(log.level)" size="small">{{ log.level }}</el-tag>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  Loading,
  CircleCheck,
  CircleClose,
  Warning,
  InfoFilled,
  Tools,
  RefreshRight,
  QuestionFilled,
  View,
  Back,
  Download
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['complete', 'back'])

// 测试状态
const environmentTest = ref({
  status: 'testing', // pending, testing, passed, failed
  details: null,
  autoFixAvailable: false,
  autoFixing: false
})

const accountTest = ref({
  status: 'pending',
  accounts: [],
  passedCount: 0,
  totalCount: 0
})

const botTest = ref({
  status: 'pending',
  bots: [],
  passedCount: 0,
  totalCount: 0
})

const mappingTest = ref({
  status: 'pending',
  mappings: [],
  validCount: 0,
  totalCount: 0
})

const messageTest = ref({
  status: 'pending',
  results: [],
  passedCount: 0,
  totalCount: 0
})

const testLogs = ref([])
const retryingBots = ref({})
const retestingAll = ref(false)

// 计算测试进度
const overallProgress = computed(() => {
  const steps = [
    environmentTest.value.status,
    accountTest.value.status,
    botTest.value.status,
    mappingTest.value.status,
    messageTest.value.status
  ]
  
  const completed = steps.filter(s => s === 'passed' || s === 'failed').length
  return Math.round((completed / 5) * 100)
})

const overallStatus = computed(() => {
  if (overallProgress.value === 100) {
    return allTestsPassed.value ? 'success' : 'exception'
  }
  return undefined
})

const testingComplete = computed(() => {
  return overallProgress.value === 100
})

const allTestsPassed = computed(() => {
  return (
    environmentTest.value.status === 'passed' &&
    accountTest.value.status === 'passed' &&
    botTest.value.status === 'passed' &&
    messageTest.value.status === 'passed'
  )
})

// 辅助函数
const getStatusIcon = (status) => {
  const iconMap = {
    pending: 'Clock',
    testing: 'Loading',
    passed: 'CircleCheck',
    failed: 'CircleClose'
  }
  return iconMap[status] || 'Clock'
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    testing: 'warning',
    passed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待中',
    testing: '测试中',
    passed: '✅ 通过',
    failed: '❌ 失败'
  }
  return textMap[status] || '未知'
}

const getTestClass = (status) => {
  return {
    'test-pending': status === 'pending',
    'test-testing': status === 'testing',
    'test-passed': status === 'passed',
    'test-failed': status === 'failed'
  }
}

const getSummaryType = () => {
  if (overallProgress.value < 100) return 'warning'
  return allTestsPassed.value ? 'success' : 'danger'
}

const getProgressText = () => {
  if (overallProgress.value < 100) {
    return '测试进行中...'
  }
  return allTestsPassed.value ? '所有测试通过' : '部分测试失败'
}

const getLogType = (level) => {
  const typeMap = {
    info: 'info',
    success: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return typeMap[level] || 'info'
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

const getSummaryMessage = () => {
  if (allTestsPassed.value) {
    return '恭喜！所有配置测试通过，您可以开始使用系统了'
  }
  
  const failedTests = []
  if (environmentTest.value.status === 'failed') failedTests.push('环境')
  if (accountTest.value.status === 'failed') failedTests.push('账号')
  if (botTest.value.status === 'failed') failedTests.push('Bot')
  if (messageTest.value.status === 'failed') failedTests.push('消息发送')
  
  return `${failedTests.join('、')}测试未通过，建议修复后再使用`
}

// 添加日志
const addLog = (level, message) => {
  testLogs.value.push({
    timestamp: new Date().toISOString(),
    level,
    message
  })
}

// 执行测试序列
const runTests = async () => {
  addLog('info', '开始配置测试...')
  
  // 1. 环境检查
  await testEnvironment()
  
  // 2. 账号测试
  await testAccounts()
  
  // 3. Bot测试
  await testBots()
  
  // 4. 映射测试
  await testMappings()
  
  // 5. 真实消息测试
  await testMessageSending()
  
  addLog('success', '所有测试完成')
}

// 1. 环境检查
const testEnvironment = async () => {
  try {
    environmentTest.value.status = 'testing'
    addLog('info', '正在检查环境...')
    
    const result = await api.checkEnvironment()
    
    environmentTest.value.details = {
      redis: {
        label: 'Redis服务',
        passed: result.redis_available,
        message: result.redis_message || 'Redis运行正常'
      },
      chromium: {
        label: 'Chromium浏览器',
        passed: result.chromium_available,
        message: result.chromium_message || 'Chromium已安装'
      },
      disk: {
        label: '磁盘空间',
        passed: result.disk_available,
        message: `可用空间: ${result.disk_free_gb}GB`
      },
      network: {
        label: '网络连接',
        passed: result.network_available,
        message: result.network_message || '网络连接正常'
      }
    }
    
    const allPassed = Object.values(environmentTest.value.details).every(d => d.passed)
    
    if (allPassed) {
      environmentTest.value.status = 'passed'
      addLog('success', '✅ 环境检查通过')
    } else {
      environmentTest.value.status = 'failed'
      environmentTest.value.autoFixAvailable = result.auto_fix_available
      addLog('error', '❌ 环境检查失败')
    }
  } catch (error) {
    environmentTest.value.status = 'failed'
    addLog('error', `环境检查异常: ${error.message}`)
  }
}

// 2. 账号测试
const testAccounts = async () => {
  try {
    accountTest.value.status = 'testing'
    addLog('info', '正在测试KOOK账号...')
    
    const accounts = await api.getAccounts()
    accountTest.value.totalCount = accounts.length
    
    if (accounts.length === 0) {
      accountTest.value.status = 'failed'
      addLog('error', '未配置任何KOOK账号')
      return
    }
    
    // 测试每个账号
    const testPromises = accounts.map(async (account) => {
      try {
        const testResult = await api.testAccount(account.id)
        return {
          id: account.id,
          email: account.email,
          status: account.status,
          passed: testResult.success,
          message: testResult.message,
          server_count: testResult.server_count || 0,
          channel_count: testResult.channel_count || 0,
          response_time: testResult.response_time ? `${testResult.response_time}ms` : 'N/A'
        }
      } catch (error) {
        return {
          id: account.id,
          email: account.email,
          status: 'offline',
          passed: false,
          message: error.message || '测试失败',
          server_count: 0,
          channel_count: 0,
          response_time: 'N/A'
        }
      }
    })
    
    accountTest.value.accounts = await Promise.all(testPromises)
    accountTest.value.passedCount = accountTest.value.accounts.filter(a => a.passed).length
    
    if (accountTest.value.passedCount > 0) {
      accountTest.value.status = 'passed'
      addLog('success', `✅ ${accountTest.value.passedCount}/${accountTest.value.totalCount} 个账号测试通过`)
    } else {
      accountTest.value.status = 'failed'
      addLog('error', '❌ 所有账号测试失败')
    }
  } catch (error) {
    accountTest.value.status = 'failed'
    addLog('error', `账号测试异常: ${error.message}`)
  }
}

// 3. Bot配置测试
const testBots = async () => {
  try {
    botTest.value.status = 'testing'
    addLog('info', '正在测试Bot配置...')
    
    const bots = await api.getBotConfigs()
    botTest.value.totalCount = bots.length
    
    if (bots.length === 0) {
      botTest.value.status = 'failed'
      addLog('error', '未配置任何Bot')
      return
    }
    
    // 测试每个Bot
    const testPromises = bots.map(async (bot) => {
      try {
        const testResult = await api.testBot({
          platform: bot.platform,
          config: bot.config
        })
        
        return {
          id: bot.id,
          name: bot.name,
          platform: bot.platform,
          passed: testResult.success,
          message: testResult.message || '连接成功',
          solution: testResult.solution || null
        }
      } catch (error) {
        return {
          id: bot.id,
          name: bot.name,
          platform: bot.platform,
          passed: false,
          message: error.message || '连接失败',
          error: error.response?.data?.detail || error.message,
          solution: {
            title: '连接失败',
            steps: [
              '1. 检查网络连接是否正常',
              '2. 验证Bot配置信息是否正确',
              '3. 确认Bot权限是否足够',
              '4. 查看详细错误日志'
            ],
            autoFixAvailable: false
          }
        }
      }
    })
    
    botTest.value.bots = await Promise.all(testPromises)
    botTest.value.passedCount = botTest.value.bots.filter(b => b.passed).length
    
    if (botTest.value.passedCount > 0) {
      botTest.value.status = 'passed'
      addLog('success', `✅ ${botTest.value.passedCount}/${botTest.value.totalCount} 个Bot测试通过`)
    } else {
      botTest.value.status = 'failed'
      addLog('error', '❌ 所有Bot测试失败')
    }
  } catch (error) {
    botTest.value.status = 'failed'
    addLog('error', `Bot测试异常: ${error.message}`)
  }
}

// 4. 映射测试
const testMappings = async () => {
  try {
    mappingTest.value.status = 'testing'
    addLog('info', '正在验证频道映射...')
    
    const mappings = await api.getMappings()
    mappingTest.value.totalCount = mappings.length
    
    if (mappings.length === 0) {
      mappingTest.value.status = 'failed'
      addLog('warning', '⚠️ 未配置任何频道映射')
      return
    }
    
    // 验证映射有效性
    mappingTest.value.mappings = mappings.map(mapping => ({
      ...mapping,
      valid: mapping.enabled && mapping.kook_channel_id && mapping.target_channel_id
    }))
    
    mappingTest.value.validCount = mappingTest.value.mappings.filter(m => m.valid).length
    
    if (mappingTest.value.validCount > 0) {
      mappingTest.value.status = 'passed'
      addLog('success', `✅ ${mappingTest.value.validCount}/${mappingTest.value.totalCount} 个映射有效`)
    } else {
      mappingTest.value.status = 'failed'
      addLog('error', '❌ 所有映射无效')
    }
  } catch (error) {
    mappingTest.value.status = 'failed'
    addLog('error', `映射验证异常: ${error.message}`)
  }
}

// 5. 真实消息发送测试
const testMessageSending = async () => {
  try {
    messageTest.value.status = 'testing'
    addLog('info', '正在发送测试消息...')
    
    const bots = botTest.value.bots.filter(b => b.passed)
    messageTest.value.totalCount = bots.length
    
    if (bots.length === 0) {
      messageTest.value.status = 'failed'
      addLog('error', '没有可用的Bot，跳过消息测试')
      return
    }
    
    // 向每个Bot发送测试消息
    const sendPromises = bots.map(async (bot) => {
      try {
        const testMessage = {
          content: `🧪 KOOK消息转发系统 - 测试消息\n\n` +
                   `✅ 如果您看到这条消息，说明配置成功！\n` +
                   `⏰ 发送时间: ${new Date().toLocaleString('zh-CN')}\n` +
                   `🤖 Bot: ${bot.name}\n` +
                   `📋 平台: ${bot.platform}\n\n` +
                   `📝 这是一条自动发送的测试消息，可以忽略。`,
          platform: bot.platform,
          bot_id: bot.id
        }
        
        const result = await api.sendTestMessage(testMessage)
        
        return {
          bot_id: bot.id,
          bot_name: bot.name,
          platform: bot.platform,
          success: true,
          message: '测试消息发送成功',
          sent_at: new Date().toISOString(),
          latency: result.latency || 0,
          message_id: result.message_id
        }
      } catch (error) {
        return {
          bot_id: bot.id,
          bot_name: bot.name,
          platform: bot.platform,
          success: false,
          message: '测试消息发送失败',
          error: error.response?.data?.detail || error.message
        }
      }
    })
    
    messageTest.value.results = await Promise.all(sendPromises)
    messageTest.value.passedCount = messageTest.value.results.filter(r => r.success).length
    
    if (messageTest.value.passedCount > 0) {
      messageTest.value.status = 'passed'
      addLog('success', `✅ ${messageTest.value.passedCount}/${messageTest.value.totalCount} 条测试消息发送成功`)
      
      // 显示通知
      ElNotification({
        title: '🎉 测试消息已发送',
        message: `成功向 ${messageTest.value.passedCount} 个平台发送测试消息，请在对应平台查看`,
        type: 'success',
        duration: 10000
      })
    } else {
      messageTest.value.status = 'failed'
      addLog('error', '❌ 所有测试消息发送失败')
    }
  } catch (error) {
    messageTest.value.status = 'failed'
    addLog('error', `消息测试异常: ${error.message}`)
  }
}

// 自动修复环境
const autoFixEnvironment = async () => {
  try {
    environmentTest.value.autoFixing = true
    addLog('info', '正在自动修复环境问题...')
    
    const result = await api.autoFixEnvironment()
    
    if (result.success) {
      ElMessage.success('环境问题已自动修复')
      addLog('success', '✅ 环境自动修复成功')
      
      // 重新测试环境
      await testEnvironment()
    } else {
      ElMessage.error(`自动修复失败: ${result.message}`)
      addLog('error', `❌ 自动修复失败: ${result.message}`)
    }
  } catch (error) {
    ElMessage.error(`自动修复异常: ${error.message}`)
    addLog('error', `自动修复异常: ${error.message}`)
  } finally {
    environmentTest.value.autoFixing = false
  }
}

// 重试单个Bot
const retryBot = async (botId) => {
  try {
    retryingBots.value[botId] = true
    addLog('info', `重新测试Bot ${botId}...`)
    
    // 重新执行Bot测试
    await testBots()
  } catch (error) {
    ElMessage.error(`重试失败: ${error.message}`)
  } finally {
    retryingBots.value[botId] = false
  }
}

// 重新测试所有
const retestAll = async () => {
  try {
    retestingAll.value = true
    addLog('info', '重新测试所有配置...')
    
    await runTests()
  } catch (error) {
    ElMessage.error(`重新测试失败: ${error.message}`)
  } finally {
    retestingAll.value = false
  }
}

// 显示错误解决方案
const showErrorSolution = (result) => {
  if (!result.solution) {
    ElMessage.info('暂无解决方案')
    return
  }
  
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <p><strong>错误原因：</strong>${result.error}</p>
      <h4>解决步骤：</h4>
      <ol>
        ${result.solution.steps.map(step => `<li>${step}</li>`).join('')}
      </ol>
    </div>`,
    `${result.platform} - ${result.bot_name}`,
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '知道了'
    }
  )
}

// 打开平台
const openPlatform = (platform) => {
  const urls = {
    discord: 'https://discord.com/channels/@me',
    telegram: 'https://web.telegram.org',
    feishu: 'https://www.feishu.cn'
  }
  
  const url = urls[platform]
  if (url) {
    window.open(url, '_blank')
  }
}

// 完成向导
const completeWizard = () => {
  ElMessageBox.confirm(
    '配置测试全部通过！\n\n点击"开始使用"后，系统将自动开始监听和转发消息。',
    '🎉 配置完成',
    {
      confirmButtonText: '开始使用',
      cancelButtonText: '稍后',
      type: 'success'
    }
  ).then(() => {
    emit('complete')
  })
}

// 部分通过的处理
const handlePartialSuccess = () => {
  ElMessageBox.confirm(
    '部分测试未通过，但您仍然可以使用系统。\n\n' +
    '未通过的功能将不可用，建议修复后再使用。\n\n' +
    '是否继续？',
    '⚠️ 部分功能不可用',
    {
      confirmButtonText: '继续使用',
      cancelButtonText: '返回修复',
      type: 'warning'
    }
  ).then(() => {
    emit('complete')
  })
}

// 返回配置
const backToConfig = () => {
  emit('back')
}

// 导出日志
const exportLogs = () => {
  const logText = testLogs.value.map(log => 
    `[${formatTime(log.timestamp)}] [${log.level.toUpperCase()}] ${log.message}`
  ).join('\n')
  
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test-log-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('日志已导出')
}

// 组件挂载时自动开始测试
onMounted(() => {
  // 延迟500ms开始测试，让用户看到初始状态
  setTimeout(() => {
    runTests()
  }, 500)
})
</script>

<style scoped>
.step-testing {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.testing-header {
  text-align: center;
  margin-bottom: 30px;
}

.testing-header h2 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px 0;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.progress-card {
  margin-bottom: 30px;
}

.overall-progress {
  padding: 20px;
}

.progress-summary {
  margin-top: 20px;
  text-align: center;
}

.test-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.test-item {
  transition: all 0.3s ease;
}

.test-item.test-testing {
  border-left: 4px solid #E6A23C;
  animation: pulse 2s infinite;
}

.test-item.test-passed {
  border-left: 4px solid #67C23A;
}

.test-item.test-failed {
  border-left: 4px solid #F56C6C;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(230, 162, 60, 0);
  }
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.test-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #303133;
}

.test-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.test-details {
  padding-top: 15px;
  border-top: 1px dashed #DCDFE6;
  margin-top: 15px;
}

.detail-message {
  margin-left: 10px;
  color: #606266;
}

.account-test-item,
.bot-test-item,
.message-result {
  margin-bottom: 20px;
  padding: 15px;
  background: #F5F7FA;
  border-radius: 8px;
}

.account-test-item:last-child,
.bot-test-item:last-child,
.message-result:last-child {
  margin-bottom: 0;
}

.bot-test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.bot-test-message {
  color: #606266;
  margin: 10px 0;
}

.solution-steps {
  margin: 10px 0;
  padding-left: 20px;
}

.solution-steps li {
  margin: 5px 0;
  line-height: 1.6;
}

.success-info,
.error-info {
  margin-top: 15px;
}

.retry-all {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #DCDFE6;
}

.summary-card {
  margin-bottom: 30px;
}

.summary-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.log-card {
  max-height: 400px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.log-entry {
  padding: 8px 12px;
  border-left: 3px solid transparent;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-entry.info {
  border-left-color: #909399;
  background: #F4F4F5;
}

.log-entry.success {
  border-left-color: #67C23A;
  background: #F0F9FF;
}

.log-entry.warning {
  border-left-color: #E6A23C;
  background: #FDF6EC;
}

.log-entry.error {
  border-left-color: #F56C6C;
  background: #FEF0F0;
}

.log-time {
  color: #909399;
  font-size: 12px;
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: #303133;
}

.progress-text {
  font-size: 18px;
  font-weight: bold;
}
</style>
