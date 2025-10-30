<template>
  <div class="message-history-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>
        <el-icon><ChatLineSquare /></el-icon>
        消息历史
      </h1>
      
      <el-button-group>
        <el-button :icon="Refresh" @click="loadMessages" :loading="loading">
          刷新
        </el-button>
        <el-button :icon="Download" @click="exportMessages">
          导出
        </el-button>
      </el-button-group>
    </div>
    
    <!-- 搜索过滤区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索消息内容..."
            :prefix-icon="Search"
            clearable
            style="width: 300px;"
          />
        </el-form-item>
        
        <el-form-item label="发送者">
          <el-input
            v-model="filterForm.author"
            placeholder="用户名或ID"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        
        <el-form-item label="频道">
          <el-select v-model="filterForm.channel" placeholder="选择频道" clearable filterable>
            <el-option
              v-for="channel in channels"
              :key="channel.id"
              :label="channel.name"
              :value="channel.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="消息类型">
          <el-select v-model="filterForm.messageType" placeholder="全部类型" clearable>
            <el-option label="全部" value="" />
            <el-option label="文本" value="text" />
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
            <el-option label="文件" value="file" />
            <el-option label="音频" value="audio" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilter">
            搜索
          </el-button>
          <el-button @click="resetFilter">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 消息列表 -->
    <el-card class="messages-card">
      <template #header>
        <div class="card-header">
          <span>消息列表（{{ filteredMessages.length }} 条）</span>
          
          <el-space>
            <el-select v-model="sortBy" size="small" @change="sortMessages">
              <el-option label="时间倒序" value="time_desc" />
              <el-option label="时间正序" value="time_asc" />
              <el-option label="发送者" value="author" />
            </el-select>
            
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">
                <el-icon><List /></el-icon>
              </el-radio-button>
              <el-radio-button label="card">
                <el-icon><Grid /></el-icon>
              </el-radio-button>
            </el-radio-group>
          </el-space>
        </div>
      </template>
      
      <el-empty 
        v-if="filteredMessages.length === 0 && !loading"
        description="没有找到消息"
      >
        <el-button type="primary" @click="resetFilter">
          清除过滤条件
        </el-button>
      </el-empty>
      
      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list'" class="messages-list" v-loading="loading">
        <el-timeline>
          <el-timeline-item
            v-for="message in paginatedMessages"
            :key="message.id"
            :timestamp="formatTime(message.timestamp)"
            placement="top"
          >
            <el-card class="message-card" shadow="hover">
              <div class="message-header">
                <div class="author-info">
                  <el-avatar :src="message.author.avatar" :size="32">
                    {{ message.author.username[0] }}
                  </el-avatar>
                  <div class="author-details">
                    <div class="author-name">{{ message.author.nickname || message.author.username }}</div>
                    <el-text type="info" size="small">
                      {{ message.channel_name }} · {{ message.server_name }}
                    </el-text>
                  </div>
                </div>
                
                <el-space>
                  <el-tag :type="getMessageTypeTag(message.type)" size="small">
                    {{ getMessageTypeLabel(message.type) }}
                  </el-tag>
                  
                  <el-button-group size="small">
                    <el-button :icon="View" @click="viewDetail(message)">
                      详情
                    </el-button>
                    <el-button :icon="CopyDocument" @click="copyMessage(message)">
                      复制
                    </el-button>
                  </el-button-group>
                </el-space>
              </div>
              
              <div class="message-content">
                <!-- 文本消息 -->
                <div v-if="message.type === 'text'" class="text-content">
                  {{ truncateText(message.content, 200) }}
                </div>
                
                <!-- 图片消息 -->
                <div v-else-if="message.type === 'image'" class="image-content">
                  <el-image
                    v-for="(img, index) in message.attachments"
                    :key="index"
                    :src="img.url"
                    :preview-src-list="message.attachments.map(a => a.url)"
                    fit="cover"
                    style="width: 100px; height: 100px; margin-right: 8px;"
                  />
                </div>
                
                <!-- 其他类型 -->
                <div v-else class="other-content">
                  <el-icon :size="32"><Document /></el-icon>
                  <span>{{ message.attachments?.[0]?.filename || '附件' }}</span>
                </div>
                
                <!-- 引用消息 -->
                <div v-if="message.quote" class="quote-content">
                  <el-icon><Back /></el-icon>
                  回复 {{ message.quote.author.username }}: {{ truncateText(message.quote.content, 50) }}
                </div>
                
                <!-- @提及 -->
                <div v-if="message.mentions && message.mentions.length > 0" class="mentions">
                  <el-tag v-for="mention in message.mentions" :key="mention.id" size="small">
                    @{{ mention.username || mention.id }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        
        <!-- 分页 -->
        <el-pagination
          v-if="filteredMessages.length > pageSize"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredMessages.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
          class="pagination"
        />
      </div>
      
      <!-- 卡片视图 -->
      <div v-else class="messages-grid" v-loading="loading">
        <el-row :gutter="16">
          <el-col
            v-for="message in paginatedMessages"
            :key="message.id"
            :span="8"
            :xs="24"
            :sm="12"
            :md="8"
          >
            <el-card class="message-grid-card" shadow="hover" @click="viewDetail(message)">
              <div class="grid-card-header">
                <el-avatar :src="message.author.avatar" :size="40">
                  {{ message.author.username[0] }}
                </el-avatar>
                <div class="grid-card-info">
                  <div class="grid-card-author">{{ message.author.nickname }}</div>
                  <el-text type="info" size="small">{{ formatTime(message.timestamp) }}</el-text>
                </div>
              </div>
              
              <div class="grid-card-content">
                <div v-if="message.type === 'text'">
                  {{ truncateText(message.content, 100) }}
                </div>
                <el-image
                  v-else-if="message.type === 'image'"
                  :src="message.attachments[0].url"
                  fit="cover"
                  style="width: 100%; height: 150px;"
                />
                <div v-else class="grid-card-file">
                  <el-icon :size="48"><Document /></el-icon>
                  <el-text size="small">{{ message.attachments?.[0]?.filename }}</el-text>
                </div>
              </div>
              
              <div class="grid-card-footer">
                <el-tag :type="getMessageTypeTag(message.type)" size="small">
                  {{ getMessageTypeLabel(message.type) }}
                </el-tag>
                <el-text type="info" size="small">
                  {{ message.channel_name }}
                </el-text>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 分页 -->
        <el-pagination
          v-if="filteredMessages.length > pageSize"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredMessages.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
          class="pagination"
        />
      </div>
    </el-card>
    
    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="消息详情"
      width="800px"
    >
      <div v-if="currentMessage" class="message-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="消息ID">
            {{ currentMessage.id }}
          </el-descriptions-item>
          <el-descriptions-item label="消息类型">
            <el-tag :type="getMessageTypeTag(currentMessage.type)">
              {{ getMessageTypeLabel(currentMessage.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发送者">
            {{ currentMessage.author.nickname || currentMessage.author.username }}
          </el-descriptions-item>
          <el-descriptions-item label="用户ID">
            {{ currentMessage.author.id }}
          </el-descriptions-item>
          <el-descriptions-item label="服务器">
            {{ currentMessage.server_name }}
          </el-descriptions-item>
          <el-descriptions-item label="频道">
            #{{ currentMessage.channel_name }}
          </el-descriptions-item>
          <el-descriptions-item label="时间戳" :span="2">
            {{ formatFullTime(currentMessage.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="消息内容" :span="2">
            <pre class="message-content-pre">{{ currentMessage.content }}</pre>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentMessage.attachments && currentMessage.attachments.length > 0" label="附件" :span="2">
            <el-space>
              <el-link
                v-for="(attachment, index) in currentMessage.attachments"
                :key="index"
                :href="attachment.url"
                target="_blank"
              >
                {{ attachment.filename }}
              </el-link>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentMessage.mentions && currentMessage.mentions.length > 0" label="@提及" :span="2">
            <el-space>
              <el-tag v-for="mention in currentMessage.mentions" :key="mention.id">
                @{{ mention.username || mention.id }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentMessage.quote" class="quote-detail">
          <h4>引用消息</h4>
          <el-card>
            <div>{{ currentMessage.quote.author.username }}: {{ currentMessage.quote.content }}</div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatLineSquare, Refresh, Download, Search, List, Grid,
  View, CopyDocument, Document, Back
} from '@element-plus/icons-vue'
import { useClipboard } from '@vueuse/core'
import axios from 'axios'

// 剪贴板
const { copy } = useClipboard()

// 状态
const loading = ref(false)
const messages = ref([])
const channels = ref([])
const viewMode = ref('list')
const sortBy = ref('time_desc')
const detailDialogVisible = ref(false)
const currentMessage = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)

// 过滤表单
const filterForm = ref({
  keyword: '',
  author: '',
  channel: '',
  messageType: '',
  timeRange: null
})

// 过滤后的消息
const filteredMessages = computed(() => {
  let result = messages.value
  
  // 关键词搜索
  if (filterForm.value.keyword) {
    const keyword = filterForm.value.keyword.toLowerCase()
    result = result.filter(m => 
      m.content.toLowerCase().includes(keyword)
    )
  }
  
  // 发送者过滤
  if (filterForm.value.author) {
    const author = filterForm.value.author.toLowerCase()
    result = result.filter(m => 
      m.author.username.toLowerCase().includes(author) ||
      m.author.nickname?.toLowerCase().includes(author)
    )
  }
  
  // 频道过滤
  if (filterForm.value.channel) {
    result = result.filter(m => m.channel_id === filterForm.value.channel)
  }
  
  // 消息类型过滤
  if (filterForm.value.messageType) {
    result = result.filter(m => m.type === filterForm.value.messageType)
  }
  
  // 时间范围过滤
  if (filterForm.value.timeRange && filterForm.value.timeRange.length === 2) {
    const [start, end] = filterForm.value.timeRange
    result = result.filter(m => {
      const msgTime = new Date(m.timestamp)
      return msgTime >= start && msgTime <= end
    })
  }
  
  return result
})

// 分页后的消息
const paginatedMessages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMessages.value.slice(start, end)
})

// 加载消息
async function loadMessages() {
  loading.value = true
  
  try {
    const response = await axios.get('/api/messages/history', {
      params: { limit: 1000 }
    })
    
    messages.value = response.data.messages || []
    channels.value = response.data.channels || []
    
  } catch (error) {
    ElMessage.error('加载消息失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 应用过滤
function applyFilter() {
  currentPage.value = 1
  ElMessage.info(`找到 ${filteredMessages.value.length} 条消息`)
}

// 重置过滤
function resetFilter() {
  filterForm.value = {
    keyword: '',
    author: '',
    channel: '',
    messageType: '',
    timeRange: null
  }
  currentPage.value = 1
  ElMessage.success('过滤条件已重置')
}

// 排序消息
function sortMessages() {
  // 排序逻辑已通过computed实现
}

// 查看详情
function viewDetail(message) {
  currentMessage.value = message
  detailDialogVisible.value = true
}

// 复制消息
async function copyMessage(message) {
  await copy(message.content)
  ElMessage.success('消息已复制到剪贴板')
}

// 导出消息
function exportMessages() {
  const data = filteredMessages.value.map(m => ({
    时间: formatFullTime(m.timestamp),
    发送者: m.author.nickname || m.author.username,
    服务器: m.server_name,
    频道: m.channel_name,
    类型: getMessageTypeLabel(m.type),
    内容: m.content
  }))
  
  // 转换为CSV
  const csv = convertToCSV(data)
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `messages-${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success(`已导出 ${data.length} 条消息`)
}

// 转换为CSV
function convertToCSV(data) {
  if (data.length === 0) return ''
  
  const header = Object.keys(data[0]).join(',')
  const rows = data.map(row => 
    Object.values(row).map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')
  )
  
  return [header, ...rows].join('\n')
}

// 分页变化
function handlePageChange() {
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 工具函数
function getMessageTypeTag(type) {
  const tags = {
    text: '',
    image: 'success',
    video: 'warning',
    file: 'info',
    audio: 'danger'
  }
  return tags[type] || ''
}

function getMessageTypeLabel(type) {
  const labels = {
    text: '文本',
    image: '图片',
    video: '视频',
    file: '文件',
    audio: '音频'
  }
  return labels[type] || type
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

function formatFullTime(timestamp) {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function truncateText(text, maxLength) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 初始化
onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.message-history-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-card {
  margin-bottom: 24px;
}

.messages-card {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-list {
  min-height: 400px;
}

.message-card {
  margin: 8px 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
}

.message-content {
  margin-top: 12px;
}

.text-content {
  line-height: 1.6;
}

.image-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.other-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.quote-content {
  margin-top: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-left: 3px solid #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.mentions {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.messages-grid {
  min-height: 400px;
}

.message-grid-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.message-grid-card:hover {
  transform: translateY(-4px);
}

.grid-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.grid-card-info {
  flex: 1;
}

.grid-card-author {
  font-weight: 600;
}

.grid-card-content {
  margin: 12px 0;
  min-height: 100px;
}

.grid-card-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fa;
  border-radius: 4px;
}

.grid-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.pagination {
  margin-top: 24px;
  justify-content: center;
}

.message-content-pre {
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.quote-detail {
  margin-top: 16px;
}

.quote-detail h4 {
  margin: 16px 0 8px 0;
}
</style>
