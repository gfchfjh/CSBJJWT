<template>
  <!-- ✅ P1-1优化: Telegram Chat ID自动检测组件 -->
  <el-dialog
    v-model="visible"
    title="🔍 自动检测Chat ID"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="detectStep !== 1"
  >
    <div class="detect-content">
      <!-- 步骤指示器 -->
      <el-steps :active="detectStep" align-center style="margin-bottom: 30px;">
        <el-step title="发送消息" icon="ChatDotSquare" />
        <el-step title="检测中" icon="Loading" />
        <el-step title="选择群组" icon="Select" />
      </el-steps>

      <!-- 步骤1: 发送消息提示 -->
      <div v-show="detectStep === 0" class="detect-step">
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <h3>请按以下步骤操作：</h3>
          </template>
          <ol style="margin: 10px 0; padding-left: 20px; line-height: 2;">
            <li>打开Telegram应用（手机或电脑版）</li>
            <li>进入需要配置的群组</li>
            <li><strong style="color: #E6A23C;">在群组中发送任意消息</strong>（如："测试"）</li>
            <li>等待系统自动检测（最多30秒）</li>
          </ol>
        </el-alert>

        <el-alert 
          type="warning" 
          :closable="false"
          style="margin-top: 15px;"
        >
          <template #title>
            ⚠️ 注意事项
          </template>
          <ul style="margin: 10px 0; padding-left: 20px;">
            <li>确保Bot已添加到群组</li>
            <li>确保Bot有读取消息的权限</li>
            <li>建议使用测试群组进行首次配置</li>
          </ul>
        </el-alert>

        <div class="detect-actions" style="margin-top: 20px; text-align: center;">
          <el-space :size="15">
            <el-button size="large" @click="handleCancel">
              取消
            </el-button>
            <el-button 
              type="primary" 
              size="large" 
              @click="startDetecting"
            >
              <el-icon><CircleCheck /></el-icon>
              我已发送，开始检测
            </el-button>
          </el-space>
        </div>
      </div>

      <!-- 步骤2: 检测中 -->
      <div v-show="detectStep === 1" class="detect-step">
        <el-result icon="loading">
          <template #title>
            <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
              <el-icon class="is-loading" :size="48" color="#409EFF">
                <Loading />
              </el-icon>
              <span>正在检测群组消息...</span>
            </div>
          </template>
          <template #sub-title>
            <div style="color: #909399;">
              <p>检测进度: {{ detectProgress }}/30 秒</p>
              <p>已检测到 <strong style="color: #409EFF;">{{ detectedGroups.length }}</strong> 个群组</p>
            </div>
          </template>
        </el-result>

        <el-progress 
          :percentage="(detectProgress / 30) * 100"
          :show-text="false"
          style="margin-bottom: 20px;"
        />

        <div class="detect-tips" style="text-align: center; color: #909399;">
          <el-alert type="info" :closable="false">
            <template #title>
              💡 检测提示
            </template>
            <p style="margin: 5px 0;">如果长时间未检测到，请确认：</p>
            <ul style="text-align: left; display: inline-block; margin: 10px 0;">
              <li>Bot是否已添加到群组</li>
              <li>Bot是否有读取消息的权限</li>
              <li>是否在正确的群组发送了消息</li>
            </ul>
            <el-button 
              size="small" 
              @click="handleCancel"
              style="margin-top: 10px;"
            >
              取消检测
            </el-button>
          </el-alert>
        </div>
      </div>

      <!-- 步骤3: 选择群组 -->
      <div v-show="detectStep === 2" class="detect-step">
        <el-alert
          :type="detectedGroups.length > 0 ? 'success' : 'warning'"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        >
          <template #title>
            {{ detectedGroups.length > 0 
               ? `✅ 检测成功！发现 ${detectedGroups.length} 个群组` 
               : '⚠️ 未检测到群组' }}
          </template>
          {{ detectedGroups.length > 0 
             ? '请选择要配置的群组：' 
             : '请检查Bot配置或重新尝试' }}
        </el-alert>

        <!-- 群组列表 -->
        <el-radio-group 
          v-if="detectedGroups.length > 0"
          v-model="selectedChatId" 
          style="width: 100%;"
        >
          <el-radio
            v-for="group in detectedGroups"
            :key="group.chat_id"
            :label="group.chat_id"
            style="width: 100%; margin: 10px 0;"
            border
          >
            <div class="group-option">
              <div class="group-info">
                <div class="group-name">
                  <el-icon :size="20"><ChatDotSquare /></el-icon>
                  <strong>{{ group.title || '未命名群组' }}</strong>
                </div>
                <div class="group-details">
                  <el-tag size="small" type="info">
                    Chat ID: {{ group.chat_id }}
                  </el-tag>
                  <el-tag v-if="group.member_count" size="small" type="success">
                    {{ group.member_count }} 成员
                  </el-tag>
                  <span style="color: #909399; font-size: 12px;">
                    最后活跃: {{ formatTime(group.last_message_time) }}
                  </span>
                </div>
              </div>
              <div v-if="group.last_message_text" class="group-preview">
                <el-text size="small" type="info">
                  最新消息: {{ truncateText(group.last_message_text, 50) }}
                </el-text>
              </div>
            </div>
          </el-radio>
        </el-radio-group>

        <div class="detect-actions" style="margin-top: 20px; text-align: center;">
          <el-space :size="15">
            <el-button @click="detectStep = 0">
              <el-icon><RefreshLeft /></el-icon>
              重新检测
            </el-button>
            <el-button 
              type="primary" 
              :disabled="!selectedChatId"
              @click="confirmChatId"
            >
              <el-icon><Select /></el-icon>
              确认选择
            </el-button>
          </el-space>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Loading, CircleCheck, ChatDotSquare, 
  RefreshLeft, Select 
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  botToken: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'selected'])

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const detectStep = ref(0)
const detecting = ref(false)
const detectProgress = ref(0)
const detectedGroups = ref([])
const selectedChatId = ref('')

let pollInterval = null

// 开始检测
const startDetecting = async () => {
  if (!props.botToken) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  detectStep.value = 1
  detectProgress.value = 0
  detectedGroups.value = []
  detecting.value = true

  // 轮询检测（每秒检查一次，最多30秒）
  const maxAttempts = 30
  let attempts = 0

  pollInterval = setInterval(async () => {
    attempts++
    detectProgress.value = attempts

    try {
      const response = await api.post('/api/telegram-helper/auto-detect-chat', {
        token: props.botToken
      })

      if (response.groups && response.groups.length > 0) {
        // 检测到群组
        detectedGroups.value = response.groups
        detectStep.value = 2
        detecting.value = false
        clearInterval(pollInterval)
        
        ElMessage.success(`检测到 ${response.groups.length} 个群组`)
      }
    } catch (error) {
      console.error('检测失败:', error)
    }

    // 超时
    if (attempts >= maxAttempts) {
      clearInterval(pollInterval)
      detecting.value = false
      
      if (detectedGroups.value.length === 0) {
        ElMessage.warning({
          message: '检测超时，未找到群组。请确认：\n' +
                   '1. Bot已添加到群组\n' +
                   '2. 在群组中发送了消息\n' +
                   '3. Bot有读取消息的权限',
          duration: 8000,
          showClose: true
        })
        detectStep.value = 2  // 仍然进入选择步骤，显示空列表
      }
    }
  }, 1000)
}

// 确认选择
const confirmChatId = () => {
  if (!selectedChatId.value) {
    ElMessage.warning('请选择一个群组')
    return
  }

  const selectedGroup = detectedGroups.value.find(g => g.chat_id === selectedChatId.value)
  
  emit('selected', {
    chat_id: selectedChatId.value,
    title: selectedGroup?.title || '',
    member_count: selectedGroup?.member_count || 0
  })

  ElMessage.success('Chat ID已自动填充')
  visible.value = false
  
  // 重置状态
  resetState()
}

// 取消
const handleCancel = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
  visible.value = false
  resetState()
}

// 重置状态
const resetState = () => {
  detectStep.value = 0
  detectProgress.value = 0
  detectedGroups.value = []
  selectedChatId.value = ''
  detecting.value = false
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 监听对话框关闭
watch(() => visible.value, (newVal) => {
  if (!newVal && pollInterval) {
    clearInterval(pollInterval)
    resetState()
  }
})
</script>

<style scoped>
.detect-step {
  min-height: 300px;
}

.group-option {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  width: 100%;
}

.group-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.group-details {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.group-preview {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}

.detect-tips {
  margin-top: 20px;
}
</style>
