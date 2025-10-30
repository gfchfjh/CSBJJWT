<template>
  <div class="channel-mapping-step">
    <div class="step-header">
      <h2>🔀 第3步：设置频道映射</h2>
      <p>建立KOOK频道到目标平台的转发关系</p>
    </div>

    <el-alert
      title="🤖 智能推荐模式"
      type="success"
      :closable="false"
      show-icon
    >
      <p>系统会根据频道名称自动推荐最匹配的目标频道</p>
      <p>您也可以手动调整任何映射关系</p>
    </el-alert>

    <div class="mapping-mode">
      <el-radio-group v-model="mappingMode">
        <el-radio label="smart">
          <el-icon><MagicStick /></el-icon>
          智能推荐映射（推荐）
        </el-radio>
        <el-radio label="manual">
          <el-icon><Edit /></el-icon>
          手动配置映射
        </el-radio>
      </el-radio-group>
    </div>

    <!-- 智能推荐模式 -->
    <div v-if="mappingMode === 'smart'" class="smart-mapping">
      <el-button 
        type="primary" 
        @click="runSmartMapping"
        :loading="analyzing"
      >
        <el-icon><MagicStick /></el-icon>
        开始智能分析
      </el-button>

      <div v-if="smartRecommendations.length > 0" class="recommendations">
        <h3>📋 推荐映射结果：</h3>
        <p class="recommendation-tip">
          绿色勾选框表示推荐的映射，您可以取消不需要的映射
        </p>

        <div 
          v-for="(rec, index) in smartRecommendations"
          :key="index"
          class="recommendation-item"
        >
          <div class="source-channel">
            <el-icon class="channel-icon"><Folder /></el-icon>
            <div class="channel-info">
              <strong>{{ rec.kook_channel_name }}</strong>
              <span class="server-name">来自: {{ rec.kook_server_name }}</span>
            </div>
          </div>

          <el-icon class="arrow-icon"><Right /></el-icon>

          <div class="target-channels">
            <el-checkbox-group v-model="rec.selected_targets">
              <div 
                v-for="target in rec.recommended_targets"
                :key="`${target.platform}-${target.channel_id}`"
                class="target-option"
              >
                <el-checkbox :label="`${target.platform}-${target.channel_id}`">
                  <div class="target-info">
                    <el-tag :type="getPlatformTagType(target.platform)" size="small">
                      {{ target.platform }}
                    </el-tag>
                    <span>{{ target.channel_name }}</span>
                    <el-tag 
                      v-if="target.confidence > 0.8" 
                      type="success" 
                      size="small"
                      effect="dark"
                    >
                      推荐度: {{ (target.confidence * 100).toFixed(0) }}%
                    </el-tag>
                    <el-tag 
                      v-else
                      type="info" 
                      size="small"
                    >
                      推荐度: {{ (target.confidence * 100).toFixed(0) }}%
                    </el-tag>
                  </div>
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </div>
        </div>
      </div>
    </div>

    <!-- 手动配置模式 -->
    <div v-else class="manual-mapping">
      <div class="mapping-table">
        <el-button type="primary" @click="addMapping">
          <el-icon><Plus /></el-icon>
          添加映射
        </el-button>

        <el-table :data="manualMappings" style="margin-top: 20px;">
          <el-table-column label="KOOK频道" width="250">
            <template #default="scope">
              <el-cascader
                v-model="scope.row.kook_channel"
                :options="kookChannelTree"
                placeholder="选择KOOK频道"
                :props="{ expandTrigger: 'hover' }"
                style="width: 100%;"
              />
            </template>
          </el-table-column>

          <el-table-column label="转发目标">
            <template #default="scope">
              <el-select 
                v-model="scope.row.targets" 
                multiple 
                placeholder="选择转发目标"
                style="width: 100%;"
              >
                <el-option-group
                  v-for="platform in ['discord', 'telegram', 'feishu']"
                  :key="platform"
                  :label="platform.toUpperCase()"
                >
                  <el-option
                    v-for="bot in getBotsForPlatform(platform)"
                    :key="bot.id"
                    :label="bot.name"
                    :value="`${platform}-${bot.id}`"
                  />
                </el-option-group>
              </el-select>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button 
                size="small" 
                type="danger" 
                @click="removeMapping(scope.$index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 映射预览 -->
    <div v-if="totalMappingsCount > 0" class="mapping-summary">
      <el-divider />
      <h3>📊 映射统计：</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="KOOK频道数" :value="mappedKookChannelsCount" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="总映射数" :value="totalMappingsCount" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="目标平台数" :value="targetPlatformsCount" />
        </el-col>
      </el-row>
    </div>

    <!-- 底部按钮 -->
    <div class="step-footer">
      <el-button @click="handlePrev">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      
      <el-button 
        type="primary" 
        @click="handleNext"
        :disabled="totalMappingsCount === 0"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  MagicStick, 
  Edit, 
  Folder, 
  Right, 
  Plus,
  ArrowLeft, 
  ArrowRight 
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

const mappingMode = ref('smart')
const analyzing = ref(false)
const smartRecommendations = ref([])
const manualMappings = reactive([])
const kookChannelTree = ref([])

// 获取KOOK频道树
const fetchKookChannels = async () => {
  try {
    const response = await api.get('/api/servers/discover')
    kookChannelTree.value = response.data.servers.map(server => ({
      value: server.id,
      label: server.name,
      children: server.channels.map(channel => ({
        value: channel.id,
        label: channel.name
      }))
    }))
  } catch (error) {
    ElMessage.error('获取KOOK频道失败：' + error.message)
  }
}

// 智能推荐映射
const runSmartMapping = async () => {
  analyzing.value = true
  
  try {
    const response = await api.post('/api/smart-mapping/recommend')
    
    if (response.data.success) {
      smartRecommendations.value = response.data.recommendations.map(rec => ({
        ...rec,
        selected_targets: rec.recommended_targets
          .filter(t => t.confidence > 0.6)
          .map(t => `${t.platform}-${t.channel_id}`)
      }))
      
      ElMessage.success(`✅ 智能分析完成！找到 ${smartRecommendations.value.length} 个推荐映射`)
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('智能分析失败：' + error.message)
  } finally {
    analyzing.value = false
  }
}

// 手动添加映射
const addMapping = () => {
  manualMappings.push({
    kook_channel: [],
    targets: []
  })
}

// 删除映射
const removeMapping = (index) => {
  manualMappings.splice(index, 1)
}

// 获取指定平台的Bot列表
const getBotsForPlatform = (platform) => {
  // TODO: 从props或store获取已配置的Bot
  return []
}

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const types = {
    'discord': 'primary',
    'telegram': 'success',
    'feishu': 'warning'
  }
  return types[platform] || 'info'
}

// 计算映射统计
const mappedKookChannelsCount = computed(() => {
  if (mappingMode.value === 'smart') {
    return smartRecommendations.value.filter(r => r.selected_targets.length > 0).length
  } else {
    return manualMappings.filter(m => m.kook_channel.length > 0 && m.targets.length > 0).length
  }
})

const totalMappingsCount = computed(() => {
  if (mappingMode.value === 'smart') {
    return smartRecommendations.value.reduce((sum, rec) => sum + rec.selected_targets.length, 0)
  } else {
    return manualMappings.reduce((sum, m) => sum + m.targets.length, 0)
  }
})

const targetPlatformsCount = computed(() => {
  let platforms = new Set()
  
  if (mappingMode.value === 'smart') {
    smartRecommendations.value.forEach(rec => {
      rec.selected_targets.forEach(target => {
        const platform = target.split('-')[0]
        platforms.add(platform)
      })
    })
  } else {
    manualMappings.forEach(m => {
      m.targets.forEach(target => {
        const platform = target.split('-')[0]
        platforms.add(platform)
      })
    })
  }
  
  return platforms.size
})

// 导出映射数据
const exportMappings = () => {
  if (mappingMode.value === 'smart') {
    return smartRecommendations.value
      .filter(rec => rec.selected_targets.length > 0)
      .map(rec => ({
        kook_server_id: rec.kook_server_id,
        kook_channel_id: rec.kook_channel_id,
        kook_channel_name: rec.kook_channel_name,
        targets: rec.selected_targets.map(target => {
          const [platform, channel_id] = target.split('-')
          return { platform, channel_id }
        })
      }))
  } else {
    return manualMappings
      .filter(m => m.kook_channel.length > 0 && m.targets.length > 0)
      .map(m => ({
        kook_server_id: m.kook_channel[0],
        kook_channel_id: m.kook_channel[1],
        targets: m.targets.map(target => {
          const [platform, channel_id] = target.split('-')
          return { platform, channel_id }
        })
      }))
  }
}

const handlePrev = () => {
  emit('prev')
}

const handleNext = () => {
  if (totalMappingsCount.value === 0) {
    ElMessage.warning('请至少配置一个频道映射')
    return
  }

  const mappings = exportMappings()
  emit('next', mappings)
}

// 组件挂载时获取KOOK频道
fetchKookChannels()
</script>

<style scoped>
.channel-mapping-step {
  max-width: 900px;
  margin: 0 auto;
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 10px 0;
}

.step-header p {
  color: #909399;
  font-size: 14px;
}

.mapping-mode {
  margin: 20px 0;
  text-align: center;
}

.smart-mapping,
.manual-mapping {
  margin-top: 30px;
}

.recommendations {
  margin-top: 20px;
}

.recommendations h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 10px;
}

.recommendation-tip {
  font-size: 13px;
  color: #909399;
  margin-bottom: 20px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  margin-bottom: 15px;
  background: #f5f7fa;
}

.source-channel {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 250px;
}

.channel-icon {
  font-size: 24px;
  color: #409EFF;
}

.channel-info strong {
  display: block;
  font-size: 15px;
  color: #303133;
}

.server-name {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}

.arrow-icon {
  font-size: 20px;
  color: #909399;
  flex-shrink: 0;
}

.target-channels {
  flex: 1;
}

.target-option {
  margin-bottom: 10px;
}

.target-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mapping-summary {
  margin-top: 30px;
}

.mapping-summary h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
}

.step-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #DCDFE6;
  display: flex;
  justify-content: space-between;
}
</style>
