<template>
  <div class="complete-step">
    <el-result icon="success" title="">
      <template #icon>
        <div class="success-icon-wrapper">
          <el-icon :size="120" color="#67C23A" class="success-icon">
            <SuccessFilled />
          </el-icon>
          <div class="success-particles">
            <div class="particle" v-for="i in 12" :key="i"></div>
          </div>
        </div>
      </template>
      
      <template #title>
        <h1 class="result-title">✅ 配置完成！</h1>
      </template>
      
      <template #sub-title>
        <p class="result-subtitle">恭喜！您已成功完成基础配置</p>
      </template>
      
      <template #extra>
        <!-- 配置摘要 -->
        <el-card class="summary-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>配置摘要</span>
            </div>
          </template>
          
          <el-descriptions :column="1" border size="large">
            <el-descriptions-item>
              <template #label>
                <div class="label-content">
                  <el-icon><User /></el-icon>
                  <span>KOOK账号</span>
                </div>
              </template>
              <el-tag type="success" size="large">
                {{ accountEmail || '未设置' }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item>
              <template #label>
                <div class="label-content">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>已选服务器</span>
                </div>
              </template>
              <el-tag type="info" size="large">
                {{ selectedServersCount }} 个
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item>
              <template #label>
                <div class="label-content">
                  <el-icon><ChatLineSquare /></el-icon>
                  <span>已选频道</span>
                </div>
              </template>
              <el-tag type="info" size="large">
                {{ selectedChannelsCount }} 个
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item>
              <template #label>
                <div class="label-content">
                  <el-icon><CircleCheck /></el-icon>
                  <span>登录状态</span>
                </div>
              </template>
              <el-tag type="success" size="large">
                <el-icon><Check /></el-icon>
                已登录
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 下一步操作引导 -->
        <el-card class="next-steps-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Guide /></el-icon>
              <span>接下来您可以</span>
            </div>
          </template>
          
          <el-steps direction="vertical" :active="0" class="custom-steps">
            <el-step status="wait">
              <template #icon>
                <el-icon><Message /></el-icon>
              </template>
              <template #title>
                <div class="step-title">
                  <span>1. 配置转发Bot</span>
                  <el-tag type="warning" size="small">推荐</el-tag>
                </div>
              </template>
              <template #description>
                <div class="step-description">
                  <p>配置Discord/Telegram/飞书的Webhook或Bot，才能开始转发消息</p>
                  <el-button type="primary" size="small" @click="goToBots">
                    立即配置 →
                  </el-button>
                </div>
              </template>
            </el-step>
            
            <el-step status="wait">
              <template #icon>
                <el-icon><Share /></el-icon>
              </template>
              <template #title>
                <span>2. 设置频道映射</span>
              </template>
              <template #description>
                <div class="step-description">
                  <p>设置KOOK频道与目标平台的映射关系，支持智能映射</p>
                  <el-button size="small" @click="goToMapping">
                    立即配置 →
                  </el-button>
                </div>
              </template>
            </el-step>
            
            <el-step status="wait">
              <template #icon>
                <el-icon><VideoPlay /></el-icon>
              </template>
              <template #title>
                <span>3. 启动转发服务</span>
              </template>
              <template #description>
                <div class="step-description">
                  <p>一切就绪，启动消息转发服务，开始实时转发</p>
                  <el-button type="success" size="small" @click="startService">
                    <el-icon><VideoPlay /></el-icon>
                    立即启动
                  </el-button>
                </div>
              </template>
            </el-step>
          </el-steps>
        </el-card>
        
        <!-- 快速链接 -->
        <div class="quick-links-section">
          <h3>
            <el-icon><Link /></el-icon>
            快速链接
          </h3>
          <div class="quick-links">
            <el-button text @click="goToHelp">
              <el-icon><Reading /></el-icon>
              查看完整文档
            </el-button>
            <el-divider direction="vertical" />
            <el-button text @click="goToTutorials">
              <el-icon><VideoCamera /></el-icon>
              观看视频教程
            </el-button>
            <el-divider direction="vertical" />
            <el-button text @click="goToHome">
              <el-icon><HomeFilled /></el-icon>
              进入主界面
            </el-button>
          </div>
        </div>
        
        <!-- 主要操作按钮 -->
        <div class="main-actions">
          <el-button size="large" @click="goToHome">
            稍后配置，先看看
          </el-button>
          <el-button type="primary" size="large" @click="goToBots">
            <el-icon><Right /></el-icon>
            开始配置Bot
          </el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  SuccessFilled,
  Document,
  User,
  OfficeBuilding,
  ChatLineSquare,
  CircleCheck,
  Check,
  Guide,
  Message,
  Share,
  VideoPlay,
  Link,
  Reading,
  VideoCamera,
  HomeFilled,
  Right
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  accountEmail: {
    type: String,
    default: ''
  },
  selectedServers: {
    type: Array,
    default: () => []
  },
  selectedChannels: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

const selectedServersCount = computed(() => props.selectedServers?.length || 0)
const selectedChannelsCount = computed(() => props.selectedChannels?.length || 0)

// 方法
const goToBots = () => {
  router.push('/bots')
}

const goToMapping = () => {
  router.push('/mapping')
}

const goToHome = () => {
  router.push('/')
}

const goToHelp = () => {
  router.push('/help')
}

const goToTutorials = () => {
  router.push('/tutorials')
}

const startService = async () => {
  try {
    await api.post('/api/system/start')
    ElMessage.success('✅ 服务启动成功！')
    setTimeout(() => {
      router.push('/')
    }, 1000)
  } catch (error) {
    console.error('启动服务失败:', error)
    ElMessage.error('启动服务失败: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.complete-step {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.success-icon-wrapper {
  position: relative;
  display: inline-block;
  margin: 20px 0;
}

.success-icon {
  position: relative;
  z-index: 2;
  animation: bounce 1s ease-in-out;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-20px) scale(1.1);
  }
}

.success-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #67C23A;
  border-radius: 50%;
  opacity: 0;
  animation: particle-explode 1.5s ease-out infinite;
}

.particle:nth-child(1) { animation-delay: 0s; transform: rotate(0deg) translateX(0); }
.particle:nth-child(2) { animation-delay: 0.1s; transform: rotate(30deg) translateX(0); }
.particle:nth-child(3) { animation-delay: 0.2s; transform: rotate(60deg) translateX(0); }
.particle:nth-child(4) { animation-delay: 0.3s; transform: rotate(90deg) translateX(0); }
.particle:nth-child(5) { animation-delay: 0.4s; transform: rotate(120deg) translateX(0); }
.particle:nth-child(6) { animation-delay: 0.5s; transform: rotate(150deg) translateX(0); }
.particle:nth-child(7) { animation-delay: 0.6s; transform: rotate(180deg) translateX(0); }
.particle:nth-child(8) { animation-delay: 0.7s; transform: rotate(210deg) translateX(0); }
.particle:nth-child(9) { animation-delay: 0.8s; transform: rotate(240deg) translateX(0); }
.particle:nth-child(10) { animation-delay: 0.9s; transform: rotate(270deg) translateX(0); }
.particle:nth-child(11) { animation-delay: 1s; transform: rotate(300deg) translateX(0); }
.particle:nth-child(12) { animation-delay: 1.1s; transform: rotate(330deg) translateX(0); }

@keyframes particle-explode {
  0% {
    opacity: 0;
    transform: translateX(0) scale(1);
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateX(80px) scale(0);
  }
}

.result-title {
  font-size: 36px;
  margin: 10px 0;
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.result-subtitle {
  font-size: 18px;
  color: #909399;
}

.summary-card,
.next-steps-card {
  margin: 20px 0;
  text-align: left;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.label-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.custom-steps {
  padding: 20px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.step-description {
  padding: 10px 0;
}

.step-description p {
  margin-bottom: 10px;
  color: #606266;
  line-height: 1.6;
}

.quick-links-section {
  margin: 30px 0;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
}

.quick-links-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  color: #303133;
}

.quick-links {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-links .el-button {
  font-size: 15px;
}

.main-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.main-actions .el-button {
  height: 50px;
  padding: 0 40px;
  font-size: 16px;
}

/* 暗黑模式 */
.dark .result-title {
  background: linear-gradient(135deg, #85CE61 0%, #95D475 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .quick-links-section {
  background: linear-gradient(135deg, #2c2c2c 0%, #3a3a3a 100%);
}

.dark .quick-links-section h3 {
  color: #e5eaf3;
}
</style>
