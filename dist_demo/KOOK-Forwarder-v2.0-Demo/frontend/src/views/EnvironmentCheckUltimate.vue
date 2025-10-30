<template>
  <div class="environment-check-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>🔍 环境检测</h2>
          <el-tag v-if="allPassed" type="success" size="large">
            ✅ 检测通过
          </el-tag>
          <el-tag v-else-if="checking" type="info" size="large">
            ⏳ 检测中...
          </el-tag>
          <el-tag v-else type="warning" size="large">
            ⚠️ 发现问题
          </el-tag>
        </div>
      </template>
      
      <!-- 检测进度 -->
      <div class="progress-section">
        <el-progress 
          :percentage="progress" 
          :status="allPassed ? 'success' : checking ? '' : 'exception'"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="percentage-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        
        <div v-if="duration > 0" class="duration-text">
          检测耗时: <strong>{{ duration }}</strong> 秒
        </div>
      </div>
      
      <!-- 检测结果 -->
      <div v-if="!checking && results" class="results-section">
        <h3>📋 检测结果</h3>
        
        <el-row :gutter="20">
          <!-- Python版本 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.python?.version_ok)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Python v-if="results.python?.version_ok" style="color: #67C23A;" />
                  <Close v-else style="color: #F56C6C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">Python版本</div>
                <div class="check-status">{{ results.python?.status }}</div>
                <div class="check-detail">
                  当前: {{ results.python?.version }} | 要求: {{ results.python?.required }}
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- Chromium浏览器 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.chromium?.installed)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Monitor v-if="results.chromium?.installed" style="color: #67C23A;" />
                  <Close v-else style="color: #F56C6C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">Chromium浏览器</div>
                <div class="check-status">{{ results.chromium?.status }}</div>
                <div v-if="results.chromium?.path" class="check-detail">
                  路径: {{ results.chromium.path }}
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- Redis服务 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.redis?.running)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Connection v-if="results.redis?.running" style="color: #67C23A;" />
                  <Close v-else style="color: #F56C6C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">Redis服务</div>
                <div class="check-status">{{ results.redis?.status }}</div>
                <div class="check-detail">
                  地址: {{ results.redis?.host }}:{{ results.redis?.port }}
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- 网络连接 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.network?.all_reachable)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Link v-if="results.network?.all_reachable" style="color: #67C23A;" />
                  <Close v-else style="color: #E6A23C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">网络连接</div>
                <div class="check-status">{{ results.network?.status }}</div>
                <div v-if="results.network?.results" class="check-detail">
                  <div v-for="(reachable, url) in results.network.results" :key="url">
                    {{ reachable ? '✅' : '❌' }} {{ getUrlDomain(url) }}
                  </div>
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- 端口可用性 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.ports?.all_available)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Connection v-if="results.ports?.all_available" style="color: #67C23A;" />
                  <Close v-else style="color: #E6A23C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">端口可用性</div>
                <div class="check-status">{{ results.ports?.status }}</div>
                <div v-if="results.ports?.results" class="check-detail">
                  <div v-for="(info, port) in results.ports.results" :key="port">
                    {{ info.available ? '✅' : '❌' }} {{ info.name }} ({{ port }})
                  </div>
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- 磁盘空间 -->
          <el-col :span="12">
            <div class="check-item" :class="getItemClass(results.disk_space?.sufficient)">
              <div class="check-icon">
                <el-icon :size="32">
                  <Files v-if="results.disk_space?.sufficient" style="color: #67C23A;" />
                  <Close v-else style="color: #F56C6C;" />
                </el-icon>
              </div>
              <div class="check-content">
                <div class="check-title">磁盘空间</div>
                <div class="check-status">{{ results.disk_space?.status }}</div>
                <div class="check-detail">
                  剩余: {{ results.disk_space?.free_gb }}GB / 总计: {{ results.disk_space?.total_gb }}GB
                  <br>
                  已用: {{ results.disk_space?.used_percent }}%
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 可修复的问题 -->
      <div v-if="fixableIssues.length > 0" class="fixable-issues-section">
        <el-alert 
          title="🔧 检测到可自动修复的问题" 
          type="warning" 
          :closable="false"
        >
          <ul>
            <li v-for="issue in fixableIssues" :key="issue.issue">
              <strong>{{ issue.issue }}</strong>
              <span v-if="issue.severity === 'critical'" class="severity-badge critical">严重</span>
              <span v-else class="severity-badge warning">警告</span>
              <div class="fix-command">修复方式: {{ issue.fix_command }}</div>
            </li>
          </ul>
        </el-alert>
        
        <el-button 
          type="primary" 
          size="large" 
          @click="autoFix"
          :loading="fixing"
          style="width: 100%; margin-top: 15px;"
        >
          <el-icon><Tools /></el-icon>
          一键自动修复
        </el-button>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button 
          v-if="!checking"
          size="large"
          @click="recheckEnvironment"
        >
          <el-icon><Refresh /></el-icon>
          重新检测
        </el-button>
        
        <el-button 
          v-if="allPassed" 
          type="success" 
          size="large"
          @click="continueToWizard"
        >
          <el-icon><Right /></el-icon>
          环境正常，继续配置
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor,
  Connection,
  Link,
  Files,
  Close,
  Tools,
  Refresh,
  Right
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const checking = ref(false)
const fixing = ref(false)
const progress = ref(0)
const duration = ref(0)
const results = ref(null)
const fixableIssues = ref([])

const allPassed = computed(() => {
  if (!results.value) return false
  return results.value.all_passed === true
})

const getItemClass = (passed) => {
  return passed ? 'check-item-success' : 'check-item-error'
}

const getUrlDomain = (url) => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return url
  }
}

const checkEnvironment = async () => {
  try {
    checking.value = true
    progress.value = 0
    
    // 模拟进度增长
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 500)
    
    const response = await api.get('/api/environment/check-all')
    
    clearInterval(progressInterval)
    progress.value = 100
    
    results.value = response.data.results
    duration.value = response.data.duration
    fixableIssues.value = response.data.fixable_issues || []
    
    if (response.data.all_passed) {
      ElMessage.success(`✅ 环境检测通过！（耗时${duration.value}秒）`)
    } else {
      ElMessage.warning(`⚠️ 检测到 ${fixableIssues.value.length} 个问题`)
    }
  } catch (error) {
    ElMessage.error('环境检测失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    checking.value = false
  }
}

const autoFix = async () => {
  try {
    fixing.value = true
    
    const response = await api.post('/api/environment/auto-fix')
    
    if (response.data.success) {
      ElMessage.success(`✅ 已修复 ${response.data.fixed.length} 个问题`)
      
      // 重新检测
      setTimeout(() => {
        checkEnvironment()
      }, 2000)
    } else {
      const failedCount = response.data.failed.length
      ElMessageBox.alert(
        `部分问题无法自动修复（${failedCount}个），请手动处理`,
        '修复结果',
        { type: 'warning' }
      )
    }
  } catch (error) {
    ElMessage.error('自动修复失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    fixing.value = false
  }
}

const recheckEnvironment = async () => {
  await checkEnvironment()
}

const continueToWizard = () => {
  router.push('/wizard/quick-3-steps')
}

// 组件挂载时自动检测
checkEnvironment()
</script>

<style scoped>
.environment-check-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
}

.progress-section {
  margin: 30px 0;
}

.percentage-text {
  font-size: 16px;
  font-weight: bold;
}

.duration-text {
  text-align: center;
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

.results-section {
  margin-top: 30px;
}

.results-section h3 {
  margin-bottom: 20px;
  font-size: 18px;
}

.check-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.check-item-success {
  background: #F0F9FF;
  border-color: #409EFF;
}

.check-item-error {
  background: #FEF0F0;
  border-color: #F56C6C;
}

.check-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.check-icon {
  flex-shrink: 0;
}

.check-content {
  flex: 1;
}

.check-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.check-status {
  font-size: 14px;
  margin-bottom: 5px;
}

.check-detail {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.fixable-issues-section {
  margin-top: 30px;
}

.fixable-issues-section ul {
  margin: 15px 0;
  padding-left: 20px;
}

.fixable-issues-section li {
  margin: 10px 0;
  line-height: 1.8;
}

.severity-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-left: 8px;
}

.severity-badge.critical {
  background: #F56C6C;
  color: white;
}

.severity-badge.warning {
  background: #E6A23C;
  color: white;
}

.fix-command {
  font-size: 12px;
  color: #606266;
  margin-top: 5px;
  padding: 5px 10px;
  background: #F5F7FA;
  border-radius: 4px;
  font-family: monospace;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
}
</style>
