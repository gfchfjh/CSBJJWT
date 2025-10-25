<template>
  <div class="wizard-step-environment">
    <h2>🔍 环境检查</h2>
    <p class="description">
      正在检查您的系统环境，确保所有必需组件已正确安装...
    </p>

    <!-- 检查进度 -->
    <el-progress
      v-if="checking"
      :percentage="progress"
      :status="progress === 100 ? 'success' : undefined"
    />

    <!-- 检查结果 -->
    <div v-if="!checking && checkResults" class="check-results">
      <!-- 摘要 -->
      <el-alert
        :type="checkResults.summary.failed === 0 ? 'success' : 'warning'"
        :title="getResultTitle()"
        :closable="false"
        show-icon
      >
        <p>
          ✅ 通过: {{ checkResults.summary.passed }} 项<br>
          ❌ 失败: {{ checkResults.summary.failed }} 项<br>
          🔧 可修复: {{ checkResults.summary.fixable }} 项
        </p>
      </el-alert>

      <!-- 详细结果 -->
      <el-collapse v-model="activeNames" class="results-list">
        <!-- 通过的检查 -->
        <el-collapse-item title="✅ 通过的检查" name="passed">
          <el-timeline>
            <el-timeline-item
              v-for="item in checkResults.passed"
              :key="item.name"
              type="success"
              :timestamp="item.name"
            >
              {{ item.message }}
            </el-timeline-item>
          </el-timeline>
        </el-collapse-item>

        <!-- 失败的检查 -->
        <el-collapse-item
          v-if="checkResults.failed.length > 0"
          title="❌ 失败的检查"
          name="failed"
        >
          <el-timeline>
            <el-timeline-item
              v-for="item in checkResults.failed"
              :key="item.name"
              type="danger"
              :timestamp="item.name"
            >
              <p>{{ item.message }}</p>
              <el-button
                v-if="item.fixable"
                type="primary"
                size="small"
                :loading="fixing[item.name]"
                @click="handleFix(item.name)"
              >
                🔧 自动修复
              </el-button>
            </el-timeline-item>
          </el-timeline>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="$emit('prev')">
        上一步
      </el-button>
      
      <el-button
        v-if="!checking"
        type="info"
        @click="handleRecheck"
      >
        🔄 重新检查
      </el-button>

      <el-button
        v-if="!checking && canProceed"
        type="primary"
        @click="$emit('next')"
      >
        下一步
      </el-button>

      <el-button
        v-if="!checking && !canProceed && hasFixableIssues"
        type="warning"
        @click="handleFixAll"
      >
        🔧 一键修复全部
      </el-button>
    </div>

    <!-- 帮助提示 -->
    <el-alert
      v-if="!canProceed && !hasFixableIssues"
      type="error"
      title="无法继续"
      :closable="false"
    >
      <p>检测到严重问题，无法自动修复。请手动解决后重新检查。</p>
      <el-button type="text" @click="openHelp">
        📖 查看解决方案
      </el-button>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

// 状态
const checking = ref(false)
const progress = ref(0)
const checkResults = ref(null)
const activeNames = ref(['failed'])
const fixing = ref({})

// 计算属性
const canProceed = computed(() => {
  if (!checkResults.value) return false
  return checkResults.value.summary.failed === 0
})

const hasFixableIssues = computed(() => {
  if (!checkResults.value) return false
  return checkResults.value.summary.fixable > 0
})

// 方法
const getResultTitle = () => {
  if (!checkResults.value) return ''
  
  const { passed, failed } = checkResults.value.summary
  
  if (failed === 0) {
    return '✅ 环境检查通过'
  } else {
    return `⚠️ 发现 ${failed} 个问题`
  }
}

const runCheck = async () => {
  try {
    checking.value = true
    progress.value = 0
    checkResults.value = null

    // 模拟进度
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 200)

    const response = await api.get('/environment/check')
    
    clearInterval(progressInterval)
    progress.value = 100
    
    checkResults.value = response
    
    setTimeout(() => {
      checking.value = false
    }, 500)

  } catch (error) {
    checking.value = false
    ElMessage.error('环境检查失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleFix = async (issueName) => {
  try {
    fixing.value[issueName] = true
    
    const response = await api.post(`/environment/fix/${encodeURIComponent(issueName)}`)
    
    if (response.success) {
      ElMessage.success(`✅ ${issueName} 修复成功`)
      // 重新检查
      await runCheck()
    } else {
      ElMessage.error(`❌ ${issueName} 修复失败: ${response.message}`)
    }
    
  } catch (error) {
    ElMessage.error('修复失败：' + (error.response?.data?.detail || error.message))
  } finally {
    fixing.value[issueName] = false
  }
}

const handleFixAll = async () => {
  try {
    const fixableIssues = checkResults.value.failed.filter(item => item.fixable)
    
    if (fixableIssues.length === 0) {
      return
    }

    const confirmed = await ElMessageBox.confirm(
      `将尝试自动修复 ${fixableIssues.length} 个问题，是否继续？`,
      '一键修复',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (!confirmed) return

    for (const issue of fixableIssues) {
      await handleFix(issue.name)
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量修复失败：' + error.message)
    }
  }
}

const handleRecheck = () => {
  runCheck()
}

const openHelp = () => {
  // 打开帮助页面
  window.open('/help#environment', '_blank')
}

// 生命周期
onMounted(() => {
  runCheck()
})
</script>

<style scoped>
.wizard-step-environment {
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 10px;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.check-results {
  margin: 30px 0;
}

.results-list {
  margin-top: 20px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;
}

.el-timeline {
  padding-left: 20px;
}
</style>
