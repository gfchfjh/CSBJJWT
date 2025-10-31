<template>
  <div class="app-container">
    <!-- ✅ v17.0.0深度优化: 免责声明弹窗（首次启动强制显示） -->
    <DisclaimerDialog
      v-model="disclaimerVisible"
      @accepted="onDisclaimerAccepted"
      @declined="onDisclaimerDeclined"
    />
    
    <!-- ✅ P0-2优化: 首次运行检测器 -->
    <FirstRunDetector />
    
    <router-view />
    
    <!-- ✅ P0-5优化：友好错误提示对话框（全局） -->
    <ErrorDialog
      v-model="errorDialog.visible"
      :error-data="errorDialog.data"
      @fixed="onErrorFixed"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSystemStore } from './store/system'
import ErrorDialog from './components/ErrorDialog.vue'
import DisclaimerDialog from './views/DisclaimerDialog.vue'
import { globalErrorHandler } from './composables/useErrorHandler'
import FirstRunDetector from './components/FirstRunDetector.vue'

const systemStore = useSystemStore()

// ✅ P0-5优化：全局错误对话框状态
const errorDialog = reactive({
  visible: false,
  data: {}
})

// 监听全局错误处理器
watch(() => globalErrorHandler.showErrorDialog.value, (show) => {
  errorDialog.visible = show
  if (show) {
    errorDialog.data = globalErrorHandler.currentError.value || {}
  }
})

// 错误修复完成回调
const onErrorFixed = (result) => {
  console.log('✅ 错误已修复:', result)
}

// ✅ v17.0.0深度优化: 免责声明状态
const disclaimerVisible = ref(false)

onMounted(() => {
  // ✅ v17.0.0深度优化: 检查免责声明
  checkDisclaimer()
  
  // 初始化系统状态
  systemStore.fetchSystemStatus()
})

// ✅ v17.0.0深度优化: 检查免责声明状态
const checkDisclaimer = async () => {
  try {
    const response = await fetch('/api/disclaimer/status')
    if (response.ok) {
      const data = await response.json()
      
      // 如果未同意过，显示免责声明
      if (data.needs_accept) {
        // 延迟显示，确保页面已加载
        setTimeout(() => {
          disclaimerVisible.value = true
        }, 500)
      }
    } else {
      // API失败时，检查本地存储作为备选
      const accepted = localStorage.getItem('disclaimer_accepted')
      if (!accepted) {
        setTimeout(() => {
          disclaimerVisible.value = true
        }, 500)
      }
    }
  } catch (error) {
    console.error('检查免责声明状态失败:', error)
    // 出错时，仍然显示免责声明（安全起见）
    setTimeout(() => {
      disclaimerVisible.value = true
    }, 500)
  }
}

// ✅ v17.0.0深度优化: 用户同意免责声明
const onDisclaimerAccepted = () => {
  // 本地也保存一份（备份）
  localStorage.setItem('disclaimer_accepted', 'true')
  localStorage.setItem('disclaimer_accepted_at', new Date().toISOString())
  
  ElMessage.success({
    message: '感谢您的理解和支持，欢迎使用KOOK消息转发系统',
    duration: 3000
  })
}

// ✅ v17.0.0深度优化: 用户拒绝免责声明
const onDisclaimerDeclined = () => {
  ElMessage.warning('您已拒绝免责声明，应用将退出')
}
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100%;
}
</style>
