/**
 * 错误消息本地化模块
 * 将技术性错误转换为用户友好的提示信息
 */

export const ERROR_MESSAGES = {
  // Cookie相关错误
  'COOKIE_EXPIRED': {
    title: '登录信息已过期',
    message: 'KOOK登录信息已失效，请重新登录',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. 点击「重新登录」按钮',
      '2. 或使用Chrome扩展重新导出Cookie',
      '3. 如多次失效，请检查浏览器Cookie设置'
    ],
    actionButton: {
      text: '重新登录',
      action: 'relogin'
    }
  },

  'COOKIE_INVALID': {
    title: 'Cookie格式错误',
    message: '您输入的Cookie格式不正确',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 使用Chrome扩展一键导出（推荐）',
      '2. 确保完整复制Cookie内容',
      '3. 检查是否包含特殊字符',
      '4. 查看Cookie获取教程'
    ],
    actionButton: {
      text: '查看教程',
      action: 'showCookieGuide'
    }
  },

  'COOKIE_MISSING': {
    title: '未找到Cookie',
    message: '请先导入KOOK的Cookie信息',
    icon: 'info',
    type: 'info',
    solutions: [
      '1. 点击「导入Cookie」按钮',
      '2. 从浏览器复制Cookie',
      '3. 或使用Chrome扩展一键导出'
    ],
    actionButton: {
      text: '导入Cookie',
      action: 'showCookieImport'
    }
  },

  // 网络相关错误
  'NETWORK_ERROR': {
    title: '网络连接异常',
    message: '无法连接到KOOK服务器',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查网络连接是否正常',
      '2. 尝试关闭VPN或代理',
      '3. 检查防火墙设置',
      '4. 稍后再试'
    ],
    actionButton: {
      text: '重试',
      action: 'retry'
    }
  },

  'TIMEOUT_ERROR': {
    title: '连接超时',
    message: '请求超时，服务器响应缓慢',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. 检查网络速度',
      '2. 重试连接',
      '3. 更换网络环境'
    ],
    actionButton: {
      text: '重试',
      action: 'retry'
    }
  },

  'SERVER_ERROR': {
    title: '服务器错误',
    message: 'KOOK服务器返回错误，请稍后重试',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 等待5-10分钟后重试',
      '2. 检查KOOK官方状态',
      '3. 如持续失败，请联系支持'
    ],
    actionButton: {
      text: '查看状态',
      action: 'checkStatus'
    }
  },

  // 账号相关错误
  'ACCOUNT_BANNED': {
    title: '账号已被封禁',
    message: '您的KOOK账号可能被封禁',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查KOOK账号状态',
      '2. 联系KOOK客服了解情况',
      '3. 更换其他账号尝试'
    ],
    actionButton: {
      text: '联系客服',
      action: 'contactSupport'
    }
  },

  'ACCOUNT_OFFLINE': {
    title: '账号离线',
    message: 'KOOK账号显示离线状态',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. Cookie已过期 → 重新登录',
      '2. IP被限制 → 更换网络或使用代理',
      '3. 账号异常 → 检查KOOK账号状态'
    ],
    actionButton: {
      text: '诊断问题',
      action: 'diagnose'
    }
  },

  // Bot配置错误
  'DISCORD_WEBHOOK_INVALID': {
    title: 'Discord Webhook无效',
    message: 'Discord Webhook URL格式不正确或已失效',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查Webhook URL是否完整',
      '2. 确认Webhook未被删除',
      '3. 重新创建Webhook',
      '4. 查看Discord配置教程'
    ],
    actionButton: {
      text: '查看教程',
      action: 'showDiscordGuide'
    }
  },

  'TELEGRAM_BOT_ERROR': {
    title: 'Telegram Bot错误',
    message: 'Telegram Bot Token无效或权限不足',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查Bot Token是否正确',
      '2. 确认Bot已添加到群组',
      '3. 检查Bot权限设置',
      '4. 重新获取Chat ID'
    ],
    actionButton: {
      text: '查看教程',
      action: 'showTelegramGuide'
    }
  },

  'FEISHU_APP_ERROR': {
    title: '飞书应用错误',
    message: '飞书App ID或Secret配置错误',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查App ID和Secret是否正确',
      '2. 确认应用已发布',
      '3. 检查应用权限',
      '4. 查看飞书配置教程'
    ],
    actionButton: {
      text: '查看教程',
      action: 'showFeishuGuide'
    }
  },

  // 转发相关错误
  'RATE_LIMIT': {
    title: 'API限流',
    message: '发送速度过快，触发了平台限流',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. 消息会自动排队等待',
      '2. 不会丢失任何消息',
      '3. 请耐心等待队列消化',
      '4. 建议减少映射数量'
    ],
    actionButton: {
      text: '查看队列',
      action: 'showQueue'
    }
  },

  'MESSAGE_TOO_LONG': {
    title: '消息过长',
    message: '消息内容超出目标平台限制',
    icon: 'info',
    type: 'info',
    solutions: [
      '1. 消息已自动分段发送',
      '2. Discord限制：2000字符',
      '3. Telegram限制：4096字符',
      '4. 飞书限制：5000字符'
    ]
  },

  'IMAGE_UPLOAD_FAILED': {
    title: '图片上传失败',
    message: '图片上传到目标平台失败',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 自动切换到图床模式重试',
      '2. 检查图片大小（限制10MB）',
      '3. 检查网络连接',
      '4. 查看图片处理设置'
    ],
    actionButton: {
      text: '查看设置',
      action: 'showImageSettings'
    }
  },

  'FILE_TOO_LARGE': {
    title: '文件过大',
    message: '附件文件超过大小限制',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. 当前限制：50MB',
      '2. 建议使用文件分享链接',
      '3. 或压缩后重新上传'
    ]
  },

  'FILE_DANGEROUS': {
    title: '文件被拦截',
    message: '检测到危险文件类型，已拦截',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 禁止转发可执行文件（.exe, .bat等）',
      '2. 禁止转发脚本文件（.js, .vbs等）',
      '3. 如需转发，请添加到白名单',
      '4. 查看文件安全设置'
    ],
    actionButton: {
      text: '文件安全设置',
      action: 'showFileSecurity'
    }
  },

  // 服务相关错误
  'REDIS_CONNECTION_FAILED': {
    title: 'Redis连接失败',
    message: '消息队列服务连接失败',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查Redis服务是否运行',
      '2. 尝试重启应用',
      '3. 检查端口6379是否被占用',
      '4. 查看日志获取详细信息'
    ],
    actionButton: {
      text: '重启服务',
      action: 'restartService'
    }
  },

  'DATABASE_ERROR': {
    title: '数据库错误',
    message: '配置数据库操作失败',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 检查磁盘空间是否充足',
      '2. 尝试重启应用',
      '3. 如持续失败，可能需要重置数据库',
      '4. 建议先备份配置'
    ],
    actionButton: {
      text: '备份配置',
      action: 'backup'
    }
  },

  'MEMORY_LIMIT': {
    title: '内存使用过高',
    message: '应用内存使用超过限制',
    icon: 'warning',
    type: 'warning',
    solutions: [
      '1. 已自动清理缓存',
      '2. 建议减少并发任务',
      '3. 考虑重启应用释放内存',
      '4. 可在设置中调整内存限制'
    ],
    actionButton: {
      text: '查看内存',
      action: 'showMemory'
    }
  },

  // 浏览器相关错误
  'BROWSER_CRASHED': {
    title: '浏览器崩溃',
    message: '用于监听KOOK的浏览器进程崩溃',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 正在自动重启浏览器...',
      '2. 如多次崩溃，请重启应用',
      '3. 检查系统资源是否充足',
      '4. 建议减少同时监听的账号数'
    ],
    actionButton: {
      text: '查看日志',
      action: 'showLogs'
    }
  },

  // 映射相关错误
  'NO_MAPPING': {
    title: '未配置映射',
    message: '该频道未配置转发映射',
    icon: 'info',
    type: 'info',
    solutions: [
      '1. 前往「频道映射」页面配置',
      '2. 使用「智能映射」功能自动创建',
      '3. 或手动创建映射规则'
    ],
    actionButton: {
      text: '配置映射',
      action: 'gotoMapping'
    }
  },

  // 通用错误
  'UNKNOWN_ERROR': {
    title: '未知错误',
    message: '发生了未知错误',
    icon: 'error',
    type: 'error',
    solutions: [
      '1. 尝试重启应用',
      '2. 查看日志了解详情',
      '3. 如持续发生，请提交Issue',
      '4. 附带错误日志以便排查'
    ],
    actionButton: {
      text: '查看日志',
      action: 'showLogs'
    }
  }
};

/**
 * 根据错误代码或错误信息获取友好提示
 * @param {Error|string} error - 错误对象或错误代码
 * @returns {Object} 友好错误信息
 */
export function getErrorMessage(error) {
  // 如果是字符串，直接作为错误代码
  if (typeof error === 'string') {
    return ERROR_MESSAGES[error] || ERROR_MESSAGES['UNKNOWN_ERROR'];
  }

  // 如果是Error对象，尝试从message中提取错误代码
  if (error instanceof Error) {
    const message = error.message;

    // 匹配常见错误模式
    if (message.includes('cookie') && message.includes('expired')) {
      return ERROR_MESSAGES['COOKIE_EXPIRED'];
    }
    if (message.includes('cookie') && message.includes('invalid')) {
      return ERROR_MESSAGES['COOKIE_INVALID'];
    }
    if (message.includes('network') || message.includes('ENOTFOUND')) {
      return ERROR_MESSAGES['NETWORK_ERROR'];
    }
    if (message.includes('timeout') || message.includes('ETIMEDOUT')) {
      return ERROR_MESSAGES['TIMEOUT_ERROR'];
    }
    if (message.includes('webhook') && message.includes('invalid')) {
      return ERROR_MESSAGES['DISCORD_WEBHOOK_INVALID'];
    }
    if (message.includes('rate limit') || message.includes('429')) {
      return ERROR_MESSAGES['RATE_LIMIT'];
    }
    if (message.includes('too long') || message.includes('2000')) {
      return ERROR_MESSAGES['MESSAGE_TOO_LONG'];
    }
    if (message.includes('redis')) {
      return ERROR_MESSAGES['REDIS_CONNECTION_FAILED'];
    }
    if (message.includes('database')) {
      return ERROR_MESSAGES['DATABASE_ERROR'];
    }

    // 默认未知错误
    return {
      ...ERROR_MESSAGES['UNKNOWN_ERROR'],
      message: message // 保留原始错误信息
    };
  }

  return ERROR_MESSAGES['UNKNOWN_ERROR'];
}

/**
 * 格式化错误信息为HTML
 * @param {Object} errorInfo - 错误信息对象
 * @returns {string} HTML字符串
 */
export function formatErrorHTML(errorInfo) {
  const { title, message, solutions, actionButton } = errorInfo;

  let html = `<div class="error-detail">`;
  html += `<h3>${title}</h3>`;
  html += `<p>${message}</p>`;

  if (solutions && solutions.length > 0) {
    html += `<div class="solutions">`;
    html += `<strong>💡 解决方案：</strong>`;
    html += `<ul>`;
    solutions.forEach(solution => {
      html += `<li>${solution}</li>`;
    });
    html += `</ul>`;
    html += `</div>`;
  }

  html += `</div>`;

  return html;
}

/**
 * 显示用户友好的错误对话框
 * @param {Error|string} error - 错误对象或错误代码
 * @param {Object} ElMessageBox - Element Plus的MessageBox组件
 * @returns {Promise} 用户操作结果
 */
export async function showFriendlyError(error, ElMessageBox) {
  const errorInfo = getErrorMessage(error);
  const html = formatErrorHTML(errorInfo);

  const options = {
    title: errorInfo.icon === 'error' ? '❌ ' + errorInfo.title :
           errorInfo.icon === 'warning' ? '⚠️ ' + errorInfo.title :
           errorInfo.icon === 'info' ? 'ℹ️ ' + errorInfo.title :
           errorInfo.title,
    dangerouslyUseHTMLString: true,
    message: html,
    type: errorInfo.type,
    confirmButtonText: errorInfo.actionButton ? errorInfo.actionButton.text : '知道了',
    showCancelButton: !!errorInfo.actionButton,
    cancelButtonText: '关闭'
  };

  try {
    await ElMessageBox(options);
    // 如果有操作按钮，返回action
    return errorInfo.actionButton ? errorInfo.actionButton.action : null;
  } catch {
    // 用户取消
    return null;
  }
}

export default {
  ERROR_MESSAGES,
  getErrorMessage,
  formatErrorHTML,
  showFriendlyError
};
