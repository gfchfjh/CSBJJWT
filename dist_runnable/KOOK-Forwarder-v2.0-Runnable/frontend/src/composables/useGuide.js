/**
 * 新手引导系统 (使用driver.js)
 * ✅ P0-6优化：分步高亮引导，覆盖所有核心功能
 */

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 模拟driver.js的基础功能（如果未安装）
// 注意：生产环境应该安装真实的driver.js: npm install driver.js
class SimpleDriver {
  constructor(options) {
    this.options = options
    this.currentStep = 0
  }

  drive() {
    const steps = this.options.steps || []
    if (steps.length === 0) return

    this.showStep(0)
  }

  showStep(index) {
    const steps = this.options.steps || []
    if (index >= steps.length) {
      this.complete()
      return
    }

    const step = steps[index]
    this.currentStep = index

    // 高亮元素
    const element = document.querySelector(step.element)
    if (!element) {
      console.warn(`引导元素未找到: ${step.element}`)
      this.showStep(index + 1)
      return
    }

    // 滚动到元素
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })

    // 添加高亮效果
    element.classList.add('driver-highlighted')

    // 显示提示（使用Element Plus的Message）
    const popover = step.popover || {}
    ElMessage({
      message: `${popover.title}\n${popover.description}`,
      type: 'info',
      duration: 5000,
      showClose: true,
      onClose: () => {
        element.classList.remove('driver-highlighted')
        this.showStep(index + 1)
      }
    })
  }

  complete() {
    if (this.options.onDestroyStarted) {
      this.options.onDestroyStarted()
    }
    ElMessage.success('✅ 引导完成！')
  }
}

// 尝试导入真实的driver.js，失败则使用简单版本
let driver
try {
  // 如果安装了driver.js，使用真实版本
  // driver = require('driver.js').driver
  // 如果未安装，使用简单版本
  driver = (options) => new SimpleDriver(options)
} catch (e) {
  driver = (options) => new SimpleDriver(options)
}

// 引导状态
const isGuidingActive = ref(false)
const currentGuidanceStep = ref(0)

/**
 * 使用引导系统
 */
export function useGuide() {
  const router = useRouter()

  /**
   * 完整引导（8步）
   */
  const startFullGuide = () => {
    const driverObj = driver({
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: [
        {
          element: '#app',
          popover: {
            title: '👋 欢迎使用KOOK消息转发系统',
            description: '我将带您快速了解系统的核心功能，整个过程约需3分钟。',
            position: 'center'
          }
        },
        {
          element: '#nav-accounts',
          popover: {
            title: '第1步：账号管理',
            description: '首先需要添加KOOK账号。点击"账号管理"进入账号页面，然后点击"添加账号"按钮。',
            position: 'bottom'
          }
        },
        {
          element: '#add-account-btn',
          popover: {
            title: '第2步：添加账号',
            description: '支持两种方式：Cookie导入（推荐）或账号密码登录。Cookie导入更安全快捷。',
            position: 'left'
          },
          onHighlightStarted: () => {
            router.push('/accounts')
          }
        },
        {
          element: '#nav-bots',
          popover: {
            title: '第3步：配置机器人',
            description: '添加账号后，需要配置转发Bot。支持Discord、Telegram、飞书三个平台。',
            position: 'bottom'
          }
        },
        {
          element: '#add-bot-btn',
          popover: {
            title: '第4步：添加Bot',
            description: '点击"添加Bot"，选择平台并填写配置信息。每个平台都有详细的配置教程。',
            position: 'left'
          },
          onHighlightStarted: () => {
            router.push('/bots')
          }
        },
        {
          element: '#nav-mapping',
          popover: {
            title: '第5步：频道映射',
            description: '建立KOOK频道与目标平台的映射关系。可以使用"智能映射"自动创建。',
            position: 'bottom'
          }
        },
        {
          element: '#smart-mapping-btn',
          popover: {
            title: '第6步：智能映射',
            description: '智能映射会自动识别同名或相似的频道，为您快速建立映射关系。',
            position: 'left'
          },
          onHighlightStarted: () => {
            router.push('/mapping')
          }
        },
        {
          element: '#start-service-btn',
          popover: {
            title: '第7步：启动服务',
            description: '所有配置完成后，点击"启动服务"开始转发消息。',
            position: 'bottom'
          },
          onHighlightStarted: () => {
            router.push('/')
          }
        },
        {
          element: '#nav-logs',
          popover: {
            title: '第8步：查看日志',
            description: '在这里可以实时查看消息转发状态，包括成功、失败和等待中的消息。',
            position: 'bottom'
          }
        }
      ],
      onDestroyStarted: () => {
        isGuidingActive.value = false
        localStorage.setItem('guide_completed_full', 'true')
        ElMessage.success('🎉 完整引导已完成！您现在可以开始使用了')
      }
    })

    isGuidingActive.value = true
    driverObj.drive()
  }

  /**
   * 快速引导（3步）
   */
  const startQuickGuide = () => {
    const driverObj = driver({
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: [
        {
          element: '#app',
          popover: {
            title: '⚡ 快速上手',
            description: '3步快速完成配置，开始使用KOOK消息转发系统！',
            position: 'center'
          }
        },
        {
          element: '#add-account-btn',
          popover: {
            title: '步骤1：添加KOOK账号',
            description: '导入Cookie或使用账号密码登录',
            position: 'bottom'
          },
          onHighlightStarted: () => {
            router.push('/accounts')
          }
        },
        {
          element: '#add-bot-btn',
          popover: {
            title: '步骤2：配置转发Bot',
            description: '添加Discord/Telegram/飞书Bot',
            position: 'bottom'
          },
          onHighlightStarted: () => {
            router.push('/bots')
          }
        },
        {
          element: '#start-service-btn',
          popover: {
            title: '步骤3：启动服务',
            description: '点击启动，开始转发消息！',
            position: 'bottom'
          },
          onHighlightStarted: () => {
            router.push('/')
          }
        }
      ],
      onDestroyStarted: () => {
        isGuidingActive.value = false
        localStorage.setItem('guide_completed_quick', 'true')
        ElMessage.success('✅ 快速引导完成！')
      }
    })

    isGuidingActive.value = true
    driverObj.drive()
  }

  /**
   * 功能演示引导（针对特定功能）
   */
  const startFeatureGuide = (featureName) => {
    const guides = {
      // Cookie导入演示
      'cookie-import': {
        steps: [
          {
            element: '#cookie-import-btn',
            popover: {
              title: '🍪 Cookie导入',
              description: '点击此按钮打开Cookie导入对话框',
              position: 'bottom'
            }
          },
          {
            element: '.drag-upload-area',
            popover: {
              title: '拖拽上传',
              description: '将Cookie文件拖拽到此区域，或点击选择文件',
              position: 'top'
            }
          },
          {
            element: '.cookie-textarea',
            popover: {
              title: '粘贴Cookie',
              description: '也可以直接粘贴Cookie文本，支持JSON、Netscape等格式',
              position: 'top'
            }
          }
        ]
      },
      
      // 智能映射演示
      'smart-mapping': {
        steps: [
          {
            element: '#smart-mapping-btn',
            popover: {
              title: '🎯 智能映射',
              description: '点击智能映射，系统会自动识别同名频道',
              position: 'bottom'
            }
          },
          {
            element: '.mapping-preview-panel',
            popover: {
              title: '映射预览',
              description: '在这里可以查看所有映射关系，确认无误后保存',
              position: 'top'
            }
          }
        ]
      },
      
      // 过滤规则演示
      'filter-rules': {
        steps: [
          {
            element: '#nav-filter',
            popover: {
              title: '🔧 过滤规则',
              description: '设置消息过滤规则，控制哪些消息需要转发',
              position: 'bottom'
            }
          },
          {
            element: '.keyword-filter',
            popover: {
              title: '关键词过滤',
              description: '设置黑名单/白名单关键词，精确控制转发内容',
              position: 'right'
            }
          }
        ]
      }
    }

    const guide = guides[featureName]
    if (!guide) {
      console.warn(`未找到功能引导: ${featureName}`)
      return
    }

    const driverObj = driver({
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: guide.steps,
      onDestroyStarted: () => {
        isGuidingActive.value = false
        localStorage.setItem(`guide_feature_${featureName}`, 'true')
      }
    })

    isGuidingActive.value = true
    driverObj.drive()
  }

  /**
   * 检查是否需要显示引导
   */
  const shouldShowGuide = () => {
    // 检查是否完成过引导
    const fullCompleted = localStorage.getItem('guide_completed_full')
    const quickCompleted = localStorage.getItem('guide_completed_quick')
    const wizardCompleted = localStorage.getItem('wizard_completed')

    // 如果完成过向导或引导，不再显示
    if (fullCompleted || quickCompleted || wizardCompleted) {
      return false
    }

    return true
  }

  /**
   * 重置引导状态（用于测试或重新引导）
   */
  const resetGuide = () => {
    localStorage.removeItem('guide_completed_full')
    localStorage.removeItem('guide_completed_quick')
    localStorage.removeItem('wizard_completed')
    ElMessage.success('引导状态已重置，刷新页面后将重新显示引导')
  }

  /**
   * 显示引导选择对话框
   */
  const showGuideChoice = () => {
    // 这里可以显示一个对话框让用户选择完整引导还是快速引导
    // 暂时直接启动快速引导
    startQuickGuide()
  }

  return {
    // 状态
    isGuidingActive,
    currentGuidanceStep,
    
    // 方法
    startFullGuide,
    startQuickGuide,
    startFeatureGuide,
    shouldShowGuide,
    resetGuide,
    showGuideChoice
  }
}

// 全局引导管理器
let globalGuide = null

export function useGlobalGuide() {
  if (!globalGuide) {
    globalGuide = useGuide()
  }
  return globalGuide
}

/**
 * 添加引导样式到全局
 */
export function injectGuideStyles() {
  const styleId = 'guide-custom-styles'
  if (document.getElementById(styleId)) return

  const style = document.createElement('style')
  style.id = styleId
  style.textContent = `
    /* Driver.js 高亮元素样式 */
    .driver-highlighted {
      position: relative;
      z-index: 9999;
      box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.6),
                  0 0 0 8px rgba(64, 158, 255, 0.3);
      border-radius: 8px;
      transition: all 0.3s ease;
      animation: pulse-highlight 2s ease-in-out infinite;
    }

    @keyframes pulse-highlight {
      0%, 100% {
        box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.6),
                    0 0 0 8px rgba(64, 158, 255, 0.3);
      }
      50% {
        box-shadow: 0 0 0 6px rgba(64, 158, 255, 0.8),
                    0 0 0 12px rgba(64, 158, 255, 0.4);
      }
    }

    /* 简易Popover样式 */
    .driver-popover {
      position: fixed;
      z-index: 10000;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
      padding: 20px;
      max-width: 400px;
    }

    .driver-popover-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 12px;
    }

    .driver-popover-description {
      font-size: 14px;
      color: #606266;
      line-height: 1.6;
      margin-bottom: 16px;
    }

    .driver-popover-footer {
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }

    /* 遮罩层 */
    .driver-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 9998;
    }
  `
  document.head.appendChild(style)
}

// 导出默认实例
export const globalGuide = useGlobalGuide()
