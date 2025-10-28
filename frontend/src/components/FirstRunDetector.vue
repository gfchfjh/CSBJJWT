<template>
  <!-- 首次运行检测器（隐藏组件，自动执行） -->
  <div v-if="false"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElNotification } from 'element-plus'
import api from '@/api'

const router = useRouter()

onMounted(async () => {
  await checkFirstRun()
})

/**
 * 检查是否首次运行
 */
const checkFirstRun = async () => {
  try {
    const response = await api.get('/api/wizard/check-first-run')
    
    if (response.data.is_first_run) {
      // 🔥 首次运行，显示欢迎弹窗
      await showWelcomeDialog()
    } else if (!response.data.wizard_completed) {
      // 向导未完成，检查配置完整性
      await checkConfigCompleteness()
    }
  } catch (error) {
    console.error('首次运行检测失败:', error)
  }
}

/**
 * 显示欢迎弹窗
 */
const showWelcomeDialog = async () => {
  try {
    await ElMessageBox.confirm(`
      <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: #409EFF; margin-bottom: 20px;">🎉 欢迎使用KOOK消息转发系统！</h2>
        
        <div style="text-align: left; margin: 20px 0; padding: 15px; background: #f5f7fa; border-radius: 8px;">
          <p style="margin: 10px 0;"><strong>我们将用3步帮您完成配置：</strong></p>
          <p style="margin: 8px 0;">1️⃣ 登录KOOK账号（1分钟）</p>
          <p style="margin: 8px 0;">2️⃣ 配置转发Bot（2分钟）</p>
          <p style="margin: 8px 0;">3️⃣ 设置频道映射（2分钟）</p>
          <p style="margin: 10px 0; color: #67C23A;"><strong>总耗时：约5分钟</strong></p>
        </div>
        
        <div style="color: #909399; font-size: 13px; margin-top: 15px;">
          💡 配置过程随时可以保存，下次继续
        </div>
      </div>
    `, '首次启动向导', {
      confirmButtonText: '开始配置 →',
      cancelButtonText: '稍后配置',
      type: 'success',
      dangerouslyUseHTMLString: true,
      distinguishCancelAndClose: true,
      closeOnClickModal: false,
      closeOnPressEscape: false
    })
    
    // 用户点击"开始配置"，跳转到3步向导
    router.push('/wizard/quick-3-steps')
    
  } catch (action) {
    if (action === 'cancel') {
      // 用户点击"稍后配置"
      ElNotification({
        title: '提示',
        message: '您可以随时从菜单进入配置向导',
        type: 'info',
        duration: 3000
      })
    }
  }
}

/**
 * 检查配置完整性
 */
const checkConfigCompleteness = async () => {
  try {
    const response = await api.get('/api/wizard/check-config-completeness')
    
    if (!response.data.complete) {
      // 配置不完整，显示提醒
      const missing = response.data.missing_items
      const completeness = response.data.completeness
      
      ElNotification({
        title: '配置未完成',
        message: `当前配置完成度：${completeness}%\n还有 ${missing.length} 项配置需要完成`,
        type: 'warning',
        duration: 0,  // 不自动关闭
        position: 'bottom-right',
        onClick: () => {
          // 点击通知，跳转到配置页面
          if (missing.length > 0) {
            const firstMissing = missing[0]
            router.push(firstMissing.action_url || '/wizard')
          }
        }
      })
    }
  } catch (error) {
    console.error('检查配置完整性失败:', error)
  }
}
</script>

<style scoped>
/* 隐藏组件，仅用于逻辑 */
</style>
