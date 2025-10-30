<template>
  <div class="step3-smart-mapping">
    <h2>🎯 步骤3: AI智能映射</h2>
    <p class="step-desc">AI将自动分析并推荐频道映射关系，您可以调整后一键应用</p>

    <!-- 加载KOOK频道 -->
    <div v-if="loading" class="loading-section">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在分析KOOK频道...</p>
    </div>

    <!-- 映射推荐列表 -->
    <div v-else-if="recommendations.length > 0" class="recommendations-section">
      <el-alert
        title="💡 AI推荐说明"
        type="info"
        :closable="false"
        show-icon
      >
        <p>基于频道名称、关键词和历史学习，AI为您推荐了以下映射：</p>
        <ul>
          <li>绿色徽章：高置信度推荐（90%+）</li>
          <li>蓝色徽章：一般推荐（70%+）</li>
          <li>灰色徽章：低置信度（50%+）</li>
        </ul>
      </el-alert>

      <div class="recommendations-list">
        <div
          v-for="(rec, index) in recommendations"
          :key="index"
          class="recommendation-item"
        >
          <!-- KOOK源频道 -->
          <div class="source-channel">
            <div class="channel-info">
              <el-icon><Folder /></el-icon>
              <div>
                <div class="channel-name">{{ rec.kook_channel.server_name }}</div>
                <div class="channel-subname"># {{ rec.kook_channel.name }}</div>
              </div>
            </div>
          </div>

          <el-icon class="arrow-icon"><ArrowRight /></el-icon>

          <!-- 推荐的目标频道 -->
          <div class="target-channels">
            <div
              v-for="(suggestion, sIndex) in rec.suggestions"
              :key="sIndex"
              class="suggestion-item"
            >
              <el-checkbox
                v-model="suggestion.selected"
                @change="handleSelectionChange(rec, suggestion)"
              >
                <div class="suggestion-content">
                  <div class="suggestion-header">
                    <img
                      :src="`/icons/${suggestion.platform}.svg`"
                      :alt="suggestion.platform"
                      class="platform-icon-small"
                    />
                    <span class="channel-name">{{ suggestion.channel_name }}</span>
                    <el-tag
                      :type="getConfidenceType(suggestion.score)"
                      size="small"
                    >
                      {{ (suggestion.score * 100).toFixed(0) }}%
                    </el-tag>
                  </div>
                  <div class="suggestion-reason">
                    {{ suggestion.reason }}
                  </div>
                </div>
              </el-checkbox>
            </div>

            <!-- 没有推荐时 -->
            <div v-if="rec.suggestions.length === 0" class="no-suggestion">
              <el-text type="info">暂无合适推荐，您可以稍后手动配置</el-text>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <el-divider />
      <div class="mapping-summary">
        <el-statistic title="KOOK频道总数" :value="recommendations.length" />
        <el-statistic title="AI推荐映射" :value="totalSuggestions" />
        <el-statistic title="已选择映射" :value="selectedMappings" />
      </div>
    </div>

    <!-- 无频道提示 -->
    <div v-else class="empty-section">
      <el-empty description="未检测到KOOK频道，请确保已登录并加入服务器" />
    </div>

    <!-- 底部操作 -->
    <div class="step-actions">
      <el-button size="large" @click="$emit('prev')">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>

      <el-space>
        <el-button size="large" @click="skipMapping">
          跳过映射
        </el-button>
        
        <el-button
          type="primary"
          size="large"
          :disabled="selectedMappings === 0"
          :loading="applying"
          @click="handleComplete"
        >
          <el-icon><Check /></el-icon>
          应用映射并完成（{{ selectedMappings }}个）
        </el-button>
      </el-space>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Loading,
  Folder,
  ArrowRight,
  ArrowLeft,
  Check
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  accountId: {
    type: Number,
    required: true
  },
  botConfigs: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['complete', 'prev'])

// 数据
const loading = ref(true)
const applying = ref(false)
const recommendations = ref([])

// 统计
const totalSuggestions = computed(() => {
  return recommendations.value.reduce((sum, rec) => sum + rec.suggestions.length, 0)
})

const selectedMappings = computed(() => {
  return recommendations.value.reduce((sum, rec) => {
    return sum + rec.suggestions.filter(s => s.selected).length
  }, 0)
})

// 加载推荐
onMounted(async () => {
  await loadRecommendations()
})

const loadRecommendations = async () => {
  loading.value = true
  
  try {
    // 1. 获取KOOK频道列表
    const channelsResponse = await api.get(`/api/accounts/${props.accountId}/channels`)
    const kookChannels = channelsResponse.data.channels || []
    
    if (kookChannels.length === 0) {
      loading.value = false
      return
    }
    
    // 2. 获取目标平台的频道列表
    const targetChannels = []
    
    for (const botConfig of props.botConfigs) {
      const response = await api.get(`/api/bots/${botConfig.id}/channels`)
      const channels = response.data.channels || []
      
      targetChannels.push(...channels.map(ch => ({
        ...ch,
        bot_id: botConfig.id,
        bot_name: botConfig.name,
        platform: botConfig.platform
      })))
    }
    
    // 3. 调用AI推荐API
    const recommendResponse = await api.post('/api/mappings/smart-recommend', {
      kook_channels: kookChannels,
      target_channels: targetChannels,
      account_id: props.accountId
    })
    
    const rawRecommendations = recommendResponse.data.recommendations || []
    
    // 4. 处理推荐结果（默认选中高置信度的）
    recommendations.value = rawRecommendations.map(rec => ({
      kook_channel: rec.kook_channel,
      suggestions: rec.suggestions.map(sug => ({
        ...sug,
        selected: sug.score >= 0.7  // 自动选中70%+的推荐
      }))
    }))
    
    ElMessage.success(`AI分析完成！推荐了${totalSuggestions.value}个映射`)
    
  } catch (error) {
    console.error('加载推荐失败:', error)
    ElMessage.error('加载推荐失败：' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 选择变化（用于学习）
const handleSelectionChange = (rec, suggestion) => {
  // 记录用户选择，用于AI学习
  api.post('/api/mappings/learn', {
    kook_channel_id: rec.kook_channel.id,
    target_channel_id: suggestion.channel_id,
    accepted: suggestion.selected
  }).catch(err => {
    console.error('记录学习数据失败:', err)
  })
}

// 置信度类型
const getConfidenceType = (score) => {
  if (score >= 0.9) return 'success'
  if (score >= 0.7) return 'primary'
  if (score >= 0.5) return 'info'
  return 'info'
}

// 跳过映射
const skipMapping = async () => {
  try {
    await ElMessageBox.confirm(
      '跳过映射后，消息将不会自动转发。您可以稍后在"频道映射"页面手动配置。',
      '确认跳过',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续配置',
        type: 'warning'
      }
    )
    
    emit('complete', {
      mappings: []
    })
  } catch {
    // 用户取消
  }
}

// 应用并完成
const handleComplete = async () => {
  applying.value = true
  
  try {
    // 收集所有选中的映射
    const mappings = []
    
    for (const rec of recommendations.value) {
      const selectedSuggestions = rec.suggestions.filter(s => s.selected)
      
      for (const sug of selectedSuggestions) {
        mappings.push({
          kook_server_id: rec.kook_channel.server_id,
          kook_channel_id: rec.kook_channel.id,
          kook_channel_name: rec.kook_channel.name,
          target_platform: sug.platform,
          target_bot_id: sug.bot_id,
          target_channel_id: sug.channel_id,
          target_channel_name: sug.channel_name
        })
      }
    }
    
    // 批量保存映射
    const response = await api.post('/api/mappings/batch', {
      mappings: mappings
    })
    
    if (response.data.success) {
      ElMessage.success(`✅ 成功创建${mappings.length}个频道映射！`)
      
      // 启动消息转发服务
      try {
        await api.post('/api/scrapers/start', {
          account_id: props.accountId
        })
        
        ElMessage.success('✅ 消息转发服务已启动！')
      } catch (error) {
        console.error('启动服务失败:', error)
        ElMessage.warning('映射已保存，但服务启动失败，请稍后手动启动')
      }
      
      emit('complete', {
        mappings: mappings
      })
    } else {
      ElMessage.error('保存映射失败')
    }
    
  } catch (error) {
    console.error('应用映射失败:', error)
    ElMessage.error('应用失败：' + (error.response?.data?.message || error.message))
  } finally {
    applying.value = false
  }
}
</script>

<style scoped>
.step3-smart-mapping h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
}

.step-desc {
  color: #909399;
  margin: 0 0 30px 0;
}

.loading-section {
  text-align: center;
  padding: 80px 20px;
}

.loading-section .el-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 20px;
}

.recommendations-section {
  animation: fadeIn 0.5s ease;
}

.recommendations-list {
  margin-top: 30px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.recommendation-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.source-channel {
  flex: 0 0 250px;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.channel-info .el-icon {
  font-size: 24px;
  color: #409eff;
}

.channel-name {
  font-weight: 600;
  color: #303133;
}

.channel-subname {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.arrow-icon {
  flex: 0 0 24px;
  font-size: 24px;
  color: #dcdfe6;
  margin-top: 20px;
}

.target-channels {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: all 0.2s;
}

.suggestion-item:hover {
  background: #ecf5ff;
}

.suggestion-content {
  margin-left: 24px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.platform-icon-small {
  width: 20px;
  height: 20px;
}

.suggestion-reason {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.no-suggestion {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.mapping-summary {
  display: flex;
  justify-content: space-around;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.empty-section {
  padding: 60px 20px;
}

.step-actions {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 深色主题 */
.dark .recommendation-item {
  background: #1e1e1e;
  border-color: #2c2c2c;
}

.dark .suggestion-item {
  background: #252525;
}

.dark .suggestion-item:hover {
  background: #2a2a2a;
}
</style>
