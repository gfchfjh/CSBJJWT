/**
 * 全局错误处理器
 * 自动将技术错误转换为友好提示并显示ErrorDialog
 */

import { ref } from 'vue'
import api from '@/api'

// 全局错误状态
const currentError = ref(null)
const showErrorDialog = ref(false)

export function useErrorHandler() {
  /**
   * 处理错误并显示友好提示
   * @param {Error|string} error - 错误对象或错误消息
   * @param {Object} options - 配置选项
   * @returns {Promise<Object>} 翻译后的错误信息
   */
  const handleError = async (error, options = {}) => {
    const {
      showDialog = true,  // 是否显示对话框
      silent = false,     // 是否静默处理（不显示任何提示）
      fallbackMessage = '发生了一个错误'  // 备用错误消息
    } = options

    // 提取技术错误信息
    let technicalError = ''
    if (error instanceof Error) {
      technicalError = error.message
      // 如果是网络错误，尝试获取更详细的信息
      if (error.response) {
        technicalError = error.response.data?.detail || error.response.statusText || technicalError
      }
    } else if (typeof error === 'string') {
      technicalError = error
    } else if (error.detail) {
      technicalError = error.detail
    } else {
      technicalError = JSON.stringify(error)
    }

    console.error('🔴 处理错误:', technicalError)

    if (silent) {
      return null
    }

    try {
      // 调用后端错误翻译API
      const response = await api.post('/api/error-translator/translate', {
        technical_error: technicalError
      })

      const translatedError = {
        title: response.title || '发生错误',
        message: response.message || fallbackMessage,
        solution: response.solution || [],
        auto_fix: response.auto_fix || null,
        fix_description: response.fix_description || null,
        severity: response.severity || 'error',
        category: response.category || 'unknown',
        technical_error: technicalError
      }

      console.log('✅ 错误翻译成功:', translatedError)

      // 显示错误对话框
      if (showDialog) {
        currentError.value = translatedError
        showErrorDialog.value = true
      }

      return translatedError
    } catch (translateError) {
      console.error('❌ 错误翻译失败:', translateError)
      
      // 翻译失败，使用默认错误信息
      const defaultError = {
        title: '😕 发生了一个错误',
        message: technicalError || fallbackMessage,
        solution: [
          '1️⃣ 请重试操作',
          '2️⃣ 如果问题持续，请重启应用',
          '3️⃣ 查看帮助中心或联系技术支持'
        ],
        auto_fix: null,
        severity: 'error',
        category: 'unknown',
        technical_error: technicalError
      }

      if (showDialog) {
        currentError.value = defaultError
        showErrorDialog.value = true
      }

      return defaultError
    }
  }

  /**
   * 批量处理错误
   * @param {Array<Error>} errors - 错误数组
   * @param {Object} options - 配置选项
   */
  const handleErrors = async (errors, options = {}) => {
    if (!Array.isArray(errors) || errors.length === 0) {
      return
    }

    // 只显示第一个错误的对话框，其他错误记录到控制台
    const firstError = await handleError(errors[0], options)
    
    // 其他错误静默处理
    for (let i = 1; i < errors.length; i++) {
      await handleError(errors[i], { ...options, showDialog: false })
    }

    return firstError
  }

  /**
   * 关闭错误对话框
   */
  const closeErrorDialog = () => {
    showErrorDialog.value = false
    currentError.value = null
  }

  /**
   * 包装异步函数，自动处理错误
   * @param {Function} fn - 异步函数
   * @param {Object} options - 错误处理选项
   * @returns {Function} 包装后的函数
   */
  const withErrorHandler = (fn, options = {}) => {
    return async (...args) => {
      try {
        return await fn(...args)
      } catch (error) {
        await handleError(error, options)
        throw error // 重新抛出错误，让调用者可以继续处理
      }
    }
  }

  /**
   * 显示特定类型的错误
   * @param {string} errorType - 错误类型（如 'chromium_not_installed'）
   */
  const showErrorByType = async (errorType) => {
    try {
      const response = await api.get(`/api/error-translator/info/${errorType}`)
      
      currentError.value = {
        ...response,
        technical_error: `Error Type: ${errorType}`
      }
      showErrorDialog.value = true
    } catch (error) {
      console.error('获取错误信息失败:', error)
      await handleError(error)
    }
  }

  /**
   * 获取所有错误类别
   * @returns {Promise<Array<string>>} 错误类别列表
   */
  const getErrorCategories = async () => {
    try {
      const response = await api.get('/api/error-translator/categories')
      return response
    } catch (error) {
      console.error('获取错误类别失败:', error)
      return []
    }
  }

  /**
   * 获取指定类别的所有错误
   * @param {string} category - 错误类别
   * @returns {Promise<Array<string>>} 错误类型列表
   */
  const getErrorsByCategory = async (category) => {
    try {
      const response = await api.get(`/api/error-translator/category/${category}`)
      return response
    } catch (error) {
      console.error(`获取类别"${category}"的错误失败:`, error)
      return []
    }
  }

  return {
    // 状态
    currentError,
    showErrorDialog,
    
    // 方法
    handleError,
    handleErrors,
    closeErrorDialog,
    withErrorHandler,
    showErrorByType,
    getErrorCategories,
    getErrorsByCategory
  }
}

// 导出单例，用于全局访问
let globalErrorHandler = null

export function useGlobalErrorHandler() {
  if (!globalErrorHandler) {
    globalErrorHandler = useErrorHandler()
  }
  return globalErrorHandler
}
