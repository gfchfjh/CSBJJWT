/**
 * 统一通知管理 Composable
 * 提供更好的用户反馈体验
 */
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus'

export function useNotification() {
  /**
   * 成功通知
   */
  const notifySuccess = (title, message, duration = 3000) => {
    ElNotification({
      title,
      message,
      type: 'success',
      duration,
      position: 'top-right'
    })
  }

  /**
   * 错误通知
   */
  const notifyError = (title, message, duration = 5000) => {
    ElNotification({
      title,
      message,
      type: 'error',
      duration,
      position: 'top-right',
      showClose: true
    })
  }

  /**
   * 警告通知
   */
  const notifyWarning = (title, message, duration = 4000) => {
    ElNotification({
      title,
      message,
      type: 'warning',
      duration,
      position: 'top-right'
    })
  }

  /**
   * 信息通知
   */
  const notifyInfo = (title, message, duration = 3000) => {
    ElNotification({
      title,
      message,
      type: 'info',
      duration,
      position: 'top-right'
    })
  }

  /**
   * 带操作的通知
   */
  const notifyWithAction = (title, message, actionText, onAction) => {
    const h = ElNotification.$createElement
    ElNotification({
      title,
      message: h('div', [
        h('p', message),
        h('el-button', {
          size: 'small',
          type: 'primary',
          onClick: onAction
        }, actionText)
      ]),
      duration: 0, // 不自动关闭
      position: 'top-right'
    })
  }

  /**
   * 进度通知
   */
  const notifyProgress = (title, progress = 0) => {
    const h = ElNotification.$createElement
    return ElNotification({
      title,
      message: h('el-progress', {
        percentage: progress,
        strokeWidth: 8
      }),
      duration: 0,
      position: 'top-right',
      showClose: false
    })
  }

  /**
   * 简单消息提示
   */
  const showMessage = (message, type = 'info', duration = 2000) => {
    ElMessage({
      message,
      type,
      duration,
      showClose: true
    })
  }

  /**
   * 确认对话框
   */
  const confirm = async (message, title = '确认', options = {}) => {
    try {
      await ElMessageBox.confirm(message, title, {
        confirmButtonText: options.confirmText || '确定',
        cancelButtonText: options.cancelText || '取消',
        type: options.type || 'warning',
        distinguishCancelAndClose: true,
        ...options
      })
      return true
    } catch (action) {
      if (action === 'cancel' || action === 'close') {
        return false
      }
      throw action
    }
  }

  /**
   * 输入对话框
   */
  const prompt = async (message, title = '输入', options = {}) => {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        confirmButtonText: options.confirmText || '确定',
        cancelButtonText: options.cancelText || '取消',
        inputPattern: options.pattern,
        inputErrorMessage: options.errorMessage || '输入格式不正确',
        inputPlaceholder: options.placeholder || '',
        inputValue: options.defaultValue || '',
        ...options
      })
      return value
    } catch (action) {
      if (action === 'cancel' || action === 'close') {
        return null
      }
      throw action
    }
  }

  /**
   * 警告对话框
   */
  const alert = async (message, title = '提示', options = {}) => {
    await ElMessageBox.alert(message, title, {
      confirmButtonText: options.confirmText || '确定',
      type: options.type || 'info',
      ...options
    })
  }

  /**
   * 操作反馈（带加载）
   */
  const withLoading = async (asyncFunc, loadingText = '处理中...') => {
    const loading = ElMessage({
      message: loadingText,
      type: 'info',
      duration: 0,
      iconClass: 'el-icon-loading'
    })

    try {
      const result = await asyncFunc()
      loading.close()
      return { success: true, data: result }
    } catch (error) {
      loading.close()
      return { success: false, error }
    }
  }

  /**
   * API错误处理
   */
  const handleApiError = (error, customMessage = null) => {
    console.error('API错误:', error)

    let message = customMessage || '操作失败'
    let title = '错误'

    if (error.response) {
      // 服务器响应错误
      const status = error.response.status
      const data = error.response.data

      switch (status) {
        case 400:
          title = '请求错误'
          message = data.detail || data.message || '请求参数有误'
          break
        case 401:
          title = '未授权'
          message = '请先登录'
          break
        case 403:
          title = '禁止访问'
          message = '您没有权限执行此操作'
          break
        case 404:
          title = '未找到'
          message = '请求的资源不存在'
          break
        case 429:
          title = '请求过快'
          message = '操作过于频繁，请稍后再试'
          break
        case 500:
          title = '服务器错误'
          message = data.detail || '服务器内部错误，请稍后重试'
          break
        case 503:
          title = '服务不可用'
          message = '服务暂时不可用，请稍后重试'
          break
        default:
          title = `错误 ${status}`
          message = data.detail || data.message || '未知错误'
      }
    } else if (error.request) {
      // 请求发送失败
      title = '网络错误'
      message = '无法连接到服务器，请检查网络连接'
    } else {
      // 其他错误
      message = error.message || '未知错误'
    }

    notifyError(title, message)
  }

  /**
   * 成功操作反馈
   */
  const handleSuccess = (message, showNotification = true) => {
    if (showNotification) {
      showMessage(message, 'success')
    }
  }

  /**
   * 批量操作进度通知
   */
  const batchOperationProgress = (total, current, successCount, failCount) => {
    const percentage = Math.round((current / total) * 100)
    const message = `处理进度：${current}/${total}，成功：${successCount}，失败：${failCount}`
    
    return {
      percentage,
      message,
      isComplete: current >= total
    }
  }

  return {
    // 通知
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
    notifyWithAction,
    notifyProgress,

    // 消息
    showMessage,

    // 对话框
    confirm,
    prompt,
    alert,

    // 工具
    withLoading,
    handleApiError,
    handleSuccess,
    batchOperationProgress
  }
}
