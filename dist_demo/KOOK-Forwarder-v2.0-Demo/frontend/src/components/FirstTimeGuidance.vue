<template>
  <transition name="slide-fade">
    <el-alert
      v-if="visible && isFirstTime"
      type="success"
      :closable="true"
      @close="handleClose"
      class="first-time-guidance"
    >
      <template #title>
        <div class="guidance-title">
          <el-icon :size="24"><SuccessFilled /></el-icon>
          <span>🎉 欢迎使用KOOK消息转发系统！</span>
        </div>
      </template>
      
      <div class="guidance-content">
        <p class="guidance-intro">
          您已成功添加KOOK账号并选择了监听的服务器！
          接下来只需要3步，即可开始转发消息：
        </p>

        <div class="steps-preview">
          <el-steps direction="vertical" :active="0">
            <el-step title="配置转发机器人" description="添加Discord/Telegram/飞书机器人">
              <template #icon>
                <el-icon><Robot /></el-icon>
              </template>
            </el-step>
            <el-step title="设置频道映射" description="将KOOK频道映射到目标平台">
              <template #icon>
                <el-icon><Connection /></el-icon>
              </template>
            </el-step>
            <el-step title="启动转发服务" description="开始自动转发消息">
              <template #icon>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </div>

        <div class="guidance-actions">
          <el-button type="primary" size="large" @click="startQuickSetup">
            <el-icon><MagicStick /></el-icon>
            开始快速配置（5分钟）
          </el-button>
          <el-button size="large" @click="exploreFirst">
            先看看主界面
          </el-button>
          <el-button size="large" @click="watchTutorial">
            <el-icon><VideoCamera /></el-icon>
            观看视频教程
          </el-button>
        </div>

        <div class="guidance-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>提示：您可以随时在"帮助"菜单中重新开始配置</span>
        </div>
      </div>
    </el-alert>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { SuccessFilled, Robot, Connection, VideoPlay, MagicStick, VideoCamera, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()
const visible = ref(true)
const isFirstTime = ref(false)

const emit = defineEmits(['startSetup', 'watchTutorial'])

onMounted(() => {
  // 检查是否是首次使用
  const wizardCompleted = localStorage.getItem('wizard_completed')
  const hasConfiguredBots = localStorage.getItem('has_configured_bots')
  const guidanceDismissed = sessionStorage.getItem('guidance_dismissed')
  
  // 如果完成了向导，但没有配置Bot，且本次会话没有关闭提示
  isFirstTime.value = wizardCompleted && !hasConfiguredBots && !guidanceDismissed
})

// 开始快速配置
function startQuickSetup() {
  visible.value = false
  sessionStorage.setItem('guidance_dismissed', 'true')
  emit('startSetup')
  router.push('/quick-setup')
}

// 先探索主界面
function exploreFirst() {
  visible.value = false
  sessionStorage.setItem('guidance_dismissed', 'true')
}

// 观看视频教程
function watchTutorial() {
  visible.value = false
  sessionStorage.setItem('guidance_dismissed', 'true')
  emit('watchTutorial')
}

// 关闭提示
function handleClose() {
  visible.value = false
  sessionStorage.setItem('guidance_dismissed', 'true')
}
</script>

<style scoped>
.first-time-guidance {
  margin: 20px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.guidance-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #67C23A;
}

.guidance-content {
  margin-top: 20px;
}

.guidance-intro {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 25px;
}

.steps-preview {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.guidance-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.guidance-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.5s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
