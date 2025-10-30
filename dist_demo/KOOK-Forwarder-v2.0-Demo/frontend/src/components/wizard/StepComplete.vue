<template>
  <el-card class="step-card complete-card">
    <div class="complete-content">
      <!-- 成功图标 -->
      <div class="success-icon">
        <el-icon :size="120" color="#67C23A">
          <CircleCheck />
        </el-icon>
      </div>

      <h1 class="complete-title">🎉 配置完成！</h1>
      <p class="complete-subtitle">您的KOOK消息转发系统已准备就绪</p>

      <!-- 配置摘要 -->
      <el-descriptions 
        :column="2" 
        border 
        class="config-summary"
        title="配置摘要"
      >
        <el-descriptions-item label="KOOK账号">
          <el-tag type="success">
            {{ props.wizardData.accounts?.length || 0 }} 个
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="监听服务器">
          <el-tag type="primary">
            {{ serverCount }} 个
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="监听频道">
          <el-tag type="warning">
            {{ props.wizardData.selectedChannels?.length || 0 }} 个
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="转发平台">
          <el-tag 
            v-for="platform in props.wizardData.selectedPlatforms || []" 
            :key="platform"
            style="margin-right: 5px"
          >
            {{ platformNames[platform] || platform }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="频道映射">
          <el-tag type="info">
            {{ props.wizardData.mappings?.length || estimatedMappings }} 个
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="配置模式">
          <el-tag :type="props.mode === 'quick' ? 'success' : 'warning'">
            {{ props.mode === 'quick' ? '快速模式' : '专业模式' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 下一步建议 -->
      <div class="next-steps">
        <h3>💡 接下来您可以：</h3>
        <el-timeline>
          <el-timeline-item 
            timestamp="Step 1" 
            placement="top"
            type="primary"
          >
            <el-card>
              <h4>🚀 启动转发服务</h4>
              <p>点击下方"进入主界面"，然后点击"启动服务"开始自动转发消息</p>
            </el-card>
          </el-timeline-item>

          <el-timeline-item 
            timestamp="Step 2" 
            placement="top"
            type="success"
          >
            <el-card>
              <h4>🎯 优化频道映射</h4>
              <p>在"频道映射"页面查看和调整自动创建的映射关系</p>
            </el-card>
          </el-timeline-item>

          <el-timeline-item 
            timestamp="Step 3" 
            placement="top"
            type="warning"
          >
            <el-card>
              <h4>🔧 配置过滤规则</h4>
              <p>在"过滤规则"页面设置关键词过滤、用户过滤等（可选）</p>
            </el-card>
          </el-timeline-item>

          <el-timeline-item 
            timestamp="Step 4" 
            placement="top"
            type="info"
          >
            <el-card>
              <h4>📊 查看实时日志</h4>
              <p>在"实时日志"页面监控消息转发情况</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 快捷提示 -->
      <el-alert
        v-if="props.mode === 'quick'"
        title="💡 快速模式提示"
        type="success"
        :closable="false"
        show-icon
        class="quick-tip"
      >
        <p>系统已使用智能映射自动配置频道，准确度约90%</p>
        <p>如需调整映射关系，请在主界面的"频道映射"页面进行修改</p>
      </el-alert>

      <!-- 主操作按钮 -->
      <div class="main-actions">
        <el-button 
          type="primary" 
          size="large"
          @click="handleComplete"
        >
          <el-icon><Promotion /></el-icon>
          进入主界面
        </el-button>

        <el-button 
          size="large"
          @click="restartWizard"
        >
          <el-icon><Refresh /></el-icon>
          重新配置
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { 
  CircleCheck, 
  Promotion, 
  Refresh 
} from '@element-plus/icons-vue'

const props = defineProps({
  mode: String,
  wizardData: Object
})

const emit = defineEmits(['complete', 'restart'])

const platformNames = {
  discord: 'Discord',
  telegram: 'Telegram',
  feishu: '飞书'
}

// 计算服务器数量（去重）
const serverCount = computed(() => {
  const serverIds = new Set()
  props.wizardData.selectedChannels?.forEach(ch => {
    serverIds.add(ch.server_id)
  })
  return serverIds.size
})

// 预估映射数
const estimatedMappings = computed(() => {
  const channels = props.wizardData.selectedChannels?.length || 0
  const platforms = props.wizardData.selectedPlatforms?.length || 1
  return channels * platforms
})

const handleComplete = () => {
  emit('complete')
}

const restartWizard = () => {
  if (confirm('确定要重新配置吗？当前配置将被保留。')) {
    emit('restart')
  }
}
</script>

<style scoped>
.step-card {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
}

.complete-content {
  text-align: center;
  padding: 40px 20px;
}

.success-icon {
  margin-bottom: 30px;
  animation: scaleIn 0.6s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.complete-title {
  font-size: 36px;
  color: #303133;
  margin: 0 0 10px 0;
}

.complete-subtitle {
  font-size: 18px;
  color: #909399;
  margin-bottom: 40px;
}

.config-summary {
  margin-bottom: 40px;
  text-align: left;
}

.next-steps {
  text-align: left;
  margin: 40px 0;
  padding: 30px;
  background: #f5f7fa;
  border-radius: 8px;
}

.next-steps h3 {
  margin-top: 0;
  color: #303133;
}

.next-steps :deep(.el-timeline-item__wrapper) {
  padding-left: 20px;
}

.next-steps .el-card {
  margin-bottom: 0;
}

.next-steps h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.next-steps p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.quick-tip {
  margin: 30px 0;
}

.quick-tip p {
  margin: 5px 0;
}

.main-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.main-actions .el-button {
  min-width: 180px;
  font-size: 16px;
  padding: 16px 32px;
}
</style>
