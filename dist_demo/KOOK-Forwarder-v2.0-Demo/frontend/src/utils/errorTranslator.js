/**
 * 错误翻译器 - 将技术错误翻译为用户友好的提示
 * P0-7优化: 提供解决方案
 */

// 错误模式匹配表
const errorPatterns = {
  // ==================== Telegram错误 ====================
  'flood': {
    title: '⏱️ 操作过于频繁',
    message: 'Telegram限制了发送速度，请稍后再试',
    solution: '建议等待30秒后重试，或降低消息发送频率',
    type: 'warning',
    autoRetry: true
  },
  'flood control': {
    title: '⏱️ 触发限流保护',
    message: 'Telegram API检测到过于频繁的请求',
    solution: '系统会自动等待后重试，请勿重复操作',
    type: 'warning',
    autoRetry: true
  },
  'too many requests': {
    title: '⏱️ 请求过多',
    message: '超过了API的请求限制',
    solution: '请稍等片刻，系统会自动处理',
    type: 'warning',
    autoRetry: true
  },
  'wrong file identifier': {
    title: '🖼️ 图片无效',
    message: '图片URL已失效或格式不支持',
    solution: '请重新上传图片，或在设置中启用"仅使用图床"模式',
    type: 'error',
    action: {
      text: '查看图片设置',
      path: '/settings#image-strategy'
    }
  },
  'file_id': {
    title: '📁 文件标识符错误',
    message: '无法识别的文件标识符',
    solution: '建议重新发送文件，或检查文件大小是否超过限制（50MB）',
    type: 'error'
  },
  'chat not found': {
    title: '❌ 群组不存在',
    message: '找不到指定的Chat ID',
    solution: '请确保Bot已添加到群组，并使用"自动获取Chat ID"功能重新获取',
    type: 'error',
    action: {
      text: '重新获取Chat ID',
      path: '/bots#telegram'
    }
  },
  'bot was kicked': {
    title: '🚫 Bot被移出群组',
    message: 'Telegram Bot已被管理员移除',
    solution: '请重新将Bot添加到群组，并赋予必要的权限',
    type: 'error'
  },
  'bot was blocked': {
    title: '🚫 Bot被封禁',
    message: '用户封禁了此Bot',
    solution: '请联系用户解除封禁，或更换其他Bot',
    type: 'error'
  },
  'message is too long': {
    title: '📏 消息过长',
    message: '消息超过了Telegram的4096字符限制',
    solution: '系统会自动分段发送，请稍候',
    type: 'warning',
    autoRetry: true
  },

  // ==================== Discord错误 ====================
  'Invalid Webhook Token': {
    title: '🔑 Webhook无效',
    message: 'Discord Webhook Token已失效或被删除',
    solution: '请重新创建Webhook并更新配置',
    type: 'error',
    action: {
      text: '重新配置Webhook',
      path: '/bots#discord'
    }
  },
  'Unknown Webhook': {
    title: '❌ Webhook不存在',
    message: 'Discord服务器上找不到此Webhook',
    solution: '请检查Webhook URL是否正确，或重新创建Webhook',
    type: 'error'
  },
  '429': {
    title: '⏱️ Discord API限流',
    message: 'Discord限制了请求速度',
    solution: '系统会自动等待后重试，通常需要等待5-10秒',
    type: 'warning',
    autoRetry: true
  },
  'rate limit': {
    title: '⏱️ 触发速率限制',
    message: 'Discord检测到过多请求',
    solution: '建议降低转发频率，或配置多个Webhook分散流量',
    type: 'warning',
    action: {
      text: '了解Webhook池',
      path: '/help#webhook-pool'
    }
  },
  'Missing Permissions': {
    title: '🔒 缺少权限',
    message: 'Discord Bot缺少必要的权限',
    solution: '请检查Bot权限设置，确保拥有"发送消息"和"上传文件"权限',
    type: 'error'
  },
  'Cannot send an empty message': {
    title: '📭 消息为空',
    message: '尝试发送空消息到Discord',
    solution: '请检查消息内容是否正确格式化',
    type: 'error'
  },
  'Message content is too long': {
    title: '📏 消息超长',
    message: '消息超过Discord的2000字符限制',
    solution: '系统会自动分段发送',
    type: 'warning',
    autoRetry: true
  },
  'File too large': {
    title: '📦 文件过大',
    message: '文件超过Discord的上传限制（8MB免费版/50MB Nitro）',
    solution: '请压缩文件或使用图床模式',
    type: 'error'
  },

  // ==================== 飞书错误 ====================
  'app_ticket_invalid': {
    title: '🔑 App凭证无效',
    message: '飞书应用凭证已过期',
    solution: '请检查App ID和App Secret是否正确',
    type: 'error',
    action: {
      text: '重新配置飞书',
      path: '/bots#feishu'
    }
  },
  'tenant_access_token': {
    title: '🔐 访问令牌失效',
    message: '飞书访问令牌已过期',
    solution: '系统会自动刷新令牌，请稍后重试',
    type: 'warning',
    autoRetry: true
  },
  'no permission': {
    title: '🚫 无权限',
    message: '飞书Bot缺少必要权限',
    solution: '请在飞书开放平台开启"发送消息"权限',
    type: 'error'
  },
  'chat not found': {
    title: '❌ 群组不存在',
    message: '找不到指定的飞书群组',
    solution: '请确保Bot已添加到群组',
    type: 'error'
  },

  // ==================== KOOK错误 ====================
  'cookie expired': {
    title: '🍪 Cookie已过期',
    message: 'KOOK登录状态已失效',
    solution: '请重新导入Cookie或使用账号密码登录',
    type: 'error',
    action: {
      text: '重新登录',
      path: '/accounts'
    }
  },
  'authentication failed': {
    title: '🔐 认证失败',
    message: 'KOOK账号认证失败',
    solution: '请检查Cookie是否正确，或重新登录',
    type: 'error'
  },
  'websocket closed': {
    title: '🔌 连接断开',
    message: 'KOOK WebSocket连接已关闭',
    solution: '系统会自动重连，最多重试5次',
    type: 'warning',
    autoRetry: true
  },
  'captcha required': {
    title: '🔐 需要验证码',
    message: 'KOOK要求输入验证码',
    solution: '请在弹出窗口中输入验证码',
    type: 'warning'
  },

  // ==================== 网络错误 ====================
  'Network Error': {
    title: '🌐 网络连接失败',
    message: '无法连接到服务器',
    solution: '请检查网络连接，确保后端服务正在运行（端口9527）',
    type: 'error',
    action: {
      text: '检查服务状态',
      path: '/settings#service-status'
    }
  },
  'ECONNREFUSED': {
    title: '🚫 连接被拒绝',
    message: '无法连接到目标服务器',
    solution: '请确保服务正在运行，或检查防火墙设置',
    type: 'error'
  },
  'timeout': {
    title: '⏰ 请求超时',
    message: '服务器响应时间过长（超过30秒）',
    solution: '请检查网络状况，或稍后重试',
    type: 'warning',
    autoRetry: true
  },
  'ETIMEDOUT': {
    title: '⏰ 连接超时',
    message: '连接超时，服务器未响应',
    solution: '请检查网络连接和服务器状态',
    type: 'error'
  },
  'DNS': {
    title: '🌐 域名解析失败',
    message: '无法解析域名，请检查网络连接',
    solution: '请确保网络正常，DNS服务可用',
    type: 'error'
  },

  // ==================== 通用错误 ====================
  '401': {
    title: '🔐 未授权',
    message: '身份验证失败',
    solution: '请重新登录系统',
    type: 'error',
    action: {
      text: '重新登录',
      path: '/login'
    }
  },
  '403': {
    title: '🚫 禁止访问',
    message: '没有权限访问此资源',
    solution: '请联系管理员获取访问权限',
    type: 'error'
  },
  '404': {
    title: '❌ 资源不存在',
    message: '请求的资源未找到',
    solution: '请检查URL是否正确，或联系技术支持',
    type: 'error'
  },
  '500': {
    title: '⚠️ 服务器错误',
    message: '服务器内部错误',
    solution: '请稍后重试，问题持续请查看日志或联系技术支持',
    type: 'error'
  },
  '502': {
    title: '🔌 网关错误',
    message: '网关或代理服务器错误',
    solution: '服务器暂时不可用，请稍后重试',
    type: 'error'
  },
  '503': {
    title: '🚧 服务不可用',
    message: '服务暂时不可用',
    solution: '服务可能正在维护，请稍后重试',
    type: 'warning'
  },
  'JSON': {
    title: '📄 数据格式错误',
    message: '服务器返回的数据格式不正确',
    solution: '请检查API配置或联系技术支持',
    type: 'error'
  },
  'parse': {
    title: '🔧 解析失败',
    message: '无法解析服务器返回的数据',
    solution: '数据格式可能有误，请联系技术支持',
    type: 'error'
  }
}

/**
 * 翻译错误信息
 * @param {Error|string} error - 错误对象或错误消息
 * @returns {object} 友好的错误信息对象
 */
export function translateError(error) {
  // 提取错误消息
  let errorMsg = ''
  if (typeof error === 'string') {
    errorMsg = error
  } else if (error instanceof Error) {
    errorMsg = error.message || error.toString()
  } else if (error?.message) {
    errorMsg = error.message
  } else if (error?.response?.data?.message) {
    errorMsg = error.response.data.message
  } else if (error?.response?.data?.detail) {
    errorMsg = error.response.data.detail
  } else {
    errorMsg = String(error)
  }

  errorMsg = errorMsg.toLowerCase()

  // 查找匹配的错误模式
  for (const [pattern, translation] of Object.entries(errorPatterns)) {
    if (errorMsg.includes(pattern.toLowerCase())) {
      return {
        ...translation,
        originalError: errorMsg.substring(0, 200), // 保留原始错误（截断）
        timestamp: new Date().toISOString()
      }
    }
  }

  // 未匹配到，返回通用错误
  return {
    title: '❌ 操作失败',
    message: '发生了未知错误',
    solution: '请查看详细日志，或联系技术支持',
    type: 'error',
    originalError: errorMsg.substring(0, 200),
    timestamp: new Date().toISOString()
  }
}

/**
 * 获取错误类型的图标
 * @param {string} type - 错误类型 (error/warning/info)
 * @returns {string} Element Plus图标类名
 */
export function getErrorIcon(type) {
  const icons = {
    error: 'el-icon-circle-close',
    warning: 'el-icon-warning',
    info: 'el-icon-info',
    success: 'el-icon-circle-check'
  }
  return icons[type] || icons.error
}

/**
 * 判断错误是否可以自动重试
 * @param {Error|string} error - 错误对象或错误消息
 * @returns {boolean} 是否可以自动重试
 */
export function canAutoRetry(error) {
  const translated = translateError(error)
  return translated.autoRetry === true
}

/**
 * 获取错误的建议操作
 * @param {Error|string} error - 错误对象或错误消息
 * @returns {object|null} 操作对象 {text, path} 或 null
 */
export function getErrorAction(error) {
  const translated = translateError(error)
  return translated.action || null
}

/**
 * 格式化错误用于显示
 * @param {Error|string} error - 错误对象或错误消息
 * @param {boolean} includeOriginal - 是否包含原始错误信息
 * @returns {string} 格式化后的错误信息
 */
export function formatErrorMessage(error, includeOriginal = false) {
  const translated = translateError(error)
  
  let message = `${translated.title}\n\n${translated.message}\n\n💡 ${translated.solution}`
  
  if (includeOriginal && translated.originalError) {
    message += `\n\n详细信息：${translated.originalError}`
  }
  
  return message
}

export default {
  translateError,
  getErrorIcon,
  canAutoRetry,
  getErrorAction,
  formatErrorMessage
}
