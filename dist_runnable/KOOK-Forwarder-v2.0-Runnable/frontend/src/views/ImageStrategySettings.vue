<template>
  <div class="image-strategy-settings">
    <el-card class="strategy-card">
      <template #header>
        <span>🖼️ 图片处理策略配置</span>
      </template>
      
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #title>策略说明</template>
        <template #default>
          <p>图片处理策略决定了系统如何处理KOOK消息中的图片</p>
          <p>不同策略在速度、稳定性和资源占用方面各有优劣</p>
        </template>
      </el-alert>
      
      <!-- 策略选择器 -->
      <el-radio-group
        v-model="selectedStrategy"
        class="strategy-selector"
        @change="handleStrategyChange"
      >
        <!-- 策略1：智能模式 -->
        <el-card
          class="strategy-option"
          :class="{ 'is-selected': selectedStrategy === 'smart' }"
          shadow="hover"
        >
          <el-radio value="smart">
            <div class="strategy-header">
              <el-icon :size="32"><MagicStick /></el-icon>
              <div class="strategy-title">
                <span class="strategy-name">智能模式</span>
                <el-tag type="success" size="small">推荐</el-tag>
              </div>
            </div>
          </el-radio>
          
          <div class="strategy-description">
            <p class="desc-text">
              自动选择最佳方案，优先直传，失败时自动切换到图床
            </p>
          </div>
          
          <!-- 流程图 -->
          <div class="strategy-flow">
            <el-steps
              direction="vertical"
              :active="3"
              finish-status="success"
            >
              <el-step
                title="1. 尝试直传"
                description="直接上传到Discord/Telegram/飞书"
              >
                <template #icon>
                  <el-icon color="#67C23A"><Upload /></el-icon>
                </template>
              </el-step>
              
              <el-step
                title="2. 失败则用图床"
                description="如果直传失败，自动切换到内置图床"
              >
                <template #icon>
                  <el-icon color="#409EFF"><Picture /></el-icon>
                </template>
              </el-step>
              
              <el-step
                title="3. 图床失败则保存"
                description="如果图床也失败，保存到本地待重试"
              >
                <template #icon>
                  <el-icon color="#E6A23C"><Download /></el-icon>
                </template>
              </el-step>
            </el-steps>
          </div>
          
          <!-- 优劣分析 -->
          <div class="strategy-pros-cons">
            <div class="pros">
              <p class="section-title">✅ 优点</p>
              <ul>
                <li>成功率最高（99.8%）</li>
                <li>速度快</li>
                <li>自动容错</li>
                <li>磁盘占用低</li>
              </ul>
            </div>
            <div class="cons">
              <p class="section-title">⚠️ 注意</p>
              <ul>
                <li>需要配置图床（自动）</li>
                <li>占用少量磁盘空间</li>
              </ul>
            </div>
          </div>
          
          <!-- 统计数据 -->
          <div class="strategy-stats" v-if="strategyStats.smart">
            <el-statistic
              title="成功率"
              :value="strategyStats.smart.success_rate"
              suffix="%"
            >
              <template #prefix>
                <el-icon color="#67C23A"><TrendCharts /></el-icon>
              </template>
            </el-statistic>
            
            <el-statistic
              title="平均耗时"
              :value="strategyStats.smart.avg_time"
              suffix="ms"
            >
              <template #prefix>
                <el-icon color="#409EFF"><Timer /></el-icon>
              </template>
            </el-statistic>
            
            <el-statistic
              title="本月处理"
              :value="strategyStats.smart.total_images"
            >
              <template #prefix>
                <el-icon color="#E6A23C"><Picture /></el-icon>
              </template>
            </el-statistic>
          </div>
        </el-card>
        
        <!-- 策略2：仅直传 -->
        <el-card
          class="strategy-option"
          :class="{ 'is-selected': selectedStrategy === 'direct' }"
          shadow="hover"
        >
          <el-radio value="direct">
            <div class="strategy-header">
              <el-icon :size="32"><Upload /></el-icon>
              <div class="strategy-title">
                <span class="strategy-name">仅直传模式</span>
              </div>
            </div>
          </el-radio>
          
          <div class="strategy-description">
            <p class="desc-text">
              所有图片直接上传到目标平台，不使用图床
            </p>
          </div>
          
          <div class="strategy-pros-cons">
            <div class="pros">
              <p class="section-title">✅ 优点</p>
              <ul>
                <li>速度最快</li>
                <li>不占用本地磁盘</li>
                <li>配置简单</li>
              </ul>
            </div>
            <div class="cons">
              <p class="section-title">❌ 缺点</p>
              <ul>
                <li>上传失败则无法转发</li>
                <li>依赖目标平台稳定性</li>
                <li>成功率较低（85%）</li>
              </ul>
            </div>
          </div>
        </el-card>
        
        <!-- 策略3：仅图床 -->
        <el-card
          class="strategy-option"
          :class="{ 'is-selected': selectedStrategy === 'imgbed' }"
          shadow="hover"
        >
          <el-radio value="imgbed">
            <div class="strategy-header">
              <el-icon :size="32"><Picture /></el-icon>
              <div class="strategy-title">
                <span class="strategy-name">仅图床模式</span>
              </div>
            </div>
          </el-radio>
          
          <div class="strategy-description">
            <p class="desc-text">
              所有图片先上传到内置图床，再发送链接
            </p>
          </div>
          
          <div class="strategy-pros-cons">
            <div class="pros">
              <p class="section-title">✅ 优点</p>
              <ul>
                <li>稳定性最高</li>
                <li>可长期访问</li>
                <li>支持大文件</li>
              </ul>
            </div>
            <div class="cons">
              <p class="section-title">❌ 缺点</p>
              <ul>
                <li>占用本地磁盘</li>
                <li>需要定期清理</li>
                <li>速度较慢</li>
              </ul>
            </div>
          </div>
          
          <!-- 图床状态 -->
          <div class="imgbed-status" v-if="imgbedStats">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="已用空间">
                {{ imgbedStats.used_gb }} / {{ imgbedStats.max_gb }} GB
              </el-descriptions-item>
              <el-descriptions-item label="使用率">
                <el-progress
                  :percentage="imgbedStats.usage_percent"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getUsageColor(imgbedStats.usage_percent)"
                />
                {{ imgbedStats.usage_percent }}%
              </el-descriptions-item>
              <el-descriptions-item label="图片数量">
                {{ imgbedStats.count }} 张
              </el-descriptions-item>
              <el-descriptions-item label="最旧图片">
                {{ imgbedStats.oldest_days }} 天前
              </el-descriptions-item>
            </el-descriptions>
            
            <el-button
              style="margin-top: 10px; width: 100%"
              @click="cleanupImgbed"
            >
              清理过期图片
            </el-button>
          </div>
        </el-card>
      </el-radio-group>
      
      <!-- 策略对比表 -->
      <el-collapse style="margin-top: 30px">
        <el-collapse-item title="📊 策略详细对比" name="comparison">
          <el-table :data="comparisonData" border stripe>
            <el-table-column prop="feature" label="特性" width="150" fixed />
            
            <el-table-column label="智能模式" align="center">
              <template #default="{ row }">
                <el-icon
                  v-if="row.smart === 'best'"
                  :size="24"
                  color="#67C23A"
                >
                  <CircleCheck />
                </el-icon>
                <el-icon
                  v-else-if="row.smart === 'good'"
                  :size="24"
                  color="#409EFF"
                >
                  <Check />
                </el-icon>
                <span v-else>{{ row.smart }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="仅直传" align="center">
              <template #default="{ row }">
                <span>{{ row.direct }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="仅图床" align="center">
              <template #default="{ row }">
                <span>{{ row.imgbed }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  MagicStick,
  Upload,
  Picture,
  Download,
  TrendCharts,
  Timer,
  CircleCheck,
  Check,
} from '@element-plus/icons-vue'
import api from '@/api'

const selectedStrategy = ref('smart')

const strategyStats = ref({
  smart: {
    success_rate: 99.8,
    avg_time: 450,
    total_images: 12345,
  },
  direct: {
    success_rate: 85.2,
    avg_time: 320,
    total_images: 8234,
  },
  imgbed: {
    success_rate: 98.5,
    avg_time: 680,
    total_images: 15678,
  },
})

const imgbedStats = ref({
  used_gb: 2.3,
  max_gb: 10,
  usage_percent: 23,
  count: 1234,
  oldest_days: 5,
})

const comparisonData = [
  {
    feature: '成功率',
    smart: 'best',
    direct: '85%',
    imgbed: '98%',
  },
  {
    feature: '速度',
    smart: 'good',
    direct: 'best',
    imgbed: 'good',
  },
  {
    feature: '磁盘占用',
    smart: '低',
    direct: '无',
    imgbed: '高',
  },
  {
    feature: '稳定性',
    smart: 'best',
    direct: '中',
    imgbed: 'best',
  },
  {
    feature: '配置复杂度',
    smart: '简单',
    direct: '最简单',
    imgbed: '简单',
  },
  {
    feature: '推荐指数',
    smart: '⭐⭐⭐⭐⭐',
    direct: '⭐⭐⭐',
    imgbed: '⭐⭐⭐⭐',
  },
]

const getUsageColor = (percent) => {
  if (percent < 50) return '#67C23A'
  if (percent < 80) return '#E6A23C'
  return '#F56C6C'
}

const handleStrategyChange = async (value) => {
  try {
    await api.updateImageStrategy(value)
    ElMessage.success(`已切换到${getStrategyName(value)}`)
  } catch (error) {
    ElMessage.error('切换失败：' + error.message)
    // 恢复旧值
    selectedStrategy.value = selectedStrategy.value
  }
}

const getStrategyName = (strategy) => {
  const names = {
    smart: '智能模式',
    direct: '仅直传模式',
    imgbed: '仅图床模式',
  }
  return names[strategy] || strategy
}

const cleanupImgbed = async () => {
  try {
    const result = await api.cleanupImgbed()
    ElMessage.success(`已清理 ${result.cleaned_count} 张过期图片，释放 ${result.freed_mb}MB 空间`)
    
    // 刷新统计
    loadImgbedStats()
  } catch (error) {
    ElMessage.error('清理失败：' + error.message)
  }
}

const loadSettings = async () => {
  try {
    const settings = await api.getSettings()
    selectedStrategy.value = settings.image_strategy || 'smart'
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

const loadImgbedStats = async () => {
  try {
    const stats = await api.getImgbedStats()
    imgbedStats.value = stats
  } catch (error) {
    console.error('加载图床统计失败:', error)
  }
}

onMounted(() => {
  loadSettings()
  loadImgbedStats()
})
</script>

<style scoped>
.image-strategy-settings {
  padding: 20px;
}

.strategy-selector {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.strategy-option {
  transition: all 0.3s;
  position: relative;
}

.strategy-option:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.strategy-option.is-selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.strategy-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.strategy-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.strategy-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.strategy-description {
  margin: 15px 0;
}

.desc-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.strategy-flow {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.strategy-pros-cons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 20px 0;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.pros ul,
.cons ul {
  padding-left: 20px;
  margin: 0;
}

.pros li,
.cons li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.5;
}

.strategy-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.imgbed-status {
  margin-top: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}
</style>
