/**
 * 新手引导系统 - Composable
 * ✅ P0-11: 使用driver.js实现交互式引导
 */
import { ref, computed } from 'vue'
import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'

// 引导进度状态
const onboardingState = ref({
  completed: false,
  currentStep: 0,
  skipped: false,
  timestamp: null
})

// 从localStorage加载状态
const STORAGE_KEY = 'kook_forwarder_onboarding_state'

function loadOnboardingState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      onboardingState.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('加载引导状态失败:', error)
  }
}

function saveOnboardingState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(onboardingState.value))
  } catch (error) {
    console.error('保存引导状态失败:', error)
  }
}

// 初始化
loadOnboardingState()

/**
 * 新手引导Hook
 */
export function useOnboarding() {
  const driverObj = ref(null)
  
  // 是否需要显示引导
  const needsOnboarding = computed(() => {
    return !onboardingState.value.completed && !onboardingState.value.skipped
  })
  
  /**
   * 启动完整引导流程
   */
  function startFullTour() {
    const steps = [
      // 欢迎步骤
      {
        element: '#app',
        popover: {
          title: '👋 欢迎使用KOOK消息转发系统',
          description: '让我们用2分钟时间了解系统的核心功能。您可以随时按ESC键跳过引导。',
          side: 'left',
          align: 'start'
        }
      },
      
      // 配置向导
      {
        element: '#wizard-container',
        popover: {
          title: '🎯 配置向导',
          description: '首次使用？点击这里启动3步配置向导，快速完成基础设置。',
          side: 'bottom',
          align: 'start'
        }
      },
      
      // 账号管理
      {
        element: '#accounts-menu',
        popover: {
          title: '👤 账号管理',
          description: '在这里添加和管理KOOK账号。支持Cookie导入和密码登录两种方式。',
          side: 'right',
          align: 'start'
        }
      },
      
      // Bot配置
      {
        element: '#bots-menu',
        popover: {
          title: '🤖 Bot配置',
          description: '配置Discord、Telegram、飞书的Bot。我们提供详细的图文教程。',
          side: 'right',
          align: 'start'
        }
      },
      
      // 频道映射
      {
        element: '#mapping-menu',
        popover: {
          title: '🔀 频道映射',
          description: '这是核心功能！使用可视化编辑器建立KOOK频道和目标平台的映射关系。',
          side: 'right',
          align: 'start'
        }
      },
      
      // 过滤规则
      {
        element: '#filter-menu',
        popover: {
          title: '🔧 过滤规则',
          description: '设置关键词过滤、用户黑白名单等，精确控制转发内容。',
          side: 'right',
          align: 'start'
        }
      },
      
      // 实时监控
      {
        element: '#logs-menu',
        popover: {
          title: '📋 实时监控',
          description: '查看转发日志、统计信息和系统状态。支持实时刷新。',
          side: 'right',
          align: 'start'
        }
      },
      
      // 系统设置
      {
        element: '#settings-menu',
        popover: {
          title: '⚙️ 系统设置',
          description: '调整图片处理策略、日志保留时长等高级设置。',
          side: 'right',
          align: 'start'
        }
      },
      
      // 启动按钮
      {
        element: '#start-service-btn',
        popover: {
          title: '🚀 启动服务',
          description: '完成配置后，点击这个按钮启动消息转发服务。',
          side: 'bottom',
          align: 'center'
        }
      },
      
      // 完成
      {
        element: '#app',
        popover: {
          title: '🎉 引导完成！',
          description: '您已经了解了所有核心功能。现在可以开始配置您的转发系统了。需要帮助？点击右上角的帮助按钮查看详细文档。',
          side: 'left',
          align: 'start'
        }
      }
    ]
    
    driverObj.value = driver({
      showProgress: true,
      progressText: '第 {{current}} 步，共 {{total}} 步',
      nextBtnText: '下一步',
      prevBtnText: '上一步',
      doneBtnText: '完成',
      closeBtnText: '关闭',
      showButtons: ['next', 'previous', 'close'],
      steps,
      onDestroyStarted: () => {
        // 引导被关闭
        if (driverObj.value.getActiveIndex() === steps.length - 1) {
          // 完成引导
          markOnboardingCompleted()
        } else {
          // 中途退出
          saveCurrentProgress()
        }
      },
      onNextClick: (element, step, options) => {
        // 更新进度
        onboardingState.value.currentStep = options.state.activeIndex + 1
        saveOnboardingState()
        
        driverObj.value.moveNext()
      },
      onPrevClick: () => {
        onboardingState.value.currentStep = Math.max(0, onboardingState.value.currentStep - 1)
        saveOnboardingState()
        
        driverObj.value.movePrevious()
      }
    })
    
    driverObj.value.drive()
  }
  
  /**
   * 启动特定模块的引导
   */
  function startModuleTour(moduleName) {
    const moduleSteps = {
      // 账号管理引导
      accounts: [
        {
          element: '#add-account-btn',
          popover: {
            title: '添加KOOK账号',
            description: '点击这里添加新的KOOK账号',
            side: 'bottom'
          }
        },
        {
          element: '#account-list',
          popover: {
            title: '账号列表',
            description: '已添加的账号会显示在这里，包括在线状态和最后活跃时间',
            side: 'right'
          }
        }
      ],
      
      // 频道映射引导
      mapping: [
        {
          element: '#mapping-canvas',
          popover: {
            title: '可视化编辑器',
            description: '在这个画布上拖拽节点来建立映射关系',
            side: 'bottom'
          }
        },
        {
          element: '#smart-mapping-btn',
          popover: {
            title: '智能映射',
            description: '点击这里自动匹配相似的频道名称',
            side: 'left'
          }
        },
        {
          element: '#save-mapping-btn',
          popover: {
            title: '保存映射',
            description: '完成编辑后记得保存',
            side: 'left'
          }
        }
      ],
      
      // Bot配置引导
      bots: [
        {
          element: '#add-bot-btn',
          popover: {
            title: '添加Bot',
            description: '支持Discord、Telegram、飞书三种平台',
            side: 'bottom'
          }
        },
        {
          element: '#bot-tutorial-btn',
          popover: {
            title: '查看教程',
            description: '不知道如何创建Bot？点击查看详细教程',
            side: 'left'
          }
        }
      ]
    }
    
    const steps = moduleSteps[moduleName]
    
    if (!steps) {
      console.warn(`未找到模块引导: ${moduleName}`)
      return
    }
    
    driverObj.value = driver({
      showProgress: true,
      progressText: '第 {{current}} 步，共 {{total}} 步',
      nextBtnText: '下一步',
      prevBtnText: '上一步',
      doneBtnText: '完成',
      closeBtnText: '关闭',
      steps
    })
    
    driverObj.value.drive()
  }
  
  /**
   * 高亮单个元素
   */
  function highlightElement(selector, options = {}) {
    const defaultOptions = {
      element: selector,
      popover: {
        title: options.title || '提示',
        description: options.description || '',
        side: options.side || 'bottom',
        align: options.align || 'start'
      }
    }
    
    driverObj.value = driver({
      showProgress: false,
      showButtons: ['close'],
      closeBtnText: '知道了',
      steps: [defaultOptions]
    })
    
    driverObj.value.drive()
  }
  
  /**
   * 标记引导完成
   */
  function markOnboardingCompleted() {
    onboardingState.value.completed = true
    onboardingState.value.timestamp = Date.now()
    saveOnboardingState()
  }
  
  /**
   * 跳过引导
   */
  function skipOnboarding() {
    onboardingState.value.skipped = true
    onboardingState.value.timestamp = Date.now()
    saveOnboardingState()
    
    if (driverObj.value) {
      driverObj.value.destroy()
    }
  }
  
  /**
   * 重置引导状态
   */
  function resetOnboarding() {
    onboardingState.value = {
      completed: false,
      currentStep: 0,
      skipped: false,
      timestamp: null
    }
    saveOnboardingState()
  }
  
  /**
   * 保存当前进度
   */
  function saveCurrentProgress() {
    saveOnboardingState()
  }
  
  /**
   * 从当前进度继续
   */
  function continueFromProgress() {
    if (driverObj.value && onboardingState.value.currentStep > 0) {
      driverObj.value.drive(onboardingState.value.currentStep)
    } else {
      startFullTour()
    }
  }
  
  return {
    // 状态
    needsOnboarding,
    onboardingState,
    
    // 方法
    startFullTour,
    startModuleTour,
    highlightElement,
    markOnboardingCompleted,
    skipOnboarding,
    resetOnboarding,
    continueFromProgress
  }
}

/**
 * 自动触发引导
 */
export function autoStartOnboarding() {
  const { needsOnboarding, startFullTour } = useOnboarding()
  
  if (needsOnboarding.value) {
    // 延迟1秒启动，给页面渲染时间
    setTimeout(() => {
      startFullTour()
    }, 1000)
  }
}
