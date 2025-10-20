/**
 * 国际化配置
 * 使用vue-i18n实现多语言支持
 */
import { createI18n } from 'vue-i18n'

// 导入语言包
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

// 从localStorage获取用户选择的语言，默认为简体中文
const savedLanguage = localStorage.getItem('app_language') || 'zh-CN'

const i18n = createI18n({
  locale: savedLanguage,  // 当前语言
  fallbackLocale: 'zh-CN',  // 回退语言
  legacy: false,  // 使用Composition API模式
  globalInjection: true,  // 全局注入$t函数
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

export default i18n

// 切换语言的辅助函数
export function setLanguage(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('app_language', locale)
  
  // 同步Element Plus语言
  // 注意：需要在main.js中处理Element Plus的语言切换
  
  return locale
}

// 获取当前语言
export function getCurrentLanguage() {
  return i18n.global.locale.value
}

// 获取所有支持的语言
export function getSupportedLanguages() {
  return [
    { value: 'zh-CN', label: '简体中文', icon: '🇨🇳' },
    { value: 'en-US', label: 'English', icon: '🇺🇸' }
  ]
}
