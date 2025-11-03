/**
 * 主题切换系统
 * �?P1-6: 亮色/暗色主题切换
 */
import { ref, watch } from 'vue'

// 主题类型
export const ThemeType = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
}

// 当前主题
const currentTheme = ref(localStorage.getItem('theme') || ThemeType.LIGHT)

// 系统主题
const systemTheme = ref(
  window.matchMedia('(prefers-color-scheme: dark)').matches 
    ? ThemeType.DARK 
    : ThemeType.LIGHT
)

// 实际使用的主�?
const activeTheme = ref(getActiveTheme())

/**
 * 获取实际使用的主�?
 */
function getActiveTheme() {
  if (currentTheme.value === ThemeType.AUTO) {
    return systemTheme.value
  }
  return currentTheme.value
}

/**
 * 应用主题
 */
function applyTheme(theme) {
  // �Ƴ�����������
  document.documentElement.classList.remove('light', 'dark', 'light-theme', 'dark-theme')
  
  // ���Ӷ�Ӧ�����ࣨƥ�� CSS ѡ������
  if (theme === ThemeType.DARK) {
    document.documentElement.classList.add('dark')  // CSS �õ��� html.dark
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.classList.add('light')
    document.documentElement.setAttribute('data-theme', 'light')
  }
  
  activeTheme.value = theme
}
/**
 * 主题切换组合式函�?
 */
export function useTheme() {
  /**
   * 设置主题
   */
  function setTheme(theme) {
    if (!Object.values(ThemeType).includes(theme)) {
      console.error('Invalid theme type:', theme)
      return
    }
    
    currentTheme.value = theme
    localStorage.setItem('theme', theme)
    
    // 更新实际主题
    const newActiveTheme = getActiveTheme()
    applyTheme(newActiveTheme)
  }
  
  /**
   * 切换主题
   */
  function toggleTheme() {
    if (activeTheme.value === ThemeType.LIGHT) {
      setTheme(ThemeType.DARK)
    } else {
      setTheme(ThemeType.LIGHT)
    }
  }
  
  /**
   * 监听系统主题变化
   */
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    systemTheme.value = e.matches ? ThemeType.DARK : ThemeType.LIGHT
    
    // 如果当前是自动模式，更新主题
    if (currentTheme.value === ThemeType.AUTO) {
      applyTheme(systemTheme.value)
    }
  })
  
  // 监听currentTheme变化
  watch(currentTheme, () => {
    const newActiveTheme = getActiveTheme()
    applyTheme(newActiveTheme)
  })
  
  // 初始应用主题
  applyTheme(activeTheme.value)
  
  return {
    currentTheme,
    activeTheme,
    systemTheme,
    setTheme,
    toggleTheme,
    ThemeType
  }
}

/**
 * 初始化主题（仅在应用启动时调用一次）
 */
export function initThemeOnce() {
  // 应用初始主题
  applyTheme(activeTheme.value)
}

// 主题颜色配置
export const themeColors = {
  light: {
    primary: '#409EFF',
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399',
    background: '#FFFFFF',
    backgroundSecondary: '#F5F7FA',
    text: '#303133',
    textSecondary: '#606266',
    border: '#DCDFE6'
  },
  dark: {
    primary: '#409EFF',
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399',
    background: '#1F1F1F',
    backgroundSecondary: '#2A2A2A',
    text: '#E5E5E5',
    textSecondary: '#A8A8A8',
    border: '#4C4C4C'
  }
}
