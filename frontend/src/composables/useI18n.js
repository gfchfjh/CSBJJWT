/**
 * ✅ P2-2新增：国际化组合函数
 * 提供在组件中使用国际化的便捷方法
 */
import { useI18n as vueUseI18n } from 'vue-i18n'
import { computed } from 'vue'

/**
 * 国际化组合函数
 * 
 * @example
 * ```js
 * const { t, locale, setLocale, localeLabel } = useI18n()
 * 
 * // 翻译
 * t('common.save')  // "保存" 或 "Save"
 * 
 * // 带参数翻译
 * t('accounts.deleteConfirm', { email: 'user@example.com' })
 * 
 * // 切换语言
 * setLocale('en-US')
 * 
 * // 获取当前语言标签
 * console.log(localeLabel.value)  // "简体中文" 或 "English"
 * ```
 */
export function useI18n() {
  const { t, locale, d, n } = vueUseI18n()

  /**
   * 切换语言
   * @param {string} newLocale - 'zh-CN' | 'en-US'
   */
  const setLocale = (newLocale) => {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
    document.querySelector('html')?.setAttribute('lang', newLocale)
  }

  /**
   * 当前语言的显示标签
   */
  const localeLabel = computed(() => {
    return locale.value === 'zh-CN' ? '简体中文' : 'English'
  })

  /**
   * 所有支持的语言选项
   */
  const localeOptions = [
    { value: 'zh-CN', label: '简体中文', flag: '🇨🇳' },
    { value: 'en-US', label: 'English', flag: '🇺🇸' }
  ]

  /**
   * 翻译消息类型（success/error/warning/info）
   * @param {string} type - 消息类型
   * @param {string} key - 消息键
   * @param {object} params - 参数
   */
  const tm = (type, key, params) => {
    return t(`messages.${type}.${key}`, params)
  }

  /**
   * 翻译验证消息
   * @param {string} key - 验证键
   * @param {object} params - 参数
   */
  const tv = (key, params) => {
    return t(`validation.${key}`, params)
  }

  /**
   * 格式化日期
   * @param {Date|string|number} date - 日期
   * @param {string} format - 格式类型 'short' | 'long' | 'time'
   */
  const formatDate = (date, format = 'long') => {
    if (!date) return '-'
    const dateObj = date instanceof Date ? date : new Date(date)
    return d(dateObj, format)
  }

  /**
   * 格式化数字
   * @param {number} number - 数字
   * @param {string} format - 格式类型 'decimal' | 'percent' | 'currency'
   */
  const formatNumber = (number, format = 'decimal') => {
    if (number === null || number === undefined) return '-'
    return n(number, format)
  }

  /**
   * 格式化字节大小
   * @param {number} bytes - 字节数
   */
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = locale.value === 'zh-CN'
      ? ['B', 'KB', 'MB', 'GB', 'TB']
      : ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  /**
   * 格式化时长（秒）
   * @param {number} seconds - 秒数
   */
  const formatDuration = (seconds) => {
    if (!seconds || seconds < 0) return locale.value === 'zh-CN' ? '0秒' : '0s'

    const units = locale.value === 'zh-CN'
      ? { d: '天', h: '小时', m: '分', s: '秒' }
      : { d: 'd', h: 'h', m: 'm', s: 's' }

    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    const parts = []
    if (days > 0) parts.push(`${days}${units.d}`)
    if (hours > 0) parts.push(`${hours}${units.h}`)
    if (minutes > 0) parts.push(`${minutes}${units.m}`)
    if (secs > 0 || parts.length === 0) parts.push(`${secs}${units.s}`)

    return parts.join(' ')
  }

  /**
   * 相对时间（多久之前）
   * @param {Date|string|number} date - 日期
   */
  const formatRelative = (date) => {
    if (!date) return '-'
    const dateObj = date instanceof Date ? date : new Date(date)
    const now = new Date()
    const diffMs = now - dateObj
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (locale.value === 'zh-CN') {
      if (diffSec < 60) return '刚刚'
      if (diffMin < 60) return `${diffMin}分钟前`
      if (diffHour < 24) return `${diffHour}小时前`
      if (diffDay < 30) return `${diffDay}天前`
      return formatDate(dateObj, 'short')
    } else {
      if (diffSec < 60) return 'just now'
      if (diffMin < 60) return `${diffMin}m ago`
      if (diffHour < 24) return `${diffHour}h ago`
      if (diffDay < 30) return `${diffDay}d ago`
      return formatDate(dateObj, 'short')
    }
  }

  return {
    // 基础函数
    t,
    locale,
    setLocale,
    localeLabel,
    localeOptions,

    // 消息翻译
    tm,
    tv,

    // 格式化函数
    formatDate,
    formatNumber,
    formatBytes,
    formatDuration,
    formatRelative,

    // 原始函数（高级用法）
    d,
    n
  }
}

export default useI18n
