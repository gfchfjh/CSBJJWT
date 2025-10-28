<template>
  <div class="smart-mapping-recommendation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🧠 智能映射推荐</span>
          <el-tag type="primary">AI驱动</el-tag>
        </div>
      </template>
      
      <!-- 输入KOOK频道 -->
      <el-form label-width="120px">
        <el-form-item label="KOOK频道">
          <el-input 
            v-model="kookChannelName" 
            placeholder="例如: #公告频道"
            @input="onChannelNameChange"
          >
            <template #prefix>
              <el-icon><ChatDotSquare /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="目标平台">
          <el-select v-model="selectedPlatform" placeholder="选择平台" @change="loadTargetChannels">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <!-- 推荐结果 -->
      <div v-if="suggestions.length > 0" class="suggestions-section">
        <h3>💡 智能推荐结果</h3>
        
        <el-alert 
          type="info" 
          :closable="false" 
          style="margin-bottom: 15px;"
        >
          基于三重匹配算法（完全匹配 + 相似匹配 + 关键词匹配）+ 历史学习
        </el-alert>
        
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="suggestion-item"
          :class="getSuggestionClass(suggestion.confidence)"
          @click="selectSuggestion(suggestion)"
        >
          <div class="suggestion-rank">
            {{ index + 1 }}
          </div>
          
          <div class="suggestion-content">
            <div class="suggestion-channel">
              <el-icon><ChatLineSquare /></el-icon>
              {{ suggestion.channel.name }}
            </div>
            <div class="suggestion-meta">
              ID: {{ suggestion.channel.id }}
            </div>
          </div>
          
          <div class="suggestion-confidence">
            <el-progress
              type="circle"
              :percentage="suggestion.confidence"
              :width="60"
              :stroke-width="6"
              :color="getConfidenceColor(suggestion.confidence)"
            >
              <template #default="{ percentage }">
                <span style="font-size: 12px; font-weight: bold;">{{ percentage }}%</span>
              </template>
            </el-progress>
            <div class="confidence-level">
              {{ suggestion.confidence_level }}置信度
            </div>
          </div>
          
          <div class="suggestion-action">
            <el-button
              v-if="suggestion.recommended"
              type="primary"
              size="small"
              @click.stop="selectSuggestion(suggestion)"
            >
              选择
            </el-button>
            <el-button
              v-else
              size="small"
              @click.stop="selectSuggestion(suggestion)"
            >
              选择
            </el-button>
          </div>
        </div>
        
        <div v-if="suggestions.length === 0" class="no-suggestions">
          <el-empty description="未找到匹配的频道">
            <el-button type="primary" @click="manualMapping">手动配置映射</el-button>
          </el-empty>
        </div>
      </div>
      
      <!-- 加载中 -->
      <div v-if="loading" class="loading-section">
        <el-skeleton :rows="3" animated />
      </div>
      
      <!-- 学习引擎统计 -->
      <div v-if="showStats" class="stats-section">
        <el-divider />
        <h4>📊 学习引擎统计</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="总映射数">
            {{ stats.total_unique_mappings || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="映射总次数">
            {{ stats.total_mapping_count || 0 }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="stats.top_mappings && stats.top_mappings.length > 0" style="margin-top: 15px;">
          <strong>最常用映射：</strong>
          <ul style="margin-top: 10px; font-size: 13px;">
            <li v-for="mapping in stats.top_mappings.slice(0, 5)" :key="mapping.kook_channel">
              {{ mapping.kook_channel }} → {{ mapping.target_channel }} ({{ mapping.count }}次)
            </li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotSquare, ChatLineSquare } from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['select'])

const kookChannelName = ref('')
const selectedPlatform = ref('discord')
const suggestions = ref([])
const loading = ref(false)
const showStats = ref(true)
const stats = ref({})

let debounceTimer = null

const onChannelNameChange = () => {
  // 防抖：500ms后才执行推荐
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (kookChannelName.value.trim()) {
      getSuggestions()
    }
  }, 500)
}

const loadTargetChannels = async () => {
  // 加载目标平台的频道列表（这里简化处理）
  if (kookChannelName.value.trim()) {
    getSuggestions()
  }
}

const getSuggestions = async () => {
  if (!kookChannelName.value.trim()) {
    suggestions.value = []
    return
  }
  
  try {
    loading.value = true
    
    // 这里应该先获取目标平台的频道列表
    // 简化演示，使用模拟数据
    const targetChannels = await fetchTargetChannels(selectedPlatform.value)
    
    const response = await api.post('/api/mapping/learning/suggest', {
      kook_channel_name: kookChannelName.value,
      target_channels: targetChannels
    })
    
    suggestions.value = response.data.suggestions || []
    
    if (suggestions.value.length > 0) {
      ElMessage.success(`找到 ${suggestions.value.length} 个推荐映射`)
    }
    
  } catch (error) {
    ElMessage.error('获取推荐失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const fetchTargetChannels = async (platform) => {
  // 实际应该调用API获取目标平台的频道
  // 这里返回模拟数据
  return [
    { id: 'ch_announcements', name: 'announcements', platform: 'discord' },
    { id: 'ch_events', name: 'events', platform: 'discord' },
    { id: 'ch_updates', name: 'updates', platform: 'discord' },
  ]
}

const getSuggestionClass = (confidence) => {
  if (confidence >= 70) return 'suggestion-high'
  if (confidence >= 50) return 'suggestion-medium'
  return 'suggestion-low'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 70) return '#67C23A'
  if (confidence >= 50) return '#E6A23C'
  return '#F56C6C'
}

const selectSuggestion = (suggestion) => {
  emit('select', {
    kook_channel: kookChannelName.value,
    target_channel: suggestion.channel,
    confidence: suggestion.confidence
  })
  
  ElMessage.success('已选择该映射')
  
  // 记录到学习引擎
  recordMapping(suggestion.channel.id)
}

const recordMapping = async (targetChannelId) => {
  try {
    await api.post('/api/mapping/learning/record', null, {
      params: {
        kook_channel_id: kookChannelName.value,
        target_channel_id: targetChannelId
      }
    })
  } catch (error) {
    console.error('记录映射失败:', error)
  }
}

const manualMapping = () => {
  router.push('/mapping')
}

// 加载统计信息
const loadStats = async () => {
  try {
    const response = await api.get('/api/mapping/learning/stats')
    stats.value = response.data.stats || {}
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

loadStats()
</script>

<style scoped>
.smart-mapping-recommendation {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.suggestions-section {
  margin-top: 20px;
}

.suggestions-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.suggestion-high {
  background: #F0F9FF;
  border-color: #67C23A;
}

.suggestion-medium {
  background: #FDF6EC;
  border-color: #E6A23C;
}

.suggestion-low {
  background: #FEF0F0;
  border-color: #F56C6C;
}

.suggestion-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.suggestion-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-channel {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.suggestion-meta {
  font-size: 12px;
  color: #909399;
}

.suggestion-confidence {
  text-align: center;
  flex-shrink: 0;
}

.confidence-level {
  font-size: 12px;
  color: #606266;
  margin-top: 5px;
}

.suggestion-action {
  flex-shrink: 0;
}

.no-suggestions {
  padding: 40px;
  text-align: center;
}

.loading-section {
  padding: 20px;
}

.stats-section {
  margin-top: 20px;
}

.stats-section h4 {
  margin-bottom: 15px;
  font-size: 15px;
  color: #303133;
}
</style>
