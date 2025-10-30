<template>
  <div class="wizard-testing-ultimate">
    <!-- ✅ P0-2深度优化：完整的5项测试向导 -->
    
    <div class="testing-header">
      <h2>🧪 配置测试验证</h2>
      <p>我们将进行5项全面测试，确保您的配置正确无误</p>
    </div>
    
    <!-- 总体进度 -->
    <el-card class="progress-card">
      <el-progress 
        :percentage="overallProgress" 
        :status="progressStatus"
        :stroke-width="24"
        :text-inside="true"
      />
      <div class="progress-info">
        <span v-if="testing">⏳ 测试进行中...</span>
        <span v-else-if="testComplete && overallSuccess">
          ✅ 全部测试通过！配置完美！
        </span>
        <span v-else-if="testComplete && !overallSuccess" class="warning">
          ⚠️  部分测试失败，请查看详情
        </span>
        <span v-else>准备开始测试</span>
      </div>
    </el-card>
    
    <!-- 测试项列表 -->
    <div class="test-items">
      <el-card 
        v-for="(test, index) in tests" 
        :key="test.name"
        class="test-item"
        :class="getTestClass(test)"
      >
        <div class="test-header">
          <div class="test-icon-wrapper">
            <el-icon 
              v-if="test.status === 'success'" 
              class="test-icon success"
              :size="32"
            >
              <CircleCheck />
            </el-icon>
            <el-icon 
              v-else-if="test.status === 'failed'" 
              class="test-icon failed"
              :size="32"
            >
              <CircleClose />
            </el-icon>
            <el-icon 
              v-else-if="test.status === 'testing'" 
              class="test-icon testing rotating"
              :size="32"
            >
              <Loading />
            </el-icon>
            <el-icon 
              v-else 
              class="test-icon pending"
              :size="32"
            >
              <Clock />
            </el-icon>
          </div>
          
          <div class="test-info">
            <h3>{{ index + 1 }}. {{ test.name }}</h3>
            <div class="test-description">{{ test.description }}</div>
          </div>
          
          <div class="test-duration" v-if="test.duration_ms">
            <el-tag size="small">{{ test.duration_ms }}ms</el-tag>
          </div>
        </div>
        
        <!-- 测试详情 -->
        <div v-if="test.details && Object.keys(test.details).length > 0" class="test-details">
          <el-divider />
          <el-descriptions :column="2" size="small" border>
            <template v-for="(value, key) in test.details" :key="key">
              <el-descriptions-item :label="formatLabel(key)">
                <span v-if="isObject(value)">
                  {{ formatValue(value) }}
                </span>
                <span v-else>{{ value }}</span>
              </el-descriptions-item>
            </template>
          </el-descriptions>
        </div>
        
        <!-- 错误信息和修复建议 -->
        <div v-if="test.status === 'failed' && test.fix_suggestion" class="fix-suggestion">
          <el-divider />
          <el-alert
            :title="test.fix_suggestion.title"
            type="warning"
            :closable="false"
          >
            <div class="fix-steps">
              <p><strong>解决方案：</strong></p>
              <ol>
                <li v-for="(step, idx) in test.fix_suggestion.steps" :key="idx">
                  {{ step }}
                </li>
              </ol>
              
              <div class="fix-actions" v-if="test.fix_suggestion.auto_fixable">
                <el-button 
                  type="primary" 
                  size="small"
                  :loading="autoFixing"
                  @click="autoFix(test.name)"
                >
                  <el-icon><Tools /></el-icon>
                  一键自动修复
                </el-button>
              </div>
            </div>
          </el-alert>
        </div>
        
        <!-- 特殊显示：Bot测试结果 -->
        <div v-if="test.name === 'Bot配置测试' && test.details && test.details.bots" class="bot-results">
          <el-divider />
          <div class="bot-list">
            <div 
              v-for="(botResult, botName) in test.details.bots" 
              :key="botName"
              class="bot-result-item"
            >
              <el-icon 
                :class="botResult.status === 'success' ? 'success' : 'failed'"
                :size="20"
              >
                <CircleCheck v-if="botResult.status === 'success'" />
                <CircleClose v-else />
              </el-icon>
              <span class="bot-name">{{ botName }}</span>
              <el-tag :type="botResult.status === 'success' ? 'success' : 'danger'" size="small">
                {{ botResult.platform }}
              </el-tag>
              <span class="bot-message">{{ botResult.message }}</span>
            </div>
          </div>
        </div>
        
        <!-- 特殊显示：真实消息发送结果 -->
        <div v-if="test.name === '真实消息发送' && test.details && test.details.results" class="send-results">
          <el-divider />
          <el-alert
            title="📨 测试消息发送记录"
            type="info"
            :closable="false"
          >
            <div class="send-list">
              <div 
                v-for="(result, botName) in test.details.results" 
                :key="botName"
                class="send-result-item"
              >
                <el-icon 
                  :class="result.success ? 'success' : 'failed'"
                  :size="18"
                >
                  <Check v-if="result.success" />
                  <Close v-else />
                </el-icon>
                <span class="bot-name">{{ botName }}</span>
                <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                  {{ result.platform }}
                </el-tag>
                <span class="send-message">{{ result.message }}</span>
              </div>
            </div>
          </el-alert>
        </div>
      </el-card>
    </div>
    
    <!-- 测试日志 -->
    <el-card class="test-log-card" v-if="testLogs.length > 0">
      <template #header>
        <div class="card-header">
          <span>📋 测试日志</span>
          <el-button size="small" @click="exportTestLog">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
        </div>
      </template>
      
      <div class="test-log">
        <div v-for="(log, index) in testLogs" :key="index" class="log-entry">
          {{ log }}
        </div>
      </div>
    </el-card>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="goBack" :disabled="testing">
        <el-icon><ArrowLeft /></el-icon>
        返回上一步
      </el-button>
      
      <el-button 
        type="primary"
        :loading="testing"
        @click="runTests"
        v-if="!testComplete"
      >
        <el-icon><VideoPlay /></el-icon>
        {{ testing ? '测试中...' : '开始测试' }}
      </el-button>
      
      <el-button 
        type="warning"
        @click="runTests"
        v-if="testComplete && !overallSuccess"
      >
        <el-icon><Refresh /></el-icon>
        重新测试
      </el-button>
      
      <el-button 
        type="success"
        size="large"
        @click="complete"
        v-if="testComplete && overallSuccess"
      >
        <el-icon><Check /></el-icon>
        完成配置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  CircleCheck,
  CircleClose,
  Loading,
  Clock,
  Tools,
  Check,
  Close,
  Download,
  ArrowLeft,
  VideoPlay,
  Refresh
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['back', 'complete'])

// 测试状态
const testing = ref(false)
const testComplete = ref(false)
const autoFixing = ref(false)

// 测试项
const tests = ref([
  {
    name: '环境检查',
    description: '检查Redis、Chromium、磁盘空间、网络连接',
    status: 'pending',
    progress: 0,
    details: {},
    duration_ms: null
  },
  {
    name: 'KOOK账号测试',
    description: '验证登录状态、服务器数量、频道数量、响应时间',
    status: 'pending',
    progress: 0,
    details: {},
    duration_ms: null
  },
  {
    name: 'Bot配置测试',
    description: '测试Discord、Telegram、飞书Bot连接',
    status: 'pending',
    progress: 0,
    details: {},
    duration_ms: null
  },
  {
    name: '频道映射验证',
    description: '检查映射配置的有效性',
    status: 'pending',
    progress: 0,
    details: {},
    duration_ms: null
  },
  {
    name: '真实消息发送',
    description: '向所有Bot发送真实测试消息',
    status: 'pending',
    progress: 0,
    details: {},
    duration_ms: null
  }
])

// 测试日志
const testLogs = ref([])

// 计算总体进度
const overallProgress = computed(() => {
  const completedTests = tests.value.filter(t => 
    t.status === 'success' || t.status === 'failed'
  ).length
  return Math.round((completedTests / tests.value.length) * 100)
})

// 计算进度状态
const progressStatus = computed(() => {
  if (testing.value) return undefined
  if (!testComplete.value) return undefined
  
  const failedCount = tests.value.filter(t => t.status === 'failed').length
  if (failedCount === 0) return 'success'
  if (failedCount === tests.value.length) return 'exception'
  return 'warning'
})

// 判断是否全部成功
const overallSuccess = computed(() => {
  return tests.value.every(t => t.status === 'success')
})

// 获取测试项样式类
const getTestClass = (test) => {
  return {
    'test-success': test.status === 'success',
    'test-failed': test.status === 'failed',
    'test-testing': test.status === 'testing',
    'test-pending': test.status === 'pending'
  }
}

// 格式化标签
const formatLabel = (key) => {
  const labelMap = {
    'redis': 'Redis',
    'chromium': 'Chromium',
    'disk': '磁盘空间',
    'network': '网络连接',
    'account_id': '账号ID',
    'email': '邮箱',
    'login_status': '登录状态',
    'server_count': '服务器数',
    'channel_count': '频道数',
    'response_time_ms': '响应时间',
    'total_count': '总数',
    'valid_count': '有效数',
    'invalid_count': '无效数',
    'total': '总计',
    'failed': '失败数'
  }
  return labelMap[key] || key
}

// 判断是否为对象
const isObject = (value) => {
  return typeof value === 'object' && value !== null
}

// 格式化值
const formatValue = (value) => {
  if (value.status) {
    return `${value.status}: ${value.message || ''}`
  }
  return JSON.stringify(value)
}

// 运行测试
const runTests = async () => {
  testing.value = true
  testComplete.value = false
  testLogs.value = []
  
  // 重置所有测试状态
  tests.value.forEach(test => {
    test.status = 'pending'
    test.progress = 0
    test.details = {}
    test.error = null
    test.fix_suggestion = null
    test.duration_ms = null
  })
  
  try {
    ElMessage.info('开始配置测试...')
    
    // 调用后端API
    const response = await api.post('/api/wizard-testing-enhanced/comprehensive-test')
    
    // 更新测试结果
    response.tests.forEach((result, index) => {
      tests.value[index].status = result.status
      tests.value[index].progress = result.progress
      tests.value[index].details = result.details
      tests.value[index].error = result.error
      tests.value[index].fix_suggestion = result.fix_suggestion
      tests.value[index].duration_ms = result.duration_ms
    })
    
    // 获取测试日志
    const logResponse = await api.get('/api/wizard-testing-enhanced/test-log')
    testLogs.value = logResponse.logs || []
    
    testComplete.value = true
    
    if (response.overall_status === 'success') {
      ElMessage.success({
        message: '🎉 所有测试通过！您的配置完美！',
        duration: 5000
      })
    } else if (response.overall_status === 'partial') {
      ElMessage.warning({
        message: `⚠️  部分测试失败（${response.failed_count}项），请查看详情`,
        duration: 5000
      })
    } else {
      ElMessage.error({
        message: '❌ 测试失败，请检查配置',
        duration: 5000
      })
    }
    
  } catch (error) {
    ElMessage.error('测试失败：' + (error.response?.data?.detail || error.message))
    testComplete.value = true
  } finally {
    testing.value = false
  }
}

// 自动修复
const autoFix = async (testName) => {
  autoFixing.value = true
  
  try {
    let issueType = ''
    
    if (testName === '环境检查') {
      // 根据错误信息判断修复类型
      const test = tests.value.find(t => t.name === testName)
      if (test.details.redis?.status === 'error') {
        issueType = 'redis'
      } else if (test.details.chromium?.status === 'error') {
        issueType = 'chromium'
      }
    }
    
    if (!issueType) {
      ElMessage.warning('无法确定修复类型')
      return
    }
    
    ElMessage.info(`正在自动修复: ${issueType}...`)
    
    const response = await api.post(`/api/wizard-testing-enhanced/auto-fix/${issueType}`)
    
    if (response.success) {
      ElMessage.success(`✅ 修复成功: ${response.message}`)
      
      // 重新运行测试
      setTimeout(() => {
        runTests()
      }, 2000)
    } else {
      ElMessage.error(`修复失败: ${response.message}`)
    }
    
  } catch (error) {
    ElMessage.error('自动修复失败：' + (error.response?.data?.detail || error.message))
  } finally {
    autoFixing.value = false
  }
}

// 导出测试日志
const exportTestLog = async () => {
  try {
    const response = await api.post('/api/wizard-testing-enhanced/export-log')
    
    // 创建Blob并下载
    const blob = new Blob([response.content], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = response.filename
    a.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('测试日志已导出')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

// 返回上一步
const goBack = () => {
  emit('back')
}

// 完成配置
const complete = () => {
  ElMessageBox.confirm(
    '恭喜！您已完成所有配置和测试。点击确定将进入主界面。',
    '🎉 配置完成',
    {
      confirmButtonText: '进入主界面',
      cancelButtonText: '再检查一下',
      type: 'success'
    }
  ).then(() => {
    emit('complete')
  }).catch(() => {
    // 用户取消
  })
}

// 自动开始测试（可选）
onMounted(() => {
  ElMessageBox.confirm(
    '我们将对您的配置进行全面测试，包括发送真实测试消息到所有Bot。\n\n测试预计需要30秒-1分钟。',
    '开始测试',
    {
      confirmButtonText: '立即开始',
      cancelButtonText: '稍后手动开始',
      type: 'info'
    }
  ).then(() => {
    runTests()
  }).catch(() => {
    // 用户选择稍后开始
  })
})
</script>

<style scoped>
.wizard-testing-ultimate {
  padding: 20px;
}

.testing-header {
  text-align: center;
  margin-bottom: 30px;
}

.testing-header h2 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #303133;
}

.testing-header p {
  font-size: 16px;
  color: #909399;
}

.progress-card {
  margin-bottom: 20px;
}

.progress-info {
  text-align: center;
  margin-top: 15px;
  font-size: 16px;
  font-weight: 500;
}

.progress-info .warning {
  color: #E6A23C;
}

.test-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.test-item {
  transition: all 0.3s;
}

.test-item.test-success {
  border-left: 4px solid #67C23A;
}

.test-item.test-failed {
  border-left: 4px solid #F56C6C;
}

.test-item.test-testing {
  border-left: 4px solid #409EFF;
  background: #ecf5ff;
}

.test-item.test-pending {
  border-left: 4px solid #E4E7ED;
}

.test-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-icon-wrapper {
  flex-shrink: 0;
}

.test-icon {
  display: block;
}

.test-icon.success {
  color: #67C23A;
}

.test-icon.failed {
  color: #F56C6C;
}

.test-icon.testing {
  color: #409EFF;
}

.test-icon.pending {
  color: #C0C4CC;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.test-info {
  flex: 1;
}

.test-info h3 {
  font-size: 18px;
  margin: 0 0 5px 0;
  color: #303133;
}

.test-description {
  font-size: 14px;
  color: #909399;
}

.test-duration {
  flex-shrink: 0;
}

.test-details {
  margin-top: 15px;
}

.fix-suggestion {
  margin-top: 15px;
}

.fix-steps {
  margin-top: 10px;
}

.fix-steps ol {
  margin: 10px 0;
  padding-left: 20px;
}

.fix-steps li {
  margin: 5px 0;
}

.fix-actions {
  margin-top: 15px;
}

.bot-results, .send-results {
  margin-top: 15px;
}

.bot-list, .send-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bot-result-item, .send-result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.bot-result-item .success, .send-result-item .success {
  color: #67C23A;
}

.bot-result-item .failed, .send-result-item .failed {
  color: #F56C6C;
}

.bot-name {
  font-weight: 500;
  min-width: 120px;
}

.bot-message, .send-message {
  color: #606266;
  flex: 1;
}

.test-log-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-log {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.log-entry {
  margin: 3px 0;
  color: #606266;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #DCDFE6;
}
</style>
