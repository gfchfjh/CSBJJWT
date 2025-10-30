/**
 * 错误处理工具
 */
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

/**
 * 错误代码映射表
 */
const ERROR_MESSAGES = {
  // 网络错误
  'ECONNREFUSED': '无法连接到服务器，请检查后端服务是否启动',
  'ETIMEDOUT': '请求超时，请检查网络连接',
  'NETWORK_ERROR': '网络错误，请检查网络连接',
  
  // 认证错误
  401: '未登录或登录已过期，请重新登录',
  403: '没有权限访问',
  
  // 业务错误
  400: '请求参数错误',
  404: '请求的资源不存在',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务暂时不可用',
  
  // Redis错误
  'REDIS_CONNECTION_ERROR': 'Redis连接失败',
  'REDIS_TIMEOUT': 'Redis操作超时',
  
  // KOOK错误
  'KOOK_LOGIN_FAILED': 'KOOK登录失败',
  'KOOK_CONNECTION_ERROR': 'KOOK连接失败',
  'COOKIE_INVALID': 'Cookie无效或已过期',
  
  // Bot错误
  'DISCORD_WEBHOOK_ERROR': 'Discord Webhook配置错误',
  'TELEGRAM_BOT_ERROR': 'Telegram Bot配置错误',
  'FEISHU_APP_ERROR': '飞书应用配置错误'
}

/**
 * 错误解决方案映射表
 */
const ERROR_SOLUTIONS = {
  'ECONNREFUSED': [
    '检查后端服务是否正在运行',
    '检查端口9527是否被占用',
    '尝试重启应用'
  ],
  'REDIS_CONNECTION_ERROR': [
    'Redis服务可能未启动',
    '检查端口6379是否被占用',
    '查看系统设置中的Redis状态',
    '尝试重启应用'
  ],
  'KOOK_LOGIN_FAILED': [
    '检查Cookie或密码是否正确',
    '尝试重新获取Cookie',
    '检查账号是否被封禁'
  ],
  'COOKIE_INVALID': [
    'Cookie已过期，请重新登录KOOK获取',
    '确保Cookie格式正确（JSON数组）',
    '检查Cookie是否包含必要字段'
  ]
}

/**
 * 处理API错误
 * @param {Error} error - 错误对象
 * @param {Object} options - 配置选项
 */
export function handleApiError(error, options = {}) {
  const {
    title = '操作失败',
    showNotification = false,
    showMessage = true,
    showSolution = true
  } = options
  
  let errorMessage = '未知错误'
  let errorCode = null
  let solutions = []
  
  // 解析错误
  if (error.response) {
    // 服务器返回错误
    errorCode = error.response.status
    errorMessage = error.response.data?.detail || 
                   error.response.data?.message || 
                   ERROR_MESSAGES[errorCode] || 
                   `服务器错误 (${errorCode})`
    
    // 获取错误代码（如果有）
    const code = error.response.data?.code
    if (code && ERROR_SOLUTIONS[code]) {
      solutions = ERROR_SOLUTIONS[code]
    }
  } else if (error.request) {
    // 请求发出但没有响应
    errorCode = error.code || 'NETWORK_ERROR'
    errorMessage = ERROR_MESSAGES[errorCode] || '网络错误'
    solutions = ERROR_SOLUTIONS[errorCode] || []
  } else {
    // 其他错误
    errorMessage = error.message || '未知错误'
  }
  
  // 显示错误消息
  if (showMessage) {
    ElMessage.error({
      message: errorMessage,
      duration: 5000
    })
  }
  
  // 显示通知（包含解决方案）
  if (showNotification || (showSolution && solutions.length > 0)) {
    const notificationMessage = solutions.length > 0
      ? `${errorMessage}\n\n💡 解决建议：\n${solutions.map((s, i) => `${i + 1}. ${s}`).join('\n')}`
      : errorMessage
    
    ElNotification.error({
      title,
      message: notificationMessage,
      duration: 10000,
      dangerouslyUseHTMLString: false
    })
  }
  
  // 返回错误信息
  return {
    message: errorMessage,
    code: errorCode,
    solutions
  }
}

/**
 * 显示成功消息
 * @param {string} message - 消息内容
 * @param {Object} options - 配置选项
 */
export function showSuccess(message, options = {}) {
  const { duration = 3000, showNotification = false } = options
  
  if (showNotification) {
    ElNotification.success({
      title: '成功',
      message,
      duration
    })
  } else {
    ElMessage.success({
      message,
      duration
    })
  }
}

/**
 * 显示警告消息
 * @param {string} message - 消息内容
 * @param {Object} options - 配置选项
 */
export function showWarning(message, options = {}) {
  const { duration = 3000, showNotification = false } = options
  
  if (showNotification) {
    ElNotification.warning({
      title: '警告',
      message,
      duration
    })
  } else {
    ElMessage.warning({
      message,
      duration
    })
  }
}

/**
 * 确认危险操作
 * @param {string} message - 提示消息
 * @param {Object} options - 配置选项
 * @returns {Promise} 确认结果
 */
export async function confirmDangerousAction(message, options = {}) {
  const {
    title = '确认操作',
    confirmButtonText = '确定',
    cancelButtonText = '取消',
    type = 'warning'
  } = options
  
  try {
    await ElMessageBox.confirm(message, title, {
      confirmButtonText,
      cancelButtonText,
      type,
      center: true
    })
    return true
  } catch {
    return false
  }
}

/**
 * 输入对话框
 * @param {string} message - 提示消息
 * @param {Object} options - 配置选项
 * @returns {Promise<string|null>} 输入内容
 */
export async function promptInput(message, options = {}) {
  const {
    title = '请输入',
    inputType = 'text',
    inputPlaceholder = '',
    inputValidator = null
  } = options
  
  try {
    const { value } = await ElMessageBox.prompt(message, title, {
      inputType,
      inputPlaceholder,
      inputValidator,
      center: true
    })
    return value
  } catch {
    return null
  }
}
