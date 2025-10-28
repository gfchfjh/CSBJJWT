/**
 * 系统托盘管理器（终极版）
 * ✅ P1-3深度优化: 实时统计 + 快捷控制
 */

const { Tray, Menu, nativeImage, shell } = require('electron')
const path = require('path')
const axios = require('axios')

class TrayManagerUltimate {
  constructor(mainWindow) {
    this.mainWindow = mainWindow
    this.tray = null
    this.statsInterval = null
    
    // 统计数据
    this.stats = {
      today_total: 0,
      success_rate: 0,
      queue_size: 0,
      service_running: false,
      accounts_online: 0,
      accounts_total: 0
    }
    
    this.init()
    this.startStatsUpdate()
  }
  
  init() {
    /**
     * 初始化托盘图标
     */
    const iconPath = path.join(__dirname, '../public/icon.png')
    const icon = nativeImage.createFromPath(iconPath)
    
    this.tray = new Tray(icon.resize({ width: 16, height: 16 }))
    this.tray.setToolTip('KOOK消息转发系统')
    
    // 设置初始菜单
    this.updateMenu()
    
    // 点击托盘图标
    this.tray.on('click', () => {
      this.toggleMainWindow()
    })
    
    // 双击托盘图标
    this.tray.on('double-click', () => {
      this.mainWindow.show()
      this.mainWindow.focus()
    })
    
    console.log('✅ 托盘管理器已初始化')
  }
  
  async fetchStats() {
    /**
     * 🔥 从后端API获取实时统计
     */
    try {
      const response = await axios.get('http://localhost:9527/api/system/tray-stats', {
        timeout: 3000
      })
      
      this.stats = response.data
      this.updateMenu()
      
    } catch (error) {
      // 静默失败，不影响用户体验
      if (error.code !== 'ECONNREFUSED') {
        console.error('获取托盘统计失败:', error.message)
      }
    }
  }
  
  updateMenu() {
    /**
     * 更新托盘菜单（包含实时统计）
     */
    const serviceIcon = this.stats.service_running ? '✅' : '⏸️'
    const serviceLabel = this.stats.service_running ? '运行中' : '已停止'
    const successRate = this.stats.success_rate.toFixed(1)
    
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'KOOK消息转发系统',
        enabled: false,
        icon: this.getIconPath('icon16.png')
      },
      { type: 'separator' },
      
      // 📊 实时统计
      {
        label: '📊 今日统计',
        enabled: false
      },
      {
        label: `    转发: ${this.stats.today_total} 条`,
        enabled: false
      },
      {
        label: `    成功率: ${successRate}%`,
        enabled: false
      },
      {
        label: `    队列: ${this.stats.queue_size} 条`,
        enabled: false,
        click: () => {
          if (this.stats.queue_size > 0) {
            this.showLogsPage()
          }
        }
      },
      { type: 'separator' },
      
      // 服务状态
      {
        label: `服务: ${serviceIcon} ${serviceLabel}`,
        enabled: false
      },
      {
        label: `账号: ${this.stats.accounts_online}/${this.stats.accounts_total} 在线`,
        enabled: false
      },
      { type: 'separator' },
      
      // 🎮 快捷控制
      {
        label: '🎮 控制',
        submenu: [
          {
            label: this.stats.service_running ? '⏸️ 停止服务' : '▶️ 启动服务',
            click: () => this.toggleService()
          },
          {
            label: '🔄 重启服务',
            enabled: this.stats.service_running,
            click: () => this.restartService()
          },
          { type: 'separator' },
          {
            label: '🧪 测试转发',
            click: () => this.testForwarding()
          },
          {
            label: '🗑️ 清空队列',
            enabled: this.stats.queue_size > 0,
            click: () => this.clearQueue()
          }
        ]
      },
      
      // 📋 快捷导航
      {
        label: '📋 导航',
        submenu: [
          {
            label: '🏠 主页',
            click: () => this.navigateTo('/')
          },
          {
            label: '👤 账号管理',
            click: () => this.navigateTo('/accounts')
          },
          {
            label: '🤖 Bot配置',
            click: () => this.navigateTo('/bots')
          },
          {
            label: '🔀 频道映射',
            click: () => this.navigateTo('/mapping')
          },
          {
            label: '📝 实时日志',
            click: () => this.navigateTo('/logs')
          },
          {
            label: '⚙️ 系统设置',
            click: () => this.navigateTo('/settings')
          }
        ]
      },
      
      { type: 'separator' },
      
      // 显示/隐藏主窗口
      {
        label: '🏠 显示主窗口',
        click: () => {
          this.mainWindow.show()
          this.mainWindow.focus()
        }
      },
      
      // 帮助
      {
        label: '❓ 帮助',
        submenu: [
          {
            label: '📖 使用文档',
            click: () => {
              shell.openExternal('https://github.com/gfchfjh/CSBJJWT/blob/main/docs/用户手册.md')
            }
          },
          {
            label: '🐛 报告问题',
            click: () => {
              shell.openExternal('https://github.com/gfchfjh/CSBJJWT/issues')
            }
          },
          {
            label: '⭐ GitHub',
            click: () => {
              shell.openExternal('https://github.com/gfchfjh/CSBJJWT')
            }
          }
        ]
      },
      
      { type: 'separator' },
      
      // 退出
      {
        label: '❌ 退出程序',
        click: () => {
          this.mainWindow.webContents.send('app-quit')
        }
      }
    ])
    
    this.tray.setContextMenu(contextMenu)
    
    // 🔥 更新托盘图标提示文本（显示实时数据）
    this.tray.setToolTip(
      `KOOK消息转发系统\n` +
      `━━━━━━━━━━━━━━━\n` +
      `状态: ${serviceLabel}\n` +
      `今日: ${this.stats.today_total}条\n` +
      `成功率: ${successRate}%\n` +
      `队列: ${this.stats.queue_size}条\n` +
      `账号: ${this.stats.accounts_online}/${this.stats.accounts_total}`
    )
  }
  
  getIconPath(iconName) {
    return path.join(__dirname, '../public', iconName)
  }
  
  toggleMainWindow() {
    if (this.mainWindow.isVisible()) {
      this.mainWindow.hide()
    } else {
      this.mainWindow.show()
      this.mainWindow.focus()
    }
  }
  
  async toggleService() {
    try {
      const endpoint = this.stats.service_running ?
        'http://localhost:9527/api/system/stop' :
        'http://localhost:9527/api/system/start'
      
      await axios.post(endpoint, {}, { timeout: 5000 })
      
      setTimeout(() => this.fetchStats(), 1000)
      
    } catch (error) {
      console.error('切换服务失败:', error.message)
    }
  }
  
  async restartService() {
    try {
      await axios.post('http://localhost:9527/api/system/restart', {}, { timeout: 5000 })
      
      setTimeout(() => this.fetchStats(), 2000)
      
    } catch (error) {
      console.error('重启服务失败:', error.message)
    }
  }
  
  async testForwarding() {
    try {
      await axios.post('http://localhost:9527/api/system/test-forward', {}, { timeout: 10000 })
      
      this.showNotification('success', '测试成功', '测试消息已发送')
      
    } catch (error) {
      this.showNotification('error', '测试失败', error.message)
    }
  }
  
  async clearQueue() {
    try {
      await axios.post('http://localhost:9527/api/queue/clear', {}, { timeout: 5000 })
      
      this.showNotification('success', '队列已清空', '')
      setTimeout(() => this.fetchStats(), 1000)
      
    } catch (error) {
      this.showNotification('error', '清空失败', error.message)
    }
  }
  
  navigateTo(route) {
    this.mainWindow.show()
    this.mainWindow.focus()
    this.mainWindow.webContents.send('navigate-to', route)
  }
  
  showLogsPage() {
    this.navigateTo('/logs?filter=pending')
  }
  
  showNotification(type, title, body) {
    const { Notification } = require('electron')
    
    const notification = new Notification({
      title: title,
      body: body,
      icon: this.getIconPath('icon.png')
    })
    
    notification.show()
  }
  
  startStatsUpdate() {
    /**
     * 启动定时刷新统计（每5秒）
     */
    this.fetchStats()
    
    this.statsInterval = setInterval(() => {
      this.fetchStats()
    }, 5000)
    
    console.log('⏰ 托盘统计自动刷新已启动（每5秒）')
  }
  
  stopStatsUpdate() {
    if (this.statsInterval) {
      clearInterval(this.statsInterval)
      this.statsInterval = null
      console.log('⏰ 托盘统计刷新已停止')
    }
  }
  
  destroy() {
    this.stopStatsUpdate()
    
    if (this.tray) {
      this.tray.destroy()
      this.tray = null
      console.log('🗑️ 托盘已清理')
    }
  }
}

module.exports = TrayManagerUltimate
