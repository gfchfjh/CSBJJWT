/**
 * ✅ P2-2新增：国际化配置模块
 * 支持简体中文和英文
 */
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import enUS from './en-US.json'

// 从本地存储获取语言设置，默认中文
const getDefaultLocale = () => {
  const saved = localStorage.getItem('locale')
  if (saved) return saved
  
  // 检测浏览器语言
  const browserLang = navigator.language || navigator.userLanguage
  if (browserLang.startsWith('zh')) return 'zh-CN'
  return 'en-US'
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: getDefaultLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  },
  // 自定义数字和日期格式化
  numberFormats: {
    'zh-CN': {
      currency: {
        style: 'currency',
        currency: 'CNY'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percent: {
        style: 'percent',
        minimumFractionDigits: 1
      }
    },
    'en-US': {
      currency: {
        style: 'currency',
        currency: 'USD'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percent: {
        style: 'percent',
        minimumFractionDigits: 1
      }
    }
  },
  datetimeFormats: {
    'zh-CN': {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      },
      long: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      },
      time: {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }
    },
    'en-US': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      },
      time: {
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      }
    }
  }
})

/**
 * 切换语言
 * @param {string} locale - 'zh-CN' | 'en-US'
 */
export const setLocale = (locale) => {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  
  // 更新HTML lang属性
  document.querySelector('html').setAttribute('lang', locale)
  
  // 更新Element Plus语言
  if (window.__ELEMENT_PLUS__) {
    const ElLocale = locale === 'zh-CN' 
      ? window.__ELEMENT_PLUS__.zhCn 
      : window.__ELEMENT_PLUS__.en
    window.__ELEMENT_PLUS__.locale(ElLocale)
  }
}

/**
 * 获取当前语言
 */
export const getLocale = () => {
  return i18n.global.locale.value
}

/**
 * 翻译函数（可在非Vue组件中使用）
 * @param {string} key - 翻译键
 * @param {object} params - 参数
 */
export const t = (key, params) => {
  return i18n.global.t(key, params)
}

export default i18n
