/**
 * 新手引导配置
 * 使用 driver.js 实现分步高亮引导
 */

import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'
import { ElMessage } from 'element-plus'

/**
 * 完整引导配置（8步）
 */
export const fullOnboardingSteps = [
  {
    element: '.app-header',
    popover: {
      title: '👋 欢迎使用KOOK消息转发系统！',
      description: '这是一个简单的引导教程，帮助您快速上手。预计耗时：2分钟',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '.sidebar-accounts',
    popover: {
      title: '📧 第1步：添加KOOK账号',
      description: '点击这里进入账号管理页，添加您的KOOK账号。支持Cookie导入或账号密码登录。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-bots',
    popover: {
      title: '🤖 第2步：配置转发机器人',
      description: '配置Discord、Telegram或飞书的Bot，用于接收转发的消息。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-mapping',
    popover: {
      title: '🔀 第3步：设置频道映射',
      description: '将KOOK频道映射到目标平台频道，建立转发关系。支持拖拽操作！',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-logs',
    popover: {
      title: '📋 第4步：查看转发日志',
      description: '实时监控消息转发状态，查看成功率和错误信息。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-settings',
    popover: {
      title: '⚙️ 第5步：系统设置',
      description: '配置图片处理策略、限流保护、自动清理等高级功能。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-help',
    popover: {
      title: '❓ 第6步：获取帮助',
      description: '遇到问题？查看详细教程、视频演示和常见问题解答。',
      side: 'right',
      align: 'start'
    }
  },
  {
    popover: {
      title: '🎉 引导完成！',
      description: '恭喜您已了解所有核心功能！现在开始配置您的第一个转发任务吧。\n\n💡 提示：您可以随时在帮助中心重新查看本引导。',
      side: 'center',
      align: 'center'
    }
  }
]

/**
 * 快速引导配置（3步核心流程）
 */
export const quickOnboardingSteps = [
  {
    popover: {
      title: '🚀 快速上手（3步完成）',
      description: '让我们用最快的速度配置您的转发系统！',
      side: 'center',
      align: 'center'
    }
  },
  {
    element: '.sidebar-accounts',
    popover: {
      title: '1️⃣ 添加KOOK账号',
      description: '首先添加您的KOOK账号，这是转发消息的源头。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-bots',
    popover: {
      title: '2️⃣ 配置转发Bot',
      description: '配置至少一个转发目标（Discord/Telegram/飞书）。',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '.sidebar-mapping',
    popover: {
      title: '3️⃣ 设置映射关系',
      description: '最后，建立KOOK频道到目标平台的映射。完成后即可开始转发！',
      side: 'right',
      align: 'start'
    }
  }
]

/**
 * 功能演示引导配置（针对特定功能）
 */
export const featureOnboardingSteps = {
  // 映射功能演示
  mapping: [
    {
      element: '.mapping-tabs',
      popover: {
        title: '🎨 频道映射有两种方式',
        description: '传统表格模式和可视化编辑器模式，您可以自由切换。',
        side: 'bottom',
        align: 'center'
      }
    },
    {
      element: '.visual-editor-tab',
      popover: {
        title: '✨ 推荐：可视化编辑器',
        description: '拖拽式操作，所见即所得，快速建立映射关系。',
        side: 'bottom',
        align: 'center'
      }
    },
    {
      element: '.kook-channels-panel',
      popover: {
        title: '📌 步骤1：选择KOOK频道',
        description: '从左侧选择要转发的KOOK频道。',
        side: 'right',
        align: 'start'
      }
    },
    {
      element: '.target-bots-panel',
      popover: {
        title: '🎯 步骤2：拖拽到目标',
        description: '将频道拖拽到右侧的Bot卡片上，即可建立映射。',
        side: 'left',
        align: 'start'
      }
    }
  ],
  
  // Cookie导入演示
  cookieImport: [
    {
      element: '.cookie-import-methods',
      popover: {
        title: '📋 Cookie导入有3种方式',
        description: '文件上传、直接粘贴、浏览器扩展，选择最方便的方式。',
        side: 'bottom',
        align: 'center'
      }
    },
    {
      element: '.drag-drop-area',
      popover: {
        title: '🎯 推荐：拖拽上传',
        description: '将Cookie JSON文件直接拖到这里，最快捷！',
        side: 'top',
        align: 'center'
      }
    }
  ]
}

/**
 * 创建引导实例
 */
export function createOnboarding(type = 'full', options = {}) {
  const steps = type === 'quick' ? quickOnboardingSteps : fullOnboardingSteps
  
  const driverObj = driver({
    showProgress: true,
    steps: steps,
    nextBtnText: '下一步 →',
    prevBtnText: '← 上一步',
    doneBtnText: '完成 ✓',
    progressText: '{{current}} / {{total}}',
    onDestroyStarted: () => {
      if (driverObj.hasNextStep() || confirm('确定要退出引导吗？')) {
        driverObj.destroy()
      }
    },
    onDestroyed: () => {
      // 标记引导已完成
      localStorage.setItem(`onboarding_${type}_completed`, 'true')
      localStorage.setItem(`onboarding_${type}_completed_at`, new Date().toISOString())
      
      ElMessage.success('引导完成！您可以随时在帮助中心重新查看。')
    },
    ...options
  })
  
  return driverObj
}

/**
 * 创建功能演示引导
 */
export function createFeatureOnboarding(feature, options = {}) {
  const steps = featureOnboardingSteps[feature]
  
  if (!steps) {
    console.warn(`未找到功能 "${feature}" 的引导配置`)
    return null
  }
  
  const driverObj = driver({
    showProgress: true,
    steps: steps,
    nextBtnText: '下一步 →',
    prevBtnText: '← 上一步',
    doneBtnText: '我知道了 ✓',
    progressText: '{{current}} / {{total}}',
    ...options
  })
  
  return driverObj
}

/**
 * 检查是否需要显示引导
 */
export function shouldShowOnboarding(type = 'full') {
  const completed = localStorage.getItem(`onboarding_${type}_completed`)
  return !completed
}

/**
 * 重置引导状态（用于"重新开始引导"功能）
 */
export function resetOnboarding(type = 'full') {
  localStorage.removeItem(`onboarding_${type}_completed`)
  localStorage.removeItem(`onboarding_${type}_completed_at`)
  ElMessage.info('引导状态已重置')
}

/**
 * 获取引导完成信息
 */
export function getOnboardingInfo(type = 'full') {
  const completed = localStorage.getItem(`onboarding_${type}_completed`)
  const completedAt = localStorage.getItem(`onboarding_${type}_completed_at`)
  
  return {
    completed: completed === 'true',
    completedAt: completedAt ? new Date(completedAt) : null
  }
}

/**
 * 启动首次引导（在应用启动时调用）
 */
export function startFirstTimeOnboarding() {
  // 检查是否是首次启动
  const hasSeenAnyOnboarding = localStorage.getItem('onboarding_full_completed') || 
                                localStorage.getItem('onboarding_quick_completed')
  
  if (!hasSeenAnyOnboarding) {
    // 延迟1秒启动，确保页面已完全加载
    setTimeout(() => {
      // 询问用户选择哪种引导
      const useQuick = confirm(
        '检测到您是首次使用！\n\n' +
        '点击"确定"开始快速引导（3步，约1分钟）\n' +
        '点击"取消"开始完整引导（8步，约2分钟）\n\n' +
        '您也可以稍后在帮助中心重新查看引导。'
      )
      
      const onboarding = createOnboarding(useQuick ? 'quick' : 'full')
      onboarding.drive()
    }, 1000)
  }
}

export default {
  createOnboarding,
  createFeatureOnboarding,
  shouldShowOnboarding,
  resetOnboarding,
  getOnboardingInfo,
  startFirstTimeOnboarding,
  fullOnboardingSteps,
  quickOnboardingSteps,
  featureOnboardingSteps
}
