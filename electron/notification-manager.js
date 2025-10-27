/**
 * Electron桌面通知管理器
 * 功能：
 * - 智能通知分类
 * - 静音时段支持
 * - 通知历史记录
 * - 点击跳转功能
 */

const { Notification, app } = require('electron')
const path = require('path')

class NotificationManager {
  constructor() {
    this.notificationHistory = []
    this.maxHistory = 100
    this.soundEnabled = true
    this.quietHours = {
      enabled: false,
      start: 22,  // 22:00
      end: 7      // 7:00
    }
    
    // 通知统计
    this.stats = {
      total: 0,
      byType: {
        success: 0,
        warning: 0,
        error: 0,
        info: 0
      }
    }
  }

  /**
   * 发送桌面通知
   * 
   * @param {Object} options
   * @param {string} options.title - 标题
   * @param {string} options.body - 内容
   * @param {string} options.type - 类型: success/warning/error/info
   * @param {string} options.urgency - 优先级: low/normal/critical
   * @param {Function} options.onClick - 点击回调
   * @param {boolean} options.silent - 是否静音
   */
  send(options) {
    // 检查是否在静音时段
    if (this.isInQuietHours() && options.urgency !== 'critical') {
      console.log('[通知] 当前处于静音时段，跳过通知')
      return null
    }

    const {
      title = 'KOOK转发系统',
      body,
      type = 'info',
      urgency = 'normal',
      onClick,
      silent = false
    } = options

    // 根据类型选择图标和声音
    const iconPath = this.getIconForType(type)
    const sound = (this.soundEnabled && !silent) ? this.getSoundForType(type) : null

    // 创建通知
    const notification = new Notification({
      title,
      body,
      icon: iconPath,
      urgency,
      sound,
      timeoutType: urgency === 'critical' ? 'never' : 'default',
      silent: silent || !this.soundEnabled
    })

    // 点击事件
    if (onClick) {
      notification.on('click', () => {
        console.log('[通知] 用户点击通知:', title)
        onClick()
      })
    }

    // 关闭事件
    notification.on('close', () => {
      console.log('[通知] 通知已关闭:', title)
    })

    // 记录历史
    const record = {
      title,
      body,
      type,
      urgency,
      timestamp: Date.now(),
      clicked: false
    }
    
    this.notificationHistory.push(record)

    // 限制历史记录数量
    if (this.notificationHistory.length > this.maxHistory) {
      this.notificationHistory.shift()
    }

    // 更新统计
    this.stats.total++
    this.stats.byType[type] = (this.stats.byType[type] || 0) + 1

    // 显示通知
    notification.show()
    
    console.log(`[通知] 已发送${type}通知:`, title)
    
    return notification
  }

  /**
   * 发送成功通知
   */
  success(title, body, onClick) {
    return this.send({
      title,
      body,
      type: 'success',
      urgency: 'low',
      onClick
    })
  }

  /**
   * 发送警告通知
   */
  warning(title, body, onClick) {
    return this.send({
      title,
      body,
      type: 'warning',
      urgency: 'normal',
      onClick
    })
  }

  /**
   * 发送错误通知
   */
  error(title, body, onClick) {
    return this.send({
      title,
      body,
      type: 'error',
      urgency: 'critical',
      onClick
    })
  }

  /**
   * 发送信息通知
   */
  info(title, body, onClick) {
    return this.send({
      title,
      body,
      type: 'info',
      urgency: 'normal',
      onClick
    })
  }

  /**
   * 批量发送通知（防止通知轰炸）
   * 
   * @param {Array} notifications - 通知数组
   * @param {number} delay - 每条通知间隔（毫秒）
   */
  async sendBatch(notifications, delay = 1000) {
    for (const notif of notifications) {
      this.send(notif)
      
      if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  /**
   * 根据类型获取图标
   */
  getIconForType(type) {
    const iconMap = {
      success: 'icon-success.png',
      warning: 'icon-warning.png',
      error: 'icon-error.png',
      info: 'icon-info.png'
    }

    const iconFile = iconMap[type] || iconMap.info
    
    // 尝试多个可能的路径
    const possiblePaths = [
      path.join(__dirname, '../public/icons', iconFile),
      path.join(__dirname, '../build/icons', iconFile),
      path.join(__dirname, '../frontend/public/icons', iconFile),
      path.join(app.getAppPath(), 'public/icons', iconFile)
    ]

    // 返回第一个存在的路径
    const fs = require('fs')
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        return p
      }
    }

    // 如果都不存在，返回默认图标
    return path.join(__dirname, '../build/icon.png')
  }

  /**
   * 根据类型获取提示音
   */
  getSoundForType(type) {
    if (process.platform !== 'darwin') {
      // Windows和Linux使用默认提示音
      return null
    }

    // macOS系统提示音
    const soundMap = {
      success: 'Ping',
      warning: 'Basso',
      error: 'Sosumi',
      info: 'Pop'
    }

    return soundMap[type] || null
  }

  /**
   * 检查是否在静音时段
   */
  isInQuietHours() {
    if (!this.quietHours.enabled) {
      return false
    }

    const now = new Date()
    const hour = now.getHours()
    const { start, end } = this.quietHours

    if (start < end) {
      // 同一天的时间段，例如: 8:00 - 18:00
      return hour >= start && hour < end
    } else {
      // 跨日的时间段，例如: 22:00 - 7:00
      return hour >= start || hour < end
    }
  }

  /**
   * 设置静音时段
   */
  setQuietHours(enabled, start, end) {
    this.quietHours = { enabled, start, end }
    console.log('[通知] 静音时段设置:', this.quietHours)
  }

  /**
   * 设置是否启用声音
   */
  setSoundEnabled(enabled) {
    this.soundEnabled = enabled
    console.log('[通知] 声音已', enabled ? '启用' : '禁用')
  }

  /**
   * 获取通知历史
   */
  getHistory(limit = 50) {
    return this.notificationHistory.slice(-limit)
  }

  /**
   * 清空通知历史
   */
  clearHistory() {
    this.notificationHistory = []
    console.log('[通知] 历史记录已清空')
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      ...this.stats,
      historyCount: this.notificationHistory.length,
      quietHoursActive: this.isInQuietHours()
    }
  }

  /**
   * 测试通知
   */
  test() {
    this.send({
      title: '🔔 通知测试',
      body: '如果您看到这条消息，说明通知功能正常工作！',
      type: 'info',
      urgency: 'normal'
    })
  }
}

// 创建全局实例
const notificationManager = new NotificationManager()

module.exports = notificationManager
