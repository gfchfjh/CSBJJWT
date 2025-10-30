/**
 * 错误处理工具 - 友好提示系统
 * ✅ P0-12: 将错误代码转换为用户友好的提示
 */
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

/**
 * 错误代码映射表
 */
export const ERROR_MESSAGES = {
  // KOOK相关错误
  'KOOK_AUTH_FAILED': {
    title: 'KOOK登录失败',
    message: 'Cookie已过期或账号密码错误，请重新登录',
    type: 'error',
    icon: '🔒',
    actions: [
      { label: '重新登录', action: 'relogin' },
      { label: '查看教程', action: 'tutorial', link: '/docs/kook-login' }
    ],
    solutions: [
      '1. 检查Cookie是否正确复制',
      '2. 尝试重新获取Cookie',
      '3. 使用账号密码登录'
    ]
  },
  
  'KOOK_CONNECTION_LOST': {
    title: 'KOOK连接断开',
    message: '与KOOK服务器的连接已断开，正在尝试重新连接...',
    type: 'warning',
    icon: '📡',
    actions: [
      { label: '手动重连', action: 'reconnect' },
      { label: '查看状态', action: 'status' }
    ],
    solutions: [
      '1. 检查网络连接',
      '2. 稍等片刻，系统会自动重连',
      '3. 如持续失败，请重启服务'
    ]
  },
  
  'KOOK_RATE_LIMITED': {
    title: 'KOOK请求过于频繁',
    message: '触发了KOOK的速率限制，请稍后再试',
    type: 'warning',
    icon: '⏱️',
    solutions: [
      '1. 等待30秒后再试',
      '2. 减少频道数量',
      '3. 降低消息转发频率'
    ]
  },
  
  'KOOK_SERVER_NOT_FOUND': {
    title: '服务器不存在',
    message: '无法找到指定的KOOK服务器，可能已被删除或您没有访问权限',
    type: 'error',
    icon: '❌',
    solutions: [
      '1. 检查服务器ID是否正确',
      '2. 确认您是服务器成员',
      '3. 刷新服务器列表'
    ]
  },
  
  'KOOK_CHANNEL_NOT_FOUND': {
    title: '频道不存在',
    message: '无法找到指定的频道，可能已被删除或权限不足',
    type: 'error',
    icon: '❌',
    solutions: [
      '1. 检查频道是否存在',
      '2. 确认您有访问权限',
      '3. 刷新频道列表'
    ]
  },
  
  // Discord相关错误
  'DISCORD_WEBHOOK_INVALID': {
    title: 'Discord Webhook无效',
    message: 'Webhook URL格式错误或已失效',
    type: 'error',
    icon: '🔗',
    actions: [
      { label: '重新配置', action: 'reconfig' },
      { label: '测试连接', action: 'test' },
      { label: '查看教程', action: 'tutorial', link: '/docs/discord-webhook' }
    ],
    solutions: [
      '1. 检查Webhook URL是否完整',
      '2. 确认Webhook未被删除',
      '3. 重新创建Webhook'
    ]
  },
  
  'DISCORD_RATE_LIMITED': {
    title: 'Discord速率限制',
    message: '发送消息过快，触发Discord限流',
    type: 'warning',
    icon: '🚦',
    solutions: [
      '1. 消息已自动排队，稍后重试',
      '2. 减少频道映射数量',
      '3. 调整限流设置'
    ]
  },
  
  'DISCORD_MESSAGE_TOO_LONG': {
    title: '消息过长',
    message: 'Discord消息长度超过2000字符',
    type: 'warning',
    icon: '📝',
    solutions: [
      '1. 消息已自动分段发送',
      '2. 考虑启用消息摘要',
      '3. 过滤掉过长的消息'
    ]
  },
  
  // Telegram相关错误
  'TELEGRAM_BOT_TOKEN_INVALID': {
    title: 'Telegram Bot Token无效',
    message: 'Bot Token格式错误或已失效',
    type: 'error',
    icon: '🤖',
    actions: [
      { label: '重新配置', action: 'reconfig' },
      { label: '查看教程', action: 'tutorial', link: '/docs/telegram-bot' }
    ],
    solutions: [
      '1. 检查Token是否完整',
      '2. 与@BotFather确认Token',
      '3. 重新创建Bot'
    ]
  },
  
  'TELEGRAM_CHAT_NOT_FOUND': {
    title: 'Telegram群组未找到',
    message: 'Chat ID不存在或Bot未加入群组',
    type: 'error',
    icon: '👥',
    solutions: [
      '1. 检查Chat ID是否正确',
      '2. 确认Bot已加入群组',
      '3. 使用自动获取Chat ID功能'
    ]
  },
  
  'TELEGRAM_BOT_KICKED': {
    title: 'Bot被移出群组',
    message: 'Bot已被踢出Telegram群组',
    type: 'error',
    icon: '🚪',
    actions: [
      { label: '重新邀请Bot', action: 'reinvite' }
    ],
    solutions: [
      '1. 重新将Bot添加到群组',
      '2. 检查Bot权限设置',
      '3. 更新群组配置'
    ]
  },
  
  // 飞书相关错误
  'FEISHU_APP_ID_INVALID': {
    title: '飞书App ID无效',
    message: 'App ID或App Secret配置错误',
    type: 'error',
    icon: '🔑',
    actions: [
      { label: '重新配置', action: 'reconfig' },
      { label: '查看教程', action: 'tutorial', link: '/docs/feishu-app' }
    ],
    solutions: [
      '1. 检查App ID和Secret是否正确',
      '2. 确认应用已启用',
      '3. 重新获取凭证'
    ]
  },
  
  'FEISHU_TOKEN_EXPIRED': {
    title: '飞书Token过期',
    message: '飞书访问Token已过期',
    type: 'warning',
    icon: '⏰',
    solutions: [
      '1. 系统会自动刷新Token',
      '2. 如持续失败，请重新配置',
      '3. 检查App Secret是否正确'
    ]
  },
  
  // 图片处理错误
  'IMAGE_DOWNLOAD_FAILED': {
    title: '图片下载失败',
    message: '无法下载图片，可能被防盗链保护',
    type: 'warning',
    icon: '🖼️',
    solutions: [
      '1. 图片已保存到失败队列',
      '2. 稍后会自动重试',
      '3. 检查网络连接'
    ]
  },
  
  'IMAGE_TOO_LARGE': {
    title: '图片过大',
    message: '图片大小超过限制',
    type: 'warning',
    icon: '📦',
    solutions: [
      '1. 系统会自动压缩图片',
      '2. 调整压缩质量设置',
      '3. 跳过过大的图片'
    ]
  },
  
  'IMAGE_UPLOAD_FAILED': {
    title: '图片上传失败',
    message: '图片上传到目标平台失败',
    type: 'error',
    icon: '☁️',
    solutions: [
      '1. 已切换到图床模式',
      '2. 检查目标平台状态',
      '3. 重试上传'
    ]
  },
  
  // 系统错误
  'NETWORK_ERROR': {
    title: '网络错误',
    message: '网络连接异常，请检查网络设置',
    type: 'error',
    icon: '🌐',
    solutions: [
      '1. 检查网络连接',
      '2. 检查代理设置',
      '3. 稍后重试'
    ]
  },
  
  'DATABASE_ERROR': {
    title: '数据库错误',
    message: '数据库操作失败',
    type: 'error',
    icon: '💾',
    actions: [
      { label: '重启服务', action: 'restart' },
      { label: '查看日志', action: 'logs' }
    ],
    solutions: [
      '1. 检查磁盘空间',
      '2. 重启应用程序',
      '3. 恢复数据库备份'
    ]
  },
  
  'CONFIG_INVALID': {
    title: '配置错误',
    message: '配置文件格式错误或参数无效',
    type: 'error',
    icon: '⚙️',
    actions: [
      { label: '重置配置', action: 'reset' },
      { label: '查看文档', action: 'docs' }
    ],
    solutions: [
      '1. 检查配置参数',
      '2. 恢复默认配置',
      '3. 查看配置文档'
    ]
  },
  
  'SERVICE_UNAVAILABLE': {
    title: '服务不可用',
    message: '后端服务未启动或无法连接',
    type: 'error',
    icon: '🔧',
    actions: [
      { label: '启动服务', action: 'start' },
      { label: '查看状态', action: 'status' }
    ],
    solutions: [
      '1. 启动后端服务',
      '2. 检查端口占用',
      '3. 查看服务日志'
    ]
  },
  
  // 通用错误
  'UNKNOWN_ERROR': {
    title: '未知错误',
    message: '发生了未预期的错误',
    type: 'error',
    icon: '❓',
    actions: [
      { label: '重试', action: 'retry' },
      { label: '查看日志', action: 'logs' },
      { label: '联系支持', action: 'support' }
    ],
    solutions: [
      '1. 查看详细错误日志',
      '2. 尝试重启应用',
      '3. 联系技术支持'
    ]
  }
}

/**
 * 错误处理类
 */
export class ErrorHandler {
  /**
   * 处理错误
   * @param {Error|string} error - 错误对象或错误代码
   * @param {Object} options - 额外选项
   */
  static handle(error, options = {}) {
    let errorCode = null
    let errorMessage = null
    let errorDetails = null
    
    // 解析错误
    if (typeof error === 'string') {
      errorCode = error
    } else if (error instanceof Error) {
      errorMessage = error.message
      errorDetails = error.stack
      
      // 尝试从错误消息中提取错误代码
      errorCode = this.extractErrorCode(errorMessage)
    } else if (error?.code) {
      errorCode = error.code
      errorMessage = error.message
      errorDetails = error.details
    }
    
    // 获取错误信息
    const errorInfo = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES['UNKNOWN_ERROR']
    
    // 根据选项决定展示方式
    const displayMode = options.mode || 'notification' // notification | message | dialog
    
    if (displayMode === 'notification') {
      this.showNotification(errorInfo, errorCode, errorMessage, options)
    } else if (displayMode === 'message') {
      this.showMessage(errorInfo, errorCode, errorMessage, options)
    } else if (displayMode === 'dialog') {
      this.showDialog(errorInfo, errorCode, errorMessage, errorDetails, options)
    }
    
    // 记录错误日志
    this.logError(errorCode, errorMessage, errorDetails)
  }
  
  /**
   * 显示通知
   */
  static showNotification(errorInfo, errorCode, errorMessage, options) {
    const message = errorMessage || errorInfo.message
    
    ElNotification({
      title: `${errorInfo.icon} ${errorInfo.title}`,
      message: message,
      type: errorInfo.type,
      duration: options.duration || 5000,
      showClose: true,
      dangerouslyUseHTMLString: false
    })
  }
  
  /**
   * 显示消息提示
   */
  static showMessage(errorInfo, errorCode, errorMessage, options) {
    const message = `${errorInfo.icon} ${errorInfo.title}: ${errorMessage || errorInfo.message}`
    
    ElMessage({
      message,
      type: errorInfo.type,
      duration: options.duration || 3000,
      showClose: true
    })
  }
  
  /**
   * 显示对话框
   */
  static async showDialog(errorInfo, errorCode, errorMessage, errorDetails, options) {
    const message = `
      <div class="error-dialog">
        <div class="error-message">
          ${errorMessage || errorInfo.message}
        </div>
        ${errorInfo.solutions ? `
          <div class="error-solutions">
            <h4>💡 解决方案：</h4>
            <ul>
              ${errorInfo.solutions.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
        ${errorDetails && options.showDetails ? `
          <div class="error-details">
            <details>
              <summary>查看详细错误信息</summary>
              <pre>${errorDetails}</pre>
            </details>
          </div>
        ` : ''}
      </div>
    `
    
    const buttons = []
    
    if (errorInfo.actions) {
      errorInfo.actions.forEach(action => {
        buttons.push({
          text: action.label,
          callback: () => this.handleAction(action, options)
        })
      })
    }
    
    try {
      await ElMessageBox.alert(message, `${errorInfo.icon} ${errorInfo.title}`, {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '知道了',
        type: errorInfo.type,
        customClass: 'error-message-box'
      })
    } catch (e) {
      // 用户关闭对话框
    }
  }
  
  /**
   * 处理操作按钮
   */
  static handleAction(action, options) {
    if (action.link) {
      // 打开链接
      window.open(action.link, '_blank')
    } else if (action.action && options.onAction) {
      // 触发回调
      options.onAction(action.action)
    }
  }
  
  /**
   * 从错误消息中提取错误代码
   */
  static extractErrorCode(message) {
    if (!message) return null
    
    // 尝试匹配常见的错误模式
    const patterns = [
      /KOOK.*auth/i,
      /KOOK.*connect/i,
      /Discord.*webhook/i,
      /Telegram.*token/i,
      /Telegram.*chat/i,
      /Feishu.*app/i,
      /image.*download/i,
      /image.*upload/i,
      /network/i,
      /database/i
    ]
    
    for (const pattern of patterns) {
      if (pattern.test(message)) {
        // 简化实现，实际应该更精确
        if (/auth|login|cookie/i.test(message)) return 'KOOK_AUTH_FAILED'
        if (/connect|disconnect/i.test(message)) return 'KOOK_CONNECTION_LOST'
        if (/webhook/i.test(message)) return 'DISCORD_WEBHOOK_INVALID'
        if (/token/i.test(message)) return 'TELEGRAM_BOT_TOKEN_INVALID'
        if (/chat/i.test(message)) return 'TELEGRAM_CHAT_NOT_FOUND'
        if (/download/i.test(message)) return 'IMAGE_DOWNLOAD_FAILED'
        if (/upload/i.test(message)) return 'IMAGE_UPLOAD_FAILED'
        if (/network/i.test(message)) return 'NETWORK_ERROR'
        if (/database/i.test(message)) return 'DATABASE_ERROR'
      }
    }
    
    return null
  }
  
  /**
   * 记录错误日志
   */
  static logError(errorCode, errorMessage, errorDetails) {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      code: errorCode,
      message: errorMessage,
      details: errorDetails
    }
    
    // 发送到后端日志系统
    try {
      fetch('/api/logs/error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry)
      }).catch(err => {
        console.error('Failed to send error log:', err)
      })
    } catch (e) {
      // 忽略日志发送失败
    }
    
    // 同时输出到控制台
    console.error('[ErrorHandler]', logEntry)
  }
}

/**
 * 便捷方法
 */
export function handleError(error, options = {}) {
  ErrorHandler.handle(error, options)
}

export function showErrorDialog(error, options = {}) {
  ErrorHandler.handle(error, { ...options, mode: 'dialog' })
}

export function showErrorNotification(error, options = {}) {
  ErrorHandler.handle(error, { ...options, mode: 'notification' })
}

export function showErrorMessage(error, options = {}) {
  ErrorHandler.handle(error, { ...options, mode: 'message' })
}

/**
 * 全局错误处理器
 */
export function setupGlobalErrorHandler(app) {
  // Vue错误处理
  app.config.errorHandler = (err, instance, info) => {
    console.error('[Vue Error]', err, info)
    handleError(err, { mode: 'notification' })
  }
  
  // 未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('[Unhandled Promise]', event.reason)
    handleError(event.reason, { mode: 'notification' })
  })
  
  // 全局错误
  window.addEventListener('error', (event) => {
    console.error('[Global Error]', event.error)
    handleError(event.error, { mode: 'notification' })
  })
}
