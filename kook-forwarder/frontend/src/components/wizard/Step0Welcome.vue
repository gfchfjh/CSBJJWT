<template>
  <div class="welcome-step">
    <div class="welcome-header">
      <el-icon :size="80" color="#409EFF"><CircleCheck /></el-icon>
      <h1>🎉 欢迎使用KOOK消息转发系统</h1>
      <p class="subtitle">本向导将帮助您完成基础配置，预计耗时：3-5分钟</p>
    </div>
    
    <!-- 免责声明滚动区域 -->
    <el-card class="disclaimer-card" shadow="never">
      <template #header>
        <span class="card-header-title">
          <el-icon><WarningFilled /></el-icon>
          重要声明
        </span>
      </template>
      
      <div
        class="disclaimer-content"
        ref="disclaimerRef"
        @scroll="handleScroll"
      >
        <h2>⚠️ 使用前必读</h2>
        <p class="important-text">
          <strong>本软件仅供学习和研究使用，使用本软件可能违反KOOK服务条款。</strong>
        </p>
        
        <h3>📋 使用风险</h3>
        <ul class="risk-list">
          <li>
            <el-icon color="#F56C6C"><Close /></el-icon>
            本软件通过浏览器自动化抓取KOOK消息，可能违反KOOK服务条款
          </li>
          <li>
            <el-icon color="#F56C6C"><Close /></el-icon>
            使用本软件可能导致账号被封禁，请自行承担风险
          </li>
          <li>
            <el-icon color="#F56C6C"><Close /></el-icon>
            请勿用于商业用途或非法目的
          </li>
          <li>
            <el-icon color="#F56C6C"><Close /></el-icon>
            请勿滥用或恶意使用本软件
          </li>
        </ul>
        
        <h3>⚖️ 法律责任</h3>
        <ul class="legal-list">
          <li>
            <el-icon color="#67C23A"><Check /></el-icon>
            仅在已获授权的场景下使用
          </li>
          <li>
            <el-icon color="#67C23A"><Check /></el-icon>
            转发的消息内容可能涉及版权，请遵守相关法律法规
          </li>
          <li>
            <el-icon color="#67C23A"><Check /></el-icon>
            本软件开发者不承担任何法律责任
          </li>
          <li>
            <el-icon color="#67C23A"><Check /></el-icon>
            您有责任确保使用本软件的合法性
          </li>
        </ul>
        
        <h3>🔐 数据安全</h3>
        <ul class="security-list">
          <li>
            <el-icon color="#409EFF"><Lock /></el-icon>
            所有数据本地存储，不上传云端
          </li>
          <li>
            <el-icon color="#409EFF"><Lock /></el-icon>
            Cookie和密码均使用AES-256加密
          </li>
          <li>
            <el-icon color="#409EFF"><Lock /></el-icon>
            您需要保管好设备，防止数据泄露
          </li>
          <li>
            <el-icon color="#409EFF"><Lock /></el-icon>
            定期备份配置，避免数据丢失
          </li>
        </ul>
        
        <h3>💡 最佳实践</h3>
        <ul class="tips-list">
          <li>建议使用小号进行测试，避免主号被封</li>
          <li>不要频繁登录/退出，避免触发风控</li>
          <li>合理设置转发频率，避免被平台限流</li>
          <li>定期查看日志，及时发现异常</li>
        </ul>
        
        <div class="final-warning">
          <el-alert
            type="error"
            :closable="false"
            show-icon
          >
            <template #title>
              <strong>最终声明：使用本软件即表示您已充分了解并接受以上所有风险和责任。</strong>
            </template>
          </el-alert>
        </div>
      </div>
    </el-card>
    
    <!-- 阅读进度条 -->
    <div class="progress-section">
      <el-progress
        :percentage="readProgress"
        :color="progressColor"
        :stroke-width="15"
        :format="formatProgress"
      />
      <p class="progress-hint" v-if="readProgress < 100">
        <el-icon><InfoFilled /></el-icon>
        请滚动到底部阅读完整声明
      </p>
    </div>
    
    <!-- 双重确认 -->
    <div class="confirmation-section">
      <el-checkbox
        v-model="agreed"
        :disabled="readProgress < 100"
        size="large"
        class="agreement-checkbox"
      >
        <strong>我已仔细阅读并同意以上所有条款</strong>
      </el-checkbox>
      
      <el-alert
        v-if="!agreed && readProgress >= 100"
        type="warning"
        :closable="false"
        show-icon
        class="agreement-hint"
      >
        请勾选同意条款后继续
      </el-alert>
    </div>
    
    <!-- 操作按钮 -->
    <div class="button-group">
      <el-button size="large" @click="handleReject">
        <el-icon><CloseBold /></el-icon>
        拒绝并退出
      </el-button>
      <el-button
        type="primary"
        size="large"
        :disabled="!agreed"
        @click="handleAccept"
      >
        <el-icon><Check /></el-icon>
        同意并继续
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  CircleCheck,
  WarningFilled,
  Close,
  Check,
  Lock,
  InfoFilled,
  CloseBold
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const disclaimerRef = ref(null)
const readProgress = ref(0)
const agreed = ref(false)

const emit = defineEmits(['next', 'cancel'])

// 计算属性
const progressColor = computed(() => {
  if (readProgress.value === 100) return '#67C23A'
  if (readProgress.value >= 50) return '#E6A23C'
  return '#F56C6C'
})

const formatProgress = (percentage) => {
  if (percentage === 100) {
    return '✅ 已读完'
  }
  return `已阅读 ${percentage}%`
}

// 方法
const handleScroll = (e) => {
  const el = e.target
  const scrollTop = el.scrollTop
  const scrollHeight = el.scrollHeight
  const clientHeight = el.clientHeight
  
  if (scrollHeight <= clientHeight) {
    // 内容较短，直接标记为已读
    readProgress.value = 100
    return
  }
  
  const progress = Math.round((scrollTop / (scrollHeight - clientHeight)) * 100)
  readProgress.value = Math.min(progress, 100)
}

const handleReject = async () => {
  try {
    await ElMessageBox.confirm(
      '您确定要退出吗？退出后将无法使用本软件。',
      '确认退出',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '继续使用',
        type: 'warning'
      }
    )
    
    // 用户确认退出
    if (window.electron) {
      window.electron.quit()
    } else {
      router.push('/')
    }
  } catch {
    // 用户取消，继续留在当前页面
  }
}

const handleAccept = () => {
  // 记录用户已同意
  localStorage.setItem('terms_accepted', 'true')
  localStorage.setItem('terms_accepted_time', Date.now().toString())
  
  emit('next')
}

onMounted(() => {
  // 检查内容高度
  const el = disclaimerRef.value
  if (el) {
    // 稍微延迟以确保DOM渲染完成
    setTimeout(() => {
      if (el.scrollHeight <= el.clientHeight) {
        readProgress.value = 100
      }
    }, 100)
  }
})
</script>

<style scoped>
.welcome-step {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-header {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-header h1 {
  font-size: 32px;
  margin: 20px 0 10px;
  color: #303133;
}

.subtitle {
  font-size: 16px;
  color: #909399;
}

.disclaimer-card {
  margin-bottom: 20px;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.disclaimer-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
  line-height: 1.8;
  font-size: 15px;
}

.disclaimer-content h2 {
  color: #F56C6C;
  font-size: 24px;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.disclaimer-content h3 {
  color: #409EFF;
  font-size: 18px;
  margin: 25px 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.important-text {
  background: #fef0f0;
  padding: 15px;
  border-left: 4px solid #F56C6C;
  border-radius: 4px;
  margin: 15px 0;
}

.disclaimer-content ul {
  list-style: none;
  padding: 0;
}

.disclaimer-content li {
  margin: 12px 0;
  padding-left: 10px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.disclaimer-content li .el-icon {
  margin-top: 3px;
  flex-shrink: 0;
}

.risk-list li {
  color: #F56C6C;
}

.legal-list li {
  color: #67C23A;
}

.security-list li {
  color: #409EFF;
}

.tips-list {
  background: #f0f9ff;
  padding: 15px 20px;
  border-radius: 8px;
  border: 1px solid #d0e8ff;
}

.tips-list li {
  color: #606266;
  list-style: disc;
  margin-left: 20px;
}

.final-warning {
  margin-top: 30px;
}

.progress-section {
  margin: 25px 0;
}

.progress-hint {
  text-align: center;
  color: #909399;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.confirmation-section {
  margin: 25px 0;
}

.agreement-checkbox {
  display: flex;
  justify-content: center;
  font-size: 16px;
}

.agreement-checkbox :deep(.el-checkbox__label) {
  font-size: 16px;
}

.agreement-hint {
  margin-top: 15px;
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-top: 30px;
}

.button-group .el-button {
  flex: 1;
  height: 50px;
  font-size: 16px;
}

/* 滚动条样式 */
.disclaimer-content::-webkit-scrollbar {
  width: 8px;
}

.disclaimer-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.disclaimer-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.disclaimer-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 暗黑模式 */
.dark .welcome-header h1 {
  color: #e5eaf3;
}

.dark .important-text {
  background: #4a2828;
  border-left-color: #F56C6C;
}

.dark .tips-list {
  background: #1a3a52;
  border-color: #2c5f8d;
}

.dark .disclaimer-content::-webkit-scrollbar-track {
  background: #2c2c2c;
}

.dark .disclaimer-content::-webkit-scrollbar-thumb {
  background: #555;
}

.dark .disclaimer-content::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style>
