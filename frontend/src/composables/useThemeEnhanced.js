/**
 * 主题管理 Composable（增强版）
 * P3-6: 主题切换动画
 * 
 * 功能：
 * - 浅色/深色/自动三种模式
 * - 平滑切换动画
 * - 持久化保存
 * - 系统主题跟随
 */
import { ref, watch, onMounted } from 'vue'

const THEME_KEY = 'app-theme'
const THEME_MODE_KEY = 'theme-mode'

export function useThemeEnhanced() {
  // 主题模式：light / dark / auto
  const themeMode = ref('light')
  
  // 当前实际主题：light / dark
  const currentTheme = ref('light')
  
  // 是否正在切换
  const switching = ref(false)
  
  /**
   * 设置主题
   */
  const setTheme = (theme) => {
    if (switching.value) return
    
    switching.value = true
    currentTheme.value = theme
    
    // 应用主题
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
    
    // 保存到 localStorage
    localStorage.setItem(THEME_KEY, theme)
    
    // 切换动画完成后重置状态
    setTimeout(() => {
      switching.value = false
    }, 300)
  }
  
  /**
   * 设置主题模式
   */
  const setThemeMode = (mode) => {
    themeMode.value = mode
    localStorage.setItem(THEME_MODE_KEY, mode)
    
    if (mode === 'auto') {
      // 自动模式：跟随系统
      applySystemTheme()
    } else {
      // 手动模式：应用指定主题
      setTheme(mode)
    }
  }
  
  /**
   * 应用系统主题
   */
  const applySystemTheme = () => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(prefersDark ? 'dark' : 'light')
  }
  
  /**
   * 切换主题
   */
  const toggleTheme = () => {
    const newTheme = currentTheme.value === 'light' ? 'dark' : 'light'
    
    if (themeMode.value === 'auto') {
      // 如果是自动模式，切换到手动模式
      setThemeMode(newTheme)
    } else {
      // 手动模式，直接切换
      setTheme(newTheme)
      setThemeMode(newTheme)
    }
  }
  
  /**
   * 监听系统主题变化
   */
  const watchSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    mediaQuery.addEventListener('change', (e) => {
      if (themeMode.value === 'auto') {
        setTheme(e.matches ? 'dark' : 'light')
      }
    })
  }
  
  /**
   * 初始化主题
   */
  const initTheme = () => {
    // 从 localStorage 加载主题模式
    const savedMode = localStorage.getItem(THEME_MODE_KEY) || 'light'
    const savedTheme = localStorage.getItem(THEME_KEY) || 'light'
    
    themeMode.value = savedMode
    
    if (savedMode === 'auto') {
      applySystemTheme()
    } else {
      setTheme(savedTheme)
    }
    
    // 监听系统主题变化
    watchSystemTheme()
  }
  
  // 生命周期
  onMounted(() => {
    initTheme()
  })
  
  return {
    themeMode,
    currentTheme,
    switching,
    setTheme,
    setThemeMode,
    toggleTheme
  }
}


/**
 * ECharts 主题配置
 */
export function getEChartsTheme(theme) {
  if (theme === 'dark') {
    return {
      backgroundColor: '#1e1e1e',
      textStyle: {
        color: '#e8e8e8'
      },
      title: {
        textStyle: {
          color: '#e8e8e8'
        }
      },
      legend: {
        textStyle: {
          color: '#c8c8c8'
        }
      },
      axisLine: {
        lineStyle: {
          color: '#3a3a3a'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#2a2a2a'
        }
      }
    }
  } else {
    return {
      backgroundColor: '#ffffff',
      textStyle: {
        color: '#303133'
      },
      title: {
        textStyle: {
          color: '#303133'
        }
      },
      legend: {
        textStyle: {
          color: '#606266'
        }
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#ebeef5'
        }
      }
    }
  }
}
