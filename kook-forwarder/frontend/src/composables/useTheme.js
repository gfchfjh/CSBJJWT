/**
 * 主题管理Composable
 */
import { ref, watch, onMounted } from 'vue'

// 主题类型
export const THEME_LIGHT = 'light'
export const THEME_DARK = 'dark'
export const THEME_AUTO = 'auto'

// 当前主题（响应式）
const currentTheme = ref(THEME_LIGHT)
const isDark = ref(false)

/**
 * 使用主题
 * @returns {Object} 主题相关的状态和方法
 */
export function useTheme() {
  /**
   * 应用主题
   * @param {string} theme - 主题类型
   */
  const applyTheme = (theme) => {
    let actualTheme = theme
    
    // 如果是自动模式，检测系统主题
    if (theme === THEME_AUTO) {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? THEME_DARK
        : THEME_LIGHT
    }
    
    // 更新状态
    isDark.value = actualTheme === THEME_DARK
    
    // 应用到HTML
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      document.documentElement.setAttribute('data-theme', 'light')
    }
  }
  
  /**
   * 切换主题
   * @param {string} theme - 主题类型
   */
  const setTheme = (theme) => {
    currentTheme.value = theme
    applyTheme(theme)
    
    // 保存到本地存储
    localStorage.setItem('app_theme', theme)
  }
  
  /**
   * 切换深色/浅色
   */
  const toggleTheme = () => {
    const newTheme = currentTheme.value === THEME_DARK ? THEME_LIGHT : THEME_DARK
    setTheme(newTheme)
  }
  
  /**
   * 初始化主题
   */
  const initTheme = () => {
    // 从本地存储读取
    const savedTheme = localStorage.getItem('app_theme') || THEME_LIGHT
    currentTheme.value = savedTheme
    applyTheme(savedTheme)
    
    // 监听系统主题变化（自动模式）
    if (savedTheme === THEME_AUTO) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', (e) => {
        if (currentTheme.value === THEME_AUTO) {
          applyTheme(THEME_AUTO)
        }
      })
    }
  }
  
  // 监听主题变化
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })
  
  return {
    currentTheme,
    isDark,
    setTheme,
    toggleTheme,
    initTheme,
    THEME_LIGHT,
    THEME_DARK,
    THEME_AUTO
  }
}

// 在应用启动时初始化
let initialized = false

export function initThemeOnce() {
  if (!initialized) {
    const { initTheme } = useTheme()
    initTheme()
    initialized = true
  }
}
