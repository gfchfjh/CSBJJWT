/**
 * 主题管理 Composable
 * 支持浅色/深色/跟随系统三种模式
 */
import { ref, watch, onMounted } from 'vue'

const THEME_KEY = 'kook-forwarder-theme'
const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
}

// 全局主题状态
const currentTheme = ref(THEME_MODES.AUTO)
const isDark = ref(false)

export function useTheme() {
  /**
   * 获取系统主题偏好
   */
  const getSystemTheme = () => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return THEME_MODES.DARK
    }
    return THEME_MODES.LIGHT
  }

  /**
   * 应用主题到页面
   */
  const applyTheme = (theme) => {
    const htmlElement = document.documentElement
    
    if (theme === THEME_MODES.DARK) {
      htmlElement.classList.add('dark')
      htmlElement.setAttribute('data-theme', 'dark')
      isDark.value = true
    } else {
      htmlElement.classList.remove('dark')
      htmlElement.setAttribute('data-theme', 'light')
      isDark.value = false
    }
  }

  /**
   * 设置主题
   */
  const setTheme = (theme) => {
    currentTheme.value = theme
    localStorage.setItem(THEME_KEY, theme)

    // 根据选择应用主题
    if (theme === THEME_MODES.AUTO) {
      const systemTheme = getSystemTheme()
      applyTheme(systemTheme)
    } else {
      applyTheme(theme)
    }
  }

  /**
   * 初始化主题
   */
  const initTheme = () => {
    // 从 localStorage 读取保存的主题
    const savedTheme = localStorage.getItem(THEME_KEY)
    
    if (savedTheme && Object.values(THEME_MODES).includes(savedTheme)) {
      setTheme(savedTheme)
    } else {
      // 默认跟随系统
      setTheme(THEME_MODES.AUTO)
    }

    // 监听系统主题变化
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      
      mediaQuery.addEventListener('change', (e) => {
        // 只在自动模式下响应系统主题变化
        if (currentTheme.value === THEME_MODES.AUTO) {
          applyTheme(e.matches ? THEME_MODES.DARK : THEME_MODES.LIGHT)
        }
      })
    }
  }

  /**
   * 切换主题（在浅色和深色之间切换）
   */
  const toggleTheme = () => {
    if (isDark.value) {
      setTheme(THEME_MODES.LIGHT)
    } else {
      setTheme(THEME_MODES.DARK)
    }
  }

  return {
    currentTheme,
    isDark,
    THEME_MODES,
    setTheme,
    toggleTheme,
    initTheme,
    getSystemTheme
  }
}

// 自动初始化主题（仅在首次导入时执行）
if (typeof window !== 'undefined') {
  const { initTheme } = useTheme()
  initTheme()
}
