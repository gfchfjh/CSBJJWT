/**
 * Axios 拦截器配置
 * ✅ P0-2优化：集成友好错误提示
 */

import { ElMessage } from 'element-plus'
import { showFriendlyError } from '@/composables/useErrorHandler'

/**
 * 设置请求拦截器
 */
export function setupRequestInterceptor(axios) {
  axios.interceptors.request.use(
    config => {
      // 可以在这里添加token等
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )
}

/**
 * 设置响应拦截器（集成友好错误提示）
 */
export function setupResponseInterceptor(axios) {
  axios.interceptors.response.use(
    response => response,
    async error => {
      // 提取错误信息
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
          // 可能是映射未找到或Bot未配置
          if (technicalError.toLowerCase().includes('mapping')) {
            errorType = 'mapping_not_found'
          } else if (technicalError.toLowerCase().includes('bot')) {
            errorType = 'bot_not_configured'
          }
        } else if (status === 429) {
          errorType = 'rate_limit_exceeded'
        }
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorType = 'network_timeout'
      } else if (error.message.includes('Network Error')) {
        errorType = 'network_timeout'
      }
      
      // 显示友好错误
      try {
        await showFriendlyError(technicalError, errorType)
      } catch (e) {
        // 如果友好错误对话框失败，降级为Toast
        console.error('友好错误对话框显示失败:', e)
        ElMessage.error(technicalError)
      }
      
      return Promise.reject(error)
    }
  )
}

/**
 * 设置所有拦截器
 */
export function setupInterceptors(axios) {
  setupRequestInterceptor(axios)
  setupResponseInterceptor(axios)
}
