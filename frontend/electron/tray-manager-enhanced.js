/**
 * ✅ P0-4深度优化：Electron托盘管理器（增强版）
 * 
 * 功能：
 * - 4种动态状态图标（在线/重连/错误/离线）
 * - 实时统计菜单
 * - 快捷操作
 * - 定时更新
 */

const { Tray, Menu, nativeImage, app } = require('electron')
const path = require('path')
const axios = require('axios')

class TrayManagerEnhanced {
  constructor(mainWindow) {
    this.mainWindow = mainWindow
    this.tray = null
    this.updateInterval = null
    
    // 统计信息
    this.stats = {
      status: 'offline',
      todayTotal: 0,
      successRate: 0,
      queueSize: 0,
      onlineAccounts: 0,
      activeBots: 0,
      uptime: 0
    }
    
    // 后端API地址
    this.apiBase = 'http://localhost:9527'
    
    this.init()
  }
  
  init() {
    try {
      // 创建托盘图标
      const iconPath = this.getIconPath('offline')
      this.tray = new Tray(nativeImage.createFromPath(iconPath))
      
      this.tray.setToolTip('KOOK消息转发系统')
      
      // 初始化菜单
      this.updateContextMenu()
      
      // 点击托盘图标
      this.tray.on('click', () => {
        if (this.mainWindow.isVisible()) {
          this.mainWindow.hide()
        } else {
          this.mainWindow.show()
          this.mainWindow.focus()
        }
      })
      
      // 启动定时更新（每5秒）
      this.startAutoUpdate()
      
      console.log('✅ 托盘管理器已初始化')
    } catch (error) {
      console.error('❌ 托盘管理器初始化失败:', error)
    }
  }
  
  /**
   * 获取图标路径（4种状态）
   */
  getIconPath(status) {
    const iconMap = {
      'online': 'icon-green.png',       // 在线（绿色）
      'reconnecting': 'icon-yellow.png', // 重连中（黄色）
      'error': 'icon-red.png',          // 错误（红色）
      'offline': 'icon-gray.png'        // 离线（灰色）
    }
    
    const iconFile = iconMap[status] || 'icon-gray.png'
    const iconPath = path.join(__dirname, '../build/icons', iconFile)
    
    // 如果图标文件不存在，使用默认图标
    const fs = require('fs')
    if (!fs.existsSync(iconPath)) {
      console.warn(`图标文件不存在: ${iconPath}，使用默认图标`)
      return path.join(__dirname, '../build/icon.png')
    }
    
    return iconPath
  }
  
  /**
   * 启动自动更新
   */
  startAutoUpdate() {
    // 立即更新一次
    this.fetchStats()
    
    // 定时更新（每5秒）
    this.updateInterval = setInterval(() => {
      this.fetchStats()
    }, 5000)
  }
  
  /**
   * 停止自动更新
   */
  stopAutoUpdate() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
      this.updateInterval = null
    }
  }
  
  /**
   * 从后端获取统计信息
   */
  async fetchStats() {
    try {
      const response = await axios.get(`${this.apiBase}/api/system/stats`, {
        timeout: 3000
      })
      
      const data = response.data
      
      // 更新统计信息
      this.stats = {
        status: data.service_running ? 'online' : 'offline',
        todayTotal: data.today_total || 0,
        successRate: data.success_rate || 0,
        queueSize: data.queue_size || 0,
        onlineAccounts: data.online_accounts || 0,
        activeBots: data.active_bots || 0,
        uptime: data.uptime || 0
      }
      
      // 更新托盘图标
      this.updateIcon(this.stats.status)
      
      // 更新右键菜单
      this.updateContextMenu()
      
    } catch (error) {
      // 连接失败，设置为错误状态
      this.stats.status = 'error'
      this.updateIcon('error')
      this.updateContextMenu()
    }
  }
  
  /**
   * 更新托盘图标
   */
  updateIcon(status) {
    try {
      const iconPath = this.getIconPath(status)
      this.tray.setImage(nativeImage.createFromPath(iconPath))
      
      // 更新Tooltip
      const statusText = {
        'online': '🟢 运行中',
        'reconnecting': '🟡 重连中',
        'error': '🔴 错误',
        'offline': '⚪ 离线'
      }[status] || '⚪ 离线'
      
      this.tray.setToolTip(`KOOK消息转发系统 - ${statusText}`)
    } catch (error) {
      console.error('更新托盘图标失败:', error)
    }
  }
  
  /**
   * 更新右键菜单
   */
  updateContextMenu() {
    try {
      const isRunning = this.stats.status === 'online'
      
      const contextMenu = Menu.buildFromTemplate([
        // 状态显示
        {
          label: `📊 今日转发: ${this.stats.todayTotal} 条`,
          enabled: false
        },
        {
          label: `✅ 成功率: ${this.stats.successRate}%`,
          enabled: false
        },
        {
          label: `⏳ 队列: ${this.stats.queueSize} 条`,
          enabled: false
        },
        { type: 'separator' },
        
        // 详细信息
        {
          label: `👤 在线账号: ${this.stats.onlineAccounts} 个`,
          enabled: false
        },
        {
          label: `🤖 活跃Bot: ${this.stats.activeBots} 个`,
          enabled: false
        },
        {
          label: `⏱️ 运行时长: ${this.formatUptime(this.stats.uptime)}`,
          enabled: false
        },
        { type: 'separator' },
        
        // 快捷操作
        {
          label: isRunning ? '⏸️ 停止服务' : '▶️ 启动服务',
          click: () => this.toggleService()
        },
        {
          label: '🔄 重启服务',
          enabled: isRunning,
          click: () => this.restartService()
        },
        {
          label: '🧪 测试转发',
          enabled: isRunning,
          click: () => this.testForwarding()
        },
        { type: 'separator' },
        
        // 窗口控制
        {
          label: '📱 显示主窗口',
          click: () => {
            this.mainWindow.show()
            this.mainWindow.focus()
          }
        },
        {
          label: '⚙️ 设置',
          click: () => {
            this.mainWindow.show()
            this.mainWindow.focus()
            this.mainWindow.webContents.send('navigate', '/settings')
          }
        },
        {
          label: '📋 日志',
          click: () => {
            this.mainWindow.show()
            this.mainWindow.focus()
            this.mainWindow.webContents.send('navigate', '/logs')
          }
        },
        { type: 'separator' },
        
        // 退出
        {
          label: '❌ 退出',
          click: () => {
            this.stopAutoUpdate()
            app.quit()
          }
        }
      ])
      
      this.tray.setContextMenu(contextMenu)
    } catch (error) {
      console.error('更新托盘菜单失败:', error)
    }
  }
  
  /**
   * 切换服务状态
   */
  async toggleService() {
    try {
      const isRunning = this.stats.status === 'online'
      const endpoint = isRunning ? '/api/system/stop' : '/api/system/start'
      
      await axios.post(`${this.apiBase}${endpoint}`)
      
      // 等待1秒后刷新统计
      setTimeout(() => {
        this.fetchStats()
      }, 1000)
      
    } catch (error) {
      console.error('切换服务状态失败:', error)
    }
  }
  
  /**
   * 重启服务
   */
  async restartService() {
    try {
      await axios.post(`${this.apiBase}/api/system/restart`)
      
      // 等待2秒后刷新统计
      setTimeout(() => {
        this.fetchStats()
      }, 2000)
      
    } catch (error) {
      console.error('重启服务失败:', error)
    }
  }
  
  /**
   * 测试转发
   */
  async testForwarding() {
    try {
      await axios.post(`${this.apiBase}/api/system/test-forwarding`)
      
      // 显示主窗口并跳转到日志页面
      this.mainWindow.show()
      this.mainWindow.focus()
      this.mainWindow.webContents.send('navigate', '/logs')
      
    } catch (error) {
      console.error('测试转发失败:', error)
    }
  }
  
  /**
   * 格式化运行时长
   */
  formatUptime(seconds) {
    if (!seconds || seconds < 0) return '0秒'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    const parts = []
    if (hours > 0) parts.push(`${hours}小时`)
    if (minutes > 0) parts.push(`${minutes}分钟`)
    if (secs > 0 || parts.length === 0) parts.push(`${secs}秒`)
    
    return parts.join('')
  }
  
  /**
   * 销毁托盘
   */
  destroy() {
    this.stopAutoUpdate()
    
    if (this.tray) {
      this.tray.destroy()
      this.tray = null
    }
  }
}

module.exports = TrayManagerEnhanced
