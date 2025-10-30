<template>
  <div class="completion-step">
    <div class="success-animation">
      <el-icon :size="120" color="#67C23A">
        <CircleCheckFilled />
      </el-icon>
    </div>

    <h2>🎉 配置完成！</h2>
    <p class="subtitle">您已成功完成所有基础配置，系统已准备就绪</p>

    <div class="configuration-summary">
      <el-card shadow="hover">
        <template #header>
          <h3>📋 配置摘要</h3>
        </template>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="KOOK账号">
            <el-tag type="success">
              <el-icon><CircleCheckFilled /></el-icon>
              已连接
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="转发Bot">
            <div class="bot-summary">
              <el-tag v-if="stats.discord > 0" type="primary">
                Discord: {{ stats.discord }}个
              </el-tag>
              <el-tag v-if="stats.telegram > 0" type="success">
                Telegram: {{ stats.telegram }}个
              </el-tag>
              <el-tag v-if="stats.feishu > 0" type="warning">
                飞书: {{ stats.feishu }}个
              </el-tag>
            </div>
          </el-descriptions-item>

          <el-descriptions-item label="频道映射">
            <el-tag type="info">
              {{ stats.mappings }}个映射关系
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <div class="next-steps">
      <h3>🚀 接下来您可以：</h3>
      
      <el-timeline>
        <el-timeline-item 
          type="primary" 
          :hollow="false"
          timestamp="立即开始"
        >
          <el-card>
            <h4>✨ 启动消息转发服务</h4>
            <p>点击下方"完成并启动"按钮，系统将开始自动转发KOOK消息</p>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          type="success" 
          hollow
          timestamp="可选操作"
        >
          <el-card>
            <h4>⚙️ 调整高级设置</h4>
            <p>在设置页面配置消息过滤规则、图片处理策略等</p>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          type="warning" 
          hollow
          timestamp="可选操作"
        >
          <el-card>
            <h4>📊 查看实时监控</h4>
            <p>在主界面查看转发统计、成功率、队列状态等</p>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          type="info" 
          hollow
          timestamp="需要帮助"
        >
          <el-card>
            <h4>📖 查看完整文档</h4>
            <p>访问帮助中心了解更多高级功能和使用技巧</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <div class="tips-section">
      <el-alert
        title="💡 使用提示"
        type="success"
        :closable="false"
        show-icon
      >
        <ul>
          <li>所有配置都可以在稍后修改和调整</li>
          <li>建议先测试少量频道的转发效果</li>
          <li>可以随时添加更多Bot或映射关系</li>
          <li>遇到问题可查看FAQ或联系技术支持</li>
        </ul>
      </el-alert>
    </div>

    <div class="completion-actions">
      <el-button size="large" @click="handleSkipStart">
        稍后手动启动
      </el-button>
      
      <el-button 
        type="primary" 
        size="large"
        @click="handleFinishAndStart"
        :loading="starting"
      >
        <el-icon class="el-icon--left"><VideoPlay /></el-icon>
        完成并启动服务
      </el-button>
    </div>

    <div class="quick-links">
      <el-link type="primary" @click="openHelp">
        <el-icon><QuestionFilled /></el-icon>
        查看帮助文档
      </el-link>
      <el-divider direction="vertical" />
      <el-link type="success" @click="openCommunity">
        <el-icon><ChatDotRound /></el-icon>
        加入用户社区
      </el-link>
      <el-divider direction="vertical" />
      <el-link type="warning" @click="provideFeedback">
        <el-icon><EditPen /></el-icon>
        提供反馈
      </el-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  CircleCheckFilled, 
  VideoPlay,
  QuestionFilled,
  ChatDotRound,
  EditPen
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['finish'])

const starting = ref(false)

// 配置统计（从前面的步骤传递过来）
const stats = reactive({
  discord: 1,
  telegram: 0,
  feishu: 0,
  mappings: 3
})

const handleFinishAndStart = async () => {
  starting.value = true
  
  try {
    // 启动服务
    await api.post('/api/service/start')
    
    ElMessage.success('🎉 服务启动成功！系统开始转发消息')
    
    // 等待1秒后跳转
    setTimeout(() => {
      emit('finish')
    }, 1000)
  } catch (error) {
    ElMessage.error('服务启动失败：' + error.message)
    starting.value = false
  }
}

const handleSkipStart = async () => {
  const result = await ElMessageBox.confirm(
    '您可以稍后在主界面手动启动服务。确定要跳过吗？',
    '确认',
    {
      type: 'info',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).catch(() => false)

  if (result) {
    emit('finish')
  }
}

const openHelp = () => {
  // TODO: 打开帮助文档
  ElMessage.info('打开帮助文档')
}

const openCommunity = () => {
  // TODO: 打开社区链接
  window.open('https://github.com/gfchfjh/CSBJJWT/discussions', '_blank')
}

const provideFeedback = () => {
  // TODO: 打开反馈表单
  window.open('https://github.com/gfchfjh/CSBJJWT/issues', '_blank')
}
</script>

<style scoped>
.completion-step {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
}

.success-animation {
  margin-bottom: 30px;
  animation: scaleIn 0.5s ease-out;
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

h2 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 10px 0;
}

.subtitle {
  font-size: 16px;
  color: #606266;
  margin-bottom: 40px;
}

.configuration-summary {
  margin-bottom: 40px;
  text-align: left;
}

.configuration-summary h3 {
  font-size: 18px;
  color: #303133;
  margin: 0;
}

.bot-summary {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.next-steps {
  margin-bottom: 40px;
  text-align: left;
}

.next-steps h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
  text-align: center;
}

.next-steps :deep(.el-card) {
  border: none;
  background: #f5f7fa;
}

.next-steps h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.next-steps p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.tips-section {
  margin-bottom: 40px;
  text-align: left;
}

.tips-section ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.tips-section li {
  margin: 5px 0;
  color: #606266;
}

.completion-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 30px;
}

.quick-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
}

.quick-links .el-link {
  font-size: 14px;
}
</style>
