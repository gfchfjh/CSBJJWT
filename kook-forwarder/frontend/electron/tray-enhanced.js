/**
 * 系统托盘增强版（✨ P1-3优化）
 * 功能：动态图标、实时统计、快捷操作
 */
const { Tray, Menu, nativeImage, shell } = require('electron')
const path = require('path')
const axios = require('axios')

class TrayManagerEnhanced {
  constructor(mainWindow) {
    this.mainWindow = mainWindow
    this.tray = null
    this.stats = {
      serviceRunning: false,
      todayMessages: 0,
      avgLatency: 0,
      queueSize: 0,
      activeAccounts: 0,
      activeBots: 0,
      uptime: 0
    }
    
    // 定时更新统计（每5秒）
    this.statsInterval = null
  }
  
  /**
   * 初始化托盘
   */
  init() {
    // 创建托盘图标
    this.updateTrayIcon('offline')
    
    // 创建托盘菜单
    this.updateMenu()
    
    // 开始定时更新统计
    this.startStatsUpdate()
    
    // 托盘点击事件
    this.tray.on('click', () => {
      this.mainWindow.show()
    })
  }
  
  /**
   * 更新托盘图标（✨ P1-3核心功能：动态图标）
   * 
   * @param {string} status - 'online' | 'connecting' | 'error' | 'offline'
   */
  updateTrayIcon(status) {
    let iconPath
    
    switch (status) {
      case 'online':
        iconPath = path.join(__dirname, '../public/tray-icon-online.png')
        break
      case 'connecting':
        iconPath = path.join(__dirname, '../public/tray-icon-connecting.png')
        break
      case 'error':
        iconPath = path.join(__dirname, '../public/tray-icon-error.png')
        break
      case 'offline':
      default:
        iconPath = path.join(__dirname, '../public/tray-icon-offline.png')
        break
    }
    
    // 如果图标不存在，使用默认图标
    try {
      const icon = nativeImage.createFromPath(iconPath)
      
      if (!this.tray) {
        this.tray = new Tray(icon)
        this.tray.setToolTip('KOOK消息转发系统')
      } else {
        this.tray.setImage(icon)
      }
    } catch (error) {
      console.error('更新托盘图标失败:', error)
      // 使用默认图标
      const defaultIcon = path.join(__dirname, '../public/icon.png')
      const icon = nativeImage.createFromPath(defaultIcon)
      
      if (!this.tray) {
        this.tray = new Tray(icon)
      } else {
        this.tray.setImage(icon)
      }
    }
  }
  
  /**
   * 更新托盘菜单（✨ P1-3核心功能：实时统计）
   */
  updateMenu() {
    const template = [
      {
        label: 'KOOK消息转发系统',
        enabled: false
      },
      {
        type: 'separator'
      },
      {
        label: `状态: ${this.stats.serviceRunning ? '🟢 运行中' : '🔴 已停止'}`,
        enabled: false
      },
      {
        label: `今日消息: ${this.stats.todayMessages} 条`,
        enabled: false
      },
      {
        label: `平均延迟: ${this.stats.avgLatency} ms`,
        enabled: false
      },
      {
        label: `队列大小: ${this.stats.queueSize}`,
        enabled: false
      },
      {
        label: `活跃账号: ${this.stats.activeAccounts}`,
        enabled: false
      },
      {
        label: `活跃Bot: ${this.stats.activeBots}`,
        enabled: false
      },
      {
        label: `运行时长: ${this.formatUptime(this.stats.uptime)}`,
        enabled: false
      },
      {
        type: 'separator'
      },
      {
        label: '📱 显示窗口',
        click: () => {
          this.mainWindow.show()
        }
      },
      {
        type: 'separator'
      },
      {
        label: '▶️  启动服务',
        enabled: !this.stats.serviceRunning,
        click: async () => {
          await this.startService()
        }
      },
      {
        label: '⏸️  停止服务',
        enabled: this.stats.serviceRunning,
        click: async () => {
          await this.stopService()
        }
      },
      {
        label: '🔄 重启服务',
        click: async () => {
          await this.restartService()
        }
      },
      {
        type: 'separator'
      },
      {
        label: '📂 打开日志文件夹',
        click: () => {
          const logsPath = path.join(process.cwd(), 'logs')
          shell.openPath(logsPath)
        }
      },
      {
        label: '📂 打开配置文件夹',
        click: () => {
          const configPath = path.join(process.cwd(), 'data')
          shell.openPath(configPath)
        }
      },
      {
        type: 'separator'
      },
      {
        label: '❌ 退出',
        click: () => {
          this.quit()
        }
      }
    ]
    
    const contextMenu = Menu.buildFromTemplate(template)
    this.tray.setContextMenu(contextMenu)
  }
  
  /**
   * 开始统计更新（✨ P1-3核心功能：5秒自动刷新）
   */
  startStatsUpdate() {
    // 立即更新一次
    this.updateStats()
    
    // 每5秒更新一次
    this.statsInterval = setInterval(() => {
      this.updateStats()
    }, 5000)
  }
  
  /**
   * 停止统计更新
   */
  stopStatsUpdate() {
    if (this.statsInterval) {
      clearInterval(this.statsInterval)
      this.statsInterval = null
    }
  }
  
  /**
   * 更新统计数据
   */
  async updateStats() {
    try {
      const response = await axios.get('http://localhost:9527/api/tray-stats')
      const data = response.data
      
      this.stats = {
        serviceRunning: data.service_running,
        todayMessages: data.today_messages,
        avgLatency: data.avg_latency,
        queueSize: data.queue_size,
        activeAccounts: data.active_accounts,
        activeBots: data.active_bots,
        uptime: data.uptime
      }
      
      // 根据服务状态更新图标
      if (this.stats.serviceRunning) {
        this.updateTrayIcon('online')
      } else {
        this.updateTrayIcon('offline')
      }
      
      // 更新菜单
      this.updateMenu()
      
    } catch (error) {
      console.error('更新托盘统计失败:', error)
      // 出错时显示错误图标
      this.updateTrayIcon('error')
    }
  }
  
  /**
   * 启动服务
   */
  async startService() {
    try {
      this.updateTrayIcon('connecting')
      await axios.post('http://localhost:9527/api/system/start')
      
      setTimeout(() => {
        this.updateStats()
      }, 1000)
    } catch (error) {
      console.error('启动服务失败:', error)
      this.updateTrayIcon('error')
    }
  }
  
  /**
   * 停止服务
   */
  async stopService() {
    try {
      await axios.post('http://localhost:9527/api/system/stop')
      
      setTimeout(() => {
        this.updateStats()
      }, 1000)
    } catch (error) {
      console.error('停止服务失败:', error)
    }
  }
  
  /**
   * 重启服务
   */
  async restartService() {
    try {
      this.updateTrayIcon('connecting')
      await axios.post('http://localhost:9527/api/system/restart')
      
      setTimeout(() => {
        this.updateStats()
      }, 2000)
    } catch (error) {
      console.error('重启服务失败:', error)
      this.updateTrayIcon('error')
    }
  }
  
  /**
   * 格式化运行时长
   */
  formatUptime(seconds) {
    if (!seconds) return '0分钟'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`
    }
    return `${minutes}分钟`
  }
  
  /**
   * 退出应用
   */
  quit() {
    this.stopStatsUpdate()
    require('electron').app.quit()
  }
  
  /**
   * 销毁托盘
   */
  destroy() {
    this.stopStatsUpdate()
    if (this.tray) {
      this.tray.destroy()
      this.tray = null
    }
  }
}

module.exports = TrayManagerEnhanced
