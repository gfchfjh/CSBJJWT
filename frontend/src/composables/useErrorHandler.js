/**
 * 全局错误处理 Composable
 * ✅ P0-2优化：集成友好错误提示系统
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 友好错误对话框实例（全局单例）
let friendlyErrorDialog = null

/**
 * 设置友好错误对话框实例
 */
export function setFriendlyErrorDialog(dialog) {
  friendlyErrorDialog = dialog
}

/**
 * 使用错误处理器
 */
export function useErrorHandler() {
  const isHandlingError = ref(false)
  
  /**
   * 处理错误（自动判断是否使用友好提示）
   */
  const handleError = async (error, options = {}) => {
    if (isHandlingError.value) return
    
    isHandlingError.value = true
    
    try {
      const {
        showFriendly = true,      // 是否显示友好提示
        showToast = true,          // 是否显示Toast提示
        errorType = null,          // 错误类型（用于精确匹配）
        fallbackMessage = '操作失败' // 降级提示消息
      } = options
      
      // 提取错误消息
      const technicalError = extractErrorMessage(error)
      
      // 如果启用友好提示且对话框可用
      if (showFriendly && friendlyErrorDialog) {
        await friendlyErrorDialog.showError(technicalError, errorType)
      } else if (showToast) {
        // 降级：显示Toast
        ElMessage.error(technicalError || fallbackMessage)
      }
      
      // 记录到控制台
      console.error('Error handled:', error)
      
    } finally {
      isHandlingError.value = false
    }
  }
  
  /**
   * 处理API错误（专门针对HTTP请求错误）
   */
  const handleApiError = async (error, customOptions = {}) => {
    const options = {
      showFriendly: true,
      showToast: true,
      ...customOptions
    }
    
    // 提取API错误信息
    const technicalError = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          error.message ||
                          '网络请求失败'
    
    // 根据HTTP状态码判断错误类型
    let errorType = null
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        errorType = 'cookie_expired'
      } else if (status === 403) {
        errorType = 'permission_denied'
      } else if (status === 404) {
        errorType = 'mapping_not_found'
      } else if (status === 429) {
        errorType = 'rate_limit_exceeded'
      } else if (status >= 500) {
        errorType = null // 服务器错误，使用默认提示
      }
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      errorType = 'network_timeout'
    }
    
    await handleError(technicalError, {
      ...options,
      errorType
    })
  }
  
  /**
   * 处理验证错误
   */
  const handleValidationError = (errors) => {
    if (Array.isArray(errors)) {
      const messages = errors.map(e => e.message || e).join('\n')
      ElMessage.warning(messages)
    } else {
      ElMessage.warning(errors.toString())
    }
  }
  
  /**
   * 提取错误消息
   */
  const extractErrorMessage = (error) => {
    if (typeof error === 'string') {
      return error
    }
    
    if (error.response) {
      // HTTP响应错误
      return error.response.data?.detail || 
             error.response.data?.message || 
             error.response.statusText ||
             `HTTP ${error.response.status} Error`
    }
    
    if (error.request) {
      // 请求已发送但没有收到响应
      return '网络请求超时或无响应'
    }
    
    // 其他错误
    return error.message || error.toString() || '未知错误'
  }
  
  return {
    isHandlingError,
    handleError,
    handleApiError,
    handleValidationError
  }
}

/**
 * 快捷方法：显示友好错误
 */
export async function showFriendlyError(technicalError, errorType = null) {
  if (friendlyErrorDialog) {
    await friendlyErrorDialog.showError(technicalError, errorType)
  } else {
    console.warn('FriendlyErrorDialog未初始化，降级为Toast提示')
    ElMessage.error(technicalError)
  }
}

export default {
  useErrorHandler,
  setFriendlyErrorDialog,
  showFriendlyError
}
